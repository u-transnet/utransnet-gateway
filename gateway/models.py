from django.db import models


class AbstractBlockchainTransaction(models.Model):
    trx_id = models.CharField(verbose_name='ID транзакции', max_length=512)
    trx_in_block = models.PositiveIntegerField(verbose_name='Номер транзакции в блоке')
    op_in_trx = models.PositiveIntegerField(verbose_name='Номер операции в транзакции')
    asset = models.CharField(verbose_name='Токен', max_length=128)
    amount = models.FloatField(verbose_name='Количество средств')
    account_external = models.CharField(verbose_name='Внешний аккаунт', max_length=128)
    account_internal = models.CharField(verbose_name='Внутренний аккаунт', max_length=128)

    closed = models.BooleanField(verbose_name='Закрыта', default=False)
    error = models.BooleanField(verbose_name='Ошибка', default=False)
    created = models.DateTimeField(verbose_name='Дата обработки', auto_now_add=True)

    class Meta:
        abstract = True


class BitsharesTransnetTransaction(AbstractBlockchainTransaction):

    def __str__(self):
        return 'Транзакция: %s' % self.trx_id

    class Meta:
        verbose_name = 'Bitshares в Transnet'
        verbose_name_plural = 'Bitshares в Transnet'
        ordering = ('-trx_id', )


class TransnetBitsharesTransaction(AbstractBlockchainTransaction):

    def __str__(self):
        return 'Транзакция: %s' % self.trx_id

    class Meta:
        verbose_name = 'Transnet в Bitshares'
        verbose_name_plural = 'Transnet в Bitshares'
        ordering = ('-trx_id', )
