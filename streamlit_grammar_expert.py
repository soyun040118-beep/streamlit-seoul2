# 한국어 문법 전문가 AI 챗봇 - 핵심 5가지 문법 규칙 집중 학습

import streamlit as st
import pandas as pd
import random
from py_hanspell.spell_checker import check as hanspell_check
from collections import Counter

# --- 한국어 문법 규칙 전문가 DB (5가지 핵심 규칙) ---
GRAMMAR_RULES_DB = {
    "데/대_구분": {
        "규칙": [
            {
                "원칙": "'데'는 직접 경험, '대'는 간접 경험",
                "설명": "'데'는 직접 경험한 사실을, '대'는 다른 사람에게 들은 내용을 전달할 때 사용해요.",
                "틀린예": "졸업식이 일주일 연기됐대. (직접 본 것인데 '대' 사용)",
                "맞는예": "졸업식이 일주일 연기됐데. (직접 봤을 때) / 내 친구가 그렇대. (남에게 들었을 때)"
            },
            {
                "원칙": "'대'는 ~라고 한다는 의미",
                "설명": "'대'는 '~라고 한다', '~라고 들었다'의 의미로 사용되며, 남이 말한 것이나 떠도는 말을 전달할 때 씁니다.",
                "틀린예": "그 영화 정말 재미있데. (직접 봐야 '데' 사용)",
                "맞는예": "그 영화 정말 재미있대. (남에게 들었을 때) / 그 영화 정말 재미있데. (직접 봤을 때)"
            }
        ]
    },
    
    "이에요_예요_구분": {
        "규칙": [
            {
                "원칙": "받침 있음 → '이에요', 받침 없음 → '예요'",
                "설명": "받침이 있는 명사 뒤에는 '이에요', 받침이 없는 명사 뒤에는 '예요'를 붙여요. 받침의 유무를 꼼꼼히 확인하세요!",
                "틀린예": "저는 학생예요. / 이것은 책이에요.",
                "맞는예": "저는 학생이에요. (학생: 받침 ㄴ 있음) / 이것은 책이에요. (책: 받침 ㄠ 있음) / 이것은 사과예요. (사과: 받침 없음)"
            },
            {
                "원칙": "'아니다'는 항상 '아니에요'",
                "설명": "'아니다'는 불규칙 동사로, 받침이 없지만 항상 '아니에요'가 맞아요! (줄여서 '아녜요'도 O) 절대 '아니예요'를 쓰면 안 돼요!",
                "틀린예": "아니예요, 괜찮아요. / 이건 아니예요.",
                "맞는예": "아니에요, 괜찮아요. / 이건 아니에요. (또는 줄여서 '아녜요')"
            },
            {
                "원칙": "명사의 받침을 정확히 파악하기",
                "설명": "받침이 있는 명사: 책, 학생, 손, 집, 친구(X), 선생님(X) / 받침이 없는 명사: 책상, 사과, 엄마, 아빠, 나무 / 헷갈리는 단어: '친구'(○ 받침 없음), '선생님'(○ 받침 없음)",
                "틀린예": "우리 친구는 학생예요. / 선생님은 강아지예요.",
                "맞는예": "우리 친구는 학생이에요. (친구: 받침 X, 학생: 받침 ㄴ O) / 선생님은 강아지예요. (선생님: 받침 X, 강아지: 받침 X)"
            }
        ]
    },

    "어떡해_어떻게_구분": {
        "규칙": [
            {
                "원칙": "'어떻게'는 방법을 물을 때",
                "설명": "'어떻게'는 '어떠하게'의 준말로, 방법이나 방식을 물을 때 사용해요. 의문문에서 자주 쓰입니다.",
                "틀린예": "어떡해 나한테 그럴 수 있어? / 너 집에 어떡해 가?",
                "맞는예": "어떻게 나한테 그럴 수 있어? / 너 집에 어떻게 가?"
            },
            {
                "원칙": "'어떡해'는 난감한 상황에서",
                "설명": "'어떡해'는 '어떻게 해'의 준말로, 걱정되거나 어려운 상황에서 감정을 표현할 때 사용해요. 대명사처럼 쓰입니다.",
                "틀린예": "지갑을 잃어버렸어. 어떻게! / 이 문제 너무 어려워. 어떻게!",
                "맞는예": "지갑을 잃어버렸어. 어떡해! / 이 문제 너무 어려워. 어떡해!"
            },
            {
                "원칙": "구분 팁",
                "설명": "어떻게 = 의문사 (물음표 ?) / 어떡해 = 감탄사 (느낌표 !) / '방법을 물을 때는 어떻게?', '상황이 난감할 때는 어떡해!'라고 기억하세요.",
                "틀린예": "너 어떻게 왔어? (어떡해로 잘못 쓰는 경우)",
                "맞는예": "너 어떻게 왔어? / 어때, 어떻게 지내? / 어떡해, 이제 어쩌지!"
            }
        ]
    },

    "되_돼_구분": {
        "규칙": [
            {
                "원칙": "'돼'는 '되어'의 준말",
                "설명": "'돼'는 '되어'를 줄인 표현이에요. '되어'를 원문에 넣어 말이 되는지 확인해보세요. 만약 '해'로 바꿨을 때 말이 되면 '돼'를 써요!",
                "틀린예": "그러면 안되. / 너는 할 수 없게 돼.",
                "맞는예": "그러면 안돼. (안 되어 X, 안 해 O) / 너는 할 수 없게 돼. (할 수 없게 되어 O)"
            },
            {
                "원칙": "'되'는 '하'로 바꿨을 때 말이 되는 경우",
                "설명": "'되'를 써야 할 때는 '하'로 바꿨을 때 말이 자연스러워야 해요. 주로 '~이/가 되다', '~이 된다' 같은 상태 변화를 나타낼 때 씁니다.",
                "틀린예": "선생님이 돼고 싶어요. / 내일부터 달라져야 돼.",
                "맞는예": "선생님이 되고 싶어요. (선생님이 하고 싶어요 X, 선생님이 되는 것 O) / 내일부터 달라져야 된다. (상태가 달라져야 하다 의미)"
            },
            {
                "원칙": "구분 팁: '해/하' 치환 법칙",
                "설명": "자리에 '해' 또는 '하'를 넣어서 말이 되는지 확인하세요! / '안 돼' → '안 해' (O) = '돼' 사용 / '의사가 돼' → '의사가 해' (X) = '되' 사용 / '밖에 나와도 되?' → '밖에 나와도 해?' (X) = '되' 사용",
                "틀린예": "할 수 없게 되 / 안되요",
                "맞는예": "할 수 없게 돼 (할 수 없게 해 O) / 안돼요 (안 해요 O)"
            }
        ]
    },

    "안_않_구분": {
        "규칙": [
            {
                "원칙": "'안'은 부사 (앞에 옴)",
                "설명": "'안'은 부사로, 동사나 형용사 앞에 와서 '~하지 않다'는 의미를 나타내요. '아니'의 준말입니다. 독립적인 단어처럼 쓰입니다.",
                "틀린예": "그렇게 하면 않돼. / 나는 못 않 가.",
                "맞는예": "그렇게 하면 안돼. / 나는 안 간다. / 안 먹어도 돼."
            },
            {
                "원칙": "'않'은 어미 (뒤에 붙음)",
                "설명": "'않'은 어미로, 동사나 형용사에 붙어서 '~하지 않다'의 의미를 나타내요. '아니하다'의 준말인 '않다'와 결합합니다.",
                "틀린예": "너는 나한테 미안하지도 안니? / 숙제를 아직 안 했다.",
                "맞는예": "너는 나한테 미안하지도 않니? (미안하지 않니? = 미안하다+지+않+니) / 숙제를 아직 안 했다. (아직 '안' 했다)"
            },
            {
                "원칙": "구분 팁: 문법 역할로 구분",
                "설명": "'안' = 부사, 독립적 (동사 앞에 배치) / '않' = 어미, 종속적 (동사 뒤에 붙음) / '아니하다'와 '아니다' 비교: '아니하지 않다' → '않지 않다' (X) / '아니지 않다' → '안지 않다' (X)",
                "틀린예": "내가 뭘 잘못했는지 모르지도 않니? (어색함)",
                "맞는예": "내가 뭘 잘못했는지 모르지도 않니? (모르다+지+않+니, 어미로 사용) / 난 모르지 않아. (난 안 모르지 않아 X, 난 안 몰라 O)"
            }
        ]
    }
}

