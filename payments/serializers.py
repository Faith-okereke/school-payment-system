# payments/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentProfile

class UserSerializer(serializers.ModelSerializer):
    # These fields are for input only (Frontend sends them)
    reg_number = serializers.CharField(write_only=True)
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # We send these back to the frontend
        fields = ['id', 'username', 'email', 'password', 'reg_number', 'full_name', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'read_only': True},   # Generated automatically
            'first_name': {'read_only': True}, # Generated automatically
            'last_name': {'read_only': True}   # Generated automatically
        }

    def create(self, validated_data):
        # 1. Extract the custom fields
        reg_number = validated_data.pop('reg_number')
        full_name = validated_data.pop('full_name')
        
        # 2. Split Full Name (e.g., "John Doe" -> "John", "Doe")
        names = full_name.split(' ', 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ''

        # 3. Create User (Set username = reg_number)
        user = User.objects.create_user(
            username=reg_number,  # <--- HERE IS THE TRICK
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )
        
        # 4. Create Profile
        StudentProfile.objects.create(user=user, reg_number=reg_number)
        
        return user