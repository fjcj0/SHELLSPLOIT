from shapes import print_logo, print_help
import subprocess
if __name__ == "__main__":
    print_logo()
    while True:
        print("\033[1;36m")
        print("""
        1- Customize and install payload.
        2- Help.
        3- Exit.
        """)
        print("\033[0m")
        try:
            ch = int(input("Choose option: "))
            match ch:
                case 1:
                    hosts = input(
                        "SERVER_URL,WEBSOCKET_URL,WEBSOCKET_AUDIO_URL,IP_ADDRESS_SOCKET,PORT_SOCKET > "
                    )
                    parts = hosts.split(',')
                    if len(parts) != 5:
                        print("❌ Error: Please enter exactly 5 values separated by commas.")
                        continue
                    server_url = parts[0].strip()
                    web_socket_url = parts[1].strip()
                    web_socket_audio_url = parts[2].strip()
                    ip_address_socket = parts[3].strip()
                    port_socket = parts[4].strip()
                    subprocess.run([
                        "./build.sh",
                        server_url,
                        web_socket_url,
                        web_socket_audio_url,
                        ip_address_socket,
                        port_socket
                    ])
                case 2:
                    print_help()
                case 3:
                    print("Exiting...")
                    break
                case _:
                    print("Please enter a correct option (1-3)")
        except ValueError:
            print("Please enter a valid number")
            continue