import os

WSC_API_PREFIX = os.environ.get("API_PREFIX", "v1")
WSC_LOG_LEVEL = int(os.environ.get("LOG_LEVEL", "1"))
WSC_SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
WSC_DOMAIN = os.environ.get("DOMAIN", None)
WSC_SCHEME = os.environ.get("SCHEME", "https")

ADMIN_ROLE_USER = os.environ.get("ADMIN_ROLE_USER", None)
ADMIN_ROLE_PASSWORD = os.environ.get("ADMIN_ROLE_PASSWORD", None)

# -------------------------------------------------------------------------
# Only if used as a independent service
# -------------------------------------------------------------------------
WSC_REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
WSC_REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
WSC_REDIS_DB = int(os.environ.get("REDIS_DB", 1))
WSC_LISTEN_ADDR = os.environ.get("LISTEN_ADDR", "127.0.0.1")
WSC_LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "9000"))
