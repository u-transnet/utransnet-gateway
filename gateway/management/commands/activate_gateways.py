import signal
from django.core.management.base import BaseCommand, CommandError
from threading import Thread

from gateway.src.gateway.gateway import TransnetGateway, BitsharesGateway


class Blocker:
    def __init__(self):
        self.active = False

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


class Command(BaseCommand):
    CASE_BITSHARES = 'bitshares'
    CASE_TRANSNET = 'transnet'

    GATEWAYS = {
        CASE_TRANSNET: TransnetGateway,
        CASE_BITSHARES: BitsharesGateway
    }

    help = 'Start gateway: %s, %s' % (CASE_BITSHARES, CASE_TRANSNET)

    def add_arguments(self, parser):
        parser.add_argument('blockchain_name', nargs='+', type=str)

    def handle(self, *args, **options):
        active_gateways = []

        blocker = Blocker()

        for name in options['blockchain_name']:
            gateway_class = self.GATEWAYS.get(name)
            if not gateway_class:
                continue

            gateway = gateway_class()
            active_gateways.append(gateway)

            Thread(target=lambda: gateway.start()).start()

        if active_gateways:
            blocker.start()
