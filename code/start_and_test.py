import subprocess
import time
import urllib.request

print("=== Start Test ===")

# Start server
print("1. Starting Django server...")
process = subprocess.Popen(
    ["python", "manage.py", "runserver", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for startup
time.sleep(3)

# Check process status
if process.poll() is None:
    print("Server process is running")
    
    # Try to connect
    try:
        print("2. Testing connection...")
        response = urllib.request.urlopen("http://localhost:8000/", timeout=5)
        print("Connection successful! Status:", response.status)
        print("Content length:", response.headers.get('Content-Length', 'unknown'), "bytes")
    except Exception as e:
        print("Connection failed:", str(e))
        
    # Terminate process
    print("3. Stopping server...")
    process.terminate()
    process.wait()
    print("Server stopped")
    
else:
    stdout, stderr = process.communicate()
    print("Server startup failed")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
