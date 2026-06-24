import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day179：所持金・支出ログ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day179_money_log.json")

EXPENSE_CATEGORIES = [
    "食費",
    "日用品",
    "交通",
    "娯楽",
    "医療",
    "サブスク",
    "家族",
    "学習",
    "その他",
]

INCOME_CATEGORIES = [
    "給料",
    "副収入",
    "臨時収入",
    "売上",
    "お小遣い",
    "その他",
]

TYPES = [
    "支出",
    "収入",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "logs": [],
                    "settings": {
                        "start_money": 0
                    }
                },
                f,
                ensure_ascii=False,
                indent=2
            )


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "logs" not in data:
        data["logs"] = []

    if "settings" not in data:
        data["settings"] = {"start_money": 0}

    if "start_money" not in data["settings"]:
        data["settings"]["start_money"] = 0

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

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "month": x["date"][:7],
            "type": x["type"],
            "category": x["category"],
            "amount": int(x.get("amount", 0)),
            "title": x.get("title", ""),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_log(data, log_id):
    for x in data["logs"]:
        if x["id"] == log_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💰",
    layout="wide"
)

st.title("💰 Day179：所持金・支出ログ")
st.caption("収入・支出・現在の所持金をざっくり見える化するアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("初期設定")

    start_money = st.number_input(
        "開始時の所持金",
        min_value=0,
        value=int(data["settings"].get("start_money", 0)),
        step=1000
    )

    if st.button("開始所持金を保存"):
        data["settings"]["start_money"] = int(start_money)
        save_data(data)
        st.success("保存したよ。")
        st.rerun()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("お金の動きを記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    money_type = st.radio(
        "種類",
        TYPES,
        horizontal=True
    )

    if money_type == "支出":
        category = st.selectbox("カテゴリ", EXPENSE_CATEGORIES)
    else:
        category = st.selectbox("カテゴリ", INCOME_CATEGORIES)

    title = st.text_input(
        "内容",
        placeholder="例：昼ごはん / note売上 / 電車代"
    )

    amount = st.number_input(
        "金額",
        min_value=0,
        value=1000,
        step=100
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：コンビニで購入 / 臨時収入 / 使いすぎ注意"
    )

    if st.button("💰 記録する", type="primary"):
        if not title.strip():
            st.warning("内容を入れてね。")
        elif amount <= 0:
            st.warning("金額を入れてね。")
        else:
            item = {
                "id": f"money_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": log_date.isoformat(),
                "type": money_type,
                "category": category,
                "title": title.strip(),
                "amount": int(amount),
                "memo": memo.strip(),
            }

            data["logs"].append(item)
            save_data(data)

            st.success("記録したよ。")
            st.rerun()

with right:
    st.subheader("現在のお金")

    df = to_df(data)
    start = int(data["settings"].get("start_money", 0))

    if df.empty:
        income_total = 0
        expense_total = 0
    else:
        income_total = int(df[df["type"] == "収入"]["amount"].sum())
        expense_total = int(df[df["type"] == "支出"]["amount"].sum())

    current_money = start + income_total - expense_total

    c1, c2 = st.columns(2)

    with c1:
        st.metric("開始所持金", yen(start))
        st.metric("収入合計", yen(income_total))

    with c2:
        st.metric("支出合計", yen(expense_total))
        st.metric("現在の所持金", yen(current_money))

    st.divider()

    if current_money >= start:
        st.success("開始時より増えてる！いい感じ。")
    else:
        st.warning("開始時より減ってるよ。支出を少し確認しよう。")

    if not df.empty:
        month = current_month()
        month_df = df[df["month"] == month]

        month_income = int(month_df[month_df["type"] == "収入"]["amount"].sum())
        month_expense = int(month_df[month_df["type"] == "支出"]["amount"].sum())
        month_balance = month_income - month_expense

        st.subheader("今月")
        st.metric("今月収支", yen(month_balance))
        st.write(f"収入：{yen(month_income)} / 支出：{yen(month_expense)}")

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        type_filter = st.selectbox(
            "種類で絞る",
            ["すべて"] + TYPES
        )

    with col_b:
        keyword = st.text_input(
            "検索",
            placeholder="内容・メモ"
        )

    with col_c:
        month_filter = st.text_input(
            "月で絞る",
            value="",
            placeholder="例：2026-06"
        )

    view = df.copy()

    if type_filter != "すべて":
        view = view[view["type"] == type_filter]

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if month_filter.strip():
        view = view[view["month"] == month_filter.strip()]

    st.dataframe(
        view[[
            "date",
            "type",
            "category",
            "title",
            "amount",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("月別集計")

    monthly = df.groupby(["month", "type"])["amount"].sum().reset_index()

    if not monthly.empty:
        st.dataframe(
            monthly,
            use_container_width=True,
            height=220
        )

    st.divider()
    st.subheader("支出カテゴリ別")

    expense_df = df[df["type"] == "支出"]

    if expense_df.empty:
        st.write("支出データがないよ。")
    else:
        expense_cat = expense_df.groupby("category")["amount"].sum().reset_index()
        expense_cat = expense_cat.sort_values("amount", ascending=False)

        st.dataframe(
            expense_cat,
            use_container_width=True,
            height=220
        )

    st.divider()
    st.subheader("詳細・削除")

    if view.empty:
        st.write("条件に合う記録がないよ。")
    else:
        selected_id = st.selectbox(
            "記録を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_log(data, x)['date']} / {find_log(data, x)['type']} / {find_log(data, x)['title']}"
        )

        selected = find_log(data, selected_id)

        if selected:
            st.markdown(f"## {selected['title']}")
            st.write(f"日付：{selected['date']}")
            st.write(f"種類：{selected['type']}")
            st.write(f"カテゴリ：{selected['category']}")
            st.write(f"金額：{yen(selected['amount'])}")

            if selected.get("memo"):
                st.info(selected["memo"])

            if st.button("🗑️ この記録を削除", type="secondary"):
                data["logs"] = [
                    x for x in data["logs"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day179_money_log.csv",
        mime="text/csv"
    )
