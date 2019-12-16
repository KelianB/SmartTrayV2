# SmartTray
Computer vision project for Accenture, developed by 6 students at IMT Atlantique.
This program reads a video feed from a camera and displays real-time labels and information about food on a meal tray.
It uses OpenCV for computer vision and machine learning.

## Dependencies
### Weights file
For this to work, you have to download the weights at https://pjreddie.com/media/files/yolov2.weights
and put the file in the ml/yolo directory with the name "yolov2.weights".

### Docker
You will need docker installed in order to run the server.

## How to use
Once Docker is installed, navigate to the root directory of this project and type:
```
sudo docker-compose up
```
You can then open the app by launching the index file (in the "front" directory) with your preferred browser.
By default, the camera is configured to capture images from a USB webcam. You can switch to an IP camera by changing one line in camera/camera.py.

## Improvements
- Retrain the model to recognize food specifically.
- Add more feedback to the front for errors (e.g. when the server can't reach the camera).
- Add more documentation regarding the expected WebSocket messages between containers.
- While Yolo V2 seemed faster for this application, it would be worth studying the speed and accuracy difference between Yolo V2 and V3.
