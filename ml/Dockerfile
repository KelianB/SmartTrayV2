FROM jjanzic/docker-python3-opencv

COPY ./ml/ml.py .
COPY ./ml/yolo ./yolo
COPY ./utils/ .

RUN pip install websockets

CMD [ "python", "-u", "./ml.py" ]
