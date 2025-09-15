#!/usr/bin/env python3
"""UI 수정 기능 테스트"""

import sys
sys.path.append('.')
from services.job_writing_assistant import job_assistant

# 일반 공고용 테스트 데이터 (UI에서 수집되는 형태)
test_data = {
    'title': '카페 서빙',
    'employment_type': '파트타임',
    'location': '서울 강남구',
    'duties': '고객 주문 받기, 음료 제조, 매장 청소',
    'requirements': '친절하신 분',
    'benefits': '식사 제공, 교통비 지원',
    'training_provided': True,
    'flexible_time': False,
    'job_type': 'general',
    'work_days': '월화수',
    'work_time': '09:00~18:00',
    'salary': '시급 12,000원'
}

print('=== UI 수정 기능 테스트 ===')
print('입력 데이터:', test_data)
print()

result = job_assistant.generate_job_description(test_data)
print('생성 성공:', result['success'])

if result['success']:
    print('\n=== 생성된 공고 ===')
    print('제목:', result['content']['title'])
    print('\n요약:')
    print(result['content']['summary'])
    print('\n상세설명:')
    print(result['content']['description'])
    print('\n해시태그:', result['content']['hashtags'])
    print('\n메타데이터:', result['metadata'])
else:
    print('오류:', result.get('error', '알 수 없는 오류'))
    if 'fallback_template' in result:
        print('대체 템플릿:', result['fallback_template'])