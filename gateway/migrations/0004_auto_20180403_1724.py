# Generated by Django 2.0.2 on 2018-04-03 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0003_auto_20180330_1954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bitsharestransaction',
            name='amount',
            field=models.FloatField(verbose_name='Количество средств'),
        ),
        migrations.AlterField(
            model_name='transnettransaction',
            name='amount',
            field=models.FloatField(verbose_name='Количество средств'),
        ),
    ]