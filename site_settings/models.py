from django.db import models


class SettingsModel(models.Model):

    bitshares_transnet_gateway_address = models.CharField(verbose_name='адрес', max_length=255)
    bitshares_transnet_active_wif = models.CharField(verbose_name='активный ключ', max_length=255)
    bitshares_transnet_memo_wif = models.CharField(verbose_name='memo ключ', max_length=255)
    bitshares_transnet_node_url = models.URLField(verbose_name='адрес ноды для подключения')

    transnet_bitshares_gateway_address = models.CharField(verbose_name='адрес', max_length=255)
    transnet_bitshares_active_wif = models.CharField(verbose_name='активный ключ', max_length=255)
    transnet_bitshares_memo_wif = models.CharField(verbose_name='memo ключ', max_length=255)
    transnet_bitshares_node_url = models.URLField(verbose_name='адрес ноды для подключения')

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SettingsModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
