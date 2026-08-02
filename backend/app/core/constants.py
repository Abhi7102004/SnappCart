"""Application-wide constants — avoid magic numbers/strings scattered in code"""

# ── Auth / Login ──────────────────────────────────────────────────
MAX_FAILED_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 30

# ── Tokens ────────────────────────────────────────────────────────
EMAIL_VERIFY_TOKEN_EXPIRE_HOURS = 24
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1

# ── Redis Keys ────────────────────────────────────────────────────
REFRESH_TOKEN_PREFIX = "refresh_token:"
OTP_PREFIX = "otp:"
RATE_LIMIT_PREFIX = "rate_limit:"

# ── Cookies ───────────────────────────────────────────────────────
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"