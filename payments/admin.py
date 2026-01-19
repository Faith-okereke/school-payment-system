from django.contrib import admin
from .models import Payment, StudentProfile

# This class customizes how the list looks
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'ref', 'status', 'date_created', 'verified')
    list_filter = ('status', 'verified', 'date_created')
    search_fields = ('ref', 'user__username', 'user__email')

# Register the model
admin.site.register(Payment, PaymentAdmin)
admin.site.register(StudentProfile)