from django.urls import path
from accounts import api_views

urlpatterns = [
    path('register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('profile/', api_views.ProfileAPIView.as_view(), name='api_profile'),
    path('deposit/', api_views.DepositAPIView.as_view(), name='api_deposit'),
    path('transactions/', api_views.TransactionListAPIView.as_view(), name='api_transactions'),
]
