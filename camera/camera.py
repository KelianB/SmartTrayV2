import asyncio
import utils
import os
import cv2
import base64
import videocaptureasync
from time import time

ws = None
started = False
videoCapture = None
# Location of the IP cam
WEBCAM_URI = "http://192.168.43.247:8080/video"
# Maximum frames captured per second
MAX_FPS = 30
# Port used by this module to listen for messages
LISTENING_PORT = 5001

# Called when the camera receives a message from the main module
async def onReception(websocket, head, body):
    global ws
    if ws == None:
        ws = websocket
    print("[MAIN > CAMERA]", head)

    if head == "start":
        await turnCameraOn(onCameraStartupSuccess, onCameraStartupFailure)

# Called when the camera has been successfully started
async def onCameraStartupSuccess():
    global MAX_FPS
    minDelay = 1 / MAX_FPS

    await utils.wsSend(ws, "start-success")

    while True:
        t = time()
        img = capturePicture()
        if img is not None:
            encodedImg = utils.imageToBase64(img)
            if encodedImg is not None:
                computingDelay = time()-t
                if computingDelay < minDelay:
                    await asyncio.sleep(minDelay - computingDelay)
                try:
                    await utils.wsSend(ws, "image-base64", {"time": t, "data": encodedImg})
                except Exception as e:
                    print("Error sending image:", e)
                    await asyncio.sleep(3)

# Called when the camera couldn't be started or couldn't be reached
async def onCameraStartupFailure():
    await utils.wsSend(ws, "start-failure")

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
        print("test", e)
    except Exception as e:
        print("Error while connecting to the video source:");
        print(e)
        if onFailure is not None:
            await onFailure()

# Turns the camera off
def turnCameraOff():
    global started
    started = False
    videoCapture.stop()

# Reads a picture from the camera
def capturePicture():
    if not started:
        return None

    ret, frame = False, None
    try:
        ret, frame = videoCapture.read()
    except Exception as e:
        print("Error while reading frame from VideoCapture:", e)

    if not ret:
        return None

    return frame


utils.startWsServer(LISTENING_PORT, onReception)
asyncio.get_event_loop().run_forever()
