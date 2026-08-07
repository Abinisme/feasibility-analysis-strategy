#!/usr/bin/env python3
"""
文峰桌面宠物 - 启动脚本
用法: python3 start.py [--port PORT]
"""
import http.server
import socketserver
import webbrowser
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}"
    print(f"""
╔══════════════════════════════════════╗
║     🧑‍💼 文峰桌面宠物 v1.0.0          ║
╠══════════════════════════════════════╣
║  服务地址: {url:<27} ║
║  按 Ctrl+C 停止服务                  ║
╚══════════════════════════════════════╝
    """)
    
    # 自动打开浏览器
    webbrowser.open(url)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[文峰桌面宠物] 已停止")
