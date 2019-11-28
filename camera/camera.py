import asyncio
import utils
import os
import cv2
import random
import base64
import videocaptureasync
from time import time

ws = None
WEBCAM_URI = "http://192.168.43.99:8080/video"
MAX_FPS = 60

async def onReception(websocket, head, body):
    global ws
    if ws == None:
        ws = websocket
    print("[MAIN > CAMERA]", head)

    if head == "start":
        await turnCameraOn(onCameraStarted)

# Module-wide variable
started = False

async def onCameraStarted():
    global MAX_FPS
    minDelay = 1 / MAX_FPS

    await utils.wsSend(ws, "started")

    while True:
        t = time()
        img = takePicture()
        if img is not None:
            retval, buffer = cv2.imencode(".jpg", img)
            # Convert to base64 encoding and show start of data
            jpgAsText = base64.b64encode(buffer)
            encoded = str(jpgAsText, "utf-8")
            try:
                print("sending")
                await utils.wsSend(ws, "imageBase64", {"time": t, "data": encoded})
                await asyncio.sleep(0.01)
                #delay = time()-t
                #if delay < minDelay:
                #    await asyncio.sleep(minDelay - delay)
                #print("sent", "- slept for", minDelay - delay, "s")
            except Exception as e:
                print("Error sending image:", e)
                await asyncio.sleep(3)



# Turns the camera on
async def turnCameraOn(onSuccess=None, onFailure=None):
    global started, videoCapture
    try:
        videoCapture = videocaptureasync.VideoCaptureAsync(WEBCAM_URI)
        videoCapture.start()
        started = True
        if onSuccess is not None:
            await onSuccess()
    except cv2.error as e:
        print("Error while connecting to the video source");
        print(e)
        if onFailure is not None:
            await onFailure()

# Turns the camera off
def turnCameraOff():
    global started, videoCapture
    videoCapture.stop()
    started = False

# For now, simply returns a random image from a folder
def takePicture():
    global started
    if not started:
        return None

    global videoCapture

    # Get all images from the pictures directory
    """picturesDir = "pictures"
    pictureFiles = []
    for item in os.listdir(picturesDir):
        if os.path.isfile(os.path.join(picturesDir, item)) and (item.endswith(".png") or item.endswith(".jpg")):
            pictureFiles.append(item)
    # Select a random image
    fileName = random.choice(pictureFiles)
    # Read the image
    img = cv2.imread(os.path.join(picturesDir, fileName))
    """

    frame = None
    try:
        ret, frame = videoCapture.read()
        if not ret:
            print("RET IS FALSE")
    except Exception as e:
        print("Error while reading frame from VideoCapture:", e)

    return frame

utils.startWsServer(5001, onReception)