def get_detailed_grammar_explanation(word_or_phrase: str) -> list:
    """주어진 단어나 문구에 대한 정확한 문법 설명을 반환한다."""
    search_term = word_or_phrase.lower().strip()
    explanations = []
    
    for category, rules in GRAMMAR_RULES_DB.items():
        for rule in rules.get("규칙", []):
            # 정확한 키워드 매칭 (오류 방지)
            if (search_term in rule.get("틀린예", "").lower() or
                search_term in rule.get("맞는예", "").lower() or
                search_term in rule.get("원칙", "").lower()):
                explanations.append({
                    "카테고리": category,
                    "원칙": rule.get("원칙", ""),
                    "설명": rule.get("설명", ""),
                    "틀린예": rule.get("틀린예", ""),
                    "맞는예": rule.get("맞는예", "")
                })
    
    return explanations

def analyze_error_precisely(original_word: str, corrected_word: str) -> dict:
    """오류를 정확히 분석하여 관련 규칙을 찾는다."""
    result = {
        "found": False,
        "category": None,
        "rule": None,
        "explanation": None,
        "wrong_example": None,
        "correct_example": None
    }
    
    # 5가지 핵심 규칙별 정확한 매칭
    # 1. 데/대 구분
    if original_word in ['대', '데'] or '대' in original_word or '데' in original_word:
        if 'GRAMMAR_RULES_DB' in dir():
            for rule in GRAMMAR_RULES_DB.get("데/대_구분", {}).get("규칙", []):
                result = {
                    "found": True,
                    "category": "데/대 구분",
                    "rule": rule.get("원칙"),
                    "explanation": rule.get("설명"),
                    "wrong_example": rule.get("틀린예"),
                    "correct_example": rule.get("맞는예")
                }
                return result
    
    # 2. 이에요/예요 구분
    if original_word in ['예요', '이에요', '아니예요', '아니에요'] or '예요' in original_word or '이에요' in original_word:
        if original_word == '아니예요':
            rule = GRAMMAR_RULES_DB.get("이에요_예요_구분", {}).get("규칙", [])[1]
        else:
            rule = GRAMMAR_RULES_DB.get("이에요_예요_구분", {}).get("규칙", [])[0]
        
        result = {
            "found": True,
            "category": "이에요/예요 구분",
            "rule": rule.get("원칙"),
            "explanation": rule.get("설명"),
            "wrong_example": rule.get("틀린예"),
            "correct_example": rule.get("맞는예")
        }
        return result
    
    # 3. 어떡해/어떻게 구분
    if '어떡해' in original_word or '어떻게' in original_word:
        for rule in GRAMMAR_RULES_DB.get("어떡해_어떻게_구분", {}).get("규칙", []):
            if original_word in rule.get("틀린예", "").lower():
                result = {
                    "found": True,
                    "category": "어떡해/어떻게 구분",
                    "rule": rule.get("원칙"),
                    "explanation": rule.get("설명"),
                    "wrong_example": rule.get("틀린예"),
                    "correct_example": rule.get("맞는예")
                }
                return result
    
    # 4. 되/돼 구분
    if original_word in ['돼', '되'] or '돼' in original_word or '되' in original_word:
        for rule in GRAMMAR_RULES_DB.get("되_돼_구분", {}).get("규칙", []):
            if original_word in rule.get("틀린예", "").lower():
                result = {
                    "found": True,
                    "category": "되/돼 구분",
                    "rule": rule.get("원칙"),
                    "explanation": rule.get("설명"),
                    "wrong_example": rule.get("틀린예"),
                    "correct_example": rule.get("맞는예")
                }
                return result
    
    # 5. 안/않 구분
    if original_word in ['안', '않'] or '안' in original_word or '않' in original_word:
        for rule in GRAMMAR_RULES_DB.get("안_않_구분", {}).get("규칙", []):
            if original_word in rule.get("틀린예", "").lower():
                result = {
                    "found": True,
                    "category": "안/않 구분",
                    "rule": rule.get("원칙"),
                    "explanation": rule.get("설명"),
                    "wrong_example": rule.get("틀린예"),
                    "correct_example": rule.get("맞는예")
                }
                return result
    
    return result

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="한국어 문법 전문가 AI - 핵심 5가지 규칙",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="auto",
)

