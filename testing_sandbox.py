    # if game.turn_number == 5:
        #     with open('test.txt', 'a') as f:
        #         for row in surroundings:
        #             f.write(str(row) + ' \n')
#get relative coordinates for the surrounding squares of halite

# size = 3
# surroundings = []
# for y in range(-1*size, size + 1):
#     row = []
#     for x in range(-1*size, size + 1):
#         row.append([x, y])
#     surroundings.append(row) # this is now a relative grid with (0,0) being the center
    
import cv2
import numpy as np

for i in range(2,400):
    d = np.load(f"game_play/{i}.npy")
    cv2.imshow("",cv2.resize(d, (0,0), fx=30, fy=30))
    cv2.waitKey(25)