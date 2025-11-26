import streamlit as st
import pandas as pd
import random
import os
from dotenv import load_dotenv
import numpy as np

# --- 데이터 로드 함수 ---
def get_grammar_data():
    """초등 문법 오류 데이터를 생성하고 DataFrame으로 반환합니다."""
    data = {
        '오류 유형': ['데/대', '에요/예요', '어떡해/어떻게', '되/돼', '안/않'],
        '규칙 설명': [
            '데/대는 의미가 비슷한 다른 말을 정확히 구분해서 사용해요.',
            '앞에 오는 단어에 받침이 있으면 **이에요**, 받침이 없으면 **예요**를 붙여요.',
            '"어떻게"는 "어떠하게"의 준말이고 "어떡해"는 어떻게 하여서의 준말입니다.',
            "'되어'의 준말이 '돼'예요. '되어'를 넣어 말이 되면 '돼'를 쓸 수 있어요.",
            "'아니'의 준말이 '안'이에요. '아니하다'의 준말은 '않다'고요."
        ],
        '예시 (틀린 문장)': [
            '졸업식이 일주일 연기됐데',
            '저는 학생예요.',
            '어떡해 나한테 그럴 수 있어?',
            '그러면 안되.',
            '너는 나한테 미안하지도 안니?'
        ],
        '예시 (맞는 문장)': [
            '졸업식이 일주일 연기됐대.',
            '저는 학생이에요.',
            '어떻게 나한테 그럴 수 있어?',
            '그러면 안돼. (안되어)',
            '너는 나한테 미안하지도 않니? (아니하니)'
        ],
        '빈도 (가상)': [25, 15, 10, 45, 40]
    }
    df = pd.DataFrame(data)
    df['ID'] = range(1, len(df) + 1)
    return df

# --- 퀴즈 데이터 로드 함수 ---
def get_quiz_data():
    """오류 유형별로 다양한 객관식 퀴즈 문제를 생성하고 DataFrame으로 반환합니다."""
    quiz_data = [
        # 데/대
        {'오류 유형': '데/대', '문제': '그 영화 정말 재미있[데/대].', '정답': '그 영화 정말 재미있대.', '오답들': ['그 영화 정말 재미있데.']},
        {'오류 유형': '데/대', '문제': '어제 가 보니 정말 좋[데/대].', '정답': '어제 가 보니 정말 좋데.', '오답들': ['어제 가 보니 정말 좋대.']},
        {'오류 유형': '데/대', '문제': '친구가 오늘 시험이[데/대].', '정답': '친구가 오늘 시험이래.', '오답들': ['친구가 오늘 시험이레.']},
        # 에요/예요
        {'오류 유형': '에요/예요', '문제': '이건 제 책[이에요/예요].', '정답': '이건 제 책이에요.', '오답들': ['이건 제 책예요.']},
        {'오류 유형': '에요/예요', '문제': '아니[에요/예요]. 괜찮아요.', '정답': '아니에요. 괜찮아요.', '오답들': ['아니예요. 괜찮아요.']},
        {'오류 유형': '에요/예요', '문제': '이 사과는 얼마[에요/예요]?', '정답': '이 사과는 얼마예요?', '오답들': ['이 사과는 얼마에요?']},
        # 어떡해/어떻게
        {'오류 유형': '어떡해/어떻게', '문제': '이 문제를 [어떡해/어떻게] 풀지?', '정답': '이 문제를 어떻게 풀지?', '오답들': ['이 문제를 어떡해 풀지?']},
        {'오류 유형': '어떡해/어떻게', '문제': '지갑을 잃어버렸어. [어떡해/어떻게]!', '정답': '지갑을 잃어버렸어. 어떡해!', '오답들': ['지갑을 잃어버렸어. 어떻게!']},
        {'오류 유형': '어떡해/어떻게', '문제': '너 집에 [어떡해/어떻게] 가?', '정답': '너 집에 어떻게 가?', '오답들': ['너 집에 어떡해 가?']},
        # 되/돼
        {'오류 유형': '되/돼', '문제': '그러면 안 [되/돼].', '정답': '그러면 안 돼.', '오답들': ['그러면 안 되.']},
        {'오류 유형': '되/돼', '문제': '이제 가도 [되/돼]나요?', '정답': '이제 가도 되나요?', '오답들': ['이제 가도 돼나요?']},
        {'오류 유형': '되/돼', '문제': '의사가 [되/돼]고 싶어요.', '정답': '의사가 되고 싶어요.', '오답들': ['의사가 돼고 싶어요.']},
        # 안/않
        {'오류 유형': '안/않', '문제': '너는 나한테 미안하지도 [안/않]니?', '정답': '너는 나한테 미안하지도 않니?', '오답들': ['너는 나한테 미안하지도 안니?']},
        {'오류 유형': '안/않', '문제': '숙제를 아직 [안/않] 했다.', '정답': '숙제를 아직 안 했다.', '오답들': ['숙제를 아직 않 했다.']},
        {'오류 유형': '안/않', '문제': '그렇게 하면 [안/않]돼.', '정답': '그렇게 하면 안돼.', '오답들': ['그렇게 하면 않돼.']},
    ]
    return pd.DataFrame(quiz_data)

