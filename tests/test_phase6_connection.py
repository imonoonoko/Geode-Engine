
import sys
import os
import time
import subprocess
import threading
import socket
import json
import requests

# Project Root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def find_free_port(start_port=3001):
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1
    return start_port

def start_bot_server(port):
    """Start headless bot server"""
    bot_dir = os.path.join(project_root, "src", "games", "minecraft", "bot")
    env = os.environ.copy()
    env["BOT_PORT"] = str(port)
    
    # Check if node exists
    try:
        subprocess.run(["node", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except:
        print("❌ Node.js not found. Cannot start bot server.")
        return None

    print(f"🚀 Starting Bot Server on port {port}...")
    process = subprocess.Popen(
        ["node", "bot.js"],
        cwd=bot_dir,
        shell=True,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    def print_output():
        for line in iter(process.stdout.readline, b''):
            try:
                msg = line.decode().strip()
                # print(f"[BOT] {msg}") 
            except: pass
            
    threading.Thread(target=print_output, daemon=True).start()
    return process

def test_connection():
    print("--- ⛏️ Phase 6: Minecraft Connection Test ---")
    
    # 1. Start Bot Server (Force New)
    port = 3002
    # Kill any existing on 3002 just in case (Win helper)
    os.system(f"netstat -ano | findstr {port} > nul && taskkill /F /FI \"PID eq {port}\"") # Pseudo
    
    process = start_bot_server(port)
    is_running = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            print(f"✅ Bot Server found on port {port}. Using existing.")
            is_running = True
            process = None
    
    if not is_running:
        process = start_bot_server(port)
        if not process: return False
        print("⏳ Waiting for server API...")
        time.sleep(3)
    
    api_url = f"http://localhost:{port}"
    environment_connected = False
    
    try:
        # 2. Connect to Minecraft Server (Localhost default)
        print("🔗 Sending Connect Request...")
        payload = {
            "host": "localhost",
            "port": 25565,
            "username": "TestBot_Phase6"
        }
        res = requests.post(f"{api_url}/connect", json=payload, timeout=5)
        print(f"Connect Response: {res.json()}")
        
        # 3. Poll for 'connected' state
        print("⏳ Polling for 'connected' state (max 15s)...")
        for i in range(15):
            time.sleep(1)
            try:
                state_res = requests.get(f"{api_url}/state", timeout=2)
                state = state_res.json()
                
                if state.get("connected"):
                    print(f"✅ CONNECTED! Position: {state.get('position')}")
                    environment_connected = True
                    break
                else:
                    if i % 3 == 0: print(".", end="", flush=True)
            except Exception as e:
                print(f"⚠️ Poll Error: {e}")
                
        print()
        
        if environment_connected:
            print("🎉 PASSED: Bot successfully connected to Minecraft Server.")
        else:
            print("❌ FAILED: Bot could not connect. Is the server running?")
            
    except Exception as e:
        print(f"❌ Test Exception: {e}")
    finally:
        print("🔌 Cleaning up...")
        try: 
            requests.get(f"{api_url}/disconnect", timeout=2) 
        except: pass
        if process:
            process.terminate()
        
    return environment_connected

if __name__ == "__main__":
    success = test_connection()
    if not success:
        sys.exit(1)
