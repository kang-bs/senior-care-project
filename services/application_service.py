"""
지원 서비스 모듈
===============

공고 지원 관련 비즈니스 로직을 처리합니다.

주요 기능:
- 공고 지원 처리
- 지원 상태 관리
- 지원 목록 조회
- 채팅방 자동 생성

작성자: [팀명]
최종 수정일: 2025-01-09
"""

from models import db, JobApplication, JobPost, User
from services.chat_service import ChatService
from datetime import datetime

class ApplicationService:
    
    @staticmethod
    def apply_to_job(user_id, job_id, message=None):
        """
        공고에 지원하기
        
        Args:
            user_id: 지원자 ID
            job_id: 공고 ID
            message: 지원 메시지 (선택)
            
        Returns:
            dict: 결과 정보
        """
        # 공고 존재 확인
        job = JobPost.query.get_or_404(job_id)
        
        # 자신의 공고에는 지원할 수 없음
        if job.author_id == user_id:
            return {
                'success': False,
                'message': '본인이 작성한 공고에는 지원할 수 없습니다.'
            }
        
        # 이미 지원했는지 확인
        existing_application = JobApplication.query.filter_by(
            user_id=user_id,
            job_id=job_id
        ).first()
        
        if existing_application:
            return {
                'success': False,
                'message': '이미 지원한 공고입니다.'
            }
        
        try:
            # 지원 정보 생성
            application = JobApplication(
                user_id=user_id,
                job_id=job_id,
                message=message,
                status='pending'
            )
            
            db.session.add(application)
            
            # 공고의 지원 횟수 증가
            job.application_count += 1
            
            db.session.commit()
            
            # 채팅방 자동 생성
            chat_room = ChatService.create_or_get_chat_room(
                job_id=job_id,
                applicant_id=user_id,
                employer_id=job.author_id
            )
            
            return {
                'success': True,
                'message': '지원이 완료되었습니다. 채팅방이 생성되었습니다.',
                'application_id': application.id,
                'chat_room_id': chat_room.id
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': '지원 처리 중 오류가 발생했습니다.'
            }
    
    @staticmethod
    def get_user_applications(user_id):
        """
        사용자의 지원 목록 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            list: 지원 목록
        """
        applications = JobApplication.query.filter_by(user_id=user_id)\
                                         .order_by(JobApplication.created_at.desc())\
                                         .all()
        
        return applications
    
    @staticmethod
    def get_job_applications(job_id, employer_id):
        """
        공고에 대한 지원자 목록 조회 (고용주용)
        
        Args:
            job_id: 공고 ID
            employer_id: 고용주 ID
            
        Returns:
            list: 지원자 목록
        """
        # 공고 소유자 확인
        job = JobPost.query.filter_by(id=job_id, author_id=employer_id).first_or_404()
        
        applications = JobApplication.query.filter_by(job_id=job_id)\
                                         .order_by(JobApplication.created_at.desc())\
                                         .all()
        
        return applications
    
    @staticmethod
    def update_application_status(application_id, employer_id, status):
        """
        지원 상태 업데이트 (고용주용)
        
        Args:
            application_id: 지원 ID
            employer_id: 고용주 ID
            status: 새로운 상태 ('accepted', 'rejected')
            
        Returns:
            dict: 결과 정보
        """
        application = JobApplication.query.get_or_404(application_id)
        
        # 공고 소유자 확인
        if application.job.author_id != employer_id:
            return {
                'success': False,
                'message': '권한이 없습니다.'
            }
        
        if status not in ['accepted', 'rejected']:
            return {
                'success': False,
                'message': '잘못된 상태값입니다.'
            }
        
        try:
            application.status = status
            application.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            status_text = '승인' if status == 'accepted' else '거절'
            
            return {
                'success': True,
                'message': f'지원이 {status_text}되었습니다.'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': '상태 업데이트 중 오류가 발생했습니다.'
            }
    
    @staticmethod
    def check_application_status(user_id, job_id):
        """
        지원 상태 확인
        
        Args:
            user_id: 사용자 ID
            job_id: 공고 ID
            
        Returns:
            dict: 지원 상태 정보
        """
        application = JobApplication.query.filter_by(
            user_id=user_id,
            job_id=job_id
        ).first()
        
        if not application:
            return {
                'applied': False,
                'status': None
            }
        
        return {
            'applied': True,
            'status': application.status,
            'application_id': application.id,
            'applied_at': application.created_at
        }