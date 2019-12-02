import asyncio
import websockets
import json
import numpy as np

async def wsSend(websocket, head, body=""):
    dict = {"head": head, "body": body}
    asJSON = json.dumps(dict, cls=NpEncoder)
    await websocket.send(asJSON)

def startWsServer(port, onMessageReceived, onConnectionClosed=None):
    async def listen(websocket, path):
        try:
            while True:
                response = await websocket.recv()
                msg = json.loads(response)
                await onMessageReceived(websocket, msg["head"], msg["body"])
        except Exception as e:
            print("WebSocket connection threw an exception:", e)
            if onConnectionClosed is not None:
                onConnectionClosed()

    asyncio.ensure_future(websockets.serve(listen, "", port, max_size=1e10, max_queue=None, read_limit=1e14, write_limit=1e14))

def imageFromBase64(encoded):
    from base64 import b64decode
    from cv2 import imdecode

    decoded = b64decode(encoded)
    imgData = np.fromstring(decoded, dtype=np.uint8)
    return imdecode(imgData, -1)

def imageToBase64(img):
    from base64 import b64encode
    from cv2 import imencode

    retval, buffer = imencode(".jpg", img)
    if retval:
        jpgAsText = b64encode(buffer)
        return str(jpgAsText, "utf-8")
    else:
        return None

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)
