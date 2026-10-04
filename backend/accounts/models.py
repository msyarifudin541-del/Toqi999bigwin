from decimal import Decimal
from django.db import models, transaction
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('1000.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet (${self.balance:,.2f})"

    def has_funds(self, amount):
        amount = Decimal(str(amount))
        return self.balance >= amount and amount > 0

    @transaction.atomic
    def deposit(self, amount, description="Deposit chips"):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])
        
        tx = Transaction.objects.create(
            wallet=self,
            transaction_type='DEPOSIT',
            amount=amount,
            balance_after=self.balance,
            description=description
        )
        return tx

    @transaction.atomic
    def debit(self, amount, description="Game Bet", tx_type='BET'):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient balance.")
        self.balance -= amount
        self.save(update_fields=['balance', 'updated_at'])

        tx = Transaction.objects.create(
            wallet=self,
            transaction_type=tx_type,
            amount=-amount,
            balance_after=self.balance,
            description=description
        )
        return tx

    @transaction.atomic
    def credit(self, amount, description="Game Win", tx_type='WIN'):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])

        tx = Transaction.objects.create(
            wallet=self,
            transaction_type=tx_type,
            amount=amount,
            balance_after=self.balance,
            description=description
        )
        return tx


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdrawal'),
        ('BET', 'Game Bet'),
        ('WIN', 'Game Win'),
        ('REFUND', 'Refund / Push'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.transaction_type}] {self.wallet.user.username} {self.amount:+,.2f} (Bal: {self.balance_after:,.2f})"
