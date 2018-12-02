import os
import secrets


MAX_TURNS = 50

map_settings = {32: 400,
               40: 425,
               48: 450,
               56: 475,
               64: 500}
while True:
    map_size = secrets.choice(list(map_settings.keys()))
    command_list = [f'halite.exe --replay-directory replays/ --turn-limit {MAX_TURNS} -vvv --width {map_size} --height {map_size} "python ML_bot.py" "python ML_bot.py"',
                f'halite.exe --replay-directory replays/ --turn-limit {MAX_TURNS} -vvv --width {map_size} --height {map_size} "python ML_bot.py" "python ML_bot.py" "python ML_bot.py" "python ML_bot.py"']

    command = secrets.choice(command_list)
    os.system(command)