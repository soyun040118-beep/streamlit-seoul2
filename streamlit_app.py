import streamlit as st
import pandas as pd
import random
import time
import os
from dotenv import load_dotenv
import numpy as np

# --- 데이터 로드 함수 ---
def get_grammar_data():
    """초등 문법 오류 데이터를 생성하고 DataFrame으로 반환합니다."""
    data = {
        '오류 유형': ['데/대', '에요/예요', '어떡해/어떻게', '되/돼', '안/않'],
        '규칙 설명': [
            "'데'는 직접 경험한 사실을, '대'는 다른 사람에게 들은 내용을 전달할 때 사용해요.",
            '받침이 있으면 **\'이에요\'**, 받침이 없으면 **\'예요\'**를 써요. 하지만 **\'아니다\'**는 무조건 **\'아니에요\'**가 맞아요! (줄여서 \'아녜요\'도 O) 그 이유가 궁금한 학생은 선생님과 함께 탐구해볼까요?',
            "'어떻게'는 '어떠하게'의 준말로 방법을 물을 때 쓰고, '어떡해'는 '어떻게 해'의 준말로 걱정되는 상황에서 사용해요.",
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
        {'오류 유형': '데/대', '문제': '그 영화 정말 재미있[데/대]. (남에게 들음)', '정답': '그 영화 정말 재미있대.', '오답들': ['그 영화 정말 재미있데.']},
        {'오류 유형': '데/대', '문제': '이제 가 보니 정말 좋[데/대] (간접 경험)', '정답': '이제 가 보니 정말 좋대.', '오답들': ['이제 가 보니 정말 좋데.']},
        {'오류 유형': '데/대', '문제': '친구가 오늘 시험이[래/레].', '정답': '친구가 오늘 시험이래.', '오답들': ['친구가 오늘 시험이레.']},
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
# Streamlit Cloud와 로컬 환경 모두 지원
try:
    # Streamlit Cloud의 secrets에서 먼저 시도
    if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
        GOOGLE_API_KEY = st.secrets['GOOGLE_API_KEY']
    else:
        # 로컬 환경: .env 파일에서 환경 변수 로드
        env_paths = []
        try:
            # 현재 파일의 디렉토리
            env_paths.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
        except:
            pass

        # 현재 작업 디렉토리
        env_paths.append('.env')
        env_paths.append(os.path.join(os.getcwd(), '.env'))

        # .env 파일 찾아서 로드
        loaded = False
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path, override=True)
                loaded = True
                break

        # 모든 경로에서 찾지 못한 경우 기본 로드 시도
        if not loaded:
            load_dotenv()
        
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
except:
    # 폴백: 환경 변수에서 직접 가져오기
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- 1. 앱 기본 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="wide")

# --- 사이드바 마스코트 ---
with st.sidebar:
    st.info("안녕하세요! 저는 맞춤법 요정 '맞춤이'에요. 함께 즐겁게 문법을 배워봐요! ✨")
    
    # API 키 로드 상태 표시
    st.markdown("---")
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "여기에 실제 구글 API 키를 입력하세요":
        st.success("API 키가 준비됐어요! 🤖")
    else:
        st.warning("API 키가 필요해요! 🔑")

st.title("👨‍🏫 알쏭달쏭 문법 교실 🤖")
st.write("평소에 친구들과 대화할 때 알쏭달쏭한 문법이 있지는 않았나요? 규칙을 익히고 퀴즈를 풀며 문법 실력을 키워봐요!")

# 세션 상태(session_state)에 데이터가 없으면 초기화
if 'grammar_df' not in st.session_state:
    st.session_state.grammar_df = get_grammar_data()
    st.session_state.quiz_df = get_quiz_data() # 퀴즈 데이터 로드

    # 레벨업 퀴즈 상태 초기화
    levelup_quiz = []
    for error_type in st.session_state.grammar_df['오류 유형']:
        # 각 오류 유형별로 퀴즈 데이터에서 하나의 문제를 선택
        question = st.session_state.quiz_df[st.session_state.quiz_df['오류 유형'] == error_type].sample(1).iloc[0].to_dict()
        question['user_answer'] = None
        question['correct'] = False
        levelup_quiz.append(question)
    st.session_state.levelup_quiz = levelup_quiz
    st.session_state.levelup_submitted = False

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

