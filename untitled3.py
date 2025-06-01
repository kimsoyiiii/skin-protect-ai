# -*- coding: utf-8 -*-
import streamlit as st
import requests
import datetime
import pandas as pd
import urllib3

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 페이지 설정
st.set_page_config(page_title="피부 보호 AI", layout="centered")
st.title("🌤️ AI 기반 맞춤형 피부 보호 프로그램")

# ✅ 환경변수에서 API Key 가져오기 (Streamlit Secrets)
API_KEY = st.secrets["WEATHER_API_KEY"]

# 현재 날짜 및 기상청 API 기준 시간 구하기
def get_base_time():
    now = datetime.datetime.now()
    if now.minute < 45:
        now = now - datetime.timedelta(hours=1)
    return now.strftime("%Y%m%d"), now.strftime("%H00")

# 기상청 실황 날씨 불러오기
def get_weather():
    base_date, base_time = get_base_time()
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    params = {
        "serviceKey": API_KEY,
        "pageNo": "1",
        "numOfRows": "100",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": "57",  # 경기도 광명시
        "ny": "126"
    }
    try:
        response = requests.get(url, params=params, timeout=10, verify=False)
        return response.json()
    except Exception as e:
        st.error(f"❗ 날씨 데이터 오류: {e}")
        return None

# 날씨 → 피부 조건 해석
def interpret_weather(data):
    condition = []
    try:
        items = data['response']['body']['items']['item']
        for item in items:
            if item['category'] == 'T1H':
                temp = float(item['obsrValue'])
                if temp < 10:
                    condition.append('추움')
                elif temp > 27:
                    condition.append('더움')
            elif item['category'] == 'REH':
                reh = float(item['obsrValue'])
                if reh < 40:
                    condition.append('건조함')
                elif reh > 75:
                    condition.append('습함')
            elif item['category'] == 'UV':
                uv = float(item['obsrValue'])
                if uv > 7:
                    condition.append('자외선 강함')
    except:
        pass
    return condition

# 추천 성분 DB
recommendation_db = pd.DataFrame([
    {"status": "추움", "ingredient": "세라마이드", "effect": "보습, 장벽 강화"},
    {"status": "더움", "ingredient": "살리실산", "effect": "모공 피지 용해"},
    {"status": "건조함", "ingredient": "히알루론산", "effect": "수분 유지"},
    {"status": "습함", "ingredient": "녹차 추출물", "effect": "항염, 진정"},
    {"status": "자외선 강함", "ingredient": "자외선 차단제 SPF50+", "effect": "광노화 방지"}
])

# 수동 새로고침 버튼
if st.button("🔄 날씨 새로고침"):
    st.rerun()

# 데이터 가져오기 및 결과 출력
weather_data = get_weather()
if weather_data:
    st.success("✅ 날씨 데이터를 성공적으로 불러왔습니다.")
    conditions = interpret_weather(weather_data)

    if conditions:
        st.subheader("🌡️ 감지된 피부 환경:")
        for cond in conditions:
            st.markdown(f"- **{cond}**")

        st.subheader("🧴 추천 성분:")
        matched = recommendation_db[recommendation_db["status"].isin(conditions)].drop_duplicates()
        for i, row in matched.iterrows():
            st.markdown(f"""
            🔹 **상태**: {row['status']}  
            🔸 **성분**: {row['ingredient']}  
            💡 **효과**: {row['effect']}  
            """)
    else:
        st.warning("❗ 기상 조건에 따른 피부 문제가 감지되지 않았어요.")
else:
    st.error("❗ 날씨 데이터를 불러오지 못했습니다.")
