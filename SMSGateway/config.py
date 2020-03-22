import typing

import toml

from SMSGateway.generic_event_queue import GenericEventQueue

args: any
user_config: typing.Dict[str, any] = {}
queue: GenericEventQueue


def load_user_config(filename: str) -> None:
    global user_config
    user_config = toml.load(filename)
