from django.urls import path
from games import views

urlpatterns = [
    path('', views.game_lobby_view, name='game_lobby'),
    path('baccarat/', views.baccarat_view, name='baccarat'),
    path('baccarat/deal/', views.baccarat_deal_view, name='baccarat_deal'),
    path('crash/', views.crash_view, name='crash'),
    path('crash/new-round/', views.crash_new_round_view, name='crash_new_round'),
    path('crash/bet/', views.crash_bet_view, name='crash_bet'),
    path('crash/cashout/', views.crash_cashout_view, name='crash_cashout'),
    path('crash/finish/', views.crash_finish_round_view, name='crash_finish'),
    path('provably-fair/', views.provably_fair_verify_view, name='provably_fair'),
]
