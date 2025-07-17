from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from flask_session import Session
from routes.auth import auth_bp
from routes.google_oauth import google_bp
<<<<<<< HEAD
from routes.naver_oauth import naver_bp
=======
from routes.kakao_oauth import kakao_bp
>>>>>>> kakao-login

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

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(google_bp, url_prefix="/login")
<<<<<<< HEAD
app.register_blueprint(naver_bp)
=======
app.register_blueprint(kakao_bp, url_prefix="/login")
>>>>>>> kakao-login

# 초기 DB 설정
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5002, debug=True)
