import streamlit as st
import pandas as pd
import numpy as np

# --- 데이터 로드 함수 ---
def get_grammar_data():
    """초등 문법 오류 데이터를 생성하고 DataFrame으로 반환합니다."""
    data = {
        '오류 유형': ['띄어쓰기', '받침 오류', '조사 오류', '되/돼', '안/않'],
        '규칙 설명': [
            '단어는 띄어 쓰는 것이 원칙이에요.',
            '대표적인 받침 소리와 표기를 익혀요.',
            '받침이 없는 단어에는 **는**, 받침이 있는 단어에는 **은**을 붙여요',
            "'되어'의 준말이 '돼'예요. '되어'를 넣어 말이 되면 '돼'를 쓸 수 있어요.",
            "'아니'의 준말이 '안'이에요. '아니하다'의 준말은 '않다'고요."
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
            '그러면 안돼. (안되어)',
            '너는 나한테 미안하지도 않니? (아니하니)'
        ],
        '빈도 (가상)': [25, 15, 10, 45, 40]
    }
    df = pd.DataFrame(data)
    df['ID'] = range(1, len(df) + 1)
    return df

# --- 1. 앱 기본 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="wide")
st.title("👨‍🏫 초등 문법 교정 마스터 봇 🤖")
st.write("초등학생들이 자주 틀리는 문법 실수들을 모아봤어요. 규칙을 익히고 **✅ 확인 여부**를 체크하며 문법 실력을 완성해 보세요!")

# 세션 상태(session_state)에 데이터가 없으면 초기화
if 'grammar_df' not in st.session_state:
    df = get_grammar_data()
    df['확인 여부'] = False  # '확인 여부' 초기값 설정
    st.session_state.grammar_df = df

# --- 2. 문법 오류 차트 및 데이터프레임 탭 ---
st.markdown("---")
st.subheader("📊 학생들이 자주 틀리는 문법 오류 빈도")
st.write("가장 많은 학생들이 실수하는 유형을 차트로 확인해 보세요.")

tab1, tab2 = st.tabs(["오류 빈도 차트", "규칙 전체 보기"])

with tab1:
    chart_data = st.session_state.grammar_df.sort_values(by='빈도 (가상)', ascending=False)
    st.bar_chart(
        chart_data,
        x='오류 유형',
        y='빈도 (가상)',
        color='#FF4B4B',
        height=300
    )

with tab2:
    st.dataframe(
        st.session_state.grammar_df.drop(columns=['확인 여부', 'ID']).set_index('오류 유형'),
        use_container_width=True
    )

# --- 3. 문법 확인 및 체크 기능 (Data Editor) ---
st.markdown("---")
st.subheader("✅ 나의 문법 실력 점검하기")

with st.container(border=True):
    all_error_types = st.session_state.grammar_df['오류 유형'].unique().tolist()

    # 필터링 UI
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        selected_types = st.multiselect(
            "필터링: 내가 궁금한 오류 유형을 선택해 보세요.",
            all_error_types,
            default=all_error_types,
            label_visibility="collapsed"
        )
    with col2:
        # '모두 선택/해제' 버튼 로직
        if st.button('모두 선택', use_container_width=True):
            selected_types = all_error_types
        if st.button('모두 해제', use_container_width=True):
            selected_types = []

    # 선택된 타입으로 데이터 필터링
    filtered_df = st.session_state.grammar_df[st.session_state.grammar_df['오류 유형'].isin(selected_types)]
    st.write(f"**선택된 규칙: {len(filtered_df)}개**")

    # Data Editor 설정
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
            max_value=50, # 최대값을 데이터에 맞게 조정
            width="small"
        ),
        "오류 유형": st.column_config.TextColumn(width="small"),
        "ID": None # ID 컬럼 숨기기
    }

    # data_editor를 사용하여 데이터 수정
    st.markdown("##### ✏️ 규칙을 읽고 이해했으면 체크박스를 눌러보세요!")
    edited_df = st.data_editor(
        filtered_df,
        column_config=config,
        hide_index=True,
        use_container_width=True,
        height=350,
        key="grammar_editor" # 위젯에 고유 key 부여
    )

    # 변경된 내용을 session_state에 다시 업데이트
    # 사용자가 data_editor에서 체크박스를 변경하면, 그 내용(edited_df)을 원본(st.session_state.grammar_df)에 반영
    for index, row in edited_df.iterrows():
        original_index = st.session_state.grammar_df[st.session_state.grammar_df['ID'] == row['ID']].index
        if not original_index.empty:
            st.session_state.grammar_df.loc[original_index, '확인 여부'] = row['확인 여부']


# --- 4. 학습 진행 상황 요약 ---
st.markdown("---")
st.subheader("✨ 나의 학습 진행 상황")

# 전체 데이터 기준으로 진행 상황 계산
total_df = st.session_state.grammar_df
completed_count = total_df['확인 여부'].sum()
total_count = len(total_df)
progress_ratio = completed_count / total_count if total_count > 0 else 0

col_left, col_right = st.columns([1, 2])

with col_left:
    delta_text = f"{progress_ratio * 100:.0f}% 완료"
    st.metric(
        label="완료된 규칙 수",
        value=f"{completed_count} / {total_count}개",
        delta=delta_text if progress_ratio < 1 else "성공! 🎉"
    )

with col_right:
    st.progress(progress_ratio, text=f"규칙 학습 진행률: {progress_ratio * 100:.0f}%")

    if progress_ratio == 1.0 and total_count > 0:
        st.balloons()
        st.success("🎉 축하합니다! 모든 규칙을 마스터했어요!")
    elif progress_ratio > 0:
        st.info("다음 규칙들을 정복해 봐요. 조금만 더 힘내세요!")
    else:
        st.warning("아직 확인한 규칙이 없네요. 위에 있는 체크박스를 눌러 학습을 시작해 보세요!")
