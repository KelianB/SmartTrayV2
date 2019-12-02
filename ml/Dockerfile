FROM jjanzic/docker-python3-opencv

COPY ./ml/ml.py .
COPY ./ml/requirements.txt .
COPY ./ml/yolo ./yolo
COPY ./utils/ .

RUN pip install -r requirements.txt

CMD ["python", "-u", "./ml.py"]
