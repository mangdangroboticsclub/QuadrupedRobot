#!/usr/bin/env sh

# step 1 stop robot service
systemctl stop robot

# step 2 run set_neatral.py
python3 set_neatral.py