# --- 세션 상태 초기화 ---
if 'errors' not in st.session_state:
    st.session_state.errors = []
if 'quiz_stats' not in st.session_state:
    st.session_state.quiz_stats = {'correct': 0, 'total': 0}
if 'current_quiz' not in st.session_state:
    st.session_state.current_quiz = None
if 'quiz_result' not in st.session_state:
    st.session_state.quiz_result = None

# --- 메인 화면 구성 ---
st.title("🎯 한국어 문법 전문가 AI - 핵심 5가지 규칙 집중 학습")
st.write("헷갈리는 5가지 문법을 완벽하게 이해하고, 정확한 한국어를 사용하세요!")

# --- 기능별 탭 생성 ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🖊️ 마법의 교정 펜",
    "📒 오답 노트",
    "🏆 문법 퀴즈",
    "🌳 학습 통계",
    "📚 5가지 규칙 완전 학습"
])

# --- 기능 1: 마법의 교정 펜 ---
with tab1:
    st.header("✏️ 문장 첨삭 - 정확한 설명과 함께")
    st.markdown("**오류를 찾고 정확한 문법 규칙을 학습하세요!**")
    
    sentence_input = st.text_area("검사하고 싶은 문장을 입력하세요:", height=150, placeholder="예: 저는 학생예요.")

    if st.button("맞춤법 검사하기", type="primary", use_container_width=True):
        if sentence_input:
            with st.spinner("분석 중..."):
                try:
                    spelled_sent = hanspell_check(sentence_input)
                    original_text = spelled_sent.original
                    corrected_text = spelled_sent.checked
                    
                    st.subheader("✨ 교정 결과")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("📝 원래 문장", original_text, disabled=True)
                    with col2:
                        st.text_input("✅ 고친 문장", corrected_text, disabled=True)

                    if spelled_sent.errors > 0:
                        st.info(f"🔍 {spelled_sent.errors}개의 맞춤법 오류를 찾았어요!")
                        st.subheader("📖 오류 분석 & 정확한 설명")
                        
                        for original_word, error_info in spelled_sent.words.items():
                            error_type = error_info[0]
                            corrected_word = error_info[1]
                            
                            with st.expander(f"❌ '{original_word}' → ✅ '{corrected_word}'", expanded=True):
                                st.markdown(f"**오류 유형**: `{error_type}`")
                                st.markdown(f"**올바른 표현**: `{corrected_word}`")
                                
                                # 정확한 문법 설명 검색
                                error_analysis = analyze_error_precisely(original_word, corrected_word)
                                
                                if error_analysis.get("found"):
                                    st.markdown("---")
                                    st.markdown("**📚 적용되는 문법 규칙**")
                                    st.markdown(f"**규칙**: {error_analysis['rule']}")
                                    st.markdown(f"**설명**: {error_analysis['explanation']}")
                                    st.markdown("---")
                                    st.error(f"❌ 틀린 예: {error_analysis['wrong_example']}")
                                    st.success(f"✅ 맞는 예: {error_analysis['correct_example']}")
                                else:
                                    # 기본 안내
                                    st.info("이 오류는 5가지 핵심 규칙 중 하나에 해당합니다. '5가지 규칙 완전 학습' 탭에서 더 자세히 배워보세요!")
                            
                            st.session_state.errors.append({
                                "틀린 단어": original_word,
                                "맞는 단어": corrected_word,
                                "오류 유형": error_type
                            })
                        
                        st.success("✅ 오류를 오답 노트에 기록했어요!")
                    else:
                        st.success("🎉 완벽한 문장이에요!")
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
        else:
            st.warning("문장을 입력해주세요!")

