import os
from dotenv import load_dotenv

# .env 파일을 자동으로 로드
load_dotenv()

# 개발 환경일 경우 HTTP 허용
if os.environ.get("FLASK_ENV") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

class Config:
    # 기본 설정
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")

    # SQLAlchemy
    # Use Railway's MySQL service
    SQLALCHEMY_DATABASE_URI = os.getenv("MYSQL_URL") or os.getenv("MYSQL_PUBLIC_URL")
    
    if not SQLALCHEMY_DATABASE_URI:
        # For local development, use environment variables or default values
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "Ckdhfma1406!")
        db_host = os.getenv("DB_HOST", "mysql.railway.internal")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "railway")
        
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Ensure the URI uses the correct scheme for SQLAlchemy
    if SQLALCHEMY_DATABASE_URI.startswith('mysql://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('mysql://', 'mysql+pymysql://', 1)
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth 환경 변수 키 이름
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

    # Kakao OAuth 환경 변수 키 이름
    KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
    KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")

    # 세션 저장 방식
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}