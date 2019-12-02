FROM python:3

COPY ./info/ .
COPY ./utils/ .

RUN pip install -r ./requirements.txt

CMD ["python", "-u", "./information.py"]
