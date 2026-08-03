from django.urls import path

from . import views

app_name = 'sitio'

urlpatterns = [
    path('', views.inicio, name='inicio'),
]