# --- 기능 2: 오답 노트 ---
with tab2:
    st.header("🧐 자주 틀리는 표현들")
    if st.session_state.errors:
        error_df = pd.DataFrame(st.session_state.errors)
        st.dataframe(error_df, use_container_width=True)

        st.subheader("📊 오류 유형 분석")
        error_types = [error['오류 유형'] for error in st.session_state.errors]
        type_counts = Counter(error_types)
        st.bar_chart(pd.DataFrame.from_dict(type_counts, orient='index', columns=['횟수']))

        if st.button("노트 비우기", use_container_width=True):
            st.session_state.errors = []
            st.rerun()
    else:
        st.info("📌 아직 기록된 오답이 없어요! 마법의 교정 펜을 사용해보세요.")

# --- 기능 3: 문법 퀴즈 ---
with tab3:
    st.header("🏆 핵심 5가지 문법 퀴즈")
    unique_errors = [dict(t) for t in {tuple(d.items()) for d in st.session_state.errors}]
    
    if len(unique_errors) >= 2:
        if st.button("새로운 퀴즈 시작!", use_container_width=True) or st.session_state.current_quiz:
            if not st.session_state.current_quiz:
                quiz_items = random.sample(unique_errors, 2)
                question_item = quiz_items[0]
                wrong_option_item = quiz_items[1]

                options = [question_item['맞는 단어'], wrong_option_item['맞는 단어']]
                random.shuffle(options)
                
                st.session_state.current_quiz = {
                    "question": f"'{question_item['틀린 단어']}'의 올바른 표현은?",
                    "options": options,
                    "answer": question_item['맞는 단어']
                }
                st.session_state.quiz_result = None

            quiz = st.session_state.current_quiz
            st.subheader(quiz['question'])
            user_answer = st.radio("정답 선택:", quiz['options'], index=None)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("정답 확인", use_container_width=True):
                    if user_answer:
                        st.session_state.quiz_stats['total'] += 1
                        if user_answer == quiz['answer']:
                            st.session_state.quiz_stats['correct'] += 1
                            st.session_state.quiz_result = "correct"
                            st.success("✅ 정답입니다! 👍")
                        else:
                            st.session_state.quiz_result = "incorrect"
                            st.error(f"❌ 오답입니다. 정답은 '{quiz['answer']}'예요!")
                        
                        st.session_state.current_quiz = None
                    else:
                        st.warning("정답을 선택해주세요!")
    else:
        st.info("📌 퀴즈를 만들려면 오답 노트에 2개 이상의 오답이 필요해요!")

