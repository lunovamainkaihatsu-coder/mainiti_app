import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day156：AIアプリ図鑑"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day156_ai_app_book.json")

CATEGORIES = [
    "毎日アプリ",
    "Luna",
    "占い",
    "健康",
    "ゲーム",
    "AI",
    "仕事",
    "お金",
    "生活",
    "その他",
]

STATUS = [
    "アイデア",
    "開発中",
    "完成",
    "公開中",
    "停止中",
    "改善予定",
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
            json.dump({"apps": []}, f, ensure_ascii=False, indent=2)


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

    for x in data["apps"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "category": x["category"],
            "status": x["status"],
            "rating": x.get("rating", "未評価"),
            "url": x.get("url", ""),
            "github": x.get("github", ""),
            "favorite": bool(x.get("favorite", False)),
            "description": x.get("description", ""),
            "next_update": x.get("next_update", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_app(data, app_id):
    for x in data["apps"]:
        if x["id"] == app_id:
            return x
    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide"
)

st.title("📚 Day156：AIアプリ図鑑")
st.caption("作ったアプリ・公開したアプリ・改善予定のアプリを管理する図鑑。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("アプリを登録")

    name = st.text_input(
        "アプリ名",
        placeholder="例：Day148 ありがとうログ"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    status = st.selectbox(
        "状態",
        STATUS,
        index=2
    )

    rating = st.selectbox(
        "自己評価",
        RATINGS
    )

    url = st.text_input(
        "公開URL",
        placeholder="https://..."
    )

    github = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/..."
    )

    description = st.text_area(
        "説明",
        height=130,
        placeholder="このアプリで何ができる？誰のため？"
    )

    next_update = st.text_input(
        "次に改善したいこと",
        placeholder="例：グラフ追加 / UI改善 / AI連携"
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="制作メモ、気づき、公開日など"
    )

    favorite = st.checkbox("⭐ 重要アプリ")

    if st.button("📚 図鑑に登録", type="primary"):
        if not name.strip():
            st.warning("アプリ名だけは入れてね。")
        else:
            item = {
                "id": f"app_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "name": name.strip(),
                "category": category,
                "status": status,
                "rating": rating,
                "url": url.strip(),
                "github": github.strip(),
                "description": description.strip(),
                "next_update": next_update.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["apps"].append(item)
            save_data(data)

            st.success("アプリ図鑑に登録したよ。")
            st.rerun()

with right:
    st.subheader("図鑑ステータス")

    df = to_df(data)

    total = len(df) if not df.empty else 0
    public_count = len(df[df["status"] == "公開中"]) if not df.empty else 0
    complete_count = len(df[df["status"] == "完成"]) if not df.empty else 0
    fav_count = len(df[df["favorite"] == True]) if not df.empty else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("登録アプリ数", total)
        st.metric("公開中", public_count)

    with col2:
        st.metric("完成", complete_count)
        st.metric("重要アプリ", fav_count)

    if total >= 100:
        st.success("100アプリ突破！これはもう立派な作品群だよ。")
    elif total >= 50:
        st.info("50アプリ突破が見えてきたね。かなり育ってる。")
    elif total >= 10:
        st.info("アプリ図鑑が育ち始めてるよ。")
    else:
        st.info("ここから図鑑を育てていこう。")

    st.divider()

    st.subheader("カテゴリ別")
    if not df.empty:
        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "数"]
        st.dataframe(cat_count, use_container_width=True, height=220)
    else:
        st.write("まだ集計データがないよ。")

st.divider()
st.subheader("アプリ一覧")

df = to_df(data)

if df.empty:
    st.write("まだ登録アプリがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="アプリ名・説明・改善内容")

    with col_b:
        category_filter = st.selectbox("カテゴリ", ["すべて"] + CATEGORIES)

    with col_c:
        status_filter = st.selectbox("状態", ["すべて"] + STATUS)

    fav_only = st.checkbox("⭐ 重要アプリだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["name"].fillna("").str.contains(q, case=False, na=False)
            | view["description"].fillna("").str.contains(q, case=False, na=False)
            | view["next_update"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["name", "category", "status", "rating", "favorite", "next_update"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合うアプリがないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{row['name']} / {row['category']} / {row['status']}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "アプリを選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        app = find_app(data, selected_id)

        if app:
            st.markdown(f"## {app['name']}")
            st.write(f"カテゴリ：{app['category']}")
            st.write(f"状態：{app['status']}")
            st.write(f"自己評価：{app.get('rating', '未評価')}")

            if app.get("url"):
                st.markdown(f"[公開URLを開く]({app['url']})")

            if app.get("github"):
                st.markdown(f"[GitHubを開く]({app['github']})")

            st.markdown("### 説明")
            st.write(app.get("description", ""))

            st.markdown("### 次に改善したいこと")
            st.success(app.get("next_update", ""))

            if app.get("memo"):
                st.markdown("### メモ")
                st.info(app.get("memo", ""))

            col1, col2, col3 = st.columns(3)

            with col1:
                new_status = st.selectbox(
                    "状態変更",
                    STATUS,
                    index=STATUS.index(app.get("status", "完成")),
                    key=f"status_{app['id']}"
                )

            with col2:
                new_rating = st.selectbox(
                    "自己評価変更",
                    RATINGS,
                    index=RATINGS.index(app.get("rating", "未評価")),
                    key=f"rating_{app['id']}"
                )

            with col3:
                new_fav = st.checkbox(
                    "⭐ 重要",
                    value=bool(app.get("favorite", False)),
                    key=f"fav_{app['id']}"
                )

            new_next_update = st.text_input(
                "次の改善を更新",
                value=app.get("next_update", ""),
                key=f"next_{app['id']}"
            )

            if st.button("📝 更新する"):
                app["status"] = new_status
                app["rating"] = new_rating
                app["favorite"] = new_fav
                app["next_update"] = new_next_update.strip()
                app["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ このアプリを削除", type="secondary"):
                data["apps"] = [x for x in data["apps"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day156_ai_app_book.csv",
        mime="text/csv"
    )
