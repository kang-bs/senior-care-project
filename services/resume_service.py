from models import db, Resume, Certificate
from utils.files_handler import upload_file, delete_file
from sqlalchemy.orm import selectinload

class ResumeService:
    @staticmethod
    def create_resume(user_id, resume_data, certificate_names, certificate_images):
        # ... (이전과 동일, 수정 없음)
        if Resume.query.filter_by(user_id=user_id).first():
            return None
        resume = Resume(user_id=user_id)
        db.session.add(resume)
        for key, value in resume_data.items():
            if hasattr(resume, key):
                setattr(resume, key, value)
        if certificate_names and certificate_images:
            for name, image_file in zip(certificate_names, certificate_images):
                if name.strip() and image_file and image_file.filename:
                    image_url = upload_file(file=image_file, sub_path='certificates')
                    if image_url:
                        new_cert = Certificate(name=name.strip(), image_url=image_url, resume=resume)
                        db.session.add(new_cert)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"이력서 생성 중 오류 발생: {e}")
            return None
        return resume

    @staticmethod
    def update_resume(user_id, resume_data, certificate_names, certificate_images):
        """
        기존 이력서를 수정합니다. (자격증 삭제 로직은 별도 API로 분리됨)
        """
        resume = Resume.query.options(selectinload(Resume.certificates)).filter_by(user_id=user_id).first()
        if not resume:
            return None
        for key, value in resume_data.items():
            if hasattr(resume, key):
                setattr(resume, key, value)
        if certificate_names and certificate_images:
            for name, image_file in zip(certificate_names, certificate_images):
                if name.strip() and image_file and image_file.filename:
                    image_url = upload_file(file=image_file, sub_path='certificates')
                    if image_url:
                        new_cert = Certificate(name=name.strip(), image_url=image_url, resume=resume)
                        db.session.add(new_cert)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"이력서 업데이트 중 오류 발생: {e}")
            return None
        return resume

    @staticmethod
    def delete_certificate(user_id, cert_id):
        """
        사용자 ID와 자격증 ID를 받아 해당 자격증을 안전하게 삭제합니다.
        """
        cert_to_delete = Certificate.query.get(cert_id)
        if cert_to_delete and cert_to_delete.resume and cert_to_delete.resume.user_id == user_id:
            try:
                s3_delete_successful = delete_file(cert_to_delete.image_url)
                if not s3_delete_successful:
                    print(f"S3 파일 삭제 실패로 DB 작업을 중단합니다: {cert_to_delete.image_url}")
                    return False
                db.session.delete(cert_to_delete)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"자격증 DB 삭제 중 오류 발생: {e}")
                return False
        return False

    @staticmethod
    def get_resume_by_user(user_id):
        return Resume.query.options(selectinload(Resume.certificates)).filter_by(user_id=user_id).first()

    @staticmethod
    def get_public_resume_by_user(user_id):
        return Resume.query.options(selectinload(Resume.certificates)).filter_by(user_id=user_id, is_public=True).first()
