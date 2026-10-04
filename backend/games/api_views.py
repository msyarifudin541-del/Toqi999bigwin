from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from accounts.models import Wallet
from games.models import GameRound, Bet
from games.serializers import (
    GameRoundSerializer,
    BetSerializer,
    BaccaratPlaySerializer,
    CrashBetSerializer,
    CrashCashoutSerializer,
    ProvablyFairVerifySerializer,
)
from games.game_logic.baccarat import BaccaratEngine
from games.game_logic.crash import ProvablyFair, CrashEngine

shared_baccarat = BaccaratEngine(num_decks=8)

class BaccaratPlayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BaccaratPlaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        bet_amount = serializer.validated_data['bet_amount']
        bet_choice = serializer.validated_data['bet_choice']

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        if not wallet.has_funds(bet_amount):
            return Response({
                'success': False,
                'error': f'Insufficient balance! You have ${wallet.balance:,.2f}.',
                'balance': float(wallet.balance)
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            wallet.debit(bet_amount, description=f"Baccarat Mobile bet on {bet_choice}")

            result = shared_baccarat.play_round()
            payout_info = BaccaratEngine.calculate_payout(bet_choice, float(bet_amount), result.winner)

            server_seed = ProvablyFair.generate_server_seed()
            server_hash = ProvablyFair.hash_seed(server_seed)

            game_round = GameRound.objects.create(
                game_type='BACCARAT',
                server_seed=server_seed,
                server_seed_hash=server_hash,
                client_seed='toqi999bigwin',
                status='FINISHED',
                outcome_data=result.to_dict(),
                ended_at=timezone.now()
            )

            payout_decimal = Decimal(str(payout_info['total_return']))

            bet = Bet.objects.create(
                user=request.user,
                game_round=game_round,
                bet_amount=bet_amount,
                bet_choice=bet_choice,
                payout=payout_decimal,
                status=payout_info['status']
            )

            if payout_decimal > 0:
                wallet.credit(
                    payout_decimal,
                    description=f"Baccarat Mobile: {payout_info['description']}",
                    tx_type='WIN' if payout_info['status'] == 'WON' else 'REFUND'
                )

        return Response({
            'success': True,
            'result': result.to_dict(),
            'bet': BetSerializer(bet).data,
            'payout_info': payout_info,
            'balance': float(wallet.balance)
        })


class CrashInitRoundAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        server_seed = ProvablyFair.generate_server_seed()
        server_seed_hash = ProvablyFair.hash_seed(server_seed)
        client_seed = request.data.get('client_seed', 'toqi999bigwin')
        
        last_round = GameRound.objects.filter(game_type='CRASH').order_by('-id').first()
        nonce = (last_round.nonce + 1) if last_round else 1

        crash_multiplier, _ = ProvablyFair.generate_crash_point(server_seed, client_seed, nonce)

        game_round = GameRound.objects.create(
            game_type='CRASH',
            server_seed=server_seed,
            server_seed_hash=server_seed_hash,
            client_seed=client_seed,
            nonce=nonce,
            crash_point=Decimal(str(crash_multiplier)),
            status='PENDING'
        )

        return Response({
            'success': True,
            'round_id': game_round.id,
            'server_seed_hash': server_seed_hash,
            'client_seed': client_seed,
            'nonce': nonce,
            'duration_seconds': CrashEngine.get_time_for_multiplier(crash_multiplier)
        })


class CrashBetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        round_id = request.data.get('round_id')
        if not round_id:
            return Response({'success': False, 'error': 'round_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            game_round = GameRound.objects.get(id=round_id, game_type='CRASH')
        except GameRound.DoesNotExist:
            return Response({'success': False, 'error': 'Round not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CrashBetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        bet_amount = serializer.validated_data['bet_amount']
        auto_cashout = serializer.validated_data.get('auto_cashout')

        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        if not wallet.has_funds(bet_amount):
            return Response({
                'success': False,
                'error': f'Insufficient balance! You have ${wallet.balance:,.2f}.',
                'balance': float(wallet.balance)
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            wallet.debit(bet_amount, description=f"Crash Mobile bet on Round #{game_round.id}")
            bet = Bet.objects.create(
                user=request.user,
                game_round=game_round,
                bet_amount=bet_amount,
                bet_choice='CRASH',
                auto_cashout=auto_cashout,
                status='PENDING'
            )

        return Response({
            'success': True,
            'bet': BetSerializer(bet).data,
            'balance': float(wallet.balance)
        })


class CrashCashoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CrashCashoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        bet_id = serializer.validated_data['bet_id']
        claimed_multiplier = float(serializer.validated_data['multiplier'])

        try:
            bet = Bet.objects.get(id=bet_id, user=request.user, status='PENDING')
        except Bet.DoesNotExist:
            return Response({'success': False, 'error': 'Pending bet not found'}, status=status.HTTP_404_NOT_FOUND)

        actual_crash_point = float(bet.game_round.crash_point)
        wallet, _ = Wallet.objects.get_or_create(user=request.user)

        with transaction.atomic():
            if claimed_multiplier <= actual_crash_point:
                mult_dec = Decimal(f"{claimed_multiplier:.2f}")
                payout = bet.bet_amount * mult_dec
                bet.status = 'CASHED_OUT'
                bet.cashed_out_at = mult_dec
                bet.payout = payout
                bet.save()

                wallet.credit(payout, description=f"Cross Chicken Cashout @ {mult_dec}x", tx_type='WIN')

                return Response({
                    'success': True,
                    'status': 'CASHED_OUT',
                    'multiplier': float(mult_dec),
                    'payout': float(payout),
                    'balance': float(wallet.balance)
                })
            else:
                bet.status = 'LOST'
                bet.cashed_out_at = None
                bet.payout = Decimal('0.00')
                bet.save()

                return Response({
                    'success': False,
                    'status': 'LOST',
                    'multiplier': claimed_multiplier,
                    'crash_point': actual_crash_point,
                    'balance': float(wallet.balance)
                })


class CrashFinishAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        round_id = request.data.get('round_id')
        try:
            game_round = GameRound.objects.get(id=round_id, game_type='CRASH')
        except GameRound.DoesNotExist:
            return Response({'success': False, 'error': 'Round not found'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            game_round.status = 'FINISHED'
            game_round.ended_at = timezone.now()
            game_round.save()
            game_round.bets.filter(status='PENDING').update(status='LOST')

        return Response({
            'success': True,
            'server_seed': game_round.server_seed,
            'crash_point': float(game_round.crash_point)
        })


class GameHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bets = Bet.objects.filter(user=request.user).select_related('game_round')[:30]
        return Response({
            'success': True,
            'history': BetSerializer(bets, many=True).data
        })


class ProvablyFairVerifyAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProvablyFairVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        result = ProvablyFair.verify(data['server_seed'], data['client_seed'], data['nonce'])
        return Response({
            'success': True,
            'verification': result
        })