# --- 기능 4: 통계 ---
with tab4:
    st.header("📊 학습 통계")
    total = st.session_state.quiz_stats['total']
    correct = st.session_state.quiz_stats['correct']

    if total > 0:
        accuracy = (correct / total) * 100
        st.subheader("🌳 성장 나무")
        
        if accuracy < 30:
            st.write("🌱 새싹 단계 - 시작이 반입니다!")
        elif accuracy < 70:
            st.write("🌳 나무 단계 - 계속 화이팅!")
        else:
            st.write("🌲 숲 단계 - 당신은 문법 전문가입니다!")

        col1, col2 = st.columns(2)
        col1.metric("총 퀴즈", f"{total}개")
        col2.metric("정답률", f"{accuracy:.1f}%")
        st.progress(accuracy / 100)
    else:
        st.info("📌 퀴즈를 풀면 통계를 확인할 수 있어요!")

# --- 기능 5: 5가지 규칙 완전 학습 ---
with tab5:
    st.header("📚 핵심 5가지 문법 규칙 완전 학습")
    st.markdown("**5가지 규칙을 완벽하게 마스터하세요!**")
    
    selected_category = st.selectbox(
        "📖 학습할 문법 규칙:",
        list(GRAMMAR_RULES_DB.keys()),
        format_func=lambda x: x.replace("_", " / ")
    )
    
    if selected_category in GRAMMAR_RULES_DB:
        category_rules = GRAMMAR_RULES_DB[selected_category]
        st.subheader(f"🎯 {selected_category.replace('_', ' / ')}")
        
        for idx, rule in enumerate(category_rules.get("규칙", []), 1):
            with st.expander(f"{idx}️⃣ {rule.get('원칙')}", expanded=(idx==1)):
                st.markdown(f"**📋 상세 설명**")
                st.info(rule.get("설명"))
                
                st.markdown("---")
                st.markdown("**❌ 틀린 예시**")
                st.error(rule.get("틀린예"))
                
                st.markdown("**✅ 맞는 예시**")
                st.success(rule.get("맞는예"))
    
    st.markdown("---")
    st.subheader("🔍 규칙 검색")
    search_keyword = st.text_input("찾고 싶은 단어를 입력하세요 (예: 이에요, 돼, 어떡해):")
    
    if search_keyword:
        results = get_detailed_grammar_explanation(search_keyword)
        if results:
            st.success(f"🎯 '{search_keyword}'과 관련된 {len(results)}개의 규칙을 찾았어요!")
            for result in results:
                with st.expander(f"[{result['카테고리'].replace('_', '/')}] {result['원칙']}"):
                    st.info(result['설명'])
                    st.error(f"❌ {result['틀린예']}")
                    st.success(f"✅ {result['맞는예']}")
        else:
            st.info(f"📌 '{search_keyword}'과 관련된 규칙을 찾지 못했어요. 다른 단어로 시도해보세요.")
    
    st.markdown("---")
    st.subheader("📌 5가지 핵심 규칙 요약")
    st.info("""
    **1️⃣ 데/대 구분**
    - 직접 경험: '데' (내가 봤을 때)
    - 간접 경험: '대' (남이 말했을 때)
    
    **2️⃣ 이에요/예요 구분**
    - 받침 있음: '이에요' (학생이에요, 책이에요)
    - 받침 없음: '예요' (엄마예요, 사과예요)
    - 예외: '아니다' → 항상 '아니에요'
    
    **3️⃣ 어떡해/어떻게 구분**
    - 어떻게: 방법을 물을 때 (? 의문사)
    - 어떡해: 난감한 상황에서 (! 감탄사)
    
    **4️⃣ 되/돼 구분**
    - '해'로 바꿀 때 말이 되면: '돼' (안 돼 → 안 해 O)
    - '하'로 바꿀 때 말이 되면: '되' (의사가 되다)
    
    **5️⃣ 안/않 구분**
    - '안': 부사 (앞에 옴) - 안 간다, 안 먹어
    - '않': 어미 (뒤에 붙음) - 하지 않다, 가지 않다
    """)
