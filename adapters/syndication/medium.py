from core.adapters.syndication.base import BaseSyndicator
class MediumSyndicator(BaseSyndicator):
    PLUGIN_ID = "medium"
    def format_payload(self, title, body, tags, url, desc=""):
        return {"title": title, "contentFormat": "markdown", "content": body, "canonicalUrl": url, "tags": tags}
    def push(self, payload): pass
