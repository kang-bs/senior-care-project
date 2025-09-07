#!/usr/bin/env python3
"""
Railway 데이터베이스 마이그레이션 스크립트
========================================

Railway MySQL 데이터베이스에 누락된 컬럼들을 추가합니다.

에러: Unknown column 'job_post.latitude' in 'field list'
해결: latitude, longitude 컬럼을 job_post 테이블에 추가
"""

import os
import sys
from flask import Flask
from config import Config
from models import db
import pymysql

def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def add_missing_columns():
    """누락된 컬럼들을 데이터베이스에 추가"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 데이터베이스 연결 테스트...")
            
            # 연결 테스트
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            print("✅ 데이터베이스 연결 성공")
            
            # job_post 테이블에 latitude, longitude 컬럼 추가
            print("🔄 job_post 테이블에 latitude, longitude 컬럼 추가...")
            
            # 컬럼 존재 여부 확인
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'job_post' 
                AND COLUMN_NAME IN ('latitude', 'longitude')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            # latitude 컬럼 추가
            if 'latitude' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE job_post 
                    ADD COLUMN latitude FLOAT NULL
                """)
                print("✅ latitude 컬럼 추가 완료")
            else:
                print("ℹ️ latitude 컬럼이 이미 존재합니다")
            
            # longitude 컬럼 추가
            if 'longitude' not in existing_columns:
                cursor.execute("""
                    ALTER TABLE job_post 
                    ADD COLUMN longitude FLOAT NULL
                """)
                print("✅ longitude 컬럼 추가 완료")
            else:
                print("ℹ️ longitude 컬럼이 이미 존재합니다")
            
            # 변경사항 커밋
            connection.commit()
            
            # 테이블 구조 확인
            print("\n📋 job_post 테이블 구조 확인:")
            cursor.execute("DESCRIBE job_post")
            columns = cursor.fetchall()
            for column in columns:
                if column[0] in ['latitude', 'longitude']:
                    print(f"  ✅ {column[0]}: {column[1]}")
            
            cursor.close()
            connection.close()
            
            print("\n🎉 데이터베이스 마이그레이션 완료!")
            
        except Exception as e:
            print(f"❌ 마이그레이션 실패: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("🚀 Railway 데이터베이스 마이그레이션 시작")
    add_missing_columns()
    print("✨ 완료!")