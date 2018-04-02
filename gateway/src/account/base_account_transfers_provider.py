class BaseAccountTransfersProvider:
    def __get_latest_transaction_id(self):
        raise NotImplementedError()

    def fetch_all_transactions(self):
        raise NotImplementedError()

    def fetch_new_transactions(self):
        raise NotImplementedError()