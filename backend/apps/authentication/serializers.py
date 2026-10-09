"""Serializers for the authentication app."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "username", "password", "password_confirm")
        extra_kwargs = {"email": {"required": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """Serializer for username/email + password login, issuing JWTs."""

    username_field = "email"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = self.user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the authenticated user profile."""

    class Meta:
        model = User
        fields = ("id", "email", "username", "date_joined")
        read_only_fields = ("id", "email", "username", "date_joined")
