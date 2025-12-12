#!/usr/bin/env python3
"""
GitHub API를 사용하여 저장소 생성 및 푸시
"""
import subprocess
import json
import os
import sys

REPO_NAME = "polymarket-dashboard"
GITHUB_USER = "chasanghun"

def get_github_token():
    """GitHub 토큰 찾기"""
    # 환경 변수에서 확인
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token
    
    # Git credential helper에서 확인 시도
    try:
        result = subprocess.run(
            ['git', 'credential', 'fill'],
            input='protocol=https\nhost=github.com\n\n',
            text=True,
            capture_output=True,
            timeout=5
        )
        if 'password=' in result.stdout:
            return result.stdout.split('password=')[1].strip()
    except:
        pass
    
    return None

def create_repo_with_api(token):
    """GitHub API로 저장소 생성"""
    import urllib.request
    import urllib.error
    
    url = 'https://api.github.com/user/repos'
    data = json.dumps({
        'name': REPO_NAME,
        'description': 'Polymarket 기업 마켓 대시보드',
        'public': True
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"API 오류: {e.code}")
        print(f"응답: {error_data}")
        return None

def main():
    print("🚀 GitHub 저장소 생성 및 푸시 시작...")
    print("")
    
    # 토큰 확인
    token = get_github_token()
    if not token:
        print("⚠️  GitHub 토큰을 찾을 수 없습니다.")
        print("")
        print("💡 해결 방법:")
        print("   1. GitHub Personal Access Token 생성:")
        print("      https://github.com/settings/tokens")
        print("   2. 다음 명령어 실행:")
        print(f"      export GITHUB_TOKEN=your_token")
        print("      python3 create_repo_and_push.py")
        print("")
        print("   또는 저장소를 수동으로 생성한 후:")
        print("   git push -u origin main")
        return 1
    
    print("✅ GitHub 토큰 발견")
    print("📦 저장소 생성 중...")
    
    # 저장소 생성
    repo_data = create_repo_with_api(token)
    if not repo_data:
        print("❌ 저장소 생성 실패")
        return 1
    
    print("✅ 저장소 생성 완료!")
    print(f"   URL: {repo_data.get('html_url', 'N/A')}")
    print("")
    
    # 원격 저장소 설정
    repo_url = f"https://{token}@github.com/{GITHUB_USER}/{REPO_NAME}.git"
    subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True)
    subprocess.run(['git', 'remote', 'add', 'origin', repo_url])
    
    print("📤 코드 푸시 중...")
    result = subprocess.run(['git', 'push', '-u', 'origin', 'main'])
    
    if result.returncode == 0:
        print("")
        print("✅ 푸시 완료!")
        print(f"📊 저장소: https://github.com/{GITHUB_USER}/{REPO_NAME}")
        print("")
        print("🌐 Vercel 배포:")
        print("   https://vercel.com/new 에서 저장소를 선택하여 배포하세요")
        return 0
    else:
        print("❌ 푸시 실패")
        return 1

if __name__ == '__main__':
    sys.exit(main())
