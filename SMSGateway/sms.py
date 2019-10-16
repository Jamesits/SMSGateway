class SMS(dict):
    def __init__(self, *args, **kwargs):
        self.transport_sender_uri = None
        self.transport_receiver_uri = None
        self.sms_sender = None
        self.sms_receiver = None
        self.sms_content = None
        self.sms_received_time = None

        super(SMS, self).__init__(*args, **kwargs)
        self.__dict__ = self

