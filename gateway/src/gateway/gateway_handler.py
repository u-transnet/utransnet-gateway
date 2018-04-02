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

    def _decode_memo(self, memo, blockchain_api):
        try:
            return self.Memo.decode_memo(
                self.PrivateKey(self.gateway_account_internal_memo_wif),
                self.PublicKey(memo['from'], prefix=blockchain_api.prefix),
                memo.get("nonce"),
                memo.get("message")
            )
        except Exception:
            logger.exception("Can't decode memo")
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

        blockchain_instance.finalizeOp(operation, self.InternalConfig['default_account'], 'active')

    def burn_assets(self, amount, asset, account):
        self.blockchain_api_external.reserve(self.Amount(
            amount=amount,
            asset=asset,
        ), account)

    def sync(self, transactions):
        txs_map = {
            tx.trx_id: tx
            for tx in transactions
        }

        def filter_func(tx):
            operation_data = tx['op'][1]
            return operation_data['issuer'] == self.gateway_account_internal.name and operation_data.get('memo')

        issue_txs = self.gateway_account_internal.history(None, 0, 100, limit=['asset_issue'])
        issue_txs = filter(filter_func, issue_txs)

        for tx in issue_txs:
            operation_data = tx['op'][1]
            memo = self._decode_memo(operation_data['memo'], self.blockchain_api_internal)

            if not memo:
                continue

            db_tx = txs_map.get(memo)  # remove 1.11. part of transaction id
            if not db_tx:
                continue

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

    def handle(self, transactions, get_is_active):
        for transaction in transactions:
            if not get_is_active():
                return

            target_asset = self.assets_mapping.get(transaction.asset)
            if not target_asset:
                logger.error("Unrecognized assets %s" % transaction.asset)
                continue

            try:
                self.issue_assets(self.blockchain_api_internal,
                                  transaction.amount, self.gateway_account_internal,
                                  transaction.account_internal, target_asset, transaction.trx_id[:5])
            except Exception as ex:
                logger.exception("WARNING: Can't issue assets for external account %s and internal account %s"
                                 "Trasaction: id %s, trx_id %s"
                                 % (transaction.account_external, transaction.account_internal,
                                    transaction.id, transaction.trx_id))
                transaction.error = True
                transaction.save()
                continue

            try:
                self.burn_assets(transaction.amount, transaction.asset, self.gateway_account_external)
            except Exception as ex:
                logger.exception("Can't burn assets for transaction %s " % (transaction.id))
                transaction.error = True
            else:
                transaction.closed = True

            transaction.save()


class BitsharesGatewayHandler(BitsharesApiProvider, TransnetInternalApiProvider, GatewayAccountListenerHandler):
    pass


class TransnetGatewayHandler(TransnetApiProvider, BitsharesInternalApiProvider, GatewayAccountListenerHandler):
    pass
