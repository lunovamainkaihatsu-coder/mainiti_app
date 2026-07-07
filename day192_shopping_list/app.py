import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day192：買い物リスト"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day192_shopping_list.json")

CATEGORIES = [
    "食品",
    "飲料",
    "日用品",
    "医薬品",
    "ガジェット",
    "趣味",
    "家族",
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

SHOPS = [
    "スーパー",
    "ドラッグストア",
    "コンビニ",
    "100円ショップ",
    "Amazon",
    "楽天",
    "ホームセンター",
    "その他",
]

PRIORITIES = [
    "🔴 高",
    "🟡 普通",
    "🟢 低",
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


def priority_order(priority):
    return {
        "🔴 高": 0,
        "🟡 普通": 1,
        "🟢 低": 2,
    }.get(priority, 9)


def to_df(data):
    rows = []

    for x in data["items"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "category": x["category"],
            "quantity": float(x.get("quantity", 1)),
            "unit": x["unit"],
            "shop": x["shop"],
            "priority": x["priority"],
            "done": bool(x.get("done", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df["priority_order"] = df["priority"].apply(priority_order)
        df = df.sort_values(
            ["done", "priority_order", "created_at"],
            ascending=[True, True, False]
        )

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

st.title("🛒 Day192：買い物リスト")
st.caption("買うもの・数量・お店・優先度を管理して、買い忘れを防ぐアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("買うものを追加")

    name = st.text_input(
        "商品名",
        placeholder="例：牛乳 / 卵 / トイレットペーパー"
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

    shop = st.selectbox(
        "買う予定のお店",
        SHOPS
    )

    priority = st.selectbox(
        "優先度",
        PRIORITIES
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：安ければ2本 / セールなら買う / 在庫少なめ"
    )

    if st.button("🛒 リストに追加", type="primary"):
        if not name.strip():
            st.warning("商品名を入れてね。")
        else:
            item = {
                "id": f"shop_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "name": name.strip(),
                "category": category,
                "quantity": float(quantity),
                "unit": unit,
                "shop": shop,
                "priority": priority,
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
        todo = df[df["done"] == False]
        done = df[df["done"] == True]
        high = todo[todo["priority"] == "🔴 高"]

        c1, c2 = st.columns(2)

        with c1:
            st.metric("買うもの", len(todo))
            st.metric("優先度 高", len(high))

        with c2:
            st.metric("購入済み", len(done))
            st.metric("登録合計", len(df))

        st.divider()

        st.subheader("お店別 未購入")

        if todo.empty:
            st.success("未購入のものはないよ。")
        else:
            shop_count = todo["shop"].value_counts().reset_index()
            shop_count.columns = ["お店", "件数"]

            st.dataframe(
                shop_count,
                use_container_width=True,
                height=220
            )

st.divider()
st.subheader("買い物一覧")

df = to_df(data)

if df.empty:
    st.write("まだ一覧が空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="商品名・メモ"
        )

    with col_b:
        shop_filter = st.selectbox(
            "お店で絞る",
            ["すべて"] + SHOPS
        )

    with col_c:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    col_d, col_e = st.columns(2)

    with col_d:
        priority_filter = st.selectbox(
            "優先度で絞る",
            ["すべて"] + PRIORITIES
        )

    with col_e:
        show_done = st.checkbox("購入済みも表示", value=True)

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["name"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if shop_filter != "すべて":
        view = view[view["shop"] == shop_filter]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if priority_filter != "すべて":
        view = view[view["priority"] == priority_filter]

    if not show_done:
        view = view[view["done"] == False]

    st.dataframe(
        view[[
            "done",
            "name",
            "category",
            "quantity",
            "unit",
            "shop",
            "priority",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("購入チェック・更新")

    if view.empty:
        st.write("条件に合う買い物がないよ。")
    else:
        selected_id = st.selectbox(
            "項目を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{'✅' if find_item(data, x).get('done') else '□'} {find_item(data, x)['name']} / {find_item(data, x)['shop']}"
        )

        item = find_item(data, selected_id)

        if item:
            st.markdown(f"## {item['name']}")
            st.write(f"カテゴリ：{item['category']}")
            st.write(f"数量：{item['quantity']} {item['unit']}")
            st.write(f"お店：{item['shop']}")
            st.write(f"優先度：{item['priority']}")

            if item.get("memo"):
                st.info(item["memo"])

            c1, c2, c3 = st.columns(3)

            with c1:
                new_done = st.checkbox(
                    "✅ 購入済み",
                    value=bool(item.get("done", False)),
                    key=f"done_{item['id']}"
                )

            with c2:
                new_priority = st.selectbox(
                    "優先度更新",
                    PRIORITIES,
                    index=PRIORITIES.index(item.get("priority", "🟡 普通")),
                    key=f"priority_{item['id']}"
                )

            with c3:
                new_quantity = st.number_input(
                    "数量更新",
                    min_value=0.0,
                    value=float(item.get("quantity", 1)),
                    step=0.5,
                    key=f"quantity_{item['id']}"
                )

            if st.button("📝 更新する"):
                item["done"] = new_done
                item["priority"] = new_priority
                item["quantity"] = float(new_quantity)
                item["updated_at"] = now_str()

                save_data(data)

                st.success("買い物項目を更新したよ。")
                st.rerun()

            if st.button("🗑️ この項目を削除", type="secondary"):
                data["items"] = [
                    x for x in data["items"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day192_shopping_list.csv",
        mime="text/csv"
    )
