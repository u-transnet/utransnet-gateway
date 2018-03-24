import threading

from bitshares import BitShares
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils.timezone import now

from gateway.models import BitsharesTransaction
from gateway.src.account.account_listener import AccountTransfersListener
from gateway.src.account.account_listener_base_handler import AccountListenerBaseHandler


class TestHandler(AccountListenerBaseHandler):

    processed = False

    def handle(self, transactions):
        self.processed = True


@override_settings(BLOCKCHAIN_NOBROADCAST=True)
class GatewayTest(TestCase):

    def test_account_listener(self):
        self.bitshares = BitShares(
            settings.BITSHARES_NODE_URL,
            nobroadcast=settings.BLOCKCHAIN_NOBROADCAST,
            keys=[settings.BITSHARES_GATEWAY_WIF]
        )

        handler = TestHandler()
        transfer_listener = AccountTransfersListener(
            self.bitshares, settings.BITSHARES_GATEWAY_ACCOUNT, BitsharesTransaction)
        transfer_listener.add_handler(handler)

        threading.Thread(target=lambda: transfer_listener.start()).start()
        max_waiting_seconds = 15
        start_time = now()

        while not handler.processed and (now() - start_time).seconds < max_waiting_seconds:
            pass

        transfer_listener.stop()
        self.assertTrue(handler.processed, 'No one transactions were handled')

