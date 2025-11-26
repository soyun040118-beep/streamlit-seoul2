import streamlit as st
import pandas as pd
import numpy as np

# --- 1. 앱 기본 설정 ---
st.set_page_config(layout="wide")
st.title("👨‍🏫 초등 문법 교정 마스터 봇 🤖")
st.write("초등학생들이 자주 틀리는 문법 실수들을 모아봤어요. 규칙을 익히고 **✅ 확인 여부**를 체크하며 문법 실력을 완성해 보세요!")

# --- 2. 오류 데이터 생성 (사용자가 자주 틀리는 문법 데이터) ---
# Mock data for common Korean elementary school grammar errors
data = {
    '오류 유형': ['띄어쓰기', '받침 오류', '조사 오류', '되/돼', '안/않'],
    '규칙 설명': [
        '단어는 띄어 쓰는 것이 원칙이에요.', 
        '대표적인 받침 소리와 표기를 익혀요.', 
        '받침이 없는 단어에는 **는**, 받침이 있는 단어에는 **은**을 붙여요', 
        '상황에 맞게 되/돼를 쓸 수 있어요.',
        '상황에 맞게 안/않을 쓸 수 있어요.'
    ],
    '예시 (틀린 문장)': [
        '아버지가방에 들어가신다.', 
        '꼬치 이쁘다.', 
        '나은 사과를 먹었다.', 
        '그러면 안되.',
        '너는 나한테 미안하지도 안니?'
    ],
    '예시 (맞는 문장)': [
        '아버지가 방에 들어가신다.', 
        '꽃이 예쁘다.', 
        '나는 사과를 먹었다.',
        '그러면 안돼.',
        '너는 나한테 미안하지도 않니?'
    ],
    '빈도 (가상)': [20, 10, 5, 45, 40]
}

# Create DataFrame
grammar_df = pd.DataFrame(data)

# Add a boolean column for the student to check their confirmation status (초기값은 모두 False)
grammar_df['확인 여부'] = False
# Add a simple ID for filtering/display
grammar_df['ID'] = range(1, len(grammar_df) + 1)


# --- 3. 문법 오류 차트 및 데이터프레임 탭 ---
st.markdown("---")
st.subheader("📊 학생들이 자주 틀리는 문법 오류 빈도")
st.write("가장 많은 학생들이 실수하는 유형을 차트로 확인해 보세요.")

# Tabs for Chart and Raw Data
tab1, tab2 = st.tabs(["오류 빈도 차트", "규칙 전체 보기"])

with tab1:
    # Use the '빈도 (가상)' column to show frequency
    chart_data = grammar_df.sort_values(by='빈도 (가상)', ascending=False)
    st.bar_chart(
        chart_data, 
        x='오류 유형', 
        y='빈도 (가상)', 
        color='#FF4B4B', 
        height=300
        
    )

with tab2:
    # Display the full list of rules in the second tab
    st.dataframe(grammar_df.drop(columns=['확인 여부', 'ID']).set_index('오류 유형'), use_container_width=True)


# --- 4. 문법 확인 및 체크 기능 (Data Editor) ---
st.markdown("---")
st.subheader("✅ 나의 문법 실력 점검하기")

with st.container(border=True):
    # **자신이 아는 문법 확인 (필터링 기능)**
    all_error_types = grammar_df['오류 유형'].unique().tolist()
    selected_types = st.multiselect(
        "필터링: 내가 궁금한 오류 유형을 선택해 보세요.", 
        all_error_types, 
        default=all_error_types
    )
    
    # Apply filter
    filtered_df = grammar_df[grammar_df['오류 유형'].isin(selected_types)]

    st.write(f"**선택된 규칙: {len(filtered_df)}개**")

# Data Editor Configuration - Using CheckboxColumn for the 'Check' function
config = {
    "확인 여부": st.column_config.CheckboxColumn(
        "✅ 확인했어요!",
        help="이 규칙을 완벽하게 이해했으면 체크하세요.",
        default=False,
    ),
    "빈도 (가상)": st.column_config.ProgressColumn(
        "⚠️ 오류 빈도",
        help="학생들이 자주 틀리는 정도 (높을수록 중요!)",
        format="%d",
        min_value=0,
        max_value=40,
        width="small"
    ),
    "오류 유형": st.column_config.TextColumn(width="small"),
    "ID": None # Hide the ID column
}

# The Interactive Data Editor
st.markdown("##### ✏️ 규칙을 읽고 이해했으면 체크박스를 눌러보세요!")
edited_data = st.data_editor(
    filtered_df,
    column_config=config,
    hide_index=True,
    use_container_width=True,
    height=300
)

# --- 5. 학습 진행 상황 요약 ---
st.markdown("---")
# Calculate progress from the edited data
completed_count = edited_data['확인 여부'].sum()
total_count = len(edited_data)
progress_ratio = completed_count / total_count if total_count > 0 else 0

st.subheader("✨ 나의 학습 진행 상황")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.metric(
        label="완료된 규칙 수",
        value=f"{completed_count} / {total_count}개",
        delta=f"진행률: {progress_ratio * 100:.0f}%"
    )

with col_right:
    # Display progress
    st.progress(progress_ratio, text=f"규칙 학습 진행률: {progress_ratio * 100:.0f}%")

    if progress_ratio == 1.0 and total_count > 0:
        st.balloons()
        st.success("🎉 축하합니다! 모든 규칙을 마스터했어요!")
    elif progress_ratio > 0:
        st.info("다음 규칙들을 정복해 봐요. 조금만 더 힘내세요!")
    else:
        st.warning("아직 확인한 규칙이 없네요. 위에 있는 체크박스를 눌러 학습을 시작해 보세요!")
