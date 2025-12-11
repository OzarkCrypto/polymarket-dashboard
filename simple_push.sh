#!/bin/bash
# 간단한 푸시 스크립트 (저장소가 이미 있는 경우)

echo "🚀 GitHub 푸시 시도..."
echo ""

# 저장소 URL 입력 받기
read -p "GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/polymarket-dashboard.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ URL이 입력되지 않았습니다."
    exit 1
fi

# 원격 저장소 설정
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# 푸시 시도
echo "📤 푸시 중..."
if git push -u origin main 2>&1; then
    echo "✅ 푸시 완료!"
else
    echo "❌ 푸시 실패 - 인증이 필요할 수 있습니다."
    echo ""
    echo "💡 해결 방법:"
    echo "   1. GitHub Personal Access Token 생성: https://github.com/settings/tokens"
    echo "   2. 다음 명령어 실행:"
    echo "      git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git"
    echo "      git push -u origin main"
fi
