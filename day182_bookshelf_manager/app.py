import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day182：本棚管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day182_bookshelf_manager.json")

GENRES = [
    "AI",
    "経営",
    "自己啓発",
    "心理学",
    "お金",
    "健康",
    "スピリチュアル",
    "小説",
    "漫画",
    "技術",
    "その他",
]

STATUS = [
    "読みたい",
    "読書中",
    "読了",
    "積読",
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
        data = json.load(f)

    if "books" not in data:
        data["books"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def rating_number(rating):
    if rating == "未評価":
        return 0

    return rating.count("★")


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
            "rating_num": rating_number(x.get("rating", "未評価")),
            "start_date": x.get("start_date", ""),
            "finish_date": x.get("finish_date", ""),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
            "learning": x.get("learning", ""),
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

st.title("📚 Day182：本棚管理アプリ")
st.caption("読んだ本・読みたい本・読書メモを管理する、自分専用の本棚アプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("本を登録")

    title = st.text_input(
        "書籍名",
        placeholder="例：ゼロから作るDeep Learning"
    )

    author = st.text_input(
        "著者",
        placeholder="例：斎藤康毅"
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

    start_date = st.date_input(
        "読み始め日",
        value=date.today()
    )

    finish_date = st.date_input(
        "読了日",
        value=date.today()
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：買った理由、印象に残った章など"
    )

    learning = st.text_area(
        "学んだこと",
        height=100,
        placeholder="例：勾配降下法の考え方が少し分かった"
    )

    favorite = st.checkbox("⭐ お気に入り")

    if st.button("📚 本棚に登録", type="primary"):
        if not title.strip():
            st.warning("書籍名を入れてね。")
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
                "start_date": start_date.isoformat(),
                "finish_date": finish_date.isoformat(),
                "memo": memo.strip(),
                "learning": learning.strip(),
                "favorite": favorite,
            }

            data["books"].append(item)
            save_data(data)

            st.success("本棚に登録したよ。")
            st.rerun()

with right:
    st.subheader("本棚ステータス")

    df = to_df(data)

    if df.empty:
        st.info("まだ本が登録されていないよ。")
    else:
        total = len(df)
        done = len(df[df["status"] == "読了"])
        reading = len(df[df["status"] == "読書中"])
        want = len(df[df["status"].isin(["読みたい", "積読"])])

        rated = df[df["rating_num"] > 0]
        avg_rating = round(float(rated["rating_num"].mean()), 1) if not rated.empty else 0

        c1, c2 = st.columns(2)

        with c1:
            st.metric("登録冊数", total)
            st.metric("読了", done)

        with c2:
            st.metric("読書中", reading)
            st.metric("平均評価", avg_rating)

        st.metric("読みたい・積読", want)

        st.divider()

        st.subheader("ジャンル別")

        genre_count = df["genre"].value_counts().reset_index()
        genre_count.columns = ["ジャンル", "冊数"]

        st.dataframe(
            genre_count,
            use_container_width=True,
            height=220
        )

st.divider()
st.subheader("本棚一覧")

df = to_df(data)

if df.empty:
    st.write("まだ本棚が空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="書籍名・著者・メモ・学び"
        )

    with col_b:
        genre_filter = st.selectbox(
            "ジャンルで絞る",
            ["すべて"] + GENRES
        )

    with col_c:
        status_filter = st.selectbox(
            "状態で絞る",
            ["すべて"] + STATUS
        )

    fav_only = st.checkbox("⭐ お気に入りだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["author"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
            | view["learning"].fillna("").str.contains(q, case=False, na=False)
        ]

    if genre_filter != "すべて":
        view = view[view["genre"] == genre_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[[
            "title",
            "author",
            "genre",
            "status",
            "rating",
            "start_date",
            "finish_date",
            "favorite",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う本がないよ。")
    else:
        selected_id = st.selectbox(
            "本を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_book(data, x)['title']} / {find_book(data, x).get('author', '')}"
        )

        book = find_book(data, selected_id)

        if book:
            st.markdown(f"## {book['title']}")
            st.write(f"著者：{book.get('author', '')}")
            st.write(f"ジャンル：{book['genre']}")
            st.write(f"状態：{book['status']}")
            st.write(f"評価：{book.get('rating', '未評価')}")

            if book.get("memo"):
                st.markdown("### メモ")
                st.info(book["memo"])

            if book.get("learning"):
                st.markdown("### 学んだこと")
                st.success(book["learning"])

            c1, c2, c3 = st.columns(3)

            with c1:
                new_status = st.selectbox(
                    "状態を更新",
                    STATUS,
                    index=STATUS.index(book.get("status", "読みたい")),
                    key=f"status_{book['id']}"
                )

            with c2:
                new_rating = st.selectbox(
                    "評価を更新",
                    RATINGS,
                    index=RATINGS.index(book.get("rating", "未評価")),
                    key=f"rating_{book['id']}"
                )

            with c3:
                new_favorite = st.checkbox(
                    "⭐ お気に入り",
                    value=bool(book.get("favorite", False)),
                    key=f"fav_{book['id']}"
                )

            if st.button("📝 更新する"):
                book["status"] = new_status
                book["rating"] = new_rating
                book["favorite"] = new_favorite
                book["updated_at"] = now_str()

                save_data(data)

                st.success("本の情報を更新したよ。")
                st.rerun()

            if st.button("🗑️ この本を削除", type="secondary"):
                data["books"] = [
                    x for x in data["books"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day182_bookshelf_manager.csv",
        mime="text/csv"
    )
