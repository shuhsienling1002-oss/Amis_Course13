import streamlit as st
import time
import random
from io import BytesIO

# --- 1. 核心相容性修復 (防止報錯) ---
def safe_rerun():
    """自動判斷並執行重整，相容所有版本"""
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except:
            st.stop() # 如果都失敗，至少停止執行避免紅字

def safe_play_audio(text):
    """語音播放安全模式"""
    try:
        from gtts import gTTS
        # 使用印尼語 (id) 發音，接近阿美語
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except Exception as e:
        # 如果失敗，只顯示圖示提示，不讓程式崩潰
        st.caption(f"🔇 (語音生成暫時無法使用: {str(e)})")

# --- 0. 系統配置 ---
st.set_page_config(page_title="Unit 13: I Cowa?", page_icon="📍", layout="centered")

# --- CSS 美化 ---
st.markdown("""
    <style>
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .source-tag { font-size: 12px; color: #aaa; text-align: right; font-style: italic; }
    
    /* 單字卡 */
    .word-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 4px solid #4CAF50;
    }
    .emoji-icon { font-size: 48px; margin-bottom: 10px; }
    .amis-text { font-size: 22px; font-weight: bold; color: #2E7D32; }
    .chinese-text { font-size: 16px; color: #7f8c8d; }
    
    /* 句子框 */
    .sentence-box {
        background-color: #F1F8E9;
        border-left: 5px solid #81C784;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
    }

    /* 按鈕 */
    .stButton>button {
        width: 100%; border-radius: 12px; font-size: 20px; font-weight: 600;
        background-color: #C8E6C9; color: #1B5E20; border: 2px solid #4CAF50; padding: 12px;
    }
    .stButton>button:hover { background-color: #A5D6A7; border-color: #2E7D32; }
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料庫 (修正版) ---
vocab_data = [
    {"amis": "Talacowa", "chi": "去哪裡", "icon": "❓", "source": "Row 8"},
    {"amis": "Tayra", "chi": "去 (那裡)", "icon": "👉", "source": "Row 19"},
    {"amis": "I cowa", "chi": "在哪裡 (靜態)", "icon": "📍", "source": "Row 15"},
    {"amis": "Posong", "chi": "台東", "icon": "🏞️", "source": "Row 19"},
    {"amis": "Niyaro'", "chi": "部落 / 社區", "icon": "🏘️", "source": "Row 15"},
    {"amis": "Loma'", "chi": "家", "icon": "🏠", "source": "Unit 10"},
    {"amis": "pitilidan", "chi": "學校", "icon": "🏫", "source": "Correction"},
    {"amis": "Omah", "chi": "農田 / 田地", "icon": "🌾", "source": "Correction"},
    {"amis": "Patiyamay", "chi": "商店 / 市場", "icon": "🏪", "source": "Basic"},
    {"amis": "Kaying", "chi": "小姐", "icon": "👩", "source": "Row 10"}, 
]

sentences = [
    {"amis": "Talacowa kiso?", "chi": "你要去哪裡？", "icon": "❓", "source": "Row 8"},
    {"amis": "Tayra kami i Posong.", "chi": "我們去台東。", "icon": "🚗", "source": "Row 19"},
    {"amis": "I cowa ko niyaro'?", "chi": "部落在哪裡？", "icon": "🏘️", "source": "Row 15"},
    {"amis": "I loma' ci mama.", "chi": "爸爸在家裡。", "icon": "🏠", "source": "Correction"}, 
    {"amis": "Tayra ci Kaying i pitilidan.", "chi": "小姐去學校。", "icon": "🏫", "source": "Grammar"},
]

# --- 3. 隨機題庫 ---
quiz_pool = [
    {
        "q": "Talacowa kiso?",
        "audio": "Talacowa kiso",
        "options": ["你要去哪裡？", "你是誰？", "現在幾點？"],
        "ans": "你要去哪裡？",
        "hint": "Tala (前往) + Cowa (哪裡)"
    },
    {
        "q": "Tayra kami i Posong.",
        "audio": "Tayra kami i Posong",
        "options": ["我們去台東", "我們去學校", "我們在部落"],
        "ans": "我們去台東",
        "hint": "Posong 是地名 (台東)"
    },
    {
        "q": "你想問別人的「部落在哪裡」，該怎麼說？",
        "audio": None,
        "options": ["I cowa ko niyaro'?", "Talacowa ko niyaro'?", "Pina ko niyaro'?"],
        "ans": "I cowa ko niyaro'?",
        "hint": "詢問「位置」用 I cowa"
    },
    {
        "q": "Tayra ci Ina i _______ (媽媽去買菜)",
        "audio": None,
        "options": ["Patiyamay (市場/商店)", "pitilidan (學校)", "Loma' (家)"],
        "ans": "Patiyamay (市場/商店)",
        "hint": "買菜通常去市場"
    },
    {
        "q": "單字測驗：pitilidan",
        "audio": "pitilidan",
        "options": ["學校", "農田", "家"],
        "ans": "學校",
        "hint": "讀書寫字的地方"
    },
    {
        "q": "I loma' ci mama.",
        "audio": "I loma' ci mama",
        "options": ["爸爸在家裡", "爸爸去上班", "爸爸在睡覺"],
        "ans": "爸爸在家裡",
        "hint": "I loma' (在家)"
    },
    {
        "q": "單字測驗：Omah",
        "audio": "Omah",
        "options": ["農田 / 田地", "學校", "市場"],
        "ans": "農田 / 田地",
        "hint": "種作物的地方"
    }
]

# --- 4. 狀態初始化 (最重要的一步) ---
if 'init' not in st.session_state:
    st.session_state.score = 0
    st.session_state.quiz_questions = random.sample(quiz_pool, 3)
    st.session_state.current_q_idx = 0
    st.session_state.quiz_id = str(random.randint(1000, 9999)) # 防止 Key 重複
    st.session_state.init = True

# --- 5. 主介面 ---
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>Unit 13: I Cowa?</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>地點與移動 (修正版)</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📚 詞彙與句型", "🎲 隨機挑戰"])

# === Tab 1: 學習模式 ===
with tab1:
    st.subheader("📝 核心單字")
    col1, col2 = st.columns(2)
    for i, word in enumerate(vocab_data):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="word-card">
                <div class="emoji-icon">{word['icon']}</div>
                <div class="amis-text">{word['amis']}</div>
                <div class="chinese-text">{word['chi']}</div>
                <div class="source-tag">src: {word['source']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 聽發音", key=f"btn_vocab_{i}"):
                safe_play_audio(word['amis'])

    st.markdown("---")
    st.subheader("🗣️ 實用句型")
    for i, s in enumerate(sentences):
        st.markdown(f"""
        <div class="sentence-box">
            <div style="font-size: 20px; font-weight: bold; color: #1B5E20;">{s['icon']} {s['amis']}</div>
            <div style="font-size: 16px; color: #555; margin-top: 5px;">{s['chi']}</div>
            <div class="source-tag">src: {s['source']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"▶️ 播放句型", key=f"btn_sent_{i}"):
            safe_play_audio(s['amis'])

# === Tab 2: 隨機挑戰模式 ===
with tab2:
    st.markdown("### 🎲 隨機評量")
    
    # 確保索引不超標
    if st.session_state.current_q_idx < len(st.session_state.quiz_questions):
        q_data = st.session_state.quiz_questions[st.session_state.current_q_idx]
        
        # 進度條
        st.progress((st.session_state.current_q_idx) / 3)
        st.markdown(f"**Question {st.session_state.current_q_idx + 1} / 3**")
        
        # 顯示題目
        st.markdown(f"### {q_data['q']}")
        if q_data['audio']:
            if st.button("🎧 播放題目音檔", key=f"btn_audio_{st.session_state.current_q_idx}"):
                safe_play_audio(q_data['audio'])
        
        # [關鍵修正] 使用 quiz_id 確保 key 唯一，避免 DuplicateWidgetKey 錯誤
        unique_key = f"q_{st.session_state.quiz_id}_{st.session_state.current_q_idx}"
        user_choice = st.radio("請選擇正確答案：", q_data['options'], key=unique_key)
        
        if st.button("送出答案", key=f"btn_submit_{st.session_state.current_q_idx}"):
            if user_choice == q_data['ans']:
                st.balloons()
                st.success("🎉 答對了！")
                time.sleep(1) # 等待一下讓使用者看到成功訊息
                st.session_state.score += 100
                st.session_state.current_q_idx += 1
                safe_rerun()
            else:
                st.error(f"不對喔！提示：{q_data['hint']}")
                
    else:
        # 結算畫面
        st.progress(1.0)
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background-color: #C8E6C9; border-radius: 20px; margin-top: 20px;'>
            <h1 style='color: #1B5E20;'>🏆 挑戰成功！</h1>
            <h3 style='color: #333;'>本次得分：{st.session_state.score}</h3>
            <p>你已經完成本輪測試。</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 再來一局 (重新抽題)", key="btn_restart"):
            st.session_state.score = 0
            st.session_state.current_q_idx = 0
            st.session_state.quiz_questions = random.sample(quiz_pool, 3)
            st.session_state.quiz_id = str(random.randint(1000, 9999)) # 更新 ID 防止報錯
            safe_rerun()
