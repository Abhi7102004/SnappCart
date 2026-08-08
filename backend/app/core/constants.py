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
RESEND_VERIFY_PREFIX = "resend_verify:"
FORGOT_PASSWORD_PREFIX = "forgot_password:"

# ── Cookies ───────────────────────────────────────────────────────
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"

# ── Email / Cooldowns ─────────────────────────────────────────────
RESEND_VERIFICATION_COOLDOWN_SECONDS = 60
FORGOT_PASSWORD_COOLDOWN_SECONDS = 60

# ── OAuth ─────────────────────────────────────────────────────────
OAUTH_STATE_PREFIX = "oauth_state:"
OAUTH_STATE_TTL_SECONDS = 300

# ── Pagination ────────────────────────────────────────────────────
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── 2FA ───────────────────────────────────────────────────────────
BACKUP_CODE_COUNT = 5
TWO_FA_ISSUER = "SnappCart"
TWO_FA_TOTP_PREFIX = "2fa_pending:"
TWO_FA_TOTP_TTL_SECONDS = 300