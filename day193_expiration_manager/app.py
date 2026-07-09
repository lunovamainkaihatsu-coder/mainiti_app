import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day193：賞味期限管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day193_expiration_manager.json")

CATEGORIES = [
    "野菜",
    "肉",
    "魚",
    "卵・乳製品",
    "飲料",
    "主食",
    "調味料",
    "冷凍食品",
    "お菓子",
    "その他",
]

UNITS = [
    "個",
    "本",
    "袋",
    "箱",
    "パック",
    "g",
    "kg",
    "ml",
    "L",
    "その他",
]

LOCATIONS = [
    "冷蔵庫",
    "冷凍庫",
    "常温",
    "キッチン",
    "食品棚",
    "その他",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"foods": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "foods" not in data:
        data["foods"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def days_left(expiration_date):
    try:
        d = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        return (d - date.today()).days
    except:
        return None


def expiration_status(days):
    if days is None:
        return "不明"

    if days < 0:
        return "⚫ 期限切れ"

    if days == 0:
        return "🔴 今日まで"

    if days <= 3:
        return "🟠 3日以内"

    if days <= 7:
        return "🟡 7日以内"

    return "🟢 余裕あり"


def to_df(data):
    rows = []

    for x in data["foods"]:
        days = days_left(x.get("expiration_date", ""))

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "category": x["category"],
            "quantity": float(x.get("quantity", 1)),
            "unit": x["unit"],
            "location": x["location"],
            "expiration_date": x["expiration_date"],
            "days_left": days if days is not None else "",
            "status": expiration_status(days),
            "memo": x.get("memo", ""),
            "favorite": bool(x.get("favorite", False)),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        status_order = {
            "⚫ 期限切れ": 0,
            "🔴 今日まで": 1,
            "🟠 3日以内": 2,
            "🟡 7日以内": 3,
            "🟢 余裕あり": 4,
            "不明": 5,
        }

        df["status_order"] = df["status"].map(status_order)
        df = df.sort_values(
            ["status_order", "expiration_date", "created_at"],
            ascending=[True, True, False]
        )

    return df


def find_food(data, food_id):
    for x in data["foods"]:
        if x["id"] == food_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🥛",
    layout="wide"
)

st.title("🥛 Day193：賞味期限管理アプリ")
st.caption("食品の賞味期限・消費期限を登録して、期限切れや期限間近を見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("食品を登録")

    name = st.text_input(
        "食品名",
        placeholder="例：牛乳 / 卵 / 納豆 / パン"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    c1, c2 = st.columns(2)

    with c1:
        quantity = st.number_input(
            "数量",
            min_value=0.0,
            value=1.0,
            step=0.5
        )

    with c2:
        unit = st.selectbox(
            "単位",
            UNITS
        )

    location = st.selectbox(
        "保管場所",
        LOCATIONS
    )

    expiration_date = st.date_input(
        "賞味期限・消費期限",
        value=date.today()
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：早めに使う / 冷凍予定 / セールで購入"
    )

    favorite = st.checkbox("⭐ 優先して使いたい")

    left_days = days_left(expiration_date.isoformat())
    st.info(f"期限状態：{expiration_status(left_days)}")

    if st.button("🥛 食品を登録", type="primary"):
        if not name.strip():
            st.warning("食品名を入れてね。")
        else:
            item = {
                "id": f"food_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "name": name.strip(),
                "category": category,
                "quantity": float(quantity),
                "unit": unit,
                "location": location,
                "expiration_date": expiration_date.isoformat(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["foods"].append(item)
            save_data(data)

            st.success("食品を登録したよ。")
            st.rerun()

with right:
    st.subheader("期限ステータス")

    df = to_df(data)

    if df.empty:
        st.info("まだ食品が登録されていないよ。")
    else:
        expired = len(df[df["status"] == "⚫ 期限切れ"])
        today_count = len(df[df["status"] == "🔴 今日まで"])
        three_days = len(df[df["status"] == "🟠 3日以内"])
        seven_days = len(df[df["status"] == "🟡 7日以内"])

        c1, c2 = st.columns(2)

        with c1:
            st.metric("登録食品", len(df))
            st.metric("期限切れ", expired)

        with c2:
            st.metric("今日まで", today_count)
            st.metric("3日以内", three_days)

        st.metric("7日以内", seven_days)

        st.divider()

        st.subheader("急いで使いたい食品")

        urgent = df[df["status"].isin(["⚫ 期限切れ", "🔴 今日まで", "🟠 3日以内"])]

        if urgent.empty:
            st.success("急いで使う食品は少なそう。いい感じ！")
        else:
            st.dataframe(
                urgent[[
                    "name",
                    "category",
                    "quantity",
                    "unit",
                    "location",
                    "expiration_date",
                    "days_left",
                    "status",
                    "memo",
                ]],
                use_container_width=True,
                height=240
            )

st.divider()
st.subheader("食品一覧")

df = to_df(data)

if df.empty:
    st.write("まだ一覧が空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="食品名・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        location_filter = st.selectbox(
            "保管場所で絞る",
            ["すべて"] + LOCATIONS
        )

    status_filter = st.selectbox(
        "期限状態で絞る",
        ["すべて", "⚫ 期限切れ", "🔴 今日まで", "🟠 3日以内", "🟡 7日以内", "🟢 余裕あり"]
    )

    fav_only = st.checkbox("⭐ 優先して使いたいものだけ")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["name"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if location_filter != "すべて":
        view = view[view["location"] == location_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[[
            "name",
            "category",
            "quantity",
            "unit",
            "location",
            "expiration_date",
            "days_left",
            "status",
            "favorite",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う食品がないよ。")
    else:
        selected_id = st.selectbox(
            "食品を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_food(data, x)['name']} / {find_food(data, x)['expiration_date']}"
        )

        food = find_food(data, selected_id)

        if food:
            left_days = days_left(food.get("expiration_date", ""))

            st.markdown(f"## {food['name']}")
            st.write(f"カテゴリ：{food['category']}")
            st.write(f"数量：{food['quantity']} {food['unit']}")
            st.write(f"保管場所：{food['location']}")
            st.write(f"期限：{food['expiration_date']}")
            st.info(expiration_status(left_days))

            if food.get("memo"):
                st.write(food["memo"])

            c1, c2, c3 = st.columns(3)

            with c1:
                new_quantity = st.number_input(
                    "数量更新",
                    min_value=0.0,
                    value=float(food.get("quantity", 1)),
                    step=0.5,
                    key=f"qty_{food['id']}"
                )

            with c2:
                new_location = st.selectbox(
                    "保管場所更新",
                    LOCATIONS,
                    index=LOCATIONS.index(food.get("location", "冷蔵庫")),
                    key=f"location_{food['id']}"
                )

            with c3:
                new_favorite = st.checkbox(
                    "⭐ 優先して使う",
                    value=bool(food.get("favorite", False)),
                    key=f"fav_{food['id']}"
                )

            if st.button("📝 更新する"):
                food["quantity"] = float(new_quantity)
                food["location"] = new_location
                food["favorite"] = new_favorite
                food["updated_at"] = now_str()

                save_data(data)

                st.success("食品を更新したよ。")
                st.rerun()

            if st.button("✅ 使い切ったので削除", type="secondary"):
                data["foods"] = [
                    x for x in data["foods"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.success("食品を削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day193_expiration_manager.csv",
        mime="text/csv"
    )
