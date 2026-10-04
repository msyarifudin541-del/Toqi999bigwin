import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class GameRound(models.Model):
    GAME_TYPES = [
        ('BACCARAT', 'Baccarat (Punto Banco)'),
        ('CRASH', 'Cross Chicken (Crash)'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending / Betting Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished'),
    ]

    round_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    server_seed = models.CharField(max_length=128)
    server_seed_hash = models.CharField(max_length=128)
    client_seed = models.CharField(max_length=64, default="toqi999bigwin")
    nonce = models.PositiveIntegerField(default=1)
    crash_point = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    outcome_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"[{self.game_type}] Round #{self.id} ({self.status})"


class Bet(models.Model):
    BET_STATUS = [
        ('PENDING', 'Pending'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
        ('CASHED_OUT', 'Cashed Out'),
        ('PUSH', 'Pushed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets')
    game_round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='bets')
    bet_amount = models.DecimalField(max_digits=12, decimal_places=2)
    bet_choice = models.CharField(max_length=50)  # 'PLAYER', 'BANKER', 'TIE', or 'CRASH'
    auto_cashout = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    cashed_out_at = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payout = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=BET_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.game_round.game_type} (${self.bet_amount:,.2f}) -> {self.status}"
