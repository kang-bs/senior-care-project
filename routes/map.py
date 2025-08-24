from flask import Blueprint, render_template, current_app
from flask_login import login_required

map_bp = Blueprint("map", __name__)

@map_bp.route("/map")
@login_required
def show_map():
    kakao_key = current_app.config.get("KAKAO_MAP_API_KEY")
    return render_template("map.html", kakao_key=kakao_key)