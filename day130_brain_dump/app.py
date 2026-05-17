import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day130：脳内ごちゃごちゃ整理メモ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day130_brain_dump.json")

CATEGORIES = [
    "不安",
    "やること",
    "アイデア",
    "欲望",
    "気になること",
    "その他",
]

PRIORITIES = ["低", "中", "高"]


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


def to_df(data):
    rows = []
    for x in data["memos"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "category": x["category"],
            "priority": x["priority"],
            "content": x["content"],
            "favorite": bool(x.get("favorite", False)),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🧠", layout="wide")
st.title("🧠 Day130：脳内ごちゃごちゃ整理メモ")
st.caption("頭の中を外に出して、少し整理するアプリ。")

data = load_data()

left, right = st.columns([1,1], gap="large")

# ----------------------------
# 入力
# ----------------------------
with left:
    st.subheader("書き出す")

    content = st.text_area(
        "頭の中にあること",
        height=180,
        placeholder="思いついたこと、不安、やること、なんでもOK"
    )

    category = st.selectbox("分類", CATEGORIES)
    priority = st.selectbox("優先度", PRIORITIES, index=1)
    favorite = st.checkbox("⭐ 大事")

    if st.button("🧠 整理メモ保存", type="primary"):
        if not content.strip():
            st.warning("何か書いてみよう")
        else:
            item = {
                "id": f"memo_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "content": content.strip(),
                "category": category,
                "priority": priority,
                "favorite": favorite,
            }

            data["memos"].append(item)
            save_data(data)

            st.success("頭の中を少し外に出せたね。")
            st.rerun()

# ----------------------------
# 表示
# ----------------------------
with right:
    st.subheader("整理されたメモ")

    df = to_df(data)

    if df.empty:
        st.info("まだメモがないよ")
    else:
        keyword = st.text_input("🔎 検索")
        cat_filter = st.selectbox("分類フィルタ", ["すべて"] + CATEGORIES)
        fav_only = st.checkbox("⭐ 大事だけ")

        view = df.copy()

        if keyword.strip():
            view = view[
                view["content"].str.contains(keyword, case=False, na=False)
            ]

        if cat_filter != "すべて":
            view = view[view["category"] == cat_filter]

        if fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(
            view[["category", "priority", "content", "favorite"]],
            use_container_width=True,
            height=360
        )

        st.divider()

        if not view.empty:
            selected = st.selectbox("詳細を見る", view["id"].tolist())

            item = next(
                (x for x in data["memos"] if x["id"] == selected),
                None
            )

            if item:
                st.markdown(f"### {item['category']} / 優先度：{item['priority']}")
                st.write(item["content"])

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
                        data["memos"] = [
                            x for x in data["memos"]
                            if x["id"] != item["id"]
                        ]
                        save_data(data)
                        st.rerun()

# ----------------------------
# CSV
# ----------------------------
st.divider()

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day130_brain_dump.csv",
        mime="text/csv"
    )
