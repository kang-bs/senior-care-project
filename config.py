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
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:Ckdhfma1406!@127.0.0.1:5002/senior_project")
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