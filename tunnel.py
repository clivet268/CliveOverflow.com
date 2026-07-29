import subprocess
import time

# Start your Flask app and the Serveo tunnel concurrently
if __name__ == "__main__":
    print("Starting Flask app and opening public Serveo tunnel...")
    
    # Launch Flask
    flask_process = subprocess.Popen(["python", "app.py"])
    
    # Give Flask a couple of seconds to spin up
    time.sleep(2)
    
    # Launch Serveo SSH tunnel to hide your IP and provide a free URL
    tunnel_process = subprocess.Popen(["ssh", "-R", "80:localhost:5000", "serveo.net"])
    
    try:
        tunnel_process.wait()
    except KeyboardInterrupt:
        flask_process.terminate()
        tunnel_process.terminate()