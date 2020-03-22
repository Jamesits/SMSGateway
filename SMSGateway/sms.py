import dataclasses
import datetime


@dataclasses.dataclass
class SMS:
    sender: str
    receiver: str
    content: str
    received_at: datetime.datetime
