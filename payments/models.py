# payments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings  # <--- Best practice for importing settings
import secrets
import requests

class Payment(models.Model):
    # Link to the User (null=True allows guest payments without crashing)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    amount = models.PositiveIntegerField()
    email = models.EmailField()
    ref = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    purpose = models.CharField(max_length=200, default='School Fees', blank=True)
    session = models.CharField(max_length=100, default='2025/2026', blank=True)

    def __str__(self):
        # Safety check: If there is a user, show their name. If not, show "Guest"
        if self.user:
            return f"{self.user.username} - {self.amount}"
        return f"Guest - {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            if not Payment.objects.filter(ref=ref).exists():
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self):
        return int(self.amount) * 100
    
    def verify_payment(self):
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        url = f'https://api.paystack.co/transaction/verify/{self.ref}'
        headers = {'Authorization': f'Bearer {paystack_secret_key}'}
        
        try:
            response = requests.get(url, headers=headers)
            result = response.json()
            
            if result['data']['status'] == 'success':
                self.verified = True
                self.save()
                return True
        except Exception as e:
            print(f"Error verifying payment: {e}")
            
        return False


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reg_number = models.CharField(max_length=11)
    level = models.CharField(max_length=10, default="100L")  # e.g., "100L", "200L", "300L", "400L"

    def __str__(self):
        return self.reg_number

class FeeStructure(models.Model):
    level = models.CharField(max_length=10, unique=True)  # "400L", "300L", etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    breakdown = models.JSONField(default=list)  # Store fee items as JSON
    
    def __str__(self):
        return f"Fee Structure - {self.level}"