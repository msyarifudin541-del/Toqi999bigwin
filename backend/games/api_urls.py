from django.urls import path
from games import api_views

urlpatterns = [
    path('baccarat/play/', api_views.BaccaratPlayAPIView.as_view(), name='api_baccarat_play'),
    path('crash/init-round/', api_views.CrashInitRoundAPIView.as_view(), name='api_crash_init'),
    path('crash/bet/', api_views.CrashBetAPIView.as_view(), name='api_crash_bet'),
    path('crash/cashout/', api_views.CrashCashoutAPIView.as_view(), name='api_crash_cashout'),
    path('crash/finish/', api_views.CrashFinishAPIView.as_view(), name='api_crash_finish'),
    path('history/', api_views.GameHistoryAPIView.as_view(), name='api_game_history'),
    path('verify/', api_views.ProvablyFairVerifyAPIView.as_view(), name='api_provably_fair_verify'),
]
