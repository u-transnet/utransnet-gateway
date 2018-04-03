from bitshares import BitShares
from django.conf import settings
from transnet import Transnet

from gateway.models import BitsharesTransaction, TransnetTransaction
from gateway.src.account.account_transfers_provider import TransnetAccountTransfersProvider, \
    BitsharesAccountTransfersProvider
from gateway.src.gateway.base_gateway import BaseGateway
from gateway.src.gateway.gateway_handler import TransnetGatewayHandler, BitsharesGatewayHandler


class TransnetBasedGateway(BaseGateway):
    def __init__(self):
        self.transnet = Transnet(
            settings.TRANSNET_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': settings.TRANSNET_GATEWAY_WIF,
            }
        )
        self.transnet.set_default_account(settings.TRANSNET_GATEWAY_ACCOUNT)

        super(TransnetBasedGateway, self).__init__()


class BitsharesBasedGateway(BaseGateway):
    def __init__(self):
        self.bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': settings.BITSHARES_GATEWAY_WIF,
            },
        )
        self.bitshares.set_default_account(settings.BITSHARES_GATEWAY_ACCOUNT)

        super(BitsharesBasedGateway, self).__init__()


class BitsharesTransnetGateway(TransnetBasedGateway, BitsharesBasedGateway):
    TRANSACTION_MODEL = BitsharesTransaction
    ASSETS_MAPPING = settings.BTS_TRNS_ASSETS_MAPPING

    def _create_transfers_handler(self):
        return BitsharesGatewayHandler(
            self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT,
            self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT, settings.TRANSNET_GATEWAY_WIF_MEMO,
            self.ASSETS_MAPPING
        )

    def _create_transfers_provider(self):
        return BitsharesAccountTransfersProvider(
            self.bitshares, settings.BITSHARES_GATEWAY_WIF_MEMO, settings.BITSHARES_GATEWAY_ACCOUNT,
            self.TRANSACTION_MODEL)


class TransnetBitsharesGateway(TransnetBasedGateway, BitsharesBasedGateway):
    TRANSACTION_MODEL = TransnetTransaction
    ASSETS_MAPPING = settings.TRNS_BTS_ASSETS_MAPPING

    def _create_transfers_handler(self):
        return TransnetGatewayHandler(self.transnet, settings.TRANSNET_GATEWAY_ACCOUNT,
                               self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT, settings.BITSHARES_GATEWAY_WIF_MEMO,
                               self.ASSETS_MAPPING
                               )

    def _create_transfers_provider(self):
        return TransnetAccountTransfersProvider(
            self.transnet, settings.TRANSNET_GATEWAY_WIF_MEMO, settings.TRANSNET_GATEWAY_ACCOUNT,
            self.TRANSACTION_MODEL)
