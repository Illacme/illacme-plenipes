#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Webhook 拦截雷达 (Mock Webhook Receiver)
零依赖，基于 Python 标准库。用于捕获和打印引擎发出的 JSON 全域分发包。
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class WebhookReceiver(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. 获取请求体长度
        content_length = int(self.headers.get('Content-Length', 0))
        # 2. 读取并解码请求体数据
        post_data = self.rfile.read(content_length)

        try:
            # 3. 解析为 JSON 字典
            payload = json.loads(post_data.decode('utf-8'))
            
            # 4. 在终端进行酷炫的格式化高亮打印
            print("\n" + "🚀 " + "="*55)
            print("📡 [雷达拦截] 成功捕获来自 Illacme 引擎的全域分发包！")
            print("="*58)
            print(f"🎯 事件类型 : {payload.get('event')}")
            print(f"📝 文章标题 : {payload.get('metadata', {}).get('title')}")
            print(f"🔗 永久链接 : {payload.get('metadata', {}).get('canonical_url')}")
            print(f"✂️  正文截取 : {payload.get('content', {}).get('raw_text')}...")
            print("-" * 58)
            print("📦 完整 JSON Payload 结构如下:")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            print("="*58 + "\n")

            # 5. 向引擎返回 200 OK，证明接收成功
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "received_loud_and_clear"}')

        except Exception as e:
            print(f"\n❌ 解析 Payload 失败: {e}")
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        # 屏蔽系统底层默认的啰嗦 HTTP 日志，保持终端清爽
        pass

def run(port=5678):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, WebhookReceiver)
    print(f"👀 [雷达就绪] 万向推流阀测试网关已启动 | 监听端口: {port}")
    print("   └── 💡 请在另一个终端窗口运行: python plenipes.py --sync")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 接收器已安全关闭。")
        httpd.server_close()

# 监听器启动测试命令：python tests/mock_webhook_server.py
if __name__ == '__main__':
    run()
