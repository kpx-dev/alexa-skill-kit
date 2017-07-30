FROM python:3-jessie

WORKDIR /home

RUN apt-get update && apt-get install build-essential python-dev libssl1.0.0 libssl-dev -y

CMD [ "python" ]