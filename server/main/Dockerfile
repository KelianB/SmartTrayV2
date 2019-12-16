FROM jjanzic/docker-python3-opencv
# FROM python:3

COPY ./main/ .
COPY ./utils/ .

RUN pip install -r ./requirements.txt

EXPOSE 5000

CMD ["python", "-u", "./main.py"]
