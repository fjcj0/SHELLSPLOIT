#!/usr/bin/env bash
[[ ! -f sessions.json ]] && touch sessions.json; [[ ! -f build_log.txt ]] && touch build_log.txt
set -e
echo "Checking for Node.js and Python..."
OS="$(uname)"
install_node() {
  if [ "$OS" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "Installing Homebrew..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install node
  elif [ "$OS" = "Linux" ]; then
    sudo apt update
    sudo apt install -y nodejs npm
  else
    echo "Unsupported OS"
    exit 1
  fi
}
install_python() {
  if [ "$OS" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "Installing Homebrew..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python
  elif [ "$OS" = "Linux" ]; then
    sudo apt update
    sudo apt install -y python3 python3-pip
  else
    echo "Unsupported OS"
    exit 1
  fi
}
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js not found. Installing..."
  install_node
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python not found. Installing..."
  install_python
fi
echo "Installing Node.js dependencies..."
cd server || { echo "server folder not found"; exit 1; }
npm install
echo "Installing Python dependencies..."
cd ..
pip3 install -r requirements.txt
echo "Setup complete!"