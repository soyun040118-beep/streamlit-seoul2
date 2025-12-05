import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

# API 키 로드 (Streamlit Cloud와 로컬 환경 모두 지원)
# Streamlit Cloud에서는 st.secrets를 사용, 로컬에서는 .env 파일 사용
try:
    # Streamlit Cloud의 secrets에서 먼저 시도
    if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
        API_KEY = st.secrets['GOOGLE_API_KEY']
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
        
        API_KEY = os.getenv("GOOGLE_API_KEY")
except:
    # 폴백: 환경 변수에서 직접 가져오기
    API_KEY = os.getenv("GOOGLE_API_KEY")

# 사용 가능한 모델 목록을 동적으로 가져오기
def get_available_models():
    """사용 가능한 모델 목록을 가져옵니다."""
    available_models = []
    
    # v1beta API로 모델 목록 조회 시도
    for api_version in ["v1beta", "v1"]:
        try:
            list_url = f"https://generativelanguage.googleapis.com/{api_version}/models?key={API_KEY}"
            response = requests.get(list_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    for model in data["models"]:
                        model_name = model.get("name", "")
                        supported_methods = model.get("supportedGenerationMethods", [])
                        # streamGenerateContent를 지원하는 모델만 추가
                        if "streamGenerateContent" in supported_methods:
                            # 모델 이름에서 버전 추출 (예: "models/gemini-pro" -> "gemini-pro")
                            if "/" in model_name:
                                short_name = model_name.split("/")[-1]
                                available_models.append((api_version, short_name))
                    if available_models:
                        break
        except:
            continue
    
    # 모델 목록을 가져오지 못한 경우 기본 모델 사용
    if not available_models:
        available_models = [
            ("v1beta", "gemini-pro"),
            ("v1", "gemini-pro"),
        ]
    
    return available_models

# 세션 상태에 모델 목록 저장 (한 번만 조회)
if 'available_models' not in st.session_state:
    st.session_state.available_models = get_available_models()

API_CONFIGS = st.session_state.available_models

# 기본 설정
if API_CONFIGS:
    API_VERSION = API_CONFIGS[0][0]
    MODEL_NAME = API_CONFIGS[0][1]
else:
    # 폴백
    API_VERSION = "v1beta"
    MODEL_NAME = "gemini-pro"

st.set_page_config(page_title="Gemini 문법 교정 챗봇", page_icon="🤖", layout="wide")

# SNS 스타일 CSS 추가
st.markdown("""
<style>
    /* 메인 컨테이너 스타일 */
    .main-chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f5f5f5;
        border-radius: 10px;
    }
    
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
    
    /* 채팅 입력창 스타일 */
    .stChatInput {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    /* 헤더 스타일 */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px 10px 0 0;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="chat-header">
    <h1 style="margin: 0; color: white;">🤖 문법 교정 챗봇</h1>
    <p style="margin: 5px 0 0 0; color: rgba(255,255,255,0.9);">나는 문법을 마스터한 초등학생이야! 뭐든지 물어봐!</p>
</div>
""", unsafe_allow_html=True)

# 사이드바에 '새 대화 시작' 버튼 추가
with st.sidebar:
    st.title("메뉴")
    if st.button("🗑️ 새 대화 시작", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💬 대화 기록")
    st.caption(f"총 {len(st.session_state.get('messages', []))}개의 메시지")

if not API_KEY or API_KEY == "여기에 실제 구글 API 키를 입력하세요":
    st.error("앗! 구글 API 키가 설정되지 않았어요. .env 파일을 확인해주세요.")
    st.stop()

# 스트리밍 응답을 처리하는 제너레이터 함수
def stream_gemini_response(payload):
    """Gemini API로부터 스트리밍 응답을 받아 텍스트 청크를 yield합니다."""
    last_error = None
    for api_version, model_name in API_CONFIGS:
        # 스트리밍을 지원하는 streamGenerateContent 엔드포인트 사용
        api_url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:streamGenerateContent"
        params = {"key": API_KEY, "alt": "sse"}
        
        try:
            # stream=True로 요청을 보내고, 응답을 순회합니다.
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
                                continue # 가끔 빈 data 청크나 잘못된 JSON이 올 수 있음
                return # 성공적으로 스트리밍이 끝나면 함수 종료
        except requests.exceptions.HTTPError as e:
            last_error = e
            if e.response.status_code == 404:
                continue # 404 오류 시 다음 모델 시도
            else:
                break # 다른 HTTP 오류는 즉시 중단
        except Exception as exc:
            last_error = exc
            break
    
    # 모든 시도가 실패한 경우
    if last_error:
        yield f"Gemini를 호출하는 데 실패했어요: {last_error}"


# 세션 상태에 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 컨테이너
chat_container = st.container()

# 이전 대화 기록 표시 (SNS 스타일)
with chat_container:
    for idx, message in enumerate(st.session_state.messages):
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
    st.session_state.messages.append(user_message)
    
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
                for msg in st.session_state.messages:
                    role = "model" if msg["role"] == "assistant" else "user"
                    conversation_history.append({"role": role, "parts": [{"text": msg["content"]}]})

                # 마지막 사용자 메시지 앞에 페르소나 프롬프트 추가
                system_prompt = (
                    "너는 문법을 완벽하게 마스터한 똑똑한 초등학생이야. "
                    "사용자의 질문에 대해, 맞춤법과 문법을 친절하고 상세하게 설명해줘. "
                    "항상 밝고 명랑한 초등학생 말투를 사용해줘. 예를 들어, '~했어!', '~야!', '~거든!' 같은 말투를 사용해봐."
                )
                
                # API 요청 페이로드 구성
                payload = {
                    "contents": [
                        {"role": "user", "parts": [{"text": system_prompt}]},
                        {"role": "model", "parts": [{"text": "응, 알겠어! 이제부터 나는 문법을 마스터한 초등학생이야! 뭐든지 물어봐!"}]},
                        *conversation_history
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topP": 1,
                        "topK": 1,
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
                        st.session_state.messages.append({
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
                        st.session_state.messages.pop() # 실패한 사용자 메시지 제거
                except Exception as e:
                    error_message = f"스트리밍 중 오류가 발생했어요: {e}"
                    st.error(error_message)
                    # 실패한 경우, 마지막 사용자 메시지를 기록에서 제거하여 재시도할 수 있도록 함
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        st.session_state.messages.pop()
