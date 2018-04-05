from django.db import models
from django.utils.translation import gettext_lazy as _

class SettingsModel(models.Model):

    bitshares_transnet_gateway_address = models.CharField(verbose_name=_('Address'), max_length=255)
    bitshares_transnet_active_wif = models.CharField(verbose_name=_('Active key (WIF)'), max_length=255)
    bitshares_transnet_memo_wif = models.CharField(verbose_name=_('Memo key (WIF)'), max_length=255)
    bitshares_transnet_node_url = models.CharField(verbose_name=_('URL of node'), max_length=255)

    transnet_bitshares_gateway_address = models.CharField(verbose_name=_('Address'), max_length=255)
    transnet_bitshares_active_wif = models.CharField(verbose_name=_('Active key (WIF)'), max_length=255)
    transnet_bitshares_memo_wif = models.CharField(verbose_name=_('Memo key (WIF)'), max_length=255)
    transnet_bitshares_node_url = models.CharField(verbose_name=_('URL of node'), max_length=255)

    def __str__(self):
        return _('Settings')

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SettingsModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = _('Settings')
        verbose_name_plural = _('Settings')
