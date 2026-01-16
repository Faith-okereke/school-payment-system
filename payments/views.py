# payments/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Payment

@csrf_exempt  # Allows your frontend to send data without a CSRF token
def initiate_payment(request):
    if request.method == "POST":
        # 1. Get the data sent from the Frontend
        try:
            data = json.loads(request.body)
            email = data.get('email')
            amount = data.get('amount') # Amount in Naira
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not email or not amount:
            return JsonResponse({'error': 'Email and Amount are required'}, status=400)

        # 2. Save to Database
        payment = Payment.objects.create(email=email, amount=amount)
        payment.save()

        # 3. Send the keys back to Frontend so IT can open Paystack
        return JsonResponse({
            'status': 'success',
            'email': payment.email,
            'amount_kobo': payment.amount_value(),
            'ref': payment.ref,
            'public_key': settings.PAYSTACK_PUBLIC_KEY
        })

    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


@csrf_exempt
def verify_payment(request, ref):
    try:
        payment = Payment.objects.get(ref=ref)
        verified = payment.verify_payment()

        if verified:
            return JsonResponse({'status': 'success', 'message': 'Payment Verified'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Verification failed'}, status=400)

    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment reference not found'}, status=404)