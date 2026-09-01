#!/bin/bash
set -e
cd "$(dirname "$0")"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv handsonvenv

# Activate virtual environment
echo "Activating virtual environment..."
source handsonvenv/bin/activate

# --- Proxy settings (if needed) ---
# If you are behind a proxy, uncomment(Remove '#') and edit the following lines:
# export HTTP_PROXY="http://your.proxy.server:port"
# export HTTPS_PROXY="http://your.proxy.server:port"
# pip config set global.proxy http://your.proxy.server:port


# Install packages
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r ../requirements.txt

# Make shell scripts executable
chmod +x ../../RUN/ForMacUsers/01_Excel2MaiMLProtocol.sh
chmod +x ../../RUN/ForMacUsers/02_Excel2MaiMLData.sh
chmod +x ../../RUN/ForMacUsers/03_MaiMLStandaloneViewer.sh
chmod +x ../../RUN/ForMacUsers/05_elabftw2MaiML.sh

TARGET_DIR="../../RUN/ForMacUsers"
ZIPFILE="../DATAFILES.zip"

# Check if the ZIP file exists and extract it
if [ -f "$ZIPFILE" ]; then
    echo "Unzipping data files into $TARGET_DIR ..."
    unzip -o "$ZIPFILE" -d "$TARGET_DIR"
else
    echo "Error: ZIP file '$ZIPFILE' not found."
    exit 1
fi

echo "Setup complete!"