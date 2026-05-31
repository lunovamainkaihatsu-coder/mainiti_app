import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day155：アイデア保管庫"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day155_idea_box.json")

CATEGORIES = [
    "アプリ",
    "ゲーム",
    "AI",
    "ブログ",
    "起業",
    "収益化",
    "趣味",
    "その他",
]

PRIORITIES = [
    "低",
    "中",
    "高",
    "神アイデア",
]

STATUS = [
    "メモ",
    "検討中",
    "作業中",
    "実現済み",
    "保留",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"ideas": []}, f, ensure_ascii=False, indent=2)


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

    for x in data["ideas"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "category": x["category"],
            "priority": x["priority"],
            "status": x["status"],
            "favorite": bool(x.get("favorite", False)),
            "content": x.get("content", ""),
            "next_step": x.get("next_step", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_idea(data, idea_id):
    for x in data["ideas"]:
        if x["id"] == idea_id:
            return x
    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💡",
    layout="wide"
)

st.title("💡 Day155：アイデア保管庫")
st.caption("思いついたアプリ案・ゲーム案・AI案・ブログ案を忘れないための保管庫。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("アイデアを保存")

    title = st.text_input(
        "タイトル",
        placeholder="例：筋トレ図鑑アプリ"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    priority = st.radio(
        "優先度",
        PRIORITIES,
        horizontal=True
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    content = st.text_area(
        "内容",
        height=160,
        placeholder="どんなアイデア？何ができる？誰に役立つ？"
    )

    next_step = st.text_input(
        "次の一歩",
        placeholder="例：画面構成だけ考える"
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="思いついた背景、参考、補足など"
    )

    favorite = st.checkbox("⭐ お気に入り")

    if st.button("💡 保存する", type="primary"):
        if not title.strip():
            st.warning("タイトルだけは入れてね。")
        else:
            item = {
                "id": f"idea_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "category": category,
                "priority": priority,
                "status": status,
                "content": content.strip(),
                "next_step": next_step.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["ideas"].append(item)
            save_data(data)

            st.success("アイデアを保存したよ。")
            st.rerun()

with right:
    st.subheader("アイデア一覧")

    df = to_df(data)

    if df.empty:
        st.info("まだアイデアがないよ。思いついたものを1つ入れてみよう。")
    else:
        keyword = st.text_input("🔎 検索", placeholder="タイトル・内容・次の一歩")
        category_filter = st.selectbox("カテゴリで絞る", ["すべて"] + CATEGORIES)
        status_filter = st.selectbox("状態で絞る", ["すべて"] + STATUS)
        fav_only = st.checkbox("⭐ お気に入りだけ")

        view = df.copy()

        if keyword.strip():
            q = keyword.strip()
            view = view[
                view["title"].fillna("").str.contains(q, case=False, na=False)
                | view["content"].fillna("").str.contains(q, case=False, na=False)
                | view["next_step"].fillna("").str.contains(q, case=False, na=False)
            ]

        if category_filter != "すべて":
            view = view[view["category"] == category_filter]

        if status_filter != "すべて":
            view = view[view["status"] == status_filter]

        if fav_only:
            view = view[view["favorite"] == True]

        st.metric("表示中のアイデア数", len(view))

        st.dataframe(
            view[["title", "category", "priority", "status", "favorite", "next_step"]],
            use_container_width=True,
            height=320
        )

st.divider()
st.subheader("詳細・更新")

df = to_df(data)

if df.empty:
    st.write("まだ詳細表示できるアイデアがないよ。")
else:
    options = df["id"].tolist()
    labels = {
        row["id"]: f"{row['title']} / {row['category']} / {row['priority']}"
        for _, row in df.iterrows()
    }

    selected_id = st.selectbox(
        "アイデアを選ぶ",
        options,
        format_func=lambda x: labels.get(x, x)
    )

    idea = find_idea(data, selected_id)

    if idea:
        st.markdown(f"## {idea['title']}")
        st.write(f"カテゴリ：{idea['category']}")
        st.write(f"優先度：{idea['priority']}")
        st.write(f"状態：{idea['status']}")

        st.markdown("### 内容")
        st.write(idea.get("content", ""))

        st.markdown("### 次の一歩")
        st.success(idea.get("next_step", ""))

        if idea.get("memo"):
            st.markdown("### メモ")
            st.info(idea.get("memo", ""))

        col1, col2, col3 = st.columns(3)

        with col1:
            new_status = st.selectbox(
                "状態変更",
                STATUS,
                index=STATUS.index(idea.get("status", "メモ")),
                key=f"status_{idea['id']}"
            )

        with col2:
            new_priority = st.selectbox(
                "優先度変更",
                PRIORITIES,
                index=PRIORITIES.index(idea.get("priority", "中")),
                key=f"priority_{idea['id']}"
            )

        with col3:
            new_fav = st.checkbox(
                "⭐ お気に入り",
                value=bool(idea.get("favorite", False)),
                key=f"fav_{idea['id']}"
            )

        new_next_step = st.text_input(
            "次の一歩を更新",
            value=idea.get("next_step", ""),
            key=f"next_{idea['id']}"
        )

        if st.button("📝 更新する"):
            idea["status"] = new_status
            idea["priority"] = new_priority
            idea["favorite"] = new_fav
            idea["next_step"] = new_next_step.strip()
            idea["updated_at"] = now_str()

            save_data(data)
            st.success("更新したよ。")
            st.rerun()

        if st.button("🗑️ このアイデアを削除", type="secondary"):
            data["ideas"] = [x for x in data["ideas"] if x["id"] != selected_id]
            save_data(data)
            st.warning("削除したよ。")
            st.rerun()

st.divider()

df = to_df(data)

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day155_idea_box.csv",
        mime="text/csv"
    )
