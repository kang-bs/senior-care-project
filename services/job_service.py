from models import db, JobPost, JobBookmark, User
from sqlalchemy import desc
from flask_login import current_user

class JobService:
    @staticmethod
    def get_all_jobs(page=1, per_page=10):
        """모든 공고 조회 (페이지네이션)"""
        return JobPost.query.order_by(desc(JobPost.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_job_by_id(job_id):
        """ID로 공고 조회"""
        return JobPost.query.get_or_404(job_id)
    
    @staticmethod
    def create_job(job_data):
        """새 공고 생성"""
        job = JobPost(**job_data)
        db.session.add(job)
        db.session.commit()
        return job
    
    @staticmethod
    def update_job(job_id, job_data):
        """공고 수정"""
        job = JobPost.query.get_or_404(job_id)
        for key, value in job_data.items():
            setattr(job, key, value)
        db.session.commit()
        return job
    
    @staticmethod
    def delete_job(job_id):
        """공고 삭제"""
        job = JobPost.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return True
    
    @staticmethod
    def increment_view_count(job_id):
        """조회수 증가"""
        job = JobPost.query.get(job_id)
        if job:
            job.view_count += 1
            db.session.commit()
    
    @staticmethod
    def get_user_bookmarks(user_id):
        """사용자의 찜 목록 조회"""
        bookmarks = JobBookmark.query.filter_by(user_id=user_id).all()
        return [bookmark.job for bookmark in bookmarks]
    
    @staticmethod
    def toggle_bookmark(user_id, job_id):
        """찜하기/찜 해제 토글"""
        bookmark = JobBookmark.query.filter_by(
            user_id=user_id, job_id=job_id
        ).first()
        
        if bookmark:
            # 찜 해제
            db.session.delete(bookmark)
            job = JobPost.query.get(job_id)
            if job:
                job.bookmark_count = max(0, job.bookmark_count - 1)
            db.session.commit()
            return False
        else:
            # 찜하기
            bookmark = JobBookmark(user_id=user_id, job_id=job_id)
            db.session.add(bookmark)
            job = JobPost.query.get(job_id)
            if job:
                job.bookmark_count += 1
            db.session.commit()
            return True
    
    @staticmethod
    def is_bookmarked(user_id, job_id):
        """찜 여부 확인"""
        if not user_id:
            return False
        return JobBookmark.query.filter_by(
            user_id=user_id, job_id=job_id
        ).first() is not None
    
    @staticmethod
    def search_jobs(query, filters=None):
        """공고 검색"""
        jobs_query = JobPost.query
        
        if query:
            jobs_query = jobs_query.filter(
                JobPost.title.contains(query) |
                JobPost.company.contains(query) |
                JobPost.description.contains(query)
            )
        
        if filters:
            if filters.get('region'):
                jobs_query = jobs_query.filter(
                    JobPost.region.contains(filters['region'])
                )
            if filters.get('recruitment_type'):
                jobs_query = jobs_query.filter(
                    JobPost.recruitment_type == filters['recruitment_type']
                )
            if filters.get('work_period'):
                jobs_query = jobs_query.filter(
                    JobPost.work_period == filters['work_period']
                )
        
        return jobs_query.order_by(desc(JobPost.created_at)).all()