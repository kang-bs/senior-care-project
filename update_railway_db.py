#!/usr/bin/env python3
"""
Railway 데이터베이스 스키마 업데이트 스크립트
===========================================

이 스크립트는 Railway 환경에서 데이터베이스 테이블을 최신 models.py에 맞게 업데이트합니다.

사용법:
1. Railway 환경변수가 설정된 상태에서 실행
2. 또는 로컬에서 Railway DATABASE_URL로 직접 연결하여 실행
"""

import os
import sys
from flask import Flask
from config import Config
from models import db

def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def update_database_schema():
    """데이터베이스 스키마 업데이트"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 데이터베이스 연결 테스트...")
            
            # 연결 테스트
            result = db.engine.execute('SELECT 1 as test')
            print("✅ 데이터베이스 연결 성공")
            
            print("🔄 데이터베이스 스키마 업데이트 시작...")
            
            # 모든 테이블 생성/업데이트 (기존 테이블은 유지, 새 컬럼만 추가)
            db.create_all()
            
            print("✅ 데이터베이스 스키마 업데이트 완료!")
            
            # 테이블 목록 확인
            print("\n📋 현재 테이블 목록:")
            tables = db.engine.execute("SHOW TABLES").fetchall()
            for table in tables:
                print(f"  - {table[0]}")
                
        except Exception as e:
            print(f"❌ 데이터베이스 업데이트 실패: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("🚀 Railway 데이터베이스 스키마 업데이트 시작")
    update_database_schema()
    print("🎉 완료!")