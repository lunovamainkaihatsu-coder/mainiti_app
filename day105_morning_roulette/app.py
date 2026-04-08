import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day105：おはようルーレット"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day105_morning_roulette.json")

MORNING_POOL = [
    {
        "type": "攻め",
        "message": "今日は少し前に出られる日かも。",
        "action": "やりたいことを1つだけやる",
        "luna": "ご主人、今日はちょっとだけ踏み出してみよ？"
    },
    {
        "type": "守り",
        "message": "今日は整えながら進む日。",
        "action": "小さなタスクを1つ片付ける",
        "luna": "無理しなくていいよ、でも止まらないでいこうね。"
    },
    {
        "type": "回復",
        "message": "今日は回復優先でもいい日。",
        "action": "ゆっくりする時間を作る",
        "luna": "ご主人、守る日もちゃんと大事だからね。"
    },
    {
        "type": "遊び",
        "message": "今日は少し楽しさを優先してみて。",
        "action": "楽しいことを1つやる",
        "luna": "楽しいって、ちゃんと未来に効くんだよ。"
    },
    {
        "type": "静か",
        "message": "今日は落ち着いて過ごすとよさそう。",
        "action": "深呼吸してから行動する",
        "luna": "焦らなくて大丈夫。静かなスタートもいいよ。"
    },
]

RARITY = [
    ("N", 0.7),
    ("R", 0.25),
    ("SR", 0.05),
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
            "type": x["type"],
            "rarity": x["rarity"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# logic
# ----------------------------
def pick_rarity():
    r = random.random()
    acc = 0
    for rarity, prob in RARITY:
        acc += prob
        if r <= acc:
            return rarity
    return "N"


def draw_morning():
    rarity = pick_rarity()
    item = random.choice(MORNING_POOL)

    luna = item["luna"]
    if rarity == "R":
        luna += " 今日はちょっといい流れ来てるかも。"
    elif rarity == "SR":
        luna += " しかも今日はかなりいい日だよ。"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "type": item["type"],
        "message": item["message"],
        "action": item["action"],
        "luna": luna,
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🌅", layout="wide")
st.title("🌅 Day105：おはようルーレット")
st.caption("朝に1回、今日の方向性を受け取るアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day105_morning_roulette.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest"] = None
        st.rerun()

left, right = st.columns([1, 1])

with left:
    if st.button("🌅 ルーレットを回す", type="primary"):
        result = draw_morning()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    latest = st.session_state.get("latest")
    if latest:
        st.markdown(f"## {latest['type']}")
        st.write(latest["message"])

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

df = to_df(data)
if not df.empty:
    st.dataframe(df)
