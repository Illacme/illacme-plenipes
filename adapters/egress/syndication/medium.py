from core.adapters.syndication.base import BaseSyndicator
class MediumSyndicator(BaseSyndicator):
    PLUGIN_ID = "medium"
    DISPLAY_NAME = "Medium"
    VERSION = "V1.0"
    DESCRIPTION = "同步至 Medium 全球创作平台，支持 Markdown 格式化与 Canonical URL 溯源。"
    def format_payload(self, title, body, tags, url, desc=""):
        return {"title": title, "contentFormat": "markdown", "content": body, "canonicalUrl": url, "tags": tags}
    def push(self, payload): pass
