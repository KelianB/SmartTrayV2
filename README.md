# SmartTray
Computer vision project for Accenture, developed by 6 students at IMT Atlantique.
This program reads a video feed from a camera and displays real-time labels and information about food on a meal tray.
It uses OpenCV for computer vision and machine learning.

## Dependencies
### Weight files
For this to work, you have to download the weights at https://pjreddie.com/media/files/yolov3.weights
and put the file in the "yolo" directory with the name "yolov3.weights".

### How to use
This project was was made to work with Docker. Once Docker is installed, navigate to the root directory and type:
```
sudo docker-compose up
```
You can then open the app by launching the index file (in the "front" directory) with your preferred browser.

By default, the camera is configured to capture images from a USB webcam. You can switch to an IP camera by changing one line in camera/camera.py.

## Improvements
- Add more feedback to the front for errors (e.g. when the server can't reach the camera)
- Add more documentation for WebSockets between containers
