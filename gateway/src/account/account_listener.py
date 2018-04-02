from threading import Condition, Lock

import signal


class ListenerState:
    _active = False
    _lock = Lock()

    @property
    def active(self):
        with self._lock:
            return self._active

    @active.setter
    def active(self, value):
        with self._lock:
            self._active = value


class AccountTransfersListener:
    UPDATE_TIME_DEFAULT = 5
    handlers = []

    def __init__(self, transfer_provider, update_time=UPDATE_TIME_DEFAULT):
        self.transfers_provider = transfer_provider
        self.update_time = update_time
        self.state = ListenerState()
        self.blocker = Condition(Lock())
        self.__register_signal_handlers()

    def __register_signal_handlers(self):

        def gracefully_stop(*args, **kwargs):
            self.stop()

        def create_handler(new_handler, signalnum):
            old_handler = signal.getsignal(signalnum)

            def wrapper(*args, **kwargs):
                new_handler(*args, **kwargs)
                old_handler(*args, **kwargs)

            return wrapper

        signal.signal(signal.SIGINT, create_handler(gracefully_stop, signal.SIGINT))
        signal.signal(signal.SIGTERM, create_handler(gracefully_stop, signal.SIGTERM))

    def _create_transfers_processor(self, blockchain_api, account_address, transaction_model, memo_wif):
        raise NotImplementedError()

    def add_handler(self, handler):
        self.handlers.append(handler)

    def start(self):
        self.active = True
        self.blocker.acquire()
        try:
            while self.active:
                new_transactions = self.transfers_provider.fetch_new_transactions()
                for handler in self.handlers:
                    handler.handle(new_transactions, lambda: self.active)
                if self.active:
                    self.blocker.wait(self.update_time)
        finally:
            self.blocker.release()

    def stop(self):
        self.active = False
        try:
            self.blocker.acquire()
            self.blocker.notify()
        finally:
            self.blocker.release()

    @property
    def active(self):
        return self.state.active

    @active.setter
    def active(self, value):
        self.state.active = value
