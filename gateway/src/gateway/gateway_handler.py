import random

from gateway.src.account.base_account_listener_handler import BaseAccountListenerHandler
from logging import getLogger

from gateway.src.api_providers.base_api_provider import BaseApiProvider
from gateway.src.api_providers.base_internal_api_provider import BaseInternalApiProvider
from gateway.src.api_providers.bitshares_api_provider import BitsharesApiProvider
from gateway.src.api_providers.bitshares_internal_api_provider import BitsharesInternalApiProvider
from gateway.src.api_providers.transnet_api_provider import TransnetApiProvider
from gateway.src.api_providers.transnet_internal_api_provider import TransnetInternalApiProvider
from gateway.src.gateway.base_gateway_handler import BaseGatewayAccountListenerHandler

logger = getLogger(__name__)


class GatewayAccountListenerHandler(BaseInternalApiProvider, BaseApiProvider, BaseGatewayAccountListenerHandler):
    def __init__(self,
                 blockchain_api_external, gateway_account_external,
                 blockchain_api_internal, gateway_account_internal, gateway_account_internal_memo_wif,
                 assets_mapping=None):
        self.blockchain_api_external = blockchain_api_external
        self.blockchain_api_internal = blockchain_api_internal
        self.gateway_account_external = gateway_account_external
        self.gateway_account_internal = gateway_account_internal
        self.gateway_account_internal_memo_wif = gateway_account_internal_memo_wif
        self.assets_mapping = assets_mapping or {}

        self.assets_issues_txs_map = {}

    def _encrypt_memo(self, blockchain_instance, memo_wif, from_account, to_account, message):
        nonce = random.getrandbits(64)

        enc = self.InternalMemo.encode_memo(
            self.InternalPrivateKey(memo_wif),
            self.InternalPublicKey(
                to_account["options"]["memo_key"],
                prefix=blockchain_instance.prefix
            ),
            nonce,
            message
        )

        return {
            "message": enc,
            "nonce": nonce,
            "from": from_account["options"]["memo_key"],
            "to": to_account["options"]["memo_key"]
        }

    def _decode_asset_issue_memo(self, memo_wif, memo, blockchain_api):
        try:
            return self.Memo.decode_memo(
                self.PrivateKey(memo_wif),
                self.PublicKey(memo['to'], prefix=blockchain_api.prefix),
                memo.get("nonce"),
                memo.get("message")
            )
        except Exception:
            logger.error("Can't decode memo")
            return ''

    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset, message):
        if not 'default_account' in self.InternalConfig:
            raise ValueError("You need to provide an account")

        issuer = self.InternalAccount(issuer)
        to = self.InternalAccount(to)
        target_asset = self.InternalAsset(target_asset)

        operation = self.InternalOperations.Asset_issue(**{
            "fee": {"amount": 0, "asset_id": '1.3.0'},
            "issuer": issuer["id"],
            "issue_to_account": to["id"],
            "asset_to_issue": {
                "amount": amount * 10 ** target_asset.precision,
                "asset_id": target_asset["id"]
            },
            "memo": self._encrypt_memo(blockchain_instance, self.gateway_account_internal_memo_wif, issuer, to, message)
        })

        return blockchain_instance.finalizeOp(operation, self.InternalConfig['default_account'], 'active')

    def burn_assets(self, amount, asset, account):
        account = self.Account(account)

        self.blockchain_api_external.reserve(self.Amount(
            amount=amount,
            asset=asset,
        ), account)

    def __sync_transaction(self, db_tx):

        operation_data = self.assets_issues_txs_map.get(db_tx.trx_id)
        if not operation_data:
            return

        asset = self.InternalAsset(operation_data['asset_to_issue']['asset_id'])
        amount = operation_data['asset_to_issue']['amount'] / 10 ** asset.precision
        issue_to_account = self.InternalAccount(operation_data['issue_to_account'])

        if db_tx.amount == amount \
                and db_tx.asset == asset.symbol \
                and db_tx.account_internal == issue_to_account.name:
            db_tx.closed = True
        else:
            db_tx.error = True

        db_tx.save()

    def sync(self, transactions, get_is_active=None):
        gateway_account_internal = self.InternalAccount(self.gateway_account_internal)

        def filter_func(tx):
            operation_data = tx['op'][1]
            return operation_data['issuer'] == gateway_account_internal['id'] and operation_data.get('memo')

        issue_txs = gateway_account_internal.history(None, 0, 100, only_ops=['asset_issue'])
        issue_txs = filter(filter_func, issue_txs)

        for tx in issue_txs:
            if not get_is_active():
                return

            operation_data = tx['op'][1]
            memo = self._decode_asset_issue_memo(self.gateway_account_internal_memo_wif, operation_data['memo'],
                                                 self.blockchain_api_internal)

            if not memo:
                continue

            self.assets_issues_txs_map[memo] = operation_data

        for transaction in transactions:
            self.__sync_transaction(transaction)

    def handle(self, transactions, get_is_active):
        for transaction in transactions:
            if not get_is_active():
                return

            target_asset = self.assets_mapping.get(transaction.asset)
            if not target_asset:
                logger.error("Unrecognized assets %s" % transaction.asset)
                continue

            self.__sync_transaction(transaction)
            if transaction.closed or transaction.error:
                continue

            try:
                issue_tx = self.issue_assets(self.blockchain_api_internal,
                                             transaction.amount, self.gateway_account_internal,
                                             transaction.account_internal, target_asset, transaction.trx_id)
            except Exception as ex:
                logger.exception("WARNING: Can't issue assets for external account %s and internal account %s"
                                 "Trasaction: id %s, trx_id %s"
                                 % (transaction.account_external, transaction.account_internal,
                                    transaction.id, transaction.trx_id))
                transaction.error = True
                transaction.save()
                continue

            self.assets_issues_txs_map[transaction.trx_id] = issue_tx['operations'][0][1]

            try:
                self.burn_assets(transaction.amount, transaction.asset, self.gateway_account_external)
            except Exception as ex:
                logger.exception("Can't burn assets for transaction %s " % transaction.id)
            transaction.closed = True

            transaction.save()


class BitsharesGatewayHandler(BitsharesApiProvider, TransnetInternalApiProvider, GatewayAccountListenerHandler):
    pass


class TransnetGatewayHandler(TransnetApiProvider, BitsharesInternalApiProvider, GatewayAccountListenerHandler):
    pass
