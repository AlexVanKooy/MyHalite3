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
    command_list = [f'halite.exe --replay-directory replays/ --"no-timeout" --turn-limit {MAX_TURNS} -vvv --width {map_size} --height {map_size} "python ML_bot_v1.py" "python ML_bot_v1.py"',
                f'halite.exe --replay-directory replays/ --"no-timeout" --turn-limit {MAX_TURNS} -vvv --width {map_size} --height {map_size} "python ML_bot_v1.py" "python ML_bot_v0.py" "python ML_bot_v0.py" "python ML_bot_v0.py"']

    command = secrets.choice(command_list)
    os.system(command)