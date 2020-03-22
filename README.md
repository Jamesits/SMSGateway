# SMSGateway

SMS routing toolkit for VOIP devices.

This project is currently under heavy development. Expect config format incompatibility at any new version.

## Running

At project root:

```shell
python3 -m SMSGateway
```

## Supported Protocols

### Receiving

Generic:

* SMTP
* SMPP

Vendor specific:

* [Dbltek SMS Server](SMSGateway/DbltekSmsListener)

## Sending

* SMTP 