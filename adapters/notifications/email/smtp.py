# -*- coding: utf-8 -*-
"""
📧 SMTP 标准邮件通知适配器驱动
支持标准 SMTP 协议、SSL (465) 与 STARTTLS (587/25)，向指定管理员与订阅者邮箱分发出版状态与运维告警。
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Dict, Any, List
from core.adapters.egress.webhook.base import BaseWebhookDriver

class SmtpEmailDriver(BaseWebhookDriver):
    PLUGIN_ID = "email"
    ALIASES = ["smtp", "email_notification", "smtp_email"]
    DISPLAY_NAME = "📧 SMTP 邮件通知适配器"
    VERSION = "V1.0"
    DESCRIPTION = "通过标准 SMTP / SSL / STARTTLS 发送高质感 HTML 出版通知与故障运维告警。"

    def match(self, url: str) -> bool:
        return "smtp" in url.lower() or "mail" in url.lower()

    def get_recipients(self) -> List[str]:
        raw = self.config.get("receivers") or self.config.get("to") or ""
        if isinstance(raw, list):
            return [str(x).strip() for x in raw if str(x).strip()]
        if isinstance(raw, str):
            return [x.strip() for x in raw.replace(';', ',').split(',') if x.strip()]
        return []

    def build_payload(self, title: str, url_path: str, lang_code: str, ael_tag: str) -> Dict[str, Any]:
        return {
            "subject": f"📚 [Plenipes] 出版成功: {title} ({lang_code.upper()})",
            "title": title,
            "url_path": url_path,
            "lang": lang_code,
            "ael_iter_id": ael_tag,
            "html_body": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0f141c; color: #e2e8f0; border-radius: 12px; border: 1px solid #1e293b;">
                <h2 style="color: #00f2fe; margin-top: 0;">🚀 文章已成功出版</h2>
                <p style="font-size: 1.1rem; font-weight: bold; color: #fff;">{title}</p>
                <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin: 16px 0;">
                    <p style="margin: 4px 0; font-size: 0.85rem;">🌐 <b>语种代码</b>: <span style="color:#00f2fe;">{lang_code.upper()}</span></p>
                    <p style="margin: 4px 0; font-size: 0.85rem;">🔗 <b>访问路径</b>: <code style="color:#a855f7;">{url_path}</code></p>
                    <p style="margin: 4px 0; font-size: 0.85rem;">🏷️ <b>AEL 追踪</b>: <code>{ael_tag}</code></p>
                </div>
                <hr style="border: none; border-top: 1px solid #334155; margin: 20px 0;">
                <p style="font-size: 0.75rem; color: #64748b; margin-bottom: 0;">来自 Illacme Plenipes 数字出版自动化中枢</p>
            </div>
            """
        }

    def send_email(self, subject: str, html_body: str) -> bool:
        host = self.config.get("smtp_host") or ""
        port = int(self.config.get("smtp_port") or (465 if self.config.get("use_ssl", True) else 587))
        user = self.config.get("smtp_user") or ""
        password = self.config.get("smtp_pass") or self.config.get("password") or ""
        sender = self.config.get("sender") or user
        recipients = self.get_recipients()

        if not host or not user or not password or not recipients:
            raise ValueError("SMTP 主机、账号、密码或收件人列表未配置完整。")

        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = Header(f"Illacme Plenipes <{sender}>", 'utf-8')
        msg['To'] = Header(", ".join(recipients), 'utf-8')

        part_html = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part_html)

        use_ssl = bool(self.config.get("use_ssl", port == 465))
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=10) as server:
                server.login(user, password)
                server.sendmail(sender, recipients, msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.ehlo()
                if self.config.get("use_tls", True):
                    server.starttls()
                    server.ehlo()
                server.login(user, password)
                server.sendmail(sender, recipients, msg.as_string())
        return True
