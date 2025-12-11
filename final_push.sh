#!/bin/bash
# 최종 푸시 스크립트

REPO_NAME="polymarket-dashboard"
GITHUB_USER="chasanghun"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "🚀 GitHub 푸시 시도..."
echo ""

# 원격 저장소 설정
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

echo "📤 푸시 중..."
if git push -u origin main 2>&1; then
    echo ""
    echo "✅ 푸시 완료!"
    echo ""
    echo "📊 저장소: https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
    echo "🌐 Vercel 배포:"
    echo "   https://vercel.com/new 에서 저장소를 선택하여 배포하세요"
else
    echo ""
    echo "⚠️  푸시 실패 - 저장소가 없거나 인증이 필요합니다"
    echo ""
    echo "💡 해결 방법:"
    echo "   1. GitHub에서 저장소 생성: https://github.com/new"
    echo "      저장소 이름: $REPO_NAME"
    echo "   2. Personal Access Token 생성: https://github.com/settings/tokens"
    echo "   3. 다음 명령어 실행:"
    echo "      git remote set-url origin https://YOUR_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "      git push -u origin main"
fi
