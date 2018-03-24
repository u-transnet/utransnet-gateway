from time import sleep

from .account_transfers_processor import AccountTransfersProcessor


class AccountTransfersListener(object):
    UPDATE_TIME_DEFAULT = 5
    handlers = []

    def __init__(self, blockchain_api, account_address, transaction_model, update_time=UPDATE_TIME_DEFAULT):
        self.transfers_processors = AccountTransfersProcessor(blockchain_api, account_address, transaction_model)
        self.update_time = update_time
        self.run = False

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
