-- 채팅방 개별 사용자 나가기 필드 추가 마이그레이션
-- 실행일: 2025-01-09

-- applicant_left 컬럼 추가 (지원자가 나갔는지 여부)
ALTER TABLE chat_room 
ADD COLUMN applicant_left BOOLEAN DEFAULT FALSE COMMENT '지원자가 나갔는지 여부';

-- employer_left 컬럼 추가 (고용주가 나갔는지 여부)  
ALTER TABLE chat_room 
ADD COLUMN employer_left BOOLEAN DEFAULT FALSE COMMENT '고용주가 나갔는지 여부';

-- 기존 데이터에 대해 기본값 설정 (모든 기존 채팅방은 나가지 않은 상태로 설정)
UPDATE chat_room 
SET applicant_left = FALSE, employer_left = FALSE 
WHERE applicant_left IS NULL OR employer_left IS NULL;

-- 마이그레이션 완료 확인용 쿼리
SELECT 
    COUNT(*) as total_rooms,
    SUM(CASE WHEN applicant_left = TRUE THEN 1 ELSE 0 END) as applicant_left_count,
    SUM(CASE WHEN employer_left = TRUE THEN 1 ELSE 0 END) as employer_left_count
FROM chat_room;
