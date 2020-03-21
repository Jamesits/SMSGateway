class IListener:
    def __init__(self: "IListener", current_listener: any, config: any):
        raise NotImplementedError

    def start(self: "IListener"):
        raise NotImplementedError

    def stop(self: "IListener"):
        raise NotImplementedError
