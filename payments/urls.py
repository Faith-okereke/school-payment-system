# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("test-token/", views.test_token, name="test_token"),
    path("fee-structure/", views.fee_structure, name="fee_structure"),
    path("initiate-payment/", views.initiate_payment, name="initiate_payment"),
    path("verify/<str:ref>/", views.verify_payment, name="verify_payment"),
    path("payment-history/", views.payment_history, name="payment-history"),
]
