import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day191：在庫管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day191_inventory_manager.json")

CATEGORIES = [
    "食品",
    "飲料",
    "日用品",
    "医薬品",
    "ガジェット",
    "文房具",
    "趣味",
    "その他",
]

UNITS = [
    "個",
    "本",
    "袋",
    "箱",
    "パック",
    "ロール",
    "g",
    "kg",
    "ml",
    "L",
    "その他",
]

LOCATIONS = [
    "キッチン",
    "冷蔵庫",
    "冷凍庫",
    "洗面所",
    "リビング",
    "書斎",
    "倉庫",
    "その他",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"items": [], "logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "items" not in data:
        data["items"] = []

    if "logs" not in data:
        data["logs"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def stock_status(current, minimum):
    if current <= 0:
        return "🔴 在庫切れ"

    if current <= minimum:
        return "🟡 少ない"

    return "🟢 十分"


def to_item_df(data):
    rows = []

    for x in data["items"]:
        current = float(x.get("current_stock", 0))
        minimum = float(x.get("minimum_stock", 0))

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "category": x["category"],
            "current_stock": current,
            "minimum_stock": minimum,
            "unit": x["unit"],
            "location": x["location"],
            "status": stock_status(current, minimum),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        status_order = {
            "🔴 在庫切れ": 0,
            "🟡 少ない": 1,
            "🟢 十分": 2,
        }

        df["status_order"] = df["status"].map(status_order)
        df = df.sort_values(["status_order", "favorite", "created_at"], ascending=[True, False, False])

    return df


def to_log_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "created_at": x["created_at"],
            "date": x["date"],
            "item_name": x["item_name"],
            "action": x["action"],
            "amount": float(x.get("amount", 0)),
            "unit": x.get("unit", ""),
            "before": float(x.get("before", 0)),
            "after": float(x.get("after", 0)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_item(data, item_id):
    for x in data["items"]:
        if x["id"] == item_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📦",
    layout="wide"
)

st.title("📦 Day191：在庫管理アプリ")
st.caption("家にあるものの在庫数・最低在庫・保管場所を管理して、買い忘れを防ぐアプリ。")

data = load_data()

tab1, tab2, tab3 = st.tabs(["📦 在庫管理", "➕ 入出庫", "📜 履歴"])

with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("在庫を登録")

        name = st.text_input(
            "商品名",
            placeholder="例：プロテイン / 単三電池 / トイレットペーパー"
        )

        category = st.selectbox(
            "カテゴリ",
            CATEGORIES
        )

        c1, c2 = st.columns(2)

        with c1:
            current_stock = st.number_input(
                "現在の在庫数",
                min_value=0.0,
                value=1.0,
                step=0.5
            )

        with c2:
            minimum_stock = st.number_input(
                "最低在庫数",
                min_value=0.0,
                value=1.0,
                step=0.5
            )

        unit = st.selectbox(
            "単位",
            UNITS
        )

        location = st.selectbox(
            "保管場所",
            LOCATIONS
        )

        memo = st.text_area(
            "メモ",
            height=90,
            placeholder="例：安い時に買う / いつもAmazonで購入"
        )

        favorite = st.checkbox("⭐ よく使う")

        if st.button("📦 在庫を登録", type="primary"):
            if not name.strip():
                st.warning("商品名を入れてね。")
            else:
                item = {
                    "id": f"item_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "date": today_str(),
                    "name": name.strip(),
                    "category": category,
                    "current_stock": float(current_stock),
                    "minimum_stock": float(minimum_stock),
                    "unit": unit,
                    "location": location,
                    "memo": memo.strip(),
                    "favorite": favorite,
                }

                data["items"].append(item)
                save_data(data)

                st.success("在庫を登録したよ。")
                st.rerun()

    with right:
        st.subheader("在庫ステータス")

        df = to_item_df(data)

        if df.empty:
            st.info("まだ在庫が登録されていないよ。")
        else:
            shortage = len(df[df["status"] == "🟡 少ない"])
            empty = len(df[df["status"] == "🔴 在庫切れ"])
            enough = len(df[df["status"] == "🟢 十分"])

            c1, c2 = st.columns(2)

            with c1:
                st.metric("登録商品", len(df))
                st.metric("在庫切れ", empty)

            with c2:
                st.metric("少ない", shortage)
                st.metric("十分", enough)

            st.divider()

            st.subheader("不足・在庫切れ")

            danger = df[df["status"].isin(["🔴 在庫切れ", "🟡 少ない"])]

            if danger.empty:
                st.success("不足している在庫はなさそう。いい感じ！")
            else:
                st.dataframe(
                    danger[["name", "category", "current_stock", "unit", "minimum_stock", "location", "status"]],
                    use_container_width=True,
                    height=220
                )

    st.divider()
    st.subheader("在庫一覧")

    df = to_item_df(data)

    if df.empty:
        st.write("まだ在庫一覧が空だよ。")
    else:
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            keyword = st.text_input(
                "検索",
                placeholder="商品名・メモ"
            )

        with col_b:
            category_filter = st.selectbox(
                "カテゴリで絞る",
                ["すべて"] + CATEGORIES
            )

        with col_c:
            location_filter = st.selectbox(
                "場所で絞る",
                ["すべて"] + LOCATIONS
            )

        fav_only = st.checkbox("⭐ よく使うものだけ")

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

        if fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(
            view[[
                "name",
                "category",
                "current_stock",
                "unit",
                "minimum_stock",
                "location",
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
            st.write("条件に合う在庫がないよ。")
        else:
            selected_id = st.selectbox(
                "在庫を選ぶ",
                view["id"].tolist(),
                format_func=lambda x: f"{find_item(data, x)['name']} / {find_item(data, x)['location']}"
            )

            item = find_item(data, selected_id)

            if item:
                st.markdown(f"## {item['name']}")
                st.write(f"カテゴリ：{item['category']}")
                st.write(f"在庫：{item['current_stock']} {item['unit']}")
                st.write(f"最低在庫：{item['minimum_stock']} {item['unit']}")
                st.write(f"場所：{item['location']}")
                st.info(stock_status(float(item["current_stock"]), float(item["minimum_stock"])))

                if item.get("memo"):
                    st.write(item["memo"])

                c1, c2, c3 = st.columns(3)

                with c1:
                    new_stock = st.number_input(
                        "在庫数更新",
                        min_value=0.0,
                        value=float(item.get("current_stock", 0)),
                        step=0.5,
                        key=f"stock_{item['id']}"
                    )

                with c2:
                    new_minimum = st.number_input(
                        "最低在庫更新",
                        min_value=0.0,
                        value=float(item.get("minimum_stock", 0)),
                        step=0.5,
                        key=f"min_{item['id']}"
                    )

                with c3:
                    new_favorite = st.checkbox(
                        "⭐ よく使う",
                        value=bool(item.get("favorite", False)),
                        key=f"fav_{item['id']}"
                    )

                if st.button("📝 更新する"):
                    item["current_stock"] = float(new_stock)
                    item["minimum_stock"] = float(new_minimum)
                    item["favorite"] = new_favorite
                    item["updated_at"] = now_str()

                    save_data(data)

                    st.success("在庫を更新したよ。")
                    st.rerun()

                if st.button("🗑️ この在庫を削除", type="secondary"):
                    data["items"] = [
                        x for x in data["items"]
                        if x["id"] != selected_id
                    ]

                    save_data(data)
                    st.warning("在庫を削除したよ。")
                    st.rerun()

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ 在庫CSVダウンロード",
            data=csv,
            file_name="day191_inventory_manager_items.csv",
            mime="text/csv"
        )

with tab2:
    st.subheader("入出庫する")

    df = to_item_df(data)

    if df.empty:
        st.info("まず在庫を登録してね。")
    else:
        selected_id = st.selectbox(
            "商品を選ぶ",
            df["id"].tolist(),
            format_func=lambda x: f"{find_item(data, x)['name']} / 現在 {find_item(data, x)['current_stock']} {find_item(data, x)['unit']}",
            key="movement_item"
        )

        item = find_item(data, selected_id)

        if item:
            st.markdown(f"## {item['name']}")
            st.write(f"現在：{item['current_stock']} {item['unit']}")

            action = st.radio(
                "操作",
                ["入庫", "出庫"],
                horizontal=True
            )

            amount = st.number_input(
                "数量",
                min_value=0.0,
                value=1.0,
                step=0.5
            )

            memo = st.text_area(
                "入出庫メモ",
                height=80,
                placeholder="例：Amazonで購入 / 1つ使った"
            )

            if st.button("📦 入出庫を反映", type="primary"):
                before = float(item.get("current_stock", 0))

                if action == "入庫":
                    after = before + float(amount)
                else:
                    after = max(0, before - float(amount))

                item["current_stock"] = after
                item["updated_at"] = now_str()

                log = {
                    "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "date": today_str(),
                    "item_id": item["id"],
                    "item_name": item["name"],
                    "action": action,
                    "amount": float(amount),
                    "unit": item["unit"],
                    "before": before,
                    "after": after,
                    "memo": memo.strip(),
                }

                data["logs"].append(log)
                save_data(data)

                st.success(f"{action}を反映したよ。")
                st.rerun()

with tab3:
    st.subheader("入出庫履歴")

    log_df = to_log_df(data)

    if log_df.empty:
        st.write("まだ入出庫履歴がないよ。")
    else:
        st.dataframe(
            log_df[[
                "date",
                "item_name",
                "action",
                "amount",
                "unit",
                "before",
                "after",
                "memo",
            ]],
            use_container_width=True,
            height=320
        )

        csv = log_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ 履歴CSVダウンロード",
            data=csv,
            file_name="day191_inventory_manager_logs.csv",
            mime="text/csv"
        )