# --- 환경 변수 로드 ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- 1. 앱 기본 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="wide")

# --- 사이드바 마스코트 ---
with st.sidebar:
    st.image("https://i.imgur.com/4sGo6va.png", width=150)
    st.info("안녕하세요! 저는 맞춤법 요정 '맞춤이'에요. 함께 즐겁게 문법을 배워봐요! ✨")
    
    # API 키 로드 상태 표시
    st.markdown("---")
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "여기에 실제 구글 API 키를 입력하세요":
        st.success("API 키가 준비됐어요! 🤖")
    else:
        st.warning("API 키가 필요해요! 🔑")

col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("👨‍🏫 알쏭달쏭 문법 교실 🤖")
    st.write("초등학생들이 자주 헷갈리는 문법들을 모았어요. 규칙을 익히고 퀴즈를 풀며 문법 실력을 키워봐요!")
with col2:
    st.image("https://i.imgur.com/VpA2pT4.png", width=150)

# 세션 상태(session_state)에 데이터가 없으면 초기화
if 'grammar_df' not in st.session_state:
    df = get_grammar_data()
    df['확인 여부'] = False  # '확인 여부' 초기값 설정
    st.session_state.grammar_df = df
    st.session_state.quiz_df = get_quiz_data() # 퀴즈 데이터 로드
    # 퀴즈 기록을 위한 session_state 초기화
    if 'quiz_history' not in st.session_state:
        st.session_state.quiz_history = []
    if 'incorrect_questions' not in st.session_state:
        st.session_state.incorrect_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'retry_mode' not in st.session_state:
        st.session_state.retry_mode = False
    if 'current_retry_index' not in st.session_state:
        st.session_state.current_retry_index = 0

# --- 2. 문법 오류 차트 및 데이터프레임 탭 ---
st.markdown("---")
st.subheader("📊 친구들이 가장 많이 헷갈려요!")
st.write("어떤 문법을 가장 많이 틀리는지 차트로 확인하고, 중요한 규칙부터 공부해 보세요.")

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
st.subheader("✅ 꼼꼼히 확인하고 레벨 업!")

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
st.subheader("✨ 나의 학습 리포트")

# 전체 데이터 기준으로 진행 상황 계산
total_df = st.session_state.grammar_df
completed_count = total_df['확인 여부'].sum()
total_count = len(total_df)
progress_ratio = completed_count / total_count if total_count > 0 else 0

