import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-toqi999bigwin-pws-2026')
DEBUG = os.environ.get('PRODUCTION', 'False').lower() != 'true'

# ALLOWED_HOSTS & CSRF PWS
ALLOWED_HOSTS = [
    '*',
    'localhost',
    '127.0.0.1',
    '10.0.2.2',
    'toqi999bigwin.pws.cs.ui.ac.id',
    'muhammad.syarifudin51-toqi999bigwin.pws.cs.ui.ac.id',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.pws.cs.ui.ac.id',
    'https://toqi999bigwin.pws.cs.ui.ac.id',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party Apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Local Apps
    'accounts',
    'games',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Wajib untuk WhiteNoise (PBP Tutorial 01)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core_project.wsgi.application'

# Database Engine Setup
if os.environ.get('PRODUCTION', 'False').lower() == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'muhammad.syarifudin51'),
            'USER': os.environ.get('DB_USER', 'muhammad.syarifudin51'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'sK8Pj2BW'),
            'HOST': os.environ.get('DB_HOST', '10.119.106.139'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'options': f"-c search_path={os.environ.get('SCHEMA', 'public')}"
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static Files Setup (WhiteNoise Support)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
WHITENOISE_USE_FINDERS = True
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'