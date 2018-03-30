from bitshares.account import Account
from bitshares.asset import Asset
from logging import getLogger

from bitshares.memo import Memo
from decimal import Decimal

logger = getLogger(__name__)


class AccountTransfersProcessor(object):
    LIMIT_DEFAULT = 1000

    def __init__(self, blockchain_api, account_address, transaction_model, limit=LIMIT_DEFAULT):
        self.blockchain_api = blockchain_api
        self.address = account_address
        self.transaction_model = transaction_model
        self.limit = limit

    def __get_latest_transaction_id(self):
        transaction = self.transaction_model.objects.order_by('id').last()
        if transaction:
            return transaction.trx_id
        return 0

    def __decode_memo(self, account_from, account_to, memo, bitshares_instance):
        try:
            return Memo(account_from, account_to, bitshares_instance).decrypt(memo)
        except:
            return ''

    def process_transactions(self):
        account = Account(self.address)

        try:
            txs = account.history(0, self.__get_latest_transaction_id(), self.limit, only_ops=["transfer"])
        except Exception as exc:
            logger.exception("Can't retrieve history from blockchain")
            return []

        new_transactions = []
        for tx in txs:
            operation_data = tx['op'][1]
            if operation_data['to'] != account['id'] or not operation_data.get('memo'):
                continue

            asset = Asset(operation_data['amount']['asset_id'])
            account_internal = self.__decode_memo(operation_data['from'], operation_data['to'], operation_data['memo'], self.blockchain_api)
            transaction = self.transaction_model.objects.create(
                trx_id=tx['id'],
                trx_in_block=tx['trx_in_block'],
                op_in_trx=tx['op_in_trx'],
                asset=asset.symbol,
                amount=Decimal(operation_data['amount']['amount'])/10 ** asset.precision,
                account_external=Account(operation_data['from']).name,
                account_internal=account_internal
            )
            new_transactions.append(transaction)

        return new_transactions
