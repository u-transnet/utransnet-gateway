from bitshares.account import Account as BTSAccount
from bitshares.amount import Amount as BTSAmount
from bitshares.asset import Asset as BTSAsset
from bitsharesbase import operations as BTSoperations
from bitshares.storage import configStorage as BTSconfig

from transnet.account import Account as TRNSAccount
from transnet.amount import Amount as TRNSAmount
from transnet.asset import Asset as TRNSAsset
from transnetbase import operations as TRNSoperations
from transnet.storage import configStorage as TRNSconfig

from gateway.src.account.account_listener_base_handler import AccountListenerBaseHandler
from logging import getLogger

logger = getLogger(__name__)


class BaseGatewayHandler(AccountListenerBaseHandler):
    def __init__(self,
                 blockchain_api_external, gateway_address_external,
                 blockchain_api_internal, gateway_address_internal,
                 assets_mapping=None):
        self.blockchain_api_external = blockchain_api_external
        self.blockchain_api_internal = blockchain_api_internal
        self.gateway_address_external = gateway_address_external
        self.gateway_address_internal = gateway_address_internal
        self.assets_mapping = assets_mapping or {}

    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset):
        raise NotImplementedError()

    def burn_assets(self, amount, asset, account):
        raise NotImplementedError()

    def handle(self, transactions):
        for transaction in transactions:
            target_asset = self.assets_mapping.get(transaction.asset)
            if not target_asset:
                logger.error("Unrecognized assets %s" % transaction.asset)
                continue

            try:
                self.issue_assets(self.blockchain_api_internal,
                                  transaction.amount, self.gateway_address_internal,
                                  transaction.account_internal, target_asset)
            except Exception as ex:
                logger.exception("WARNING: Can't issue assets for external account %s and internal account %s"
                                 "Trasaction: id %s, trx_id %s"
                                 % (transaction.account_external, transaction.account_internal,
                                    transaction.id, transaction.trx_id))
                transaction.error = True
                transaction.save()
                continue

            try:
                self.burn_assets(transaction.amount, transaction.asset, self.gateway_address_external)
            except Exception as ex:
                logger.exception("Can't burn assets for transaction %s " % (transaction.id))
                transaction.error = True
            else:
                transaction.closed = True

            transaction.save()


class BitsharesGatewayHandler(BaseGatewayHandler):
    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset):
        if not 'default_account' in TRNSconfig:
            raise ValueError("You need to provide an account")

        issuer = TRNSAccount(issuer)
        to = TRNSAccount(to)
        target_asset = TRNSAsset(target_asset)

        operation = TRNSoperations.Asset_issue(**{
            "fee": {"amount": 0, "asset_id": TRNSAsset('UTT')['id']},
            "issuer": issuer["id"],
            "issue_to_account": to["id"],
            "asset_to_issue": {
                "amount": amount * 10 ** target_asset.precision,
                "asset_id": target_asset["id"]
            }
        })

        blockchain_instance.finalizeOp(operation, TRNSconfig['default_account'], 'active')

    def burn_assets(self, amount, asset, account):
        self.blockchain_api_external.reserve(BTSAmount(
            amount=amount,
            asset=asset,
            bitshares_instance=self.blockchain_api_external
        ), account)


class TransnetGatewayHandler(BaseGatewayHandler):
    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset):
        if not 'default_account' in BTSconfig:
            raise ValueError("You need to provide an account")

        issuer = BTSAccount(issuer)
        to = BTSAccount(to)
        target_asset = BTSAsset(target_asset)

        operation = BTSoperations.Asset_issue(**{
            "fee": {"amount": 0, "asset_id": BTSAsset('BTS')['id']},
            "issuer": issuer["id"],
            "issue_to_account": to["id"],
            "asset_to_issue": {
                "amount": amount * 10 ** target_asset.precision,
                "asset_id": target_asset["id"]
            }
        })

        blockchain_instance.finalizeOp(operation, BTSconfig['default_account'], 'active')

    def burn_assets(self, amount, asset, account):
        self.blockchain_api_external.reserve(TRNSAmount(
            amount=amount,
            asset=asset,
            transnet_instance=self.blockchain_api_external
        ), account)
