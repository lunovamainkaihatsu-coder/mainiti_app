import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day160：願い事保管庫"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day160_wish_vault.json")

CATEGORIES = [
    "お金",
    "仕事",
    "AI",
    "健康",
    "家族",
    "恋愛",
    "趣味",
    "学習",
    "その他",
]

STATUS = [
    "願った",
    "行動中",
    "もうすぐ",
    "叶った",
]

ENERGY = [
    "🌱 静かな願い",
    "✨ 叶えたい",
    "🔥 本気",
    "🌕 絶対叶える",
]

LUNA_COMMENTS = {
    "願った": "願いを書けた時点で、もう未来に向けた一歩だよ。",
    "行動中": "願いに向かって動いてるご主人、すごくいい流れだよ。",
    "もうすぐ": "あと少しの気配があるね。焦らず、でも止まらずいこう。",
    "叶った": "ご主人、叶ったね。本当におめでとう。ちゃんと形になったよ。",
}


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"wishes": []}, f, ensure_ascii=False, indent=2)


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

    for x in data["wishes"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "wish": x["wish"],
            "category": x["category"],
            "status": x["status"],
            "energy": x.get("energy", ""),
            "first_step": x.get("first_step", ""),
            "reason": x.get("reason", ""),
            "favorite": bool(x.get("favorite", False)),
            "achieved_date": x.get("achieved_date", ""),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_wish(data, wish_id):
    for x in data["wishes"]:
        if x["id"] == wish_id:
            return x
    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌠",
    layout="wide"
)

st.title("🌠 Day160：願い事保管庫")
st.caption("願いを書いて、行動して、叶うまで見守るアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("願いを登録")

    wish = st.text_input(
        "願い",
        placeholder="例：LUNAPOCKETを完成させる"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    energy = st.radio(
        "願いの強さ",
        ENERGY,
        horizontal=True
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    reason = st.text_area(
        "なぜ叶えたい？",
        height=100,
        placeholder="例：AIと人類が共存する未来を作りたいから"
    )

    first_step = st.text_input(
        "最初の一歩",
        placeholder="例：今日5分だけ開発する"
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="叶った時のイメージ、期限、思いついたことなど"
    )

    favorite = st.checkbox("⭐ 大事な願い")

    if st.button("🌠 願いを保存", type="primary"):
        if not wish.strip():
            st.warning("願いを入力してね。")
        else:
            achieved_date = today_str() if status == "叶った" else ""

            item = {
                "id": f"wish_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "wish": wish.strip(),
                "category": category,
                "energy": energy,
                "status": status,
                "reason": reason.strip(),
                "first_step": first_step.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
                "achieved_date": achieved_date,
            }

            data["wishes"].append(item)
            save_data(data)

            st.success("願いを保存したよ。")
            st.rerun()

with right:
    st.subheader("願いの状況")

    df = to_df(data)

    total = len(df) if not df.empty else 0
    active = len(df[df["status"] == "行動中"]) if not df.empty else 0
    near = len(df[df["status"] == "もうすぐ"]) if not df.empty else 0
    achieved = len(df[df["status"] == "叶った"]) if not df.empty else 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("願いの数", total)
        st.metric("行動中", active)

    with col2:
        st.metric("もうすぐ", near)
        st.metric("叶った", achieved)

    if total > 0:
        rate = int(achieved / total * 100)
        st.progress(rate / 100)
        st.info(f"成就率：{rate}%")

    st.divider()

    if not df.empty:
        st.subheader("カテゴリ別")
        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "数"]
        st.dataframe(cat_count, use_container_width=True, height=220)
    else:
        st.info("まだ願いが登録されていないよ。")

st.divider()
st.subheader("願い一覧")

df = to_df(data)

if df.empty:
    st.write("まだ願いがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="願い・理由・一歩・メモ")

    with col_b:
        category_filter = st.selectbox("カテゴリ", ["すべて"] + CATEGORIES)

    with col_c:
        status_filter = st.selectbox("状態", ["すべて"] + STATUS)

    fav_only = st.checkbox("⭐ 大事な願いだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["wish"].fillna("").str.contains(q, case=False, na=False)
            | view["reason"].fillna("").str.contains(q, case=False, na=False)
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
        view[["date", "wish", "category", "status", "energy", "first_step", "favorite"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う願いがないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{row['wish']} / {row['category']} / {row['status']}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "願いを選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        item = find_wish(data, selected_id)

        if item:
            st.markdown(f"## 🌠 {item['wish']}")
            st.write(f"カテゴリ：{item['category']}")
            st.write(f"状態：{item['status']}")
            st.write(f"願いの強さ：{item.get('energy', '')}")

            st.markdown("### なぜ叶えたい？")
            st.info(item.get("reason", ""))

            st.markdown("### 最初の一歩")
            st.success(item.get("first_step", ""))

            if item.get("memo"):
                st.markdown("### メモ")
                st.write(item.get("memo", ""))

            if item.get("achieved_date"):
                st.success(f"叶った日：{item['achieved_date']}")

            st.markdown("### ルナのひとこと")
            st.info(LUNA_COMMENTS.get(item["status"], "願いは、書いた瞬間から動き出すよ。"))

            col1, col2, col3 = st.columns(3)

            with col1:
                new_status = st.selectbox(
                    "状態変更",
                    STATUS,
                    index=STATUS.index(item.get("status", "願った")),
                    key=f"status_{item['id']}"
                )

            with col2:
                new_energy = st.selectbox(
                    "願いの強さ変更",
                    ENERGY,
                    index=ENERGY.index(item.get("energy", "✨ 叶えたい")),
                    key=f"energy_{item['id']}"
                )

            with col3:
                new_fav = st.checkbox(
                    "⭐ 大事",
                    value=bool(item.get("favorite", False)),
                    key=f"fav_{item['id']}"
                )

            new_first_step = st.text_input(
                "次の一歩を更新",
                value=item.get("first_step", ""),
                key=f"step_{item['id']}"
            )

            if st.button("📝 更新する"):
                old_status = item.get("status", "")

                item["status"] = new_status
                item["energy"] = new_energy
                item["favorite"] = new_fav
                item["first_step"] = new_first_step.strip()
                item["updated_at"] = now_str()

                if new_status == "叶った" and old_status != "叶った":
                    item["achieved_date"] = today_str()

                if new_status != "叶った":
                    item["achieved_date"] = ""

                save_data(data)
                st.success("願いを更新したよ。")
                st.rerun()

            if st.button("🗑️ この願いを削除", type="secondary"):
                data["wishes"] = [x for x in data["wishes"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day160_wish_vault.csv",
        mime="text/csv"
    )
