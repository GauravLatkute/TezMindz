import dj_database_url
from decouple import config

from .base import *  # noqa: F401,F403
from .base import BASE_DIR

DEBUG = False

# No sqlite fallback in production — fail loudly at startup if this is
# missing rather than silently writing to a local sqlite file on Render.
DATABASES = {"default": dj_database_url.config(env="DATABASE_URL", conn_max_age=600)}

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
