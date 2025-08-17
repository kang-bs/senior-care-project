#!/usr/bin/env python3
"""
JobPost 테이블에 기업 이음 전용 컬럼 추가 마이그레이션 스크립트
"""

import os
import sys
import pymysql

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
    
    def get_db_connection():
        """데이터베이스 연결 생성"""
        # DATABASE_URL에서 연결 정보 파싱
        db_url = Config.SQLALCHEMY_DATABASE_URI
        # mysql+pymysql://root:password@localhost/database_name 형태
        
        if 'mysql+pymysql://' in db_url:
            # URL 파싱
            url_parts = db_url.replace('mysql+pymysql://', '').split('/')
            auth_host = url_parts[0]
            database = url_parts[1] if len(url_parts) > 1 else 'senior_house'
            
            if '@' in auth_host:
                auth, host = auth_host.split('@')
                if ':' in auth:
                    user, password = auth.split(':')
                else:
                    user = auth
                    password = ''
            else:
                host = auth_host
                user = 'root'
                password = ''
            
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            else:
                port = 3306
        else:
            # 기본값
            host = 'localhost'
            port = 3306
            user = 'root'
            password = 'bguy5732!?'
            database = 'senior_house'
        
        return pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
    
    def check_column_exists(cursor, table_name, column_name):
        """컬럼이 존재하는지 확인"""
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
        """)
        return cursor.fetchone()[0] > 0
    
    def add_columns_to_job_post():
        """JobPost 테이블에 새 컬럼들 추가"""
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            print("📊 JobPost 테이블 컬럼 추가 시작...")
            
            # 추가할 컬럼들 정의
            new_columns = [
                ("job_category", "VARCHAR(50)"),
                ("job_category_custom", "VARCHAR(100)"),
                ("salary_min", "INT"),
                ("salary_max", "INT"),
                ("salary_negotiable", "BOOLEAN DEFAULT FALSE"),
                ("experience_required", "VARCHAR(20)"),
                ("benefit_commute_bus", "BOOLEAN DEFAULT FALSE"),
                ("benefit_lunch", "BOOLEAN DEFAULT FALSE"),
                ("benefit_uniform", "BOOLEAN DEFAULT FALSE"),
                ("benefit_health_checkup", "BOOLEAN DEFAULT FALSE"),
                ("benefit_other", "VARCHAR(200)"),
                ("disabled_parking", "BOOLEAN DEFAULT FALSE"),
                ("disabled_elevator", "BOOLEAN DEFAULT FALSE"),
                ("disabled_ramp", "BOOLEAN DEFAULT FALSE"),
                ("disabled_restroom", "BOOLEAN DEFAULT FALSE"),
                ("recruitment_start_date", "DATE"),
                ("recruitment_end_date", "DATE")
            ]
            
            added_columns = []
            skipped_columns = []
            
            for column_name, column_type in new_columns:
                if check_column_exists(cursor, 'job_post', column_name):
                    print(f"  ⏭️  {column_name} (이미 존재)")
                    skipped_columns.append(column_name)
                else:
                    try:
                        sql = f"ALTER TABLE job_post ADD COLUMN {column_name} {column_type}"
                        cursor.execute(sql)
                        print(f"  ✅ {column_name} 추가됨")
                        added_columns.append(column_name)
                    except Exception as e:
                        print(f"  ❌ {column_name} 추가 실패: {e}")
            
            connection.commit()
            
            print(f"\n📋 결과 요약:")
            print(f"  - 추가된 컬럼: {len(added_columns)}개")
            print(f"  - 기존 컬럼: {len(skipped_columns)}개")
            
            if added_columns:
                print(f"\n✅ 새로 추가된 컬럼들:")
                for col in added_columns:
                    print(f"  - {col}")
            
            if skipped_columns:
                print(f"\n⏭️  이미 존재하는 컬럼들:")
                for col in skipped_columns:
                    print(f"  - {col}")
            
            print("\n🎉 JobPost 테이블 마이그레이션 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 마이그레이션 오류: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()
    
    def verify_migration():
        """마이그레이션 결과 확인"""
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            print("\n🔍 마이그레이션 결과 확인 중...")
            
            # job_post 테이블의 모든 컬럼 조회
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'job_post'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            
            print(f"\n📋 job_post 테이블 컬럼 목록 ({len(columns)}개):")
            for col_name, data_type, is_nullable, default_val in columns:
                nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                default = f" DEFAULT {default_val}" if default_val else ""
                print(f"  - {col_name}: {data_type} {nullable}{default}")
            
            # 기업 이음 전용 컬럼들 확인
            company_columns = [
                'job_category', 'job_category_custom', 'salary_min', 'salary_max',
                'salary_negotiable', 'experience_required', 'benefit_commute_bus',
                'benefit_lunch', 'benefit_uniform', 'benefit_health_checkup',
                'benefit_other', 'disabled_parking', 'disabled_elevator',
                'disabled_ramp', 'disabled_restroom', 'recruitment_start_date',
                'recruitment_end_date'
            ]
            
            existing_columns = [col[0] for col in columns]
            
            print(f"\n🆕 기업 이음 전용 컬럼 상태:")
            all_present = True
            for col in company_columns:
                if col in existing_columns:
                    print(f"  ✅ {col}")
                else:
                    print(f"  ❌ {col} (누락)")
                    all_present = False
            
            if all_present:
                print(f"\n🎉 모든 기업 이음 전용 컬럼이 정상적으로 추가되었습니다!")
            else:
                print(f"\n⚠️  일부 컬럼이 누락되었습니다. 마이그레이션을 다시 실행해주세요.")
            
            return all_present
            
        except Exception as e:
            print(f"❌ 확인 중 오류: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    if __name__ == "__main__":
        print("🚀 JobPost 테이블 마이그레이션 시작\n")
        
        try:
            # 1. 컬럼 추가
            if add_columns_to_job_post():
                # 2. 결과 확인
                if verify_migration():
                    print("\n✅ 마이그레이션 성공! 이제 기업 이음 기능을 사용할 수 있습니다.")
                    print("\n📝 다음 단계:")
                    print("   1. Flask 앱 재시작")
                    print("   2. 홈 화면에서 '기업 이음' 탭 클릭")
                    print("   3. 기업 회원으로 로그인 후 공고 작성")
                else:
                    print("\n⚠️  마이그레이션이 완전하지 않습니다. 수동으로 확인이 필요합니다.")
            else:
                print("\n❌ 마이그레이션 실패")
                
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            import traceback
            traceback.print_exc()

except ImportError as e:
    print(f"❌ Import 오류: {e}")
    print("필요한 패키지가 설치되어 있는지 확인해주세요.")
    print("pip install pymysql")
except Exception as e:
    print(f"❌ 설정 오류: {e}")
    import traceback
    traceback.print_exc()