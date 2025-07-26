import json
from flask import Blueprint, jsonify

areas_bp = Blueprint("areas", __name__)

with open("./data/sido.json", encoding="utf-8") as f:
    sido_list = json.load(f)
with open("./data/sigungu.json", encoding="utf-8") as f:
    sigungu_list = json.load(f)
with open("./data/dong.json", encoding="utf-8") as f:
    dong_list = json.load(f)


def last_token(s):
    return s.split()[-1] if s else s
def sigungu_token(s):
    return s.split()[-1] if s else s
def sido_token(s):
    return s  # 시도 name 완전값

@areas_bp.route("/api/areas/sido")
def get_sido():
    return jsonify([{"name": sido_token(s["name"])} for s in sido_list])

@areas_bp.route("/api/areas/sigungu_by_name/<sido_name>")
def get_sigungu_by_name(sido_name):
    sido_code = next((s['code'] for s in sido_list if sido_token(s["name"]) == sido_name), None)
    if not sido_code:
        return jsonify([])
    return jsonify([
        {"name": sigungu_token(s["name"])}
        for s in sigungu_list if s["sido_code"] == sido_code
    ])

@areas_bp.route("/api/areas/dong_by_name/<sido_name>/<sigungu_name>")
def get_dong_by_name(sido_name, sigungu_name):
    sido_code = next((s['code'] for s in sido_list if sido_token(s["name"]) == sido_name), None)
    if not sido_code:
        return jsonify([])
    sigungu_code = next(
        (
            s['code'] for s in sigungu_list
            if s['sido_code'] == sido_code and sigungu_token(s["name"]) == sigungu_name
        ),
        None
    )
    if not sigungu_code:
        return jsonify([])
    return jsonify([
        {"name": last_token(d["name"])}
        for d in dong_list if d["sigungu_code"] == sigungu_code
    ])