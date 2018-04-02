from threading import Condition, Lock

import signal

from gateway.src.account.account_transfers_processor import BitSharesAccountTransfersProcessor, \
    TransnetAccountTransfersProcessor


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


class BaseAccountTransfersListener:
    UPDATE_TIME_DEFAULT = 5
    handlers = []

    def __init__(self, blockchain_api, memo_wif, account_address, transaction_model, update_time=UPDATE_TIME_DEFAULT):
        self.transfers_processors = self._create_transfers_processor(blockchain_api, memo_wif, account_address,
                                                                     transaction_model)
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
        self.state.active = True
        self.blocker.acquire()
        try:
            while self.state.active:
                new_transactions = self.transfers_processors.process_transactions()
                for handler in self.handlers:
                    handler.handle(new_transactions, lambda: self.state.active)
                if self.state.active:
                    self.blocker.wait(self.update_time)
        finally:
            self.blocker.release()

    def stop(self):
        self.state.active = False
        try:
            self.blocker.acquire()
            self.blocker.notify()
        finally:
            self.blocker.release()


class BitSharesAccountTransfersListener(BaseAccountTransfersListener):
    def _create_transfers_processor(self, blockchain_api, memo_wif, account_address, transaction_model):
        return BitSharesAccountTransfersProcessor(blockchain_api, memo_wif, account_address, transaction_model)


class TransnetAccountTransfersListener(BaseAccountTransfersListener):
    def _create_transfers_processor(self, blockchain_api, memo_wif, account_address, transaction_model):
        return TransnetAccountTransfersProcessor(blockchain_api, memo_wif, account_address, transaction_model)
