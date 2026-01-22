import streamlit as st
import random
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="🌙 深夜の独り言AI", layout="centered")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※このアプリは創作・心理表現です。霊的存在や予言などは含みません。"


# --------------------
# データ保存系
# --------------------
def load_history():
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except:
        return []

def save_history(data):
    HISTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------
# セリフデータ
# --------------------
DARK_LINES = [
    "誰にも言えないことほど、心の真ん中にある。",
    "眠れない夜は、現実より正直になる。",
    "静かな部屋ほど、心の音はうるさい。",
    "考えすぎているわけじゃない。ただ、感じすぎているだけ。",
    "闇は怖いんじゃない。光を欲しがっているだけ。"
]

SOFT_LINES = [
    "今日は、ちゃんと頑張ってたよ。",
    "言葉にできない日も、無意味じゃない。",
    "何もしない時間も、あなたの一部。",
    "少し立ち止まっても、大丈夫。",
    "あなたは、思っているより優しい。"
]

PSY_LINES = [
    "今の気分は、心が『休ませて』って言っているサインかも。",
    "心は、ちゃんと現状を教えてくれている。",
    "その感情は、あなたの敵じゃない。",
    "感じていること自体が、前に進んでいる証。",
]

ENDING_LINES = [
    "今夜は、無理しなくていい。",
    "この夜が、あなたを守りますように。",
    "ちゃんと、朝は来るよ。",
    "今日は、ここまででいい。"
]


def generate_whisper(dark_mode: bool):
    main = random.choice(DARK_LINES if dark_mode else SOFT_LINES)
    psy = random.choice(PSY_LINES)
    end = random.choice(ENDING_LINES)
    return main, psy, end


# --------------------
# UI
# --------------------
st.title("🌙 深夜の独り言AI")
st.caption("眠れない夜に、ルナがそっと囁きます。")
st.info(DISCLAIMER)

mood = st.text_input("今の気分（任意）", placeholder="例：眠れない、虚しい、焦る、理由はない…")
dark_mode = st.toggle("🌑 深夜モード（闇寄り）", value=True)

if st.button("独り言を聞く", use_container_width=True):
    main, psy, end = generate_whisper(dark_mode)
    st.session_state["result"] = (main, psy, end)

if "result" in st.session_state:
    main, psy, end = st.session_state["result"]

    st.subheader("🕯 ルナの独り言")
    st.markdown(f"**{main}**")
    st.caption(f"🌑 {psy}")
    st.markdown(f"🌙 *{end}*")

    history = load_history()
    if st.button("💾 保存する"):
        history.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "mood": mood,
            "dark_mode": dark_mode,
            "main": main,
            "psy": psy,
            "end": end
        })
        save_history(history)
        st.success("保存しました")

with st.expander("🗂 過去の独り言（最新10件）"):
    history = load_history()
    if not history:
        st.write("まだ記録がありません")
    else:
        for row in reversed(history[-10:]):
            st.markdown(f"**{row['time']}**｜気分：{row.get('mood','')}")
            st.markdown(row["main"])
            st.caption(row["psy"])
            st.markdown(f"*{row['end']}*")
            st.write("---")
