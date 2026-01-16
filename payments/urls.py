# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This means: when user visits the homepage, show initiate_payment
    path('', views.initiate_payment, name='initiate_payment'),
    
    # This handles the verification link
    path('verify/<str:ref>/', views.verify_payment, name='verify_payment'),
]