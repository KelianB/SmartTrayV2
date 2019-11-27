import asyncio
import websockets
import json
import numpy as np


async def wsSend(websocket, head, body=""):
    dict = {"head": head, "body": body}
    asJSON = json.dumps(dict, cls=NpEncoder)
    await websocket.send(asJSON)

def startWsServer(port, onMessageReceived):
    async def listen(websocket, path):
        response = await websocket.recv()
        msg = json.loads(response)
        await onMessageReceived(websocket, msg["head"], msg["body"])
        await listen(websocket, path)
            
    asyncio.get_event_loop().run_until_complete(websockets.serve(listen, "", port, max_size=1e10))
    asyncio.get_event_loop().run_forever()

    
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