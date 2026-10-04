from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Wallet, Transaction

class AccountsModelTests(TestCase):
    def test_user_wallet_creation_signal(self):
        user = User.objects.create_user(username='testplayer', password='password123')
        self.assertTrue(hasattr(user, 'wallet'))
        self.assertEqual(user.wallet.balance, Decimal('1000.00'))
        self.assertEqual(user.wallet.transactions.count(), 1)

    def test_wallet_deposit_and_debit(self):
        user = User.objects.create_user(username='bettor', password='password123')
        wallet = user.wallet

        wallet.deposit(Decimal('250.00'), "Test deposit")
        self.assertEqual(wallet.balance, Decimal('1250.00'))

        wallet.debit(Decimal('100.00'), "Test bet")
        self.assertEqual(wallet.balance, Decimal('1150.00'))

        with self.assertRaises(ValueError):
            wallet.debit(Decimal('5000.00'))
