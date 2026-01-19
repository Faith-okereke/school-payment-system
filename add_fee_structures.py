#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_fees_backend.settings')
django.setup()

from payments.models import FeeStructure

# Create fee structures for each level
levels = ["100L", "200L", "300L", "400L"]
amounts = [50000, 60000, 70000, 80000]  # in kobo or your currency

for level, amount in zip(levels, amounts):
    fee, created = FeeStructure.objects.get_or_create(
        level=level,
        defaults={
            'amount': amount,
            'breakdown': []
        }
    )
    if created:
        print(f"Created: {level} - {amount}")
    else:
        print(f"Already exists: {level}")

print("Done!")
