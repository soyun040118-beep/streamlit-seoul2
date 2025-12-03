import os
import json
import json
import requests
import streamlit as st
from dotenv import load_dotenv

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

st.set_page_config(page_title="Gemini 문법 교정 챗봇", page_icon="🤖")
st.title("🤖 문법 교정 챗봇")
st.caption("나는 문법을 마스터한 초등학생이야! 뭐든지 물어봐!")

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

# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력을 위한 채팅 입력창
if prompt := st.chat_input("맞춤법이나 문법이 궁금한 문장을 입력해봐!"):
    # 사용자 메시지를 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("Gemini가 열심히 생각하고 있어..."):
            # 페르소나 설정 및 대화 기록을 API 요청 형식으로 변환
            conversation_history = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                conversation_history.append({"role": role, "parts": [{"text": msg["content"]}]})

            # 마지막 사용자 메시지 앞에 페르소나 프롬프트 추가
            # 참고: Gemini는 공식적인 'system' 역할이 없으므로, 대화의 일부로 컨텍스트를 제공합니다.
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
                # 스트리밍 응답을 화면에 표시하고 전체 응답을 저장
                response_stream = stream_gemini_response(payload)
                full_response = st.write_stream(response_stream)
                
                # 성공적으로 응답을 받으면 대화 기록에 추가
                if full_response:
                     st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    # 스트림에서 아무것도 반환되지 않은 경우 (오류는 스트림 내에서 처리됨)
                    st.error("앗, 응답을 생성하지 못했어. 다시 시도해줄래?")
                    st.session_state.messages.pop() # 실패한 사용자 메시지 제거
            except Exception as e:
                error_message = f"스트리밍 중 오류가 발생했어요: {e}"
                st.error(error_message)
                # 실패한 경우, 마지막 사용자 메시지를 기록에서 제거하여 재시도할 수 있도록 함
                st.session_state.messages.pop()
            else:
                # 스트림에서 아무것도 반환되지 않은 경우 (오류는 스트림 내에서 처리됨)
                st.error("앗, 응답을 생성하지 못했어. 다시 시도해줄래?")
                st.session_state.messages.pop() # 실패한 사용자 메시지 제거
        except Exception as e:
            error_message = f"스트리밍 중 오류가 발생했어요: {e}"
            st.error(error_message)
            # 실패한 경우, 마지막 사용자 메시지를 기록에서 제거하여 재시도할 수 있도록 함
            st.session_state.messages.pop()
