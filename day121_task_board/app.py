import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day121：やること整理ボード"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day121_task_board.json")

CATEGORIES = ["今日", "今週", "いつか"]
STATUS = ["未着手", "進行中", "完了"]


# ----------------------------
# storage
# ----------------------------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"tasks": []}, f, ensure_ascii=False, indent=2)


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
    for x in data["tasks"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "task": x["task"],
            "category": x["category"],
            "status": x["status"],
            "favorite": x.get("favorite", False),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🗂️", layout="wide")
st.title("🗂️ Day121：やること整理ボード")
st.caption("今日・今週・いつかでタスクを整理するシンプルアプリ。")

data = load_data()

# ----------------------------
# タスク追加
# ----------------------------
st.subheader("タスク追加")

col1, col2 = st.columns([3,1])

with col1:
    new_task = st.text_input("やること")

with col2:
    category = st.selectbox("分類", CATEGORIES)

if st.button("➕ 追加", type="primary"):
    if not new_task.strip():
        st.warning("タスクを入力してね")
    else:
        task = {
            "id": f"task_{datetime.now().strftime('%H%M%S%f')}",
            "created_at": now_str(),
            "task": new_task.strip(),
            "category": category,
            "status": "未着手",
            "favorite": False,
        }
        data["tasks"].append(task)
        save_data(data)
        st.rerun()

st.divider()

# ----------------------------
# ボード表示
# ----------------------------
cols = st.columns(3)

for i, cat in enumerate(CATEGORIES):
    with cols[i]:
        st.subheader(cat)

        for t in data["tasks"]:
            if t["category"] == cat:

                with st.container():
                    st.markdown(f"**{t['task']}**")
                    st.caption(f"状態：{t['status']}")

                    col_a, col_b, col_c = st.columns(3)

                    # ステータス変更
                    with col_a:
                        new_status = st.selectbox(
                            "状態",
                            STATUS,
                            index=STATUS.index(t["status"]),
                            key=f"status_{t['id']}"
                        )
                        if new_status != t["status"]:
                            t["status"] = new_status
                            save_data(data)
                            st.rerun()

                    # お気に入り
                    with col_b:
                        fav = st.checkbox("⭐", value=t.get("favorite", False), key=f"fav_{t['id']}")
                        if fav != t.get("favorite", False):
                            t["favorite"] = fav
                            save_data(data)
                            st.rerun()

                    # 削除
                    with col_c:
                        if st.button("🗑️", key=f"del_{t['id']}"):
                            data["tasks"] = [x for x in data["tasks"] if x["id"] != t["id"]]
                            save_data(data)
                            st.rerun()

                    st.divider()

st.divider()

# ----------------------------
# CSV
# ----------------------------
df = to_df(data)

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ CSVダウンロード", data=csv)
