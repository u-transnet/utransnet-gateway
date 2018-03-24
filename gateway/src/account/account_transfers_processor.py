from bitshares.account import Account
from bitshares.asset import Asset
from logging import getLogger

from bitshares.memo import Memo

logger = getLogger(__name__)


class AccountTransfersProcessor(object):
    LIMIT_DEFAULT = 1000

    def __init__(self, blockchain_api, account_address, transaction_model, limit=LIMIT_DEFAULT):
        self.blockchain_api = blockchain_api
        self.address = account_address
        self.transaction_model = transaction_model
        self.limit = limit

    def __get_latest_transaction_id(self):
        transaction = self.transaction_model.objects.last()
        if transaction:
            return transaction.tx_id
        return 0

    def __decode_memo(self, memo, bitshares_instance):
        return Memo(memo['from'], memo['to'], bitshares_instance).decrypt(memo['message'])

    def process_transactions(self):
        account = Account(self.address)

        try:
            txs = account.history(0, self.__get_latest_transaction_id(), self.limit, only_ops=["transfer"])
        except Exception as exc:
            logger.exception("Can't retrieve history from blockchain")
            return

        new_transactions = []
        for tx in txs:
            operation_data = tx['op'][1]
            if operation_data['to'] != account['id']:
                continue

            transaction = self.transaction_model.objects.create(
                trx_id=tx['id'],
                trx_in_block=tx['trx_in_block'],
                op_in_trx=tx['op_in_trx'],
                asset=Asset(operation_data['amount']['asset_id']).symbol,
                amount=operation_data['amount'] / pow(10, 5),
                account_external=Account(operation_data['from']).name,
                account_internal=self.__decode_memo(operation_data['memo'], self.blockchain_api)
            )
            new_transactions.append(transaction)

        return new_transactions
