# Generated by Django 2.0.2 on 2018-04-04 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0005_auto_20180403_2338'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bitsharestransnettransaction',
            options={'ordering': ('-trx_id',), 'verbose_name': 'Bitshares to Transnet', 'verbose_name_plural': 'Bitshares to Transnet'},
        ),
        migrations.AlterModelOptions(
            name='transnetbitsharestransaction',
            options={'ordering': ('-trx_id',), 'verbose_name': 'Transnet to Bitshares', 'verbose_name_plural': 'Transnet to Bitshares'},
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='account_external',
            field=models.CharField(max_length=128, verbose_name='External blockchain account'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='account_internal',
            field=models.CharField(max_length=128, verbose_name='Internal blockchain account'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='amount',
            field=models.FloatField(verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='asset',
            field=models.CharField(max_length=128, verbose_name='Asset'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='closed',
            field=models.BooleanField(default=False, verbose_name='Closed'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='error',
            field=models.BooleanField(default=False, verbose_name='Error'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='op_in_trx',
            field=models.PositiveIntegerField(verbose_name='Number of operation in transaction'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='trx_id',
            field=models.CharField(max_length=512, verbose_name='Transaction ID'),
        ),
        migrations.AlterField(
            model_name='bitsharestransnettransaction',
            name='trx_in_block',
            field=models.PositiveIntegerField(verbose_name='Number of transaction in blck'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='account_external',
            field=models.CharField(max_length=128, verbose_name='External blockchain account'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='account_internal',
            field=models.CharField(max_length=128, verbose_name='Internal blockchain account'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='amount',
            field=models.FloatField(verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='asset',
            field=models.CharField(max_length=128, verbose_name='Asset'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='closed',
            field=models.BooleanField(default=False, verbose_name='Closed'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='error',
            field=models.BooleanField(default=False, verbose_name='Error'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='op_in_trx',
            field=models.PositiveIntegerField(verbose_name='Number of operation in transaction'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='trx_id',
            field=models.CharField(max_length=512, verbose_name='Transaction ID'),
        ),
        migrations.AlterField(
            model_name='transnetbitsharestransaction',
            name='trx_in_block',
            field=models.PositiveIntegerField(verbose_name='Number of transaction in blck'),
        ),
    ]
