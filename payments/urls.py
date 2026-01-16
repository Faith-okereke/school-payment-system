# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('test-token/', views.test_token, name='test_token'),
    
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('verify/<str:ref>/', views.verify_payment, name='verify_payment'),
]