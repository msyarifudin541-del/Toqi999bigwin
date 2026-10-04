from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from accounts.models import Wallet, Transaction

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create(user=instance)
        # Record initial complimentary welcome chips
        Transaction.objects.create(
            wallet=wallet,
            transaction_type='DEPOSIT',
            amount=wallet.balance,
            balance_after=wallet.balance,
            description="Welcome Bonus Chips!"
        )

@receiver(post_save, sender=User)
def save_user_wallet(sender, instance, **kwargs):
    if hasattr(instance, 'wallet'):
        instance.wallet.save()
