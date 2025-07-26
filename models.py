from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 기본 정보
    name = db.Column(db.String(100), nullable=True)
    nickname = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=True)         # 'male', 'female' 등
    birth_date = db.Column(db.Date, nullable=True)
    sido = db.Column(db.String(30))
    sigungu = db.Column(db.String(30))
    dong = db.Column(db.String(40))

    # 일반 로그인용
    username = db.Column(db.String(50), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)       # 비밀번호는 해시 저장

    # 사용자 유형: 0 - 일반, 1 - 기업, 2 - 관리자
    user_type = db.Column(db.Integer, default=0)

    # 소셜 로그인 정보
    social_type = db.Column(db.String(20), nullable=True)     # 'google', 'kakao', 'naver'
    social_id = db.Column(db.String(255), nullable=True)

    # 가입일
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 유니크 제약: 동일 소셜 타입과 ID는 중복 불가
    __table_args__ = (
        db.UniqueConstraint('social_type', 'social_id', name='uq_social_login'),
    )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User id={self.id} type={self.user_type} username={self.username}>"
