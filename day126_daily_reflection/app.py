import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import random

APP_TITLE = "Day126：今日のふりかえりAI"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day126_daily_reflection.json")

LUNA_COMMENTS = [
    "今日はちゃんと進んでる日だね。小さくても前に進んでるのが大事。",
    "完璧じゃなくていいよ。ちゃんと振り返れてる時点で強い。",
    "できたこと、ちゃんと見てるのえらいよ。そこが次につながる。",
    "今日は守りの日だったかもね。それでもちゃんと意味あるよ。",
    "明日の1つを決めたのいいね。それだけで流れ変わるよ。",
]


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
            "mood": x["mood"],
            "favorite": x.get("favorite", False),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🌙", layout="wide")
st.title("🌙 Day126：今日のふりかえりAI")
st.caption("1日を軽く振り返って、明日につなげるアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1,1])

# 入力
with left:
    st.subheader("今日のふりかえり")

    did = st.text_area("できたこと")
    not_did = st.text_area("できなかったこと")
    mood = st.text_input("今日の気分")
    tomorrow = st.text_input("明日やること1つ")

    if st.button("🌙 ふりかえり保存", type="primary"):
        if not did.strip() and not_did.strip():
            st.warning("少しだけでも書こう")
        else:
            comment = random.choice(LUNA_COMMENTS)

            item = {
                "id": f"log_{datetime.now().strftime('%H%M%S%f')}",
                "created_at": now_str(),
                "did": did,
                "not_did": not_did,
                "mood": mood,
                "tomorrow": tomorrow,
                "comment": comment,
                "favorite": False,
            }

            data["logs"].append(item)
            save_data(data)
            st.session_state["latest"] = item
            st.rerun()

# 表示
with right:
    st.subheader("今日のまとめ")

    latest = st.session_state.get("latest")

    if latest:
        st.markdown("### できたこと")
        st.write(latest["did"])

        st.markdown("### できなかったこと")
        st.write(latest["not_did"])

        st.markdown("### 気分")
        st.write(latest["mood"])

        st.markdown("### 明日")
        st.success(latest["tomorrow"])

        st.markdown("### ルナのコメント")
        st.info(latest["comment"])

        fav = st.checkbox("⭐", value=latest.get("favorite", False))
        if fav != latest.get("favorite", False):
            latest["favorite"] = fav
            for x in data["logs"]:
                if x["id"] == latest["id"]:
                    x["favorite"] = fav
            save_data(data)

st.divider()

df = to_df(data)

if not df.empty:
    st.subheader("履歴")
    st.dataframe(df)

    selected = st.selectbox("選択", df["id"].tolist())

    for x in data["logs"]:
        if x["id"] == selected:
            item = x
            break

    st.markdown("### 詳細")
    st.write(item["did"])
    st.write(item["not_did"])
    st.write(item["mood"])
    st.write(item["tomorrow"])
