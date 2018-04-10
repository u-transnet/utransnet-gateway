from django.contrib import admin

from gateway.models import BitsharesTransnetTransaction, TransnetBitsharesTransaction


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('trx_id', 'trx_in_block', 'op_in_trx', 'asset', 'amount', 'account_external', 'account_internal',
                    'state', 'created')
    search_fields = ('trx_id', 'account_external', 'account_internal',)
    list_filter = ('asset', 'state', 'created')
    readonly_fields = ('trx_id', 'trx_in_block', 'op_in_trx', 'asset', 'amount', 'account_external', 'account_internal')

    def has_add_permission(self, request):
        return False


@admin.register(BitsharesTransnetTransaction)
class BitsharesTransnetTransactionAdmin(TransactionAdmin):
    pass


@admin.register(TransnetBitsharesTransaction)
class TransnetBitsharesTransactionAdmin(TransactionAdmin):
    pass