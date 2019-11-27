FROM python:3

COPY ./info/ .
COPY ./utils/ .

RUN pip install websockets
RUN pip install pymysql
RUN pip install numpy

CMD [ "python", "-u", "./information.py" ]
