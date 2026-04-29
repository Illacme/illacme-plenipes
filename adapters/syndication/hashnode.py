from core.adapters.syndication.base import BaseSyndicator
class HashnodeSyndicator(BaseSyndicator):
    PLUGIN_ID = "hashnode"
    def format_payload(self, title, body, tags, url, desc=""): return {}
    def push(self, payload): pass
