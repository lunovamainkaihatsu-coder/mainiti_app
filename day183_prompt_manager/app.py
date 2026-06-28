import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day183：AIプロンプト管理帳"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day183_prompt_manager.json")

CATEGORIES = [
    "ChatGPT",
    "画像生成",
    "Streamlit",
    "Android",
    "note",
    "X",
    "Unity",
    "Python",
    "その他",
]

PURPOSES = [
    "コード作成",
    "エラー修正",
    "文章作成",
    "要約",
    "画像生成",
    "アイデア出し",
    "分析",
    "その他",
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
            json.dump({"prompts": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "prompts" not in data:
        data["prompts"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def rating_num(rating):
    if rating == "未評価":
        return 0

    return rating.count("★")


def parse_tags(text):
    tags = []

    for part in text.replace("、", ",").split(","):
        tag = part.strip()
        if tag:
            tags.append(tag)

    return tags


def tags_to_text(tags):
    if isinstance(tags, list):
        return ", ".join(tags)

    return ""


def to_df(data):
    rows = []

    for x in data["prompts"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "category": x["category"],
            "purpose": x["purpose"],
            "tags": tags_to_text(x.get("tags", [])),
            "rating": x.get("rating", "未評価"),
            "rating_num": rating_num(x.get("rating", "未評価")),
            "favorite": bool(x.get("favorite", False)),
            "prompt": x.get("prompt", ""),
            "memo": x.get("memo", ""),
            "use_count": int(x.get("use_count", 0)),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(["favorite", "rating_num", "created_at"], ascending=[False, False, False])

    return df


def find_prompt(data, prompt_id):
    for x in data["prompts"]:
        if x["id"] == prompt_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Day183：AIプロンプト管理帳")
st.caption("ChatGPT・画像生成・開発・note用のプロンプトを保存して、検索・再利用するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("プロンプトを登録")

    title = st.text_input(
        "タイトル",
        placeholder="例：Streamlitアプリ修正依頼"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    purpose = st.selectbox(
        "用途",
        PURPOSES
    )

    tags_text = st.text_input(
        "タグ",
        placeholder="例：エラー, 修正, app.py"
    )

    rating = st.selectbox(
        "評価",
        RATINGS
    )

    prompt = st.text_area(
        "プロンプト本文",
        height=180,
        placeholder="例：このコードのエラー原因を探して、修正版を全文でください。"
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：Streamlitでエラーが出た時に使う"
    )

    favorite = st.checkbox("⭐ お気に入り")

    if st.button("🤖 保存する", type="primary"):
        if not title.strip():
            st.warning("タイトルを入れてね。")
        elif not prompt.strip():
            st.warning("プロンプト本文を入れてね。")
        else:
            item = {
                "id": f"prompt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "category": category,
                "purpose": purpose,
                "tags": parse_tags(tags_text),
                "rating": rating,
                "favorite": favorite,
                "prompt": prompt.strip(),
                "memo": memo.strip(),
                "use_count": 0,
            }

            data["prompts"].append(item)
            save_data(data)

            st.success("プロンプトを保存したよ。")
            st.rerun()

with right:
    st.subheader("プロンプト状況")

    df = to_df(data)

    if df.empty:
        st.info("まだプロンプトが登録されていないよ。")
    else:
        total = len(df)
        fav_count = len(df[df["favorite"] == True])
        used_total = int(df["use_count"].sum())
        rated = df[df["rating_num"] > 0]
        avg_rating = round(float(rated["rating_num"].mean()), 1) if not rated.empty else 0

        c1, c2 = st.columns(2)

        with c1:
            st.metric("登録数", total)
            st.metric("お気に入り", fav_count)

        with c2:
            st.metric("使用回数", used_total)
            st.metric("平均評価", avg_rating)

        st.divider()

        st.subheader("カテゴリ別")

        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "数"]

        st.dataframe(
            cat_count,
            use_container_width=True,
            height=220
        )

st.divider()
st.subheader("プロンプト一覧")

df = to_df(data)

if df.empty:
    st.write("まだ一覧に表示するプロンプトがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="タイトル・タグ・本文・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        purpose_filter = st.selectbox(
            "用途で絞る",
            ["すべて"] + PURPOSES
        )

    fav_only = st.checkbox("⭐ お気に入りだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["tags"].fillna("").str.contains(q, case=False, na=False)
            | view["prompt"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if purpose_filter != "すべて":
        view = view[view["purpose"] == purpose_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[[
            "title",
            "category",
            "purpose",
            "tags",
            "rating",
            "favorite",
            "use_count",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・コピー用表示")

    if view.empty:
        st.write("条件に合うプロンプトがないよ。")
    else:
        selected_id = st.selectbox(
            "プロンプトを選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_prompt(data, x)['title']} / {find_prompt(data, x)['category']}"
        )

        item = find_prompt(data, selected_id)

        if item:
            st.markdown(f"## {item['title']}")
            st.write(f"カテゴリ：{item['category']}")
            st.write(f"用途：{item['purpose']}")
            st.write(f"タグ：{tags_to_text(item.get('tags', []))}")
            st.write(f"評価：{item.get('rating', '未評価')}")
            st.write(f"使用回数：{item.get('use_count', 0)}")

            if item.get("memo"):
                st.info(item["memo"])

            st.markdown("### コピペ用プロンプト")
            st.code(item.get("prompt", ""), language="text")

            c1, c2, c3 = st.columns(3)

            with c1:
                new_rating = st.selectbox(
                    "評価を更新",
                    RATINGS,
                    index=RATINGS.index(item.get("rating", "未評価")),
                    key=f"rating_{item['id']}"
                )

            with c2:
                new_favorite = st.checkbox(
                    "⭐ お気に入り",
                    value=bool(item.get("favorite", False)),
                    key=f"fav_{item['id']}"
                )

            with c3:
                used = st.checkbox(
                    "今回使った",
                    value=False,
                    key=f"used_{item['id']}"
                )

            if st.button("📝 更新する"):
                item["rating"] = new_rating
                item["favorite"] = new_favorite

                if used:
                    item["use_count"] = int(item.get("use_count", 0)) + 1

                item["updated_at"] = now_str()

                save_data(data)

                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ このプロンプトを削除", type="secondary"):
                data["prompts"] = [
                    x for x in data["prompts"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day183_prompt_manager.csv",
        mime="text/csv"
    )
