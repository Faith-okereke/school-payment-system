# school_fees_project/urls.py
from django.contrib import admin
from django.urls import path, include  # <-- Make sure 'include' is here

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Add this line to link your payments app
    path('', include('payments.urls')), 
]