import os
import typing

from SMSGateway.sms import SMS


def dict_value_normalize(
        d: typing.Dict[str, any],
        key: str,
        default: any = None,
        override_none: bool = False,
        to_lower: bool = False,
        trim: bool = False,
):
    if default is not None:
        if key not in d:
            d[key] = default
        else:
            if override_none and (d[key] is None):
                d[key] = default

    if key in d and isinstance(d[key], str):
        if to_lower:
            d[key] = d[key].lower()
        if trim:
            d[key] = d[key].strip()


def create_mustache_context_from_sms(sms: SMS):
    return {
        'sender': sms.sender,
        'receiver': sms.receiver,
        'content': sms.content,
        'received_at': sms.received_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


def find_first_existing_file(f_list: typing.List[str]) -> str:
    for f in f_list:
        if os.path.isfile(f):
            return f
    return ""
