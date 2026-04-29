from core.adapters.syndication.base import BaseSyndicator
class GhostSyndicator(BaseSyndicator):
    PLUGIN_ID = "ghost"
    def format_payload(self, title, body, tags, url, desc=""): return {}
    def push(self, payload): pass
