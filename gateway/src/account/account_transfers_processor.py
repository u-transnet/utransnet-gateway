from logging import getLogger

from bitsharesbase import memo as BTSMemo
from bitsharesbase.account import PrivateKey as BTSPrivateKey, PublicKey as BTSPublicKey
from bitshares.account import Account as BTSAccount
from bitshares.asset import Asset as BTSAsset

from transnetbase import memo as TRNSMemo
from transnetbase.account import PrivateKey as TRNSPrivateKey, PublicKey as TRNSPublicKey
from transnet.account import Account as TRNSAccount
from transnet.asset import Asset as TRNSAsset

logger = getLogger(__name__)


class BaseAccountTransfersProcessor(object):
    LIMIT_DEFAULT = 1000

    def __init__(self, blockchain_api, memo_wif, account_address, transaction_model, limit=LIMIT_DEFAULT):
        self.blockchain_api = blockchain_api
        self.address = account_address
        self.memo_wif = memo_wif
        self.transaction_model = transaction_model
        self.limit = limit

    def __get_latest_transaction_id(self):
        transaction = self.transaction_model.objects.order_by('trx_id').last()
        if transaction:
            return transaction.trx_id
        return 0

    def _decode_memo(self, account_from, account_to, memo, blockchain_api):
        raise NotImplementedError()

    def _fetch_asset(self, asset_id):
        raise NotImplementedError()

    def _fetch_account(self, account):
        raise NotImplementedError()

    def process_transactions(self):
        account = self._fetch_account(self.address)

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

            asset = self._fetch_asset(operation_data['amount']['asset_id'])
            account_internal = self._decode_memo(operation_data['from'], operation_data['to'], operation_data['memo'],
                                                  self.blockchain_api)
            transaction = self.transaction_model.objects.create(
                trx_id=tx['id'][5:],  # remove 1.11. part of transaction id
                trx_in_block=tx['trx_in_block'],
                op_in_trx=tx['op_in_trx'],
                asset=asset.symbol,
                amount=operation_data['amount']['amount'] / 10 ** asset.precision,
                account_external=self._fetch_account(operation_data['from']).name,
                account_internal=account_internal
            )
            new_transactions.append(transaction)

        return new_transactions


class BitSharesAccountTransfersProcessor(BaseAccountTransfersProcessor):
    def _decode_memo(self, account_from, account_to, memo, blockchain_api):
        try:
            return BTSMemo.decode_memo(
                BTSPrivateKey(self.memo_wif),
                BTSPublicKey(memo['from'], prefix=blockchain_api.prefix),
                memo.get("nonce"),
                memo.get("message")
            )
        except Exception:
            logger.exception("Can't decode memo")
            return ''

    def _fetch_account(self, account):
        return BTSAccount(account)

    def _fetch_asset(self, asset_id):
        return BTSAsset(asset_id)


class TransnetAccountTransfersProcessor(BaseAccountTransfersProcessor):
    def _decode_memo(self, account_from, account_to, memo, blockchain_api):
        try:
            return TRNSMemo.decode_memo(
                TRNSPrivateKey(self.memo_wif),
                TRNSPublicKey(memo['from'], prefix=blockchain_api.prefix),
                memo.get("nonce"),
                memo.get("message")
            )
        except Exception:
            logger.exception("Can't decode memo")
            return ''

    def _fetch_account(self, account):
        return TRNSAccount(account)

    def _fetch_asset(self, asset_id):
        return TRNSAsset(asset_id)
