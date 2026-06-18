import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day173：水分補給トラッカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day173_water_tracker.json")

DRINK_TYPES = [
    "水",
    "お茶",
    "炭酸水",
    "コーヒー",
    "プロテイン",
    "スムージー",
    "ジュース",
    "その他",
]

QUICK_AMOUNTS = [
    100,
    200,
    250,
    300,
    500,
    750,
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
                        "daily_goal": 2000
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
        data["settings"] = {"daily_goal": 2000}

    if "daily_goal" not in data["settings"]:
        data["settings"]["daily_goal"] = 2000

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def current_month():
    return date.today().strftime("%Y-%m")


def ml(value):
    return f"{int(value):,} ml"


def to_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "month": x["date"][:7],
            "drink_type": x["drink_type"],
            "amount": int(x.get("amount", 0)),
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
    page_icon="💧",
    layout="wide"
)

st.title("💧 Day173：水分補給トラッカー")
st.caption("今日飲んだ水分量を記録して、目標達成率を見える化するアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("目標設定")

    current_goal = int(
        data["settings"].get(
            "daily_goal",
            2000
        )
    )

    daily_goal = st.number_input(
        "1日の目標水分量（ml）",
        min_value=500,
        max_value=5000,
        value=current_goal,
        step=100
    )

    if st.button("目標を保存"):
        data["settings"]["daily_goal"] = int(daily_goal)
        save_data(data)
        st.success("目標を保存したよ。")
        st.rerun()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("水分を記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    drink_type = st.selectbox(
        "飲み物",
        DRINK_TYPES
    )

    quick = st.selectbox(
        "よく使う量",
        QUICK_AMOUNTS,
        index=3,
        format_func=lambda x: f"{x} ml"
    )

    amount = st.number_input(
        "飲んだ量（ml）",
        min_value=0,
        value=int(quick),
        step=50
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="例：朝の水 / 運動後 / スムージー"
    )

    if st.button("💧 記録する", type="primary"):
        if amount <= 0:
            st.warning("飲んだ量を入力してね。")
        else:
            item = {
                "id": f"water_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": log_date.isoformat(),
                "drink_type": drink_type,
                "amount": int(amount),
                "memo": memo.strip(),
            }

            data["logs"].append(item)
            save_data(data)

            st.success("水分補給を記録したよ。")
            st.rerun()

with right:
    st.subheader("今日の水分量")

    df = to_df(data)
    goal = int(data["settings"].get("daily_goal", 2000))

    if df.empty:
        st.info("まだ記録がないよ。")
    else:
        today = today_str()
        month = current_month()

        today_df = df[df["date"] == today]
        month_df = df[df["month"] == month]

        today_total = int(today_df["amount"].sum()) if not today_df.empty else 0
        month_total = int(month_df["amount"].sum()) if not month_df.empty else 0
        total = int(df["amount"].sum())

        remaining = max(goal - today_total, 0)
        rate = min(today_total / goal, 1.0) if goal > 0 else 0

        c1, c2 = st.columns(2)

        with c1:
            st.metric("今日", ml(today_total))
            st.metric("今月", ml(month_total))

        with c2:
            st.metric("あと", ml(remaining))
            st.metric("累計", ml(total))

        st.progress(rate)

        if today_total >= goal:
            st.success("今日の水分目標達成！いい感じ！")
        elif today_total >= goal * 0.7:
            st.info("あと少しで達成だよ。")
        else:
            st.warning("まだ少なめ。こまめに飲もう。")

        st.divider()

        if not today_df.empty:
            st.subheader("今日の内訳")
            type_sum = today_df.groupby("drink_type")["amount"].sum().reset_index()
            type_sum = type_sum.sort_values("amount", ascending=False)

            st.dataframe(
                type_sum,
                use_container_width=True,
                height=220
            )

st.divider()
st.subheader("水分補給履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="メモ")

    with col_b:
        drink_filter = st.selectbox("飲み物で絞る", ["すべて"] + DRINK_TYPES)

    with col_c:
        month_filter = st.text_input("月で絞る", value="", placeholder="例：2026-06")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if drink_filter != "すべて":
        view = view[view["drink_type"] == drink_filter]

    if month_filter.strip():
        view = view[view["month"] == month_filter.strip()]

    st.dataframe(
        view[["date", "drink_type", "amount", "memo"]],
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
            row["id"]: f"{row['date']} / {row['drink_type']} / {ml(row['amount'])}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "記録を選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        item = find_log(data, selected_id)

        if item:
            st.markdown(f"## {item['drink_type']}")
            st.write(f"日付：{item['date']}")
            st.write(f"量：{ml(item.get('amount', 0))}")

            if item.get("memo"):
                st.info(item["memo"])

            new_amount = st.number_input(
                "量を更新",
                min_value=0,
                value=int(item.get("amount", 0)),
                step=50,
                key=f"amount_{item['id']}"
            )

            if st.button("📝 更新する"):
                item["amount"] = int(new_amount)
                item["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

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
        file_name="day173_water_tracker.csv",
        mime="text/csv"
    )