# --- 2. 문법 오류 차트 ---
st.markdown("---")
st.subheader("📊 친구들이 가장 많이 헷갈려요!")
st.write("어떤 문법을 가장 많이 틀리는지 차트로 확인하고, 중요한 규칙부터 공부해 보세요.")

# 오류 빈도 차트
chart_data = st.session_state.grammar_df.sort_values(by='빈도 (가상)', ascending=False)
st.bar_chart(
    chart_data,
    x='오류 유형',
    y='빈도 (가상)',
    color='#FF4B4B',
    height=300
)

# --- 2-1. 규칙 전체 보기 (개선된 가독성) ---
st.markdown("---")
st.subheader("📚 문법 규칙 전체 보기")
st.write("각 문법 규칙을 자세히 확인하고 예시를 통해 이해해 보세요.")

# 각 규칙을 카드 형태로 표시하여 가독성 향상
for idx, row in st.session_state.grammar_df.iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"### {row['오류 유형']}")
            st.metric("오류 빈도", f"{row['빈도 (가상)']}회")
        
        with col2:
            st.markdown("#### 📖 규칙 설명")
            st.info(row['규칙 설명'])
            
            st.markdown("#### ✍️ 예시")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.error(f"**틀린 문장:**\n{row['예시 (틀린 문장)']}")
            with col_ex2:
                st.success(f"**맞는 문장:**\n{row['예시 (맞는 문장)']}")
    
    st.markdown("")  # 간격 추가

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

        # 선택지 생성 및 섞기 (매번 동일하게 섞이도록 시드 고정)
        question_id = hash(question_data['문제'])
        random.seed(question_id)
        options = question_data['오답들'] + [question_data['정답']]
        random.shuffle(options)
        
        # 폼 키를 문제별로 고유하게 생성
        form_key = f"quiz_form_{question_id}"
        radio_key = f"quiz_radio_{question_id}"
        
        # 이미 제출된 답변이 있는지 확인
        submitted_answer = st.session_state.get(f"submitted_answer_{question_id}", None)
        is_submitted = st.session_state.get(f"is_submitted_{question_id}", False)
        
        with st.form(key=form_key):
            # 제출된 답변이 있으면 해당 답변을 기본값으로 설정
            default_index = None
            if submitted_answer and submitted_answer in options:
                default_index = options.index(submitted_answer)
            
            user_answer = st.radio("선택지:", options, index=default_index, key=radio_key)
            submit_button = st.form_submit_button("정답 제출")

            if submit_button:
                # 폼 제출 시점에 radio 값이 None일 수 있으므로 session_state에서 직접 확인
                # st.radio는 폼 안에서 사용될 때 key를 통해 session_state에 값을 저장합니다
                radio_value = st.session_state.get(radio_key, None)
                
                # user_answer가 None이면 session_state에서 가져오기
                final_answer = user_answer if user_answer is not None else radio_value
                
                # 여전히 None이면 경고
                if final_answer is None:
                    st.warning("답을 선택해 주세요!")
                else:
                    # 최종 답변 사용
                    user_answer = final_answer
                    # 답변을 session_state에 저장
                    st.session_state[f"submitted_answer_{question_id}"] = user_answer
                    st.session_state[f"is_submitted_{question_id}"] = True
                    
                    # 정답 여부 확인 (문자열 비교를 정확하게 - 공백 제거 및 정규화)
                    user_ans_clean = str(user_answer).strip()
                    correct_ans_clean = str(question_data['정답']).strip()
                    is_correct = (user_ans_clean == correct_ans_clean)
                    
                    # 디버깅용 (필요시 주석 해제)
                    # st.write(f"디버그: 선택한 답='{user_ans_clean}', 정답='{correct_ans_clean}', 일치={is_correct}")

                    if is_correct:
                        st.session_state.answer_feedback = "correct"
                        st.session_state.answer_feedback_question_id = question_id
                        if st.session_state.retry_mode:
                            st.session_state.incorrect_questions[st.session_state.current_retry_index] = None
                        # 정답일 때 풍선 표시 후 빠르게 다음 문제로 이동 (1초 후)
                        st.session_state[f"auto_next_question_{question_id}"] = True
                        st.session_state[f"auto_next_timer_{question_id}"] = time.time()
                        st.session_state[f"auto_next_delay_{question_id}"] = 1.0  # 1초 딜레이
                    else:
                        st.session_state.answer_feedback = "incorrect"
                        st.session_state.answer_feedback_question_id = question_id
                        # 오답 기록
                        st.session_state.quiz_history.append(question_data['오류 유형'])
                        # 중복되지 않게 오답 목록에 추가
                        is_duplicate = any(
                            q is not None and 
                            q.get('문제') == question_data.get('문제') 
                            for q in st.session_state.incorrect_questions
                        )
                        if not is_duplicate and not st.session_state.retry_mode:
                            # 오답 문제를 복사해서 저장 (원본 데이터 보존)
                            incorrect_q = question_data.copy()
                            incorrect_q['user_wrong_answer'] = user_answer
                            st.session_state.incorrect_questions.append(incorrect_q)
                        # 오답일 때도 자동으로 다음 문제로 이동 (3초 후)
                        st.session_state[f"auto_next_question_{question_id}"] = True
                        st.session_state[f"auto_next_timer_{question_id}"] = time.time()

        # 정답 제출 후 피드백 표시 (같은 문제에 대해서만)
        if is_submitted and st.session_state.get('answer_feedback_question_id') == question_id:
            if st.session_state.answer_feedback == "correct":
                st.success("🎉 정답입니다!")
                st.balloons()
                # 정답일 때 빠르게 다음 문제로 넘어가기 (1초 후)
                auto_next_key = f"auto_next_question_{question_id}"
                timer_key = f"auto_next_timer_{question_id}"
                delay_key = f"auto_next_delay_{question_id}"
                if st.session_state.get(auto_next_key, False):
                    elapsed = time.time() - st.session_state.get(timer_key, time.time())
                    delay = st.session_state.get(delay_key, 1.0)
                    remaining = max(0, delay - elapsed)
                    if remaining > 0:
                        # 자동으로 다시 렌더링하여 다음 문제로 이동
                        st.rerun()
                    else:
                        # 시간이 지나면 다음 문제로 이동
                        st.session_state[f"is_submitted_{question_id}"] = False
                        st.session_state[f"submitted_answer_{question_id}"] = None
                        st.session_state[auto_next_key] = False
                        if timer_key in st.session_state:
                            del st.session_state[timer_key]
                        if delay_key in st.session_state:
                            del st.session_state[delay_key]
                        generate_question(st.session_state.retry_mode)
                        st.rerun()
            elif st.session_state.answer_feedback == "incorrect":
                st.error(f"❌ 아쉬워요, 정답은 **'{question_data['정답']}'** 입니다.")
                if submitted_answer:
                    st.warning(f"선택하신 답: **'{submitted_answer}'**")
                
                with st.expander("🔍 왜 틀렸을까요? (규칙 확인)", expanded=True):
                    st.markdown(f"##### 💡 **{question_data['오류 유형']}** 규칙")
                    with st.container(border=True):
                        st.info(f"**규칙:** {question_data['규칙 설명']}")
                        # 예시 문장 추가
                        st.success(f"**올바른 예시:** {question_data['정답']}")
                        st.error(f"**틀린 예시:** {question_data['오답들'][0] if question_data['오답들'] else ''}")
                
                # 자동으로 다음 문제로 넘어가기 (3초 후)
                auto_next_key = f"auto_next_question_{question_id}"
                timer_key = f"auto_next_timer_{question_id}"
                if st.session_state.get(auto_next_key, False):
                    elapsed = time.time() - st.session_state.get(timer_key, time.time())
                    remaining = max(0, 3 - int(elapsed))
                    if remaining > 0:
                        st.info(f"⏱️ {remaining}초 후 자동으로 다음 문제로 넘어갑니다...")
                        # 자동으로 다시 렌더링하여 카운트다운 업데이트
                        st.rerun()
                    else:
                        # 시간이 지나면 다음 문제로 이동
                        st.session_state[f"is_submitted_{question_id}"] = False
                        st.session_state[f"submitted_answer_{question_id}"] = None
                        st.session_state[auto_next_key] = False
                        if timer_key in st.session_state:
                            del st.session_state[timer_key]
                        generate_question(st.session_state.retry_mode)
                        st.rerun()

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
                with st.container(border=True):
                    st.info(f"**규칙:** {rule_info['규칙 설명']}")
                    st.success(f"**올바른 예시:** {rule_info['예시 (맞는 문장)']}")
                    st.error(f"**틀린 예시:** {rule_info['예시 (틀린 문장)']}")
            else:
                st.write("아직 기록된 오답이 없습니다.")

