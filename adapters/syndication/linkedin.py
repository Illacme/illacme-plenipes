from core.adapters.syndication.base import BaseSyndicator
class LinkedInSyndicator(BaseSyndicator):
    PLUGIN_ID = "linkedin"
    def format_payload(self, title, body, tags, url, desc=""): return {}
    def push(self, payload): pass
