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
            '받침이 있으면 **\'이에요\'**, 받침이 없으면 **\'예요\'**를 써요.\n\n하지만 **\'아니다\'**는 무조건 **\'아니에요\'**가 맞아요! (줄여서 \'아녜요\'도 O) 그 이유가 궁금한 학생은 선생님과 함께 탐구해볼까요?',
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
        # 이에요/예요
        {'오류 유형': '에요/예요', '문제': '내가 가장 좋아하는 색깔은 노랑[이에요/예요].', '정답': '내가 가장 좋아하는 색깔은 노랑이에요.', '오답들': ['내가 가장 좋아하는 색깔은 노랑예요.']},
        {'오류 유형': '에요/예요', '문제': '저 푸들은 우리집 강아지[이에요/예요].', '정답': '저 푸들은 우리집 강아지예요.', '오답들': ['저 푸들은 우리집 강아지이에요.']},
        {'오류 유형': '에요/예요', '문제': '제가 가장 아끼는 물건은 이 가방[이에요/예요].', '정답': '제가 가장 아끼는 물건은 이 가방이에요.', '오답들': ['제가 가장 아끼는 물건은 이 가방예요.']},
        {'오류 유형': '에요/예요', '문제': '이 꽃은 장미[이에요/예요].', '정답': '이 꽃은 장미예요.', '오답들': ['이 꽃은 장미이에요.']},
        {'오류 유형': '에요/예요', '문제': '제 이름은 닉[이에요/예요].', '정답': '제 이름은 닉이에요.', '오답들': ['제 이름은 닉예요.']},
        # 데/대
        {'오류 유형': '데/대', '문제': '철수가 그러는데, 이 식당 음식이 정말 맛있[데/대].', '정답': '철수가 그러는데, 이 식당 음식이 정말 맛있대.', '오답들': ['철수가 그러는데, 이 식당 음식이 정말 맛있데.']},
        {'오류 유형': '데/대', '문제': '서현이가 그 카페는 분위기가 참 좋[데/대].', '정답': '서현이가 그 카페는 분위기가 참 좋대.', '오답들': ['서현이가 그 카페는 분위기가 참 좋데.']},
        {'오류 유형': '데/대', '문제': '주디는 경찰이 되고 싶[데/대].', '정답': '주디는 경찰이 되고 싶대.', '오답들': ['주디는 경찰이 되고 싶데.']},
        {'오류 유형': '데/대', '문제': '벌써 그렇게 시간이 많이 흘렀[데/대]요?', '정답': '벌써 그렇게 시간이 많이 흘렀대요?', '오답들': ['벌써 그렇게 시간이 많이 흘렀데요?']},
        {'오류 유형': '데/대', '문제': '오즈의 마법사는 마술을 정말 잘한 [데/대].', '정답': '오즈의 마법사는 마술을 정말 잘한 대.', '오답들': ['오즈의 마법사는 마술을 정말 잘한 데.']},
        # 어떡해/어떻게
        {'오류 유형': '어떡해/어떻게', '문제': '갑자기 비가 오는데, 우산이 없으니 [어떡해/어떻게] 해야 할까?', '정답': '갑자기 비가 오는데, 우산이 없으니 어떻게 해야 할까?', '오답들': ['갑자기 비가 오는데, 우산이 없으니 어떡해 해야 할까?']},
        {'오류 유형': '어떡해/어떻게', '문제': '지각인데, 이젠 정말 [어떡해/어떻게]?', '정답': '지각인데, 이젠 정말 어떡해?', '오답들': ['지각인데, 이젠 정말 어떻게?']},
        {'오류 유형': '어떡해/어떻게', '문제': '내일은 날씨가 [어떡해/어떻게] 될지 궁금하다.', '정답': '내일은 날씨가 어떻게 될지 궁금하다.', '오답들': ['내일은 날씨가 어떡해 될지 궁금하다.']},
        {'오류 유형': '어떡해/어떻게', '문제': '네가 그럴 수 있니, [어떡해/어떻게] 나한테 이래!', '정답': '네가 그럴 수 있니, 어떻게 나한테 이래!', '오답들': ['네가 그럴 수 있니, 어떡해 나한테 이래!']},
        {'오류 유형': '어떡해/어떻게', '문제': '친구와 다퉜는데, 화해를 [어떡해/어떻게] 시켜야 할지 모르겠다.', '정답': '친구와 다퉜는데, 화해를 어떻게 시켜야 할지 모르겠다.', '오답들': ['친구와 다퉜는데, 화해를 어떡해 시켜야 할지 모르겠다.']},
        # 되/돼
        {'오류 유형': '되/돼', '문제': '이제 곧 방학이 [되/돼]니까 계획을 세워야지.', '정답': '이제 곧 방학이 되니까 계획을 세워야지.', '오답들': ['이제 곧 방학이 돼니까 계획을 세워야지.']},
        {'오류 유형': '되/돼', '문제': '그렇게 하면 안 [되/돼].', '정답': '그렇게 하면 안 돼.', '오답들': ['그렇게 하면 안 되.']},
        {'오류 유형': '되/돼', '문제': '예진이는 간절한 바람 끝에 회장이 [되/돼]었다.', '정답': '예진이는 간절한 바람 끝에 회장이 되었다.', '오답들': ['예진이는 간절한 바람 끝에 회장이 돼었다.']},
        {'오류 유형': '되/돼', '문제': '늦지 않으려면 빨리 출발해야 [되/돼]요.', '정답': '늦지 않으려면 빨리 출발해야 돼요.', '오답들': ['늦지 않으려면 빨리 출발해야 되요.']},
        {'오류 유형': '되/돼', '문제': '열심히 노력하면 무엇이든 이룰 수 있게 [될/됄]거야.', '정답': '열심히 노력하면 무엇이든 이룰 수 있게 될거야.', '오답들': ['열심히 노력하면 무엇이든 이룰 수 있게 됄거야.']},
        # 안/않
        {'오류 유형': '안/않', '문제': '나는 숙제를 [안/않] 했다.', '정답': '나는 숙제를 안 했다.', '오답들': ['나는 숙제를 않 했다.']},
        {'오류 유형': '안/않', '문제': '몸이 좋지 [안/않]아서 병원에 갔다.', '정답': '몸이 좋지 않아서 병원에 갔다.', '오답들': ['몸이 좋지 안아서 병원에 갔다.']},
        {'오류 유형': '안/않', '문제': '그 소식은 확실하지 [안/않]다.', '정답': '그 소식은 확실하지 않다.', '오답들': ['그 소식은 확실하지 안다.']},
        {'오류 유형': '안/않', '문제': '그 문제는 해결하기 쉽지 [안/않]았다.', '정답': '그 문제는 해결하기 쉽지 않았다.', '오답들': ['그 문제는 해결하기 쉽지 안았다.']},
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
    
    # 챗봇 대화 초기화 버튼
    st.markdown("---")
    if st.button("🔄 챗봇 대화 초기화", use_container_width=True, type="secondary"):
        if 'chat_messages' in st.session_state:
            st.session_state.chat_messages = []
        if 'current_quiz_question' in st.session_state:
            st.session_state.current_quiz_question = None
        if 'asked_questions' in st.session_state:
            st.session_state.asked_questions = []
        st.rerun()

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

