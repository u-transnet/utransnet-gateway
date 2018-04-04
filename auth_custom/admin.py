import django
from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext, gettext_lazy as _

from auth_custom.models import User


class ChangeUserAdminForm(auth_admin.UserChangeForm):
    phone = forms.CharField(label=User._meta.get_field('phone').verbose_name)


class CreationUserAdminForm(auth_admin.UserCreationForm):
    phone = forms.CharField(label=User._meta.get_field('phone').verbose_name)

    class Meta:
        model = User
        fields = ("username", "phone")
        field_classes = {'username': UsernameField}


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = ChangeUserAdminForm
    add_form = CreationUserAdminForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'password1', 'password2'),
        }),
    )

    list_display = ('username', 'email', 'phone', 'first_name', 'last_name', 'is_staff')
