import typing

from SMSGateway.sms import SMS


def dict_fill_default(d: typing.Dict[str, any], key: str, default: any, override_none: bool = False):
    if key not in d:
        d[key] = default
    else:
        if override_none and (d[key] is None):
            d[key] = default


def create_mustache_context_from_sms(sms: SMS):
    return {
        'sender': sms.sender,
        'receiver': sms.receiver,
        'content': sms.content,
        'received_at': sms.received_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
