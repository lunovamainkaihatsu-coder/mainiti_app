import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day135：食事管理ログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day135_meal_log.json")

MEAL_TYPES = ["朝食", "昼食", "夕食", "間食"]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"meals": []}, f, ensure_ascii=False, indent=2)


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
    for x in data["meals"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "meal_type": x["meal_type"],
            "foods": x["foods"],
            "protein_note": x.get("protein_note", ""),
            "feeling": x.get("feeling", ""),
            "memo": x.get("memo", ""),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🍽️", layout="wide")
st.title("🍽️ Day135：食事管理ログ")
st.caption("朝・昼・晩・間食を記録して、食生活を見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("食事を記録する")

    meal_date = st.date_input("日付", value=date.today())
    meal_type = st.radio("区分", MEAL_TYPES, horizontal=True)

    foods = st.text_area(
        "食べたもの",
        height=150,
        placeholder="例：亜麻仁油入りヨーグルト、バナナ、プロテイン"
    )

    protein_note = st.text_input(
        "たんぱく質メモ（任意）",
        placeholder="例：プロテインあり / 鶏むね / 卵2個"
    )

    feeling = st.selectbox(
        "食後の感じ",
        ["未選択", "軽い", "普通", "満足", "食べすぎ", "胃もたれ", "眠い"]
    )

    memo = st.text_area(
        "メモ（任意）",
        height=80,
        placeholder="例：朝は調子よかった / 夜に少し食べすぎた"
    )

    favorite = st.checkbox("⭐ 良かった食事として保存")

    if st.button("🍽️ 食事を保存", type="primary"):
        if not foods.strip():
            st.warning("食べたものを少しだけでも書いてね。")
        else:
            item = {
                "id": f"meal_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": meal_date.isoformat(),
                "meal_type": meal_type,
                "foods": foods.strip(),
                "protein_note": protein_note.strip(),
                "feeling": feeling,
                "memo": memo.strip(),
                "favorite": favorite,
            }
            data["meals"].append(item)
            save_data(data)
            st.success("食事を保存したよ。")
            st.rerun()

with right:
    st.subheader("今日の食事")

    today_meals = [
        x for x in data["meals"]
        if x.get("date") == today_str()
    ]

    if not today_meals:
        st.info("今日の記録はまだないよ。")
    else:
        for meal_type in MEAL_TYPES:
            meals = [x for x in today_meals if x["meal_type"] == meal_type]
            st.markdown(f"### {meal_type}")
            if meals:
                for m in sorted(meals, key=lambda x: x["created_at"]):
                    st.write(m["foods"])
                    if m.get("protein_note"):
                        st.caption(f"たんぱく質：{m['protein_note']}")
                    if m.get("feeling") and m["feeling"] != "未選択":
                        st.caption(f"食後：{m['feeling']}")
            else:
                st.caption("未記録")

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ食事ログがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        filter_date = st.date_input("日付で絞る", value=date.today())

    with col_b:
        filter_meal = st.selectbox("区分で絞る", ["すべて"] + MEAL_TYPES)

    with col_c:
        fav_only = st.checkbox("⭐ 良かった食事だけ")

    view = df.copy()

    if filter_date:
        view = view[view["date"] == filter_date.isoformat()]

    if filter_meal != "すべて":
        view = view[view["meal_type"] == filter_meal]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "meal_type", "foods", "protein_note", "feeling", "favorite"]],
        use_container_width=True,
        height=320
    )

    if not view.empty:
        with st.expander("詳細・編集"):
            selected = st.selectbox("記録を選ぶ", view["id"].tolist())
            item = next((x for x in data["meals"] if x["id"] == selected), None)

            if item:
                st.markdown(f"### {item['date']} / {item['meal_type']}")
                st.write(item["foods"])

                if item.get("protein_note"):
                    st.write(f"たんぱく質メモ：{item['protein_note']}")
                if item.get("feeling"):
                    st.write(f"食後の感じ：{item['feeling']}")
                if item.get("memo"):
                    st.write(f"メモ：{item['memo']}")

                fav = st.checkbox("⭐ 良かった食事", value=bool(item.get("favorite", False)))
                if fav != bool(item.get("favorite", False)):
                    item["favorite"] = fav
                    save_data(data)
                    st.rerun()

                if st.button("🗑️ この記録を削除", type="secondary"):
                    data["meals"] = [x for x in data["meals"] if x["id"] != selected]
                    save_data(data)
                    st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day135_meal_log.csv",
        mime="text/csv"
    )
