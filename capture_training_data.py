import numpy as np
import config
import cv2
import time
import os
import win32api
import win32gui
import win32con
import win32ui

FILE_NAME = "data.npy"

# This function one-hot-encodes the user actions
def keyOutput(key):
    #output = [LEFT, FORWARD, RIGHT]
    keyEncode = [0,0,0]

    #Steering commands take precedence
    if "A" in key:
        keyEncode[0] = 1
    elif "D" in key:
        keyEncode[2] = 1
    elif "W" in key:
        keyEncode[1] = 1
        
    return keyEncode

# This function reads user keypresses
def readKey():
    keys = []
    for key in "AWDC":
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
	# Loads the data file if it exists. If not, creates a new one.
    if os.path.exists(config.FILE_NAME):
        print("Adding to existing file,", config.FILE_NAME)
        data = list(np.load(config.FILE_NAME, allow_pickle=True))
        print("File contains", len(data), "frames.")
    else:
        print("File not detected, creating new...")
        data = []

	# Delay to allow user the opportunity to prepare to drive the vehicle
    print("Gameplay capture will begin in 3 seconds...")
    time.sleep(3)
    print('GO! Note: The "C" key will start/stop the image capture')

    gameCapture = True
    
    while(True):
        if gameCapture == True:
            screenShot = screenGrab(0, 40) # 40 pixel offset to account for titlebar

            # Reduce image size for reduced network input
            screenShot = cv2.resize(screenShot, (config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT))
            screenShot = cv2.cvtColor(screenShot, cv2.COLOR_BGR2RGB)

            # Capture keypress
            key = readKey()
            keyPress = keyOutput(key)

            # Add to data to list
			if not keyPress == [0,0,0]: # Only adds frames that contain control data
				data.append([screenShot, keyPress])

            # Save every 100 frames
            if len(data) % 100 == 0:
                print(len(data), "frames captured")
                np.save(config.FILE_NAME, data)

        if "C" in readKey():
            if gameCapture == True:
				print("Image capture stopped")
                gameCapture = False
                time.sleep(0.5) # This line prevents thrashing of toggle state
                #program will idle until capture reenabled
            else:
				print("Now capturing images")
                gameCapture = True
                time.sleep(0.5)

main()
















