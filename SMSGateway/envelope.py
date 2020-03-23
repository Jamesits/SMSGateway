import dataclasses
import typing

# https://github.com/python/mypy/blob/master/docs/source/common_issues.rst#import-cycles
if typing.TYPE_CHECKING:
    from SMSGateway.generic_vertex import GenericVertex
    from SMSGateway.sms import SMS


@dataclasses.dataclass
class Envelope:
    """A message in the global event queue"""
    from_vertex: "GenericVertex"
    to_vertex: "GenericVertex"
    sms: "SMS"
