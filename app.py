from flask import Flask, render_template
from config import Config
from models import db, User
from flask_login import LoginManager
from flask_session import Session
from routes.auth import auth_bp
from routes.google_oauth import google_bp
from routes.naver_oauth import naver_bp
from routes.kakao_oauth import kakao_bp
from routes.areas import areas_bp
from routes.jobs import jobs_bp
from routes.chat import chat_bp
from routes.company import company_bp
from routes.resume import senior_resume_bp
from utils.helpers import format_date, format_datetime, format_salary, get_work_days, calculate_time_ago
from cli import register_cli  # ⬅ cli.py에서 만든 함수 import
from routes.admin.admin import admin_bp
app = Flask(__name__)
app.config.from_object(Config)

Session(app)
db.init_app(app)

# Railway 환경에서 데이터베이스 초기화
def init_database():
    try:
        with app.app_context():
            # 데이터베이스 연결 테스트
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()
            
            if test_value and test_value[0] == 1:
                print("✅ 데이터베이스 연결 성공!")
                
                # 테이블 존재 여부 확인
                try:
                    # User 테이블이 존재하는지 확인
                    db.session.execute(text("SELECT COUNT(*) FROM users LIMIT 1"))
                    print("✅ 데이터베이스 테이블이 이미 존재합니다.")
                except Exception as table_error:
                    print(f"⚠️ 테이블이 존재하지 않습니다: {table_error}")
                    print("🔄 데이터베이스 테이블을 생성합니다...")
                    
                    # 테이블 생성
                    db.create_all()
                    print("✅ 데이터베이스 테이블 생성 완료!")
                
                return True
            else:
                print("❌ 데이터베이스 연결 테스트 실패")
                return False
                
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        print(f"데이터베이스 URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
        return False

# Railway 환경에서 애플리케이션 시작 시 데이터베이스 초기화
try:
    with app.app_context():
        init_database()
except Exception as e:
    print(f"⚠️ 데이터베이스 초기화 중 오류 발생: {e}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.home"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 루트 라우트 - 스플래시 페이지
@app.route('/')
def splash():
    return render_template('splash.html')

# 템플릿 필터 등록
app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.filters['format_salary'] = format_salary
app.jinja_env.filters['get_work_days'] = get_work_days
app.jinja_env.filters['time_ago'] = calculate_time_ago

# 블루프린트 등록
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(naver_bp)
app.register_blueprint(kakao_bp, url_prefix="/login")
app.register_blueprint(areas_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(company_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(senior_resume_bp,url_prefix='/resume')

# 초기 DB 설정


if __name__ == '__main__':
    # 로컬 개발 환경에서 데이터베이스 연결 테스트
    init_database()
    app.run(port=5002, debug=True)
