FROM jjanzic/docker-python3-opencv

COPY ./camera/camera.py .
COPY ./camera/videocaptureasync.py .
COPY ./utils/ .

RUN pip install websockets

CMD [ "python", "-u", "./camera.py" ]
