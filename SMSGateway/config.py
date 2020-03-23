import typing

import toml

from SMSGateway.generic_event_queue import GenericEventQueue

args: typing.Any
user_config: typing.MutableMapping[str, typing.Any] = {}
queue: GenericEventQueue


def load_user_config(filename: str) -> None:
    global user_config
    user_config = toml.load(filename)
