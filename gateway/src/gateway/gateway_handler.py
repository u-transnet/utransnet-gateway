from bitshares.amount import Amount
from bitsharesbase import operations

from gateway.src.account.account_listener_base_handler import AccountListenerBaseHandler
from logging import getLogger

logger = getLogger(__name__)


class GatewayHandler(AccountListenerBaseHandler):
    def __init__(self, transaction_model, blockchain_api_external, gateway_address_external,
                 blockchain_api_internal, gateway_address_internal, assets_mapping=None):
        self.transaction_model = transaction_model
        self.blockchain_api_external = blockchain_api_external
        self.blockchain_api_internal = blockchain_api_internal
        self.gateway_address_external = gateway_address_external
        self.gateway_address_internal = gateway_address_internal
        self.assets_mapping = assets_mapping or {}

    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset):

        operation = operations.Asset_issue(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "issuer": issuer["id"],
            "issue_to_account": to["id"],
            "asset_to_issue": {
                "amount": amount,
                "asset_id": target_asset["id"]
            }
        })

        blockchain_instance.finalizeOp(operation)

    def handler(self, transactions):
        for transaction in transactions:
            target_asset = self.assets_mapping.get(transaction.asset)
            if not target_asset:
                logger.error("Unrecognized assets %s" % transaction.asset)
                return

            try:
                burn_transaction = self.blockchain_api_external.reserve(Amount(
                    amount=transaction.amount,
                    asset=transaction.asset,
                    bitshares_instance=self.blockchain_api_external
                ), self.gateway_address_external)
            except Exception as ex:
                logger.exception("Can't burn assets for transaction %s " % (transaction.id))
                continue

            try:
                self.issue_assets(self.blockchain_api_internal,
                                  transaction.amount, self.gateway_address_internal,
                                  transaction.transaction.account_internal, target_asset)
            except Exception as ex:
                logger.critical("WARNING: Can't issue assets for external account %s and internal account %s"
                                % (transaction.account_external, transaction.account_internal))
                transaction.error = True
            else:
                transaction.closed = True

            transaction.save()
