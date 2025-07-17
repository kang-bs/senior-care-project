from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# 최초 실행 시 테이블 생성 models.py 기반 지우지 말 것!
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Flask + MySQL 연결 완료!'

if __name__ == '__main__':
    app.run(port= 5002, debug=True)
