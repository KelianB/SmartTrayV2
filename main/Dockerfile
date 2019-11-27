FROM jjanzic/docker-python3-opencv
# FROM python:3

COPY ./main/ .
COPY ./utils/ .


RUN pip install websockets
RUN pip install matplotlib

ENV DISPLAY=$DISPLAY

CMD [ "python", "-u", "./main.py" ]
