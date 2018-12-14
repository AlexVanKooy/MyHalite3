import tensorflow as tf
import os
import random
import time
import numpy as np
from tqdm import tqdm
# import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import TensorBoard

LOAD_TRAIN_FILES = False # true if we alread have batch train files
LOAD_PREV_MODEL = False # true if you want to transfer learn from existing model
HALITE_TRESHOLD = 4300

TRAINING_CHUNK_SIZE = 500    
PREV_MODEL_NAME =""# "models/3-conv-32-nodes-0-dense-1544115588"
VALIDATION_GAME_COUNT = 50 #number of games to validate against
NAME = f"4ep-smallDropAfterConv-3conv64-1Dense32-50Drop-{int(time.time())}"
EPOCHS = 4

TRAINING_DATA_DIR = 'training_data'

training_file_names = []

def balance(x,y): # we are making sure each direction appears evenly in the data, x=gamemap stuff y= move
    _0 = []
    _1 = []
    _2 = []
    _3 = []
    _4 = []

    for x,y in zip(x,y):
        if y == 0:
            _0.append([x,y])
        elif y == 1 :
            _1.append([x,y])
        elif y == 2 :
            _2.append([x,y])
        elif y == 3 :
            _3.append([x,y])
        elif y == 4 :
            _4.append([x,y])
    shortest = min([len(_0),
                   len(_1),
                   len(_2),
                   len(_3),
                   len(_4)])
    _0 = _0[:shortest]
    _1 = _1[:shortest]
    _2 = _2[:shortest]
    _3 = _3[:shortest]
    _4 = _4[:shortest]
    balanced = _0 + _1 + _2 + _3 + _4
    random.shuffle(balanced)
    print(f"the shortest file was {shortest}, the total balanced length was {len(balanced)}")

    xs = [] 
    ys = [ ]
    #now that the data is balanced 
    for x, y in balanced:
        xs.append(x)
        ys.append(y)
    return xs, ys

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


for f in os.listdir(TRAINING_DATA_DIR):
    halite_amount = int(f.split("-")[0])
    if halite_amount >= HALITE_TRESHOLD:
        training_file_names.append(os.path.join(TRAINING_DATA_DIR, f))

print(f"after the threshold we have {len(training_file_names)} games.\n")

random.shuffle(training_file_names)


if LOAD_TRAIN_FILES:
    test_x = np.load("saved_train_files/test_x.npy")
    test_y = np.load("saved_train_files/test_x.npy")
else:
    test_x = []
    test_y = []

    for f in tqdm(training_file_names[:VALIDATION_GAME_COUNT]):
        data = np.load(f)
        # 0th element is the game x
        # 1st element is the y choice
        for d in data:
            test_x.append(np.array(d[0]))
            test_y.append(d[1])

    np.save("saved_train_files/test_x.npy",test_x)
    np.save("saved_train_files/test_y.npy", test_y)
test_x = np.array(test_x)
#chuck loading as batches

tensorboard = TensorBoard(log_dir=f"logs/{NAME}")
if LOAD_PREV_MODEL:
    model = tf.keras.models.load_model(PREV_MODEL_NAME)

else:
    model = Sequential()

    model.add(Conv2D(64, (3, 3), padding="same", input_shape=test_x.shape[1:]))
    model.add(Activation('relu'))
    model.add(Dropout(0.01))
    model.add(MaxPooling2D(pool_size=(2, 2), padding="same"))

    
    
    model.add(Conv2D(64, (3, 3), padding="same"))
    model.add(Activation('relu'))
    model.add(Dropout(0.01))
    model.add(MaxPooling2D(pool_size=(2, 2), padding="same"))

    model.add(Dropout(0.01))

    model.add(Conv2D(64, (3, 3), padding="same"))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2), padding="same"))

    model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors

    model.add(Dense(64)) #removed this layer based on the iterative model results
    model.add(Dropout(0.5))

    model.add(Dense(5)) # I think this is the number of options for the network (N, S, E, W, no movement)
    model.add(Activation('softmax'))

    #fit loss = sparse categorical cross entropy
opt = tf.keras.optimizers.Adam(lr=1e-3, decay=1e-3)
model.compile(loss="sparse_categorical_crossentropy",
              optimizer = opt,
              metrics=['accuracy'])

for e in range(EPOCHS):
    training_file_chunks = chunks(training_file_names[VALIDATION_GAME_COUNT:], TRAINING_CHUNK_SIZE)

    print(f"currently working on outer epoch {e} out of {EPOCHS}")
    
    for idx, training_files in enumerate(training_file_chunks):

        print(f"working on training file chunk {idx+1}/{round(len(training_file_names)/TRAINING_CHUNK_SIZE, 2)}")
        if LOAD_TRAIN_FILES or e > 0:
            X = np.load(f"saved_chunks/X-{idx}.npy")
            y = np.load(f"saved_chunks/y-{idx}.npy")

        else:
            X = []
            y = []

            for f in tqdm(training_files):
                data = np.load(f)
                for d in data:
                    X.append(np.array(d[0]))
                    y.append(d[1])

            

            X, y = balance(X,y)
            test_x, test_y = balance(test_x, test_y)

            X = np.array(X)
            y = np.array(y)

            test_x = np.array(test_x)
            test_y = np.array(test_y)

            np.save(f"saved_chunks/X-{idx}.npy", X)
            np.save(f"saved_chunks/y-{idx}.npy", y)

        model.fit(X, y, batch_size=32, epochs=1, validation_data=(test_x, test_y), callbacks=[tensorboard])
        model.save(f"models/{NAME}")



