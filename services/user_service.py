from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    @staticmethod
    def create_user(user_data):
        """새 사용자 생성"""
        if 'password' in user_data:
            user_data['password'] = generate_password_hash(user_data['password'])
        
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_id(user_id):
        """ID로 사용자 조회"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_username(username):
        """사용자명으로 사용자 조회"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_social_login(social_type, social_id):
        """소셜 로그인 정보로 사용자 조회"""
        return User.query.filter_by(
            social_type=social_type, 
            social_id=social_id
        ).first()
    
    @staticmethod
    def update_user(user_id, user_data):
        """사용자 정보 수정"""
        user = User.query.get_or_404(user_id)
        
        if 'password' in user_data:
            user_data['password'] = generate_password_hash(user_data['password'])
        
        for key, value in user_data.items():
            setattr(user, key, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def verify_password(user, password):
        """비밀번호 확인"""
        if not user or not user.password:
            return False
        return check_password_hash(user.password, password)
    
    @staticmethod
    def delete_user(user_id):
        """사용자 삭제"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return True