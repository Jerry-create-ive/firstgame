import subprocess
import time

try:
    print("Starting Django server...")
    process = subprocess.Popen(
        ["python", "manage.py", "runserver", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(5)
    
    stdout, stderr = process.communicate(timeout=2)
    
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    print("Return code:", process.returncode)
    
except subprocess.TimeoutExpired:
    print("Server is running successfully!")
    process.kill()
except Exception as e:
    print(f"Error: {e}")
