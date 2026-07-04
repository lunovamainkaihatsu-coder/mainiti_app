import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day189：レシート管理帳"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day189_receipt_manager.json")

CATEGORIES = [
    "食費",
    "日用品",
    "交通",
    "医療",
    "娯楽",
    "学習",
    "家族",
    "サブスク",
    "その他",
]

PAYMENTS = [
    "現金",
    "クレジットカード",
    "PayPay",
    "楽天Pay",
    "交通系IC",
    "デビットカード",
    "その他",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"receipts": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "receipts" not in data:
        data["receipts"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def current_month():
    return date.today().strftime("%Y-%m")


def yen(value):
    return f"{int(value):,} 円"


def to_df(data):
    rows = []

    for x in data["receipts"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "month": x["date"][:7],
            "shop": x["shop"],
            "category": x["category"],
            "payment": x["payment"],
            "amount": int(x.get("amount", 0)),
            "memo": x.get("memo", ""),
            "favorite": bool(x.get("favorite", False)),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_receipt(data, receipt_id):
    for x in data["receipts"]:
        if x["id"] == receipt_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Day189：レシート管理帳")
st.caption("店名・金額・カテゴリ・支払い方法を記録して、支出を見える化するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("レシートを登録")

    receipt_date = st.date_input(
        "購入日",
        value=date.today()
    )

    shop = st.text_input(
        "店名",
        placeholder="例：ローソン / イオン / Amazon"
    )

    amount = st.number_input(
        "金額",
        min_value=0,
        value=1000,
        step=10
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    payment = st.selectbox(
        "支払い方法",
        PAYMENTS
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：昼ごはん / 日用品まとめ買い / セール品"
    )

    favorite = st.checkbox("⭐ 見返したいレシート")

    if st.button("🧾 保存する", type="primary"):
        if not shop.strip():
            st.warning("店名を入れてね。")
        elif amount <= 0:
            st.warning("金額を入れてね。")
        else:
            item = {
                "id": f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": receipt_date.isoformat(),
                "shop": shop.strip(),
                "amount": int(amount),
                "category": category,
                "payment": payment,
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["receipts"].append(item)
            save_data(data)

            st.success("レシートを保存したよ。")
            st.rerun()

with right:
    st.subheader("支出ステータス")

    df = to_df(data)

    if df.empty:
        st.info("まだレシートが登録されていないよ。")
    else:
        month = current_month()
        month_df = df[df["month"] == month]

        total = int(df["amount"].sum())
        month_total = int(month_df["amount"].sum()) if not month_df.empty else 0
        receipt_count = len(df)
        month_count = len(month_df)

        c1, c2 = st.columns(2)

        with c1:
            st.metric("今月支出", yen(month_total))
            st.metric("今月枚数", month_count)

        with c2:
            st.metric("累計支出", yen(total))
            st.metric("累計枚数", receipt_count)

        st.divider()

        if not month_df.empty:
            st.subheader("今月カテゴリ別")

            cat = month_df.groupby("category")["amount"].sum().reset_index()
            cat = cat.sort_values("amount", ascending=False)

            st.dataframe(
                cat,
                use_container_width=True,
                height=220
            )

st.divider()
st.subheader("レシート一覧")

df = to_df(data)

if df.empty:
    st.write("まだレシート一覧が空だよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="店名・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        payment_filter = st.selectbox(
            "支払い方法で絞る",
            ["すべて"] + PAYMENTS
        )

    month_filter = st.text_input(
        "月で絞る",
        value="",
        placeholder="例：2026-07"
    )

    fav_only = st.checkbox("⭐ 見返したいものだけ")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["shop"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if payment_filter != "すべて":
        view = view[view["payment"] == payment_filter]

    if month_filter.strip():
        view = view[view["month"] == month_filter.strip()]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[[
            "date",
            "shop",
            "category",
            "payment",
            "amount",
            "favorite",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("集計")

    if not view.empty:
        c1, c2 = st.columns(2)

        with c1:
            st.metric("表示中の合計", yen(int(view["amount"].sum())))

        with c2:
            st.metric("表示中の枚数", len(view))

        st.subheader("月別集計")

        monthly = df.groupby("month")["amount"].sum().reset_index()
        monthly = monthly.sort_values("month", ascending=False)

        st.dataframe(
            monthly,
            use_container_width=True,
            height=220
        )

        st.subheader("支払い方法別")

        pay = df.groupby("payment")["amount"].sum().reset_index()
        pay = pay.sort_values("amount", ascending=False)

        st.dataframe(
            pay,
            use_container_width=True,
            height=220
        )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合うレシートがないよ。")
    else:
        selected_id = st.selectbox(
            "レシートを選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_receipt(data, x)['date']} / {find_receipt(data, x)['shop']} / {yen(find_receipt(data, x)['amount'])}"
        )

        receipt = find_receipt(data, selected_id)

        if receipt:
            st.markdown(f"## {receipt['shop']}")
            st.write(f"購入日：{receipt['date']}")
            st.write(f"金額：{yen(receipt['amount'])}")
            st.write(f"カテゴリ：{receipt['category']}")
            st.write(f"支払い方法：{receipt['payment']}")

            if receipt.get("memo"):
                st.info(receipt["memo"])

            c1, c2, c3 = st.columns(3)

            with c1:
                new_amount = st.number_input(
                    "金額を更新",
                    min_value=0,
                    value=int(receipt.get("amount", 0)),
                    step=10,
                    key=f"amount_{receipt['id']}"
                )

            with c2:
                new_category = st.selectbox(
                    "カテゴリ更新",
                    CATEGORIES,
                    index=CATEGORIES.index(receipt.get("category", "その他")),
                    key=f"category_{receipt['id']}"
                )

            with c3:
                new_favorite = st.checkbox(
                    "⭐ 見返したい",
                    value=bool(receipt.get("favorite", False)),
                    key=f"fav_{receipt['id']}"
                )

            if st.button("📝 更新する"):
                receipt["amount"] = int(new_amount)
                receipt["category"] = new_category
                receipt["favorite"] = new_favorite
                receipt["updated_at"] = now_str()

                save_data(data)

                st.success("レシートを更新したよ。")
                st.rerun()

            if st.button("🗑️ このレシートを削除", type="secondary"):
                data["receipts"] = [
                    x for x in data["receipts"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day189_receipt_manager.csv",
        mime="text/csv"
    )
