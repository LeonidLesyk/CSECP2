from django.urls import path

from . import views

urlpatterns = [
    path('sendmessage/', views.send, name='send'),
    path('readmessage/', views.read, name='reasmessage'),
    path('certify/', views.certify, name='certify'),
    path('registeruser/', views.register, name='registeruser'),
    
]