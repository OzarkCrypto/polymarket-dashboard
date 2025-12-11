#!/bin/bash
# Polymarket 대시보드 실행 스크립트

echo "🚀 Polymarket 기업 마켓 대시보드 시작 중..."
echo ""

# 가상환경 확인 및 생성 (선택사항)
if [ ! -d "venv" ]; then
    echo "📦 가상환경이 없습니다. 생성하시겠습니까? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
else
    source venv/bin/activate
fi

# 패키지 설치 확인
echo "📦 필요한 패키지 확인 중..."
pip install -q -r requirements.txt

# 대시보드 실행
echo ""
echo "🌐 대시보드를 시작합니다..."
echo "브라우저에서 자동으로 열립니다."
echo ""
streamlit run polymarket_dashboard.py

