import signal
from django.core.management.base import BaseCommand, CommandError
from threading import Thread

from gateway.src.gateway.gateway import TransnetBitsharesGateway, BitsharesTransnetGateway


class Blocker:
    def __init__(self, active_gateways):
        self.active = False
        self.active_gateways = active_gateways

        def gracefully_stop(*args, **kwargs):
            self.stop()

        signal.signal(signal.SIGINT, gracefully_stop)
        signal.signal(signal.SIGTERM, gracefully_stop)

    def start(self):
        self.active = True
        while self.active:
            pass

    def stop(self):
        self.active = False
        for gateway in self.active_gateways:
            gateway.stop()


class Command(BaseCommand):
    CASE_BITSHARES = 'bitshares_transnet'
    CASE_TRANSNET = 'transnet_bitshares'

    GATEWAYS = {
        CASE_TRANSNET: TransnetBitsharesGateway,
        CASE_BITSHARES: BitsharesTransnetGateway
    }

    help = 'Start gateway: %s, %s' % (CASE_BITSHARES, CASE_TRANSNET)

    def add_arguments(self, parser):
        parser.add_argument('blockchain_name', nargs='+', type=str)

    def handle(self, *args, **options):
        active_gateways = []

        for name in options['blockchain_name']:
            gateway_class = self.GATEWAYS.get(name)
            if not gateway_class:
                continue

            gateway = gateway_class()
            active_gateways.append(gateway)

            Thread(target=lambda: gateway.start()).start()

        blocker = Blocker(active_gateways)
        if active_gateways:
            blocker.start()
