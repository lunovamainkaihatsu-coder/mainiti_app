import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day118：読書記録ノート"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day118_reading_log.json")

GENRES = [
    "自己啓発",
    "お金・ビジネス",
    "AI・テクノロジー",
    "心理・脳科学",
    "健康",
    "スピリチュアル",
    "小説",
    "その他",
]

STATUS = ["未読", "読書中", "読了", "積読", "再読したい"]


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


def to_df(data):
    rows = []
    for b in data["books"]:
        rows.append({
            "id": b.get("id"),
            "created_at": b.get("created_at"),
            "updated_at": b.get("updated_at"),
            "title": b.get("title"),
            "author": b.get("author"),
            "genre": b.get("genre"),
            "status": b.get("status"),
            "fun_score": b.get("fun_score"),
            "review_score": b.get("review_score"),
            "favorite": bool(b.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("updated_at", ascending=False)
    return df


def find_book(data, book_id):
    for b in data["books"]:
        if b["id"] == book_id:
            return b
    return None


st.set_page_config(page_title=APP_TITLE, page_icon="📚", layout="wide")
st.title("📚 Day118：読書記録ノート")
st.caption("読んだ本を、学び・実践・見返し用に保存するアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day118_reading_log.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🔎 表示フィルター")
    keyword = st.text_input("検索", placeholder="タイトル・著者で検索")
    genre_filter = st.selectbox("ジャンル", ["すべて"] + GENRES)
    status_filter = st.selectbox("読了状況", ["すべて"] + STATUS)
    fav_only = st.checkbox("⭐ お気に入りだけ")

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("本を記録する")

    with st.form("book_form", clear_on_submit=False):
        title = st.text_input("本のタイトル")
        author = st.text_input("著者")
        genre = st.selectbox("ジャンル", GENRES)
        status = st.selectbox("読了状況", STATUS, index=2)

        summary = st.text_area(
            "内容まとめ",
            height=140,
            placeholder="この本は何について書かれていた？"
        )

        learnings = st.text_area(
            "学び・気づき",
            height=120,
            placeholder="印象に残った考え方、言葉、視点など"
        )

        actions = st.text_area(
            "実践したいこと",
            height=100,
            placeholder="この本を読んで、何をやってみたい？"
        )

        quote = st.text_area(
            "印象に残った一文・メモ",
            height=80,
            placeholder="短い引用や、自分用メモ"
        )

        fun_score = st.slider("おもしろさ", 1, 5, 3)
        review_score = st.slider("見返す可能性", 1, 5, 3)
        favorite = st.checkbox("⭐ お気に入りにする")

        submitted = st.form_submit_button("📚 保存する", type="primary")

        if submitted:
            if not title.strip():
                st.warning("タイトルだけは入れてね。")
            else:
                book = {
                    "id": f"book_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "updated_at": now_str(),
                    "title": title.strip(),
                    "author": author.strip(),
                    "genre": genre,
                    "status": status,
                    "summary": summary.strip(),
                    "learnings": learnings.strip(),
                    "actions": actions.strip(),
                    "quote": quote.strip(),
                    "fun_score": fun_score,
                    "review_score": review_score,
                    "favorite": favorite,
                }
                data["books"].append(book)
                save_data(data)
                st.success("読書記録を保存したよ。知識が資産になったね。")
                st.rerun()

with right:
    st.subheader("読書ログ")

    df = to_df(data)

    if df.empty:
        st.info("まだ読書記録がないよ。左から1冊登録してみてね。")
    else:
        view = df.copy()

        if keyword.strip():
            q = keyword.strip().lower()
            view = view[
                view["title"].fillna("").str.lower().str.contains(q) |
                view["author"].fillna("").str.lower().str.contains(q)
            ]

        if genre_filter != "すべて":
            view = view[view["genre"] == genre_filter]

        if status_filter != "すべて":
            view = view[view["status"] == status_filter]

        if fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(
            view[["title", "author", "genre", "status", "fun_score", "review_score", "favorite"]],
            use_container_width=True,
            height=360
        )

        st.divider()
        st.subheader("詳細を見る")

        if view.empty:
            st.write("条件に合う本がないよ。")
        else:
            options = view["id"].tolist()
            labels = {
                row["id"]: f"{row['title']} / {row.get('author', '')}"
                for _, row in view.iterrows()
            }

            selected_id = st.selectbox(
                "本を選ぶ",
                options=options,
                format_func=lambda x: labels.get(x, x)
            )

            book = find_book(data, selected_id)

            if book:
                st.markdown(f"## {book['title']}")
                st.write(f"著者：{book.get('author', '')}")
                st.write(f"ジャンル：{book.get('genre', '')} / 状況：{book.get('status', '')}")
                st.write(f"おもしろさ：{book.get('fun_score')} / 見返す可能性：{book.get('review_score')}")
                st.write(f"お気に入り：{'⭐' if book.get('favorite') else '—'}")

                st.markdown("### 内容まとめ")
                st.write(book.get("summary", ""))

                st.markdown("### 学び・気づき")
                st.write(book.get("learnings", ""))

                st.markdown("### 実践したいこと")
                st.success(book.get("actions", ""))

                st.markdown("### 印象に残った一文・メモ")
                st.info(book.get("quote", ""))

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("⭐ お気に入り切替"):
                        book["favorite"] = not bool(book.get("favorite", False))
                        book["updated_at"] = now_str()
                        save_data(data)
                        st.rerun()

                with col_b:
                    if st.button("🗑️ この記録を削除", type="secondary"):
                        data["books"] = [b for b in data["books"] if b["id"] != selected_id]
                        save_data(data)
                        st.warning("削除したよ。")
                        st.rerun()
