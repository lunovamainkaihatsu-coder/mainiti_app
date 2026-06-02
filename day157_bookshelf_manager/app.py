import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day157：本棚管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day157_bookshelf_manager.json")

GENRES = [
    "自己啓発",
    "ビジネス",
    "お金",
    "AI・技術",
    "心理学",
    "健康",
    "スピリチュアル",
    "小説",
    "漫画",
    "その他",
]

STATUS = [
    "読みたい",
    "積読",
    "読書中",
    "読了",
    "再読したい",
]

RATINGS = [
    "未評価",
    "★",
    "★★",
    "★★★",
    "★★★★",
    "★★★★★",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"books": []}, f, ensure_ascii=False, indent=2)


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

    for x in data["books"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "author": x.get("author", ""),
            "genre": x["genre"],
            "status": x["status"],
            "rating": x.get("rating", "未評価"),
            "favorite": bool(x.get("favorite", False)),
            "learning": x.get("learning", ""),
            "next_action": x.get("next_action", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_book(data, book_id):
    for x in data["books"]:
        if x["id"] == book_id:
            return x
    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide"
)

st.title("📚 Day157：本棚管理アプリ")
st.caption("読んだ本・読みたい本・学んだことをまとめて管理するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("本を登録")

    title = st.text_input(
        "本のタイトル",
        placeholder="例：金持ち父さん貧乏父さん"
    )

    author = st.text_input(
        "著者",
        placeholder="例：ロバート・キヨサキ"
    )

    genre = st.selectbox(
        "ジャンル",
        GENRES
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    rating = st.selectbox(
        "評価",
        RATINGS
    )

    summary = st.text_area(
        "ざっくり内容",
        height=120,
        placeholder="この本はどんな内容？"
    )

    learning = st.text_area(
        "学んだこと",
        height=120,
        placeholder="印象に残ったこと、気づき"
    )

    next_action = st.text_input(
        "次の行動",
        placeholder="例：1つだけ実践する / メモを見返す"
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="読んだ日、買った理由、気になる章など"
    )

    favorite = st.checkbox("⭐ お気に入り本")

    if st.button("📚 本棚に登録", type="primary"):
        if not title.strip():
            st.warning("タイトルだけは入れてね。")
        else:
            item = {
                "id": f"book_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "author": author.strip(),
                "genre": genre,
                "status": status,
                "rating": rating,
                "summary": summary.strip(),
                "learning": learning.strip(),
                "next_action": next_action.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["books"].append(item)
            save_data(data)

            st.success("本棚に登録したよ。")
            st.rerun()

with right:
    st.subheader("本棚ステータス")

    df = to_df(data)

    total = len(df) if not df.empty else 0
    finished = len(df[df["status"] == "読了"]) if not df.empty else 0
    reading = len(df[df["status"] == "読書中"]) if not df.empty else 0
    want = len(df[df["status"].isin(["読みたい", "積読"])]) if not df.empty else 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("登録冊数", total)
        st.metric("読了", finished)

    with col2:
        st.metric("読書中", reading)
        st.metric("読みたい/積読", want)

    st.divider()

    if not df.empty:
        st.subheader("ジャンル別")
        genre_count = df["genre"].value_counts().reset_index()
        genre_count.columns = ["ジャンル", "冊数"]
        st.dataframe(genre_count, use_container_width=True, height=220)
    else:
        st.info("まだ本が登録されてないよ。")

st.divider()
st.subheader("本棚一覧")

df = to_df(data)

if df.empty:
    st.write("まだ本棚が空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="タイトル・著者・学び")

    with col_b:
        genre_filter = st.selectbox("ジャンル", ["すべて"] + GENRES)

    with col_c:
        status_filter = st.selectbox("状態", ["すべて"] + STATUS)

    fav_only = st.checkbox("⭐ お気に入りだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["author"].fillna("").str.contains(q, case=False, na=False)
            | view["learning"].fillna("").str.contains(q, case=False, na=False)
        ]

    if genre_filter != "すべて":
        view = view[view["genre"] == genre_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["title", "author", "genre", "status", "rating", "favorite", "next_action"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う本がないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{row['title']} / {row['status']} / {row['rating']}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "本を選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        book = find_book(data, selected_id)

        if book:
            st.markdown(f"## {book['title']}")
            st.write(f"著者：{book.get('author', '')}")
            st.write(f"ジャンル：{book['genre']}")
            st.write(f"状態：{book['status']}")
            st.write(f"評価：{book.get('rating', '未評価')}")

            st.markdown("### ざっくり内容")
            st.write(book.get("summary", ""))

            st.markdown("### 学んだこと")
            st.info(book.get("learning", ""))

            st.markdown("### 次の行動")
            st.success(book.get("next_action", ""))

            if book.get("memo"):
                st.markdown("### メモ")
                st.write(book.get("memo", ""))

            col1, col2, col3 = st.columns(3)

            with col1:
                new_status = st.selectbox(
                    "状態変更",
                    STATUS,
                    index=STATUS.index(book.get("status", "読みたい")),
                    key=f"status_{book['id']}"
                )

            with col2:
                new_rating = st.selectbox(
                    "評価変更",
                    RATINGS,
                    index=RATINGS.index(book.get("rating", "未評価")),
                    key=f"rating_{book['id']}"
                )

            with col3:
                new_fav = st.checkbox(
                    "⭐ お気に入り",
                    value=bool(book.get("favorite", False)),
                    key=f"fav_{book['id']}"
                )

            new_next_action = st.text_input(
                "次の行動を更新",
                value=book.get("next_action", ""),
                key=f"next_{book['id']}"
            )

            if st.button("📝 更新する"):
                book["status"] = new_status
                book["rating"] = new_rating
                book["favorite"] = new_fav
                book["next_action"] = new_next_action.strip()
                book["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ この本を削除", type="secondary"):
                data["books"] = [x for x in data["books"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day157_bookshelf_manager.csv",
        mime="text/csv"
    )
