import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day122：習慣チェック表"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day122_habit_tracker.json")


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"habits": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today_str():
    return date.today().isoformat()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calc_streak(logs):
    streak = 0
    today = date.today()

    for i in range(0, 365):
        d = (today - pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        if d in logs:
            streak += 1
        else:
            break
    return streak


def calc_rate(logs):
    if not logs:
        return 0
    return int(len(logs) / 30 * 100)  # 30日基準


st.set_page_config(page_title=APP_TITLE, page_icon="✅", layout="wide")
st.title("✅ Day122：習慣チェック表")
st.caption("毎日の習慣をチェックして、継続を見える化するアプリ。")

data = load_data()

# ----------------------------
# 習慣追加
# ----------------------------
st.subheader("習慣を追加")

col1, col2 = st.columns([3,1])

with col1:
    new_habit = st.text_input("習慣名（例：筋トレ、読書）")

with col2:
    if st.button("➕ 追加", type="primary"):
        if not new_habit.strip():
            st.warning("入力してね")
        else:
            habit = {
                "id": f"hab_{datetime.now().strftime('%H%M%S%f')}",
                "name": new_habit.strip(),
                "created_at": now_str(),
                "logs": [],
                "favorite": False,
            }
            data["habits"].append(habit)
            save_data(data)
            st.rerun()

st.divider()

# ----------------------------
# 習慣一覧
# ----------------------------
st.subheader("今日の習慣")

today = today_str()

for h in data["habits"]:
    with st.container():
        st.markdown(f"### {h['name']}")

        done_today = today in h["logs"]

        col1, col2, col3, col4 = st.columns(4)

        # チェック
        with col1:
            checked = st.checkbox("今日やった", value=done_today, key=h["id"])
            if checked and not done_today:
                h["logs"].append(today)
                save_data(data)
                st.rerun()
            elif not checked and done_today:
                h["logs"].remove(today)
                save_data(data)
                st.rerun()

        # 連続日数
        with col2:
            st.write(f"連続：{calc_streak(h['logs'])}日")

        # 達成率
        with col3:
            st.write(f"達成率：{calc_rate(h['logs'])}%")

        # お気に入り
        with col4:
            fav = st.checkbox("⭐", value=h.get("favorite", False), key=f"fav_{h['id']}")
            if fav != h.get("favorite", False):
                h["favorite"] = fav
                save_data(data)
                st.rerun()

        # 削除
        if st.button("🗑️ 削除", key=f"del_{h['id']}"):
            data["habits"] = [x for x in data["habits"] if x["id"] != h["id"]]
            save_data(data)
            st.rerun()

        st.divider()

# ----------------------------
# CSV
# ----------------------------
rows = []
for h in data["habits"]:
    for d in h["logs"]:
        rows.append({
            "habit": h["name"],
            "date": d
        })

df = pd.DataFrame(rows)

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ CSVダウンロード", data=csv)
