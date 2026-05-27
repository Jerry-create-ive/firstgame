#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8000

os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server started at http://localhost:{PORT}")
    print(f"Game URL: http://localhost:{PORT}/main/static/game_full.html")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()