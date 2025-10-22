import streamlit as st
import pandas as pd
import random
import time

# --- 1. 앱 기본 설정 및 초기 데이터 표시 ---
st.title('My First Streamlit App💐🤖-SY')

# 초기 데이터프레임
st.header("1. 초기 데이터 테이블")
st.write("Streamlit의 `st.dataframe`을 사용한 테이블:")
st.dataframe(pd.DataFrame({
    'first column':[1,2,3,4],
    'second column':[10,20,30,40]
}))

st.markdown("---")

# --- 2. 축하 풍선 버튼 (Key 추가) ---
st.header("2. 🎉 축하 풍선 버튼")
st.write(':rainbow[**🎈 버튼을 누르면 축하 풍선이 날아가요!**]')
st.markdown('아래 버튼을 눌러보세요.')

# 🔑 key="balloons_send_key"를 추가하여 ID 충돌 해결
if st.button("🎉 풍선 보내기 (Send balloons!)", key="balloons_send_key"):
    # 버튼이 눌렸을 때 st.balloons() 함수 호출
    st.balloons()

    # 사용자에게 피드백을 주기 위해 잠시 메시지를 표시합니다.
    st.success("풍선 효과가 활성화되었습니다!")
    
    # 2초 동안 기다린 후 메시지를 지웁니다.
    time.sleep(2)
    st.empty()

st.markdown("---")

# --- 3. 동물 뽑기 버튼 (Key 유지) ---
st.header("3. 🐾 동물 뽑기 버튼")

# 랜덤으로 선택할 동물 이모티콘 리스트
animal_emojis = [
    "🐶", "🐱", "🐰", "🐻", "🦊", "🐼", "🦁", "🐯", 
    "🐒", "🐸", "🐳", "🐘", "🦒", "🐴", "🦉", "🐧"
]

# 🔑 key="animal_pick_btn"을 사용하여 ID 충돌 해결
if st.button("🎲 동물 뽑기 버튼 (Pick an Animal!)", key="animal_pick_btn"):
    # 리스트에서 랜덤으로 동물 이모티콘 선택
    selected_animal = random.choice(animal_emojis)
    
    # 선택된 동물을 크게 표시
    st.markdown(
        f"""
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 80px; animation: bounce 0.5s ease-in-out infinite alternate;">
                {selected_animal}
            </span>
            <p style="font-size: 20px; font-weight: bold; color: #4B0082; margin-top: 10px;">
                당신의 선택은 바로 {selected_animal} 입니다!
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
st.markdown("---")

