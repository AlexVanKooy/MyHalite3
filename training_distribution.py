import matplotlib.pyplot as plt
import os
import numpy as np
from statistics import mean
import seaborn as sns

all_files = os.listdir('first_network_game_data')

halite_amounts = []

for f in all_files:
    halite = int(f.split("-")[0])
    halite_amounts.append(halite)
# sns.set()
# halite_amounts
sns.distplot(np.array(halite_amounts))
print(f"{len(halite_amounts)} games found \n")   
# plt.hist(halite_amounts)
plt.show()
print(f"mean halite amount = {mean(halite_amounts)}\n")

