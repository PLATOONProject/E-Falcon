FROM ubuntu:18.04

WORKDIR /eFalcon
ADD . /eFalcon

RUN apt-get --assume-yes update
RUN apt-get --assume-yes install python3.7 python3-pip
RUN pip3 install -r /eFalcon/requirements.txt
RUN pip3 install spacy==2.2.4
RUN pip3 install -U flask-cors

RUN python3 -m spacy download en


EXPOSE 5005

ENTRYPOINT /usr/bin/python3 /eFalcon/api.py
