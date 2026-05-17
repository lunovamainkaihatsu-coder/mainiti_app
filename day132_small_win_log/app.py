import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import random

APP_TITLE = "Day132：小さな勝ちログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day132_small_win_log.json")

CATEGORIES = [
    "生活",
    "健康",
    "仕事",
    "勉強",
    "メンタル",
    "その他",
]

LUNA_COMMENTS = [
    "小さくても“できた”はちゃんと前進だよ。",
    "ご主人、その積み重ねかなり大事。",
    "今日はちゃんと勝ってる日だね。",
    "こういう小さい成功が、あとで大きく効いてくるよ。",
    "完璧じゃなくてOK。できたことを見ていこう。",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"wins": []}, f, ensure_ascii=False, indent=2)


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

    for x in data["wins"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "category": x["category"],
            "win": x["win"],
            "favorite": bool(x.get("favorite", False)),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🏆", layout="wide")
st.title("🏆 Day132：小さな勝ちログ")
st.caption("今日の“できた”を積み上げるアプリ。")

data = load_data()

left, right = st.columns([1,1], gap="large")

# ----------------------------
# 入力
# ----------------------------
with left:
    st.subheader("今日の勝ちを書く")

    win = st.text_area(
        "今日できたこと",
        height=140,
        placeholder="例：散歩した、5分だけ作業した、ちゃんと起きた"
    )

    category = st.selectbox("カテゴリ", CATEGORIES)

    mood = st.text_input(
        "今の気分（任意）",
        placeholder="例：少し安心した"
    )

    favorite = st.checkbox("⭐ 大事な勝ち")

    if st.button("🏆 勝ちを記録", type="primary"):
        if not win.strip():
            st.warning("小さなことでも書いてみよう")
        else:
            item = {
                "id": f"win_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "category": category,
                "win": win.strip(),
                "mood": mood.strip(),
                "favorite": favorite,
                "comment": random.choice(LUNA_COMMENTS),
            }

            data["wins"].append(item)
            save_data(data)

            st.success("今日の勝ちを保存したよ。")
            st.rerun()

# ----------------------------
# 表示
# ----------------------------
with right:
    st.subheader("最近の勝ち")

    df = to_df(data)

    if df.empty:
        st.info("まだ勝ちログがないよ")
    else:
        latest = data["wins"][-1]

        st.markdown(f"## {latest['win']}")
        st.write(f"カテゴリ：{latest['category']}")

        if latest.get("mood"):
            st.write(f"気分：{latest['mood']}")

        st.info(latest["comment"])

        total = len(data["wins"])
        st.metric("累計勝ち数", total)

st.divider()

# ----------------------------
# 履歴
# ----------------------------
st.subheader("履歴")

if not df.empty:

    fav_only = st.checkbox("⭐ 大事な勝ちだけ")

    view = df.copy()

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["category", "win", "favorite"]],
        use_container_width=True,
        height=320
    )

    selected = st.selectbox("詳細を見る", view["id"].tolist())

    item = next(
        (x for x in data["wins"] if x["id"] == selected),
        None
    )

    if item:
        st.markdown("### 勝ち内容")
        st.write(item["win"])

        st.write(f"カテゴリ：{item['category']}")

        if item.get("mood"):
            st.write(f"気分：{item['mood']}")

        st.info(item["comment"])

        col1, col2 = st.columns(2)

        with col1:
            fav = st.checkbox(
                "⭐ お気に入り",
                value=bool(item.get("favorite", False)),
                key=f"fav_{item['id']}"
            )

            if fav != bool(item.get("favorite", False)):
                item["favorite"] = fav
                save_data(data)
                st.rerun()

        with col2:
            if st.button("🗑️ 削除", key=f"del_{item['id']}"):
                data["wins"] = [
                    x for x in data["wins"]
                    if x["id"] != item["id"]
                ]
                save_data(data)
                st.rerun()

# ----------------------------
# CSV
# ----------------------------
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day132_small_win_log.csv",
        mime="text/csv"
    )