# --- 7. 오답 노트 및 다시 풀기 기능 ---
incorrect_count = sum(1 for q in st.session_state.get('incorrect_questions', []) if q is not None)
if incorrect_count > 0:
    st.markdown("---")
    st.subheader("📓 나만의 비밀 오답 노트")
    
    with st.container(border=True):
        st.write(f"퀴즈에서 틀렸던 문제 **{incorrect_count}개**가 있어요. '오답 정복하기' 버튼을 눌러 다시 풀어봐요!")
        
        # 오답 목록을 더 자세하게 표시
        with st.expander(f"📋 오답 목록 보기 ({incorrect_count}개)", expanded=False):
            for i, q in enumerate(st.session_state.incorrect_questions):
                if q is None: # 이미 맞힌 문제는 건너뛰기
                    continue
                with st.container(border=True):
                    st.markdown(f"**{i+1}. [{q['오류 유형']}]** {q['문제']}")
                    st.write(f"**정답:** {q['정답']}")
                    if 'user_wrong_answer' in q:
                        st.write(f"**내가 선택한 답:** ~~{q['user_wrong_answer']}~~ ❌")
                    st.caption(f"규칙: {q.get('규칙 설명', '')[:50]}...")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✍️ 오답 정복하기!", type="primary", use_container_width=True):
                st.session_state.retry_mode = True
                st.session_state.current_retry_index = 0
                # 첫 번째 오답 문제로 이동
                while (st.session_state.current_retry_index < len(st.session_state.incorrect_questions) and 
                       st.session_state.incorrect_questions[st.session_state.current_retry_index] is None):
                    st.session_state.current_retry_index += 1
                generate_question(retry=True)
                # 피드백 초기화 및 페이지 새로고침
                if 'answer_feedback' in st.session_state:
                    del st.session_state.answer_feedback
                st.rerun()
        
        with col2:
            if st.button("🗑️ 오답 노트 초기화", use_container_width=True):
                st.session_state.incorrect_questions = []
                st.session_state.quiz_history = []
                st.session_state.retry_mode = False
                st.session_state.current_retry_index = 0
                st.session_state.current_question = None
                if 'answer_feedback' in st.session_state:
                    del st.session_state.answer_feedback
                st.success("오답 노트가 초기화되었습니다!")
                st.rerun()

        if st.session_state.retry_mode:
            st.info("💡 오답 퀴즈 모드가 활성화되었습니다. 상단의 퀴즈 섹션에서 문제를 풀어주세요.")

