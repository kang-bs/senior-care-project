import os
from dotenv import load_dotenv

# .env 파일 자동 로드 (로컬 환경에서만 적용됨)
load_dotenv()

# 개발 환경일 경우 HTTP 허용
if os.environ.get("FLASK_ENV") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

class Config:
    # 기본 설정
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")

    # SQLAlchemy configuration
    # For production (Railway)
    RAILWAY_DB_URI = os.getenv("DATABASE_URL")   # <-- 여기서 DATABASE_URL 읽도록 수정
    
    # For local development
    LOCAL_DB_URI = "mysql+pymysql://root:comep1522w@localhost:3306/senior_house"
    
    # Use Railway DB if available, otherwise fall back to local DB
    SQLALCHEMY_DATABASE_URI = RAILWAY_DB_URI if RAILWAY_DB_URI else LOCAL_DB_URI
    
    # Print database info (for debugging, remove in production)
    print(f"Using database: {'Railway' if RAILWAY_DB_URI else 'Local'}")
    if SQLALCHEMY_DATABASE_URI:
        print(f"Database host: {SQLALCHEMY_DATABASE_URI.split('@')[-1].split('/')[0]}")
    else:
        print("Database host: localhost")
    
    # Ensure the URI uses the correct scheme for SQLAlchemy
    if SQLALCHEMY_DATABASE_URI.startswith('mysql://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('mysql://', 'mysql+pymysql://', 1)
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

    # Naver OAuth
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

    # Kakao OAuth
    KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
    KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")

    # 세션 저장 방식
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")

    # 업로드 설정
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
