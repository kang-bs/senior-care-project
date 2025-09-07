"""
채용 공고 AI 글쓰기 도우미 라우트
===============================

채용 공고 작성을 도와주는 AI 서비스 API입니다.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from services.job_writing_assistant import job_assistant

# 블루프린트 생성
job_assistant_bp = Blueprint("job_assistant", __name__)

@job_assistant_bp.route("/job-assistant")
@login_required
def job_assistant_page():
    """
    AI 글쓰기 도우미 페이지 (기업용)
    """
    # 기업 회원만 접근 가능
    if current_user.user_type != 1:
        return "기업 회원만 이용 가능합니다.", 403
    
    return render_template("job_assistant/assistant.html")

@job_assistant_bp.route("/general-job-assistant")
@login_required
def general_job_assistant_page():
    """
    AI 글쓰기 도우미 안내 페이지
    """
    # 일반 사용자(0) 또는 기업 사용자(1) 모두 접근 가능
    if current_user.user_type not in [0, 1]:
        return f"접근 권한이 없습니다. 현재 사용자 타입: {current_user.user_type}", 403
    
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI 도우미 안내</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body text-center">
                            <h1 class="text-success mb-4">🤖 AI 도우미 안내</h1>
                            <p class="lead">AI 도우미가 공고 작성 페이지에 통합되었습니다!</p>
                            <div class="alert alert-info">
                                <h5>📝 사용 방법</h5>
                                <ol class="text-start">
                                    <li>공고 작성 페이지에서 기본 정보를 입력하세요</li>
                                    <li>"상세 설명" 위의 <strong class="text-success">AI 도우미</strong> 버튼을 클릭하세요</li>
                                    <li>팝업에서 추가 정보를 입력하고 생성하세요</li>
                                    <li>생성된 설명을 확인하고 필요시 수정하세요</li>
                                </ol>
                            </div>
                            <div class="mt-4">
                                <a href="/jobs/create" class="btn btn-success btn-lg me-3">
                                    📝 일반 공고 작성하기
                                </a>
                                <a href="/company/create" class="btn btn-primary btn-lg">
                                    🏢 기업 공고 작성하기
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@job_assistant_bp.route("/api/job-draft", methods=["POST"])
@login_required
def generate_job_draft():
    """
    채용 공고 초안 생성 API
    """
    
    # 권한 체크: 기업 회원(1) 또는 일반 회원(0) 모두 접근 가능
    if current_user.user_type not in [0, 1]:
        return jsonify({
            "success": False,
            "error": "로그인이 필요합니다."
        }), 403
    
    try:
        # 요청 데이터 파싱
        job_data = request.get_json()
        
        if not job_data:
            return jsonify({
                "success": False,
                "error": "요청 데이터가 없습니다."
            }), 400
        
        # AI 글쓰기 도우미 실행
        result = job_assistant.generate_job_description(job_data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"서버 오류: {str(e)}"
        }), 500

@job_assistant_bp.route("/api/job-validate", methods=["POST"])
@login_required
def validate_job_data():
    """
    채용 공고 데이터 검증 API
    """
    
    if current_user.user_type not in [0, 1]:
        return jsonify({
            "success": False,
            "error": "로그인이 필요합니다."
        }), 403
    
    try:
        job_data = request.get_json()
        
        validation_result = {
            "success": True,
            "issues": [],
            "suggestions": [],
            "score": 100
        }
        
        # 필수 필드 검증
        required_fields = {
            "title": "채용 제목",
            "employment_type": "고용 형태",
            "location": "근무 지역",
            "duties": "주요 업무"
        }
        
        for field, name in required_fields.items():
            if not job_data.get(field):
                validation_result["issues"].append(f"{name}이 누락되었습니다.")
                validation_result["score"] -= 20
        
        # 급여 정보 검증
        pay_info = job_data.get("pay", {})
        if not pay_info or not pay_info.get("amount"):
            validation_result["suggestions"].append("급여 정보를 명시하면 지원율이 높아집니다.")
            validation_result["score"] -= 10
        
        # 복리후생 검증
        if not job_data.get("benefits"):
            validation_result["suggestions"].append("복리후생 정보를 추가하면 매력도가 높아집니다.")
            validation_result["score"] -= 5
        
        # 시니어 친화 검증
        if not job_data.get("senior_friendly"):
            validation_result["suggestions"].append("시니어 친화 옵션을 활성화하면 더 많은 지원자를 유치할 수 있습니다.")
        
        return jsonify(validation_result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"검증 중 오류: {str(e)}"
        }), 500

@job_assistant_bp.route("/api/job-templates")
@login_required
def get_job_templates():
    """
    채용 공고 템플릿 목록 제공
    """
    
    template_type = request.args.get('type', 'company')
    
    if template_type == 'general':
        # 일반 공고용 템플릿 (더 간단하고 친근함)
        templates = {
            "cafe_service": {
                "name": "카페/음식점",
                "template": {
                    "title": "카페 서빙",
                    "employment_type": "파트타임",
                    "duties": "손님 주문받기, 음료 서빙, 간단한 정리",
                    "requirements": "친절하신 분, 깔끔하신 분",
                    "benefits": "식사 제공, 자유로운 분위기",
                    "senior_friendly": True
                }
            },
            "mart_cashier": {
                "name": "마트/편의점",
                "template": {
                    "title": "마트 계산원",
                    "employment_type": "파트타임",
                    "duties": "계산, 손님 응대, 상품 정리",
                    "requirements": "성실하신 분",
                    "benefits": "직원 할인, 교통비 지원",
                    "senior_friendly": True
                }
            },
            "cleaning": {
                "name": "청소/관리",
                "template": {
                    "title": "사무실 청소",
                    "employment_type": "파트타임",
                    "duties": "사무실 청소, 화장실 정리, 쓰레기 정리",
                    "requirements": "깔끔하고 성실하신 분",
                    "benefits": "자유로운 시간, 단순 업무",
                    "senior_friendly": True
                }
            },
            "delivery": {
                "name": "배달/운송",
                "template": {
                    "title": "음식 배달",
                    "employment_type": "알바",
                    "duties": "음식 배달, 간단한 주문 확인",
                    "requirements": "오토바이 운전 가능하신 분",
                    "benefits": "시간당 정산, 팁 별도",
                    "senior_friendly": True
                }
            }
        }
    else:
        # 기업 공고용 템플릿 (기존)
        templates = {
            "customer_service": {
                "name": "고객 서비스",
                "template": {
                    "title": "고객 상담원",
                    "employment_type": "정규직",
                    "duties": "고객 문의 응답, 상담 서비스 제공, 고객 만족도 관리",
                    "requirements": "고객 서비스 경험, 원활한 의사소통 능력",
                    "benefits": "4대보험, 퇴직금, 교육비 지원",
                    "senior_friendly": True
                }
            },
            "office_admin": {
                "name": "사무 관리",
                "template": {
                    "title": "사무 보조",
                    "employment_type": "계약직",
                    "duties": "문서 작성, 전화 응대, 일정 관리, 간단한 회계 업무",
                    "requirements": "기본적인 컴퓨터 활용 능력, 꼼꼼한 성격",
                    "benefits": "4대보험, 중식 제공, 교통비 지원",
                    "senior_friendly": True
                }
            },
            "retail": {
                "name": "판매/서비스",
                "template": {
                    "title": "매장 판매원",
                    "employment_type": "파트타임",
                    "duties": "상품 판매, 고객 안내, 매장 정리, 계산 업무",
                    "requirements": "서비스 마인드, 친절한 성격",
                    "benefits": "직원 할인, 유니폼 제공, 상여금",
                    "senior_friendly": True
                }
            },
            "security": {
                "name": "보안/관리",
                "template": {
                    "title": "시설 관리원",
                    "employment_type": "정규직",
                    "duties": "시설 보안, 출입 통제, 순찰, 간단한 시설 점검",
                    "requirements": "책임감, 성실함, 기본적인 체력",
                    "benefits": "4대보험, 야간 수당, 휴게 시설",
                    "senior_friendly": True
                }
            }
        }
    
    return jsonify({
        "success": True,
        "templates": templates
    })

@job_assistant_bp.route("/api/job-keywords")
@login_required
def get_job_keywords():
    """
    직무별 추천 키워드 제공
    """
    
    keywords = {
        "duties": {
            "고객서비스": ["고객 상담", "문의 응답", "불만 처리", "서비스 개선"],
            "사무업무": ["문서 작성", "데이터 입력", "전화 응대", "일정 관리"],
            "판매업무": ["상품 판매", "고객 안내", "재고 관리", "계산 업무"],
            "관리업무": ["시설 관리", "보안 업무", "출입 통제", "점검 업무"]
        },
        "requirements": {
            "기본역량": ["성실함", "책임감", "원활한 의사소통", "팀워크"],
            "기술역량": ["컴퓨터 활용", "오피스 프로그램", "POS 시스템", "기본 회계"],
            "경험": ["고객 서비스 경험", "사무 업무 경험", "판매 경험", "관리 경험"]
        },
        "benefits": {
            "기본혜택": ["4대보험", "퇴직금", "유급휴가", "경조사비"],
            "추가혜택": ["중식 제공", "교통비 지원", "교육비 지원", "직원 할인"],
            "시니어특화": ["유연 근무", "건강검진", "안전 교육", "멘토링"]
        }
    }
    
    return jsonify({
        "success": True,
        "keywords": keywords
    })