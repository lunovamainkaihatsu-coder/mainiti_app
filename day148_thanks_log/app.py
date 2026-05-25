import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd
import random

APP_TITLE = "Day148：ありがとうログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day148_thanks_log.json")

LUNA_COMMENTS = [
    "ご主人、ありがとうを見つけられる日って、それだけで少し優しい日だよ。",
    "小さな感謝を残すの、すごくいい習慣だよ。",
    "今日の中にちゃんと光を見つけられたね。",
    "ありがとうって、未来の自分を少し温めてくれるんだよ。",
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


def today_str():
    return date.today().isoformat()


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "thanks_1": x.get("thanks_1", ""),
            "thanks_2": x.get("thanks_2", ""),
            "thanks_3": x.get("thanks_3", ""),
            "memo": x.get("memo", ""),
            "favorite": bool(x.get("favorite", False)),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🙏", layout="wide")
st.title("🙏 Day148：ありがとうログ")
st.caption("今日ありがたかったことを、1〜3つ残すアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日のありがとうを書く")

    thanks_1 = st.text_input("ありがとう 1", placeholder="例：朝ごはんがおいしかった")
    thanks_2 = st.text_input("ありがとう 2", placeholder="例：娘が笑ってくれた")
    thanks_3 = st.text_input("ありがとう 3", placeholder="例：少し作業できた")

    memo = st.text_area(
        "メモ",
        height=100,
        placeholder="今日の気づきや、残しておきたいこと"
    )

    favorite = st.checkbox("⭐ 大事なありがとう")

    if st.button("🙏 保存する", type="primary"):
        if not thanks_1.strip() and not thanks_2.strip() and not thanks_3.strip():
            st.warning("1つだけでも書いてみよう。")
        else:
            item = {
                "id": f"thanks_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "thanks_1": thanks_1.strip(),
                "thanks_2": thanks_2.strip(),
                "thanks_3": thanks_3.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
                "comment": random.choice(LUNA_COMMENTS),
            }

            data["logs"].append(item)
            save_data(data)
            st.success("ありがとうを保存したよ。")
            st.rerun()

with right:
    st.subheader("今日のありがとう")

    today_logs = [x for x in data["logs"] if x["date"] == today_str()]

    if not today_logs:
        st.info("今日のありがとうはまだないよ。")
    else:
        latest = sorted(today_logs, key=lambda x: x["created_at"])[-1]

        st.markdown("### 今日見つけた光")
        for key in ["thanks_1", "thanks_2", "thanks_3"]:
            if latest.get(key):
                st.success(latest[key])

        if latest.get("memo"):
            st.write(f"メモ：{latest['memo']}")

        st.markdown("### ルナのひとこと")
        st.info(latest.get("comment", ""))

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ 大事なありがとうだけ表示")
    view = df.copy()

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "thanks_1", "thanks_2", "thanks_3", "memo", "favorite"]],
        use_container_width=True,
        height=320
    )

    selected = st.selectbox("削除する記録を選ぶ", view["id"].tolist())

    if st.button("🗑️ 選択した記録を削除", type="secondary"):
        data["logs"] = [x for x in data["logs"] if x["id"] != selected]
        save_data(data)
        st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day148_thanks_log.csv",
        mime="text/csv"
    )
