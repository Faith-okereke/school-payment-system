# payments/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Payment
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import PaymentSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from .models import FeeStructure, StudentProfile
import requests


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


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_payment(request, ref):
    # 1. Get the payment from your DB (it's currently 'pending')
    payment = get_object_or_404(Payment, ref=ref)

    # 2. Check if it's already verified (to save time)
    if payment.verified:
        return Response(PaymentSerializer(payment).data)

    # 3. Ask Paystack: "Did this guy actually pay?"
    url = f"https://api.paystack.co/transaction/verify/{ref}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        result = response.json()

        # 4. If Paystack says "success", WE UPDATE OUR DB
        if result['status'] is True and result['data']['status'] == 'success':
            
            # --- THE MAGIC LINES ---
            payment.verified = True
            payment.status = 'success'  # <--- This updates the status
            payment.save()              # <--- This commits the change to DB
            # -----------------------
            
            return Response(PaymentSerializer(payment).data)
        
        else:
            return Response({"error": "Payment verification failed"}, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create a token for the new user immediately
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # <--- Crucial: Blocks unauthenticated access
def payment_history(request):
    # 1. Get the logged-in user
    user = request.user
    
    # 2. Filter payments for THIS user only, ordered by newest first
    payments = Payment.objects.filter(user=user).order_by('-date_created')
    
    # 3. Serialize the data
    serializer = PaymentSerializer(payments, many=True)
    
    # 4. Return JSON
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fee_structure(request):
    """Get the current fee structure for the user's level"""
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        user_level = student_profile.level  # e.g., "400L"
        
        # Fetch fee structure from database
        fee = FeeStructure.objects.get(level=user_level)
        return Response({
            'level': fee.level,
            'amount': fee.amount,
            'breakdown': fee.breakdown  # If stored as JSON field
        })
    except StudentProfile.DoesNotExist:
        return Response(
            {'error': 'Student profile not found'},
            status=404
        )
    except FeeStructure.DoesNotExist:
        return Response(
            {'error': 'Fee structure not found for your level'},
            status=404
        )