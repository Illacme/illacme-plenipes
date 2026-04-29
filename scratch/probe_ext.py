import sys
import os
sys.path.append(os.getcwd())
from core.config.config import load_config
from core.adapters.egress.ssg import SSGAdapter

def probe():
    cfg = load_config("config.sovereign.yaml")
    theme_name = cfg.active_theme
    theme_opts = cfg.theme_options.get(theme_name)
    if not theme_opts:
        from core.config.config import ThemeSettings
        theme_opts = ThemeSettings()
    theme_opts.name = theme_name
    
    adapter = SSGAdapter(theme_opts)
    print(f"Theme: {theme_name}")
    print(f"Renderer: {adapter.active_renderer.__class__.__name__}")
    print(f"Extension from adapter: {getattr(adapter, 'output_extension', 'NOT_FOUND')}")
    print(f"Extension from renderer: {getattr(adapter.active_renderer, 'output_extension', 'NOT_FOUND')}")

if __name__ == "__main__":
    probe()
