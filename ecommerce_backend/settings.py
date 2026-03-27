import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ========== SECURITY - READ FROM ENVIRONMENT VARIABLES ==========
# Get secret key from environment variable (for production security)
SECRET_KEY = os.environ.get('SECRET_KEY', '8d6436fecc0239b6d1a2c9f3bf9775f2')

# Get debug mode from environment variable (False in production)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Get allowed hosts from environment variable (for production)
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# ========== END SECURITY ==========

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'api',
    # ========== ADDED FOR PRODUCTION ==========
    'whitenoise.runserver_nostatic',  # For serving static files in production
    # ========== END ADDED ==========
]

JAZZMIN_SETTINGS = {
    "site_title": "Melake Mihiret Admin",
    "site_header": "Melake Mihiret",
    "site_brand": "Melake Mihiret Cosmetics",
    "welcome_sign": "Welcome to Melake Mihiret Admin Panel",
    "copyright": "Melake Mihiret",
    "search_model": ["auth.User", "api.Product"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "api.Product": "fas fa-box",
        "api.Order": "fas fa-shopping-cart",
        "api.Category": "fas fa-tags",
        "api.Message": "fas fa-envelope",
    },
    "top_menu": [
        {"name": "Dashboard", "url": "admin:index", "icon": "fas fa-tachometer-alt"},
        {"name": "Products", "url": "admin:api_product_changelist", "icon": "fas fa-box"},
        {"name": "Orders", "url": "admin:api_order_changelist", "icon": "fas fa-shopping-cart"},
    ],
}

# ========== MIDDLEWARE - ADDED WHITENOISE FOR STATIC FILES ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ADDED: For serving static files in production
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ========== END MIDDLEWARE ==========

ROOT_URLCONF = 'ecommerce_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'ecommerce_backend.wsgi.application'

# ========== DATABASE - SUPPORTS BOTH SQLITE AND POSTGRESQL ==========
# Check if we have a DATABASE_URL (for production) or use SQLite (for development)
import dj_database_url

if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=not DEBUG  # Require SSL in production
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# ========== END DATABASE ==========

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========== STATIC & MEDIA FILES - CONFIGURED FOR PRODUCTION ==========
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # ADDED: Where collectstatic puts files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # ADDED: For efficient static file serving

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# ========== END STATIC & MEDIA ==========

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== CORS - READ FROM ENVIRONMENT VARIABLES ==========
# Get CORS allowed origins from environment variable (for production)
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# In development, allow all origins
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
# ========== END CORS ==========

# ========== CSRF TRUSTED ORIGINS - READ FROM ENVIRONMENT ==========
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(',')
# ========== END CSRF ==========

# ========== REST FRAMEWORK SETTINGS ==========
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
# ========== END REST FRAMEWORK ==========

# ========== ADDED: SECURITY SETTINGS FOR PRODUCTION ==========
# Only apply these in production (when DEBUG is False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    CSRF_COOKIE_SECURE = True  # Only send CSRF cookies over HTTPS
    SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS filter
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
    SECURE_HSTS_SECONDS = 31536000  # 1 year - HTTP Strict Transport Security
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
# ========== END SECURITY SETTINGS ==========
