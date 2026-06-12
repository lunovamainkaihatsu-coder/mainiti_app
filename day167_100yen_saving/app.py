import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day167：1日100円節約チャレンジ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day167_100yen_saving.json")

CATEGORIES = [
    "飲み物",
    "お菓子",
    "外食",
    "買い物",
    "交通",
    "サブスク",
    "娯楽",
    "その他",
]

CHALLENGE_GOALS = [
    100,
    300,
    500,
    1000,
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "logs": [],
                    "settings": {
                        "daily_goal": 100
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
        data["settings"] = {"daily_goal": 100}

    if "daily_goal" not in data["settings"]:
        data["settings"]["daily_goal"] = 100

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
            "category": x["category"],
            "title": x["title"],
            "amount": int(x.get("amount", 0)),
            "memo": x.get("memo", ""),
            "favorite": bool(x.get("favorite", False)),
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
    page_icon="💴",
    layout="wide"
)

st.title("💴 Day167：1日100円節約チャレンジ")
st.caption("小さな節約を記録して、月・年でどれだけ効くか見える化するアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("チャレンジ設定")

    current_goal = int(data["settings"].get("daily_goal", 100))

    goal = st.selectbox(
        "1日の節約目標",
        CHALLENGE_GOALS,
        index=CHALLENGE_GOALS.index(current_goal) if current_goal in CHALLENGE_GOALS else 0,
        format_func=lambda x: f"{x:,} 円"
    )

    if st.button("目標を保存"):
        data["settings"]["daily_goal"] = int(goal)
        save_data(data)
        st.success("目標を保存したよ。")
        st.rerun()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の節約を記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    title = st.text_input(
        "節約内容",
        placeholder="例：コンビニコーヒーを我慢"
    )

    amount = st.number_input(
        "節約できた金額",
        min_value=0,
        value=100,
        step=10
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：家のコーヒーで済ませた / お菓子を買わなかった"
    )

    favorite = st.checkbox("⭐ 良い節約")

    if st.button("💴 記録する", type="primary"):
        if not title.strip():
            st.warning("節約内容を入れてね。")
        elif amount <= 0:
            st.warning("節約金額を入れてね。")
        else:
            item = {
                "id": f"saving_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": log_date.isoformat(),
                "category": category,
                "title": title.strip(),
                "amount": int(amount),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["logs"].append(item)
            save_data(data)

            st.success("節約を記録したよ。")
            st.rerun()

with right:
    st.subheader("今日・今月の節約")

    df = to_df(data)
    daily_goal = int(data["settings"].get("daily_goal", 100))

    if df.empty:
        st.info("まだ節約記録がないよ。")
    else:
        today = today_str()
        month = current_month()

        today_df = df[df["date"] == today]
        month_df = df[df["month"] == month]

        today_total = int(today_df["amount"].sum()) if not today_df.empty else 0
        month_total = int(month_df["amount"].sum()) if not month_df.empty else 0
        total = int(df["amount"].sum())

        c1, c2 = st.columns(2)

        with c1:
            st.metric("今日の節約", yen(today_total))
            st.metric("今月の節約", yen(month_total))

        with c2:
            st.metric("累計節約", yen(total))
            st.metric("年間換算", yen(today_total * 365))

        rate = min(today_total / daily_goal, 1.0) if daily_goal > 0 else 0
        st.progress(rate)

        if today_total >= daily_goal:
            st.success("今日の節約目標達成！")
        else:
            st.info(f"今日の目標まであと {yen(daily_goal - today_total)}")

        st.divider()

        if not month_df.empty:
            st.subheader("今月カテゴリ別")
            cat = month_df.groupby("category")["amount"].sum().reset_index()
            cat = cat.sort_values("amount", ascending=False)
            st.dataframe(cat, use_container_width=True, height=220)

st.divider()
st.subheader("節約履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="節約内容・メモ")

    with col_b:
        category_filter = st.selectbox("カテゴリで絞る", ["すべて"] + CATEGORIES)

    with col_c:
        month_filter = st.text_input("月で絞る", value="", placeholder="例：2026-06")

    fav_only = st.checkbox("⭐ 良い節約だけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if month_filter.strip():
        view = view[view["month"] == month_filter.strip()]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "category", "title", "amount", "favorite", "memo"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う記録がないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{row['date']} / {row['title']} / {yen(row['amount'])}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "記録を選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        item = find_log(data, selected_id)

        if item:
            st.markdown(f"## {item['title']}")
            st.write(f"日付：{item['date']}")
            st.write(f"カテゴリ：{item['category']}")
            st.write(f"節約額：{yen(item.get('amount', 0))}")

            if item.get("memo"):
                st.info(item["memo"])

            c1, c2 = st.columns(2)

            with c1:
                new_amount = st.number_input(
                    "節約額を更新",
                    min_value=0,
                    value=int(item.get("amount", 0)),
                    step=10,
                    key=f"amount_{item['id']}"
                )

            with c2:
                new_fav = st.checkbox(
                    "⭐ 良い節約",
                    value=bool(item.get("favorite", False)),
                    key=f"fav_{item['id']}"
                )

            if st.button("📝 更新する"):
                item["amount"] = int(new_amount)
                item["favorite"] = new_fav
                item["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ この記録を削除", type="secondary"):
                data["logs"] = [x for x in data["logs"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day167_100yen_saving.csv",
        mime="text/csv"
    )
