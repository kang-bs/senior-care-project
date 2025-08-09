from flask import Flask
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
from utils.helpers import format_date, format_datetime, format_salary, get_work_days, calculate_time_ago

app = Flask(__name__)
app.config.from_object(Config)

Session(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.home"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 템플릿 필터 등록
app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.filters['format_salary'] = format_salary
app.jinja_env.filters['get_work_days'] = get_work_days
app.jinja_env.filters['time_ago'] = calculate_time_ago

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(naver_bp)
app.register_blueprint(kakao_bp, url_prefix="/login")
app.register_blueprint(areas_bp)
app.register_blueprint(jobs_bp)

# 초기 DB 설정
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5002, debug=True)
