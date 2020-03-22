import dataclasses


@dataclasses.dataclass
class Envelope:
    from_vertex: "SMSGateway.generic_vertex.GenericVertex"
    to_vertex: "SMSGateway.generic_vertex.GenericVertex"
    sms: "SMSGateway.sms.SMS"
