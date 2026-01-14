# payments/models.py
from django.db import models
import secrets

import requests

from school_fees_backend import settings

class Payment(models.Model):
    amount = models.PositiveIntegerField() # Amount in kobo (Paystack uses kobo)
    email = models.EmailField()
    ref = models.CharField(max_length=200) # Paystack reference
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self):
        return int(self.amount) * 100
    
    def verify_payment(self):
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        url = f'https://api.paystack.co/transaction/verify/{self.ref}'
        headers = {'Authorization': f'Bearer {paystack_secret_key}'}
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result['data']['status'] == 'success':
            self.verified = True
            self.save()
            return True
        return False