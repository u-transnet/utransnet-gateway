from django.contrib import admin

from site_settings.models import SettingsModel


@admin.register(SettingsModel)
class SettingsModelAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Bitshares - Transnet', {
            'fields': [
                'bitshares_transnet_gateway_address',
                'bitshares_transnet_active_wif',
                'bitshares_transnet_memo_wif',
                'bitshares_transnet_node_url',
            ]
        }),
        ('Transnet - Bitshares', {
            'fields': [
                'transnet_bitshares_gateway_address',
                'transnet_bitshares_active_wif',
                'transnet_bitshares_memo_wif',
                'transnet_bitshares_node_url',
            ]
        })
    )
