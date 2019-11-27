import asyncio
import websockets
import json
import utils
import os
import cv2 
import random
import base64

async def onReception(ws, head, body):          
    print("[MAIN > CAMERA]", head) 
        
    if head == "start":             
        turnCameraOn()
        await utils.wsSend(ws, "started")
    if head == "takepicture":
        img = takePicture()
        retval, buffer = cv2.imencode(".jpg", img)
        # Convert to base64 encoding and show start of data
        jpgAsText = base64.b64encode(buffer)
        encoded = str(jpgAsText, "utf-8")
        await utils.wsSend(ws, "imageBase64", encoded)


# Module-wide variable
cam = {
    "started": False
}

# Turns the camera on
def turnCameraOn(onSuccess=None, onFailure=None):
    global cam, cap
    cam["started"] = True

    if onSuccess is not None:
        onSuccess()
    # cannot fail for now
    
# Turns the camera off
def turnCameraOff():
    global cam, cap
    cap.release()
    cam["started"] = False

# For now, simply returns a random image from a folder    
def takePicture():
    if not cam["started"]:
        return None
    
    # Get all images from the pictures directory
    picturesDir = "pictures"
    pictureFiles = []
    for item in os.listdir(picturesDir):
        if os.path.isfile(os.path.join(picturesDir, item)) and (item.endswith(".png") or item.endswith(".jpg")):
            pictureFiles.append(item)
    # Select a random image
    fileName = random.choice(pictureFiles)
    # Read the image
    img = cv2.imread(os.path.join(picturesDir, fileName))  
    
    # img = cv2.VideoCapture(0)
    
    return img
    
utils.startWsServer(5001, onReception)