# --- 3. (구) -> (신) 꼼꼼히 확인하고 레벨 업! (위치 이동 및 기능 변경) ---
st.markdown("---")
st.subheader("✅ 꼼꼼히 확인하고 레벨 업!")
st.info("각 문법 규칙을 잘 이해했는지 확인 퀴즈를 통해 점검해 보세요. 모든 문제를 맞혀야 학습 진도율 100%를 달성할 수 있어요!")

# 레벨업 퀴즈 폼
form_key = "levelup_quiz_form"
with st.form(form_key, clear_on_submit=False):
    for i, q in enumerate(st.session_state.levelup_quiz):
        st.markdown(f"**Q{i+1}. [{q['오류 유형']}] 유형 확인 문제**")
        
        # 규칙 설명 Expander
        with st.expander("🤔 관련 규칙 보기"):
            rule_info = st.session_state.grammar_df.loc[st.session_state.grammar_df['오류 유형'] == q['오류 유형']].iloc[0]
            with st.container(border=True):
                st.info(f"**규칙:** {rule_info['규칙 설명']}")
                st.success(f"**올바른 예시:** {rule_info['예시 (맞는 문장)']}")
                st.error(f"**틀린 예시:** {rule_info['예시 (틀린 문장)']}")

        # 선택지 생성 및 섞기 (문제별로 고정된 시드 사용)
        random.seed(i + hash(q['문제']))
        options = q['오답들'] + [q['정답']]
        random.shuffle(options)
        
        # 현재 저장된 답변이 있으면 표시
        current_answer = st.session_state.levelup_quiz[i].get('user_answer', None)
        default_index = None
        if current_answer and current_answer in options:
            default_index = options.index(current_answer)
        
        user_answer = st.radio(
            f"다음 중 올바른 문장을 고르세요: **{q['문제']}**",
            options,
            index=default_index,
            key=f"levelup_radio_{i}"
        )
        
        # 폼 제출 전에도 답변 저장 (실시간 업데이트)
        if user_answer is not None:
            st.session_state.levelup_quiz[i]['user_answer'] = user_answer

    levelup_submitted = st.form_submit_button("모두 풀었어요! 정답 제출하기", type="primary", use_container_width=True)

    if levelup_submitted:
        # 제출 시점에 답변을 session_state에 저장 (이중 확인)
        for i, q in enumerate(st.session_state.levelup_quiz):
            radio_value = st.session_state.get(f"levelup_radio_{i}", None)
            if radio_value is not None:
                st.session_state.levelup_quiz[i]['user_answer'] = radio_value

        st.session_state.levelup_submitted = True
        # 채점
        all_correct = True
        for q in st.session_state.levelup_quiz:
            user_ans = q.get('user_answer', None)
            if user_ans == q['정답']:
                q['correct'] = True
            else:
                q['correct'] = False
                all_correct = False
        
        if all_correct:
            st.balloons()
            st.success("### 💯 완벽해요! 모든 확인 문제를 맞혔습니다!")
        else:
            st.warning("### 아쉬워요! 틀린 문제가 있어요. 아래 채점표를 보고 다시 도전해 보세요!")

