from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from flask_dance.contrib.google import google
from models import db, User

# 인증 관련 라우트를 담당하는 블루프린트 생성
auth_bp = Blueprint("auth", __name__)

# 홈 화면 렌더링
@auth_bp.route("/")
def home():
    return render_template("home.html")

# Google OAuth 로그인 후 콜백 처리
@auth_bp.route("/google_login_callback")
def google_login_callback():
    # 인증되지 않았으면 Google 로그인 페이지로 리다이렉트
    if not google.authorized:
        return redirect(url_for("google.login"))

    # 사용자 정보 요청
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Google login failed", 400

    # 사용자 정보 파싱
    info = resp.json()
    social_id = info["id"]
    email = info.get("email")
    name = info.get("name")

    # 기존 사용자인지 확인하고 없으면 새로 등록
    user = User.query.filter_by(social_type="google", social_id=social_id).first()
    if not user:
        user = User(
            name=name,
            nickname=name or email,
            social_type="google",
            social_id=social_id
        )
        db.session.add(user)
        db.session.commit()

    # 로그인 처리 후 프로필 페이지로 이동
    login_user(user)
    return redirect(url_for("auth.profile"))

# 로그인한 사용자의 프로필 페이지
@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# 로그아웃 처리
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.home"))
