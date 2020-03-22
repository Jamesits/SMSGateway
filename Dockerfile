FROM python:3-buster
LABEL maintainer="docker@public.swineson.me"

RUN apt-get update \
	&& apt-get upgrade -y \
	&& apt-get install -y python3 python3-pip python3-setuptools \
	&& rm -rf /var/lib/apt/lists/*

COPY . /tmp/SMSGateway

RUN cd /tmp/SMSGateway \
    && python3 setup.py install \
    && cd \
    && rm -r /tmp/SMSGateway

CMD [ "smsgateway" ]
