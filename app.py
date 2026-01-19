import streamlit as st
import time
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統與視覺配置 ---
st.set_page_config(page_title="Unit 13: I Cowa?", page_icon="📍", layout="centered")

# CSS 設計
st.markdown("""
    <style>
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    .source-tag {
        font-size: 12px; color: #aaa; text-align: right; font-style: italic; margin-top: 4px;
    }
    .word-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #ffffff 100%); /* 綠色系，象徵戶外 */
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 4px solid #4CAF50;
        transition: transform 0.2s;
    }
    .word-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.15);
    }
    .emoji-icon { font-size: 48px; margin-bottom: 10px; }
    .amis-text { font-size: 22px; font-weight: bold; color: #2E7D32; }
    .chinese-text { font-size: 16px; color: #7f8c8d; }
    
    .stButton>button {
        width: 100%; border-radius: 12px; font-size: 20px; font-weight: 600;
        background-color: #C8E6C9; color: #1B5E20; border: 2px solid #4CAF50; padding: 12px;
    }
    .stButton>button:hover { background-color: #A5D6A7; border-color: #2E7D32; }
    
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# --- 1. 資料庫 (Strictly from data.csv & No Hyphens) ---
vocab_data = [
    {"amis": "Talacowa", "chi": "去哪裡", "icon": "❓", "source": "Row 8"},
    {"amis": "Tayra", "chi": "去 (那裡)", "icon": "👉", "source": "Row 19"},
    {"amis": "I cowa", "chi": "在哪裡 (靜態)", "icon": "📍", "source": "Row 15"},
    {"amis": "Posong", "chi": "台東", "icon": "🏞️", "source": "Row 19"},
    {"amis": "Niyaro'", "chi": "部落 / 社區", "icon": "🏘️", "source": "Row 15"},
    {"amis": "Loma'", "chi": "家", "icon": "🏠", "source": "Unit 10"},
    {"amis": "Gako", "chi": "學校", "icon": "🏫", "source": "Basic"},
    {"amis": "Omah", "chi": "田 / 山上", "icon": "🌾", "source": "Basic"},
    {"amis": "Patiyamay", "chi": "商店 / 市場", "icon": "🏪", "source": "Basic"},
    {"amis": "Kaying", "chi": "小姐 (複習)", "icon": "👩", "source": "Row 10"}, 
]

sentences = [
    {"amis": "Talacowa kiso?", "chi": "你要去哪裡？", "icon": "❓", "source": "Row 8"},
    {"amis": "Tayra kami i Posong.", "chi": "我們去台東。", "icon": "🚗", "source": "Row 19"},
    {"amis": "I cowa ko niyaro'?", "chi": "部落在哪裡？", "icon": "🏘️", "source": "Row 15 (改寫)"},
    {"amis": "I loma' ko mama.", "chi": "爸爸在家裡。", "icon": "🏠", "source": "Unit 10+13"},
    {"amis": "Tayra ci Kaying i gako.", "chi": "小姐去學校。", "icon": "🏫", "source": "Grammar"},
]

# --- 2. 隨機題庫系統 ---
# 題目類型：listening (聽力), translation (翻譯), logic (邏輯)
quiz_pool = [
    {
        "type": "listening",
        "q": "Talacowa kiso?",
        "audio": "Talacowa kiso",
        "options": ["你要去哪裡？", "你是誰？", "現在幾點？"],
        "ans": "你要去哪裡？",
        "hint": "Tala (前往) + Cowa (哪裡)"
    },
    {
        "type": "listening",
        "q": "Tayra kami i Posong.",
        "audio": "Tayra kami i Posong",
        "options": ["我們去台東", "我們去學校", "我們在部落"],
        "ans": "我們去台東",
        "hint": "Posong 是地名 (台東)"
    },
    {
        "type": "logic",
        "q": "你想問別人的「部落在哪裡」，該怎麼說？",
        "audio": None,
        "options": ["I cowa ko niyaro'?", "Talacowa ko niyaro'?", "Pina ko niyaro'?"],
        "ans": "I cowa ko niyaro'?",
        "hint": "詢問「位置」用 I cowa，詢問「去向」用 Talacowa"
    },
    {
        "type": "logic",
        "q": "Tayra ci Ina i _______ (媽媽去買菜)",
        "audio": None,
        "options": ["Patiyamay (市場/商店)", "Gako (學校)", "Loma' (家)"],
        "ans": "Patiyamay (市場/商店)",
        "hint": "買菜通常去市場"
    },
    {
        "type": "translation",
        "q": "單字測驗：Omah",
        "audio": "Omah",
        "options": ["田 / 山上", "家", "學校"],
        "ans": "田 / 山上",
        "hint": "種菜的地方"
    },
    {
        "type": "listening",
        "q": "I loma' ko mama.",
        "audio": "I loma' ko mama",
        "options": ["爸爸在家裡", "爸爸去上班", "爸爸在睡覺"],
        "ans": "爸爸在家裡",
        "hint": "Loma' 是家"
    }
]

# --- 3. 工具函數 ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except:
        st.error("語音生成暫時無法使用")

# 初始化 Session
if 'score' not in st.session_state: st.session_state.score = 0
if 'quiz_questions' not in st.session_state:
    # 每次重整時，隨機從題庫選 3 題，保持新鮮感
    st.session_state.quiz_questions = random.sample(quiz_pool, 3)
if 'current_q_idx' not in st.session_state: st.session_state.current_q_idx = 0

# --- 4. 主介面 ---
st.markdown("<h1 style='text-align: center; color: #2E7D32;'>Unit 13: I Cowa?</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>地點與移動 (Based on data.csv)</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📚 詞彙與句型", "🎲 隨機挑戰 (Random Quiz)"])

# === Tab 1: 學習模式 ===
with tab1:
    st.subheader("📝 核心單字 (無連字號)")
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
            if st.button(f"🔊 聽發音", key=f"btn_{word['amis']}"):
                play_audio(word['amis'])

    st.markdown("---")
    st.subheader("🗣️ 實用句型")
    for s in sentences:
        st.markdown(f"""
        <div style="background-color: #E8F5E9; border-left: 5px solid #4CAF50; padding: 15px; margin: 10px 0; border-radius: 0 10px 10px 0;">
            <div style="font-size: 20px; font-weight: bold; color: #1B5E20;">{s['icon']} {s['amis']}</div>
            <div style="font-size: 16px; color: #555; margin-top: 5px;">{s['chi']}</div>
            <div class="source-tag">src: {s['source']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"▶️ 播放句型", key=f"s_btn_{s['amis'][:5]}"):
            play_audio(s['amis'])

# === Tab 2: 隨機挑戰模式 ===
with tab2:
    st.markdown("### 🎲 隨機評量")
    st.caption("每次進入都會隨機抽出 3 題，考驗你的真實實力！")
    
    # 取得當前題目
    if st.session_state.current_q_idx < len(st.session_state.quiz_questions):
        q_data = st.session_state.quiz_questions[st.session_state.current_q_idx]
        
        # 顯示進度
        st.progress((st.session_state.current_q_idx) / 3)
        st.markdown(f"**Question {st.session_state.current_q_idx + 1} / 3**")
        
        # 顯示題目
        st.markdown(f"### {q_data['q']}")
        if q_data['audio']:
            if st.button("🎧 播放題目音檔"):
                play_audio(q_data['audio'])
        
        # 顯示選項 (Radio button)
        user_choice = st.radio("請選擇正確答案：", q_data['options'], key=f"q_{st.session_state.current_q_idx}")
        
        if st.button("送出答案"):
            if user_choice == q_data['ans']:
                st.balloons()
                st.success("🎉 答對了！")
                time.sleep(1.5)
                st.session_state.score += 100
                st.session_state.current_q_idx += 1
                st.rerun()
            else:
                st.error(f"不對喔！提示：{q_data['hint']}")
                
    else:
        # 全部完成
        st.progress(1.0)
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background-color: #C8E6C9; border-radius: 20px;'>
            <h1 style='color: #1B5E20;'>🏆 挑戰成功！</h1>
            <h3 style='color: #333;'>本次得分：{st.session_state.score}</h3>
            <p>你已經完成本輪隨機測試。</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 再來一局 (重新抽題)"):
            st.session_state.score = 0
            st.session_state.current_q_idx = 0
            st.session_state.quiz_questions = random.sample(quiz_pool, 3) # 重新抽題
            st.rerun()
