FROM python:3.11

WORKDIR /backend

COPY entrypoint.sh /entrypoint.sh
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY src/ src/
