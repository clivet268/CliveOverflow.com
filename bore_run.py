import subprocess
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_app():
    print("Starting Flask application...")
    # Start Flask app process
    flask_process = subprocess.Popen([sys.executable, "app.py"])
    
    time.sleep(2)  # Give Flask a couple of seconds to bind to port 5000
    
    bore_host = os.getenv("BORE_HOST", "bore.pub")
    
    # Web App Bore Configuration (Port 5000 -> 61540)
    web_port = os.getenv("BORE_PORT", "61540")
    
    # RCON Bore Configuration (Port 25575 -> 61541)
    rcon_port = os.getenv("RCON_BORE_PORT", "61541")
    rcon_local_port = os.getenv("RCON_PORT", "25575")
    
    # Check if bore executable exists locally
    bore_cmd = "./bore.exe" if os.path.exists("bore.exe") else "bore"
    if not os.path.exists("bore.exe") and os.path.exists("./bore"):
        bore_cmd = "./bore"

    try:
        print(f"Starting web bore tunnel on {bore_host}:{web_port}...")
        web_bore_process = subprocess.Popen([bore_cmd, "local", "5000", "--to", bore_host, "--port", web_port])
        
        print(f"Starting RCON bore tunnel on {bore_host}:{rcon_port}...")
        rcon_bore_process = subprocess.Popen([bore_cmd, "local", rcon_local_port, "--to", bore_host, "--port", rcon_port])
        
        # Keep the script running and monitor processes
        while True:
            # Check if any process exited unexpectedly
            if flask_process.poll() is not None:
                print("Flask process stopped.")
                break
            if web_bore_process.poll() is not None:
                print("Web bore process stopped.")
                break
            if rcon_bore_process.poll() is not None:
                print("RCON bore process stopped.")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down services...")
        try:
            flask_process.terminate()
        except:
            pass
        try:
            web_bore_process.terminate()
        except:
            pass
        try:
            rcon_bore_process.terminate()
        except:
            pass

if __name__ == "__main__":
    run_app()