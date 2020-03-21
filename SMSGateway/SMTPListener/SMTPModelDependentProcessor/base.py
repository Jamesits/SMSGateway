from abc import ABCMeta, abstractmethod


class SMTPMailProcessorBase:
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def process(device, session, envelope): raise NotImplementedError
