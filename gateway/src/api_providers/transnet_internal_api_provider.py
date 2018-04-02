from transnet.transnet import PrivateKey as TRNSPrivateKey, PublicKey as TRNSPublicKey
from transnet.account import Account as TRNSAccount
from transnet.asset import Asset as TRNSAsset
from transnet.amount import Amount as TRNSAmount
from transnet.storage import configStorage as TRNSConfig
from transnetbase import memo as TRNSMemo
from transnetbase import operations as TRNSOperations

from gateway.src.api_providers.base_internal_api_provider import BaseInternalApiProvider


class TransnetInternalApiProvider(BaseInternalApiProvider):
    InternalPrivateKey = TRNSPrivateKey
    InternalPublicKey = TRNSPublicKey
    InternalAccount = TRNSAccount
    InternalAsset = TRNSAsset
    InternalAmount = TRNSAmount
    InternalConfig = TRNSConfig
    InternalMemo = TRNSMemo
    InternalOperations = TRNSOperations