from bitshares.bitshares import PrivateKey as BTSPrivateKey, PublicKey as BTSPublicKey
from bitshares.account import Account as BTSAccount
from bitshares.asset import Asset as BTSAsset
from bitshares.amount import Amount as BTSAmount
from bitshares.storage import configStorage as BTSConfig
from bitsharesbase import memo as BTSMemo
from bitsharesbase import operations as BTSOperations

from gateway.src.api_providers.base_api_provider import BaseApiProvider


class BitsharesApiProvider(BaseApiProvider):
    PrivateKey = BTSPrivateKey
    PublicKey = BTSPublicKey
    Account = BTSAccount
    Asset = BTSAsset
    Amount = BTSAmount
    Config = BTSConfig
    Memo = BTSMemo
    Operations = BTSOperations