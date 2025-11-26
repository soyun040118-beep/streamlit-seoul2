# app.py

import streamlit as st
import pandas as pd
import random
from py_hanspell.spell_checker import check as hanspell_check
from collections import Counter

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="맞춤법 탐험대",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- 세션 상태 초기화 ---
# Streamlit은 사용자가 상호작용할 때마다 스크립트를 다시 실행합니다.
# st.session_state를 사용하면 변수 값을 유지할 수 있습니다.

# 1. 오답 노트를 위한 초기화
if 'errors' not in st.session_state:
    st.session_state.errors = []

# 2. 퀴즈 통계를 위한 초기화
if 'quiz_stats' not in st.session_state:
    st.session_state.quiz_stats = {'correct': 0, 'total': 0}

# 3. 현재 퀴즈 상태를 위한 초기화
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'quiz_result' not in st.session_state:
    st.session_state.quiz_result = None


# --- 메인 화면 구성 ---
st.title("🧭 맞춤법 탐험대")
st.write("헷갈리는 맞춤법을 게임처럼 배우고, 나의 실력을 쑥쑥 키워보아요!")

# --- 기능별 탭 생성 ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🖊️ 마법의 교정 펜 (문장 첨삭)",
    "📒 나만의 비밀 노트 (오답 노트)",
    "🏆 도전! 맞춤법 퀴즈",
    "🌳 나의 성장 나무 (통계)"
])


# --- 기능 1: 마법의 교정 펜 (문장 첨삭) ---
with tab1:
    st.header("✏️ 문장을 입력하면 맞춤법을 고쳐줘요!")
    sentence_input = st.text_area("여기에 검사하고 싶은 문장을 넣어보세요. (예: 아빠가 밥을 다 먹었데.)", height=150)

    if st.button("맞춤법 검사하기", type="primary"):
        if sentence_input:
            with st.spinner("꼼꼼하게 살펴보고 있어요..."):
                # py-hanspell 라이브러리를 사용해 맞춤법 검사
                spelled_sent = hanspell_check(sentence_input)
                
                original_text = spelled_sent.original
                corrected_text = spelled_sent.checked
                
                st.subheader("✨ 교정 결과")
                st.text_input("원래 문장", original_text, disabled=True, key="original_text_input")
                st.text_input("고친 문장", corrected_text, disabled=True, key="corrected_text_input")

                # 오류가 있을 경우, 오답 노트에 추가
                if spelled_sent.errors > 0:
                    st.info(f"{spelled_sent.errors}개의 맞춤법 오류를 찾았어요!")
                    # py-hanspell의 결과 형식에 맞게 수정
                    for original_word, error_info in spelled_sent.words.items():
                        error_type = error_info[0] # 오류 유형
                        corrected_word = error_info[1] # 추천 단어
                        # 오답 노트(session_state)에 추가
                        st.session_state.errors.append({
                            "틀린 단어": original_word,
                            "맞는 단어": corrected_word,
                            "오류 유형": error_type
                        })
                    st.success("오류를 '나만의 비밀 노트'에 기록했어요!")
                else:
                    st.success("🎉 완벽한 문장이에요! 대단해요!")
        else:
            st.warning("먼저 문장을 입력해주세요!")


# --- 기능 2: 나만의 비밀 노트 (오답 노트) ---
with tab2:
    st.header("🧐 내가 자주 틀리는 맞춤법을 확인해요!")
    if st.session_state.errors:
        # Pandas DataFrame으로 오답 목록을 깔끔하게 표시
        error_df = pd.DataFrame(st.session_state.errors)
        st.dataframe(error_df, use_container_width=True)

        # 가장 많이 틀린 유형 분석
        st.subheader("🔍 자주 틀리는 유형 분석")
        error_types = [error['오류 유형'] for error in st.session_state.errors]
        type_counts = Counter(error_types)
        st.bar_chart(pd.DataFrame.from_dict(type_counts, orient='index', columns=['틀린 횟수']))

        if st.button("비밀 노트 비우기"):
            st.session_state.errors = []
            st.rerun()
    else:
        st.info("아직 기록된 오답이 없어요. '마법의 교정 펜'을 먼저 사용해보세요!")


