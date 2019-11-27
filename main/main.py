import asyncio
import websockets
import json
import utils
from datetime import datetime
import matplotlib.pyplot as plt
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

async def wsConnect(URI, onConnection, onMessageReceived):
    print("Connecting to", URI, "...")
    
    async def listen(websocket):
        response = await websocket.recv()   
        msg = json.loads(response)
        await onMessageReceived(websocket, msg["head"], msg["body"])
        await listen(websocket)    
    
    async with websockets.connect(URI, max_size=1e10) as websocket:
        await onConnection(websocket)
        await utils.wsSend(websocket, "start")
        await listen(websocket)

async def onReceptionFromCamera(ws, head, body):
    global mlWs
    print("[MAIN < CAMERA]", head)
    
    if head == "started":
        await utils.wsSend(ws, "takepicture")        
    elif head == "imageBase64":
        testShowImg(imageFromBase64(body))
        await utils.wsSend(mlWs, "imageBase64", body)
                    
async def onReceptionFromML(ws, head, body):
    print("[MAIN < ML]", head)
    
    if head == "image-items":
        itemNames = []
        for i in body:
            itemNames.append(i["label"])        
        print(body)
        
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
    cameraWs = websocket

async def onConnectionInfo(websocket):
    global infoWs
    infoWs = websocket
    await utils.wsSend(infoWs, "init-db")

     
# Initialize our system and its modules
def init():
    asyncio.ensure_future(wsConnect(ML_WS_URI, onConnectionML, onReceptionFromML)) 
    asyncio.ensure_future(wsConnect(CAMERA_WS_URI, onConnectionCamera, onReceptionFromCamera))
    asyncio.ensure_future(wsConnect(INFO_WS_URI, onConnectionInfo, onReceptionFromInfo))    
    asyncio.get_event_loop().run_forever()
            
def imageFromBase64(encoded):
    decoded = base64.b64decode(encoded)
    return cv2.imdecode(np.fromstring(decoded, dtype=np.uint8), -1)


# Displays an image and the given items (with label & boxes)
def testShowImg(img):
    print("show image")
    width, height = img.shape[1], img.shape[0]
    
    plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
    plt.show()
    
    # Create the window
    """cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", width, height)
    # Display the image
    cv2.imshow("image", img)    
    # Wait for keypress
    cv2.waitKey()
    cv2.destroyWindow("image")
    """

init()