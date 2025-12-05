import streamlit as st
import pandas as pd
import random
import time
import os
from dotenv import load_dotenv
import numpy as np
import json
import requests
from datetime import datetime

# --- 데이터 로드 함수 ---
def get_grammar_data():
    """초등 문법 오류 데이터를 생성하고 DataFrame으로 반환합니다."""
    data = {
        '오류 유형': ['데/대', '에요/예요', '어떡해/어떻게', '되/돼', '안/않'],
        '규칙 설명': [
            "'데'는 직접 경험한 사실을, '대'는 다른 사람에게 들은 내용을 전달할 때 사용해요.",
            '받침이 있으면 **'이에요'**, 받침이 없으면 **'예요'**를 써요.\n\n하지만 **'아니다'**는 무조건 **'아니에요'**가 맞아요! (줄여서 \'아녜요\'도 O) 그 이유가 궁금한 학생은 선생님과 함께 탐구해볼까요?',
            "'어떻게'는 '어떠하게'의 준말로 방법을 물을 때 쓰고, '어떡해'는 '어떻게 해'의 준말로 걱정되는 상황에서 사용해요.",
            "'되어'의 준말이 '돼'예요. '되어'를 넣어 말이 되면 '돼'를 쓸 수 있어요.\n\n**사용법:** '돼' 또는 '되' 자리에 '해' 또는 '하'를 넣어보세요.\n\n'돼'는 '해'로 바꾸었을 때 말이 되면 '돼'를 씁니다. (예: '안 돼' → '안 해' ✓)\n'되'는 '하'로 바꾸었을 때 말이 되면 '되'를 씁니다. (예: '선생님이 되고 싶어' → '선생님이 하고 싶어' ✓)",
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

# --- 챗봇 관련 함수들 ---
def get_available_models():
    """사용 가능한 모델 목록을 가져옵니다."""
    available_models = []
    
    # API 키가 없으면 빈 리스트 반환
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "여기에 실제 구글 API 키를 입력하세요":
        return []
    
    # v1beta API로 모델 목록 조회 시도
    for api_version in ["v1beta", "v1"]:
        try:
            list_url = f"https://generativelanguage.googleapis.com/{api_version}/models?key={GOOGLE_API_KEY}"
            response = requests.get(list_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    for model in data["models"]:
                        model_name = model.get("name", "")
                        supported_methods = model.get("supportedGenerationMethods", [])
                        # streamGenerateContent 또는 generateContent를 지원하는 모델 추가
                        if "streamGenerateContent" in supported_methods or "generateContent" in supported_methods:
                            # 모델 이름에서 버전 추출 (예: "models/gemini-pro" -> "gemini-pro")
                            if "/" in model_name:
                                short_name = model_name.split("/")[-1]
                                available_models.append((api_version, short_name))
                    if available_models:
                        break
            elif response.status_code == 403:
                # 403 오류 시 다음 API 버전 시도
                continue
            elif response.status_code == 404:
                # 404 오류 시 다음 API 버전 시도
                continue
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [403, 404]:
                # 403, 404 오류 시 다음 API 버전 시도
                continue
        except:
            continue
    
    # 모델 목록을 가져오지 못한 경우 기본 모델 사용 (우선순위 순서)
    # 하지만 실제로는 API 키 문제일 수 있으므로 빈 리스트 반환 권장
    if not available_models:
        # 기본 모델 목록 (실제로는 작동하지 않을 수 있음)
        available_models = [
            # v1beta API 우선 (더 안정적이고 널리 지원됨)
            ("v1beta", "gemini-pro"),
            ("v1beta", "gemini-1.5-flash"),
            ("v1beta", "gemini-1.5-pro"),
        ]
    else:
        # 가져온 모델 목록을 우선순위에 따라 정렬
        # gemini-pro를 가장 먼저 시도하도록
        priority_order = ["gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro"]
        sorted_models = []
        for priority_model in priority_order:
            for api_version, model_name in available_models:
                if model_name == priority_model and (api_version, model_name) not in sorted_models:
                    sorted_models.append((api_version, model_name))
        # 나머지 모델 추가
        for api_version, model_name in available_models:
            if (api_version, model_name) not in sorted_models:
                sorted_models.append((api_version, model_name))
        available_models = sorted_models if sorted_models else available_models
    
    return available_models

# 세션 상태에 모델 목록 저장 (한 번만 조회)
if 'available_models' not in st.session_state:
    st.session_state.available_models = get_available_models()

API_CONFIGS = st.session_state.available_models

def stream_gemini_response(payload):
    """Gemini API로부터 스트리밍 응답을 받아 텍스트 청크를 yield합니다."""
    last_error = None
    last_status_code = None
    tried_models = []
    
    for api_version, model_name in API_CONFIGS:
        # 먼저 streamGenerateContent 시도, 실패하면 generateContent 시도
        endpoints = [
            ("streamGenerateContent", True),  # 스트리밍
            ("generateContent", False)  # 비스트리밍
        ]
        
        for endpoint_name, is_streaming in endpoints:
            api_url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:{endpoint_name}"
            current_model = f"{api_version}/{model_name} ({endpoint_name})"
            
            if current_model not in tried_models:
                tried_models.append(current_model)
            
            try:
                if is_streaming:
                    # 스트리밍 엔드포인트
                    params = {"key": GOOGLE_API_KEY, "alt": "sse"}
                    with requests.post(api_url, params=params, headers={"Content-Type": "application/json"}, json=payload, stream=True, timeout=60) as response:
                        response.raise_for_status()
                        for chunk in response.iter_lines():
                            if chunk:
                                decoded_chunk = chunk.decode('utf-8')
                                if decoded_chunk.startswith('data: '):
                                    try:
                                        data = json.loads(decoded_chunk[6:])
                                        if "candidates" in data and len(data["candidates"]) > 0:
                                            candidate = data["candidates"][0]
                                            if "content" in candidate and "parts" in candidate["content"]:
                                                yield candidate["content"]["parts"][0]["text"]
                                    except json.JSONDecodeError:
                                        continue
                        return # 성공적으로 스트리밍이 끝나면 함수 종료
                else:
                    # 비스트리밍 엔드포인트
                    params = {"key": GOOGLE_API_KEY}
                    response = requests.post(api_url, params=params, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
                    response.raise_for_status()
                    data = response.json()
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            text = candidate["content"]["parts"][0]["text"]
                            # 비스트리밍이므로 전체 텍스트를 한 번에 yield
                            yield text
                            return
            except requests.exceptions.HTTPError as e:
                last_error = e
                last_status_code = e.response.status_code
                
                # 오류 응답 본문 확인
                error_detail = ""
                try:
                    error_data = e.response.json()
                    if "error" in error_data:
                        error_detail = error_data["error"].get("message", "")
                except:
                    pass
                
                if e.response.status_code == 404:
                    # 404 오류 시 다음 엔드포인트 또는 모델 시도
                    if not is_streaming:
                        # generateContent도 실패했으면 다음 모델로
                        break
                    continue
                elif e.response.status_code == 403:
                    # 403 오류도 다음 엔드포인트 또는 모델 시도
                    if not is_streaming:
                        break
                    continue
                else:
                    # 다른 HTTP 오류는 다음 엔드포인트 또는 모델 시도
                    if not is_streaming:
                        break
                    continue
            except Exception as exc:
                last_error = exc
                if not is_streaming:
                    break
                continue
    
    # 모든 시도가 실패한 경우
    if last_error:
        error_msg = f"**오류가 발생했어요!**\n\n"
        
        if last_status_code == 403:
            error_msg += "**403 Forbidden 오류:** API 키에 문제가 있거나 접근 권한이 없어요.\n\n"
            error_msg += "**해결 방법:**\n"
            error_msg += "1. Google Cloud Console에서 Gemini API가 활성화되어 있는지 확인해주세요.\n"
            error_msg += "2. API 키가 올바른지 확인해주세요.\n"
            error_msg += "3. API 키에 필요한 권한이 부여되어 있는지 확인해주세요.\n"
            if tried_models:
                error_msg += f"4. 시도한 모델들: {', '.join(tried_models)}\n\n"
        elif last_status_code == 404:
            error_msg += f"**404 Not Found 오류:** 모델을 찾을 수 없어요.\n\n"
            if tried_models:
                error_msg += f"**시도한 모델들:**\n"
                for model in tried_models:
                    error_msg += f"- {model}\n"
                error_msg += "\n"
            error_msg += "**해결 방법:**\n"
            error_msg += "1. **API 키 확인:** Google Cloud Console에서 API 키가 올바르게 생성되었는지 확인해주세요.\n"
            error_msg += "2. **Gemini API 활성화:** Google Cloud Console에서 'Generative Language API'가 활성화되어 있는지 확인해주세요.\n"
            error_msg += "3. **API 키 제한 설정:** API 키의 '애플리케이션 제한사항'에서 'Generative Language API'가 허용되어 있는지 확인해주세요.\n"
            error_msg += "4. **프로젝트 확인:** 올바른 Google Cloud 프로젝트에서 API 키를 생성했는지 확인해주세요.\n"
            error_msg += "5. **모델 목록 확인:** 페이지를 새로고침하여 사용 가능한 모델 목록을 다시 로드해보세요.\n\n"
            error_msg += "💡 **팁:** 모든 모델에서 404 오류가 발생한다면 API 키 설정에 문제가 있을 가능성이 높습니다.\n\n"
        else:
            error_msg += f"**오류 상세:** {last_error}\n\n"
            if last_status_code:
                error_msg += f"HTTP 상태 코드: {last_status_code}\n"
            if tried_models:
                error_msg += f"시도한 모델들: {', '.join(tried_models)}\n"
        
        error_msg += "\n다시 시도해주시거나, API 키 설정을 확인해주세요."
        yield error_msg

# --- 1. 앱 기본 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="wide")

# --- 사이드바 마스코트 ---
with st.sidebar:
    st.info("안녕하세요. 저는 맞춤법 해결사예요! 함께 즐겁게 문법을 배워봐요! ✨")
    
    # API 키 로드 상태 표시
    st.markdown("---")
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "여기에 실제 구글 API 키를 입력하세요":
        st.success("API 키가 준비됐어요! 🤖")
    else:
        st.warning("API 키가 필요해요! 🔑")
    
    # AI 대화 규칙
    st.markdown("---")
    st.markdown("### 🤖 AI 챗봇 사용 규칙")
    with st.container(border=True):
        st.markdown("""
        **디지털 윤리를 지켜요!** 📚
        
        ✅ **해야 할 것:**
        - 궁금한 내용만 간결하고 명료하게 물어보기
        - 정중하고 예의 바른 말투 사용하기
        - 문법과 맞춤법 질문에 집중하기
        
        ❌ **하지 말아야 할 것:**
        - 욕설이나 비속어 사용 금지
        - 타인을 비방하거나 모욕하는 말 사용 금지
        - 개인정보나 불필요한 정보 공유 금지
        
        💡 **팁:** 질문을 구체적으로 하면 더 정확한 답변을 받을 수 있어요!
        """)

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
        
        # 안내 문구 추가
        st.markdown("""
        <div style="background-color: #e8f4f8; 
                    padding: 12px; 
                    border-radius: 8px; 
                    border-left: 4px solid #1f77b4;
                    margin: 10px 0;
                    font-size: 16px;
                    color: #2c3e50;">
            💡 <strong>알맞은 답을 고르면 저절로 다음 문제로 넘어가고, 틀린 답을 고르면 나만의 오답노트가 생성돼요!</strong>
        </div>
        """, unsafe_allow_html=True)

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
                        # 폼 안에서 즉시 정답 피드백 표시
                        st.success("🎉 정답입니다!")
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
                        # 폼 안에서 즉시 오답 피드백 표시
                        st.error(f"❌ 아쉬워요, 정답은 **'{question_data['정답']}'** 입니다.")
                        st.info("💡 아래에서 틀린 이유를 확인하고 '틀린 이유 확인' 버튼을 눌러주세요.")
                    
                    # 폼 제출 후 즉시 rerun하여 피드백 표시
                    st.rerun()

        # 정답 제출 후 피드백 표시 (같은 문제에 대해서만)
        feedback_question_id = st.session_state.get('answer_feedback_question_id', None)
        # is_submitted를 다시 확인 (폼 제출 후 업데이트되었을 수 있음)
        current_is_submitted = st.session_state.get(f"is_submitted_{question_id}", False)
        
        if current_is_submitted and feedback_question_id == question_id:
            feedback_type = st.session_state.get('answer_feedback', None)
            
            if feedback_type == "correct":
                st.success("🎉 정답입니다!")
                st.balloons()
                # 정답일 때 빠르게 다음 문제로 넘어가기
                auto_next_key = f"auto_next_question_{question_id}"
                timer_key = f"auto_next_timer_{question_id}"
                delay_key = f"auto_next_delay_{question_id}"
                
                # 타이머가 설정되어 있으면 체크
                if st.session_state.get(auto_next_key, False):
                    current_time = time.time()
                    start_time = st.session_state.get(timer_key, current_time)
                    elapsed = current_time - start_time
                    delay = st.session_state.get(delay_key, 1.0)
                    
                    if elapsed >= delay:
                        # 시간이 지나면 다음 문제로 이동
                        st.session_state[f"is_submitted_{question_id}"] = False
                        st.session_state[f"submitted_answer_{question_id}"] = None
                        st.session_state[auto_next_key] = False
                        if timer_key in st.session_state:
                            del st.session_state[timer_key]
                        if delay_key in st.session_state:
                            del st.session_state[delay_key]
                        # 피드백 상태 초기화
                        if 'answer_feedback' in st.session_state:
                            del st.session_state['answer_feedback']
                        if 'answer_feedback_question_id' in st.session_state:
                            del st.session_state['answer_feedback_question_id']
                        generate_question(st.session_state.retry_mode)
                        st.rerun()
                    else:
                        # 아직 시간이 안 지났으면 잠시 후 다시 렌더링
                        # 1초 딜레이이므로 카운트다운 메시지는 표시하지 않음
                        # 자동으로 다시 렌더링하여 타이머 업데이트
                        st.rerun()
            elif feedback_type == "incorrect":
                st.error(f"❌ 아쉬워요, 정답은 **'{question_data['정답']}'** 입니다.")
                if submitted_answer:
                    st.warning(f"선택하신 답: **'{submitted_answer}'**")
                
                # 추가 설명 섹션
                with st.container(border=True):
                    st.markdown("##### 🔍 왜 틀렸을까요?")
                    st.markdown(f"**💡 {question_data['오류 유형']} 규칙**")
                    with st.container(border=True):
                        st.info(f"**규칙:** {question_data['규칙 설명']}")
                        st.success(f"**올바른 예시:** {question_data['정답']}")
                        st.error(f"**틀린 예시:** {question_data['오답들'][0] if question_data['오답들'] else ''}")
                
                # 틀린 이유 확인 버튼
                confirm_key = f"confirm_incorrect_{question_id}"
                if st.button("✅ 틀린 이유 확인", key=confirm_key, type="primary", use_container_width=True):
                    # 버튼을 누르면 다음 문제로 이동
                    st.session_state[f"is_submitted_{question_id}"] = False
                    st.session_state[f"submitted_answer_{question_id}"] = None
                    # 자동 진행 관련 상태 제거
                    auto_next_key = f"auto_next_question_{question_id}"
                    timer_key = f"auto_next_timer_{question_id}"
                    delay_key = f"auto_next_delay_{question_id}"
                    if auto_next_key in st.session_state:
                        del st.session_state[auto_next_key]
                    if timer_key in st.session_state:
                        del st.session_state[timer_key]
                    if delay_key in st.session_state:
                        del st.session_state[delay_key]
                    # 피드백 상태 초기화
                    if 'answer_feedback' in st.session_state:
                        del st.session_state['answer_feedback']
                    if 'answer_feedback_question_id' in st.session_state:
                        del st.session_state['answer_feedback_question_id']
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
# 오답 노트는 항상 표시 (오답이 있을 때만)
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

# 레벨업 퀴즈 폼 (항상 표시)
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

# --- 5. 문법 교정 챗봇 (SNS 스타일) ---
st.markdown("---")
st.subheader("🤖 문법 교정 챗봇")

# SNS 스타일 CSS 추가
st.markdown("""
<style>
    /* 사용자 메시지 스타일 (오른쪽) */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 15px;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-left: auto;
    }
    
    /* 챗봇 메시지 스타일 (왼쪽) */
    .assistant-message {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 15px;
    }
    
    .assistant-bubble {
        background: white;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* 시간 표시 */
    .message-time {
        font-size: 0.7em;
        color: #999;
        margin-top: 4px;
        text-align: right;
    }
    
    .assistant-time {
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

# 챗봇 소개 문구 (눈에 띄게 표시)
with st.container(border=True):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; 
                border-radius: 10px; 
                color: white; 
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="color: white; margin: 0;">🤖 문법 마스터 챗봇</h3>
        <p style="color: white; font-size: 1.1em; margin: 10px 0 0 0;">
            안녕하세요! 저는 문법을 마스터한 초등학생이에요.<br>
            맞춤법과 문법에 대해 친절하고 정확하게 설명해드릴게요! 💬
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 질문 형식 예시 추가
    with st.expander("💡 올바른 질문 형식 예시", expanded=False):
        st.markdown("""
        **좋은 질문 형식:**
        
        1. **구체적인 문장 제시:**
           - "이 문장이 맞나요? '저는 학생예요.'"
           - "'안되'와 '안돼' 중 어느 것이 맞나요?"
        
        2. **문법 규칙 질문:**
           - "'에요'와 '예요'의 차이점을 알려주세요."
           - "'되'와 '돼'를 구분하는 방법을 설명해주세요."
        
        3. **맞춤법 확인:**
           - "'어떡해'와 '어떻게' 중 어떤 것이 맞나요?"
           - "이 문장의 맞춤법을 확인해주세요: '그러면 안되.'"
        
        4. **예시 문장과 함께:**
           - "'아니예요'와 '아니에요' 중 어느 것이 맞나요? 예: '아니예요, 괜찮아요.'"
        
        **피해야 할 질문:**
        - 너무 모호한 질문: "문법 알려줘"
        - 여러 질문을 한 번에: "에요 예요 되 돼 안 않 모두 알려줘"
        
        💡 **팁:** 구체적인 문장이나 단어를 제시하면 더 정확한 답변을 받을 수 있어요!
        """)

# API 키 확인
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "여기에 실제 구글 API 키를 입력하세요":
    st.error("앗! 구글 API 키가 설정되지 않았어요. .env 파일을 확인해주세요.")
else:
    # 세션 상태에 대화 기록 초기화
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    
    # 대화 기록 컨테이너
    chat_container = st.container()
    
    # 이전 대화 기록 표시 (SNS 스타일)
    with chat_container:
        for idx, message in enumerate(st.session_state.chat_messages):
            role = message["role"]
            content = message["content"]
            timestamp = message.get("timestamp", "")
            
            if role == "user":
                # 사용자 메시지 (오른쪽)
                st.markdown(f"""
                <div class="user-message">
                    <div class="user-bubble">
                        {content}
                        <div class="message-time">{timestamp}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 챗봇 메시지 (왼쪽)
                st.markdown(f"""
                <div class="assistant-message">
                    <div class="assistant-bubble">
                        {content}
                        <div class="message-time assistant-time">{timestamp}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 사용자 입력을 위한 채팅 입력창
    if prompt := st.chat_input("맞춤법이나 문법이 궁금한 문장을 입력해봐!"):
        # 현재 시간 가져오기
        current_time = datetime.now().strftime("%H:%M")
        
        # 사용자 메시지를 대화 기록에 추가하고 화면에 표시
        user_message = {"role": "user", "content": prompt, "timestamp": current_time}
        st.session_state.chat_messages.append(user_message)
        
        # 사용자 메시지 즉시 표시 (SNS 스타일)
        with chat_container:
            st.markdown(f"""
            <div class="user-message">
                <div class="user-bubble">
                    {prompt}
                    <div class="message-time">{current_time}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
        # Gemini 응답 생성
        with chat_container:
            # 챗봇 응답 영역 생성
            response_placeholder = st.empty()
            
            with response_placeholder.container():
                with st.spinner("💭 생각 중..."):
                    # 페르소나 설정 및 대화 기록을 API 요청 형식으로 변환
                    conversation_history = []
                    for msg in st.session_state.chat_messages:
                        role = "model" if msg["role"] == "assistant" else "user"
                        conversation_history.append({"role": role, "parts": [{"text": msg["content"]}]})
    
                    # 마지막 사용자 메시지 앞에 페르소나 프롬프트 추가
                    system_prompt = (
                        "너는 문법을 완벽하게 마스터한 초등학생이야. "
                        "사용자의 맞춤법과 문법 질문에 대해 정확하고 전문적으로 답변해야 해. "
                        "말투는 매우 친절하고 따뜻하게, 마치 친한 선생님이 학생에게 설명해주는 것처럼 해줘. "
                        "'~예요', '~입니다', '~해요' 같은 정중하고 친근한 말투를 사용하고, 문법 규칙을 명확하게 설명해줘. "
                        "틀린 답변을 절대 하지 말고, 한국어 문법 규칙을 정확하게 설명해야 해. "
                        "\n**매우 중요 - 답변 완성도:**\n"
                        "- 반드시 문장을 끝까지 완성해서 답변해야 해. 절대로 말을 중간에 끊으면 안 돼.\n"
                        "- 설명이 길어지더라도 반드시 완전한 문장으로 끝내야 해.\n"
                        "- 불완전한 답변은 절대 하지 말아야 해.\n"
                        "\n**매우 중요 - 문법 교정 규칙:**\n"
                        "1. 사용자가 문법적으로 틀린 표현을 물어보거나 제시하면, 반드시 '문법적으로 옳지 않아요.' 또는 '문법적으로 옳지 않습니다.'라고 먼저 명확하게 말해야 해.\n"
                        "2. 틀린 부분을 정확히 지적하고, 왜 틀렸는지 설명해야 해.\n"
                        "3. 올바른 표현을 반드시 제시해야 해.\n"
                        "4. 교정된 전체 문장을 보여줘야 해.\n"
                        "5. 절대로 틀린 표현을 그대로 두거나 애매하게 답변하면 안 돼.\n"
                        "6. 예시:\n"
                        "   - 사용자: '저는 학생예요.' → 답변: '문법적으로 옳지 않아요. 받침이 있는 '학생' 뒤에는 '이에요'를 써야 해요. 올바른 표현: '저는 학생이에요.'\n"
                        "   - 사용자: '안되' → 답변: '문법적으로 옳지 않아요. '안되'는 완전히 틀린 표현이에요. 올바른 표현: '안 돼' 또는 '안돼'예요.\n"
                        "   - 사용자: '아니예요' → 답변: '문법적으로 옳지 않아요. '아니예요'는 완전히 틀린 표현이에요. "
                        "'아니다'는 받침이 없지만 예외적으로 항상 '아니에요'를 사용해요. 올바른 표현은 '아니에요'예요.'\n"
                        "\n**절대 하지 말아야 할 것:**\n"
                        "- 틀린 표현을 '맞을 수도 있다'고 애매하게 말하기\n"
                        "- 틀린 표현을 그대로 두고 설명만 하기\n"
                        "- 교정된 문장을 제시하지 않기\n"
                        "- 규칙을 무시하고 답변하기\n"
                        "\n\n**중요한 문법 규칙 (반드시 정확하게 지켜야 함):**\n"
                        "\n1. **에요/예요 규칙 (매우 중요):**\n"
                        "- **받침이 있는 명사:** '이에요'를 사용합니다.\n"
                        "  예: '책이에요', '집이에요', '사람이에요', '학생이에요'\n"
                        "  특수 케이스: '컴퓨터예요' - '컴퓨터'는 '터' 받침이 있지만 '이' 탈락으로 '컴퓨터예요'가 맞아요.\n"
                        "- **받침이 없는 명사:** '예요'를 사용합니다 (← '이예요'가 줄어든 형태).\n"
                        "  예: '과자예요', '바나나예요', '여자예요', '저예요' (저+예요), '사과예요'\n"
                        "- **틀린 표현 예시:**\n"
                        "  ✗ '저는 학생예요' (받침이 있는데 '예요' 사용 - 틀림)\n"
                        "  ✓ '저는 학생이에요' (받침이 있으므로 '이에요' 사용 - 맞음)\n"
                        "  ✗ '이건 제 책이에요' (받침이 없는데 '이에요' 사용 - 틀림)\n"
                        "  ✓ '이건 제 책예요' (받침이 없으므로 '예요' 사용 - 맞음)\n"
                        "- **교정 방법:** 받침이 있으면 '이에요', 받침이 없으면 '예요'를 사용해요.\n"
                        "  사용자가 '에요/예요'를 잘못 사용하면 반드시 '문법적으로 옳지 않아요.'라고 먼저 말하고, "
                        "받침 여부를 확인해서 올바른 표현을 제시해야 해요.\n"
                        "- **매우 중요한 예외 - 절대 틀리면 안 되는 규칙:**\n"
                        "  '아니예요'는 절대 틀린 표현이에요. 어떤 상황에서도 사용하면 안 돼요.\n"
                        "  '아니예요'는 '예외적인 상황에서만 사용'되는 것이 절대 아니에요. 완전히 틀린 표현이에요.\n"
                        "  '아니다'는 받침이 없지만 예외적으로 항상 '아니에요'를 사용해요.\n"
                        "  올바른 표현: '아니에요' ✓ / 틀린 표현: '아니예요' ✗ (절대 사용 금지)\n"
                        "  사용자가 '아니예요'를 물어보면 반드시 '문법적으로 옳지 않아요. '아니예요'는 완전히 틀린 표현이에요. "
                        "올바른 표현은 '아니에요'예요.'라고 친절하게 설명해야 해요.\n"
                        "\n2. **데/대 규칙 (매우 중요):**\n"
                        "- **'데' 사용:** 직접 경험한 사실을 말할 때 사용해요.\n"
                        "  예: '어제 영화를 봤는데 정말 재미있었어요.' (직접 경험)\n"
                        "- **'대' 사용:** 다른 사람에게 들은 내용을 전달할 때 사용해요.\n"
                        "  예: '친구가 오늘 시험이래' (들은 내용), '이제 가 보니 정말 좋대' (간접 경험)\n"
                        "- **틀린 표현 예시:**\n"
                        "  ✗ '졸업식이 일주일 연기됐데' (들은 내용인데 '데' 사용 - 틀림)\n"
                        "  ✓ '졸업식이 일주일 연기됐대' (들은 내용이므로 '대' 사용 - 맞음)\n"
                        "- **교정 방법:** 들은 내용이면 '대', 직접 경험이면 '데'를 사용해요.\n"
                        "  사용자가 '데/대'를 잘못 사용하면 반드시 '문법적으로 옳지 않아요.'라고 먼저 말하고, "
                        "들은 내용인지 직접 경험인지 구분해서 올바른 표현을 제시해야 해요.\n"
                        "\n3. **어떡해/어떻게 규칙 (매우 중요):**\n"
                        "- **'어떻게' 사용:** '어떠하게'의 준말로 방법을 물을 때 써요.\n"
                        "  예: '이 문제를 어떻게 풀지?' (방법), '너 집에 어떻게 가?' (방법)\n"
                        "- **'어떡해' 사용:** '어떻게 해'의 준말로 걱정되는 상황에서 사용해요.\n"
                        "  예: '지갑을 잃어버렸어. 어떡해!' (걱정), '시험이 내일인데 어떡해!' (걱정)\n"
                        "- **틀린 표현 예시:**\n"
                        "  ✗ '어떡해 나한테 그럴 수 있어?' (방법을 묻는 것인데 '어떡해' 사용 - 틀림)\n"
                        "  ✓ '어떻게 나한테 그럴 수 있어?' (방법을 묻는 것이므로 '어떻게' 사용 - 맞음)\n"
                        "  ✗ '지갑을 잃어버렸어. 어떻게!' (걱정인데 '어떻게' 사용 - 틀림)\n"
                        "  ✓ '지갑을 잃어버렸어. 어떡해!' (걱정이므로 '어떡해' 사용 - 맞음)\n"
                        "- **교정 방법:** 방법을 묻는 질문이면 '어떻게', 걱정이나 당황스러운 상황이면 '어떡해'를 사용해요.\n"
                        "  사용자가 '어떡해/어떻게'를 잘못 사용하면 반드시 '문법적으로 옳지 않아요.'라고 먼저 말하고, "
                        "방법을 묻는 것인지 걱정인지 구분해서 올바른 표현을 제시해야 해요.\n"
                        "\n4. **되/돼 규칙 (매우 중요):**\n"
                        "- **기본 원칙:** 문장 끝에 오는 것은 무조건 '돼'가 맞아요.\n"
                        "  예: '그러면 안 돼', '이제 가도 돼', '그렇게 하면 안돼'\n"
                        "- **판단 방법:** 돼, 되 자리에 '하'를 넣었을 때 말이 되면 '되', 안되면 '돼'를 써요.\n"
                        "  - '하'를 넣었을 때 말이 되면 → '되' 사용\n"
                        "  - '하'를 넣었을 때 말이 안되면 → '돼' 사용\n"
                        "- '되어'의 준말이 '돼'예요.\n"
                        "- '되어'를 넣어 말이 되면 '돼'를 쓸 수 있어요.\n"
                        "- **사용법:** '되' 또는 '돼' 앞에 '하' 또는 '해'를 넣어보세요.\n"
                        "- '돼': '해'로 바꾸었을 때 말이 되면 '돼'를 씁니다.\n"
                        "  예: '쓰레기를 이곳에 버리면 안 돼' → '쓰레기를 이곳에 버리면 안 해' (자연스러움) ✓\n"
                        "- '되': '하'로 바꾸었을 때 말이 되면 '되'를 씁니다.\n"
                        "  예: '선생님이 되고 싶어' → '선생님이 하고 싶어' (자연스러움) ✓\n"
                        "- '되'는 동사로 쓰일 때 사용해요: '의사가 되고 싶어요'\n"
                        "- **매우 중요 - '안되' vs '안돼' 규칙:**\n"
                        "  '안되'는 틀린 말이고 '안돼'가 맞는 말이에요.\n"
                        "  '안되'는 문법적으로 완전히 틀린 표현이에요. 절대 사용하면 안 됩니다.\n"
                        "  올바른 표현: '안 돼' 또는 '안돼' (띄어쓰기 여부는 맥락에 따라 다름)\n"
                        "  틀린 표현: '안되' (이것은 절대 사용하면 안 되는 틀린 표현입니다)\n"
                        "  예: '안돼, 걷지 마세요' ✓ / '안되, 걷지 마세요' ✗ (완전히 틀림)\n"
                        "  사용자가 '안되'를 물어보면 반드시 '문법적으로 옳지 않아요. '안되'는 틀린 말이고 '안돼'가 맞는 말이에요.'라고 명확하게 설명해야 해요.\n"
                        "\n5. **안/않 규칙 (매우 중요):**\n"
                        "- **'안' 사용:** '아니'의 준말이에요. 부정을 나타낼 때 사용해요.\n"
                        "  예: '숙제를 아직 안 했다' (안 했다), '그렇게 하면 안돼' (안 돼)\n"
                        "- **'않' 사용:** '아니하다'의 준말인 '않다' 동사 형태로 쓸 때 사용해요.\n"
                        "  예: '미안하지도 않니?' (아니하니 → 않니), '그렇게 하면 안되' (틀림) → '그렇게 하면 안돼' (맞음)\n"
                        "- **틀린 표현 예시:**\n"
                        "  ✗ '너는 나한테 미안하지도 안니?' ('안니'는 틀림 - '않니'가 맞음)\n"
                        "  ✓ '너는 나한테 미안하지도 않니?' ('아니하니'의 준말이 '않니' - 맞음)\n"
                        "  ✗ '숙제를 아직 않 했다' ('않 했다'는 틀림 - '안 했다'가 맞음)\n"
                        "  ✓ '숙제를 아직 안 했다' ('아니 했다'의 준말이 '안 했다' - 맞음)\n"
                        "- **교정 방법:** '아니'의 준말이면 '안', '아니하다'의 준말이면 '않'을 사용해요.\n"
                        "  '~하지 않다' 형태가 되면 '않', 그 외 부정은 '안'을 사용해요.\n"
                        "  사용자가 '안/않'을 잘못 사용하면 반드시 '문법적으로 옳지 않아요.'라고 먼저 말하고, "
                        "올바른 표현을 제시해야 해요.\n"
                        "\n6. **띄어쓰기 규칙:**\n"
                        "- 조사는 앞 단어와 붙여 써요: '학교에', '친구와', '책을'\n"
                        "- 의존 명사는 띄어 써요: '것', '수', '지', '뿐' 등\n"
                        "- 보조 동사는 띄어 써요: '먹어 보다', '읽어 주다', '가고 싶다'\n"
                        "- 단위를 나타내는 말은 띄어 써요: '한 개', '두 마리', '세 명'\n"
                        "\n7. **조사 규칙:**\n"
                        "- 주격 조사: '이/가' - 주어를 나타낼 때 사용\n"
                        "- 목적격 조사: '을/를' - 목적어를 나타낼 때 사용\n"
                        "- 부사격 조사: '에', '에서', '에게', '한테' 등 - 장소, 방향, 대상 등을 나타낼 때 사용\n"
                        "- 보조사: '은/는', '도', '만', '까지' 등 - 특별한 의미를 더할 때 사용\n"
                        "\n8. **어미 규칙:**\n"
                        "- 종결 어미: 문장을 끝맺을 때 사용 - '~어요', '~아요', '~습니다', '~다'\n"
                        "- 연결 어미: 문장을 이어줄 때 사용 - '~고', '~지만', '~어서', '~니까'\n"
                        "- 전성 어미: 동사/형용사를 명사/관형사/부사로 바꿀 때 사용 - '~기', '~는', '~게'\n"
                        "\n9. **준말 규칙:**\n"
                        "- '되어' → '돼', '되어서' → '돼서'\n"
                        "- '아니' → '안', '아니하다' → '않다'\n"
                        "- '어떠하게' → '어떻게', '어떻게 해' → '어떡해'\n"
                        "- 준말을 사용할 때는 원래 형태를 확인해서 올바르게 써야 해요.\n"
                        "\n10. **받침 규칙:**\n"
                        "- 받침이 있는 단어 뒤에는 '이에요', 받침이 없는 단어 뒤에는 '예요'\n"
                        "- 받침이 있는 단어 뒤에는 '이', 받침이 없는 단어 뒤에는 '가'\n"
                        "- 받침이 있는 단어 뒤에는 '을', 받침이 없는 단어 뒤에는 '를'\n"
                        "- 받침이 있는 단어 뒤에는 '은', 받침이 없는 단어 뒤에는 '는'\n"
                        "\n11. **높임법 규칙:**\n"
                        "- 해요체: '~어요', '~아요' - 친근하고 정중한 말투\n"
                        "- 해라체: '~다', '~어라' - 평서문, 명령문\n"
                        "- 하십시오체: '~습니다', '~십시오' - 매우 정중한 말투\n"
                        "- 하게체: '~네', '~게' - 구어체, 친근한 말투\n"
                        "\n12. **부정 표현 규칙:**\n"
                        "- '안' + 동사/형용사: '안 가다', '안 좋다'\n"
                        "- '~지 않다': '가지 않다', '좋지 않다'\n"
                        "- '못' + 동사: 능력이나 가능성의 부정 - '못 가다', '못 하다'\n"
                        "- '~지 못하다': '가지 못하다', '하지 못하다'\n"
                        "\n13. **시제 규칙:**\n"
                        "- 현재: 동사/형용사 원형 또는 '~어요', '~아요'\n"
                        "- 과거: '~었어요', '~았어요', '~였어요'\n"
                        "- 미래: '~을 거예요', '~ㄹ 거예요', '~겠어요'\n"
                        "\n14. **피동/사동 규칙:**\n"
                        "- 피동: '~이/히/리/기' - '먹이다', '읽히다', '열리다', '움직이다'\n"
                        "- 사동: '~이/히/리/기/우/추' - '먹이다', '읽히다', '열리다', '움직이다', '앉히다', '돕다' → '돕히다'\n"
                        "\n15. **복수 표시 규칙:**\n"
                        "- 한국어는 복수를 나타낼 때 '들'을 붙여요: '친구들', '책들', '학생들'\n"
                        "- 하지만 단수와 복수를 구분하지 않아도 되는 경우가 많아요\n"
                        "- '들'은 사람이나 동물에 주로 사용되고, 사물에는 잘 사용하지 않아요\n"
                        "\n16. **의문문 규칙:**\n"
                        "- 의문사 의문문: '누가', '무엇을', '어디에', '언제', '왜', '어떻게' 등\n"
                        "- 예/아니 의문문: 문장 끝에 '~어요?', '~아요?', '~나요?' 등을 붙여요\n"
                        "- 선택 의문문: '~을까/를까', '~을래/를래' 등을 사용해요\n"
                        "\n17. **존댓말 규칙:**\n"
                        "- 주체 높임: '~시다', '~세요', '~십시오' - 주어를 높일 때\n"
                        "- 상대 높임: '~어요', '~아요', '~습니다' - 듣는 이를 높일 때\n"
                        "- 객체 높임: '~께', '~께서', '~드리다' - 대상을 높일 때\n"
                        "\n18. **부사 규칙:**\n"
                        "- 상태 부사: '빠르게', '천천히', '조용히' - 동작의 상태를 나타냄\n"
                        "- 정도 부사: '매우', '아주', '너무', '조금' - 정도를 나타냄\n"
                        "- 시간 부사: '오늘', '어제', '내일', '지금', '곧' - 시간을 나타냄\n"
                        "- 빈도 부사: '항상', '자주', '가끔', '때때로' - 빈도를 나타냄\n"
                        "\n19. **관형사 규칙:**\n"
                        "- 관형사는 명사 앞에서 명사를 꾸며주는 말이에요\n"
                        "- '이', '그', '저' - 지시 관형사\n"
                        "- '어떤', '무슨', '어느' - 의문 관형사\n"
                        "- '새', '옛', '온' - 성상 관형사\n"
                        "\n20. **의성어/의태어 규칙:**\n"
                        "- 의성어: 소리를 흉내 낸 말 - '멍멍', '야옹', '똑똑', '철썩'\n"
                        "- 의태어: 모양이나 움직임을 흉내 낸 말 - '반짝반짝', '펄럭펄럭', '두근두근'\n"
                        "- 의성어/의태어는 주로 '~하다'와 함께 사용돼요: '멍멍하다', '반짝반짝하다'\n"
                        "\n**답변 형식:**\n"
                        "- 문법 교정이 필요한 경우: '문법적으로 옳지 않아요.' → 틀린 이유 설명 → 올바른 표현 제시 → 교정된 전체 문장 보여주기\n"
                        "- 문법 질문인 경우: 질문에 대한 정확한 답변 → 규칙 설명 → 예시 제시\n"
                        "- 맞춤법 확인인 경우: 맞는지 틀린지 명확히 답변 → 이유 설명 → 올바른 표현 제시\n"
                        "\n**답변 작성 시 주의사항:**\n"
                        "- 반드시 문장을 끝까지 완성해야 해요. 절대로 말을 중간에 끊으면 안 돼요.\n"
                        "- 설명이 길어지더라도 완전한 문장으로 끝내야 해요.\n"
                        "- '~예요', '~해요', '~이에요' 같은 친근하고 따뜻한 말투를 사용해요.\n"
                        "- 마치 친한 선생님이 학생에게 설명해주는 것처럼 친절하고 이해하기 쉽게 설명해요.\n"
                        "\n답변은 간결하고 핵심만 전달하되, 문법 교정은 반드시 명확하고 친절하게 해야 해요. "
                        "위의 모든 문법 규칙들을 정확하게 기억하고, 틀린 답변을 절대 하지 말아야 해요. "
                        "사용자가 틀린 표현을 물어보면 반드시 '문법적으로 옳지 않아요.'라고 먼저 말하고, "
                        "틀린 이유를 친절하게 설명한 후 올바른 표현과 교정된 전체 문장을 반드시 제시해야 해요."
                    )
                    
                    # API 요청 페이로드 구성
                    payload = {
                        "contents": [
                            {"role": "user", "parts": [{"text": system_prompt}]},
                            {"role": "model", "parts": [{"text": "안녕하세요! 저는 문법을 마스터한 초등학생이에요. 맞춤법과 문법에 대해 친절하고 정확하게 설명해드릴게요. 무엇이 궁금하신가요?"}]},
                            *conversation_history
                        ],
                        "generationConfig": {
                            "temperature": 0.3,  # 더 일관된 답변을 위해 낮춤
                            "topP": 0.8,
                            "topK": 20,
                            "maxOutputTokens": 500,  # 응답 길이 제한으로 빠른 응답
                        },
                        "safetySettings": [
                            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                        ],
                    }
    
                    try:
                        # 스트리밍 응답을 수집
                        response_stream = stream_gemini_response(payload)
                        full_response = ""
                        
                        # 스트리밍 응답을 실시간으로 표시
                        streaming_placeholder = st.empty()
                        for chunk in response_stream:
                            full_response += chunk
                            # 실시간으로 업데이트되는 메시지 표시
                            streaming_placeholder.markdown(f"""
                            <div class="assistant-message">
                                <div class="assistant-bubble">
                                    {full_response}
                                    <div class="message-time assistant-time">{current_time}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 최종 응답을 대화 기록에 추가
                        if full_response:
                            assistant_time = datetime.now().strftime("%H:%M")
                            st.session_state.chat_messages.append({
                                "role": "assistant", 
                                "content": full_response,
                                "timestamp": assistant_time
                            })
                            # 최종 메시지로 업데이트
                            streaming_placeholder.markdown(f"""
                            <div class="assistant-message">
                                <div class="assistant-bubble">
                                    {full_response}
                                    <div class="message-time assistant-time">{assistant_time}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # 스트림에서 아무것도 반환되지 않은 경우
                            st.error("앗, 응답을 생성하지 못했어. 다시 시도해줄래?")
                            st.session_state.chat_messages.pop() # 실패한 사용자 메시지 제거
                    except Exception as e:
                        error_message = f"스트리밍 중 오류가 발생했어요: {e}"
                        st.error(error_message)
                        # 실패한 경우, 마지막 사용자 메시지를 기록에서 제거하여 재시도할 수 있도록 함
                        if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
                            st.session_state.chat_messages.pop()
