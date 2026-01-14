# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from .models import Payment
from django.conf import settings
from django.contrib import messages
import requests

def initiate_payment(request: HttpRequest):
    if request.method == "POST":
        amount = request.POST['amount']
        email = request.POST['email']

        pk = settings.PAYSTACK_PUBLIC_KEY

        payment = Payment.objects.create(amount=amount, email=email)
        payment.save()

        context = {
            'payment': payment,
            'field_values': request.POST,
            'paystack_pub_key': pk,
            'amount_value': payment.amount_value(),
        }
        return render(request, 'make_payment.html', context)

    return render(request, 'payment.html')

def verify_payment(request: HttpRequest, ref: str):
    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()

    if verified:
        messages.success(request, "Verification Successful")
    else:
        messages.error(request, "Verification Failed")
    
    return redirect('initiate_payment')