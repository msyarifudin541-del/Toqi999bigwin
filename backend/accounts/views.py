from decimal import Decimal
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from accounts.models import Wallet, Transaction

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Ensure user has a wallet
            Wallet.objects.get_or_create(user=self.request.user)
        return context


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        errors = []
        if not username:
            errors.append("Username is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != password_confirm:
            errors.append("Passwords do not match.")
        if User.objects.filter(username=username).exists():
            errors.append("Username already taken. Please choose another.")

        if errors:
            if request.headers.get('HX-Request'):
                return render(request, 'accounts/partials/auth_errors.html', {'errors': errors})
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Redirect'] = '/accounts/dashboard/'
            return response
        messages.success(request, f"Welcome to Toqi999bigwin, {username}! 1,000 bonus chips have been added to your wallet.")
        return redirect('dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Ensure wallet exists
            Wallet.objects.get_or_create(user=user)
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = '/accounts/dashboard/'
                return response
            return redirect('dashboard')
        else:
            error = "Invalid username or password."
            if request.headers.get('HX-Request'):
                return render(request, 'accounts/partials/auth_errors.html', {'errors': [error]})
            messages.error(request, error)

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    recent_transactions = wallet.transactions.all()[:10]
    recent_bets = request.user.bets.select_related('game_round').all()[:10]
    
    context = {
        'wallet': wallet,
        'transactions': recent_transactions,
        'bets': recent_bets,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def deposit_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        amount_str = request.POST.get('amount', '100')
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError()
            wallet.deposit(amount, description="Instant Reload Chips")
            messages.success(request, f"Successfully loaded ${amount:,.2f} chips into your wallet!")
        except Exception:
            messages.error(request, "Please enter a valid positive chip amount.")

        if request.headers.get('HX-Request'):
            return render(request, 'accounts/partials/wallet_badge.html', {'wallet': wallet})
            
        return redirect('dashboard')

    return render(request, 'accounts/deposit_modal.html', {'wallet': wallet})


@login_required
def wallet_badge_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'accounts/partials/wallet_badge.html', {'wallet': wallet})
