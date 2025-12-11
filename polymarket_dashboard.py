"""
Polymarket 기업 관련 마켓 대시보드
==================================
Streamlit을 사용한 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from polymarket_scraper import PolymarketScraper

# 페이지 설정
st.set_page_config(
    page_title="Polymarket 기업 마켓 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .insider-badge {
        background-color: #ff6b6b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<div class="main-header">📊 Polymarket 기업 관련 마켓 대시보드</div>', unsafe_allow_html=True)
st.markdown("**내부 정보 우위가 있을 수 있는 기업 관련 마켓을 필터링하여 보여줍니다.**")

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 새로고침 옵션
    use_selenium = st.checkbox("Selenium 사용 (더 정확하지만 느림)", value=False)
    
    # 새로고침 버튼
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        with st.spinner("마켓 데이터 수집 중..."):
            scraper = PolymarketScraper()
            try:
                df = scraper.scrape_all_markets(max_pages=5, use_selenium=use_selenium)
                if len(df) > 0:
                    st.session_state['markets_df'] = df
                    st.success(f"✅ {len(df)}개 마켓 수집 완료!")
                else:
                    st.warning("⚠️ 데이터를 가져오지 못했습니다. Polymarket 사이트를 확인하거나 나중에 다시 시도해주세요.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")
                st.info("💡 팁: Selenium을 사용하려면 `pip install selenium`을 실행하고 Chrome 브라우저가 설치되어 있어야 합니다.")
    
    st.divider()
    
    # 필터 옵션
    st.subheader("🔍 필터")
    
    filter_insider_only = st.checkbox("내부 정보 우위 가능성만 보기", value=False)
    
    # 기업 필터
    if 'markets_df' in st.session_state and len(st.session_state['markets_df']) > 0:
        df = st.session_state['markets_df']
        companies = set()
        for companies_str in df['matched_companies'].dropna():
            companies.update(companies_str.split(', '))
        
        selected_companies = st.multiselect(
            "기업 선택",
            options=sorted(companies),
            default=[]
        )
    else:
        selected_companies = []
    
    st.divider()
    
    st.markdown("""
    ### 📝 사용 방법
    1. **데이터 새로고침** 버튼을 클릭하여 최신 마켓 데이터를 수집합니다.
    2. 필터를 사용하여 관심 있는 기업이나 마켓을 찾습니다.
    3. 마켓 카드를 클릭하여 Polymarket에서 자세히 확인합니다.
    
    ### 💡 정보 우위 마켓
    - 제품 출시일, 발표일 등 내부 정보를 가진 사람이 우위를 가질 수 있는 마켓
    - 예: "OpenAI의 새 모델이 언제 출시될까?"
    """)

# 메인 콘텐츠
if 'markets_df' not in st.session_state or len(st.session_state['markets_df']) == 0:
    st.info("👈 사이드바에서 '데이터 새로고침' 버튼을 클릭하여 마켓 데이터를 수집하세요.")
    
    # 샘플 데이터 로드 시도
    try:
        df = pd.read_csv("polymarket_company_markets.csv")
        st.session_state['markets_df'] = df
        st.success("📁 저장된 데이터를 불러왔습니다.")
    except FileNotFoundError:
        st.warning("저장된 데이터가 없습니다. 먼저 데이터를 수집해주세요.")
        st.stop()
else:
    df = st.session_state['markets_df'].copy()
    
    # 필터 적용
    if filter_insider_only:
        df = df[df['has_insider_potential'] == True]
    
    if selected_companies:
        mask = df['matched_companies'].apply(
            lambda x: any(company in str(x) for company in selected_companies)
        )
        df = df[mask]
    
    # 통계 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 마켓 수", len(df))
    
    with col2:
        insider_count = df['has_insider_potential'].sum() if 'has_insider_potential' in df.columns else 0
        st.metric("정보 우위 가능성", insider_count)
    
    with col3:
        unique_companies = set()
        for companies_str in df['matched_companies'].dropna():
            unique_companies.update(companies_str.split(', '))
        st.metric("관련 기업 수", len(unique_companies))
    
    with col4:
        if 'scraped_at' in df.columns and len(df) > 0:
            latest_scrape = pd.to_datetime(df['scraped_at']).max()
            st.metric("최신 업데이트", latest_scrape.strftime("%Y-%m-%d %H:%M"))
    
    st.divider()
    
    # 기업별 분포 차트
    if len(df) > 0:
        col_chart, col_table = st.columns([2, 1])
        
        with col_chart:
            st.subheader("📈 기업별 마켓 분포")
            
            # 기업별 카운트
            company_counts = {}
            for companies_str in df['matched_companies'].dropna():
                companies = companies_str.split(', ')
                for company in companies:
                    company_counts[company] = company_counts.get(company, 0) + 1
            
            if company_counts:
                company_df = pd.DataFrame({
                    '기업': list(company_counts.keys()),
                    '마켓 수': list(company_counts.values())
                }).sort_values('마켓 수', ascending=False).head(20)
                
                fig = px.bar(
                    company_df,
                    x='마켓 수',
                    y='기업',
                    orientation='h',
                    title="상위 20개 기업",
                    labels={'마켓 수': '마켓 수', '기업': '기업명'}
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        with col_table:
            st.subheader("🏢 기업 목록")
            company_list = sorted(set(company_counts.keys()))
            for company in company_list[:30]:
                st.write(f"- {company} ({company_counts[company]})")
    
    st.divider()
    
    # 마켓 목록
    st.subheader("📋 마켓 목록")
    
    # 정렬 옵션
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_by = st.selectbox("정렬 기준", ["제목", "기업", "정보 우위 가능성"])
    with sort_col2:
        sort_order = st.selectbox("정렬 순서", ["오름차순", "내림차순"])
    
    # 정렬 적용
    if sort_by == "제목":
        df_sorted = df.sort_values('title', ascending=(sort_order == "오름차순"))
    elif sort_by == "기업":
        df_sorted = df.sort_values('matched_companies', ascending=(sort_order == "오름차순"))
    else:
        df_sorted = df.sort_values('has_insider_potential', ascending=(sort_order == "오름차순"))
    
    # 마켓 카드 표시
    for idx, row in df_sorted.iterrows():
        with st.container():
            col_title, col_badge = st.columns([5, 1])
            
            with col_title:
                title = row.get('title', '제목 없음')
                st.markdown(f"### {title}")
            
            with col_badge:
                if row.get('has_insider_potential', False):
                    st.markdown('<span class="insider-badge">🎯 정보 우위</span>', unsafe_allow_html=True)
            
            # 메타 정보
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            
            with meta_col1:
                companies = row.get('matched_companies', 'N/A')
                st.write(f"**관련 기업:** {companies}")
            
            with meta_col2:
                description = row.get('description', '')
                if description:
                    st.write(f"**설명:** {description[:100]}...")
            
            with meta_col3:
                link = row.get('link', '')
                if link:
                    st.markdown(f"[🔗 Polymarket에서 보기]({link})")
                else:
                    st.write("링크 없음")
            
            st.divider()
    
    # 데이터 다운로드
    st.download_button(
        label="📥 CSV 다운로드",
        data=df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'),
        file_name=f"polymarket_company_markets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

