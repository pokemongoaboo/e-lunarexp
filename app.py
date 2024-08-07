import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
from openai import OpenAI


# 設置OpenAI客戶端
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# Function to fetch data from the given URL
def fetch_data(date):
    url = f'https://www.bestday123.com/{date}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {
        "日期": extract_data(soup, '日期'),
        "農曆": extract_data(soup, '農曆'),
        "歲次": extract_data(soup, '歲次'),
        "每日胎神占方": extract_data(soup, '每日胎神占方'),
        "五行": extract_data(soup, '五行'),
        "沖": extract_data(soup, '沖'),
        "彭祖百忌": extract_data(soup, '彭祖百忌'),
        "吉神宜趨": extract_data(soup, '吉神宜趨'),
        "宜": extract_data(soup, '宜'),
        "凶神宜忌": extract_data(soup, '凶神宜忌'),
        "忌": extract_data(soup, '忌'),
    }
    
    return data

# Function to extract specific data from HTML
def extract_data(soup, field_name):
    tag = soup.find(text=field_name)
    if tag:
        return tag.find_next('td').text.strip()
    return None



    
# Function to get explanation from OpenAI
def get_explanation(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        prompt=f"你是一位農民曆解說專家。請用白話文解釋以下農民曆條文的涵義並提供建議事項。\n\n{prompt}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit app
st.title('農民曆資訊查詢系統')

date = st.text_input('輸入查詢日期 (格式: YYYYMMDD)', '20240101')

if st.button('查詢'):
    data = fetch_data(date)
    st.write('### 農民曆資訊')
    
    for key, value in data.items():
        if value:
            if key in ["宜", "忌"]:
                if st.button(f"解釋 {key}"):
                    explanation = get_explanation(value)
                    st.write(f"### {key} 的解釋\n{explanation}")
            st.write(f"**{key}**: {value}")
