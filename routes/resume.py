from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, SeniorResume

senior_resume_bp = Blueprint('senior_resume', __name__)


@senior_resume_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    resume = SeniorResume.query.filter_by(user_id=current_user.id).first()
    if resume:
        # 이미 이력서가 있으면 상세보기 페이지로 이동
        return redirect(url_for('senior_resume.view'))

    if request.method == 'POST':
        work_monday = bool(request.form.get('work_monday'))
        work_tuesday = bool(request.form.get('work_tuesday'))
        work_wednesday = bool(request.form.get('work_wednesday'))
        work_thursday = bool(request.form.get('work_thursday'))
        work_friday = bool(request.form.get('work_friday'))
        work_saturday = bool(request.form.get('work_saturday'))
        work_sunday = bool(request.form.get('work_sunday'))

        work_time = request.form.getlist('work_time')
        work_time_str = ','.join(work_time) if work_time else ''

        interested_jobs = request.form.getlist('interested_jobs')
        interested_jobs_str = ','.join(interested_jobs) if interested_jobs else ''

        work_time_free_text = request.form.get('work_time_free_text')
        interested_jobs_custom = request.form.get('interested_jobs_custom')
        career_status = bool(request.form.get('career_status'))
        motivation = request.form.get('motivation')
        extra_requests = request.form.get('extra_requests')

        new_resume = SeniorResume(
            user_id=current_user.id,
            work_monday=work_monday,
            work_tuesday=work_tuesday,
            work_wednesday=work_wednesday,
            work_thursday=work_thursday,
            work_friday=work_friday,
            work_saturday=work_saturday,
            work_sunday=work_sunday,
            work_time=work_time_str,
            work_time_free_text=work_time_free_text,
            interested_jobs=interested_jobs_str,
            interested_jobs_custom=interested_jobs_custom,
            career_status=career_status,
            motivation=motivation,
            extra_requests=extra_requests
        )
        db.session.add(new_resume)
        db.session.commit()
        flash('이력서 등록이 완료되었습니다.', 'success')
        return redirect(url_for('senior_resume.view'))

    return render_template('resume/resume_register.html')


@senior_resume_bp.route('/view')
@login_required
def view():
    resume = SeniorResume.query.filter_by(user_id=current_user.id).first()
    if not resume:
        flash('등록된 이력서가 없습니다. 등록 페이지로 이동합니다.', 'warning')
        return redirect(url_for('senior_resume.register'))
    return render_template('resume/resume_view.html', resume=resume)


@senior_resume_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    resume = SeniorResume.query.filter_by(user_id=current_user.id).first()
    if not resume:
        flash('수정할 이력서가 없습니다.', 'warning')
        return redirect(url_for('senior_resume.register'))

    if request.method == 'POST':
        resume.work_monday = bool(request.form.get('work_monday'))
        resume.work_tuesday = bool(request.form.get('work_tuesday'))
        resume.work_wednesday = bool(request.form.get('work_wednesday'))
        resume.work_thursday = bool(request.form.get('work_thursday'))
        resume.work_friday = bool(request.form.get('work_friday'))
        resume.work_saturday = bool(request.form.get('work_saturday'))
        resume.work_sunday = bool(request.form.get('work_sunday'))

        work_time = request.form.getlist('work_time')
        resume.work_time = ','.join(work_time) if work_time else ''

        resume.work_time_free_text = request.form.get('work_time_free_text')

        interested_jobs = request.form.getlist('interested_jobs')
        resume.interested_jobs = ','.join(interested_jobs) if interested_jobs else ''

        resume.interested_jobs_custom = request.form.get('interested_jobs_custom')
        resume.career_status = bool(request.form.get('career_status'))
        resume.motivation = request.form.get('motivation')
        resume.extra_requests = request.form.get('extra_requests')

        db.session.commit()
        flash('이력서가 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('senior_resume.view'))

    # GET 요청 시 기존 이력서 데이터 전달
    return render_template('resume/resume_edit.html', resume=resume)