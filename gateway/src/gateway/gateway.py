from bitshares import BitShares
from django.conf import settings
from transnet import Transnet

from gateway.models import BitsharesTransnetTransaction, TransnetBitsharesTransaction
from gateway.src.account.account_transfers_provider import TransnetAccountTransfersProvider, \
    BitsharesAccountTransfersProvider
from gateway.src.gateway.base_gateway import BaseGateway
from gateway.src.gateway.gateway_handler import TransnetGatewayHandler, BitsharesGatewayHandler
from site_settings.models import SettingsModel


class TransnetBasedGateway(BaseGateway):
    def __init__(self):
        self.site_settings = SettingsModel.load()
        self.transnet = Transnet(
            self.site_settings.transnet_bitshares_node_url,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': self.site_settings.transnet_bitshares_active_wif,
            }
        )
        self.transnet.set_default_account(self.site_settings.transnet_bitshares_gateway_address)

        super(TransnetBasedGateway, self).__init__()


class BitsharesBasedGateway(BaseGateway):
    def __init__(self):
        self.site_settings = SettingsModel.load()
        self.bitshares = BitShares(
            self.site_settings.bitshares_transnet_node_url,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': self.site_settings.bitshares_transnet_active_wif,
            },
        )
        self.bitshares.set_default_account(self.site_settings.bitshares_transnet_gateway_address)

        super(BitsharesBasedGateway, self).__init__()


class BitsharesTransnetGateway(TransnetBasedGateway, BitsharesBasedGateway):
    TRANSACTION_MODEL = BitsharesTransnetTransaction
    ASSETS_MAPPING = settings.BTS_TRNS_ASSETS_MAPPING

    def _create_transfers_handler(self):
        return BitsharesGatewayHandler(
            self.bitshares, self.site_settings.bitshares_transnet_gateway_address,
            self.transnet, self.site_settings.transnet_bitshares_gateway_address,
            self.site_settings.transnet_bitshares_memo_wif,
            self.ASSETS_MAPPING
        )

    def _create_transfers_provider(self):
        return BitsharesAccountTransfersProvider(
            self.bitshares, self.site_settings.bitshares_transnet_memo_wif,
            self.site_settings.bitshares_transnet_gateway_address,
            self.TRANSACTION_MODEL)


class TransnetBitsharesGateway(TransnetBasedGateway, BitsharesBasedGateway):
    TRANSACTION_MODEL = TransnetBitsharesTransaction
    ASSETS_MAPPING = settings.TRNS_BTS_ASSETS_MAPPING

    def _create_transfers_handler(self):
        return TransnetGatewayHandler(self.transnet, self.site_settings.transnet_bitshares_gateway_address,
                                      self.bitshares, self.site_settings.bitshares_transnet_gateway_address,
                                      self.site_settings.bitshares_transnet_memo_wif,
                                      self.ASSETS_MAPPING
                                      )

    def _create_transfers_provider(self):
        return TransnetAccountTransfersProvider(
            self.transnet, self.site_settings.transnet_bitshares_memo_wif,
            self.site_settings.transnet_bitshares_gateway_address,
            self.TRANSACTION_MODEL)
