import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day101：今日の運勢カード"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day101_fortune_card.json")

FORTUNE_POOL = [
    ("大吉", "今日は流れがかなりいい日。迷ったら前へ。", "やりたいことを1つ実行"),
    ("中吉", "安定して進める日。丁寧さが鍵。", "小さなタスクを1つ終わらせる"),
    ("小吉", "少しずつ前進できる日。焦らなくてOK。", "5分だけ行動する"),
    ("吉", "無理せず整える日。土台作りが大事。", "環境を少し整える"),
    ("末吉", "今日は回復寄り。守る選択も正解。", "休息を優先する"),
]

SSR_SPECIAL = [
    ("超大吉", "流れが来てる。これは動くタイミング。", "一歩踏み出す"),
]

LUNA_COMMENTS = [
    "ご主人、今日はこの流れに乗っていこう。",
    "無理しなくても大丈夫、でも少しだけ動こうね。",
    "ちゃんと前に進んでるよ。",
    "今日はやさしくいこう。",
    "その選択、いいと思うよ。",
]


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
            "fortune": x["fortune"],
            "favorite": x.get("favorite", False),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# logic
# ----------------------------
def draw_card():
    if random.random() < 0.05:
        fortune, text, action = random.choice(SSR_SPECIAL)
        rarity = "SSR"
    else:
        fortune, text, action = random.choice(FORTUNE_POOL)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "fortune": fortune,
        "text": text,
        "action": action,
        "luna": random.choice(LUNA_COMMENTS),
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="wide")
st.title("🔮 Day101：今日の運勢カード")
st.caption("今日の流れを1枚のカードで受け取る")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

if st.button("🔮 カードを引く", type="primary"):
    result = draw_card()
    data["logs"].append(result)
    save_data(data)
    st.session_state["latest"] = result
    st.rerun()

st.divider()

latest = st.session_state.get("latest")
if latest:
    if latest["rarity"] == "SSR":
        st.success("✨ 超大吉 ✨")

    st.markdown(f"## {latest['fortune']}")
    st.write(latest["text"])

    st.markdown("### 今日の行動")
    st.success(latest["action"])

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

st.subheader("履歴")

df = to_df(data)
if df.empty:
    st.write("まだなし")
else:
    st.dataframe(df)
