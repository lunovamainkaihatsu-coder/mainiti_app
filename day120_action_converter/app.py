import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day120：学びアクション化ボタン"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day120_action_converter.json")

STATUS = ["未着手", "実行中", "完了"]

TEMPLATES = [
    "5分だけ試してみる",
    "1つだけ書き出す",
    "1回だけ実行してみる",
    "軽く調べてみる",
    "誰かに話してみる",
    "メモを1つ残す",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"actions": []}, f, ensure_ascii=False, indent=2)


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
    for x in data["actions"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "learning": x["learning"],
            "action": x["action"],
            "status": x["status"],
            "favorite": x.get("favorite", False),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def generate_action(text):
    template = random.choice(TEMPLATES)
    return f"{text} → {template}"


st.set_page_config(page_title=APP_TITLE, page_icon="⚡", layout="wide")
st.title("⚡ Day120：学びアクション化ボタン")
st.caption("学びを“今日やる小さな行動”に変換するアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1,1])

# 入力
with left:
    st.subheader("学びを入力")

    learning = st.text_area("学び・気づき", height=120)

    if st.button("⚡ アクション化", type="primary"):
        if not learning.strip():
            st.warning("何か入力してね")
        else:
            action_text = generate_action(learning.strip())

            item = {
                "id": f"act_{datetime.now().strftime('%H%M%S%f')}",
                "created_at": now_str(),
                "learning": learning.strip(),
                "action": action_text,
                "status": "未着手",
                "favorite": False,
            }

            data["actions"].append(item)
            save_data(data)
            st.session_state["latest"] = item
            st.rerun()

# 表示
with right:
    st.subheader("今日のアクション")

    latest = st.session_state.get("latest")

    if latest:
        st.markdown(f"## {latest['action']}")

        st.markdown("### 元の学び")
        st.write(latest["learning"])

        fav = st.checkbox("⭐ お気に入り", value=latest.get("favorite", False))
        if fav != latest.get("favorite", False):
            latest["favorite"] = fav
            for x in data["actions"]:
                if x["id"] == latest["id"]:
                    x["favorite"] = fav
            save_data(data)

st.divider()

st.subheader("履歴")

df = to_df(data)

if not df.empty:
    st.dataframe(df)

    selected = st.selectbox("選択", df["id"].tolist())

    for x in data["actions"]:
        if x["id"] == selected:
            item = x
            break

    st.markdown(f"### {item['action']}")
    st.write(item["learning"])

    new_status = st.selectbox("ステータス", STATUS, index=STATUS.index(item["status"]))

    if new_status != item["status"]:
        item["status"] = new_status
        save_data(data)
        st.rerun()

    if st.button("🗑️ 削除"):
        data["actions"] = [x for x in data["actions"] if x["id"] != selected]
        save_data(data)
        st.rerun()
