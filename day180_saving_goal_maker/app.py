import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day180：貯金目標メーカー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day180_saving_goal_maker.json")

CATEGORIES = [
    "引っ越し",
    "生活費",
    "投資",
    "旅行",
    "学習",
    "車",
    "家族",
    "LUNAPOCKET",
    "その他",
]

STATUS = [
    "進行中",
    "達成",
    "保留",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"goals": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "goals" not in data:
        data["goals"] = []

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
    return f"{int(round(value)):,} 円"


def days_between(start_date, target_date):
    diff = (target_date - start_date).days
    return max(diff, 1)


def calc_plan(target_amount, current_amount, target_date):
    today = date.today()
    days = days_between(today, target_date)
    remaining = max(target_amount - current_amount, 0)

    per_day = remaining / days
    per_week = per_day * 7
    per_month = per_day * 30

    progress = 0
    if target_amount > 0:
        progress = min(current_amount / target_amount, 1.0)

    return {
        "days": days,
        "remaining": remaining,
        "per_day": per_day,
        "per_week": per_week,
        "per_month": per_month,
        "progress": progress,
    }


def status_comment(progress, remaining):
    if remaining <= 0:
        return "目標達成！かなりいい感じ！"

    if progress >= 0.8:
        return "もう少しで達成。かなり近いよ。"

    if progress >= 0.5:
        return "半分以上進んでる。ここから仕上げていこう。"

    if progress >= 0.2:
        return "少しずつ積み上がってるよ。続ければ届く。"

    return "ここからスタート。小さく貯めれば大丈夫。"


def to_df(data):
    rows = []

    for x in data["goals"]:
        target_amount = int(x.get("target_amount", 0))
        current_amount = int(x.get("current_amount", 0))

        try:
            target_date = datetime.strptime(x["target_date"], "%Y-%m-%d").date()
        except:
            target_date = date.today()

        plan = calc_plan(target_amount, current_amount, target_date)

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "title": x["title"],
            "category": x["category"],
            "status": x.get("status", "進行中"),
            "target_amount": target_amount,
            "current_amount": current_amount,
            "remaining": int(plan["remaining"]),
            "target_date": x["target_date"],
            "days": int(plan["days"]),
            "per_day": int(round(plan["per_day"])),
            "per_week": int(round(plan["per_week"])),
            "per_month": int(round(plan["per_month"])),
            "progress_percent": round(plan["progress"] * 100, 1),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_goal(data, goal_id):
    for x in data["goals"]:
        if x["id"] == goal_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💰",
    layout="wide"
)

st.title("💰 Day180：貯金目標メーカー")
st.caption("目標金額・現在額・期限から、毎月・毎週・毎日いくら貯めればいいか計算するアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("貯金目標を作る")

    title = st.text_input(
        "目標名",
        placeholder="例：引っ越し資金 / 投資資金 / LUNAPOCKET開発費"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    target_amount = st.number_input(
        "目標金額",
        min_value=0,
        value=500000,
        step=10000
    )

    current_amount = st.number_input(
        "現在の貯金額",
        min_value=0,
        value=0,
        step=10000
    )

    target_date = st.date_input(
        "目標日",
        value=date.today().replace(year=date.today().year + 1)
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：毎月少しずつ積み立てる / ボーナスも入れる"
    )

    if st.button("💰 目標を保存", type="primary"):
        if not title.strip():
            st.warning("目標名を入れてね。")
        elif target_amount <= 0:
            st.warning("目標金額を入れてね。")
        else:
            item = {
                "id": f"saving_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "title": title.strip(),
                "category": category,
                "target_amount": int(target_amount),
                "current_amount": int(current_amount),
                "target_date": target_date.isoformat(),
                "status": status,
                "memo": memo.strip(),
            }

            data["goals"].append(item)
            save_data(data)

            st.success("貯金目標を保存したよ。")
            st.rerun()

with right:
    st.subheader("シミュレーション")

    plan = calc_plan(
        int(target_amount),
        int(current_amount),
        target_date
    )

    st.metric("あと必要", yen(plan["remaining"]))
    st.metric("残り日数", f"{plan['days']} 日")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("毎日", yen(plan["per_day"]))

    with c2:
        st.metric("毎週", yen(plan["per_week"]))

    with c3:
        st.metric("毎月", yen(plan["per_month"]))

    st.progress(plan["progress"])
    st.info(f"達成率：{round(plan['progress'] * 100, 1)}%")

    st.success(status_comment(plan["progress"], plan["remaining"]))

st.divider()
st.subheader("貯金目標一覧")

df = to_df(data)

if df.empty:
    st.write("まだ貯金目標がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="目標名・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        status_filter = st.selectbox(
            "状態で絞る",
            ["すべて"] + STATUS
        )

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["title"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    st.dataframe(
        view[[
            "title",
            "category",
            "status",
            "target_amount",
            "current_amount",
            "remaining",
            "target_date",
            "per_day",
            "per_week",
            "per_month",
            "progress_percent",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合う目標がないよ。")
    else:
        selected_id = st.selectbox(
            "目標を選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_goal(data, x)['title']} / {yen(find_goal(data, x)['target_amount'])}"
        )

        selected = find_goal(data, selected_id)

        if selected:
            st.markdown(f"## {selected['title']}")
            st.write(f"カテゴリ：{selected['category']}")
            st.write(f"目標金額：{yen(selected['target_amount'])}")
            st.write(f"現在額：{yen(selected['current_amount'])}")
            st.write(f"目標日：{selected['target_date']}")
            st.write(f"状態：{selected.get('status', '進行中')}")

            if selected.get("memo"):
                st.info(selected["memo"])

            c1, c2 = st.columns(2)

            with c1:
                new_current = st.number_input(
                    "現在額を更新",
                    min_value=0,
                    value=int(selected.get("current_amount", 0)),
                    step=10000,
                    key=f"current_{selected['id']}"
                )

            with c2:
                new_status = st.selectbox(
                    "状態を更新",
                    STATUS,
                    index=STATUS.index(selected.get("status", "進行中")),
                    key=f"status_{selected['id']}"
                )

            if st.button("📝 更新する"):
                selected["current_amount"] = int(new_current)
                selected["status"] = new_status
                selected["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ この目標を削除", type="secondary"):
                data["goals"] = [
                    x for x in data["goals"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day180_saving_goal_maker.csv",
        mime="text/csv"
    )
