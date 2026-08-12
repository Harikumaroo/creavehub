"""
CraveHub Django Settings
Production-ready, environment-variable driven.
"""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env from repo root / backend dir when present
def _load_env_file(path):
    """Manually load a .env file into os.environ (no dependencies)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, val = line.partition('=')
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:  # don't override real env vars
                    os.environ[key] = val
    except Exception:
        pass

# Try python-dotenv first, fall back to manual loader
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR.parent, '.env'), override=False)
    load_dotenv(os.path.join(BASE_DIR, '.env'), override=False)
except ImportError:
    _load_env_file(os.path.join(BASE_DIR.parent, '.env'))
    _load_env_file(os.path.join(BASE_DIR, '.env'))
except Exception:
    _load_env_file(os.path.join(BASE_DIR, '.env'))

# ── Core ──────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-use-50-char-min-secret")
DEBUG      = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# ── Apps ──────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",

    # CraveHub apps
    "accounts",
    "ai_engine",
    "core",
    "restaurants",
    "menu",
    "orders",
    "reviews",
    "banners",
    "cart",
    "categories",
    "dashboard",
    "instamart",
    "dining",
    "parties",
    "gifts",
    "catering",
    "notifications",
    "offers",
    "payments",
    "search",
    "tracking",
    "support",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF   = "cravehub.urls"
AUTH_USER_MODEL = "accounts.User"

TEMPLATES = [
    {
        "BACKEND":  "django.template.backends.django.DjangoTemplates",
        "DIRS":     [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS":  {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cravehub.wsgi.application"
ASGI_APPLICATION = "cravehub.asgi.application"

# ── Database configuration
# Priority: DATABASE_URL -> local SQLite (DEBUG or USE_SQLITE) -> PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_SQLITE = os.environ.get("USE_SQLITE", "") == "True"

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=60,
            ssl_require=not DEBUG,
        )
    }
elif DEBUG or USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.postgresql",
            "NAME":     os.environ.get("DB_NAME",     "cravehub_db"),
            "USER":     os.environ.get("DB_USER",     "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "root"),
            "HOST":     os.environ.get("DB_HOST",     "localhost"),
            "PORT":     os.environ.get("DB_PORT",     "5432"),
            "OPTIONS":  {
                "connect_timeout": 10,
                "sslmode": os.environ.get("DB_SSLMODE", "prefer"),
            },
            "CONN_MAX_AGE": 60,
        }
    }

# ── DRF ───────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.RevocableJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "EXCEPTION_HANDLER": "core.exception_handler.custom_exception_handler",
}

# ── Cache ──────────────────────────────────────────────────────
REDIS_URL = os.environ.get("REDIS_URL", "")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# ── JWT ───────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":    timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", 60))),
    "REFRESH_TOKEN_LIFETIME":   timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", 30))),
    "ROTATE_REFRESH_TOKENS":    True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN":        True,
    "ALGORITHM":                "HS256",
    "SIGNING_KEY":              SECRET_KEY,
    "AUTH_HEADER_TYPES":        ("Bearer",),
    "AUTH_TOKEN_CLASSES":       ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM":         "token_type",
    "JTI_CLAIM":                "jti",
    "USER_ID_FIELD":            "id",
    "USER_ID_CLAIM":            "user_id",
}

# ── CORS ──────────────────────────────────────────────────────
_cors_raw = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()] or [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # allow all in dev

# ── Static & Media ────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"

# ── Internationalisation ──────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Asia/Kolkata"
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Security hardening for production ─────────────────────────
if not DEBUG:
    SECURE_HSTS_SECONDS             = int(os.environ.get("SECURE_HSTS_SECONDS", 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
    SECURE_HSTS_PRELOAD             = True
    SECURE_SSL_REDIRECT             = os.environ.get("SECURE_SSL_REDIRECT", "True") == "True"
    SESSION_COOKIE_SECURE           = True
    CSRF_COOKIE_SECURE              = True
    SECURE_BROWSER_XSS_FILTER       = True
    SECURE_CONTENT_TYPE_NOSNIFF     = True
    SECURE_PROXY_SSL_HEADER         = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Logging ───────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
        "simple":  {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "cravehub": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO", "propagate": False},
    },
}

# ── SMS / OTP ─────────────────────────────────────────────────
SMS_BACKEND        = os.environ.get("SMS_BACKEND", "console")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")
MSG91_AUTH_KEY     = os.environ.get("MSG91_AUTH_KEY", "")
MSG91_SENDER_ID    = os.environ.get("MSG91_SENDER_ID", "CRAVEHUB")
OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))
OTP_MAX_ATTEMPTS   = int(os.environ.get("OTP_MAX_ATTEMPTS", 5))
OTP_LENGTH         = int(os.environ.get("OTP_LENGTH", 6))

# ── Razorpay ──────────────────────────────────────────────────
RAZORPAY_KEY_ID     = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")

# ── AI Engine ─────────────────────────────────────────────────
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_MODEL      = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL   = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

# Groq AI (OpenAI-compatible, ultra-fast inference)
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL        = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL     = "https://api.groq.com/openai/v1"

# ── Email / SMTP ──────────────────────────────────────────────
EMAIL_BACKEND       = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST          = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT          = int(os.environ.get("EMAIL_PORT", "587") or 587)
EMAIL_HOST_USER     = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS       = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL  = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@cravehub.local")

# ── Channels ──────────────────────────────────────────────────
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG":  {"hosts": [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }

# ── Cloudinary (optional) ─────────────────────────────────────
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL", "")
if CLOUDINARY_URL:
    import cloudinary
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)

# ── Sentry (optional) ─────────────────────────────────────────
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            send_default_pii=False,
        )
    except Exception:
        pass

# ── Rate limiting ─────────────────────────────────────────────
RATELIMIT_USE_CACHE = "default"
RATELIMIT_ENABLE    = not DEBUG

