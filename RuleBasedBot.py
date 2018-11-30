#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants
from hlt.positionals import Direction
import random
import logging

""" <<<Game Begin>>> """

game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("RuleBot_v1")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

ship_states = {} #tracking what each ship is doing
while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
  
    command_queue = []
    

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]
    position_choices = [] #Physical coordinate on the map that a bot is planning to go to
    
    for ship in me.get_ships():
        
        if ship.id not in ship_states:
            ship_states[ship.id] = "collecting"
            logging.info(" adding ship id # {} to ship states \n".format(ship.id))
        logging.info(" ship id {} state = {}".format(ship.id, ship_states[ship.id]))
        #Examine surrounding area
        position_options = ship.position.get_surrounding_cardinals() + [ship.position]
       
        #{(0,1): (19,38)}
        position_dict = {} #maps a relative direction to the global position

        #{position : amount of halite}
        #{(0,1): 500}
        halite_dict = {}
        
        #populate the position dict 
        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n]
        
        #populate the halite dict
        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount

            if (position_dict[direction] not in position_choices):# and (game_map[position].is_occupied == False):
                halite_dict[direction] = halite_amount
                # logging.info(" moving ship id {} to location {} \n".format(ship.id, position_dict[direction] ))
            else:
                logging.info("attempting to move to same spot \n")
        # if (ship_states[ship.id] == "depositing" and ship.halite_amount < constants.MAX_HALITE / 5):
        #     ship_states[ship.id] = "collecting"
        
        if (ship_states[ship.id] == "depositing") :
            # and not (ship.halite_amount < constants.MAX_HALITE / 5)):
            move = game_map.naive_navigate(ship, me.shipyard.position)
            position_choices.append(position_dict[move])
            command_queue.append(ship.move(move))


        elif (ship_states[ship.id] == "collecting" and ( game_map[ship.position].halite_amount < constants.MAX_HALITE / 10)) :
            localMaxHal_location = max(halite_dict, key=halite_dict.get)
            localMaxHal_value = game_map[position_dict[localMaxHal_location]].halite_amount
            logging.info(
                "ship id {} - local max halite @ = {} containing {} halite, current position halite = {} \n".format(ship.id,
                                                                                             localMaxHal_location,
                                                                                             localMaxHal_value,
                                                                                             game_map[position_dict[Direction.Still]].halite_amount)) 
            # if localMaxHal_value > (game_map[position_dict[Direction.Still]].halite_amount * 1.5 ):
            directional_choice = localMaxHal_location
               
            position_choices.append(position_dict[directional_choice])
            command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice]))) #move to location with the most halite
                
        if ship.halite_amount > constants.MAX_HALITE / 3:
            ship_states[ship.id] = "depositing"
        elif ship.halite_amount == 0:
            ship_states[ship.id] = "collecting"


    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

