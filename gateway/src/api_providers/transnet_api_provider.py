from transnet.transnet import PrivateKey as TRNSPrivateKey, PublicKey as TRNSPublicKey
from transnet.account import Account as TRNSAccount
from transnet.asset import Asset as TRNSAsset
from transnet.amount import Amount as TRNSAmount
from transnet.storage import configStorage as TRNSConfig
from transnetbase import memo as TRNSMemo
from transnetbase import operations as TRNSOperations

from gateway.src.api_providers.base_api_provider import BaseApiProvider


class TransnetApiProvider(BaseApiProvider):
    PrivateKey = TRNSPrivateKey
    PublicKey = TRNSPublicKey
    Account = TRNSAccount
    Asset = TRNSAsset
    Amount = TRNSAmount
    Config = TRNSConfig
    Memo = TRNSMemo
    Operations = TRNSOperations