def generate_question():
    """랜덤 퀴즈 문제를 생성합니다."""
    # "도전! 문법 퀴즈"에서는 구분 방법 질문 제외
    filtered_quiz_df = st.session_state.quiz_df[
        ~st.session_state.quiz_df['문제'].isin([
            '되/돼를 구분하는 방법은 무엇인가요?',
            '이에요, 예요를 구분하는 방법은 무엇인가요?'
        ])
    ]
    
    # 퀴즈 데이터에서 랜덤으로 문제 샘플링
    quiz_question_series = filtered_quiz_df.sample(1).iloc[0]
    rule_info_series = st.session_state.grammar_df[st.session_state.grammar_df['오류 유형'] == quiz_question_series['오류 유형']].iloc[0]
    
    question_data = quiz_question_series.to_dict()
    question_data['규칙 설명'] = rule_info_series['규칙 설명']
    st.session_state.current_question = question_data

def generate_question_from_incorrect():
    """틀린 문제 목록에서 랜덤으로 문제를 생성합니다."""
    incorrect_questions = st.session_state.get('incorrect_questions', [])
    if len(incorrect_questions) == 0:
        return False
    
    # 오답 목록에서 랜덤으로 선택
    selected_incorrect = random.choice(incorrect_questions)
    
    # 규칙 설명 추가
    rule_info_series = st.session_state.grammar_df[st.session_state.grammar_df['오류 유형'] == selected_incorrect['오류 유형']].iloc[0]
    question_data = selected_incorrect.copy()
    question_data['규칙 설명'] = rule_info_series['규칙 설명']
    
    # user_wrong_answer는 제거 (새로운 문제로)
    if 'user_wrong_answer' in question_data:
        del question_data['user_wrong_answer']
    
    st.session_state.current_question = question_data
    return True

