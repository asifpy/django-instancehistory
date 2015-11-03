# -*- coding: utf-8 -*-

from django.dispatch import Signal


class UnauthorizedSignalReceiver(Exception):
    pass


class SingleHandlerSignal(Signal):

    allowed_receiver = 'instancehistory.middleware.RequestProvider'

    def __init__(self, providing_args = None):
        return Signal.__init__(self,providing_args)

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        receiver_name = '.'.join([receiver.__class__.__module__,
            receiver.__class__.__name__])
        if receiver_name != self.allowed_receiver:
            raise UnauthorizedSignalReceiver()
        Signal.connect(self, receiver, sender, weak, dispatch_uid)


request_accessor = SingleHandlerSignal()


def get_request():
    signal_response = request_accessor.send(None)
    if not signal_response:
        return None
    return signal_response[0][1]

