"""
Core URL Configuration for Toqi999bigwin.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root / Landing page
    path('', HomeView.as_view(), name='home'),
    
    # Accounts & Wallet Web Views (HTMX supported)
    path('accounts/', include('accounts.urls')),
    
    # Core Games Web Views (HTMX supported)
    path('games/', include('games.urls')),
    
    # REST API endpoints for Mobile App (Flutter)
    path('api/accounts/', include('accounts.api_urls')),
    path('api/games/', include('games.api_urls')),
]
