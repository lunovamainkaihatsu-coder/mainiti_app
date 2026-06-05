import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day161：ビジョンボードメモ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day161_vision_board.json")

CATEGORIES = [
    "お金",
    "仕事",
    "AI",
    "健康",
    "家族",
    "趣味",
    "学習",
    "住まい",
    "その他",
]

STATUS = [
    "構想中",
    "準備中",
    "進行中",
    "実現",
]

MOODS = [
    "静かに望む",
    "ワクワクする",
    "本気で叶えたい",
    "絶対に実現する",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"visions": []}, f, ensure_ascii=False, indent=2)


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

    for x in data["visions"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "category": x["category"],
            "status": x["status"],
            "mood": x.get("mood", ""),
            "target": x.get("target", ""),
            "ideal": x.get("ideal", ""),
            "first_step": x.get("first_step", ""),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_vision(data, vision_id):
    for x in data["visions"]:
        if x["id"] == vision_id:
            return x
    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌌",
    layout="wide"
)

st.title("🌌 Day161：ビジョンボードメモ")
st.caption("理想の未来・叶えたいイメージ・今できる一歩を保存するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("ビジョンを登録")

    title = st.text_input(
        "タイトル",
        placeholder="例：LUNAPOCKET完成"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    mood = st.radio(
        "気持ち",
        MOODS,
        horizontal=True
    )

    target = st.text_input(
        "達成予定・時期",
        placeholder="例：2027年 / 半年以内 / いつか必ず"
    )

    ideal = st.text_area(
        "理想の未来",
        height=150,
        placeholder="例：ルナと自然に会話できる携帯AI端末を完成させる"
    )

    first_step = st.text_input(
        "今できる一歩",
        placeholder="例：今日10分だけ設計メモを書く"
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="関連する画像案、言葉、場所、人物、感情など"
    )

    favorite = st.checkbox("⭐ 大事なビジョン")

    if st.button("🌌 ビジョンを保存", type="primary"):
        if not title.strip():
            st.warning("タイトルだけは入れてね。")
        else:
            item = {
                "id": f"vision_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "category": category,
                "status": status,
                "mood": mood,
                "target": target.strip(),
                "ideal": ideal.strip(),
                "first_step": first_step.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["visions"].append(item)
            save_data(data)

            st.success("ビジョンを保存したよ。")
            st.rerun()

with right:
    st.subheader("ビジョンボード状況")

    df = to_df(data)

    total = len(df) if not df.empty else 0
    progress_count = len(df[df["status"] == "進行中"]) if not df.empty else 0
    realized_count = len(df[df["status"] == "実現"]) if not df.empty else 0
    fav_count = len(df[df["favorite"] == True]) if not df.empty else 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("ビジョン数", total)
        st.metric("進行中", progress_count)

    with col2:
        st.metric("実現", realized_count)
        st.metric("大事なビジョン", fav_count)

    if total > 0:
        rate = int(realized_count / total * 100)
        st.progress(rate / 100)
        st.info(f"実現率：{rate}%")

    st.divider()

    if not df.empty:
        st.subheader("カテゴリ別")
        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "数"]
        st.dataframe(cat_count, use_container_width=True, height=220)
    else:
        st.info("まだビジョンが登録されていないよ。")

st.divider()
st.subheader("ビジョン一覧")

df = to_df(data)

if df.empty:
    st.write("まだビジョンがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="タイトル・理想・一歩・メモ")

    with col_b:
        category_filter = st.selectbox("カテゴリ", ["すべて"] + CATEGORIES)

    with col_c:
        status_filter = st.selectbox("状態", ["すべて"] + STATUS)

    fav_only = st.checkbox("⭐ 大事なビジョンだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["ideal"].fillna("").str.contains(q, case=False, na=False)
            | view["first_step"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "title", "category", "status", "mood", "target", "first_step", "favorite"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合うビジョンがないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{row['title']} / {row['category']} / {row['status']}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "ビジョンを選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        item = find_vision(data, selected_id)

        if item:
            st.markdown(f"## 🌌 {item['title']}")
            st.write(f"カテゴリ：{item['category']}")
            st.write(f"状態：{item['status']}")
            st.write(f"気持ち：{item.get('mood', '')}")
            st.write(f"達成予定：{item.get('target', '')}")

            st.markdown("### 理想の未来")
            st.info(item.get("ideal", ""))

            st.markdown("### 今できる一歩")
            st.success(item.get("first_step", ""))

            if item.get("memo"):
                st.markdown("### メモ")
                st.write(item.get("memo", ""))

            col1, col2, col3 = st.columns(3)

            with col1:
                new_status = st.selectbox(
                    "状態変更",
                    STATUS,
                    index=STATUS.index(item.get("status", "構想中")),
                    key=f"status_{item['id']}"
                )

            with col2:
                new_mood = st.selectbox(
                    "気持ち変更",
                    MOODS,
                    index=MOODS.index(item.get("mood", "ワクワクする")),
                    key=f"mood_{item['id']}"
                )

            with col3:
                new_fav = st.checkbox(
                    "⭐ 大事",
                    value=bool(item.get("favorite", False)),
                    key=f"fav_{item['id']}"
                )

            new_first_step = st.text_input(
                "一歩を更新",
                value=item.get("first_step", ""),
                key=f"step_{item['id']}"
            )

            if st.button("📝 更新する"):
                item["status"] = new_status
                item["mood"] = new_mood
                item["favorite"] = new_fav
                item["first_step"] = new_first_step.strip()
                item["updated_at"] = now_str()

                save_data(data)
                st.success("ビジョンを更新したよ。")
                st.rerun()

            if st.button("🗑️ このビジョンを削除", type="secondary"):
                data["visions"] = [x for x in data["visions"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day161_vision_board.csv",
        mime="text/csv"
    )
