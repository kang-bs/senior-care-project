from flask import render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import community_bp
from models import db, JobPost
from .utils import calculate_age


@community_bp.route('/jobs')
def job_list():
    q = request.args.get('q')
    region = request.args.get('region')
    senior_only = request.args.get('senior_only') == 'true'
    age = request.args.get('age', type=int)

    query = JobPost.query.order_by(JobPost.created_at.desc())

    if q:
        query = query.filter(
            (JobPost.title.ilike(f'%{q}%')) | (JobPost.description.ilike(f'%{q}%'))
        )
    if region:
        query = query.filter(JobPost.region == region)
    if senior_only:
        query = query.filter(JobPost.is_senior_friendly.is_(True))
    if age is not None:
        query = query.filter(
            (JobPost.preferred_age_min.is_(None) | (JobPost.preferred_age_min <= age)) &
            (JobPost.preferred_age_max.is_(None) | (JobPost.preferred_age_max >= age))
        )

    jobs = query.all()
    return render_template('community/jobs/list.html', jobs=jobs)


@community_bp.route('/jobs/new', methods=['GET', 'POST'])
@login_required
def job_create():
    if current_user.user_type != 1:
        return "접근 권한이 없습니다. (기업회원만 작성 가능)", 403

    if request.method == 'POST':
        new_post = JobPost(
            title=request.form.get('title'),
            company=request.form.get('company'),
            description=request.form.get('description'),
            preferred_age_min=request.form.get('preferred_age_min') or None,
            preferred_age_max=request.form.get('preferred_age_max') or None,
            region=request.form.get('region'),
            is_senior_friendly=request.form.get('is_senior_friendly') == 'on',
            work_hours=request.form.get('work_hours'),
            contact_phone=request.form.get('contact_phone'),
            author_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('community.job_list'))

    return render_template('community/jobs/form.html')


@community_bp.route('/jobs/<int:job_id>')
def job_detail(job_id):
    job = JobPost.query.get_or_404(job_id)

    user_age = None
    if current_user.is_authenticated and current_user.birth_date:
        user_age = calculate_age(current_user.birth_date)

    return render_template('community/jobs/detail.html', job=job, user_age=user_age)


@community_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def job_delete(job_id):
    job = JobPost.query.get_or_404(job_id)

    if current_user.id != job.author_id and current_user.user_type != 2:
        abort(403)

    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('community.job_list'))


@community_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def job_edit(job_id):
    job = JobPost.query.get_or_404(job_id)

    if current_user.id != job.author_id:
        abort(403)

    if request.method == 'POST':
        job.title = request.form.get('title')
        job.company = request.form.get('company')
        job.description = request.form.get('description')
        job.preferred_age_min = request.form.get('preferred_age_min') or None
        job.preferred_age_max = request.form.get('preferred_age_max') or None
        job.region = request.form.get('region')
        job.work_hours = request.form.get('work_hours')
        job.contact_phone = request.form.get('contact_phone')
        job.is_senior_friendly = request.form.get('is_senior_friendly') == 'on'

        db.session.commit()
        return redirect(url_for('community.job_detail', job_id=job.id))

    return render_template('community/jobs/form.html', job=job, is_edit=True)
