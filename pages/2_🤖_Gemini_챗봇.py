import os
import requests
import streamlit as st
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
# 여러 경로에서 .env 파일 찾기 시도
env_paths = []
try:
    # 현재 파일의 디렉토리 (pages 폴더)
    file_dir = os.path.dirname(os.path.abspath(__file__))
    # 상위 디렉토리의 .env
    env_paths.append(os.path.join(file_dir, '..', '.env'))
    # 현재 디렉토리의 .env
    env_paths.append(os.path.join(file_dir, '.env'))
except:
    pass

# 현재 작업 디렉토리
env_paths.append('.env')
env_paths.append(os.path.join(os.getcwd(), '.env'))
# 상위 디렉토리
env_paths.append(os.path.join(os.getcwd(), '..', '.env'))

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

# Gemini API 설정
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
                        # generateContent를 지원하는 모델만 추가
                        if "generateContent" in supported_methods:
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
    with st.spinner("사용 가능한 모델을 확인하는 중..."):
        st.session_state.available_models = get_available_models()

API_CONFIGS = st.session_state.available_models

# 기본 설정
if API_CONFIGS:
    API_VERSION = API_CONFIGS[0][0]
    MODEL_NAME = API_CONFIGS[0][1]
    API_URL = f"https://generativelanguage.googleapis.com/{API_VERSION}/models/{MODEL_NAME}:generateContent"
else:
    # 폴백
    API_VERSION = "v1beta"
    MODEL_NAME = "gemini-pro"
    API_URL = f"https://generativelanguage.googleapis.com/{API_VERSION}/models/{MODEL_NAME}:generateContent"

st.set_page_config(page_title="Gemini 챗봇", page_icon="🤖")
st.title("🤖 무엇이든 물어보세요! Gemini 챗봇")

if not API_KEY or API_KEY == "여기에 실제 구글 API 키를 입력하세요":
    st.error("앗! 구글 API 키가 설정되지 않았어요. .env 파일을 확인해주세요.")
    st.stop()

# 사용 가능한 모델 정보 표시
if API_CONFIGS:
    with st.expander("📋 사용 가능한 모델 목록"):
        st.write("현재 API 키로 사용 가능한 모델들:")
        for api_ver, model_name in API_CONFIGS:
            st.write(f"  - **{api_ver}/{model_name}**")
        if st.button("🔄 모델 목록 새로고침"):
            st.session_state.available_models = get_available_models()
            st.rerun()

with st.form(key="chat_form"):
    user_input = st.text_area("질문을 입력하세요", height=120, placeholder="예) 대한민국의 수도는 어디야?")
    submitted = st.form_submit_button("Gemini에게 물어보기")

if submitted and user_input.strip():
    with st.spinner("Gemini가 답변을 만들고 있어요... 잠시만 기다려주세요!"):
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_input.strip()}
                    ]
                }
            ]
        }
        headers = {
            "Content-Type": "application/json",
        }
        
        # 여러 API 버전과 모델 조합을 시도 (404 오류 시 자동으로 다음 조합 시도)
        success = False
        last_error = None
        
        for api_version, model_name in API_CONFIGS:
            if success:
                break
                
            api_url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent"
            params = {"key": API_KEY}
            
            try:
                response = requests.post(api_url, params=params, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # 응답 구조 확인 및 텍스트 추출
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        text = candidate["content"]["parts"][0]["text"]
                        st.markdown("### 🤖 Gemini의 답변")
                        st.markdown(text)
                        if api_version != API_VERSION or model_name != MODEL_NAME:
                            st.info(f"💡 {api_version}/{model_name} 조합을 사용했습니다.")
                        success = True
                    else:
                        st.error("응답 형식이 예상과 다릅니다.")
                        st.json(data)
                else:
                    st.error("응답에 candidates가 없습니다.")
                    st.json(data)
            except requests.exceptions.HTTPError as e:
                last_error = e
                if response.status_code == 404:
                    # 404 오류면 다음 모델 시도
                    continue
                else:
                    # 다른 HTTP 오류는 즉시 처리
                    break
            except Exception as exc:
                last_error = exc
                break
        
        # 모든 모델 시도 실패 시 오류 표시
        if not success:
            if last_error and hasattr(last_error, 'response'):
                response = last_error.response
                if response.status_code == 404:
                    st.error(f"모든 API 버전과 모델 조합을 시도했지만 찾을 수 없습니다 (404 오류)")
                    st.info("💡 시도한 조합들:")
                    for api_ver, model in API_CONFIGS:
                        st.write(f"  - {api_ver}/{model}")
                    st.info("💡 사용 가능한 모델을 확인하려면 아래 버튼을 클릭하세요.")
                    
                    # 사용 가능한 모델 목록 확인 버튼
                    if st.button("사용 가능한 모델 목록 확인"):
                        try:
                            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
                            list_response = requests.get(list_url, timeout=10)
                            if list_response.status_code == 200:
                                models_data = list_response.json()
                                if "models" in models_data:
                                    st.success("✅ 사용 가능한 모델 목록:")
                                    for model in models_data["models"]:
                                        model_name = model.get("name", "알 수 없음")
                                        supported_methods = model.get("supportedGenerationMethods", [])
                                        st.write(f"  - **{model_name}** (지원 메서드: {', '.join(supported_methods)})")
                                else:
                                    st.json(models_data)
                            else:
                                st.error(f"모델 목록 조회 실패: {list_response.status_code}")
                                st.text(list_response.text)
                        except Exception as e:
                            st.error(f"모델 목록 조회 중 오류: {e}")
                    
                    st.info("💡 API 키가 유효한지, Gemini API가 활성화되어 있는지 확인해주세요.")
                    st.info("💡 Google Cloud Console에서 Generative Language API가 활성화되어 있는지 확인하세요.")
                elif response.status_code == 400:
                    st.error("요청 형식이 잘못되었습니다 (400 오류)")
                    st.info("💡 API 키와 요청 내용을 확인해주세요.")
                elif response.status_code == 403:
                    st.error("API 키 권한이 없습니다 (403 오류)")
                    st.info("💡 API 키가 유효한지, Gemini API가 활성화되어 있는지 확인해주세요.")
                else:
                    st.error(f"HTTP 오류가 발생했어요: {last_error}")
                try:
                    error_data = response.json()
                    st.json(error_data)
                except:
                    st.text(response.text)
            else:
                st.error(f"요청 중 오류가 발생했어요: {last_error}")
                st.info("💡 API 키와 네트워크 연결을 확인해주세요.")
else:
    st.info("궁금한 것을 물어보면 Gemini가 친절하게 답변해 줄 거예요!")