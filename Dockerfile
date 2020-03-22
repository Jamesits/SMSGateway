FROM python:3-buster
LABEL maintainer="docker@public.swineson.me"

COPY . /tmp/SMSGateway

RUN cd /tmp/SMSGateway \
    && python3 setup.py install \
    && cd \
    && rm -r /tmp/SMSGateway

CMD [ "smsgateway" ]
