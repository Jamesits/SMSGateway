# SMSGateway

SMS routing server for VOIP/GOIP devices.

[![Build Status](https://dev.azure.com/nekomimiswitch/General/_apis/build/status/SMSGateway?branchName=master)](https://dev.azure.com/nekomimiswitch/General/_build/latest?definitionId=79&branchName=master) [![](https://images.microbadger.com/badges/image/jamesits/smsgateway.svg)](https://microbadger.com/images/jamesits/smsgateway "Get your own image badge on microbadger.com")

Use with caution: config file format might change at any version.

## Supported Devices
* Synway SMG4008

## Supported Protocols

### Receiving
Generic:
* SMPP

### Sending
* SMTP
* Telegram Bot

## Running

Put your config file at `/etc/smsgateway/config.toml`.

### Docker

```shell
docker run --rm -it --name=smsgateway -v /etc/smsgateway:/etc/smsgateway:ro jamesits/smsgateway:latest
```

### Local Installation
At project root:

```shell
python3 -m SMSGateway
```