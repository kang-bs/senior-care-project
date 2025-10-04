from flask import Blueprint, render_template, request, redirect, url_for, flash,  jsonify
from flask_login import login_required, current_user
from services.resume_service import ResumeService
from models import Category, WorkType, Strength
from datetime import time

resumes_bp = Blueprint("resumes", __name__)


# "내 이력서" 페이지: 이력서가 있으면 보여주고, 없으면 작성 페이지로 이동
@resumes_bp.route("/my-resume")
@login_required
def my_resume():
    """
    사용자의 이력서가 있으면 보여주고, 없으면 작성 페이지로 안내합니다.
    """
    resume = ResumeService.get_resume_by_user(current_user.id)
    if resume:
        # 이력서가 존재하면, 이력서 조회 전용 템플릿을 렌더링
        return render_template("resume/my_resume.html", resume=resume)
    else:
        # 이력서가 없으면, 작성 페이지로 리다이렉트
        return redirect(url_for('resumes.create_resume'))


# 1. 이력서 작성 페이지
@resumes_bp.route("/resume/create", methods=["GET", "POST"])
@login_required
def create_resume():
    """
    새로운 이력서를 작성하는 페이지.
    """
    # 이미 이력서가 있다면 수정 페이지로 강제 이동
    if ResumeService.get_resume_by_user(current_user.id):
        flash("이미 작성된 이력서가 있습니다. 수정 페이지로 이동합니다.", "info")
        return redirect(url_for('resumes.edit_resume'))

    if request.method == "POST":
        # 시간 파싱을 위한 헬퍼 함수
        def parse_time(time_str):
            if not time_str: return None
            try:
                hour, minute = map(int, time_str.split(':'))
                return time(hour, minute)
            except ValueError:
                return None

        # 폼 데이터 수집
        resume_data = {
            'is_public': 'is_public' in request.form,
            'desired_categories': ",".join(request.form.getlist('categories')),
            'desired_work_type': request.form.get('desired_work_type'),
            'work_monday': 'work_monday' in request.form,
            'work_tuesday': 'work_tuesday' in request.form,
            'work_wednesday': 'work_wednesday' in request.form,
            'work_thursday': 'work_thursday' in request.form,
            'work_friday': 'work_friday' in request.form,
            'work_saturday': 'work_saturday' in request.form,
            'work_sunday': 'work_sunday' in request.form,
            'is_time_negotiable': 'is_time_negotiable' in request.form,
            'desired_start_time': parse_time(request.form.get('start_time')),
            'desired_end_time': parse_time(request.form.get('end_time')),
            'experience': request.form.get('experience'),
            'self_introduction': request.form.get('self_introduction'),
            'strengths': ",".join(request.form.getlist('strengths')),
            'commute_time': request.form.get('commute_time', type=int),
            'walkable_minutes': request.form.get('walkable_minutes', type=int),
            'physical_notes': request.form.get('physical_notes'),
        }
        certificate_names = request.form.getlist('certificate_names')
        certificate_images = request.files.getlist('certificate_images')

        ResumeService.create_resume(
            user_id=current_user.id,
            resume_data=resume_data,
            certificate_names=certificate_names,
            certificate_images=certificate_images
        )
        flash("이력서가 성공적으로 작성되었습니다.", "success")
        return redirect(url_for('resumes.my_resume'))

    # GET 요청: 빈 폼 템플릿을 렌더링
    return render_template(
        "resume/edit_resume.html",  # 작성과 수정이 같은 템플릿 사용
        resume=None,  # 작성 시에는 데이터가 없으므로 None 전달
        all_categories=list(Category),
        all_work_types=list(WorkType),
        all_strengths=list(Strength)
    )


# 2. 이력서 수정 페이지
@resumes_bp.route("/resume/edit", methods=["GET", "POST"])
@login_required
def edit_resume():
    """
    기존 이력서를 수정하는 페이지.
    """
    resume = ResumeService.get_resume_by_user(current_user.id)
    if not resume:
        # 수정할 이력서가 없으면 작성 페이지로 보냄
        flash("작성된 이력서가 없습니다. 먼저 이력서를 작성해주세요.", "info")
        return redirect(url_for('resumes.create_resume'))

    if request.method == "POST":
        # 시간 파싱을 위한 헬퍼 함수
        def parse_time(time_str):
            if not time_str: return None
            try:
                hour, minute = map(int, time_str.split(':'))
                return time(hour, minute)
            except ValueError:
                return None

        # 폼 데이터 수집 (작성 페이지와 동일)
        resume_data = {
            'is_public': 'is_public' in request.form,
            'desired_categories': ",".join(request.form.getlist('categories')),
            'desired_work_type': request.form.get('desired_work_type'),
            'work_monday': 'work_monday' in request.form,
            'work_tuesday': 'work_tuesday' in request.form,
            'work_wednesday': 'work_wednesday' in request.form,
            'work_thursday': 'work_thursday' in request.form,
            'work_friday': 'work_friday' in request.form,
            'work_saturday': 'work_saturday' in request.form,
            'work_sunday': 'work_sunday' in request.form,
            'is_time_negotiable': 'is_time_negotiable' in request.form,
            'desired_start_time': parse_time(request.form.get('start_time')),
            'desired_end_time': parse_time(request.form.get('end_time')),
            'experience': request.form.get('experience'),
            'self_introduction': request.form.get('self_introduction'),
            'strengths': ",".join(request.form.getlist('strengths')),
            'commute_time': request.form.get('commute_time', type=int),
            'walkable_minutes': request.form.get('walkable_minutes', type=int),
            'physical_notes': request.form.get('physical_notes'),
        }
        certificate_names = request.form.getlist('certificate_names')
        certificate_images = request.files.getlist('certificate_images')



        ResumeService.update_resume(
            user_id=current_user.id,
            resume_data=resume_data,
            certificate_names=certificate_names,
            certificate_images=certificate_images,
        )
        flash("이력서가 성공적으로 수정되었습니다.", "success")
        return redirect(url_for('resumes.my_resume'))

    # GET 요청: 데이터가 채워진 폼 템플릿을 렌더링
    return render_template(
        "resume/edit_resume.html",
        resume=resume,  # 수정 시에는 데이터가 있는 resume 객체 전달
        all_categories=list(Category),
        all_work_types=list(WorkType),
        all_strengths=list(Strength)
    )


# 3. 다른 사용자의 공개 이력서 조회 페이지
@resumes_bp.route("/resumes/<int:user_id>")
@login_required
def view_resume(user_id):
    """
    기업 회원이 특정 사용자의 공개 이력서를 조회하는 페이지.
    """
    resume = ResumeService.get_public_resume_by_user(user_id)
    if not resume:
        flash("비공개 이력서이거나 존재하지 않는 이력서입니다.", "error")
        return redirect(url_for('main.home'))  # 적절한 홈 URL로 변경 필요
    return render_template("resume/view_resume.html", resume=resume)

@resumes_bp.route("/resume/certificate/delete/<int:cert_id>", methods=['DELETE'])
@login_required
def delete_certificate(cert_id):
    """
    특정 자격증 하나를 실시간으로 삭제하는 API 엔드포인트.
    """
    success = ResumeService.delete_certificate(
        user_id=current_user.id,
        cert_id=cert_id
    )
    if success:
        return jsonify({'success': True, 'message': '자격증이 삭제되었습니다.'})
    else:
        return jsonify({'success': False, 'message': '삭제에 실패했거나 권한이 없습니다.'}), 403