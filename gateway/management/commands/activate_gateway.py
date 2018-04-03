import signal
from django.core.management.base import BaseCommand, CommandError
from threading import Thread

from gateway.src.gateway.gateway import TransnetBitsharesGateway, BitsharesTransnetGateway


class Command(BaseCommand):
    CASE_BITSHARES = 'bitshares_transnet'
    CASE_TRANSNET = 'transnet_bitshares'

    GATEWAYS = {
        CASE_TRANSNET: TransnetBitsharesGateway,
        CASE_BITSHARES: BitsharesTransnetGateway
    }

    help = 'Start gateway: %s, %s' % (CASE_BITSHARES, CASE_TRANSNET)

    def gracefully_stop(self, *args, **kwargs):
        self.gateway.stop()

    def register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.gracefully_stop)
        signal.signal(signal.SIGINT, self.gracefully_stop)

    def add_arguments(self, parser):
        parser.add_argument('blockchain_name', nargs='+', type=str)

    def handle(self, *args, **options):
        gateway_class = self.GATEWAYS.get(options['blockchain_name'][0])
        self.gateway = gateway_class()
        self.register_signal_handlers()
        self.gateway.start()