# 레벨업 퀴즈 제출 후 결과 표시
if st.session_state.levelup_submitted:
    st.markdown("##### 📝 레벨업 퀴즈 채점표")
    results_data = []
    for q in st.session_state.levelup_quiz:
        user_ans = q.get('user_answer', None)
        results_data.append({
            "유형": q['오류 유형'],
            "문제": q['문제'],
            "나의 답변": user_ans if user_ans is not None else "미선택",
            "정답": q['정답'],
            "결과": "✅" if q.get('correct', False) else "❌"
        })
    st.dataframe(results_data, use_container_width=True, hide_index=True)


# --- 4. (구) -> (신) 나의 학습 리포트 (위치 이동 및 로직 변경) ---
st.markdown("---")
st.subheader("✨ 나의 학습 리포트")

# 레벨업 퀴즈 기반으로 진행 상황 계산
completed_count = sum(1 for q in st.session_state.levelup_quiz if q['correct'])
total_count = len(st.session_state.levelup_quiz)
progress_ratio = completed_count / total_count if total_count > 0 else 0

with st.container(border=True):
    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(
            label="나의 학습 점수",
            value=f"{completed_count * (100 // total_count)} 점",
            delta=f"{completed_count} / {total_count}개 정답!" if progress_ratio < 1 else "만점! 🎉"
        )

    with col2:
        st.progress(progress_ratio, text=f"규칙 학습 진행률: {progress_ratio * 100:.0f}%")

    if not st.session_state.levelup_submitted:
        st.warning("아직 확인 퀴즈를 풀지 않았어요. '레벨 업' 섹션에서 퀴즈를 풀고 학습 리포트를 확인해 보세요!")
    elif progress_ratio == 1.0:
        st.success("🎉 축하합니다! 모든 규칙을 마스터했어요!")
    else:
        st.info("틀린 문제를 다시 확인하고 재도전해서 100점을 만들어봐요! 파이팅!")
