from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as __


class AbstractBlockchainTransaction(models.Model):

    STATE_IDLE = 'idle'
    STATE_COMPLETE = 'complete'
    STATE_ERROR = 'error'

    STATE_CHOICES = (
        (STATE_IDLE, _('Idle')),
        (STATE_COMPLETE, _('Complete')),
        (STATE_ERROR, _('Error'))
    )

    trx_id = models.CharField(verbose_name=_('Transaction ID'), max_length=512)
    trx_in_block = models.PositiveIntegerField(verbose_name=_('Number of transaction in blck'))
    op_in_trx = models.PositiveIntegerField(verbose_name=_('Number of operation in transaction'))
    asset = models.CharField(verbose_name=_('Asset'), max_length=128)
    amount = models.FloatField(verbose_name=_('Amount'))
    account_external = models.CharField(verbose_name=_('External blockchain account'), max_length=128)
    account_internal = models.CharField(verbose_name=_('Internal blockchain account'), max_length=128)

    state = models.CharField(verbose_name=_('State'), max_length=10, choices=STATE_CHOICES, default=STATE_IDLE)
    created = models.DateTimeField(verbose_name=_('Created'), auto_now_add=True)

    def __str__(self):
        return __('Transaction')+': %s' % self.trx_id

    class Meta:
        abstract = True


class BitsharesTransnetTransaction(AbstractBlockchainTransaction):

    class Meta:
        verbose_name = _('Bitshares to Transnet')
        verbose_name_plural = _('Bitshares to Transnet')
        ordering = ('-trx_id', )


class TransnetBitsharesTransaction(AbstractBlockchainTransaction):

    class Meta:
        verbose_name = _('Transnet to Bitshares')
        verbose_name_plural = _('Transnet to Bitshares')
        ordering = ('-trx_id', )
