from gateway.src.account.base_account_listener_handler import BaseAccountListenerHandler


class BaseGatewayAccountListenerHandler(BaseAccountListenerHandler):
    def sync(self, transactions):
        raise NotImplementedError()