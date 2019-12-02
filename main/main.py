import asyncio
import websockets
import json
import utils
from time import time
import base64
from cv2 import imdecode
import numpy as np

### SmartTray ###

## Authors
# Angela Hoyos, Lizeth Bernal, Philippe Rateau, Mathilde Verlyck, Minh Tri Truong, Kelian Baert
## Description
# This is the main module of our Food Recognition AI system "SmartTray".

CAMERA_WS_URI = "ws://camera:5001"
ML_WS_URI = "ws://ml:5002"
INFO_WS_URI = "ws://info:5003"

cameraWs = None
mlWs = None
infoWs = None
frontWs = None

isMLWorking = False
cameraConnectionTime = 0

# Port used for connecting and exchanging messages with the front-end
FRONT_MESSAGING_PORT = 5000

# Connects to a websocket server at the given location
async def wsConnect(URI, onConnection, onMessageReceived):
    print("Connecting to", URI, "...")

    try:
        async with websockets.connect(URI, max_size=1e10, max_queue=None, read_limit=1e14, write_limit=1e14) as websocket:
            await onConnection(websocket)
            await utils.wsSend(websocket, "start")

            while True:
                try:
                    response = await websocket.recv()
                    msg = json.loads(response)
                    await onMessageReceived(websocket, msg["head"], msg["body"])
                except Exception as e:
                    print("Connection with", URI, "threw an error:", e)
                #except websockets.exceptions.ConnectionClosed:
                #    print("Connection with", URI, "was closed")
                #    break
    except Exception as e:
        print("Connection with " + URI + " threw an exception:", e);

# Called when receiving a message from the camera module
async def onReceptionFromCamera(ws, head, body):
    global mlWs, isMLWorking, cameraConnectionTime
    print("[MAIN < CAMERA]", head)

    if head == "start-success":
        pass
    if head == "start-failure":
        # TODO Inform the front so it can display an error
        pass
    elif head == "image-base64":
        latency = time() - body["time"]
        print("latency", latency, "(connected since", time() - cameraConnectionTime, ")")

        await sendImageToFront(body["data"])
        if not isMLWorking:
            isMLWorking = True
            await utils.wsSend(mlWs, "image-base64", body["data"])

# Called when receiving a message from the machine learning module
async def onReceptionFromML(ws, head, body):
    global frontWs, isMLWorking
    print("[MAIN < ML]", head)

    if head == "image-items":
        isMLWorking = False
        if frontWs != None:
            await utils.wsSend(frontWs, "labels", body)
        # TODO send get-info to info service with the name of the items

# Called when receiving a message from the info module
async def onReceptionFromInfo(ws, head, body):
    print("[MAIN < INFO]", head)

    if head == "db-ready":
        pass
        # Test
        #await utils.wsSend(ws, "get-info", ["Veau", "Lapin", "Farine"])
    if head == "info":
        # TODO do something with info
        print(body)

# Called when we have successfully connected to the machine learning module
async def onConnectionML(websocket):
    global mlWs
    mlWs = websocket

# Called when we have successfully connected to the camera module
async def onConnectionCamera(websocket):
    global cameraWs
    global cameraConnectionTime
    cameraConnectionTime = time()
    cameraWs = websocket

# Called when we have successfully connected to the info module
async def onConnectionInfo(websocket):
    global infoWs
    infoWs = websocket
    await utils.wsSend(infoWs, "init-db")

# Initialize our system and its modules
def init():
    asyncio.ensure_future(wsConnect(ML_WS_URI, onConnectionML, onReceptionFromML))
    asyncio.ensure_future(wsConnect(CAMERA_WS_URI, onConnectionCamera, onReceptionFromCamera))
    asyncio.ensure_future(wsConnect(INFO_WS_URI, onConnectionInfo, onReceptionFromInfo))
    utils.startWsServer(FRONT_MESSAGING_PORT, onReceptionFromFront, onConnectionToFrontClosed)
    asyncio.get_event_loop().run_forever()

# Sends an encoded image to the front
async def sendImageToFront(encodedImage):
    if frontWs != None:
        await utils.wsSend(frontWs, "image-base64", encodedImage)

# Called when receiving a message from the front-end
async def onReceptionFromFront(ws, head, body):
    global frontWs
    print("[FRONT > MAIN]", head)
    if head == "handshake":
        frontWs = ws

# Called when the connection with the front has been closed
def onConnectionToFrontClosed(e):
    global frontWs
    frontWs = None

init()
