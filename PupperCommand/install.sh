#!/usr/bin/env sh

FOLDER=$(dirname $(realpath "$0"))
cd $FOLDER

sudo apt-get install -y libsdl-ttf2.0-0
yes | sudo pip install ds4drv

for file in *.service; do
    [ -f "$file" ] || break
    sudo ln -s $FOLDER/$file /lib/systemd/system/
done

sudo systemctl daemon-reload
sudo systemctl enable joystick
sudo systemctl start joystick
