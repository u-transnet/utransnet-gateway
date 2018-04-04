"""utransnetgateway URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls
from auth_custom.urls import urlpatterns as tf_urls
from django.views.generic import RedirectView

from two_factor.admin import AdminSiteOTPRequired

admin.site.__class__ = AdminSiteOTPRequired

urlpatterns = [
    path('', include(tf_urls)),
    path('', include(tf_twilio_urls)),
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('', RedirectView.as_view(url=reverse_lazy('admin:site_settings_settingsmodel_change', args=(1,)), permanent=False)),
    path('', admin.site.urls),
]
