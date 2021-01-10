from alexnet import alexnet
import numpy as np
import config
import cv2
import time
from key_output import PressKey,ReleaseKey, W, A, D
import win32api
import win32con
import win32gui
import win32ui
import random

#This function reads user keypresses
def readKey():
    keys = []
    for key in "C":
        if win32api.GetAsyncKeyState(ord(key)):
            keys.append(key)
    return keys

# This function captures screenshots of the game window
# This function was modified from https://stackoverflow.com/questions/50278695/grabscreen-py-python-win32api
def screenGrab(left, top):
    hwin = win32gui.GetDesktopWindow()

    width = config.WINDOW_WIDTH - left + 1
    height = config.WINDOW_HEIGHT - top + 1

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

def main():

    model = alexnet(config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT, config.LEARNING_RATE)
    model.load(config.MODEL_NAME)
    
    paused = False
    print('AI is driving, press "C" to pause') # "C" used for convenient keyboard position
	
    while(True):
        if not paused:
            screenShot = screenGrab(0,40) # 40 pixel offset to account for titlebar
			
			# Reduce image size
            screenShot = cv2.cvtColor(screenShot, cv2.COLOR_BGR2RGB)
            screenShot = cv2.resize(screenShot, (config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT))
			
			# Get model prediction
            prediction = model.predict([screenShot.reshape(config.CAPTURE_WIDTH,config.CAPTURE_HEIGHT,3)])[0]
            #print( np.trunc(prediction*10**2) / (10**2) * 100 ) # prediction printout

            # "Only turn if you're sure you want to turn!"
            turningThreshold = 0.85
            accelerationThreshold = 0.95

            if prediction[1] > accelerationThreshold:
                PressKey(W)
                print("GO")
            elif prediction[0] > turningThreshold:
                PressKey(A)
                print("Left")
            elif prediction[2] > turningThreshold:
                PressKey(D)
                print("Right")
            
			# Using sleep is not an ideal method because execution is suspended, need to find a way to do some sort of callback if there is time
            time.sleep(config.KEY_PRESS_DURATION) 
			# Release all keys after alotted time
            ReleaseKey(W)
            ReleaseKey(A)
            ReleaseKey(D)

        keys = readKey()

        if 'C' in keys:
            if paused == True:
                paused = False
                time.sleep(0.5) # This line prevents thrashing of toggle state
                print('AI driving')
            else:
                paused = True
                time.sleep(0.5)
                print('AI paused')

main()       










