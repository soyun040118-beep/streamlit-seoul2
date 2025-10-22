import streamlit as st

import pandas as pd



# Set the title for the web app

st.title('My First Streamlit App💐🤖-SY')



# Display introductory text

st.write("Here's our first attempt at using data to create a table:")



# Create and display a pandas DataFrame using the st.dataframe function

# st.dataframe is generally preferred over st.write for displaying tables.

st.dataframe(pd.DataFrame({

    'first column':[1,2,3,4],

    'second column':[10,20,30,40]

}))

import streamlit as st

import time



# Streamlit 앱 제목 설정

st.write(':rainbow[**🎈 버튼을 누르면 축하 풍선이 날아가요!**]')

st.markdown('아래 버튼을 눌러보세요.')



# st.button을 사용하여 버튼 생성

if st.button("🎉 풍선 보내기 (Send balloons!)"):

    # 버튼이 눌렸을 때 st.balloons() 함수 호출

    st.balloons()



    # 사용자에게 피드백을 주기 위해 잠시 메시지를 표시합니다.

    st.success("풍선 효과가 활성화되었습니다!")

    

    # 2초 동안 기다린 후 메시지를 지웁니다.

    time.sleep(2)

    st.empty()



# 참고: st.balloons()는 한 번 실행되면 자동으로 사라집니다.

import streamlit as st

import random

import time

import pandas as pd



import streamlit as st

import random

import time

import pandas as pd



# Streamlit 앱 제목 설정

st.write(':rainbow[**🎈 버튼 놀이 및 동물 뽑기 앱 🐾**] ')

st.markdown('각 버튼에 고유한 `key`를 부여하여 충돌을 해결했습니다.')







# --- 2. 동물 뽑기 버튼 ---

st.header("🐾 동물 뽑기 버튼")



# 랜덤으로 선택할 동물 이모티콘 리스트

animal_emojis = [

    "🐶", "🐱", "🐰", "🐻", "🦊", "🐼", "🦁", "🐯", 

    "🐒", "🐸", "🐳", "🐘", "🦒", "🐴", "🦉", "🐧"

]



# 🔑 key="animal_pick_btn" 추가

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

