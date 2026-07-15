#!/bin/bash
python3 -m venv venv
source venv/bin/activate

# install textual, pycryptodome, pyperclip, rich
pip install -r requirements.txt

# check if wayland or x11
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then 
	echo "Wayland detected - installing wl-clipboard..."
	sudo apt-get install -y wl-clipboard
else
	echo "X11 detected - installing xclip..."
	sudo apt-get install -y xclip
fi

echo "Setup Complete."


