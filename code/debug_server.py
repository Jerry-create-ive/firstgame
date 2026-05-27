import subprocess
import sys
import os

# Set environment variables
env = os.environ.copy()
env['PYTHONUNBUFFERED'] = '1'
env['DJANGO_DEBUG'] = '1'

print("Starting Django server with debug output...")
print("Python path:", sys.executable)

process = subprocess.Popen(
    [sys.executable, "manage.py", "runserver", "8000", "--noreload"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    env=env,
    bufsize=0
)

import threading

def read_output():
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line.decode('utf-8', errors='replace'), end='')

thread = threading.Thread(target=read_output)
thread.start()

try:
    process.wait(timeout=15)
    print(f"\nServer exited with code: {process.returncode}")
except subprocess.TimeoutExpired:
    print("\nServer is running...")
    process.terminate()
    thread.join()