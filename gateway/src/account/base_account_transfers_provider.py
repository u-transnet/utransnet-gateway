class BaseAccountTransfersProvider:
    def fetch_all_transactions(self):
        raise NotImplementedError()

    def fetch_new_transactions(self):
        raise NotImplementedError()