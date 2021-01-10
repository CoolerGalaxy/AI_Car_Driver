from alexnet import alexnet
from collections import Counter
import config
import cv2
import numpy as np
from random import shuffle
import sys

# This function performs feature engineering on the dataset
def generateData(data):
    print("Generating data (This can take a while depending on file size)")
    print("Generating from ", len(data), "source frames")
    
    newData = []

	# flip each image and action horizontally
    for each in data:
        newScreenShot = cv2.flip(each[0], 1)
        newDirection = each[1]

        if newDirection == [1,0,0]:
            newDirection = [0,0,1]
        elif newDirection == [0,0,1]:
            newDirection = [1,0,0]

        newData.append([newScreenShot, newDirection])

    newData = np.asarray(newData)
    
    return np.concatenate((data, newData))

# This function balances the data so that one action does not dominate during training
def balanceInput(file):
    data = np.load(file, allow_pickle=True)
    
    print("Initial data")
    print(len(data), "frames")
    print()
    
    data = generateData(data)

    print('After data generation')
    print(len(data), "frames")
    print()
    
    shuffle(data)

    a = [] #left turn
    w = [] #accelerate
    d = [] #right turn

	# organize data by the action that was performed
    for each in data:
        screenShot = each[0]
        direction = each[1]

        if direction == [1,0,0]:
            a.append([screenShot, direction])
        elif direction == [0,1,0]:
            w.append([screenShot, direction])
        elif direction == [0,0,1]:
            d.append([screenShot, direction])

    print("Before Balance")
    print("lefts = ", len(a))
    print("ups   = ", len(w))
    print("rights= ", len(d))
    print("---------------------")

	# equalize array lengths, dropping extra frames
    minLength = min([len(w), len(a), len(d)])

    a = a[:minLength]
    w = w[:minLength][:minLength]
    d = d[:minLength]

    print("After Balance")
    print("lefts = ", len(a))
    print("ups   = ", len(w))
    print("rights= ", len(d))

	# recombine data
    allData = a + w + d
    shuffle(allData)
    
    np.save("balancedData.npy", allData) # save as new file to preserve original data
 
if __name__ == "__main__":

    balanceInput(config.FILE_NAME)
    
    model = alexnet(config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT, config.LEARNING_RATE)

    for epoch in range(config.EPOCHS):

        # load generated file
        trainingData = np.load("balancedData.npy", allow_pickle=True)
	
        # set validation split from config file
        validationSplit = int(len(trainingData) * config.SPLIT_PERCENT)
                
        # divide data into train/test
        train = trainingData[:validationSplit]
        test = trainingData[validationSplit:]

        # split the image and input data        
        # NOTE: image array has wrong shape, needs a dimension removed 
        trainX = np.array([each[0] for each in train])
        trainX = np.array(trainX).reshape(-1, config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT, 3)
        trainY = [each[1] for each in train]
                
        testX = np.array([each[0] for each in test])
        testX = np.array(testX).reshape(-1, config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT, 3)
        testY = [each[1] for each in test]
                
        model.fit({'input': trainX}, {'targets': trainY}, n_epoch=1, validation_set=({'input': testX}, {'targets': testY}), snapshot_step=1000, show_metric=True, run_id=config.MODEL_NAME)

        model.save(config.MODEL_NAME)






















