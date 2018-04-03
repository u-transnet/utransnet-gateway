from logging import getLogger

from bitsharesbase import memo as BTSMemo
from bitsharesbase.account import PrivateKey as BTSPrivateKey, PublicKey as BTSPublicKey
from bitshares.account import Account as BTSAccount
from bitshares.asset import Asset as BTSAsset

from transnetbase import memo as TRNSMemo
from transnetbase.account import PrivateKey as TRNSPrivateKey, PublicKey as TRNSPublicKey
from transnet.account import Account as TRNSAccount
from transnet.asset import Asset as TRNSAsset

from gateway.src.account.base_account_transfers_provider import BaseAccountTransfersProvider
from gateway.src.api_providers.base_api_provider import BaseApiProvider
from gateway.src.api_providers.bitshares_api_provider import BitsharesApiProvider
from gateway.src.api_providers.transnet_api_provider import TransnetApiProvider

logger = getLogger(__name__)


class AccountTransfersProvider(BaseAccountTransfersProvider, BaseApiProvider):
    LIMIT_DEFAULT = 1000

    def __init__(self, blockchain_api, memo_wif, account, transaction_model, limit=LIMIT_DEFAULT):
        self.blockchain_api = blockchain_api
        self.account = self.Account(account)
        self.memo_wif = memo_wif
        self.transaction_model = transaction_model
        self.limit = limit

    def __get_latest_transaction_id(self):
        transaction = self.transaction_model.objects.order_by('trx_id').last()
        if transaction:
            return transaction.trx_id
        return 0

    def _decode_memo(self, memo, blockchain_api):
        try:
            return self.Memo.decode_memo(
                self.PrivateKey(self.memo_wif),
                self.PublicKey(memo['from'], prefix=blockchain_api.prefix),
                memo.get("nonce"),
                memo.get("message")
            )
        except Exception:
            logger.error("Can't decode memo")
            return ''

    def __fetch_transactions(self, first=None, last=0, limit=100):
        try:
            txs = self.account.history(first, last, limit, only_ops=["transfer"])
        except Exception as exc:
            logger.exception("Can't retrieve history from blockchain")
            return []

        new_transactions = []
        for tx in txs:
            operation_data = tx['op'][1]
            if operation_data['to'] != self.account['id'] or not operation_data.get('memo'):
                continue

            asset = self.Asset(operation_data['amount']['asset_id'])
            account_internal = self._decode_memo(operation_data['memo'], self.blockchain_api)
            db_instance, created = self.transaction_model.objects.get_or_create(
                trx_id=tx['id'][5:],  # remove 1.11. part of transaction id
                defaults={
                    'trx_in_block': tx['trx_in_block'],
                    'op_in_trx': tx['op_in_trx'],
                    'asset': asset.symbol,
                    'amount': operation_data['amount']['amount'] / 10 ** asset.precision,
                    'account_external': self.Account(operation_data['from']).name,
                    'account_internal': account_internal
                }
            )
            if created:
                if not account_internal:
                    db_instance.error = True
                    db_instance.save()
                    continue
                new_transactions.append(db_instance)

        return new_transactions

    def fetch_all_transactions(self):
        return self.__fetch_transactions()

    def fetch_new_transactions(self):
        return self.__fetch_transactions(0, self.__get_latest_transaction_id())


class BitsharesAccountTransfersProvider(BitsharesApiProvider, AccountTransfersProvider):
    pass


class TransnetAccountTransfersProvider(TransnetApiProvider, AccountTransfersProvider):
    pass
