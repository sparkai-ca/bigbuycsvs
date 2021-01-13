from django.urls import path
from bigbuycsvs import views

urlpatterns = [
    path('', views.index),
    path('index/', views.index),
]
