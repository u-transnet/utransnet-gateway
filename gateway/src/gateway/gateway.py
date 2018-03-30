from bitshares import BitShares
from bitshares.asset import Asset as BitsharesAsset

from transnet import Transnet
from transnet.asset import Asset as TransnetAsset

from gateway import settings
from gateway.models import BitsharesTransaction, TransnetTransaction
from gateway.src.account.account_listener import AccountTransfersListener
from gateway.src.gateway.gateway_handler import TransnetGatewayHandler, BitsharesGatewayHandler


class BaseGateway(object):
    def __init__(self):
        self.bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.BITSHARES_GATEWAY_WIF]
        )
        self.bitshares.set_default_account(settings.BITSHARES_GATEWAY_ACCOUNT)

        self.transnet = Transnet(
            settings.TRANSNET_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.TRANSNET_GATEWAY_WIF]
        )
        self.transnet.set_default_account(settings.TRANSNET_GATEWAY_ACCOUNT)
        self.transfer_listener = self._create_transfer_listener()

    def _create_transfer_listener(self):
        self.transfer_listener = None
        raise NotImplementedError

    def start(self):
        self.transfer_listener.start()

    def stop(self):
        self.transfer_listener.stop()


class BitsharesGateway(BaseGateway):
    ASSETS_MAPPING = {
        'UTECH.UTCORE': TransnetAsset('UTECH.UTCORE')
    }

    def _create_transfer_listener(self):
        transfer_listener = AccountTransfersListener(
            self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT, BitsharesTransaction)
        handler = BitsharesGatewayHandler(
            self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT,
            self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT,
            'BTS', self.ASSETS_MAPPING
        )
        transfer_listener.add_handler(handler)
        return transfer_listener


class TransnetGateway(BaseGateway):
    ASSETS_MAPPING = {
        'UTECH.UTCORE': BitsharesAsset('UTECH.UTCORE')
    }

    def _create_transfer_listener(self):
        transfer_listener = AccountTransfersListener(
            self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT, TransnetTransaction)
        handler = TransnetGatewayHandler(self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT,
                                         self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT,
                                         'UTT', self.ASSETS_MAPPING
                                         )
        transfer_listener.add_handler(handler)
        return transfer_listener