with st.container(border=True):
    st.write("아래 버튼을 눌러 나의 문법 실력을 테스트해 보세요. 올바른 문장을 선택하면 됩니다.")
    st.write("문법에 자신감이 생길때까지 '새로운 문제 퀴즈' 풀기 버튼을 눌러 학습해봅시다! 버튼을 누르면 문제가 랜덤으로 나와요!")

    if st.button("🎲 새로운 퀴즈 풀기!", use_container_width=True):
        generate_question()
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
            💡 <strong>알맞은 답을 고르면 다음 문제로 넘어가고, 틀린 답을 고르면 나만의 오답노트가 생성돼요!</strong>
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
                    else:
                        st.session_state.answer_feedback = "incorrect"
                        st.session_state.answer_feedback_question_id = question_id
                        # 오답 기록
                        st.session_state.quiz_history.append(question_data['오류 유형'])
                        # 중복되지 않게 오답 목록에 추가
                        is_duplicate = any(
                            q.get('문제') == question_data.get('문제') 
                            for q in st.session_state.incorrect_questions
                        )
                        if not is_duplicate:
                            # 오답 문제를 복사해서 저장
                            incorrect_q = question_data.copy()
                            incorrect_q['user_wrong_answer'] = user_answer
                            st.session_state.incorrect_questions.append(incorrect_q)
                    
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
                
                # 다음 문제 풀기 버튼
                next_question_key = f"next_question_{question_id}"
                if st.button("다음 문제 풀기", key=next_question_key, type="primary", use_container_width=True):
                    # 상태 초기화
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
                    # last_rerun_key도 정리
                    last_rerun_key = f"last_rerun_{question_id}"
                    if last_rerun_key in st.session_state:
                        del st.session_state[last_rerun_key]
                    # 피드백 상태 초기화
                    if 'answer_feedback' in st.session_state:
                        del st.session_state['answer_feedback']
                    if 'answer_feedback_question_id' in st.session_state:
                        del st.session_state['answer_feedback_question_id']
                    # 다음 랜덤 문제 생성
                    generate_question()
                    st.rerun()
            elif feedback_type == "incorrect":
                st.error(f"❌ 아쉬워요, 정답은 **'{question_data['정답']}'** 입니다.")
                if submitted_answer:
                    st.warning(f"선택하신 답: **'{submitted_answer}'**")
                
                # 오답 설명 섹션
                confirm_key = f"confirm_incorrect_{question_id}"
                show_explanation = st.session_state.get(f"show_explanation_{question_id}", True)
                
                if show_explanation:
                    st.markdown("---")
                    with st.container(border=True):
                        st.markdown("##### 🔍 왜 틀렸을까요?")
                        st.markdown(f"**💡 {question_data['오류 유형']} 규칙**")
                        with st.container(border=True):
                            st.info(f"**규칙 설명:** {question_data['규칙 설명']}")
                            st.markdown("---")
                            st.success(f"**✅ 올바른 답:** {question_data['정답']}")
                            if submitted_answer:
                                st.error(f"**❌ 내가 선택한 답:** {submitted_answer}")
                                # 선택한 답이 왜 틀렸는지 구체적으로 설명
                                error_type = question_data['오류 유형']
                                explanation = ""
                                if error_type == "데/대":
                                    explanation = "**왜 틀렸나요?** '데'는 직접 경험한 사실을 말할 때, '대'는 다른 사람에게 들은 내용을 전달할 때 사용해요. 이 문제에서는 들은 내용이므로 '대'를 써야 해요."
                                elif error_type == "에요/예요":
                                    explanation = "**왜 틀렸나요?** 받침이 있으면 '이에요', 받침이 없으면 '예요'를 써요. '아니예요'는 항상 틀린 표현이고, '아니에요'가 맞아요."
                                elif error_type == "어떡해/어떻게":
                                    explanation = "**왜 틀렸나요?** '어떻게'는 방법을 물을 때, '어떡해'는 걱정되는 상황에서 사용해요. 이 문제의 맥락에 맞는 표현을 선택해야 해요."
                                elif error_type == "되/돼":
                                    explanation = "**왜 틀렸나요?** '되'와 '돼'를 구분하려면 '하' 또는 '해'를 넣어보세요. '해'로 바꿨을 때 말이 되면 '돼', '하'로 바꿨을 때 말이 되면 '되'를 써요. '안되'는 항상 틀린 표현이에요."
                                elif error_type == "안/않":
                                    explanation = "**왜 틀렸나요?** '안'은 '아니'의 준말이고, '않'은 '아니하다'의 준말이에요. '~하지 않다' 형태가 되면 '않', 그 외 부정은 '안'을 사용해요."
                                
                                if explanation:
                                    st.markdown(explanation)
                            # 추가 설명
                            st.markdown("---")
                            st.markdown("**📚 기억하기:** 이 규칙을 다시 한번 확인하고 다음 문제에 적용해보세요!")
                    
                    # 이어서 문제 풀기 버튼 (왜 틀렸을까요? 섹션 이후에 배치)
                    if st.button("이어서 문제 풀기", key=confirm_key, type="primary", use_container_width=True):
                        # 버튼을 누르면 규칙 제시 부분 없애고 다음 문제로 이동
                        st.session_state[f"is_submitted_{question_id}"] = False
                        st.session_state[f"submitted_answer_{question_id}"] = None
                        st.session_state[f"show_explanation_{question_id}"] = False
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
                        generate_question()
                        st.rerun()

