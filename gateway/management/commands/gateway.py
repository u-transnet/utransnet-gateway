from django.core.management.base import BaseCommand, CommandError
from threading import Thread

from gateway.src.gateway.gateway import TransnetGateway, BitsharesGateway


class Command(BaseCommand):
    CASE_BITSHARES = 'transnet'
    CASE_TRANSNET = 'transnet'

    GATEWAYS = {
        CASE_TRANSNET: TransnetGateway,
        CASE_BITSHARES: BitsharesGateway
    }

    help = 'Start gateway: %s, %s' % (CASE_BITSHARES, CASE_TRANSNET)

    def add_arguments(self, parser):
        parser.add_argument('blockchain_name', nargs='+', type=str)

    def handle(self, *args, **options):
        for name in options['blockchain_name']:
            gateway = self.GATEWAYS.get(name)
            if not gateway:
                continue

            Thread(target=lambda: gateway.start()).start()

        # Freeze command
        while True:
            pass
