#!/bin/bash
# GitHub 저장소 생성 및 푸시 자동화

REPO_NAME="polymarket-dashboard"
GITHUB_USER="chasanghun"  # GitHub 사용자명으로 변경 필요

echo "🚀 GitHub 저장소 생성 및 푸시 시작..."
echo ""

# GitHub Personal Access Token 확인
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GitHub Personal Access Token이 필요합니다."
    echo ""
    echo "📝 토큰 생성 방법:"
    echo "   1. https://github.com/settings/tokens 접속"
    echo "   2. 'Generate new token (classic)' 클릭"
    echo "   3. 'repo' 권한 선택"
    echo "   4. 토큰 생성 후 다음 명령어 실행:"
    echo "      export GITHUB_TOKEN=your_token_here"
    echo "      ./create_and_push.sh"
    echo ""
    exit 1
fi

# GitHub API로 저장소 생성
echo "📦 GitHub에 저장소 생성 중..."
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"Polymarket 기업 마켓 대시보드\",\"public\":true}")

# 응답 확인
if echo "$RESPONSE" | grep -q '"name"'; then
    echo "✅ 저장소 생성 완료!"
    REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
    
    # 원격 저장소 추가 및 푸시
    echo "📤 코드 푸시 중..."
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REPO_URL"
    
    # 토큰을 사용한 URL로 변경
    git remote set-url origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"
    
    if git push -u origin main; then
        echo "✅ 푸시 완료!"
        echo ""
        echo "📊 저장소 URL: https://github.com/$GITHUB_USER/$REPO_NAME"
        echo ""
        echo "🌐 이제 Vercel에 배포하세요:"
        echo "   https://vercel.com/new"
    else
        echo "❌ 푸시 실패"
    fi
else
    echo "❌ 저장소 생성 실패"
    echo "응답: $RESPONSE"
fi
