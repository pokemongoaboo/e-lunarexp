import streamlit as st
import requests
import re
from datetime import datetime
import openai
import pandas as pd

# 確保OpenAI API密鑰已正確配置
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API密鑰未配置。")
else:
    client = openai.OpenAI(api_key=api_key)

# Function to fetch data from the given URL
def fetch_data(date):
    url = f'https://www.bestday123.com/{date}'
    response = requests.get(url)
    content = response.text
    
    # Function to extract data using regex
    def extract_data(pattern):
        match = re.search(pattern, content)
        return match.group(1).strip().replace('&nbsp;', ' ') if match else None

    # 使用正則表達式提取所有需要的信息
    date_info = extract_data(r'【日期】</td><td>(.*?)</td>')
    lunar_info = extract_data(r'【農曆】</td><td>(.*?)</td>')
    year_info = extract_data(r'【歲次】</td><td>(.*?)</td>')
    deity_info = extract_data(r'【每日胎神占方】</td><td>(.*?)</td>')
    element_info = extract_data(r'【五行】</td><td>(.*?)</td>')
    clash_info = extract_data(r'【沖】</td><td>(.*?)</td>')
    taboos_info = extract_data(r'【彭祖百忌】</td><td>(.*?)</td>')
    auspicious_info = extract_data(r'【吉神宜趨】</td><td>(.*?)</td>')
    should_do_info = extract_data(r'<font color=#1EFB>【宜】</font></td><td>(.*?)</td>')
    should_avoid_info = extract_data(r'【凶神宜忌】</td><td>(.*?)</td>')
    avoid_info = extract_data(r'<font color=#E2A500>【忌】</font></td><td>(.*?)</td>')

    data = {
        "日期": date_info,
        "農曆": lunar_info,
        "歲次": year_info,
        "每日胎神占方": deity_info,
        "五行": element_info,
        "沖": clash_info,
        "彭祖百忌": taboos_info,
        "吉神宜趨": auspicious_info,
        "宜": should_do_info,
        "凶神宜忌": should_avoid_info,
        "忌": avoid_info,
    }
    
    return data

