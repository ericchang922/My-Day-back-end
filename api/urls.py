from django.urls import path
from . import views

app_name = 'api'
urlpatterns = [
    path('', views.index),
    path('myday/', views.my_day),
    path('message/', views.message)
]
