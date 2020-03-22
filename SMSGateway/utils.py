import typing


def dict_fill_default(d: typing.Dict[str, any], key: str, default: any, override_none: bool = False):
    if key not in d:
        d[key] = default
    else:
        if override_none and (d[key] is None):
            d[key] = default
