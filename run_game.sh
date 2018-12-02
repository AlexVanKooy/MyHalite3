#!/bin/sh

./halite --replay-directory replays/ --turn-limit 50 -vvv --width 32 --height 32 "python ML_Bot.py" "python MyBot.py"
