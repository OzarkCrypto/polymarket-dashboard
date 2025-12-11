#!/bin/bash
# 저장소 생성 대기 후 자동 푸시

REPO_NAME="polymarket-dashboard"
GITHUB_USER="chasanghun"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "⏳ GitHub 저장소 생성 대기 중..."
echo ""

# 원격 저장소 설정
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# 저장소가 생성될 때까지 대기하며 푸시 시도
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    
    # 저장소 존재 확인
    if curl -s "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME" | grep -q '"name"'; then
        echo "✅ 저장소 발견! 푸시 시작..."
        
        if git push -u origin main 2>&1; then
            echo ""
            echo "✅ 푸시 완료!"
            echo ""
            echo "📊 저장소 URL: https://github.com/$GITHUB_USER/$REPO_NAME"
            echo ""
            echo "🌐 Vercel 배포:"
            echo "   https://vercel.com/new 에서 저장소를 선택하여 배포하세요"
            exit 0
        else
            echo "⚠️  푸시 실패 - 인증이 필요할 수 있습니다"
            echo "   GitHub Personal Access Token을 사용하세요"
            exit 1
        fi
    else
        echo "⏳ 저장소 대기 중... ($ATTEMPT/$MAX_ATTEMPTS)"
        sleep 2
    fi
done

echo "❌ 타임아웃 - 저장소가 생성되지 않았습니다"
echo "   수동으로 저장소를 생성한 후 다시 시도하세요"
exit 1
