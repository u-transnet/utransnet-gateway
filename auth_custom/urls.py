from django.conf.urls import url
from two_factor.views import LoginView

core = [
    url(
        regex=r'^account/login/$',
        view=LoginView.as_view(),
        name='login',
    )
]

urlpatterns = (core, 'two_factor')