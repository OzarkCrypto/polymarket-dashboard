#!/bin/bash
# GitHub 푸시 및 Vercel 배포 스크립트

set -e

echo "🚀 Polymarket 대시보드 배포 시작..."
echo ""

# GitHub 저장소 확인
if [ -z "$GITHUB_REPO_URL" ]; then
    echo "⚠️  GitHub 저장소 URL이 설정되지 않았습니다."
    echo ""
    echo "📝 다음 단계를 따라주세요:"
    echo ""
    echo "1. GitHub에서 새 저장소를 만드세요:"
    echo "   https://github.com/new"
    echo ""
    echo "2. 저장소 이름을 입력하세요 (예: polymarket-dashboard)"
    echo ""
    echo "3. 저장소를 만든 후, 다음 명령어를 실행하세요:"
    echo ""
    echo "   export GITHUB_REPO_URL=https://github.com/YOUR_USERNAME/polymarket-dashboard.git"
    echo "   ./deploy.sh"
    echo ""
    echo "또는 직접 실행:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/polymarket-dashboard.git"
    echo "   git push -u origin main"
    echo ""
    exit 1
fi

# Git 원격 저장소 설정
echo "📦 Git 원격 저장소 설정 중..."
git remote remove origin 2>/dev/null || true
git remote add origin "$GITHUB_REPO_URL"

# GitHub에 푸시
echo "📤 GitHub에 푸시 중..."
git push -u origin main

echo "✅ GitHub 푸시 완료!"
echo ""

# Vercel 배포
echo "🌐 Vercel 배포 시작..."
echo ""

# Vercel CLI 확인
if ! command -v vercel &> /dev/null; then
    echo "📦 Vercel CLI 설치 중..."
    if command -v npm &> /dev/null; then
        npm install -g vercel
    else
        echo "⚠️  npm이 설치되어 있지 않습니다."
        echo "   Node.js를 먼저 설치해주세요: https://nodejs.org/"
        echo ""
        echo "   또는 Vercel 웹사이트에서 직접 배포하세요:"
        echo "   https://vercel.com/new"
        exit 1
    fi
fi

# Vercel 배포
echo "🚀 Vercel에 배포 중..."
vercel --prod --yes

echo ""
echo "✅ 배포 완료!"
echo ""
echo "📊 대시보드가 배포되었습니다!"
echo "   Vercel 대시보드에서 URL을 확인하세요: https://vercel.com/dashboard"

