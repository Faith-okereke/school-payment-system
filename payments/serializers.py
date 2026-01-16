# payments/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentProfile  # <--- Import the new model

class UserSerializer(serializers.ModelSerializer):
    # We explicitly add this field because it's not part of the default User model
    reg_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'reg_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 1. Remove reg_number from the data (because User model doesn't accept it)
        reg_num = validated_data.pop('reg_number')
        
        # 2. Create the standard User
        user = User.objects.create_user(**validated_data)
        
        # 3. Create the Profile linked to that User
        StudentProfile.objects.create(user=user, reg_number=reg_num)
        
        return user