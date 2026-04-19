import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day113：今日の気分アイコン"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day113_mood_icon.json")

ICONS = [
    {"emoji": "😊", "name": "いい感じ", "desc": "安定 or ちょっと前向き"},
    {"emoji": "😴", "name": "ねむい", "desc": "疲れ気味 or エネルギー低め"},
    {"emoji": "☁️", "name": "もやもや", "desc": "はっきりしない状態"},
    {"emoji": "🔥", "name": "やる気", "desc": "少し動けそう"},
    {"emoji": "🌙", "name": "静か", "desc": "落ち着きたい状態"},
    {"emoji": "🌈", "name": "うれしい", "desc": "いいことあった日"},
    {"emoji": "💤", "name": "省エネ", "desc": "最低限でいきたい日"},
    {"emoji": "🫠", "name": "とろけ", "desc": "回復優先状態"},
]

LUNA_COMMENTS = {
    "いい感じ": "ご主人、この調子でゆるく進もうね。",
    "ねむい": "今日は無理せず、回復優先でいこう。",
    "もやもや": "はっきりしなくても大丈夫。そのままでいいよ。",
    "やる気": "お、ちょっと来てるね。小さく動いてみよ？",
    "静か": "今日は静かに過ごすのが正解かも。",
    "うれしい": "その気持ち、大事にしていこうね。",
    "省エネ": "今日は省エネでもOK。ゼロじゃなければ勝ち。",
    "とろけ": "ご主人、今日はとことん休もう。",
}


# ----------------------------
# storage
# ----------------------------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "emoji": x["emoji"],
            "name": x["name"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🌈", layout="wide")
st.title("🌈 Day113：今日の気分アイコン")
st.caption("今日はどんな状態か、直感で選ぶアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSV", data=csv)

left, right = st.columns([1,1])

with left:
    st.subheader("気分を選ぶ")

    options = [f"{i['emoji']} {i['name']}" for i in ICONS]
    selected = st.radio("今日の気分", options)

    if st.button("🌈 決定", type="primary"):
        idx = options.index(selected)
        icon = ICONS[idx]

        result = {
            "id": f"log_{datetime.now().strftime('%H%M%S%f')}",
            "created_at": now_str(),
            "emoji": icon["emoji"],
            "name": icon["name"],
            "desc": icon["desc"],
            "luna": LUNA_COMMENTS[icon["name"]],
            "favorite": False,
        }

        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日の状態")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"## {latest['emoji']} {latest['name']}")
        st.write(latest["desc"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

        fav = st.checkbox("⭐ お気に入り", value=latest.get("favorite", False))
        if fav != latest.get("favorite", False):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
            save_data(data)

st.divider()

df = to_df(data)
if not df.empty:
    st.dataframe(df)
