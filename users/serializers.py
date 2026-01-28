"""user serializers."""

from rest_framework import serializers
from users.models import User, UserKYC


class UserSerializer(serializers.ModelSerializer):
    """User serializer class."""

    class Meta:
        """Meta class."""

        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ["id"]


class LogoutSerializer(serializers.Serializer):
    """Logout serializer class."""

    refresh = serializers.CharField(write_only=True)


class UserOurSerializer(serializers.Serializer):
    """User serializer class."""

    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    User = UserSerializer(read_only=True)


class UserLoginSerializer(serializers.Serializer):
    """User login serializer class."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class VerifyOTPSerializer(serializers.Serializer):
    """verify otp serializer."""

    otp = serializers.CharField(required=True)


class RequestOTPSerializer(serializers.Serializer):
    """request otp serializer."""

    email = serializers.EmailField(required=True)


class KYCSerializer(serializers.ModelSerializer):
    """kyc serializer."""

    class Meta:
        """meta class."""

        model = UserKYC
        fields = "__all__"
        read_only_fields = ["user"]
        extra_kwargs = {"approved": {"read_only": True}}

    def update(self, instance, validated_data):
        """update kyc instance."""
        request = self.context.get("request")
        if (
            request
            and request.user.is_superuser
            and not instance.approved
            and validated_data.get("approved")
        ):
            validated_data["approved"] = True
        return super().update(instance, validated_data)
