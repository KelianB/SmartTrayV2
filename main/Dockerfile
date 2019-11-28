FROM jjanzic/docker-python3-opencv
# FROM python:3

COPY ./main/ .
COPY ./utils/ .

EXPOSE 5000

RUN pip install websockets

CMD [ "python", "-u", "./main.py" ]
