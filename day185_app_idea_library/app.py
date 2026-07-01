import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day185：アプリアイデア図鑑"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day185_app_idea_library.json")

CATEGORIES = [
    "健康",
    "お金",
    "生活",
    "AI",
    "読書",
    "開発",
    "目標",
    "ゲーム",
    "占い",
    "その他",
]

DIFFICULTIES = [
    "かんたん",
    "ふつう",
    "むずかしい",
    "大型",
]

PRIORITIES = [
    "🔴 最優先",
    "🟠 高",
    "🟡 普通",
    "🟢 低",
]

STATUS = [
    "未着手",
    "構想中",
    "制作中",
    "完成",
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
        data = json.load(f)

    if "ideas" not in data:
        data["ideas"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def priority_order(priority):
    return {
        "🔴 最優先": 0,
        "🟠 高": 1,
        "🟡 普通": 2,
        "🟢 低": 3,
    }.get(priority, 9)


def difficulty_order(difficulty):
    return {
        "かんたん": 0,
        "ふつう": 1,
        "むずかしい": 2,
        "大型": 3,
    }.get(difficulty, 9)


def to_df(data):
    rows = []

    for x in data["ideas"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "category": x["category"],
            "difficulty": x["difficulty"],
            "priority": x["priority"],
            "status": x["status"],
            "planned_date": x.get("planned_date", ""),
            "completed_date": x.get("completed_date", ""),
            "favorite": bool(x.get("favorite", False)),
            "description": x.get("description", ""),
            "features": x.get("features", ""),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["priority_order"] = df["priority"].apply(priority_order)
        df["difficulty_order"] = df["difficulty"].apply(difficulty_order)
        df = df.sort_values(
            ["favorite", "status", "priority_order", "difficulty_order", "created_at"],
            ascending=[False, True, True, True, False]
        )

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

st.title("💡 Day185：アプリアイデア図鑑")
st.caption("思いついたアプリアイデアを保存して、次に作るものを選びやすくするアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("アイデアを登録")

    title = st.text_input(
        "アプリ名・アイデア名",
        placeholder="例：AI献立相談室 / 習慣RPG / 貯金クエスト"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    difficulty = st.selectbox(
        "難易度",
        DIFFICULTIES
    )

    priority = st.selectbox(
        "優先度",
        PRIORITIES
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    planned_date = st.date_input(
        "作成予定日",
        value=date.today()
    )

    description = st.text_area(
        "概要",
        height=90,
        placeholder="どんなアプリ？誰の何を解決する？"
    )

    features = st.text_area(
        "主な機能",
        height=100,
        placeholder="例：登録、一覧、検索、グラフ、CSV出力"
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="思いついた背景、追加したい機能など"
    )

    favorite = st.checkbox("⭐ かなり作りたい")

    if st.button("💡 アイデアを保存", type="primary"):
        if not title.strip():
            st.warning("アイデア名を入れてね。")
        else:
            completed_date = today_str() if status == "完成" else ""

            item = {
                "id": f"idea_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "category": category,
                "difficulty": difficulty,
                "priority": priority,
                "status": status,
                "planned_date": planned_date.isoformat(),
                "completed_date": completed_date,
                "description": description.strip(),
                "features": features.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["ideas"].append(item)
            save_data(data)

            st.success("アプリアイデアを保存したよ。")
            st.rerun()

with right:
    st.subheader("アイデア状況")

    df = to_df(data)

    if df.empty:
        st.info("まだアイデアが登録されていないよ。")
    else:
        total = len(df)
        completed = len(df[df["status"] == "完成"])
        making = len(df[df["status"] == "制作中"])
        favorite_count = len(df[df["favorite"] == True])

        c1, c2 = st.columns(2)

        with c1:
            st.metric("アイデア数", total)
            st.metric("制作中", making)

        with c2:
            st.metric("完成", completed)
            st.metric("作りたい", favorite_count)

        if total > 0:
            rate = completed / total
            st.progress(rate)
            st.info(f"完成率：{round(rate * 100, 1)}%")

        st.divider()

        st.subheader("カテゴリ別")
        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "件数"]

        st.dataframe(
            cat_count,
            use_container_width=True,
            height=220
        )

st.divider()
st.subheader("アイデア一覧")

df = to_df(data)

if df.empty:
    st.write("まだ図鑑が空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="タイトル・概要・機能・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        status_filter = st.selectbox(
            "状態で絞る",
            ["すべて"] + STATUS
        )

    col_d, col_e, col_f = st.columns(3)

    with col_d:
        difficulty_filter = st.selectbox(
            "難易度で絞る",
            ["すべて"] + DIFFICULTIES
        )

    with col_e:
        priority_filter = st.selectbox(
            "優先度で絞る",
            ["すべて"] + PRIORITIES
        )

    with col_f:
        fav_only = st.checkbox("⭐ 作りたいものだけ")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["description"].fillna("").str.contains(q, case=False, na=False)
            | view["features"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if difficulty_filter != "すべて":
        view = view[view["difficulty"] == difficulty_filter]

    if priority_filter != "すべて":
        view = view[view["priority"] == priority_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[[
            "title",
            "category",
            "difficulty",
            "priority",
            "status",
            "planned_date",
            "completed_date",
            "favorite",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合うアイデアがないよ。")
    else:
        selected_id = st.selectbox(
            "アイデアを選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_idea(data, x)['title']} / {find_idea(data, x)['category']}"
        )

        idea = find_idea(data, selected_id)

        if idea:
            st.markdown(f"## {idea['title']}")
            st.write(f"カテゴリ：{idea['category']}")
            st.write(f"難易度：{idea['difficulty']}")
            st.write(f"優先度：{idea['priority']}")
            st.write(f"状態：{idea['status']}")
            st.write(f"作成予定日：{idea.get('planned_date', '')}")

            if idea.get("completed_date"):
                st.success(f"完成日：{idea['completed_date']}")

            if idea.get("description"):
                st.markdown("### 概要")
                st.info(idea["description"])

            if idea.get("features"):
                st.markdown("### 主な機能")
                st.write(idea["features"])

            if idea.get("memo"):
                st.markdown("### メモ")
                st.write(idea["memo"])

            c1, c2, c3 = st.columns(3)

            with c1:
                new_status = st.selectbox(
                    "状態を更新",
                    STATUS,
                    index=STATUS.index(idea.get("status", "未着手")),
                    key=f"status_{idea['id']}"
                )

            with c2:
                new_priority = st.selectbox(
                    "優先度を更新",
                    PRIORITIES,
                    index=PRIORITIES.index(idea.get("priority", "🟡 普通")),
                    key=f"priority_{idea['id']}"
                )

            with c3:
                new_favorite = st.checkbox(
                    "⭐ 作りたい",
                    value=bool(idea.get("favorite", False)),
                    key=f"fav_{idea['id']}"
                )

            if st.button("📝 更新する"):
                old_status = idea.get("status", "")

                idea["status"] = new_status
                idea["priority"] = new_priority
                idea["favorite"] = new_favorite
                idea["updated_at"] = now_str()

                if new_status == "完成" and old_status != "完成":
                    idea["completed_date"] = today_str()

                if new_status != "完成":
                    idea["completed_date"] = ""

                save_data(data)

                st.success("アイデアを更新したよ。")
                st.rerun()

            if st.button("🗑️ このアイデアを削除", type="secondary"):
                data["ideas"] = [
                    x for x in data["ideas"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day185_app_idea_library.csv",
        mime="text/csv"
    )
