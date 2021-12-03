FROM docker.io/library/python:3.8
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python3.8 main.py