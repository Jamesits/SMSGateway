# SMSGateway

SMS routing server for VOIP/GOIP devices.

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