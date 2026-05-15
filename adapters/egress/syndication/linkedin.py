from core.adapters.syndication.base import BaseSyndicator
class LinkedInSyndicator(BaseSyndicator):
    PLUGIN_ID = "linkedin"
    DISPLAY_NAME = "LinkedIn"
    VERSION = "V1.0"
    DESCRIPTION = "同步至 LinkedIn 职场社交平台，支持分享文章至个人动态与组织页面。"
    def format_payload(self, title, body, tags, url, desc=""): return {}
    def push(self, payload): pass
