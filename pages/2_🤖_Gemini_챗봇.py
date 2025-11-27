import os
import requests
import streamlit as st
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Gemini 챗봇", page_icon="🤖")
st.title("🤖 무엇이든 물어보세요! Gemini 챗봇")

if not API_KEY or API_KEY == "여기에 실제 구글 API 키를 입력하세요":
    st.error("앗! 구글 API 키가 설정되지 않았어요. .env 파일을 확인해주세요.")
    st.stop()

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
        params = {"key": API_KEY}
        try:
            response = requests.post(API_URL, params=params, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            st.markdown("### 🤖 Gemini의 답변")
            st.markdown(text)
        except Exception as exc:
            st.error(f"요청 중 오류가 발생했어요: {exc}")
else:
    st.info("궁금한 것을 물어보면 Gemini가 친절하게 답변해 줄 거예요!")