# --- 6. 나만의 오답 노트 ---
# 오답이 있으면 오답 노트 표시
incorrect_count = len(st.session_state.get('incorrect_questions', []))
if incorrect_count > 0:
    st.markdown("---")
    st.subheader("📓 나만의 비밀 오답 노트")

    with st.container(border=True):
        st.write(f"틀렸던 문제 **{incorrect_count}개**")
        
        # 틀린 문제 다시 풀기 버튼
        col_retry1, col_retry2 = st.columns([1, 1])
        with col_retry1:
            if st.button("🔄 틀린 문제 다시 풀기", use_container_width=True, type="primary"):
                if generate_question_from_incorrect():
                    # 이전 답변 결과 메시지 초기화
                    if 'answer_feedback' in st.session_state:
                        del st.session_state['answer_feedback']
                    st.rerun()
                else:
                    st.warning("틀린 문제가 없어요. 먼저 퀴즈를 풀어보세요!")
        
        with col_retry2:
            if st.button("🎲 새로운 랜덤 문제", use_container_width=True):
                generate_question()
                # 이전 답변 결과 메시지 초기화
                if 'answer_feedback' in st.session_state:
                    del st.session_state['answer_feedback']
                st.rerun()
        
        # 오답 유형 분석 그래프 (약점 분석 통합)
        if st.session_state.quiz_history:
            col1, col2 = st.columns(2)

            with col1:
                with st.container(border=True):
                    st.markdown("##### 📊 오답 유형 분포")
                    incorrect_df = pd.DataFrame(st.session_state.quiz_history, columns=['오류 유형'])
                    chart_data = incorrect_df['오류 유형'].value_counts()
                    st.bar_chart(chart_data, color="#FF4B4B")

            with col2:
                with st.container(border=True):
                    st.markdown("##### 💡 가장 많이 틀린 유형")
                    if not chart_data.empty:
                        most_common_error = chart_data.index[0]
                        st.warning(f"**'{most_common_error}'** 유형을 가장 많이 틀렸어요!")

                        # 해당 규칙 정보 가져오기
                        rule_info = st.session_state.grammar_df[st.session_state.grammar_df['오류 유형'] == most_common_error].iloc[0]
                        with st.container(border=True):
                            st.info(f"**규칙:** {rule_info['규칙 설명']}")
                            st.success(f"**올바른 예시:** {rule_info['예시 (맞는 문장)']}")
                            st.error(f"**틀린 예시:** {rule_info['예시 (틀린 문장)']}")
        
        # 오답 목록
        with st.expander(f"📋 오답 목록 보기 ({incorrect_count}개)", expanded=False):
            for i, q in enumerate(st.session_state.incorrect_questions):
                with st.container(border=True):
                    st.markdown(f"**{i+1}. [{q['오류 유형']}]** {q['문제']}")
                    st.write(f"**정답:** {q['정답']}")
                    if 'user_wrong_answer' in q:
                        st.write(f"**내가 선택한 답:** ~~{q['user_wrong_answer']}~~ ❌")
                    st.caption(f"규칙: {q.get('규칙 설명', '')[:50]}...")

        if st.button("🗑️ 오답 노트 초기화", use_container_width=True):
            st.session_state.incorrect_questions = []
            st.session_state.quiz_history = []
            st.session_state.current_question = None
            if 'answer_feedback' in st.session_state:
                del st.session_state['answer_feedback']
            st.success("오답 노트가 초기화되었습니다!")
            st.rerun()

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
            저와 함께 맞춤법을 얼마나 이해했는지 확인해보아요!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 챗봇 설명
    st.info("💡 챗봇이 문법 문제를 제시하면, 여러분이 답변해주세요! 정답 여부를 확인하고 친절하게 설명해드릴게요.")

