#!/usr/bin/env python3
# Python 3.6
"""
Making ship focused ML model following SentDex halite3 tutorial
"""
import hlt
from hlt import constants
from hlt.positionals import Direction, Position
import random
import secrets
import logging
import numpy as np
import math
import time

""" <<<Game Begin>>> """

game = hlt.Game()
game.ready("ML_Bot")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

#grid length : turn number We will use as part of the desision to save the game map
map_setting = {32: 400,
               40: 425,
               48: 450,
               56: 475,
               64: 500}

TOTAL_TURNS = 50 # limit the number actions taken by the random bot. This allows the 'signal' of good choices to come out of the noise
SAVE_THRESHOLD = 4100 # threshold of halite to save game
MAX_SHIPS = 1

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    command_queue = []

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    dropoff_positions = [d.position for d in list(me.get_dropoffs()) + [me.shipyard]] 

    #if a position on the game map has a ship and it does NOT appear here, it is an enemy ship
    ship_positions = [s.position for s in list(me.get_ships())] 

    for ship in me.get_ships():        
        logging.info(f"{ship.position},{ship.position + Position(-3,3)}")
        logging.info(f"{game_map[ship.position +Position(-3,3)]}") 

        size = 16 #chosen based on the need of several potentially useful toolkits data size reqs
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
                row.append(amounts)
            surroundings.append(row)
    
        # np.save(f"game_play/{game.turn_number}.npy",surroundings)

        command_queue.append(ship.move(secrets.choice(direction_order)))




    #TODO: check if several ships are about to unload, don't want to clog the drop off
    if len(me.get_ships()) < MAX_SHIPS:

        if game.turn_number <= 200 and me.halite_amount >= (constants.SHIP_COST * 1.5) and not game_map[me.shipyard].is_occupied:
            command_queue.append(me.shipyard.spawn())

    if game.turn_number == TOTAL_TURNS:
        if me.halite_amount >= SAVE_THRESHOLD:
            np.save(f"training_data/{me.halite_amount}-{int(time.time())}.npy", surroundings)

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

