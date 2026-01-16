# payments/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}} # Don't show password in responses

    def create(self, validated_data):
        # This securely hashes the password (turns "1234" into "pbkdf2$...")
        user = User.objects.create_user(**validated_data)
        return user