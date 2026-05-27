import urllib.request
import time

# 测试访问静态文件
test_urls = [
    'http://localhost:8000/static/image/1.jpg',
    'http://localhost:8000/static/image/2.jpg',
    'http://localhost:8000/static/image/17.jpg'
]

print('=== 测试静态文件访问 ===')
for url in test_urls:
    try:
        req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
        response = urllib.request.urlopen(req, timeout=5)
        content_length = response.headers.get('Content-Length', '未知')
        print(f'✅ {url} - 状态: {response.status}, 大小: {content_length} 字节')
    except Exception as e:
        print(f'❌ {url} - 错误: {e}')
