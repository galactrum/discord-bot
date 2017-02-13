#!/bin/bash

kill -9 bot.py
#python3 bot.py &
su bot -c "python3 bot.py >/dev/null 2>&1 &"
