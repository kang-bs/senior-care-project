import os
from dotenv import load_dotenv

# Load environment variables
# In development, load from .env.local, otherwise from .env
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()

# 개발 환경일 경우 HTTP 허용
if os.environ.get("FLASK_ENV") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

class Config:
    # 기본 설정
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")

    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
    AWS_S3_REGION = os.environ.get("AWS_S3_REGION")

    # SQLAlchemy configuration
    # Railway에서 제공하는 DATABASE_URL 사용 (이미 mysql+pymysql 형태로 설정됨)
    RAILWAY_DB_URI = os.getenv("DATABASE_URL")
    
    # For local development
    LOCAL_DB_URI = "mysql+pymysql://root:comep1522w@localhost:3306/senior_house"
    
    # Railway DATABASE_URL 우선 사용, 없으면 로컬 DB 사용
    SQLALCHEMY_DATABASE_URI = RAILWAY_DB_URI if RAILWAY_DB_URI else LOCAL_DB_URI
    
    # Print database info (for debugging)
    print(f"🔍 환경변수 DATABASE_URL: {RAILWAY_DB_URI}")
    print(f"Using database: {'Railway' if RAILWAY_DB_URI else 'Local'}")
    print(f"Final SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
    
    if SQLALCHEMY_DATABASE_URI:
        try:
            # URL에서 호스트 정보 추출
            if '@' in SQLALCHEMY_DATABASE_URI:
                host_part = SQLALCHEMY_DATABASE_URI.split('@')[1].split('/')[0]
                print(f"Database host: {host_part}")
            else:
                print("Database host: localhost")
        except Exception as e:
            print(f"Database host: parsing failed - {e}")
    
    # Railway 환경 감지
    IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None
    print(f"🚂 Railway 환경: {IS_RAILWAY}")
    
    # Railway 환경에 최적화된 데이터베이스 연결 설정
    if IS_RAILWAY:
        # Railway 환경: 안정적인 연결 설정
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,           # 연결 전 ping 테스트
            'pool_recycle': 300,             # 5분마다 연결 재생성
            'pool_size': 5,                  # 연결 풀 크기
            'max_overflow': 10,              # 추가 연결 허용
            'pool_timeout': 30,              # 연결 대기 시간
            'connect_args': {
                'connect_timeout': 60,       # MySQL 연결 타임아웃
                'read_timeout': 60,          # 읽기 타임아웃
                'write_timeout': 60,         # 쓰기 타임아웃
                'charset': 'utf8mb4',        # UTF8 문자셋
                'autocommit': True           # 자동 커밋
            }
        }
    else:
        # 로컬 환경: 기본 설정
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'pool_size': 1,
            'max_overflow': 0
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

    # Kakao 지도 환경변수 키이름
    KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY")

    KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

    # 세션 저장 방식
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")

    # 업로드 설정
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
