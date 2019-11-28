import asyncio
import websockets
import json
import utils
from time import time
import base64
import cv2
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
                """
                except websockets.exceptions.ConnectionClosed:
                    print("Connection with", URI, "was closed")
                    break
                """
    except Exception as e:
        print("Connection with " + URI + " threw an exception:", e);


async def onReceptionFromCamera(ws, head, body):
    global mlWs, isMLWorking, cameraConnectionTime
    print("[MAIN < CAMERA]", head)

    if head == "started":
        pass
    elif head == "imageBase64":
        latency = time() - body["time"]
        print("latency", latency, "(connected since", time() - cameraConnectionTime, ")")

        await sendImageToFront(body["data"])
        if not isMLWorking:
            isMLWorking = True
            #await utils.wsSend(mlWs, "imageBase64", body["data"])


async def onReceptionFromML(ws, head, body):
    global frontWs, isMLWorking
    print("[MAIN < ML]", head)

    if head == "image-items":
        isMLWorking = False
        if frontWs != None:
            await utils.wsSend(frontWs, "labels", body)

        # TODO send get-info to info service with the name of the item

async def onReceptionFromInfo(ws, head, body):
    print("[MAIN < INFO]", head)

    if head == "db-ready":
        # Test
        pass
        #await utils.wsSend(ws, "get-info", ["Veau", "Lapin", "Farine"])
    if head == "info":
        # TODO do something with info
        print(body)


async def onConnectionML(websocket):
    global mlWs
    mlWs = websocket

async def onConnectionCamera(websocket):
    global cameraWs
    global cameraConnectionTime
    cameraConnectionTime = time()
    cameraWs = websocket

async def onConnectionInfo(websocket):
    global infoWs
    infoWs = websocket
    await utils.wsSend(infoWs, "init-db")

def startWsServer(port, onMessageReceived, onConnectionClosed=None):
    async def listen(websocket, path):
        try:
            while True:
                response = await websocket.recv()
                msg = json.loads(response)
                await onMessageReceived(websocket, msg["head"], msg["body"])
        except Exception as e:
            print("WebSocket connection was closed:", e)
            if onConnectionClosed is not None:
                onConnectionClosed(e);

    asyncio.ensure_future(websockets.serve(listen, "", port, max_size=1e10))


# Initialize our system and its modules
def init():
    asyncio.ensure_future(wsConnect(ML_WS_URI, onConnectionML, onReceptionFromML))
    asyncio.ensure_future(wsConnect(CAMERA_WS_URI, onConnectionCamera, onReceptionFromCamera))
    asyncio.ensure_future(wsConnect(INFO_WS_URI, onConnectionInfo, onReceptionFromInfo))
    startWsServer(5000, onReceptionFromFront, onConnectionToFrontClosed)
    asyncio.get_event_loop().run_forever()


def imageFromBase64(encoded):
    decoded = base64.b64decode(encoded)
    return cv2.imdecode(np.fromstring(decoded, dtype=np.uint8), -1)


def onConnectionToFrontClosed(e):
    global frontWs
    frontWs = None

# Displays an image and the given items (with label & boxes)
async def sendImageToFront(encodedImage):
    global frontWs
    if frontWs != None:
        await utils.wsSend(frontWs, "image-base64", encodedImage)

async def onReceptionFromFront(ws, head, body):
    global frontWs
    print("[FRONT > MAIN]", head)
    if head == "handshake":
        frontWs = ws



init()
