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
    user_type = db.Column(db.Integer, default=0)

    is_verified = db.Column(db.Boolean, default=False)  # 관리자 승인 여부 (False=대기, True=승인)
    business_registration_file = db.Column(db.String(255), nullable=True)  # 사업자 등록증 파일 경로
    business_registration_original = db.Column(db.String(255))  # 사용자 원본 파일명

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

class JobBookmark(db.Model):
    __tablename__ = 'job_bookmark'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True))
    job = db.relationship('JobPost', backref=db.backref('bookmarks', lazy=True))
    
    # 유니크 제약: 한 사용자가 같은 공고를 중복으로 찜할 수 없음
    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='uq_user_job_bookmark'),
    )
    
    def __repr__(self):
        return f"<JobBookmark user_id={self.user_id} job_id={self.job_id}>"

class JobApplication(db.Model):
    """공고 지원 모델"""
    __tablename__ = 'job_application'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 지원자
    job_id = db.Column(db.Integer, db.ForeignKey('job_post.id'), nullable=False)  # 지원한 공고
    status = db.Column(db.String(20), default='pending')  # 지원 상태: pending, accepted, rejected
    message = db.Column(db.Text, nullable=True)  # 지원 메시지
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('User', backref=db.backref('applications', lazy=True))
    job = db.relationship('JobPost', backref=db.backref('applications', lazy=True))
    
    # 유니크 제약: 한 사용자가 같은 공고에 중복 지원 불가
    __table_args__ = (
        db.UniqueConstraint('user_id', 'job_id', name='uq_user_job_application'),
    )
    
    def __repr__(self):
        return f"<JobApplication user_id={self.user_id} job_id={self.job_id} status={self.status}>"

class ChatRoom(db.Model):
    """채팅방 모델"""
    __tablename__ = 'chat_room'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_post.id'), nullable=False)  # 관련 공고
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 지원자
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 고용주
    is_active = db.Column(db.Boolean, default=True)  # 채팅방 활성 상태
    applicant_left = db.Column(db.Boolean, default=False)  # 지원자가 나갔는지 여부
    employer_left = db.Column(db.Boolean, default=False)  # 고용주가 나갔는지 여부
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    job = db.relationship('JobPost', backref=db.backref('chat_rooms', lazy=True))
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref=db.backref('applicant_chats', lazy=True))
    employer = db.relationship('User', foreign_keys=[employer_id], backref=db.backref('employer_chats', lazy=True))
    
    # 유니크 제약: 같은 공고에 대해 같은 지원자와 고용주 간 채팅방은 하나만
    __table_args__ = (
        db.UniqueConstraint('job_id', 'applicant_id', 'employer_id', name='uq_chat_room'),
    )
    
    def __repr__(self):
        return f"<ChatRoom id={self.id} job_id={self.job_id} applicant_id={self.applicant_id} employer_id={self.employer_id}>"

class ChatMessage(db.Model):
    """채팅 메시지 모델"""
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)  # 채팅방
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 발신자
    message = db.Column(db.Text, nullable=False)  # 메시지 내용
    message_type = db.Column(db.String(20), default='text')  # 메시지 타입: text, image, file
    is_read = db.Column(db.Boolean, default=False)  # 읽음 여부
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    room = db.relationship('ChatRoom', backref=db.backref('messages', lazy=True, order_by='ChatMessage.created_at'))
    sender = db.relationship('User', backref=db.backref('sent_messages', lazy=True))
    
    def __repr__(self):
        return f"<ChatMessage id={self.id} room_id={self.room_id} sender_id={self.sender_id}>"


class SeniorResume(db.Model):
    __tablename__ = 'senior_resume'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User 테이블 FK

    # 근무 요일별 Boolean 필드
    work_monday = db.Column(db.Boolean, default=False)
    work_tuesday = db.Column(db.Boolean, default=False)
    work_wednesday = db.Column(db.Boolean, default=False)
    work_thursday = db.Column(db.Boolean, default=False)
    work_friday = db.Column(db.Boolean, default=False)
    work_saturday = db.Column(db.Boolean, default=False)
    work_sunday = db.Column(db.Boolean, default=False)

    work_time = db.Column(db.String(100))              # 예: '오전,저녁(6시 이후),시간 관계 X'
    work_time_free_text = db.Column(db.String(200))    # 시간대 자유 작성 텍스트
    interested_jobs = db.Column(db.String(100))        # 예: '공공근로/환경정비,카페/식당 보조'
    interested_jobs_custom = db.Column(db.String(100)) # 직접 입력 관심 일 텍스트
    career_status = db.Column(db.Boolean)               # True: 경력 있음, False: 신입
    motivation = db.Column(db.Text)                      # 지원 동기
    extra_requests = db.Column(db.Text)                  # 기타 요청사항

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User 관계 - user.senior_resumes로 접근 가능
    user = db.relationship('User', backref=db.backref('senior_resumes', lazy=True))

    def __repr__(self):
        return f"<SeniorResume id={self.id} user_id={self.user_id}>"