import threading

from bitshares import BitShares
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils.timezone import now
from transnet import Transnet

from gateway.models import BitsharesTransnetTransaction, TransnetBitsharesTransaction
from gateway.src.account.account_listener import AccountTransfersListener
from gateway.src.account.base_account_listener_handler import BaseAccountListenerHandler
from gateway.src.account.account_transfers_provider import BitsharesAccountTransfersProvider, \
    TransnetAccountTransfersProvider
from gateway.src.gateway.gateway_handler import BitsharesGatewayHandler, TransnetGatewayHandler


class TestAccountListenerHandler(BaseAccountListenerHandler):
    processed = False

    def handle(self, transactions, get_is_active):
        self.processed = True


@override_settings(BLOCKCHAIN_NOBROADCAST=True)
class BitSharesGatewayTest(TestCase):
    def test_account_listener(self):
        self.bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': settings.BITSHARES_GATEWAY_WIF,
                'memo': settings.BITSHARES_GATEWAY_WIF_MEMO
            }
        )

        handler = TestAccountListenerHandler()

        transfers_provider = BitsharesAccountTransfersProvider(
            self.bitshares, settings.BITSHARES_GATEWAY_WIF_MEMO, settings.BITSHARES_GATEWAY_ACCOUNT,
            BitsharesTransnetTransaction
        )
        transfer_listener = AccountTransfersListener(transfers_provider)
        transfer_listener.add_handler(handler)

        threading.Thread(target=lambda: transfer_listener.start()).start()
        max_waiting_seconds = 15
        start_time = now()

        while not handler.processed and (now() - start_time).seconds < max_waiting_seconds:
            pass

        transfer_listener.stop()
        self.assertTrue(handler.processed, 'No one transactions were handled')

    def test_gateway_handler(self):
        bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.BITSHARES_GATEWAY_WIF]
        )
        bitshares.set_default_account(settings.BITSHARES_GATEWAY_ACCOUNT)

        transnet = Transnet(
            settings.TRANSNET_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': settings.TRANSNET_GATEWAY_WIF,
                'memo': settings.TRANSNET_GATEWAY_WIF_MEMO
            }
        )
        transnet.set_default_account(settings.TRANSNET_GATEWAY_ACCOUNT)

        transaction = BitsharesTransnetTransaction.objects.create(
            trx_id='test',
            trx_in_block=3,
            op_in_trx=3,
            asset='UTECH.UTCORE',
            amount=pow(10, 5),
            account_external='superpchelka23',
            account_internal='superpchelka23'
        )

        handler = BitsharesGatewayHandler(bitshares, settings.BITSHARES_GATEWAY_ACCOUNT,
                                          transnet, settings.TRANSNET_GATEWAY_ACCOUNT, settings.TRANSNET_GATEWAY_WIF_MEMO,
                                          {
                                              'UTECH.UTCORE': 'UTECH.UTCORE'
                                          })

        handler.handle([transaction], lambda: True)

        self.assertTrue(transaction.closed, 'Transaction must be properly processed')


@override_settings(BLOCKCHAIN_NOBROADCAST=True)
class TransnetGatewayTest(TestCase):
    def test_account_listener(self):
        self.transnet = Transnet(
            settings.TRANSNET_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': settings.TRANSNET_GATEWAY_WIF,
                'memo': settings.TRANSNET_GATEWAY_WIF_MEMO
            }
        )

        handler = TestAccountListenerHandler()
        transfers_provider = TransnetAccountTransfersProvider(self.transnet,
                                                              settings.TRANSNET_GATEWAY_WIF_MEMO,
                                                              settings.TRANSNET_GATEWAY_ACCOUNT, TransnetBitsharesTransaction)
        transfer_listener = AccountTransfersListener(transfers_provider)
        transfer_listener.add_handler(handler)

        threading.Thread(target=lambda: transfer_listener.start()).start()
        max_waiting_seconds = 15
        start_time = now()

        while not handler.processed and (now() - start_time).seconds < max_waiting_seconds:
            pass

        transfer_listener.stop()
        self.assertTrue(handler.processed, 'No one transactions were handled')

    def test_gateway_handler(self):
        bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys={
                'active': settings.BITSHARES_GATEWAY_WIF,
                'memo': settings.BITSHARES_GATEWAY_WIF_MEMO
            }
        )
        bitshares.set_default_account(settings.BITSHARES_GATEWAY_ACCOUNT)

        transnet = Transnet(
            settings.TRANSNET_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.TRANSNET_GATEWAY_WIF, settings.TRANSNET_GATEWAY_WIF_MEMO]
        )
        transnet.set_default_account(settings.TRANSNET_GATEWAY_ACCOUNT)

        transaction = TransnetBitsharesTransaction.objects.create(
            trx_id='test',
            trx_in_block=3,
            op_in_trx=3,
            asset='UTECH.UTCORE',
            amount=pow(10, 5),
            account_external='superpchelka23',
            account_internal='superpchelka23'
        )

        handler = TransnetGatewayHandler(transnet, settings.TRANSNET_GATEWAY_ACCOUNT,
                                         bitshares, settings.BITSHARES_GATEWAY_ACCOUNT, settings.BITSHARES_GATEWAY_WIF_MEMO,
                                         {
                                             'UTECH.UTCORE': 'UTECH.UTCORE'
                                         })

        handler.handle([transaction], lambda: True)

        self.assertTrue(transaction.closed, 'Transaction must be properly processed')
