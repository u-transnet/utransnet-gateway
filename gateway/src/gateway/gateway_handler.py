from bitshares.account import Account as BTSAccount
from bitshares.amount import Amount as BTSAmount
from bitshares.asset import Asset as BTSAsset
from bitshares.bitshares import PrivateKey as BTSPrivateKey
from bitshares.bitshares import PublicKey as BTSPublicKey
from bitsharesbase import operations as BTSoperations
from bitsharesbase import memo as BTSMemo
from bitshares.storage import configStorage as BTSconfig
import random

from transnet.account import Account as TRNSAccount
from transnet.amount import Amount as TRNSAmount
from transnet.asset import Asset as TRNSAsset
from transnet.transnet import PrivateKey as TRNSPrivateKey
from transnet.transnet import PublicKey as TRNSPublicKey
from transnetbase import operations as TRNSoperations
from transnetbase import memo as TRNSMemo
from transnet.storage import configStorage as TRNSconfig

from gateway.src.account.account_listener_base_handler import AccountListenerBaseHandler
from logging import getLogger

logger = getLogger(__name__)


class BaseGatewayHandler(AccountListenerBaseHandler):
    def __init__(self,
                 blockchain_api_external, gateway_address_external,
                 blockchain_api_internal, gateway_address_internal, gateway_address_internal_memo_wif,
                 assets_mapping=None):
        self.blockchain_api_external = blockchain_api_external
        self.blockchain_api_internal = blockchain_api_internal
        self.gateway_address_external = gateway_address_external
        self.gateway_address_internal = gateway_address_internal
        self.gateway_address_internal_memo_wif = gateway_address_internal_memo_wif
        self.assets_mapping = assets_mapping or {}

    def encrypt_memo(self, blockchain_instance, memo_wif, from_acccount, to_accout, message):
        raise NotImplementedError()

    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset, message):
        raise NotImplementedError()

    def burn_assets(self, amount, asset, account):
        raise NotImplementedError()

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
                                  transaction.amount, self.gateway_address_internal,
                                  transaction.account_internal, target_asset, transaction.trx_id)
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


class BitSharesGatewayHandler(BaseGatewayHandler):
    def encrypt_memo(self, blockchain_instance, memo_wif, from_account, to_account, message):
        nonce = random.getrandbits(64)

        enc = TRNSMemo.encode_memo(
            TRNSPrivateKey(memo_wif),
            TRNSPublicKey(
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

    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset, message):
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
            },
            "memo": self.encrypt_memo(blockchain_instance, self.gateway_address_internal_memo_wif, issuer, to, message)
        })

        blockchain_instance.finalizeOp(operation, TRNSconfig['default_account'], 'active')

    def burn_assets(self, amount, asset, account):
        self.blockchain_api_external.reserve(BTSAmount(
            amount=amount,
            asset=asset,
            bitshares_instance=self.blockchain_api_external
        ), account)


class TransnetGatewayHandler(BaseGatewayHandler):
    def encrypt_memo(self, blockchain_instance, memo_wif, from_account, to_account, message):
        nonce = random.getrandbits(64)

        enc = BTSMemo.encode_memo(
            BTSPrivateKey(memo_wif),
            BTSPublicKey(
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

    def issue_assets(self, blockchain_instance, amount, issuer, to, target_asset, message):
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
            },
            "memo": self.encrypt_memo(blockchain_instance, self.gateway_address_internal_memo_wif, issuer, to, message)
        })

        blockchain_instance.finalizeOp(operation, BTSconfig['default_account'], 'active')

    def burn_assets(self, amount, asset, account):
        self.blockchain_api_external.reserve(TRNSAmount(
            amount=amount,
            asset=asset,
            transnet_instance=self.blockchain_api_external
        ), account)
