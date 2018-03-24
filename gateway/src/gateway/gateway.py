from bitshares import BitShares

from gateway import settings
from gateway.models import BitsharesTransaction, TransnetTransaction
from gateway.src.account.account_listener import AccountTransfersListener
from gateway.src.gateway.gateway_handler import GatewayHandler


class BitsharesGateway(object):

    ASSETS_MAPPING = {
        'UT.TEST': 'UT.TEST'
    }

    def __init__(self):
        self.bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.BITSHARES_GATEWAY_WIF]
        )

        self.transnet = BitShares(
            settings.TRANSNET_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.TRANSNET_GATEWAY_WIF]
        )

        self.transfer_listener = AccountTransfersListener(
            self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT, BitsharesTransaction)
        handler = GatewayHandler(
            BitsharesTransaction, self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT,
            self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT,
            self.ASSETS_MAPPING
        )

        self.transfer_listener.add_handler(handler)

    def start(self):
        self.transfer_listener.start()

    def stop(self):
        self.transfer_listener.stop()


class TransnetGateway(object):
    ASSETS_MAPPING = {
        'UT.TEST': 'UT.TEST'
    }

    def __init__(self):
        self.bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.BITSHARES_GATEWAY_WIF]
        )

        self.transnet = BitShares(
            settings.TRANSNET_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.TRANSNET_GATEWAY_WIF]
        )

        self.transfer_listener = AccountTransfersListener(
            self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT, TransnetTransaction)
        handler = GatewayHandler(
            TransnetTransaction, self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT,
            self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT,
            self.ASSETS_MAPPING
        )

        self.transfer_listener.add_handler(handler)

    def start(self):
        self.transfer_listener.start()

    def stop(self):
        self.transfer_listener.stop()