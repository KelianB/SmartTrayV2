import asyncio
import websockets
import json
import utils
import cv2
import numpy as np
import base64
from time import time

yolo = None
PATH_CONFIG = "yolo/yolov2.cfg"
PATH_CLASSES = "yolo/classes.txt"
PATH_WEIGHTS = "yolo/yolov2.weights"

async def onReception(ws, head, body):
    print("[MAIN > ML]", head)

    if head == "start":                 
        await utils.wsSend(ws, "started")
    elif head == "imageBase64":
        img = imageFromBase64(body)
        items = processImage(img)
        await utils.wsSend(ws, "image-items", items)
        
def imageFromBase64(encoded):
    decoded = base64.b64decode(encoded)
    return cv2.imdecode(np.fromstring(decoded, dtype=np.uint8), -1)


# Initializes YOLO
def initializeModel():
    global yolo, PATH_CONFIG, PATH_CLASSES, PATH_WEIGHTS
    
    yolo = {
        "CONFIDENCE_THRESHOLD": 0.25,
        "NMS_THRESHOLD": 0.4
    }
    
    # Read class names from text file
    classes = None
    with open(PATH_CLASSES, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    
    yolo["classes"] = classes

    # Read pre-trained model and config file
    net = cv2.dnn.readNet(PATH_WEIGHTS, PATH_CONFIG)
    #net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL);
    yolo["net"] = net
    
    return net



# Runs an image through our model
def processImage(image):
    global yolo
    if yolo == None:
        print("Cannot process image through the NN: YOLO is not initialized.")
        return
        
    net = yolo["net"]

    # Parameters to play with to see how the response changes
    colorScale = 0.00392
    imageSize = 416
  
    t = time()  
  
    # Create input blob 
    blob = cv2.dnn.blobFromImage(image, colorScale, (imageSize, imageSize), (0,0,0), True, crop=False)
    
    # Set input blob for the network
    net.setInput(blob)
        
    # Run inference through the network and gather predictions from output layers        
    outs = net.forward(_getOutputLayers(net))   
  
    width, height = image.shape[1], image.shape[0]
    
    detectedItems = []
    confidences = []
    boxes = []
    
    # For each detection from each output layer, get the confidence, class id and bounding box params 
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            # Ignore weak detections (low confidence)
            if confidence > yolo["CONFIDENCE_THRESHOLD"]:
                # Detection coordinates are relative to image dimensions
                centerX, centerY, w, h = detection[0], detection[1], detection[2], detection[3]
                x = centerX - w/2
                y = centerY - h/2

                item = {
                    "label": str(yolo["classes"][class_id]),
                    "classID": class_id,
                    "box": [x, y, w, h],
                    "confidence": float(confidence)
                }
                detectedItems.append(item)
                
                confidences.append(item["confidence"])
                boxes.append([x * width, y * height, w * width, h * height])
                
    # Apply non-max suppression (removes boxes with high overlap to avoid duplicates)
    indices = cv2.dnn.NMSBoxes(boxes, confidences, yolo["CONFIDENCE_THRESHOLD"], yolo["NMS_THRESHOLD"])
    
    # Go through the detections remaining after nms
    remainingItems = []
    for i in indices:
        remainingItems.append(detectedItems[i[0]])
    
    print("[ML] Processed image in", time() - t, "s.")      
    
    return remainingItems
    
# Function to get the output layer names of the neural nets
def _getOutputLayers(net):
    layer_names = net.getLayerNames()    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


initializeModel()
print("ML module successfully initialized")
utils.startWsServer(5002, onReception)