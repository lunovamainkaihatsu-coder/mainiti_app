import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day170：買い物リストメーカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day170_shopping_list.json")

CATEGORIES = [
    "野菜",
    "肉",
    "魚",
    "卵・乳製品",
    "飲み物",
    "主食",
    "調味料",
    "日用品",
    "お菓子",
    "その他",
]

PRIORITIES = [
    "高",
    "中",
    "低",
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
    "その他",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"items": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "items" not in data:
        data["items"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def yen(value):
    return f"{int(value):,} 円"


def to_df(data):
    rows = []

    for x in data["items"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "category": x["category"],
            "priority": x["priority"],
            "quantity": x["quantity"],
            "unit": x["unit"],
            "price": int(x.get("price", 0)),
            "done": bool(x.get("done", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["priority_order"] = df["priority"].map({"高": 0, "中": 1, "低": 2})
        df = df.sort_values(["done", "priority_order", "created_at"], ascending=[True, True, False])

    return df


def find_item(data, item_id):
    for x in data["items"]:
        if x["id"] == item_id:
            return x
    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Day170：買い物リストメーカー")
st.caption("買うもの・予定価格・優先度を管理して、買い忘れを防ぐアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("買うものを追加")

    name = st.text_input(
        "商品名",
        placeholder="例：牛乳、卵、納豆"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    priority = st.selectbox(
        "優先度",
        PRIORITIES
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

    price = st.number_input(
        "予定価格",
        min_value=0,
        value=0,
        step=10
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：安ければ2本 / 特売なら買う"
    )

    if st.button("🛒 リストに追加", type="primary"):
        if not name.strip():
            st.warning("商品名を入れてね。")
        else:
            item = {
                "id": f"item_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "name": name.strip(),
                "category": category,
                "priority": priority,
                "quantity": float(quantity),
                "unit": unit,
                "price": int(price),
                "memo": memo.strip(),
                "done": False,
            }

            data["items"].append(item)
            save_data(data)

            st.success("買い物リストに追加したよ。")
            st.rerun()

with right:
    st.subheader("買い物ステータス")

    df = to_df(data)

    if df.empty:
        st.info("まだ買い物リストが空だよ。")
    else:
        not_done = df[df["done"] == False]
        done = df[df["done"] == True]

        total_price = int(df["price"].sum())
        remaining_price = int(not_done["price"].sum()) if not not_done.empty else 0

        c1, c2 = st.columns(2)

        with c1:
            st.metric("未購入", len(not_done))
            st.metric("予定金額", yen(total_price))

        with c2:
            st.metric("購入済み", len(done))
            st.metric("未購入分", yen(remaining_price))

        st.divider()

        st.subheader("カテゴリ別")
        cat_count = df.groupby("category")["name"].count().reset_index()
        cat_count.columns = ["カテゴリ", "件数"]

        st.dataframe(
            cat_count,
            use_container_width=True,
            height=220
        )

st.divider()
st.subheader("買い物リスト")

df = to_df(data)

if df.empty:
    st.write("まだ買い物リストがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="商品名・メモ")

    with col_b:
        category_filter = st.selectbox("カテゴリで絞る", ["すべて"] + CATEGORIES)

    with col_c:
        priority_filter = st.selectbox("優先度で絞る", ["すべて"] + PRIORITIES)

    show_done = st.checkbox("購入済みも表示", value=True)

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["name"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if priority_filter != "すべて":
        view = view[view["priority"] == priority_filter]

    if not show_done:
        view = view[view["done"] == False]

    st.dataframe(
        view[["done", "name", "category", "priority", "quantity", "unit", "price", "memo"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("購入チェック・更新")

    if view.empty:
        st.write("条件に合う買い物がないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{'✅' if row['done'] else '□'} {row['name']} / {row['category']} / {yen(row['price'])}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "項目を選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        item = find_item(data, selected_id)

        if item:
            st.markdown(f"## {item['name']}")
            st.write(f"カテゴリ：{item['category']}")
            st.write(f"優先度：{item['priority']}")
            st.write(f"数量：{item['quantity']} {item['unit']}")
            st.write(f"予定価格：{yen(item.get('price', 0))}")

            if item.get("memo"):
                st.info(item["memo"])

            c1, c2 = st.columns(2)

            with c1:
                new_done = st.checkbox(
                    "✅ 購入済み",
                    value=bool(item.get("done", False)),
                    key=f"done_{item['id']}"
                )

            with c2:
                new_price = st.number_input(
                    "価格を更新",
                    min_value=0,
                    value=int(item.get("price", 0)),
                    step=10,
                    key=f"price_{item['id']}"
                )

            if st.button("📝 更新する"):
                item["done"] = new_done
                item["price"] = int(new_price)
                item["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ この項目を削除", type="secondary"):
                data["items"] = [x for x in data["items"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day170_shopping_list.csv",
        mime="text/csv"
    )
