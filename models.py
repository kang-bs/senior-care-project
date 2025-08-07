from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    # 사용자 고유 ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 기본 정보
    name = db.Column(db.String(100), nullable=True)           # 이름
    nickname = db.Column(db.String(50), nullable=False)       # 닉네임
    gender = db.Column(db.String(10), nullable=True)          # 성별 (male, female 등)
    birth_date = db.Column(db.Date, nullable=True)            # 생년월일
    sido = db.Column(db.String(30), nullable=True)            # 시/도
    sigungu = db.Column(db.String(30), nullable=True)         # 시/군/구
    dong = db.Column(db.String(40), nullable=True)            # 동

    # 일반 로그인용
    username = db.Column(db.String(50), unique=True, nullable=True)  # 일반 로그인용 ID
    password = db.Column(db.String(255), nullable=True)       # 비밀번호 (해시로 저장)

    # 사용자 유형: 0 - 일반, 1 - 기업, 2 - 관리자
    user_type = db.Column(db.Integer, default=0)              # 사용자 유형

    # 소셜 로그인 정보
    social_type = db.Column(db.String(20), nullable=True)     # 소셜 로그인 타입 (google, kakao 등)
    social_id = db.Column(db.String(255), nullable=True)      # 소셜 로그인 ID

    # 추가 정보
    email = db.Column(db.String(255), nullable=True)          # 이메일
    phone = db.Column(db.String(20), nullable=True)           # 전화번호
    trust_score = db.Column(db.Float, default=0.0)            # 신뢰점수
    profile_image = db.Column(db.String(255), nullable=True)  # 프로필 사진

    # 시간 정보
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 가입일
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 수정일

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

class JobPost(db.Model):
    __tablename__ = 'job_post'

    # 공고 고유 ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 기본 공고 정보
    title = db.Column(db.String(200), nullable=False)          # 공고 제목
    company = db.Column(db.String(100), nullable=False)        # 회사 이름
    description = db.Column(db.Text, nullable=False)           # 공고 내용

    # 근무 조건
    work_start_time = db.Column(db.Time, nullable=True)        # 근무 시작 시간
    work_end_time = db.Column(db.Time, nullable=True)          # 근무 종료 시간
    recruitment_count = db.Column(db.Integer, nullable=True)   # 모집 인원
    region = db.Column(db.String(100), nullable=True)          # 근무 지역 (맵 연동)
    salary = db.Column(db.String(100), nullable=True)          # 급여

    # 근무 요일 (월화수목금토일)
    work_monday = db.Column(db.Boolean, default=False)         # 월요일
    work_tuesday = db.Column(db.Boolean, default=False)        # 화요일
    work_wednesday = db.Column(db.Boolean, default=False)      # 수요일
    work_thursday = db.Column(db.Boolean, default=False)       # 목요일
    work_friday = db.Column(db.Boolean, default=False)         # 금요일
    work_saturday = db.Column(db.Boolean, default=False)       # 토요일
    work_sunday = db.Column(db.Boolean, default=False)         # 일요일

    # 모집 형태 및 기간
    recruitment_type = db.Column(db.String(50), nullable=True) # 모집 형태
    work_period = db.Column(db.String(20), nullable=True)      # 기간 (1개월, 3개월, 6개월, 1년 이상)

    # 연락처
    contact_phone = db.Column(db.String(20), nullable=True)    # 연락처 전화번호

    # 통계 정보
    application_count = db.Column(db.Integer, default=0)       # 지원횟수
    view_count = db.Column(db.Integer, default=0)              # 조회수
    bookmark_count = db.Column(db.Integer, default=0)          # 찜 횟수

    # 작성자 및 시간 정보
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 공고 작성일
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 작성자 (User ID)

    author = db.relationship('User', backref=db.backref('job_posts', lazy=True))

    def __repr__(self):
        return f"<JobPost id={self.id} title={self.title} company={self.company}>"