# --- 기능 3: 도전! 맞춤법 퀴즈 ---
with tab3:
    st.header("🏅 오답 노트로 퀴즈를 풀어봐요!")

    # 오답이 2개 이상 있어야 퀴즈 생성 가능
    unique_errors = [dict(t) for t in {tuple(d.items()) for d in st.session_state.errors}]
    if len(unique_errors) >= 2:
        if st.button("새로운 퀴즈 시작하기!") or st.session_state.current_quiz:
            # 현재 퀴즈가 없으면 새로 생성
            if not st.session_state.current_quiz:
                # 오답 노트에서 중복을 제거한 후 무작위로 2개 선택
                quiz_items = random.sample(unique_errors, 2)
                question_item = quiz_items[0]
                wrong_option_item = quiz_items[1]

                # 보기 순서 섞기
                options = [question_item['맞는 단어'], wrong_option_item['맞는 단어']]
                random.shuffle(options)
                
                st.session_state.current_quiz = {
                    "question": f"다음 중 '{question_item['틀린 단어']}'의 올바른 표현은 무엇일까요?",
                    "options": options,
                    "answer": question_item['맞는 단어']
                }
                st.session_state.quiz_result = None # 이전 결과 초기화

            # 퀴즈 문제 표시
            quiz = st.session_state.current_quiz
            st.subheader(quiz['question'])
            user_answer = st.radio("정답을 골라주세요:", quiz['options'], index=None, key="quiz_option")

            if st.button("정답 확인하기"):
                if user_answer is not None:
                    # 통계 업데이트
                    st.session_state.quiz_stats['total'] += 1
                    if user_answer == quiz['answer']:
                        st.session_state.quiz_stats['correct'] += 1
                        st.session_state.quiz_result = "correct"
                    else:
                        st.session_state.quiz_result = "incorrect"
                    
                    # 퀴즈 상태 초기화해서 다음 퀴즈를 풀 수 있게 함
                    st.session_state.current_quiz = None
                    st.rerun() # 화면을 새로고침하여 결과 표시
                else:
                    st.warning("정답을 선택해주세요!")

            # 퀴즈 결과 표시
            if st.session_state.quiz_result == "correct":
                st.success("정답입니다! 정말 대단해요! 👍")
            elif st.session_state.quiz_result == "incorrect":
                st.error(f"아쉬워요. 정답은 '{quiz['answer']}' 였어요. 다음엔 꼭 맞힐 수 있을 거예요! 💪")

    else:
        st.info("퀴즈를 만들려면 '비밀 노트'에 2개 이상의 오답이 필요해요!")


# --- 기능 4: 나의 성장 나무 (통계) ---
with tab4:
    st.header("📊 나의 맞춤법 실력이 얼마나 늘었을까요?")

    total_quizzes = st.session_state.quiz_stats['total']
    correct_quizzes = st.session_state.quiz_stats['correct']

    if total_quizzes > 0:
        accuracy = (correct_quizzes / total_quizzes) * 100
        
        # 나의 성장 나무 시각화
        st.subheader("🌳 나의 성장 나무")
        if accuracy < 30:
            st.image("https://emojicdn.elk.sh/🌱", width=120)
            st.write("이제 막 자라나는 새싹 단계예요! 꾸준히 하면 금방 자랄 거예요.")
        elif accuracy < 70:
            st.image("https://emojicdn.elk.sh/🌳", width=120)
            st.write("튼튼한 나무로 자랐네요! 조금만 더 노력하면 울창한 숲이 될 수 있어요.")
        else:
            st.image("https://emojicdn.elk.sh/🌲", width=120)
            st.write("우와! 울창한 숲을 이뤘어요! 당신은 진정한 맞춤법 박사님!")

        # 통계 지표 표시
        st.metric(label="푼 퀴즈 수", value=f"{total_quizzes}개")
        st.metric(label="정답률", value=f"{accuracy:.1f}%")

        # 정답률을 프로그레스 바로 시각화
        st.progress(accuracy / 100)
    else:
        st.info("퀴즈를 풀면 나의 실력을 확인할 수 있어요!")

