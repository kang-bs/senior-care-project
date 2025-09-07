"""
채용 공고 AI 글쓰기 도우미
==========================

시니어 채용에 특화된 AI 글쓰기 서비스입니다.

주요 기능:
- 구조화된 입력으로 전문적인 채용 공고 생성
- 차별 표현 자동 필터링
- 시니어 친화적 문구 최적화
- 급여/근무조건 검증
- 해시태그 자동 생성
"""

import re
import json
from typing import Dict, List, Optional
from datetime import datetime

class JobWritingAssistant:
    
    def __init__(self):
        # 차별 표현 필터링 키워드
        self.discriminatory_keywords = {
            '나이': ['젊은', '청년', '20대', '30대', '40대', '50대', '60대', '나이', '연령'],
            '성별': ['남자', '여자', '남성', '여성', '미혼', '기혼', '미스', '미세스'],
            '외모': ['키', '몸무게', '외모', '미모', '잘생긴', '예쁜', '날씬한'],
            '출신': ['지역', '학벌', '출신대', '명문대', '지방대']
        }
        
        # 시니어 친화 대체 문구
        self.senior_friendly_replacements = {
            '체력이 좋은': '건강하신',
            '빠른 업무': '꼼꼼한 업무',
            '신속한': '정확한',
            '젊은 감각': '풍부한 경험',
            '트렌디한': '안정적인'
        }
        
        # 급여 단위 매핑
        self.pay_units = {
            'hourly': '시급',
            'daily': '일급', 
            'monthly': '월급',
            'yearly': '연봉',
            'negotiable': '협의'
        }

    def generate_job_description(self, job_data: Dict) -> Dict:
        """
        채용 공고 상세 설명 생성
        
        Args:
            job_data: 채용 공고 기본 정보
            
        Returns:
            생성된 채용 공고 텍스트와 메타데이터
        """
        try:
            # 입력 데이터 검증
            validated_data = self._validate_input(job_data)
            
            # 공고 타입에 따른 다른 처리
            job_type = validated_data.get('job_type', 'company')
            
            if job_type == 'general':
                # 일반 공고용 생성
                title = self._generate_general_title(validated_data)
                summary = self._generate_general_summary(validated_data)
                description = self._generate_general_description(validated_data)
                hashtags = self._generate_general_hashtags(validated_data)
            else:
                # 기업 공고용 생성 (기존)
                title = self._generate_title(validated_data)
                summary = self._generate_summary(validated_data)
                description = self._generate_detailed_description(validated_data)
                hashtags = self._generate_hashtags(validated_data)
            
            # 차별 표현 필터링
            filtered_content = self._apply_discrimination_filter({
                'title': title,
                'summary': summary,
                'description': description,
                'hashtags': hashtags
            })
            
            return {
                'success': True,
                'content': filtered_content,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'senior_friendly': validated_data.get('senior_friendly', False),
                    'tone': validated_data.get('tone', '친절'),
                    'word_count': len(filtered_content['description'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback_template': self._generate_fallback_template(job_data)
            }

    def _validate_input(self, job_data: Dict) -> Dict:
        """입력 데이터 검증 및 정규화"""
        validated = {}
        
        # 필수 필드 검증
        required_fields = ['title', 'employment_type', 'location', 'duties']
        for field in required_fields:
            if not job_data.get(field):
                raise ValueError(f"필수 필드 누락: {field}")
            validated[field] = job_data[field].strip()
        
        # 급여 정보 검증
        pay_info = job_data.get('pay', {})
        if pay_info:
            validated['pay'] = self._validate_pay_info(pay_info)
        
        # 근무 시간 검증
        schedule = job_data.get('schedule', {})
        if schedule:
            validated['schedule'] = self._validate_schedule(schedule)
        
        # 선택 필드
        optional_fields = ['requirements', 'benefits', 'apply', 'deadline', 'senior_friendly', 'tone']
        for field in optional_fields:
            if job_data.get(field):
                validated[field] = job_data[field]
        
        return validated

    def _validate_pay_info(self, pay_info: Dict) -> Dict:
        """급여 정보 검증"""
        validated_pay = {}
        
        pay_type = pay_info.get('type', 'negotiable')
        if pay_type not in self.pay_units:
            pay_type = 'negotiable'
        validated_pay['type'] = pay_type
        
        amount = pay_info.get('amount')
        if amount and isinstance(amount, (int, float)) and amount > 0:
            validated_pay['amount'] = int(amount)
        
        validated_pay['currency'] = pay_info.get('currency', 'KRW')
        
        return validated_pay

    def _validate_schedule(self, schedule: Dict) -> Dict:
        """근무 시간 검증"""
        validated_schedule = {}
        
        # 근무 요일
        if schedule.get('days'):
            validated_schedule['days'] = schedule['days']
        
        # 시간 형식 검증 (HH:MM)
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        
        for time_field in ['start', 'end']:
            time_value = schedule.get(time_field)
            if time_value and time_pattern.match(time_value):
                validated_schedule[time_field] = time_value
        
        return validated_schedule

    def _generate_title(self, job_data: Dict) -> str:
        """채용 공고 제목 생성"""
        location = job_data.get('location', '').split()[0]  # 첫 번째 지역명만
        title = job_data['title']
        employment_type = job_data['employment_type']
        
        pay_info = job_data.get('pay', {})
        pay_text = ""
        if pay_info.get('amount') and pay_info.get('type') != 'negotiable':
            pay_unit = self.pay_units.get(pay_info['type'], '')
            amount = f"{pay_info['amount']:,}"
            pay_text = f"({pay_unit} {amount}원)"
        
        if location:
            return f"[{location}] {title} {employment_type}{pay_text}"
        else:
            return f"{title} {employment_type}{pay_text}"

    def _generate_summary(self, job_data: Dict) -> str:
        """핵심 요약 3줄 생성"""
        lines = []
        
        # 1줄: 주요 업무
        duties = job_data['duties'][:50] + "..." if len(job_data['duties']) > 50 else job_data['duties']
        lines.append(f"{duties}")
        
        # 2줄: 근무 조건
        schedule_parts = []
        schedule = job_data.get('schedule', {})
        if schedule.get('days'):
            schedule_parts.append(schedule['days'])
        if schedule.get('start') and schedule.get('end'):
            schedule_parts.append(f"{schedule['start']}~{schedule['end']}")
        
        pay_info = job_data.get('pay', {})
        if pay_info.get('amount'):
            pay_unit = self.pay_units.get(pay_info['type'], '')
            amount = f"{pay_info['amount']:,}"
            schedule_parts.append(f"{pay_unit} {amount}원")
        
        if schedule_parts:
            lines.append(" / ".join(schedule_parts))
        
        # 3줄: 혜택 또는 시니어 친화 메시지
        if job_data.get('senior_friendly'):
            lines.append("기본 교육을 제공하니 처음이셔도 가능합니다.")
        elif job_data.get('benefits'):
            benefits = job_data['benefits'][:40] + "..." if len(job_data['benefits']) > 40 else job_data['benefits']
            lines.append(benefits)
        else:
            lines.append("경력 무관, 성실하신 분을 모십니다.")
        
        return "\n".join(lines)

    def _generate_detailed_description(self, job_data: Dict) -> str:
        """상세 본문 생성"""
        sections = []
        
        # 주요업무 섹션
        sections.append(f"주요업무: {job_data['duties']}")
        
        # 근무조건 섹션
        conditions = []
        conditions.append(f"{job_data['employment_type']}")
        conditions.append(job_data['location'])
        
        schedule = job_data.get('schedule', {})
        if schedule.get('days'):
            conditions.append(schedule['days'])
        if schedule.get('start') and schedule.get('end'):
            conditions.append(f"{schedule['start']}–{schedule['end']}")
        
        pay_info = job_data.get('pay', {})
        if pay_info.get('amount'):
            pay_unit = self.pay_units.get(pay_info['type'], '')
            amount = f"{pay_info['amount']:,}"
            conditions.append(f"{pay_unit} {amount}원")
        elif pay_info.get('type') == 'negotiable':
            conditions.append("급여 협의")
        
        sections.append(f"근무조건: {' / '.join(conditions)}")
        
        # 자격·우대 섹션
        if job_data.get('requirements'):
            requirements = job_data['requirements']
            if job_data.get('senior_friendly'):
                requirements += " / 미경력도 환영"
            sections.append(f"자격·우대: {requirements}")
        
        # 복리후생 섹션
        if job_data.get('benefits'):
            sections.append(f"복리후생: {job_data['benefits']}")
        
        # 지원방법 섹션
        apply_info = job_data.get('apply', '플랫폼 내 지원')
        deadline = job_data.get('deadline', '채용 시 마감')
        sections.append(f"지원방법: {apply_info} / 마감: {deadline}")
        
        return "\n\n".join(sections)

    def _generate_hashtags(self, job_data: Dict) -> List[str]:
        """해시태그 생성"""
        hashtags = []
        
        # 직무 관련
        title_words = job_data['title'].split()
        for word in title_words:
            if len(word) > 1:
                hashtags.append(f"#{word}")
        
        # 고용형태
        hashtags.append(f"#{job_data['employment_type']}")
        
        # 지역
        location_parts = job_data['location'].split()
        for part in location_parts[:2]:  # 최대 2개 지역명
            if len(part) > 1:
                hashtags.append(f"#{part}근무")
        
        # 시니어 친화
        if job_data.get('senior_friendly'):
            hashtags.append("#시니어환영")
            hashtags.append("#경력무관")
        
        # 중복 제거 및 최대 5개로 제한
        unique_hashtags = list(dict.fromkeys(hashtags))[:5]
        return unique_hashtags

    def _apply_discrimination_filter(self, content: Dict) -> Dict:
        """차별 표현 필터링"""
        filtered_content = {}
        
        for key, text in content.items():
            if isinstance(text, str):
                filtered_text = text
                
                # 차별적 키워드 제거/대체
                for category, keywords in self.discriminatory_keywords.items():
                    for keyword in keywords:
                        if keyword in filtered_text:
                            # 맥락에 따른 대체
                            if category == '나이':
                                filtered_text = re.sub(rf'\b{keyword}\b.*?[우선|선호|환영]', '경력무관', filtered_text)
                            elif category == '성별':
                                filtered_text = re.sub(rf'\b{keyword}\b.*?[우선|선호|환영]', '성별무관', filtered_text)
                
                # 시니어 친화 표현으로 대체
                for old_phrase, new_phrase in self.senior_friendly_replacements.items():
                    filtered_text = filtered_text.replace(old_phrase, new_phrase)
                
                filtered_content[key] = filtered_text
            elif isinstance(text, list):
                filtered_content[key] = text
        
        return filtered_content

    def _generate_general_title(self, job_data: Dict) -> str:
        """일반 공고용 제목 생성 (더 간단하고 친근하게)"""
        location = job_data.get('location', '').split()[0]  # 첫 번째 지역명만
        title = job_data['title']
        employment_type = job_data['employment_type']
        
        pay_info = job_data.get('pay', {})
        pay_text = ""
        if pay_info.get('amount') and pay_info.get('type') != 'negotiable':
            pay_unit = self.pay_units.get(pay_info['type'], '')
            amount = f"{pay_info['amount']:,}"
            pay_text = f" ({pay_unit} {amount}원)"
        
        # 일반 공고는 더 친근한 형태
        if location:
            return f"{location} {title} {employment_type}{pay_text} 구합니다"
        else:
            return f"{title} {employment_type}{pay_text} 구합니다"

    def _generate_general_summary(self, job_data: Dict) -> str:
        """일반 공고용 핵심 요약 (더 친근하고 간단하게)"""
        lines = []
        
        # 1줄: 업무 소개
        duties = job_data['duties']
        if len(duties) > 30:
            duties = duties[:30] + "..."
        lines.append(f"📝 {duties}")
        
        # 2줄: 근무 조건
        schedule_parts = []
        schedule = job_data.get('schedule', {})
        if schedule.get('days'):
            schedule_parts.append(schedule['days'])
        if schedule.get('time'):
            schedule_parts.append(schedule['time'])
        
        pay_info = job_data.get('pay', {})
        if pay_info.get('amount'):
            pay_unit = self.pay_units.get(pay_info['type'], '')
            amount = f"{pay_info['amount']:,}"
            schedule_parts.append(f"{pay_unit} {amount}원")
        
        if schedule_parts:
            lines.append(f"⏰ {' / '.join(schedule_parts)}")
        
        # 3줄: 시니어 친화 메시지
        if job_data.get('senior_friendly'):
            if job_data.get('training_provided'):
                lines.append("👨‍🏫 처음이셔도 괜찮습니다. 친절하게 알려드려요!")
            elif job_data.get('easy_work'):
                lines.append("😊 어렵지 않은 일이에요. 편안하게 일하실 수 있습니다.")
            else:
                lines.append("🤝 나이 상관없이 환영합니다!")
        else:
            lines.append("💪 성실하고 책임감 있는 분을 찾습니다.")
        
        return "\n".join(lines)

    def _generate_general_description(self, job_data: Dict) -> str:
        """일반 공고용 상세 설명 (더 친근하고 이해하기 쉽게)"""
        sections = []
        
        # 어떤 일인가요?
        sections.append(f"🔍 어떤 일인가요?\n{job_data['duties']}")
        
        # 근무 조건
        conditions = []
        conditions.append(f"고용형태: {job_data['employment_type']}")
        conditions.append(f"근무지: {job_data['location']}")
        
        schedule = job_data.get('schedule', {})
        if schedule.get('days'):
            conditions.append(f"근무요일: {schedule['days']}")
        if schedule.get('time'):
            conditions.append(f"근무시간: {schedule['time']}")
        
        pay_info = job_data.get('pay', {})
        if pay_info.get('amount'):
            pay_unit = self.pay_units.get(pay_info['type'], '')
            amount = f"{pay_info['amount']:,}"
            conditions.append(f"급여: {pay_unit} {amount}원")
        elif pay_info.get('type') == 'negotiable':
            conditions.append("급여: 면접 시 협의")
        
        sections.append(f"📋 근무 조건\n" + "\n".join([f"• {cond}" for cond in conditions]))
        
        # 어떤 분을 찾나요?
        if job_data.get('requirements'):
            requirements = job_data['requirements']
            # 시니어 친화적 표현 추가
            if job_data.get('senior_friendly'):
                requirements += "\n• 나이, 경력 상관없어요"
            if job_data.get('training_provided'):
                requirements += "\n• 처음이셔도 천천히 알려드립니다"
            sections.append(f"👥 어떤 분을 찾나요?\n{requirements}")
        
        # 좋은 점
        if job_data.get('benefits'):
            benefits = job_data['benefits']
            if job_data.get('flexible_time'):
                benefits += "\n• 시간 조정 가능해요"
            sections.append(f"✨ 좋은 점\n{benefits}")
        
        # 연락 방법
        contact_method = job_data.get('contact_method', '플랫폼 내 지원')
        sections.append(f"📞 연락 방법\n{contact_method}")
        
        return "\n\n".join(sections)

    def _generate_general_hashtags(self, job_data: Dict) -> List[str]:
        """일반 공고용 해시태그 (더 친근하고 검색하기 쉽게)"""
        hashtags = []
        
        # 직무 관련
        title_words = job_data['title'].split()
        for word in title_words:
            if len(word) > 1:
                hashtags.append(f"#{word}")
        
        # 고용형태
        hashtags.append(f"#{job_data['employment_type']}")
        
        # 지역
        location_parts = job_data['location'].split()
        for part in location_parts[:2]:
            if len(part) > 1:
                hashtags.append(f"#{part}")
        
        # 시니어 친화
        if job_data.get('senior_friendly'):
            hashtags.append("#시니어환영")
            hashtags.append("#나이무관")
        
        if job_data.get('easy_work'):
            hashtags.append("#쉬운일")
        
        if job_data.get('training_provided'):
            hashtags.append("#교육제공")
        
        if job_data.get('flexible_time'):
            hashtags.append("#시간조정가능")
        
        # 중복 제거 및 최대 6개로 제한
        unique_hashtags = list(dict.fromkeys(hashtags))[:6]
        return unique_hashtags

    def _generate_fallback_template(self, job_data: Dict) -> str:
        """AI 실패 시 기본 템플릿"""
        title = job_data.get('title', '채용공고')
        company = job_data.get('company', '회사명')
        location = job_data.get('location', '근무지')
        
        return f"""
{title} 채용

{company}에서 {title} 직무를 담당하실 분을 모집합니다.

근무지: {location}
고용형태: {job_data.get('employment_type', '정규직')}

많은 지원 바랍니다.
        """.strip()

# 전역 인스턴스
job_assistant = JobWritingAssistant()