from django.contrib import admin

from gateway.models import BitsharesTransaction, TransnetTransaction


class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ('trx_id', 'trx_in_block', 'op_in_trx', 'asset', 'amount', 'account_external', 'account_internal',
                    'closed', 'error', 'created')
    list_filter = ('closed', 'error', 'created')
    readonly_fields = ('trx_id', 'trx_in_block', 'op_in_trx', 'asset', 'amount', 'account_external', 'account_internal')

    def has_add_permission(self, request):
        return False


@admin.register(BitsharesTransaction)
class BitsharesBlockchainTransactionAdmin(BlockchainTransactionAdmin):
    pass


@admin.register(TransnetTransaction)
class TransnetBlockchainTransactionAdmin(BlockchainTransactionAdmin):
    pass