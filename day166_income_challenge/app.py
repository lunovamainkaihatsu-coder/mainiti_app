import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day166：収益化チャレンジ管理"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day166_income_challenge.json")

CATEGORIES = [
    "アプリ",
    "note",
    "ココナラ",
    "ブログ",
    "YouTube",
    "Kindle",
    "その他",
]

ACTIONS = [
    "制作",
    "投稿",
    "改善",
    "販売",
    "宣伝",
    "分析",
    "収益発生",
    "その他",
]

MONTHLY_GOALS = [
    1000,
    5000,
    10000,
    30000,
    50000,
    100000,
    300000,
    500000,
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": [], "settings": {"monthly_goal": 50000}}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "logs" not in data:
        data["logs"] = []

    if "settings" not in data:
        data["settings"] = {"monthly_goal": 50000}

    if "monthly_goal" not in data["settings"]:
        data["settings"]["monthly_goal"] = 50000

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
            "action": x["action"],
            "title": x["title"],
            "income": int(x.get("income", 0)),
            "views": int(x.get("views", 0)),
            "sales": int(x.get("sales", 0)),
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
    page_icon="📈",
    layout="wide"
)

st.title("📈 Day166：収益化チャレンジ管理")
st.caption("アプリ・note・ココナラなど、収益化までの行動と成果を見える化するアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("目標設定")

    current_goal = int(data["settings"].get("monthly_goal", 50000))

    goal_type = st.radio(
        "月間目標の設定方法",
        ["候補から選ぶ", "自由入力"]
    )

    if goal_type == "候補から選ぶ":
        monthly_goal = st.selectbox(
            "月間収益目標",
            MONTHLY_GOALS,
            index=MONTHLY_GOALS.index(current_goal) if current_goal in MONTHLY_GOALS else 4,
            format_func=lambda x: f"{x:,} 円"
        )
    else:
        monthly_goal = st.number_input(
            "月間収益目標",
            min_value=0,
            value=current_goal,
            step=1000
        )

    if st.button("目標を保存"):
        data["settings"]["monthly_goal"] = int(monthly_goal)
        save_data(data)
        st.success("目標を保存したよ。")
        st.rerun()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今日の活動・成果を記録")

    log_date = st.date_input(
        "日付",
        value=date.today()
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    action = st.selectbox(
        "活動内容",
        ACTIONS
    )

    title = st.text_input(
        "タイトル",
        placeholder="例：note投稿 / アプリ改善 / ココナラ出品"
    )

    income = st.number_input(
        "収益",
        min_value=0,
        value=0,
        step=100
    )

    views = st.number_input(
        "閲覧数・PV",
        min_value=0,
        value=0,
        step=10
    )

    sales = st.number_input(
        "販売数・DL数",
        min_value=0,
        value=0,
        step=1
    )

    memo = st.text_area(
        "メモ",
        height=100,
        placeholder="例：サムネ変更 / 説明文改善 / 初購入あり"
    )

    favorite = st.checkbox("⭐ 大事な活動")

    if st.button("📈 記録する", type="primary"):
        if not title.strip():
            st.warning("タイトルだけは入れてね。")
        else:
            item = {
                "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": log_date.isoformat(),
                "category": category,
                "action": action,
                "title": title.strip(),
                "income": int(income),
                "views": int(views),
                "sales": int(sales),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["logs"].append(item)
            save_data(data)

            st.success("収益化チャレンジを記録したよ。")
            st.rerun()

with right:
    st.subheader("今月の進捗")

    df = to_df(data)
    goal = int(data["settings"].get("monthly_goal", 50000))

    if df.empty:
        st.info("まだ記録がないよ。")
    else:
        month = current_month()
        month_df = df[df["month"] == month]

        month_income = int(month_df["income"].sum()) if not month_df.empty else 0
        total_income = int(df["income"].sum())
        month_actions = len(month_df)
        total_actions = len(df)

        c1, c2 = st.columns(2)

        with c1:
            st.metric("今月収益", yen(month_income))
            st.metric("累計収益", yen(total_income))

        with c2:
            st.metric("今月活動数", month_actions)
            st.metric("累計活動数", total_actions)

        if goal > 0:
            rate = min(month_income / goal, 1.0)
            st.progress(rate)
            st.info(f"月間目標 {yen(goal)} まで、あと {yen(max(goal - month_income, 0))}")

        st.divider()

        if not month_df.empty:
            st.subheader("今月カテゴリ別")
            cat = month_df.groupby("category")["income"].sum().reset_index()
            cat = cat.sort_values("income", ascending=False)
            st.dataframe(cat, use_container_width=True, height=220)

st.divider()
st.subheader("活動履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="タイトル・メモ")

    with col_b:
        category_filter = st.selectbox("カテゴリで絞る", ["すべて"] + CATEGORIES)

    with col_c:
        action_filter = st.selectbox("活動内容で絞る", ["すべて"] + ACTIONS)

    month_filter = st.text_input(
        "月で絞る",
        value="",
        placeholder="例：2026-06"
    )

    fav_only = st.checkbox("⭐ 大事な活動だけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if action_filter != "すべて":
        view = view[view["action"] == action_filter]

    if month_filter.strip():
        view = view[view["month"] == month_filter.strip()]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "category", "action", "title", "income", "views", "sales", "favorite", "memo"]],
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
            row["id"]: f"{row['date']} / {row['category']} / {row['title']} / {yen(row['income'])}"
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
            st.write(f"活動：{item['action']}")
            st.write(f"収益：{yen(item.get('income', 0))}")
            st.write(f"閲覧数：{item.get('views', 0)}")
            st.write(f"販売数/DL数：{item.get('sales', 0)}")

            if item.get("memo"):
                st.info(item["memo"])

            c1, c2, c3 = st.columns(3)

            with c1:
                new_income = st.number_input(
                    "収益を更新",
                    min_value=0,
                    value=int(item.get("income", 0)),
                    step=100,
                    key=f"income_{item['id']}"
                )

            with c2:
                new_views = st.number_input(
                    "閲覧数を更新",
                    min_value=0,
                    value=int(item.get("views", 0)),
                    step=10,
                    key=f"views_{item['id']}"
                )

            with c3:
                new_sales = st.number_input(
                    "販売数/DL数を更新",
                    min_value=0,
                    value=int(item.get("sales", 0)),
                    step=1,
                    key=f"sales_{item['id']}"
                )

            new_fav = st.checkbox(
                "⭐ 大事な活動",
                value=bool(item.get("favorite", False)),
                key=f"fav_{item['id']}"
            )

            if st.button("📝 更新する"):
                item["income"] = int(new_income)
                item["views"] = int(new_views)
                item["sales"] = int(new_sales)
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
        file_name="day166_income_challenge.csv",
        mime="text/csv"
    )
