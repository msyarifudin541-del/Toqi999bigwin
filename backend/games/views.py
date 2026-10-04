from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction

from accounts.models import Wallet
from games.models import GameRound, Bet
from games.game_logic.baccarat import BaccaratEngine
from games.game_logic.crash import ProvablyFair, CrashEngine

# Shared in-memory engine for session shoe consistency
baccarat_engine = BaccaratEngine(num_decks=8)

@login_required
def game_lobby_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    recent_wins = Bet.objects.filter(status='WON').select_related('user', 'game_round')[:8]
    return render(request, 'games/lobby.html', {
        'wallet': wallet,
        'recent_wins': recent_wins
    })


@login_required
def baccarat_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    recent_history = GameRound.objects.filter(game_type='BACCARAT', status='FINISHED')[:12]
    return render(request, 'games/baccarat.html', {
        'wallet': wallet,
        'recent_history': recent_history
    })


@login_required
def baccarat_deal_view(request):
    """Handles baccarat bet placement and resolution (HTMX supported)."""
    if request.method != 'POST':
        return redirect('baccarat')

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    bet_choice = request.POST.get('bet_choice', '').upper()
    
    if bet_choice not in ['PLAYER', 'BANKER', 'TIE']:
        return render(request, 'games/partials/baccarat_message.html', {
            'error': 'Please select Player, Banker, or Tie before dealing.'
        })

    try:
        bet_amount = Decimal(request.POST.get('bet_amount', '10.00'))
        if bet_amount <= 0:
            raise ValueError()
    except Exception:
        return render(request, 'games/partials/baccarat_message.html', {
            'error': 'Invalid bet amount. Minimum bet is $1.00.'
        })

    if not wallet.has_funds(bet_amount):
        return render(request, 'games/partials/baccarat_message.html', {
            'error': f'Insufficient balance! You have ${wallet.balance:,.2f}. Deposit chips to continue playing.'
        })

    # Execute round inside atomic transaction
    with transaction.atomic():
        # Debit bet from wallet
        wallet.debit(bet_amount, description=f"Baccarat bet on {bet_choice}")

        # Run game engine
        result = baccarat_engine.play_round()
        payout_info = BaccaratEngine.calculate_payout(bet_choice, float(bet_amount), result.winner)

        # Generate provably fair seeds for record
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

        # Credit winnings or push refund if applicable
        if payout_decimal > 0:
            wallet.credit(
                payout_decimal,
                description=f"Baccarat payout: {payout_info['description']}",
                tx_type='WIN' if payout_info['status'] == 'WON' else 'REFUND'
            )

    recent_history = GameRound.objects.filter(game_type='BACCARAT', status='FINISHED')[:12]

    context = {
        'wallet': wallet,
        'result': result.to_dict(),
        'bet': bet,
        'payout_info': payout_info,
        'recent_history': recent_history,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'games/partials/baccarat_table.html', context)
    return render(request, 'games/baccarat.html', context)


@login_required
def crash_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    recent_crashes = GameRound.objects.filter(game_type='CRASH', status='FINISHED')[:15]
    return render(request, 'games/crash.html', {
        'wallet': wallet,
        'recent_crashes': recent_crashes
    })


@login_required
def crash_new_round_view(request):
    """Pre-generates a provably fair crash round for the client session."""
    server_seed = ProvablyFair.generate_server_seed()
    server_seed_hash = ProvablyFair.hash_seed(server_seed)
    client_seed = request.GET.get('client_seed', 'toqi999bigwin')
    
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

    return JsonResponse({
        'round_id': game_round.id,
        'server_seed_hash': server_seed_hash,
        'client_seed': client_seed,
        'nonce': nonce,
        'duration_seconds': CrashEngine.get_time_for_multiplier(crash_multiplier)
    })


@login_required
def crash_bet_view(request):
    """Place a bet on an active or pending crash round."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    round_id = request.POST.get('round_id')
    game_round = get_object_or_404(GameRound, id=round_id, game_type='CRASH')

    try:
        bet_amount = Decimal(request.POST.get('bet_amount', '10.00'))
        if bet_amount <= 0:
            raise ValueError()
    except Exception:
        return JsonResponse({'error': 'Invalid bet amount'}, status=400)

    if not wallet.has_funds(bet_amount):
        return JsonResponse({'error': 'Insufficient balance'}, status=400)

    auto_cashout = request.POST.get('auto_cashout')
    auto_cashout_dec = Decimal(auto_cashout) if auto_cashout else None

    with transaction.atomic():
        wallet.debit(bet_amount, description=f"Cross Chicken bet on Round #{game_round.id}")
        bet = Bet.objects.create(
            user=request.user,
            game_round=game_round,
            bet_amount=bet_amount,
            bet_choice='CRASH',
            auto_cashout=auto_cashout_dec,
            status='PENDING'
        )

    return JsonResponse({
        'success': True,
        'bet_id': bet.id,
        'balance': float(wallet.balance)
    })


@login_required
def crash_cashout_view(request):
    """Player cashes out at the given multiplier."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    bet_id = request.POST.get('bet_id')
    claimed_multiplier = float(request.POST.get('multiplier', '1.00'))

    bet = get_object_or_404(Bet, id=bet_id, user=request.user, status='PENDING')
    game_round = bet.game_round

    actual_crash_point = float(game_round.crash_point)

    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    with transaction.atomic():
        if claimed_multiplier <= actual_crash_point:
            # Won!
            mult_dec = Decimal(f"{claimed_multiplier:.2f}")
            payout = bet.bet_amount * mult_dec
            bet.status = 'CASHED_OUT'
            bet.cashed_out_at = mult_dec
            bet.payout = payout
            bet.save()

            wallet.credit(payout, description=f"Cross Chicken Cashed Out @ {mult_dec}x", tx_type='WIN')

            return JsonResponse({
                'success': True,
                'status': 'CASHED_OUT',
                'multiplier': float(mult_dec),
                'payout': float(payout),
                'balance': float(wallet.balance)
            })
        else:
            # Busted!
            bet.status = 'LOST'
            bet.cashed_out_at = None
            bet.payout = Decimal('0.00')
            bet.save()

            return JsonResponse({
                'success': False,
                'status': 'LOST',
                'multiplier': claimed_multiplier,
                'crash_point': actual_crash_point,
                'balance': float(wallet.balance)
            })


@login_required
def crash_finish_round_view(request):
    """Finalizes the round and marks remaining pending bets as LOST."""
    round_id = request.POST.get('round_id')
    game_round = get_object_or_404(GameRound, id=round_id, game_type='CRASH')

    with transaction.atomic():
        game_round.status = 'FINISHED'
        game_round.ended_at = timezone.now()
        game_round.save()

        # Any bet still PENDING is lost
        game_round.bets.filter(status='PENDING').update(status='LOST')

    return JsonResponse({
        'success': True,
        'server_seed': game_round.server_seed,
        'crash_point': float(game_round.crash_point)
    })


def provably_fair_verify_view(request):
    context = {}
    if request.method == 'POST':
        server_seed = request.POST.get('server_seed', '').strip()
        client_seed = request.POST.get('client_seed', 'toqi999bigwin').strip()
        try:
            nonce = int(request.POST.get('nonce', '1'))
            if server_seed:
                result = ProvablyFair.verify(server_seed, client_seed, nonce)
                context['verification'] = result
        except Exception as e:
            context['error'] = str(e)

    return render(request, 'games/provably_fair.html', context)