# Function to get explanation from OpenAI
def get_explanation(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一位農民曆解說專家。請用白話文解釋以下農民曆條文的涵義並提供建議事項，儘量在tokens限制內，把建議說完。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API請求失敗: {e}")
        return "OpenAI API請求失敗"

# Function to get Lunar Terms Explanations
def get_lunar_terms_explanations():
    return {
        "嫁娶": "男娶女嫁，舉行結婚大典的吉日",
        "祭祀": "指祠堂之祭祀、即拜祭祖先或廟寺的祭拜、神明等事",
        "安葬": "舉行埋葬等儀式",
        "出行": "指外出旅行、觀光遊覽",
        "祈福": "祈求神明降福或設醮還願之事",
        "動土": "建築時、第一次動起鋤頭挖土",
        "安床": "指安置睡床臥鋪之意",
        "開光": "佛像塑成後、供奉上位之事",
        "納采": "締結婚姻的儀式、受授聘金",
        "入殮": "將屍體放入棺材之意",
        "移徙": "指搬家遷移住所之意",
        "破土": "僅指埋葬用的破土、與一般建築房屋的「動土」不同",
        "解除": "指沖洗清掃宅舍、解除災厄等事",
        "入宅": "即遷入新宅、所謂「新居落成典禮」也",
        "修造": "指陽宅之造與修理",
        "栽種": "種植物「接果」「種田禾」同",
        "開市": "「開業」之意，商品行號開張做生意",
        "移柩": "行葬儀時、將棺木移出屋外之事",
        "訂盟": "訂婚儀式的一種，俗稱小聘(訂)",
        "拆卸": "拆掉建築物",
        "立卷": "訂立各種契約互相買賣之事",
        "交易": "訂立各種契約互相買賣之事",
        "求嗣": "指向神明祈求後嗣(子孫)之意",
        "上樑": "裝上建築物屋頂的梁",
        "納財": "購屋產業、進貨、收帳、收租等",
        "起基": "建築時、第一次動起鋤頭挖土",
        "齋醮": "廟宇建醮前需舉行的齋戒儀式",
        "赴任": "走馬上任",
        "冠笄": "男女年滿二十歲所舉行的成年禮儀式",
        "安門": "放置正門門框",
        "修墳": "修理墳墓",
        "掛匾": "指懸掛招牌或各種匾額",
        "問名": "合對男女雙方的八字帖後，交換庚帖、譜牒。",
        "提親": "受男方或女方的委託，向對方提議婚嫁之事。",
        "裁衣": "裁製新娘的新衣或指做壽衣。",
        "安香": "香火之安位，例如安土地公或堂上祖先神位。",
        "出火": "移動神明之位。",
        "會親友": "拜訪或宴請親友。",
        "求醫治病": "就醫治療或動手術。",
        "立券": "訂立各種契約之事。",
        "交易": "訂立各種買賣之事。",
        "交車": "點交新購之汽機車。",
        "安機械": "安置車床、機械等設備。",
        "謝土": "指建築物完工後，或是安葬後、墳墓完成時，所舉行的祭祀。",
        "破屋": "拆除房屋之事。",
        "壞垣": "拆除圍牆之事。"
    }

# Streamlit app
#st.title('農民曆資訊查詢系統(Lunar Calendar Query and')

st.set_page_config(page_title="農民曆資訊查詢", layout="wide")

# 使用 markdown 來創建置中的兩行標題
st.markdown("""
    <h1 style="text-align: center;">農民曆資訊查詢與建議</h1>
    <h2 style="text-align: center;">(Lunar Calendar Advices)</h2>
    """, unsafe_allow_html=True)

    # 添加一些間距
st.markdown("<br>", unsafe_allow_html=True)

# 獲取今天的日期並格式化為2024年08月07日
today = datetime.today().strftime('%Y年%m月%d日')
date = st.text_input('輸入查詢日期 (格式: YYYY年MM月DD日)', today)

if 'data' not in st.session_state:
    st.session_state.data = None
if 'explanations' not in st.session_state:
    st.session_state.explanations = {}

if st.button('查詢(Query)'):
    st.session_state.data = fetch_data(date)

data = st.session_state.data

if data:
    st.write('### 農民曆資訊(Lunar Calendar)')
    
    # Create a dataframe for general information
    general_info = {key: [value] for key, value in data.items() if key not in ["宜", "忌"] and value}
    df_general = pd.DataFrame(general_info).T
    df_general.columns = ['值']
    st.table(df_general)
    
    # Function to create and display a table for "宜" or "忌" items
    def display_items_table(items, title):
        st.write(f'### 【{title}】')
        df = pd.DataFrame(columns=['項目', '解釋'])
        for item in items.split():
            explanation = get_lunar_terms_explanations().get(item, "")
            df = pd.concat([df, pd.DataFrame({'項目': [item], '解釋': [explanation]})], ignore_index=True)
        
        # Display the table
        st.table(df)
        
        # Add buttons and display explanations
        for index, row in df.iterrows():
            item = row['項目']
            if st.button(f"解釋(Advices for :) {item}", key=f"解釋_{title}_{item}"):
                prompt = f"<建議事項> : {item} {row['解釋']}"
                st.session_state.explanations[f"{title}_{item}"] = get_explanation(prompt)
            
            if f"{title}_{item}" in st.session_state.explanations:
                explanation = st.session_state.explanations[f"{title}_{item}"]
                st.markdown(f"<div style='background-color: #e6f3ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;'><b>{item} 詳細說明：</b><br>{explanation}</div>", unsafe_allow_html=True)
    
    # Display "宜" items
    if data.get("宜"):
        display_items_table(data["宜"], "宜")
    
    # Display "忌" items
    if data.get("忌"):
        display_items_table(data["忌"], "忌")

    # 列印fetch_data的回傳結果進行偵錯
    # st.write('### 調試資訊')
    # st.write(data)
