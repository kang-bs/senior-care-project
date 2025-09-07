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
from routes.map import map_bp
app = Flask(__name__)
app.config.from_object(Config)

Session(app)
db.init_app(app)

# Railway 환경에서는 데이터베이스 초기화를 지연시킴
print("🚀 애플리케이션이 시작되었습니다. 데이터베이스는 첫 요청 시 초기화됩니다.")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.home"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 데이터베이스 초기화 상태 추적
db_initialized = False

def ensure_db_initialized():
    global db_initialized
    if not db_initialized:
        try:
            # 데이터베이스 연결 테스트
            with app.app_context():
                # 간단한 쿼리로 연결 테스트
                db.engine.execute('SELECT 1')
                # 테이블 생성 (이미 존재하면 무시됨)
                db.create_all()
                db_initialized = True
                print("✅ 데이터베이스 연결 및 테이블 초기화 완료")
        except Exception as e:
            print(f"⚠️ 데이터베이스 초기화 오류: {e}")
            # Railway 환경에서는 재시도
            import time
            time.sleep(2)
            try:
                with app.app_context():
                    db.create_all()
                    db_initialized = True
                    print("✅ 데이터베이스 재시도 성공")
            except Exception as retry_error:
                print(f"❌ 데이터베이스 재시도 실패: {retry_error}")

# 에러 핸들러 추가
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    print(f"500 에러 발생: {error}")
    return "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.", 500

@app.before_request
def before_request():
    """각 요청 전에 데이터베이스 연결 확인"""
    ensure_db_initialized()

# 루트 라우트 - 스플래시 페이지
@app.route('/')
def splash():
    return render_template('splash.html')

# Railway 데이터베이스 마이그레이션 엔드포인트
@app.route('/migrate-db')
def migrate_database():
    """Railway 환경에서 데이터베이스 마이그레이션 실행"""
    try:
        # job_post 테이블에 latitude, longitude 컬럼 추가
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        # 컬럼 존재 여부 확인
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'job_post' 
            AND COLUMN_NAME IN ('latitude', 'longitude')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        results = []
        
        # latitude 컬럼 추가
        if 'latitude' not in existing_columns:
            cursor.execute("ALTER TABLE job_post ADD COLUMN latitude FLOAT NULL")
            results.append("✅ latitude 컬럼 추가 완료")
        else:
            results.append("ℹ️ latitude 컬럼이 이미 존재합니다")
        
        # longitude 컬럼 추가
        if 'longitude' not in existing_columns:
            cursor.execute("ALTER TABLE job_post ADD COLUMN longitude FLOAT NULL")
            results.append("✅ longitude 컬럼 추가 완료")
        else:
            results.append("ℹ️ longitude 컬럼이 이미 존재합니다")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return f"<h1>데이터베이스 마이그레이션 완료</h1><ul>{''.join([f'<li>{r}</li>' for r in results])}</ul>"
        
    except Exception as e:
        return f"<h1>마이그레이션 실패</h1><p>에러: {str(e)}</p>"

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

app.register_blueprint(map_bp)


# 초기 DB 설정


if __name__ == '__main__':
    # 로컬 개발 환경에서 데이터베이스 연결 테스트
    app.run(port=5002, debug=True)
