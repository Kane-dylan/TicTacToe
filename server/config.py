import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_enhanced_database_url():
    """Get enhanced database URL with production parameters"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Fix for newer SQLAlchemy versions
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Enhance with production-specific parameters
    if not any(param in database_url for param in ['sslmode=', 'connect_timeout=', 'application_name=']):
        separator = '&' if '?' in database_url else '?'
        production_params = [
            'sslmode=require',
            'application_name=tictactoe-backend',
            'connect_timeout=30',
            'target_session_attrs=read-write'
        ]
        database_url = database_url + separator + '&'.join(production_params)
    
    return database_url

class Config:
    """Production configuration for Supabase deployment"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Database configuration
    try:
        SQLALCHEMY_DATABASE_URI = get_enhanced_database_url()
    except ValueError:
        SQLALCHEMY_DATABASE_URI = None
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Connection pool settings optimized for production deployment
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 3,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 2,
        'pool_timeout': 30,
        'connect_args': {
            'sslmode': 'require',
            'application_name': 'tictactoe-backend',
            'connect_timeout': 30
        }
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = False
    
    # Supabase Configuration (optional - for additional features)
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    # CORS configuration
    CLIENT_URL = os.getenv('CLIENT_URL', 'https://tic-tac-toe-ten-murex-86.vercel.app')
    CORS_ORIGINS = [CLIENT_URL]
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration values"""
        errors = []
        
        if not cls.SECRET_KEY:
            errors.append("SECRET_KEY environment variable is required")
        
        if not cls.JWT_SECRET_KEY:
            errors.append("JWT_SECRET_KEY environment variable is required")
            
        if not os.getenv('DATABASE_URL'):
            errors.append("DATABASE_URL environment variable is required")
            
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))
    
    @classmethod
    def log_configuration(cls):
        """Log configuration details for debugging"""
        logger.info("=== Configuration Status ===")
        logger.info(f"SECRET_KEY: {'SET' if cls.SECRET_KEY else 'NOT SET'}")
        logger.info(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
        logger.info(f"JWT_SECRET_KEY: {'SET' if cls.JWT_SECRET_KEY else 'NOT SET'}")
        logger.info(f"CLIENT_URL: {cls.CLIENT_URL}")
        logger.info(f"SUPABASE_URL: {'SET' if cls.SUPABASE_URL else 'NOT SET'}")
        logger.info("=============================")
