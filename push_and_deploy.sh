#!/bin/bash
# GitHub 푸시 및 Vercel 배포를 위한 간단한 스크립트

echo "🚀 Polymarket 대시보드 배포"
echo "================================"
echo ""

# 현재 상태 확인
echo "✅ Git 저장소 상태:"
git status --short
echo ""

# GitHub 저장소 URL 입력
echo "📝 GitHub 저장소 URL을 입력하세요"
echo "   예: https://github.com/your-username/polymarket-dashboard.git"
echo ""
read -p "GitHub 저장소 URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ 저장소 URL이 입력되지 않았습니다."
    echo ""
    echo "💡 GitHub에서 저장소를 만드는 방법:"
    echo "   1. https://github.com/new 접속"
    echo "   2. 저장소 이름 입력 (예: polymarket-dashboard)"
    echo "   3. 'Create repository' 클릭"
    echo "   4. 생성된 저장소의 URL을 복사하여 위에 입력"
    exit 1
fi

# 원격 저장소 설정
echo ""
echo "📦 원격 저장소 설정 중..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# GitHub에 푸시
echo "📤 GitHub에 푸시 중..."
if git push -u origin main; then
    echo "✅ GitHub 푸시 완료!"
    echo ""
    echo "🌐 이제 Vercel에 배포하세요:"
    echo ""
    echo "   방법 1 (웹사이트 - 추천):"
    echo "   1. https://vercel.com/new 접속"
    echo "   2. GitHub 저장소 선택: $REPO_URL"
    echo "   3. 'Deploy' 클릭"
    echo ""
    echo "   방법 2 (CLI):"
    echo "   npm install -g vercel"
    echo "   vercel --prod"
    echo ""
    echo "📊 저장소 URL: https://github.com/$(echo $REPO_URL | sed 's/.*github.com\///' | sed 's/\.git$//')"
else
    echo "❌ 푸시 실패"
    echo ""
    echo "💡 해결 방법:"
    echo "   1. GitHub 인증 확인"
    echo "   2. 저장소 URL이 올바른지 확인"
    echo "   3. 저장소가 생성되었는지 확인"
    echo ""
    echo "   GitHub CLI 사용:"
    echo "   brew install gh"
    echo "   gh auth login"
fi



