from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from accounts.models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'wallet']
        read_only_fields = ['id', 'wallet']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError("Must provide both username and password.")
        data['user'] = user
        return data


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('1.00'))


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'balance_after', 'description', 'created_at']
