#!/bin/bash
# GitHub 저장소 자동 생성 및 푸시 스크립트

set -e

echo "🔧 GitHub 저장소 설정"
echo ""

# GitHub CLI 확인
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI 발견"
    
    # 로그인 확인
    if gh auth status &>/dev/null; then
        echo "✅ GitHub에 로그인되어 있습니다."
        
        # 저장소 이름 입력
        read -p "📝 저장소 이름을 입력하세요 (예: polymarket-dashboard): " REPO_NAME
        
        if [ -z "$REPO_NAME" ]; then
            REPO_NAME="polymarket-dashboard"
            echo "기본값 사용: $REPO_NAME"
        fi
        
        # 저장소 생성
        echo ""
        echo "📦 GitHub에 저장소 생성 중..."
        gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
        
        echo ""
        echo "✅ GitHub 저장소 생성 및 푸시 완료!"
        echo "   저장소 URL: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
        
    else
        echo "⚠️  GitHub에 로그인되어 있지 않습니다."
        echo "   다음 명령어로 로그인하세요:"
        echo "   gh auth login"
        exit 1
    fi
else
    echo "⚠️  GitHub CLI가 설치되어 있지 않습니다."
    echo ""
    echo "📝 수동 설정 방법:"
    echo ""
    echo "1. GitHub에서 저장소 생성:"
    echo "   https://github.com/new"
    echo ""
    echo "2. 저장소 이름 입력 (예: polymarket-dashboard)"
    echo ""
    echo "3. 다음 명령어 실행:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/polymarket-dashboard.git"
    echo "   git push -u origin main"
    echo ""
    echo "또는 GitHub CLI 설치:"
    echo "   brew install gh"
    echo "   gh auth login"
    exit 1
fi

