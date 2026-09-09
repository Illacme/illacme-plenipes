# -*- coding: utf-8 -*-
"""
Tests for Docusaurus Navigation i18n Synthesizer
"""
import os
import json
import tempfile
from core.adapters.egress.ssg.base_shards.docusaurus_i18n_synthesizer import DocusaurusI18nSynthesizer


def test_docusaurus_i18n_navbar_synthesizer():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a mock derived imprint theme directory
        theme_dir = os.path.join(tmp_dir, "imprints", "default", "themes", "docusaurus")
        os.makedirs(theme_dir, exist_ok=True)

        options = {
            "site_name": "Test Site",
            "i18n": {
                "defaultLocale": "zh-Hans",
                "locales": ["zh-Hans", "en", "ja"]
            },
            "navbar_items": [
                {"label": "📚 文档指南", "position": "left", "type": "docSidebar"},
                {"label": "📰 演示博客", "position": "left", "to": "/blog/"},
                {"label": "🌐 GitHub", "position": "right", "href": "https://github.com"}
            ],
            "navbar_items_i18n": {
                "ja": [
                    {"label": "📚 ドキュメントガイド", "raw_label": "ドキュメントガイド"},
                    {"label": "📰 デモブログ", "raw_label": "デモブログ"},
                    {"label": "🌐 GitHub", "raw_label": "GitHub"}
                ],
                "en": [
                    {"label": "📚 Document Guide", "raw_label": "Document Guide"},
                    {"label": "📰 Demo Blog", "raw_label": "Demo Blog"},
                    {"label": "🌐 GitHub Repo", "raw_label": "GitHub Repo"}
                ]
            }
        }

        success = DocusaurusI18nSynthesizer.synthesize(theme_dir, options)
        assert success is True

        # Check Japanese navbar.json
        ja_file = os.path.join(theme_dir, "i18n", "ja", "docusaurus-theme-classic", "navbar.json")
        assert os.path.exists(ja_file)
        with open(ja_file, "r", encoding="utf-8") as f:
            ja_data = json.load(f)

        assert ja_data["item.label.📚 文档指南"]["message"] == "📚 ドキュメントガイド"
        assert ja_data["item.label.📰 演示博客"]["message"] == "📰 デモブログ"
        assert ja_data["item.label.🌐 GitHub"]["message"] == "🌐 GitHub"

        # Check English navbar.json
        en_file = os.path.join(theme_dir, "i18n", "en", "docusaurus-theme-classic", "navbar.json")
        assert os.path.exists(en_file)
        with open(en_file, "r", encoding="utf-8") as f:
            en_data = json.load(f)

        assert en_data["item.label.📚 文档指南"]["message"] == "📚 Document Guide"
        assert en_data["item.label.📰 演示博客"]["message"] == "📰 Demo Blog"
        assert en_data["item.label.🌐 GitHub"]["message"] == "🌐 GitHub Repo"
