# Generated by Django 2.0.2 on 2018-03-24 11:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitsharestransaction',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 3, 24, 11, 35, 50, 746299, tzinfo=utc), verbose_name='Дата обработки'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transnettransaction',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 3, 24, 11, 35, 58, 759379, tzinfo=utc), verbose_name='Дата обработки'),
            preserve_default=False,
        ),
    ]
