class AccountListenerBaseHandler(object):
    def handle(self, transactions, get_is_active):
        raise NotImplementedError()
