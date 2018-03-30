from time import sleep

from gateway.src.account.account_transfers_processor import BitSharesAccountTransfersProcessor, \
    TransnetAccountTransfersProcessor


class BaseAccountTransfersListener(object):
    UPDATE_TIME_DEFAULT = 5
    handlers = []

    def __init__(self, blockchain_api, memo_wif, account_address, transaction_model, update_time=UPDATE_TIME_DEFAULT):
        self.transfers_processors = self._create_transfers_processor(blockchain_api, memo_wif, account_address,
                                                                     transaction_model)
        self.update_time = update_time
        self.run = False

    def _create_transfers_processor(self, blockchain_api, account_address, transaction_model, memo_wif):
        raise NotImplementedError()

    def add_handler(self, handler):
        self.handlers.append(handler)

    def start(self):
        self.run = True
        while self.run:
            new_transactions = self.transfers_processors.process_transactions()
            for handler in self.handlers:
                handler.handle(new_transactions)
            if self.run:
                sleep(self.update_time)

    def stop(self):
        self.run = False


class BitSharesAccountTransfersListener(BaseAccountTransfersListener):
    def _create_transfers_processor(self, blockchain_api, memo_wif, account_address, transaction_model):
        return BitSharesAccountTransfersProcessor(blockchain_api, memo_wif, account_address, transaction_model)

class TransnetAccountTransfersListener(BaseAccountTransfersListener):
    def _create_transfers_processor(self, blockchain_api, memo_wif, account_address, transaction_model):
        return TransnetAccountTransfersProcessor(blockchain_api, memo_wif, account_address, transaction_model)