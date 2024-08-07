import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
from datetime import datetime

# 設置OpenAI客戶端
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Function to fetch data from the given URL
def fetch_data(date):
    url = f'https://www.bestday123.com/{date}'
    st.write(f"Fetching data from URL: {url}")
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
    tag = soup.find(string=field_name)
    if tag:
        return tag.find_next('td').text.strip()
    return None

# Function to get explanation from OpenAI
def get_explanation(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一位農民曆解說專家。請用白話文解釋以下農民曆條文的涵義並提供建議事項。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

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
        "破土": "僅指埋葬用的破土、與一般建築房屋的“動土”不同",
        "解除": "指沖洗清掃宅舍、解除災厄等事",
        "入宅": "即遷入新宅、所謂“新居落成典禮”也",
        "修造": "指陽宅之造與修理",
        "栽種": "種植物“接果”“種田禾”同",
        "開市": "“開業”之意，商品行號開張做生意",
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
st.title('農民曆資訊查詢系統')

# 獲取今天的日期並格式化為2024年08月07日
today = datetime.today().strftime('%Y年%m月%d日')
date = st.text_input('輸入查詢日期 (格式: YYYY年MM月DD日)', today)

if st.button('查詢'):
    # 将输入日期转换为爬虫所需的格式 YYYYMMDD
    # date_str = datetime.strptime(date, '%Y年%m月%d日').strftime('%Y%m%d')
    data = fetch_data("2024年08月07日")
    st.write('### 農民曆資訊')
    
    for key, value in data.items():
        if value:
            st.write(f"**{key}**: {value}")
            if key in ["宜", "忌"]:
                explanations = get_lunar_terms_explanations()
                activities = value.split()
                for activity in activities:
                    explanation_text = explanations.get(activity, None)
                    if explanation_text:
                        if st.button(f"解釋 {activity}"):
                            detailed_explanation = get_explanation(explanation_text)
                            st.write(f"### {activity} 的解釋\n{detailed_explanation}")

    # 列印fetch_data的回傳結果進行偵錯
    st.write('### 調試資訊')
    st.write(data)
