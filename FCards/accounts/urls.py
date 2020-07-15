from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('accounts/sign_up/', views.sign_up, name="sign-up"),
    path('accounts/overview/', views.overview, name="account_overview"),
    path('accounts/delete/', views.delete_account, name="delete_account"),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
