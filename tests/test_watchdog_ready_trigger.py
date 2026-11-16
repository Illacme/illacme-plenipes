"""
Tests for Obsidian/local vault Frontmatter ready-state watchdog triggers
in core/services/daemon_handler.py and WatchdogSettings.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from core.config.models.system import WatchdogSettings
from core.services.daemon_handler import ChangeHandler


def _make_handler(tmp_path, ready_only: bool, auto_podcast: bool = True):
    watch_cfg = WatchdogSettings(ready_trigger_only=ready_only, auto_podcast_on_ready=auto_podcast)
    engine = SimpleNamespace(
        config=SimpleNamespace(system=SimpleNamespace(watchdog_settings=watch_cfg, typing_idle_threshold=0.1, enable_asset_audit=False)),
        paths={"shadow": str(tmp_path / "shadow"), "target_base": str(tmp_path / "dist"), "ledger_cache": str(tmp_path / "cache/l.db")},
        route_matrix=[],
        sync_document=MagicMock(),
        sentinel=SimpleNamespace(run_health_check=MagicMock()),
        meta=SimpleNamespace(save=MagicMock()),
    )
    args = SimpleNamespace(dry_run=False, force=False)
    pool = MagicMock()
    h = ChangeHandler(engine, args, set(), pool)
    # Prevent background timers from firing after test finishes
    h._lazy_gc_trigger = MagicMock()
    h._debounced_heavy_tasks = MagicMock()
    return h, engine


def test_ready_trigger_only_skips_draft_and_unmarked_notes(tmp_path):
    h, engine = _make_handler(tmp_path, ready_only=True)
    draft_md = tmp_path / "draft.md"
    draft_md.write_text("---\ntitle: WIP\nstatus: draft\n---\nHello", encoding="utf-8")
    plain_md = tmp_path / "plain.md"
    plain_md.write_text("---\ntitle: Note\n---\nHello", encoding="utf-8")

    h._dispatch_task(str(draft_md), "/blog", "blog")
    h._dispatch_task(str(plain_md), "/blog", "blog")
    engine.sync_document.assert_not_called()


def test_ready_trigger_only_runs_on_status_ready_and_auto_podcasts(tmp_path):
    h, engine = _make_handler(tmp_path, ready_only=True, auto_podcast=True)
    ready_md = tmp_path / "ready.md"
    ready_md.write_text("---\ntitle: Launch\nstatus: ready\npodcast: true\n---\nBody text", encoding="utf-8")

    with patch("core.podcast.auto_synthesize_pending_podcasts") as mock_pod, \
         patch("core.services.daemon_handler.send_notification"):
        h._dispatch_task(str(ready_md), "/blog", "blog")

    engine.sync_document.assert_called_once()
    mock_pod.assert_called_once_with(engine)
