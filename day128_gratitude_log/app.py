import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day128：今日のありがとう記録"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day128_gratitude_log.json")


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
            "content": x["content"],
            "who": x.get("who", ""),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🙏", layout="wide")
st.title("🙏 Day128：今日のありがとう記録")
st.caption("今日の“ありがとう”を1つだけ残すアプリ。")

data = load_data()

left, right = st.columns([1,1])

# 入力
with left:
    st.subheader("ありがとうを書く")

    content = st.text_area("ありがとう内容", height=120)
    who = st.text_input("誰に（任意）")
    note = st.text_area("メモ（任意）", height=80)
    favorite = st.checkbox("⭐ 大事なありがとう")

    if st.button("🙏 記録する", type="primary"):
        if not content.strip():
            st.warning("ひとこと書こう")
        else:
            item = {
                "id": f"log_{datetime.now().strftime('%H%M%S%f')}",
                "created_at": now_str(),
                "content": content.strip(),
                "who": who.strip(),
                "note": note.strip(),
                "favorite": favorite,
            }
            data["logs"].append(item)
            save_data(data)
            st.success("ありがとうを記録したよ")
            st.rerun()

# 表示
with right:
    st.subheader("今日のありがとう")

    if data["logs"]:
        latest = data["logs"][-1]

        st.markdown("### 🙏")
        st.write(latest["content"])

        if latest.get("who"):
            st.write(f"→ {latest['who']}へ")

        st.info("いい1日だったね。")

st.divider()

# 履歴
st.subheader("履歴")

df = to_df(data)

if not df.empty:
    fav_only = st.checkbox("⭐ 大事なものだけ")

    view = df.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view)

    selected = st.selectbox("選択", view["id"].tolist())

    for x in data["logs"]:
        if x["id"] == selected:
            item = x
            break

    st.markdown("### 詳細")
    st.write(item["content"])
    st.write(item.get("who",""))
    st.write(item.get("note",""))

    if st.button("🗑️ 削除"):
        data["logs"] = [x for x in data["logs"] if x["id"] != selected]
        save_data(data)
        st.rerun()

# CSV
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ CSVダウンロード", data=csv)
