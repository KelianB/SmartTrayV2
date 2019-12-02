FROM jjanzic/docker-python3-opencv

COPY ./camera/ .
COPY ./utils/ .

RUN pip install -r ./requirements.txt

CMD ["python", "-u", "./camera.py"]
