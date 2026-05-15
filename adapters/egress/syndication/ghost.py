from core.adapters.syndication.base import BaseSyndicator
class GhostSyndicator(BaseSyndicator):
    PLUGIN_ID = "ghost"
    DISPLAY_NAME = "Ghost"
    VERSION = "V1.0"
    DESCRIPTION = "同步至 Ghost 专业出版平台，支持 Content API 物理对接。"
    def format_payload(self, title, body, tags, url, desc=""): return {}
    def push(self, payload): pass
