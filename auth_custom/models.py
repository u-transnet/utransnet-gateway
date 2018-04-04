from django import forms
from django.db import models
from django.contrib.auth import models as auth_models
from django.db.models.signals import post_save
from django_otp.util import random_hex
from phonenumber_field.modelfields import PhoneNumberField
from two_factor.models import PhoneDevice


class User(auth_models.AbstractUser):
    REQUIRED_FIELDS = ['email', 'phone']

    phone = PhoneNumberField(verbose_name='Номер телефона')

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs['instance']
        obj, created = PhoneDevice.objects.get_or_create(
            user=instance,
            defaults={
                'name': 'default',
                'number': instance.phone,
                'method': 'sms',
                'key': random_hex().decode('ascii')
            }
        )

        if not created:
            obj.number = instance.phone
            obj.save()

    class Meta(auth_models.User.Meta):
        pass


post_save.connect(User.post_save, User)
