from bitshares.bitshares import PrivateKey as BTSPrivateKey, PublicKey as BTSPublicKey
from bitshares.account import Account as BTSAccount
from bitshares.asset import Asset as BTSAsset
from bitshares.amount import Amount as BTSAmount
from bitshares.storage import configStorage as BTSConfig
from bitsharesbase import memo as BTSMemo
from bitsharesbase import operations as BTSOperations

from gateway.src.api_providers.base_internal_api_provider import BaseInternalApiProvider


class BitsharesInternalApiProvider(BaseInternalApiProvider):
    InternalPrivateKey = BTSPrivateKey
    InternalPublicKey = BTSPublicKey
    InternalAccount = BTSAccount
    InternalAsset = BTSAsset
    InternalAmount = BTSAmount
    InternalConfig = BTSConfig
    InternalMemo = BTSMemo
    InternalOperations = BTSOperations