# payments/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Payment
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # <--- Only logged-in users can access this!
def initiate_payment(request):
    user = request.user  # This is automatically found from the Token
    data = request.data
    amount = data.get("amount")
    email = user.email  # Use the email from the account, don't ask for it again

    payment = Payment.objects.create(user=user, email=email, amount=amount)
    payment.save()

    return Response(
        {
            "status": "success",
            "email": payment.email,
            "amount_kobo": payment.amount_value(),
            "ref": payment.ref,
            "public_key": settings.PAYSTACK_PUBLIC_KEY,
        }
    )


@csrf_exempt
def verify_payment(request, ref):
    try:
        payment = Payment.objects.get(ref=ref)
        verified = payment.verify_payment()

        if verified:
            return Response({"status": "success", "message": "Payment Verified"})
        else:
            return Response(
                {"status": "failed", "message": "Verification failed"}, status=400
            )

    except Payment.DoesNotExist:
        return Response({"error": "Payment reference not found"}, status=404)


# --- AUTHENTICATION VIEWS ---


@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create a token for the new user immediately
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=400)


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    # Check if this user exists
    user = authenticate(username=username, password=password)

    if user is not None:
        # Get or create token for this user
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response({"token": token.key, "user": serializer.data})

    return Response({"error": "Invalid Credentials"}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Blocks access if no token provided
def test_token(request):
    return Response("passed for {}".format(request.user.email))
