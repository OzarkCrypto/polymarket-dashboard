#!/bin/bash
# 자동 배포 스크립트 - 저장소 생성 후 푸시

set -e

REPO_NAME="polymarket-dashboard"
GITHUB_USER="chasanghun"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "🚀 자동 배포 시작..."
echo ""

# 1. 원격 저장소 설정
echo "📦 원격 저장소 설정 중..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL" || true

# 2. 저장소 존재 확인 및 생성 안내
echo "🔍 GitHub 저장소 확인 중..."

# GitHub API로 저장소 확인 (토큰 없이도 public 저장소는 확인 가능)
if curl -s "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME" | grep -q '"name"'; then
    echo "✅ 저장소가 이미 존재합니다."
    EXISTS=true
else
    echo "⚠️  저장소가 아직 생성되지 않았습니다."
    echo ""
    echo "📝 다음 단계를 따라주세요:"
    echo ""
    echo "   1. 브라우저에서 https://github.com/new 열기"
    echo "   2. 저장소 이름: $REPO_NAME"
    echo "   3. Public 선택"
    echo "   4. 'Create repository' 클릭"
    echo ""
    echo "   저장소 생성 후 이 스크립트를 다시 실행하세요."
    echo ""
    echo "   또는 GitHub Personal Access Token을 사용하여 자동 생성:"
    echo "   export GITHUB_TOKEN=your_token"
    echo "   ./auto_deploy.sh"
    echo ""
    
    # 토큰이 있으면 자동 생성 시도
    if [ -n "$GITHUB_TOKEN" ]; then
        echo "🔑 토큰을 사용하여 저장소 생성 시도 중..."
        RESPONSE=$(curl -s -X POST \
          -H "Authorization: token $GITHUB_TOKEN" \
          -H "Accept: application/vnd.github.v3+json" \
          https://api.github.com/user/repos \
          -d "{\"name\":\"$REPO_NAME\",\"description\":\"Polymarket 기업 마켓 대시보드\",\"public\":true}")
        
        if echo "$RESPONSE" | grep -q '"name"'; then
            echo "✅ 저장소 생성 완료!"
            EXISTS=true
        else
            echo "❌ 저장소 생성 실패"
            echo "응답: $RESPONSE"
            exit 1
        fi
    else
        exit 1
    fi
fi

# 3. 푸시 시도
if [ "$EXISTS" = true ]; then
    echo ""
    echo "📤 코드 푸시 중..."
    
    # 토큰이 있으면 URL에 포함
    if [ -n "$GITHUB_TOKEN" ]; then
        git remote set-url origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"
    fi
    
    if git push -u origin main; then
        echo ""
        echo "✅ 푸시 완료!"
        echo ""
        echo "📊 저장소 URL: https://github.com/$GITHUB_USER/$REPO_NAME"
        echo ""
        echo "🌐 다음 단계: Vercel 배포"
        echo "   https://vercel.com/new 에서 저장소를 선택하여 배포하세요"
        echo ""
    else
        echo ""
        echo "❌ 푸시 실패"
        echo ""
        echo "💡 해결 방법:"
        echo "   1. GitHub 인증 확인"
        echo "   2. Personal Access Token 사용:"
        echo "      export GITHUB_TOKEN=your_token"
        echo "      ./auto_deploy.sh"
        echo "   3. 또는 SSH 키 설정"
    fi
fi



