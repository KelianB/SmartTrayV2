FROM jjanzic/docker-python3-opencv

COPY ./camera/ .
COPY ./utils/ .

RUN pip install websockets

CMD [ "python", "-u", "./camera.py" ]