with st.container(border=True):
    col1, col2 = st.columns([1, 2])

    with col1:
        delta_text = f"{progress_ratio * 100:.0f}% 완료"
        st.metric(
            label="나의 학습 점수",
            value=f"{completed_count * 20} 점",
            delta=f"{completed_count} / {total_count}개 확인!" if progress_ratio < 1 else "만점! 🎉"
        )

    with col2:
        st.progress(progress_ratio, text=f"규칙 학습 진행률: {progress_ratio * 100:.0f}%")

    if progress_ratio == 1.0:
        st.balloons()
        st.success("🎉 축하합니다! 모든 규칙을 마스터했어요!")
    elif progress_ratio > 0:
        st.info("다음 규칙들을 정복해 봐요. 조금만 더 힘내세요!")
    else:
        st.warning("아직 확인한 규칙이 없네요. 위에 있는 체크박스를 눌러 학습을 시작해 보세요!")

# --- 5. 문법 퀴즈 및 오답 분석 ---
st.markdown("---")
st.subheader("📝 도전! 문법 퀴즈")

def generate_question(retry=False):
    """퀴즈 문제를 생성합니다. retry 모드에서는 오답 목록에서 문제를 가져옵니다."""
    if retry:
        # 오답 목록에서 None이 아닌 다음 문제를 찾음
        while st.session_state.current_retry_index < len(st.session_state.incorrect_questions) and st.session_state.incorrect_questions[st.session_state.current_retry_index] is None:
            st.session_state.current_retry_index += 1

        if st.session_state.current_retry_index < len(st.session_state.incorrect_questions):
            question = st.session_state.incorrect_questions[st.session_state.current_retry_index]
            st.session_state.current_question = question
        else: # 모든 오답 문제를 다 푼 경우
            st.success("🎉 축하합니다! 모든 오답을 정복했어요!")
            st.session_state.retry_mode = False
            st.session_state.current_question = None
            st.session_state.current_retry_index = 0
            st.session_state.incorrect_questions = [] # 오답 목록 초기화
    else:
        # 일반 퀴즈 모드: 퀴즈 데이터에서 문제 샘플링
        quiz_question_series = st.session_state.quiz_df.sample(1).iloc[0]
        rule_info_series = st.session_state.grammar_df[st.session_state.grammar_df['오류 유형'] == quiz_question_series['오류 유형']].iloc[0]
        
        question_data = quiz_question_series.to_dict()
        question_data['규칙 설명'] = rule_info_series['규칙 설명']
        st.session_state.current_question = question_data

# 퀴즈 모드에 따라 제목 변경
quiz_title = "오답 다시 풀어보기" if st.session_state.retry_mode else "나의 문법 실력 최종 점검! (퀴즈)"
with st.container(border=True):
    st.write("아래 버튼을 눌러 나의 문법 실력을 테스트해 보세요. 올바른 문장을 선택하면 됩니다.")

    if st.button("🎲 새로운 퀴즈 풀기!", use_container_width=True):
        # 오답 모드가 아니거나, 오답이 없을 때만 일반 퀴즈 시작
        if not any(q is not None for q in st.session_state.incorrect_questions):
            st.session_state.retry_mode = False

        if st.session_state.retry_mode:
            st.session_state.current_retry_index += 1

        generate_question(st.session_state.retry_mode)
        # 이전 답변 결과 메시지 초기화
        if 'answer_feedback' in st.session_state:
            del st.session_state.answer_feedback

    # 문제가 생성되었을 경우 퀴즈 UI 표시
    if st.session_state.current_question is not None:
        question_data = st.session_state.current_question
        st.markdown(f"**문제:** 다음 중 문법적으로 올바른 문장을 고르세요.")
        st.info(f"#### {question_data['문제']}")

        with st.form(key="quiz_form"):
            # 선택지 생성 및 섞기
            options = question_data['오답들'] + [question_data['정답']]
            random.shuffle(options)
            
            user_answer = st.radio("선택지:", options, index=None, key=f"quiz_{question_data['문제']}")
            submit_button = st.form_submit_button("정답 제출")

            if submit_button:
                if user_answer is None:
                    st.warning("답을 선택해 주세요!")
                else:
                    is_correct = (user_answer == question_data['정답'])

                    if is_correct:
                        st.session_state.answer_feedback = "correct"
                        # 오답 모드에서 정답을 맞히면 해당 문제 제거
                        if st.session_state.retry_mode:
                            st.session_state.incorrect_questions[st.session_state.current_retry_index] = None
                    else:
                        st.session_state.answer_feedback = "incorrect"
                        # 오답 기록
                        st.session_state.quiz_history.append(question_data['오류 유형'])
                        # 중복되지 않게 오답 목록에 추가
                        is_duplicate = any(q is not None and q['문제'] == question_data['문제'] for q in st.session_state.incorrect_questions)
                        if not is_duplicate and not st.session_state.retry_mode:
                            st.session_state.incorrect_questions.append(question_data)

        # 정답 제출 후 피드백 표시
        if 'answer_feedback' in st.session_state:
            if st.session_state.answer_feedback == "correct":
                st.success("🎉 정답입니다! 정말 잘했어요!")
                st.balloons()
            elif st.session_state.answer_feedback == "incorrect":
                question_data = st.session_state.current_question
                st.error(f"아쉬워요, 정답은 **'{question_data['정답']}'** 입니다.")
                with st.expander("🔍 왜 틀렸을까요? (규칙 확인)"):
                    st.write(f"**오류 유형:** {question_data['오류 유형']}")
                    st.write(f"**규칙:** {question_data['규칙 설명']}")

