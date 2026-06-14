import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day169：冷蔵庫メモ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day169_fridge_memo.json")

CATEGORIES = [
    "野菜",
    "肉",
    "魚",
    "卵・乳製品",
    "飲み物",
    "主食",
    "冷凍食品",
    "調味料",
    "その他",
]

UNITS = [
    "個",
    "本",
    "袋",
    "パック",
    "g",
    "kg",
    "ml",
    "L",
    "枚",
    "その他",
]

STORAGE = [
    "冷蔵",
    "冷凍",
    "常温",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"foods": [], "shopping": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "foods" not in data:
        data["foods"] = []

    if "shopping" not in data:
        data["shopping"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def days_until(expire_date):
    try:
        d = datetime.strptime(expire_date, "%Y-%m-%d").date()
        return (d - date.today()).days
    except:
        return None


def expire_label(days):
    if days is None:
        return "期限なし"

    if days < 0:
        return "⚠️ 期限切れ"

    if days <= 3:
        return "🔴 急げ"

    if days <= 7:
        return "🟡 注意"

    return "🟢 余裕"


def to_food_df(data):
    rows = []

    for x in data["foods"]:
        days = days_until(x.get("expire_date", ""))

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "category": x["category"],
            "storage": x["storage"],
            "quantity": x["quantity"],
            "unit": x["unit"],
            "expire_date": x.get("expire_date", ""),
            "days_left": days if days is not None else "",
            "status": expire_label(days),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(["expire_date", "created_at"], ascending=[True, False])

    return df


def to_shopping_df(data):
    rows = []

    for x in data["shopping"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "category": x.get("category", "その他"),
            "done": bool(x.get("done", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_food(data, food_id):
    for x in data["foods"]:
        if x["id"] == food_id:
            return x
    return None


def find_shopping(data, shopping_id):
    for x in data["shopping"]:
        if x["id"] == shopping_id:
            return x
    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🥬",
    layout="wide"
)

st.title("🥬 Day169：冷蔵庫メモ")
st.caption("冷蔵庫の食材・賞味期限・買い物リストを管理するアプリ。")

data = load_data()

tab1, tab2, tab3 = st.tabs(["🥬 食材管理", "🛒 買い物リスト", "📊 状況"])

with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("食材を登録")

        name = st.text_input(
            "食材名",
            placeholder="例：卵、牛乳、鶏むね肉"
        )

        category = st.selectbox(
            "カテゴリ",
            CATEGORIES
        )

        storage = st.selectbox(
            "保存場所",
            STORAGE
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

        expire_date = st.date_input(
            "賞味期限・消費期限",
            value=date.today()
        )

        memo = st.text_area(
            "メモ",
            height=90,
            placeholder="例：特売で購入 / 冷凍予定 / 早めに使う"
        )

        if st.button("🥬 食材を追加", type="primary"):
            if not name.strip():
                st.warning("食材名を入れてね。")
            else:
                item = {
                    "id": f"food_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "date": today_str(),
                    "name": name.strip(),
                    "category": category,
                    "storage": storage,
                    "quantity": float(quantity),
                    "unit": unit,
                    "expire_date": expire_date.isoformat(),
                    "memo": memo.strip(),
                }

                data["foods"].append(item)
                save_data(data)

                st.success("食材を追加したよ。")
                st.rerun()

    with right:
        st.subheader("冷蔵庫の中身")

        df = to_food_df(data)

        if df.empty:
            st.info("まだ食材が登録されていないよ。")
        else:
            col_a, col_b = st.columns(2)

            with col_a:
                category_filter = st.selectbox("カテゴリ絞り込み", ["すべて"] + CATEGORIES)

            with col_b:
                storage_filter = st.selectbox("保存場所絞り込み", ["すべて"] + STORAGE)

            view = df.copy()

            if category_filter != "すべて":
                view = view[view["category"] == category_filter]

            if storage_filter != "すべて":
                view = view[view["storage"] == storage_filter]

            st.dataframe(
                view[["name", "category", "storage", "quantity", "unit", "expire_date", "days_left", "status", "memo"]],
                use_container_width=True,
                height=320
            )

            if not view.empty:
                selected_id = st.selectbox(
                    "食材を選ぶ",
                    view["id"].tolist(),
                    format_func=lambda x: f"{find_food(data, x)['name']} / {find_food(data, x)['expire_date']}"
                )

                selected = find_food(data, selected_id)

                if selected:
                    st.markdown(f"### {selected['name']}")
                    st.write(f"数量：{selected['quantity']} {selected['unit']}")
                    st.write(f"期限：{selected['expire_date']}")

                    days = days_until(selected.get("expire_date", ""))
                    st.info(expire_label(days))

                    c1, c2 = st.columns(2)

                    with c1:
                        new_quantity = st.number_input(
                            "数量を更新",
                            min_value=0.0,
                            value=float(selected.get("quantity", 1)),
                            step=0.5,
                            key=f"qty_{selected['id']}"
                        )

                    with c2:
                        new_storage = st.selectbox(
                            "保存場所を更新",
                            STORAGE,
                            index=STORAGE.index(selected.get("storage", "冷蔵")),
                            key=f"storage_{selected['id']}"
                        )

                    if st.button("📝 食材を更新"):
                        selected["quantity"] = float(new_quantity)
                        selected["storage"] = new_storage
                        selected["updated_at"] = now_str()

                        save_data(data)
                        st.success("更新したよ。")
                        st.rerun()

                    if st.button("✅ 消費したので削除", type="secondary"):
                        data["foods"] = [x for x in data["foods"] if x["id"] != selected_id]
                        save_data(data)
                        st.success("食材を削除したよ。")
                        st.rerun()

with tab2:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("買い物リストに追加")

        buy_name = st.text_input(
            "買うもの",
            placeholder="例：牛乳、卵、納豆",
            key="buy_name"
        )

        buy_category = st.selectbox(
            "カテゴリ",
            CATEGORIES,
            key="buy_category"
        )

        buy_memo = st.text_area(
            "メモ",
            height=80,
            placeholder="例：安ければ買う / 2パック",
            key="buy_memo"
        )

        if st.button("🛒 買い物リストに追加", type="primary"):
            if not buy_name.strip():
                st.warning("買うものを入れてね。")
            else:
                item = {
                    "id": f"shop_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "date": today_str(),
                    "name": buy_name.strip(),
                    "category": buy_category,
                    "memo": buy_memo.strip(),
                    "done": False,
                }

                data["shopping"].append(item)
                save_data(data)

                st.success("買い物リストに追加したよ。")
                st.rerun()

    with right:
        st.subheader("買い物リスト")

        shop_df = to_shopping_df(data)

        if shop_df.empty:
            st.info("買い物リストは空だよ。")
        else:
            show_done = st.checkbox("購入済みも表示")

            view = shop_df.copy()

            if not show_done:
                view = view[view["done"] == False]

            st.dataframe(
                view[["name", "category", "done", "memo"]],
                use_container_width=True,
                height=280
            )

            if not view.empty:
                selected_shop_id = st.selectbox(
                    "買い物項目を選ぶ",
                    view["id"].tolist(),
                    format_func=lambda x: find_shopping(data, x)["name"]
                )

                selected_shop = find_shopping(data, selected_shop_id)

                if selected_shop:
                    bought = st.checkbox(
                        "✅ 買った",
                        value=bool(selected_shop.get("done", False)),
                        key=f"done_{selected_shop['id']}"
                    )

                    if st.button("📝 買い物項目を更新"):
                        selected_shop["done"] = bought
                        selected_shop["updated_at"] = now_str()

                        save_data(data)
                        st.success("更新したよ。")
                        st.rerun()

                    if st.button("🗑️ 買い物項目を削除", type="secondary"):
                        data["shopping"] = [
                            x for x in data["shopping"]
                            if x["id"] != selected_shop_id
                        ]
                        save_data(data)
                        st.warning("削除したよ。")
                        st.rerun()

with tab3:
    st.subheader("冷蔵庫ステータス")

    df = to_food_df(data)

    if df.empty:
        st.info("まだ食材データがないよ。")
    else:
        expired = df[df["status"] == "⚠️ 期限切れ"]
        urgent = df[df["status"] == "🔴 急げ"]
        caution = df[df["status"] == "🟡 注意"]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("食材数", len(df))
        c2.metric("期限切れ", len(expired))
        c3.metric("3日以内", len(urgent))
        c4.metric("7日以内", len(caution))

        st.divider()

        st.subheader("期限が近い食材")

        near = df[df["status"].isin(["⚠️ 期限切れ", "🔴 急げ", "🟡 注意"])]

        if near.empty:
            st.success("期限が近い食材は少なそう。いい感じ！")
        else:
            st.dataframe(
                near[["name", "category", "storage", "quantity", "unit", "expire_date", "days_left", "status"]],
                use_container_width=True,
                height=300
            )

        st.divider()

        st.subheader("カテゴリ別食材数")

        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "数"]

        st.dataframe(
            cat_count,
            use_container_width=True,
            height=220
        )

st.divider()

food_df = to_food_df(data)

if not food_df.empty:
    csv = food_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ 食材CSVダウンロード",
        data=csv,
        file_name="day169_fridge_memo_foods.csv",
        mime="text/csv"
    )
