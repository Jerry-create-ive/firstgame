#!/usr/bin/env python3
"""Simple HTTP server to serve the game with static files."""

import http.server
import socketserver
import os
import urllib.parse

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Handle root path
        if path == '/' or path == '/index.html':
            self.serve_html('main/templates/index.html')
            return
            
        # Handle static files
        if path.startswith('/static/'):
            # Remove /static/ prefix
            file_path = path[8:]
            full_path = os.path.join('main/static', file_path)
            
            # Print log for debugging
            print(f"[REQUEST] {self.path} -> {full_path}")
            print(f"[EXISTS] {os.path.exists(full_path)}")
            if os.path.exists(full_path):
                print(f"[SIZE] {os.path.getsize(full_path)} bytes")
                print(f"[MODIFIED] {os.path.getmtime(full_path)}")
            
            self.serve_static(full_path)
            return
            
        # Default behavior
        super().do_GET()
    
    def serve_html(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File not found")
    
    def serve_static(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            
            # Set correct content type
            if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                self.send_header('Content-Type', 'image/jpeg')
            elif file_path.endswith('.png'):
                self.send_header('Content-Type', 'image/png')
            elif file_path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif file_path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            else:
                self.send_header('Content-Type', 'application/octet-stream')
            
            # Add cache control to prevent caching
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {file_path}")
            self.send_error(404, f"File not found: {file_path}")

if __name__ == "__main__":
    print(f"Starting simple HTTP server on port {PORT}...")
    print(f"Static files directory: {os.path.abspath('main/static')}")
    print(f"Access game at: http://localhost:{PORT}/")
    
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()