# --- 6. 오답 유형 분석 및 추천 ---
if st.session_state.quiz_history:
    st.markdown("---")
    st.subheader("📈 나의 약점 분석!")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("##### 📊 오답 유형 분포")
            incorrect_df = pd.DataFrame(st.session_state.quiz_history, columns=['오류 유형'])
            chart_data = incorrect_df['오류 유형'].value_counts()
            st.bar_chart(chart_data, color="#FF4B4B")

    with col2:
        with st.container(border=True):
            st.markdown("##### 💡 가장 많이 틀린 유형 다시보기")
            if not chart_data.empty:
                most_common_error = chart_data.index[0]
                st.warning(f"**'{most_common_error}'** 유형을 가장 많이 틀렸어요. 아래 규칙을 다시 한번 확인해 보세요!")

                # 해당 규칙 정보 가져오기
                rule_info = st.session_state.grammar_df[st.session_state.grammar_df['오류 유형'] == most_common_error].iloc[0]
                st.info(f"**규칙:** {rule_info['규칙 설명']}")
                st.write(f"**예시:** '{rule_info['예시 (틀린 문장)']}' ➡️ '{rule_info['예시 (맞는 문장)']}'")
            else:
                st.write("아직 기록된 오답이 없습니다.")

# --- 7. 오답 노트 및 다시 풀기 기능 ---
if any(q is not None for q in st.session_state.get('incorrect_questions', [])):
    st.markdown("---")
    st.subheader("📓 나만의 비밀 오답 노트")

    with st.container(border=True):
        st.write("퀴즈에서 틀렸던 문제들이에요. '오답 정복하기' 버튼을 눌러 다시 풀어봐요!")

        # 오답 목록 표시
        for i, q in enumerate(st.session_state.incorrect_questions):
            if q is None: # 이미 맞힌 문제는 건너뛰기
                continue
            st.markdown(f"**{i+1}. [{q['오류 유형']}]** {q['문제']}")

        if st.button("✍️ 오답 정복하기!", type="primary", use_container_width=True):
            st.session_state.retry_mode = True
            st.session_state.current_retry_index = 0
            generate_question(retry=True)
            # 피드백 초기화 및 페이지 새로고침
            if 'answer_feedback' in st.session_state:
                del st.session_state.answer_feedback
            st.rerun()

        if st.session_state.retry_mode:
            st.info("오답 퀴즈 모드가 활성화되었습니다. 상단의 퀴즈 섹션에서 문제를 풀어주세요.")
