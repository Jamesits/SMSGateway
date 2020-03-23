import typing

from SMSGateway.generic_vertex import GenericVertex


class GenericSource(GenericVertex):
    """Device definition"""
    vendor: str
    model: str

    def __init__(self, alias: str, object_type: str, local_config: typing.Dict[str, typing.Any], global_config: typing.Any):
        super().__init__(alias, object_type, local_config, global_config)
        self.vendor = local_config['vendor']
        self.model = local_config['model']
