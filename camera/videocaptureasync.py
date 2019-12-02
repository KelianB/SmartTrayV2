import threading
import cv2

# This class allows us to use OpenCV's video capture interface asynchronously
class VideoCaptureAsync:
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.cap.read()
        self.started = False

        if not self.grabbed:
             raise Exception("Unable to capture a picture from source " + src)

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print("[!] Asynchronous video capturing has already been started.")
            return None
        self.started = True
        self.thread = threading.Thread(target=self._captureLoop, args=())
        self.thread.start()
        return self

    def _captureLoop(self):
        while self.started:
            grabbed, frame = self.cap.read()
            if grabbed:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        if self.frame is None:
            return False, None
        return self.grabbed, self.frame.copy()

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()
