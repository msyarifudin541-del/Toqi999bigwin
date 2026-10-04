from decimal import Decimal
from rest_framework import serializers
from games.models import GameRound, Bet

class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = [
            'id', 'round_uuid', 'game_type', 'server_seed_hash',
            'client_seed', 'nonce', 'crash_point', 'outcome_data',
            'status', 'started_at', 'ended_at'
        ]


class BetSerializer(serializers.ModelSerializer):
    game_round = GameRoundSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Bet
        fields = [
            'id', 'username', 'game_round', 'bet_amount', 'bet_choice',
            'auto_cashout', 'cashed_out_at', 'payout', 'status', 'created_at'
        ]


class BaccaratPlaySerializer(serializers.Serializer):
    bet_amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1.00'))
    bet_choice = serializers.ChoiceField(choices=['PLAYER', 'BANKER', 'TIE'])


class CrashBetSerializer(serializers.Serializer):
    bet_amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1.00'))
    auto_cashout = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('1.01'), required=False, allow_null=True)


class CrashCashoutSerializer(serializers.Serializer):
    bet_id = serializers.IntegerField()
    multiplier = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('1.00'))


class ProvablyFairVerifySerializer(serializers.Serializer):
    server_seed = serializers.CharField(max_length=128)
    client_seed = serializers.CharField(max_length=64, default="toqi999bigwin")
    nonce = serializers.IntegerField(min_value=1, default=1)
