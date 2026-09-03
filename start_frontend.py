import subprocess
import time
import urllib.request

node_exe = r"C:\Program Files\nodejs\node.exe"
frontend_dir = r"C:\Users\lokha\nexus-ai-safety\frontend"

print("Starting Vite frontend...")
proc = subprocess.Popen(
    [node_exe, "vite", "--host", "--port", "3000"],
    cwd=frontend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

print("Waiting for Vite to compile...")
for i in range(30):
    time.sleep(1)
    try:
        r = urllib.request.urlopen('http://localhost:3000', timeout=2)
        print("Frontend running on port 3000, status:", r.status)
        break
    except:
        if i >= 15:
            print("Still compiling... (%d/%d)" % (i+1, 30))
        
print("Frontend process PID:", proc.pid)