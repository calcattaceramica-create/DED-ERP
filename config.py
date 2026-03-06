import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    database_url = os.environ.get('DATABASE_URL')
    # Fix for Render.com PostgreSQL URL (postgres:// -> postgresql://)
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = database_url or \
        'sqlite:///' + os.path.join(basedir, 'erp_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Application
    APP_NAME = os.environ.get('APP_NAME') or 'نظام إدارة المخزون المتكامل'
    # Base domain used for building tenant subdomain URLs (e.g. calcatta-ceramica.sbs)
    BASE_DOMAIN = os.environ.get('BASE_DOMAIN', '')
    DEFAULT_LANGUAGE = 'ar'
    BABEL_DEFAULT_LOCALE = 'ar'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Riyadh'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    LANGUAGES = {
        'ar': {'name': 'العربية', 'flag': '🇸🇦', 'dir': 'rtl'},
        'en': {'name': 'English', 'flag': '🇬🇧', 'dir': 'ltr'}
    }

    # Session Security – using Flask's built-in signed-cookie sessions
    # (Flask-Session filesystem mode caused data loss across Gunicorn workers)
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Session expires after 8 hours

    # Auto-detect HTTPS: Check if SSL certificates exist
    _ssl_cert_exists = os.path.exists(os.path.join(basedir, 'ssl', 'cert.pem'))
    SESSION_COOKIE_SECURE = _ssl_cert_exists or (os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True')

    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    SESSION_REFRESH_EACH_REQUEST = True  # Refresh session on each request

    # Security
    WTF_CSRF_ENABLED = True  # Enable CSRF protection
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    MAX_LOGIN_ATTEMPTS = 5  # Maximum failed login attempts before account lock
    ACCOUNT_LOCK_DURATION = 30  # Account lock duration in minutes
    SESSION_TIMEOUT_WARNING = 5  # Show warning 5 minutes before session expires

    # HTTPS/SSL Settings
    PREFERRED_URL_SCHEME = 'https' if _ssl_cert_exists else 'http'
    PASSWORD_MIN_LENGTH = 8  # Minimum password length
    PASSWORD_REQUIRE_UPPERCASE = True  # Require uppercase letter
    PASSWORD_REQUIRE_DIGIT = True  # Require digit
    PASSWORD_REQUIRE_SPECIAL = False  # Require special character (optional)
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'csv'}
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Currency
    DEFAULT_CURRENCY = 'EUR'
    CURRENCIES = {
        'EUR': {'name': 'يورو', 'symbol': '€'},
        'SAR': {'name': 'ريال سعودي', 'symbol': 'ر.س'},
        'USD': {'name': 'دولار أمريكي', 'symbol': '$'},
        'AED': {'name': 'درهم إماراتي', 'symbol': 'د.إ'},
        'KWD': {'name': 'دينار كويتي', 'symbol': 'د.ك'},
        'BHD': {'name': 'دينار بحريني', 'symbol': 'د.ب'},
        'JOD': {'name': 'دينار أردني', 'symbol': 'د.أ'},
        'IQD': {'name': 'دينار عراقي', 'symbol': 'ع.د'},
        'LYD': {'name': 'دينار ليبي', 'symbol': 'د.ل'},
        'TND': {'name': 'دينار تونسي', 'symbol': 'د.ت'},
        'DZD': {'name': 'دينار جزائري', 'symbol': 'د.ج'},
        'OMR': {'name': 'ريال عماني', 'symbol': 'ر.ع'},
        'QAR': {'name': 'ريال قطري', 'symbol': 'ر.ق'},
        'EGP': {'name': 'جنيه مصري', 'symbol': 'ج.م'},
    }
    
    # Tax
    DEFAULT_TAX_RATE = 18.0  # VAT 18%

    # Admin Panel IP Restriction (optional)
    # Comma-separated IPs allowed to access /settings and /admin routes.
    # Leave empty to allow all IPs (default).
    # Example: ADMIN_IP_WHITELIST=192.168.1.10,10.0.0.5
    _raw_ips = os.environ.get('ADMIN_IP_WHITELIST', '')
    ADMIN_IP_WHITELIST = [ip.strip() for ip in _raw_ips.split(',') if ip.strip()]

    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_PLAN_PRICE_IDS = {
        'monthly': os.environ.get('STRIPE_PRICE_MONTHLY', ''),
        'yearly':  os.environ.get('STRIPE_PRICE_YEARLY',  ''),
    }
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    TEMPLATES_AUTO_RELOAD = False   # no hot-reload in production
    SEND_FILE_MAX_AGE_DEFAULT = 86400  # cache static files for 24h
    SQLALCHEMY_ECHO = False         # no SQL logging in production

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

