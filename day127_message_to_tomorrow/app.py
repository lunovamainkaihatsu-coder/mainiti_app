import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd

APP_TITLE = "Day127：明日の自分へメモ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day127_message_to_tomorrow.json")


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"memos": []}, f, ensure_ascii=False, indent=2)


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


def tomorrow_str():
    return (date.today() + timedelta(days=1)).isoformat()


def today_str():
    return date.today().isoformat()


def to_df(data):
    rows = []
    for x in data["memos"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "target_date": x["target_date"],
            "message": x["message"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="✉️", layout="wide")
st.title("✉️ Day127：明日の自分へメモ")
st.caption("夜に一言残して、明日の自分を少し助けるアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("明日の自分へ残す")

    message = st.text_area(
        "メッセージ",
        height=160,
        placeholder="例：明日はまず水を飲んで、5分だけアプリを触ろう。"
    )

    target = st.date_input("届ける日", value=date.today() + timedelta(days=1))
    favorite = st.checkbox("⭐ 大事なメモにする")

    if st.button("✉️ 明日の自分へ保存", type="primary"):
        if not message.strip():
            st.warning("一言だけでも書いてね。")
        else:
            item = {
                "id": f"memo_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "target_date": target.isoformat(),
                "message": message.strip(),
                "favorite": favorite,
            }
            data["memos"].append(item)
            save_data(data)
            st.session_state["latest"] = item
            st.success("明日の自分へメモを残したよ。")
            st.rerun()

with right:
    st.subheader("今日届いているメモ")

    today_memos = [x for x in data["memos"] if x.get("target_date") == today_str()]

    if today_memos:
        for m in sorted(today_memos, key=lambda x: x["created_at"], reverse=True):
            st.markdown(f"### {'⭐ ' if m.get('favorite') else ''}メモ")
            st.write(m["message"])
            st.caption(f"作成：{m['created_at']}")
            st.divider()
    else:
        st.info("今日届いているメモはまだないよ。")

    st.subheader("最新保存メモ")
    latest = st.session_state.get("latest")
    if latest:
        st.success(latest["message"])
        st.caption(f"届ける日：{latest['target_date']}")

st.divider()
st.subheader("履歴")

df = to_df(data)
if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ 大事なメモだけ表示", value=False)
    view = df.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        selected = st.selectbox("メモを選ぶ", view["id"].tolist())
        chosen = next((x for x in data["memos"] if x["id"] == selected), None)

        if chosen:
            st.markdown("### メッセージ")
            st.write(chosen["message"])
            st.write(f"届ける日：{chosen['target_date']}")
            st.write(f"作成日：{chosen['created_at']}")

            fav = st.checkbox("⭐ 大事なメモ", value=bool(chosen.get("favorite", False)))
            if fav != bool(chosen.get("favorite", False)):
                chosen["favorite"] = fav
                save_data(data)
                st.rerun()

            if st.button("🗑️ 削除", type="secondary"):
                data["memos"] = [x for x in data["memos"] if x["id"] != selected]
                save_data(data)
                st.rerun()

csv = df.to_csv(index=False).encode("utf-8-sig") if not df.empty else None
if csv:
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day127_message_to_tomorrow.csv",
        mime="text/csv"
    )
