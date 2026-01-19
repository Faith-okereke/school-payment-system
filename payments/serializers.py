from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudentProfile
from .models import Payment


class UserSerializer(serializers.ModelSerializer):
    # 1. REMOVE the validators=[...] part here
    reg_number = serializers.CharField(write_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "reg_number", "full_name"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"read_only": True},
            "first_name": {"read_only": True},
            "last_name": {"read_only": True},
        }

    # 2. ADD this method to handle the uniqueness check manually
    def validate_reg_number(self, value):
        # We check if a User exists where username == value (the reg_number)
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This Reg Number is already registered.")
        return value

    # Add this method inside UserSerializer
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def create(self, validated_data):
        # CHANGE THIS LINE:
        # Instead of popping from validated_data (where it doesn't exist anymore),
        # grab it from the raw initial input.
        full_name = self.initial_data.get("full_name", "")

        # This one is still fine to pop because it's in validated_data
        reg_number = validated_data.pop("reg_number")

        # Split the name
        names = full_name.split(" ", 1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ""

        user = User.objects.create_user(
            username=reg_number,
            email=validated_data.get("email", ""),  # Use .get() to be safe
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
        )

        # Create Profile (ensure you have the import for StudentProfile)
        from .models import StudentProfile

        StudentProfile.objects.create(user=user, reg_number=reg_number)

        return user


class PaymentSerializer(serializers.ModelSerializer):
    # Map 'date_created' to 'date' to match frontend
    date = serializers.DateTimeField(source="date_created", format="%Y-%m-%d")
    # Map 'ref' to 'reference' if your model uses 'ref'
    reference = serializers.CharField(source="ref")

    class Meta:
        model = Payment
        fields = ["id", "reference", "amount", "status", "date", "purpose", "session"]
