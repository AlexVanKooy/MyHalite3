#!/usr/bin/env python3
# Python 3.6
"""
Making ship focused ML model following SentDex halite3 tutorial
"""
import os
import sys
stderr = sys.stderr
sys.stderr = open('./dev_output.txt', 'w')
import hlt
from hlt import constants
from hlt.positionals import Direction, Position
import random
import secrets
import logging
import numpy as np
import math
import time
import tensorflow as tf
# sys.stderr = stderr
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.05)
sess = tf.Session(config = tf.ConfigProto(gpu_options=gpu_options))

MODEL_TO_USE = "models/3conv32-2ep-softmax-1Dense32-thenDropout-40-percent-1544571232"

model = tf.keras.models.load_model(MODEL_TO_USE)

STORE_GAME_FOLDER = "first_network_game_data"

RANDOM_CHANCE = secrets.choice([0.15, 0.25, 0.35])
# "training_data"
""" <<<Game Begin>>> """

game = hlt.Game()
game.ready("ML_sentway")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))
#grid length : turn number We will use as part of the desision to save the game map
map_setting = {32: 400,
               40: 425,
               48: 450,
               56: 475,
               64: 500}

TOTAL_TURNS = 50 # limit the number actions taken by the random bot. This allows the 'signal' of good choices to come out of the noise
SAVE_THRESHOLD = 4200 # threshold of halite to save game
MAX_SHIPS = 1
SIGHT_DISTANCE = 16

direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

training_data = []# will hold all the game data, every move of every frame

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    command_queue = []

    
    dropoff_positions = [d.position for d in list(me.get_dropoffs()) + [me.shipyard]] 

    #if a position on the game map has a ship and it does NOT appear here, it is an enemy ship
    ship_positions = [s.position for s in list(me.get_ships())] 
    logging.info(f"ships length = {len(me.get_ships())} \n ")

    for ship in me.get_ships():        
        # logging.info(f"{ship.position},{ship.position + Position(-3,3)}")
        # logging.info(f"{game_map[ship.position +Position(-3,3)]}") 

        size = SIGHT_DISTANCE #chosen based on the need of several potentially useful toolkits data size reqs
        surroundings = []
        # surroundings = [[HALITE_AMOUNT, SHIP, DROPOFF]] 

        for y in range(-1*size, size + 1):
            row = []
            for x in range(-1*size, size + 1):
                current_cell = game_map[ship.position + Position(x,y)] #this is the cell we are examining as a possible move location
                # now we determine the values of the surroundings list cell by cell 
                
                if(current_cell.position in dropoff_positions):
                    drop_friend_foe = 1
                else:
                    drop_friend_foe = -1
                if (current_cell.position in ship_positions):  #if we find a ship in a location this will be our friend check
                    ship_friend_foe = 1
                else:
                    ship_friend_foe = -1

                halite = round(current_cell.halite_amount / constants.MAX_HALITE, 2) #ML algs like values between 0 & 1 or -1 & 1

                a_ship = current_cell.ship #check the cell for a ship
                structure = current_cell.structure

                #Edge cases, things that the above does not explicitly handle
                if halite is None:
                    halite = 0
                if a_ship is None:
                    a_ship = 0
                else:
                    a_ship = round(ship_friend_foe * (a_ship.halite_amount / constants.MAX_HALITE) , 2)
               
                if structure is None:
                    structure = 0
                else:
                    structure = drop_friend_foe

                amounts = (halite, a_ship, structure)

                if structure is not 0 :
                     logging.info(f"\n a structure was found at {current_cell}. It has a value of {structure} \n")

                row.append(amounts)
            surroundings.append(row)

        if secrets.choice(range(int(1/RANDOM_CHANCE))) == 1:
            choice = secrets.choice(range(len(direction_order)))
        else:
            model_out = model.predict([np.array(surroundings).reshape(-1, len(surroundings), len(surroundings), 3)])
            prediction = np.argmax(model_out)
            logging.info(f"model prediction = {direction_order[prediction]}\n")
            choice = prediction
        training_data.append([surroundings, choice])
        command_queue.append(ship.move(direction_order[choice]))




    #TODO: check if several ships are about to unload, don't want to clog the drop off
    if len(me.get_ships()) < MAX_SHIPS:

        if game.turn_number <= 200 and me.halite_amount >= (constants.SHIP_COST * 1.5) and not game_map[me.shipyard].is_occupied:
            logging.info(f" ship yard is_occupied = {game_map[me.shipyard].is_occupied} \n")
            command_queue.append(me.shipyard.spawn())

    if game.turn_number == TOTAL_TURNS:
        if me.halite_amount >= SAVE_THRESHOLD:
            np.save(f"{STORE_GAME_FOLDER}/{me.halite_amount}-{int(time.time())}.npy", training_data)

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

