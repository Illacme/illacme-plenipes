from core.adapters.syndication.base import BaseSyndicator
class HashnodeSyndicator(BaseSyndicator):
    PLUGIN_ID = "hashnode"
    DISPLAY_NAME = "Hashnode"
    VERSION = "V1.0"
    DESCRIPTION = "同步至 Hashnode 全球博客社区，支持 GraphQL 协议分发。"
    def format_payload(self, title, body, tags, url, desc=""): return {}
    def push(self, payload): pass
