from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from accounts.models import Wallet, Transaction
from accounts.serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    DepositSerializer,
    TransactionSerializer,
)

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            return Response({
                'success': True,
                'token': token.key,
                'user': user_data,
                'message': 'Registration successful!'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            # Ensure wallet exists
            Wallet.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            return Response({
                'success': True,
                'token': token.key,
                'user': user_data,
                'message': 'Login successful!'
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        user_data = UserSerializer(request.user).data
        return Response({
            'success': True,
            'user': user_data
        })


class DepositAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            tx = wallet.deposit(amount, description="Mobile App Deposit")
            return Response({
                'success': True,
                'message': f"Successfully deposited ${amount:,.2f}!",
                'balance': float(wallet.balance),
                'transaction': TransactionSerializer(tx).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TransactionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        transactions = wallet.transactions.all()[:50]
        return Response({
            'success': True,
            'transactions': TransactionSerializer(transactions, many=True).data
        })