# API 키 확인
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "여기에 실제 구글 API 키를 입력하세요":
    st.error("앗! 구글 API 키가 설정되지 않았어요. .env 파일을 확인해주세요.")
else:
    # 세션 상태에 대화 기록 및 문제 상태 초기화
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "current_quiz_question" not in st.session_state:
        st.session_state.current_quiz_question = None
    if "asked_questions" not in st.session_state:
        st.session_state.asked_questions = []  # 이미 제시한 문제 목록
    if "quiz_questions_data" not in st.session_state:
        # 문제 데이터를 챗봇에게 제공할 형식으로 변환
        quiz_list = []
        for idx, row in st.session_state.quiz_df.iterrows():
            quiz_list.append({
                "문제": row['문제'],
                "정답": row['정답'],
                "오류 유형": row['오류 유형']
            })
        st.session_state.quiz_questions_data = quiz_list
    
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
    
    # 챗봇이 문제를 제시하지 않았으면 첫 문제 제시
    if not st.session_state.chat_messages:
        # 랜덤 문제 선택 (이미 제시한 문제 제외)
        import random
        available_questions = [q for q in st.session_state.quiz_questions_data 
                             if q['문제'] not in st.session_state.asked_questions]
        if not available_questions:
            # 모든 문제를 다 제시했으면 초기화
            st.session_state.asked_questions = []
            available_questions = st.session_state.quiz_questions_data
        
        current_question = random.choice(available_questions)
        st.session_state.current_quiz_question = current_question
        st.session_state.asked_questions.append(current_question['문제'])  # 제시한 문제 기록
        
        # 챗봇이 문제 제시
        question_text = f"안녕하세요! 문법 문제를 풀어볼까요? 😊\n\n**문제:** {current_question['문제']}\n\n아래 버튼 중에서 올바른 표현을 선택해주세요!"
        current_time = datetime.now().strftime("%H:%M")
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": question_text,
            "timestamp": current_time,
            "question_data": current_question
        })
        st.rerun()
    
    # 현재 문제 데이터 가져오기
    current_question_data = None
    for msg in reversed(st.session_state.chat_messages):
        if msg.get("question_data"):
            current_question_data = msg["question_data"]
            break
    
    # 문제가 있고 아직 답변이 없거나 "다시 시도해보세요" 또는 "모르겠어요" 관련 메시지면 선택지 버튼 표시
    if current_question_data and st.session_state.chat_messages:
        last_message = st.session_state.chat_messages[-1]
        # 마지막 메시지가 챗봇의 문제 제시이거나 "다시 시도해보세요" 또는 규칙 설명 후 재시도 메시지면 버튼 표시
        show_buttons = (last_message["role"] == "assistant" and "문제:" in last_message["content"]) or \
                       (last_message["role"] == "assistant" and "다시 시도해보세요" in last_message["content"]) or \
                       (last_message["role"] == "assistant" and "다시 선택해주세요" in last_message["content"]) or \
                       (last_message["role"] == "assistant" and "이제 다시 정답을 선택해볼까요?" in last_message["content"])
        
        if show_buttons:
            # 선택지 생성 (정답 1개 + 오답 1개 + '모르겠어요')
            import random
            correct_answer = current_question_data['정답']
            wrong_answers = current_question_data.get('오답들', [])
            
            # 틀린 문장(오답) 확보 - 현재 문제와 관련된 틀린 문장만 사용
            wrong_answer = None
            
            # 1. 먼저 문제 데이터에 있는 오답 사용 (현재 문제의 틀린 문장 예시)
            if len(wrong_answers) > 0:
                wrong_answer = wrong_answers[0]
            else:
                # 2. 문제 데이터에 오답이 없으면 정답을 변형해서 현재 문제와 관련된 틀린 문장 생성
                # 문제 텍스트에서 [선택지] 부분을 찾아서 반대 선택지로 변형
                problem_text = current_question_data['문제']
                correct_text = current_question_data['정답']
                
                # 문제에서 선택지 부분 찾기
                if '[이에요/예요]' in problem_text or '[예요/이에요]' in problem_text:
                    if '이에요' in correct_text:
                        wrong_answer = correct_text.replace('이에요', '예요')
                    elif '예요' in correct_text:
                        wrong_answer = correct_text.replace('예요', '이에요')
                elif '[데/대]' in problem_text or '[대/데]' in problem_text:
                    if '데' in correct_text:
                        wrong_answer = correct_text.replace('데', '대')
                    elif '대' in correct_text:
                        wrong_answer = correct_text.replace('대', '데')
                elif '[어떡해/어떻게]' in problem_text or '[어떻게/어떡해]' in problem_text:
                    if '어떻게' in correct_text:
                        wrong_answer = correct_text.replace('어떻게', '어떡해')
                    elif '어떡해' in correct_text:
                        wrong_answer = correct_text.replace('어떡해', '어떻게')
                elif '[되/돼]' in problem_text or '[돼/되]' in problem_text or '[될/됄]' in problem_text or '[됄/될]' in problem_text:
                    if '되' in correct_text and '돼' not in correct_text:
                        wrong_answer = correct_text.replace('되', '돼')
                    elif '돼' in correct_text:
                        wrong_answer = correct_text.replace('돼', '되')
                    elif '될' in correct_text:
                        wrong_answer = correct_text.replace('될', '됄')
                    elif '됄' in correct_text:
                        wrong_answer = correct_text.replace('됄', '될')
                elif '[안/않]' in problem_text or '[않/안]' in problem_text:
                    if '안' in correct_text and '않' not in correct_text:
                        wrong_answer = correct_text.replace('안', '않')
                    elif '않' in correct_text:
                        wrong_answer = correct_text.replace('않', '안')
                
                # 변형이 실패했거나 정답과 같으면 다른 방법 시도
                if wrong_answer is None or wrong_answer == correct_answer:
                    # 정답에서 직접 변형 시도
                    variations = [
                        correct_text.replace('예요', '에요'),
                        correct_text.replace('에요', '예요'),
                        correct_text.replace('이에요', '예요'),
                        correct_text.replace('예요', '이에요'),
                        correct_text.replace('되', '돼'),
                        correct_text.replace('돼', '되'),
                        correct_text.replace('어떻게', '어떡해'),
                        correct_text.replace('어떡해', '어떻게'),
                        correct_text.replace('데', '대'),
                        correct_text.replace('대', '데'),
                        correct_text.replace('안', '않'),
                        correct_text.replace('않', '안'),
                    ]
                    for var in variations:
                        if var != correct_text and len(var) > 0:
                            wrong_answer = var
                            break
            
            # 최종 확인: 틀린 문장이 정답과 다르도록 보장
            if wrong_answer is None or wrong_answer == correct_answer:
                # 강제로 다른 문장 생성 (현재 문제의 정답을 약간 변형)
                wrong_answer = correct_text.replace('이에요', '예요').replace('예요', '이에요').replace('되', '돼').replace('돼', '되')
                if wrong_answer == correct_text:
                    wrong_answer = "틀린 문장입니다"
            
            # 틀린 문장(오답) 1개 + 정답 1개 + '모르겠어요'로 구성
            options = [wrong_answer, correct_answer, "모르겠어요"]
            random.shuffle(options)
            
            # 정답 인덱스와 모르겠어요 인덱스 저장
            correct_index = options.index(correct_answer)
            dont_know_index = options.index("모르겠어요")
            
            # 버튼으로 선택지 표시
            st.markdown("**답을 선택해주세요:**")
            col1, col2, col3 = st.columns(3)
            
            # 각 버튼에 대한 정답 여부 확인 및 처리
            button_keys = [
                f"answer_btn_0_{hash(current_question_data['문제'])}",
                f"answer_btn_1_{hash(current_question_data['문제'])}",
                f"answer_btn_2_{hash(current_question_data['문제'])}"
            ]
            
            def handle_button_click(button_index, selected_option):
                """버튼 클릭 처리 함수"""
                current_time = datetime.now().strftime("%H:%M")
                
                # 사용자 메시지로 대화창에 표시
                user_message = {"role": "user", "content": selected_option, "timestamp": current_time}
                st.session_state.chat_messages.append(user_message)
                
                if button_index == dont_know_index:
                    # 모르겠어요 버튼 처리
                    # 관련 규칙 가져오기
                    rule_info_series = st.session_state.grammar_df[
                        st.session_state.grammar_df['오류 유형'] == current_question_data['오류 유형']
                    ].iloc[0]
                    
                    rule_message = f"💡 **{current_question_data['오류 유형']} 규칙**\n\n"
                    rule_message += f"**규칙 설명:** {rule_info_series['규칙 설명']}\n\n"
                    rule_message += f"**올바른 예시:** {rule_info_series['예시 (맞는 문장)']}\n\n"
                    rule_message += f"**틀린 예시:** {rule_info_series['예시 (틀린 문장)']}\n\n"
                    rule_message += "이제 다시 정답을 선택해볼까요? 😊"
                    
                    assistant_time = datetime.now().strftime("%H:%M")
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": rule_message,
                        "timestamp": assistant_time
                    })
                    st.rerun()
                elif button_index == correct_index:
                    # 정답 처리
                    feedback_message = {"role": "assistant", "content": "정답입니다! 🎉", "timestamp": current_time}
                    st.session_state.chat_messages.append(feedback_message)
                    
                    # 다음 문제 제시 (이미 제시한 문제 제외)
                    available_questions = [q for q in st.session_state.quiz_questions_data 
                                         if q['문제'] not in st.session_state.asked_questions]
                    if not available_questions:
                        # 모든 문제를 다 제시했으면 초기화
                        st.session_state.asked_questions = []
                        available_questions = st.session_state.quiz_questions_data
                    
                    if available_questions:
                        next_question = random.choice(available_questions)
                        st.session_state.current_quiz_question = next_question
                        st.session_state.asked_questions.append(next_question['문제'])  # 제시한 문제 기록
                        next_question_text = f"다음 문제예요! 😊\n\n**문제:** {next_question['문제']}\n\n아래 버튼 중에서 올바른 표현을 선택해주세요!"
                        next_time = datetime.now().strftime("%H:%M")
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": next_question_text,
                            "timestamp": next_time,
                            "question_data": next_question
                        })
                    st.rerun()
                else:
                    # 오답 처리
                    feedback_message = {"role": "assistant", "content": "다시 시도해보세요 😊", "timestamp": current_time}
                    st.session_state.chat_messages.append(feedback_message)
                    st.rerun()
            
            with col1:
                if st.button(options[0], key=button_keys[0], use_container_width=True):
                    handle_button_click(0, options[0])
            
            with col2:
                if st.button(options[1], key=button_keys[1], use_container_width=True):
                    handle_button_click(1, options[1])
            
            with col3:
                if st.button(options[2], key=button_keys[2], use_container_width=True):
                    handle_button_click(2, options[2])
    
    # 버튼 클릭으로 답변이 처리되므로 Gemini 응답 생성은 제거
    # (버튼 클릭 시 즉시 피드백 제공)
