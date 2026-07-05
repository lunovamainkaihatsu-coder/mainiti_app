import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

APP_TITLE = "Day190：保証書・購入品管理帳"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day190_warranty_manager.json")

CATEGORIES = [
    "PC",
    "スマホ",
    "家電",
    "家具",
    "ガジェット",
    "ゲーム",
    "車",
    "日用品",
    "その他",
]

STATUS_FILTERS = [
    "すべて",
    "保証中",
    "30日以内に終了",
    "保証切れ",
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


def calc_warranty_end(purchase_date_str, warranty_months):
    try:
        purchase = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
        end_date = purchase + relativedelta(months=int(warranty_months))
        return end_date.isoformat()
    except:
        return ""


def days_left(end_date_str):
    try:
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        return (end - date.today()).days
    except:
        return None


def warranty_status(days):
    if days is None:
        return "不明"

    if days < 0:
        return "保証切れ"

    if days <= 30:
        return "30日以内に終了"

    return "保証中"


def status_icon(status):
    if status == "保証中":
        return "🟢"

    if status == "30日以内に終了":
        return "🟡"

    if status == "保証切れ":
        return "🔴"

    return "⚪"


def to_df(data):
    rows = []

    for x in data["items"]:
        end_date = calc_warranty_end(
            x.get("purchase_date", ""),
            int(x.get("warranty_months", 0))
        )

        left = days_left(end_date)
        status = warranty_status(left)

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "name": x["name"],
            "maker": x.get("maker", ""),
            "category": x["category"],
            "purchase_date": x.get("purchase_date", ""),
            "price": int(x.get("price", 0)),
            "shop": x.get("shop", ""),
            "warranty_months": int(x.get("warranty_months", 0)),
            "warranty_end": end_date,
            "days_left": left if left is not None else "",
            "status": status,
            "serial": x.get("serial", ""),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(["status", "warranty_end", "created_at"], ascending=[True, True, False])

    return df


def find_item(data, item_id):
    for x in data["items"]:
        if x["id"] == item_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Day190：保証書・購入品管理帳")
st.caption("家電・PC・ガジェットなどの購入日、保証期限、購入金額を管理するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("購入品を登録")

    name = st.text_input(
        "商品名",
        placeholder="例：Samsung SSD 990 EVO"
    )

    maker = st.text_input(
        "メーカー",
        placeholder="例：Samsung / Apple / Anker"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    purchase_date = st.date_input(
        "購入日",
        value=date.today()
    )

    price = st.number_input(
        "購入金額",
        min_value=0,
        value=10000,
        step=100
    )

    shop = st.text_input(
        "購入店舗",
        placeholder="例：Amazon / 楽天 / ヨドバシ"
    )

    warranty_months = st.number_input(
        "保証期間（月）",
        min_value=0,
        value=12,
        step=1
    )

    serial = st.text_input(
        "シリアル番号",
        placeholder="任意"
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：レシート保存済み / 箱あり / 注文番号など"
    )

    favorite = st.checkbox("⭐ 大事な購入品")

    end_date = purchase_date + relativedelta(months=int(warranty_months))
    st.info(f"保証期限：{end_date.isoformat()}")

    if st.button("🧾 登録する", type="primary"):
        if not name.strip():
            st.warning("商品名を入れてね。")
        else:
            item = {
                "id": f"warranty_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "name": name.strip(),
                "maker": maker.strip(),
                "category": category,
                "purchase_date": purchase_date.isoformat(),
                "price": int(price),
                "shop": shop.strip(),
                "warranty_months": int(warranty_months),
                "serial": serial.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["items"].append(item)
            save_data(data)

            st.success("購入品を登録したよ。")
            st.rerun()

with right:
    st.subheader("保証ステータス")

    df = to_df(data)

    if df.empty:
        st.info("まだ購入品が登録されていないよ。")
    else:
        active = len(df[df["status"] == "保証中"])
        soon = len(df[df["status"] == "30日以内に終了"])
        expired = len(df[df["status"] == "保証切れ"])
        total_value = int(df["price"].sum())

        c1, c2 = st.columns(2)

        with c1:
            st.metric("登録数", len(df))
            st.metric("保証中", active)

        with c2:
            st.metric("30日以内", soon)
            st.metric("保証切れ", expired)

        st.metric("購入総額", yen(total_value))

        st.divider()

        st.subheader("カテゴリ別")

        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "件数"]

        st.dataframe(
            cat_count,
            use_container_width=True,
            height=220
        )

st.divider()
st.subheader("購入品一覧")

df = to_df(data)

if df.empty:
    st.write("まだ一覧が空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="商品名・メーカー・店舗・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        status_filter = st.selectbox(
            "保証状態で絞る",
            STATUS_FILTERS
        )

    fav_only = st.checkbox("⭐ 大事な購入品だけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["name"].fillna("").str.contains(q, case=False, na=False)
            | view["maker"].fillna("").str.contains(q, case=False, na=False)
            | view["shop"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    display = view.copy()

    if not display.empty:
        display["保証状態"] = display["status"].apply(lambda x: f"{status_icon(x)} {x}")

    st.dataframe(
        display[[
            "name",
            "maker",
            "category",
            "purchase_date",
            "price",
            "shop",
            "warranty_months",
            "warranty_end",
            "days_left",
            "保証状態",
            "favorite",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("保証期限が近いもの")

    near = df[df["status"].isin(["30日以内に終了", "保証切れ"])]

    if near.empty:
        st.success("保証期限が近い・切れているものは少なそう。")
    else:
        st.dataframe(
            near[[
                "name",
                "maker",
                "category",
                "warranty_end",
                "days_left",
                "status",
                "memo",
            ]],
            use_container_width=True,
            height=220
        )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う購入品がないよ。")
    else:
        selected_id = st.selectbox(
            "購入品を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_item(data, x)['name']} / {find_item(data, x).get('maker', '')}"
        )

        item = find_item(data, selected_id)

        if item:
            end = calc_warranty_end(
                item.get("purchase_date", ""),
                item.get("warranty_months", 0)
            )

            left_days = days_left(end)
            status = warranty_status(left_days)

            st.markdown(f"## {item['name']}")
            st.write(f"メーカー：{item.get('maker', '')}")
            st.write(f"カテゴリ：{item['category']}")
            st.write(f"購入日：{item.get('purchase_date', '')}")
            st.write(f"購入金額：{yen(item.get('price', 0))}")
            st.write(f"購入店舗：{item.get('shop', '')}")
            st.write(f"保証期限：{end}")
            st.write(f"保証状態：{status_icon(status)} {status}")

            if item.get("serial"):
                st.write(f"シリアル番号：{item['serial']}")

            if item.get("memo"):
                st.info(item["memo"])

            c1, c2, c3 = st.columns(3)

            with c1:
                new_price = st.number_input(
                    "金額更新",
                    min_value=0,
                    value=int(item.get("price", 0)),
                    step=100,
                    key=f"price_{item['id']}"
                )

            with c2:
                new_warranty = st.number_input(
                    "保証期間更新（月）",
                    min_value=0,
                    value=int(item.get("warranty_months", 0)),
                    step=1,
                    key=f"warranty_{item['id']}"
                )

            with c3:
                new_favorite = st.checkbox(
                    "⭐ 大事",
                    value=bool(item.get("favorite", False)),
                    key=f"fav_{item['id']}"
                )

            if st.button("📝 更新する"):
                item["price"] = int(new_price)
                item["warranty_months"] = int(new_warranty)
                item["favorite"] = new_favorite
                item["updated_at"] = now_str()

                save_data(data)

                st.success("購入品を更新したよ。")
                st.rerun()

            if st.button("🗑️ この購入品を削除", type="secondary"):
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
        file_name="day190_warranty_manager.csv",
        mime="text/csv"
    )
