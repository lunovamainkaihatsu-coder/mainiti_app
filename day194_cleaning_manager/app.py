import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta

APP_TITLE = "Day194：掃除管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day194_cleaning_manager.json")

CATEGORIES = [
    "キッチン",
    "リビング",
    "トイレ",
    "お風呂",
    "洗面所",
    "寝室",
    "ベランダ",
    "窓",
    "エアコン",
    "玄関",
    "その他",
]

FREQUENCIES = [
    1,
    3,
    7,
    14,
    30,
    60,
    90,
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"tasks": [], "logs": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "tasks" not in data:
        data["tasks"] = []

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


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except:
        return date.today()


def next_clean_date(last_cleaned, frequency_days):
    last = parse_date(last_cleaned)
    return last + timedelta(days=int(frequency_days))


def days_until_next(last_cleaned, frequency_days):
    next_date = next_clean_date(last_cleaned, frequency_days)
    return (next_date - date.today()).days


def clean_status(days):
    if days < 0:
        return "⚫ 期限超過"

    if days == 0:
        return "🔴 今日掃除"

    if days <= 3:
        return "🟡 そろそろ"

    return "🟢 まだ大丈夫"


def to_task_df(data):
    rows = []

    for x in data["tasks"]:
        days = days_until_next(
            x.get("last_cleaned", today_str()),
            int(x.get("frequency_days", 7))
        )
        next_date = next_clean_date(
            x.get("last_cleaned", today_str()),
            int(x.get("frequency_days", 7))
        )

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "place": x["place"],
            "category": x["category"],
            "cleaning": x["cleaning"],
            "frequency_days": int(x.get("frequency_days", 7)),
            "last_cleaned": x.get("last_cleaned", today_str()),
            "next_clean": next_date.isoformat(),
            "days_left": days,
            "status": clean_status(days),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        status_order = {
            "⚫ 期限超過": 0,
            "🔴 今日掃除": 1,
            "🟡 そろそろ": 2,
            "🟢 まだ大丈夫": 3,
        }

        df["status_order"] = df["status"].map(status_order)
        df = df.sort_values(
            ["status_order", "next_clean", "favorite", "created_at"],
            ascending=[True, True, False, False]
        )

    return df


def to_log_df(data):
    rows = []

    for x in data["logs"]:
        rows.append({
            "created_at": x["created_at"],
            "date": x["date"],
            "place": x.get("place", ""),
            "category": x.get("category", ""),
            "cleaning": x.get("cleaning", ""),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_task(data, task_id):
    for x in data["tasks"]:
        if x["id"] == task_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 Day194：掃除管理アプリ")
st.caption("掃除場所・頻度・最終掃除日を管理して、掃除タイミングを見える化するアプリ。")

data = load_data()

tab1, tab2, tab3 = st.tabs(["🧹 掃除タスク", "✅ 今日掃除した", "📜 掃除履歴"])

with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("掃除タスクを登録")

        place = st.text_input(
            "場所",
            placeholder="例：キッチン / トイレ / お風呂"
        )

        category = st.selectbox(
            "カテゴリ",
            CATEGORIES
        )

        cleaning = st.text_input(
            "掃除内容",
            placeholder="例：シンク掃除 / 床拭き / 排水口掃除"
        )

        frequency_days = st.selectbox(
            "掃除頻度（日ごと）",
            FREQUENCIES,
            index=2,
            format_func=lambda x: f"{x}日ごと"
        )

        last_cleaned = st.date_input(
            "最終掃除日",
            value=date.today()
        )

        memo = st.text_area(
            "メモ",
            height=90,
            placeholder="例：週末にやる / 洗剤を使う / 家族担当"
        )

        favorite = st.checkbox("⭐ 重要な掃除")

        next_date = last_cleaned + timedelta(days=int(frequency_days))
        st.info(f"次回掃除予定：{next_date.isoformat()}")

        if st.button("🧹 掃除タスクを登録", type="primary"):
            if not place.strip():
                st.warning("場所を入れてね。")
            elif not cleaning.strip():
                st.warning("掃除内容を入れてね。")
            else:
                item = {
                    "id": f"clean_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "date": today_str(),
                    "place": place.strip(),
                    "category": category,
                    "cleaning": cleaning.strip(),
                    "frequency_days": int(frequency_days),
                    "last_cleaned": last_cleaned.isoformat(),
                    "memo": memo.strip(),
                    "favorite": favorite,
                }

                data["tasks"].append(item)
                save_data(data)

                st.success("掃除タスクを登録したよ。")
                st.rerun()

    with right:
        st.subheader("掃除ステータス")

        df = to_task_df(data)

        if df.empty:
            st.info("まだ掃除タスクが登録されていないよ。")
        else:
            overdue = len(df[df["status"] == "⚫ 期限超過"])
            today_count = len(df[df["status"] == "🔴 今日掃除"])
            soon = len(df[df["status"] == "🟡 そろそろ"])
            ok = len(df[df["status"] == "🟢 まだ大丈夫"])

            c1, c2 = st.columns(2)

            with c1:
                st.metric("掃除タスク", len(df))
                st.metric("期限超過", overdue)

            with c2:
                st.metric("今日掃除", today_count)
                st.metric("そろそろ", soon)

            st.metric("まだ大丈夫", ok)

            st.divider()

            st.subheader("優先して掃除する場所")

            urgent = df[df["status"].isin(["⚫ 期限超過", "🔴 今日掃除", "🟡 そろそろ"])]

            if urgent.empty:
                st.success("急ぎの掃除はなさそう。いい感じ！")
            else:
                st.dataframe(
                    urgent[[
                        "place",
                        "category",
                        "cleaning",
                        "last_cleaned",
                        "next_clean",
                        "days_left",
                        "status",
                        "memo",
                    ]],
                    use_container_width=True,
                    height=240
                )

    st.divider()
    st.subheader("掃除タスク一覧")

    df = to_task_df(data)

    if df.empty:
        st.write("まだ一覧が空だよ。")
    else:
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            keyword = st.text_input(
                "検索",
                placeholder="場所・掃除内容・メモ"
            )

        with col_b:
            category_filter = st.selectbox(
                "カテゴリで絞る",
                ["すべて"] + CATEGORIES
            )

        with col_c:
            status_filter = st.selectbox(
                "状態で絞る",
                ["すべて", "⚫ 期限超過", "🔴 今日掃除", "🟡 そろそろ", "🟢 まだ大丈夫"]
            )

        fav_only = st.checkbox("⭐ 重要な掃除だけ")

        view = df.copy()

        if keyword.strip():
            q = keyword.strip()
            view = view[
                view["place"].fillna("").str.contains(q, case=False, na=False)
                | view["cleaning"].fillna("").str.contains(q, case=False, na=False)
                | view["memo"].fillna("").str.contains(q, case=False, na=False)
            ]

        if category_filter != "すべて":
            view = view[view["category"] == category_filter]

        if status_filter != "すべて":
            view = view[view["status"] == status_filter]

        if fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(
            view[[
                "place",
                "category",
                "cleaning",
                "frequency_days",
                "last_cleaned",
                "next_clean",
                "days_left",
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
            st.write("条件に合う掃除タスクがないよ。")
        else:
            selected_id = st.selectbox(
                "掃除タスクを選ぶ",
                view["id"].tolist(),
                format_func=lambda x: f"{find_task(data, x)['place']} / {find_task(data, x)['cleaning']}"
            )

            task = find_task(data, selected_id)

            if task:
                days = days_until_next(
                    task.get("last_cleaned", today_str()),
                    int(task.get("frequency_days", 7))
                )

                st.markdown(f"## {task['place']}")
                st.write(f"カテゴリ：{task['category']}")
                st.write(f"掃除内容：{task['cleaning']}")
                st.write(f"頻度：{task['frequency_days']}日ごと")
                st.write(f"最終掃除日：{task['last_cleaned']}")
                st.info(clean_status(days))

                if task.get("memo"):
                    st.write(task["memo"])

                c1, c2, c3 = st.columns(3)

                with c1:
                    new_frequency = st.number_input(
                        "頻度更新（日）",
                        min_value=1,
                        value=int(task.get("frequency_days", 7)),
                        step=1,
                        key=f"freq_{task['id']}"
                    )

                with c2:
                    new_last = st.date_input(
                        "最終掃除日更新",
                        value=parse_date(task.get("last_cleaned", today_str())),
                        key=f"last_{task['id']}"
                    )

                with c3:
                    new_favorite = st.checkbox(
                        "⭐ 重要",
                        value=bool(task.get("favorite", False)),
                        key=f"fav_{task['id']}"
                    )

                if st.button("📝 更新する"):
                    task["frequency_days"] = int(new_frequency)
                    task["last_cleaned"] = new_last.isoformat()
                    task["favorite"] = new_favorite
                    task["updated_at"] = now_str()

                    save_data(data)

                    st.success("掃除タスクを更新したよ。")
                    st.rerun()

                if st.button("🗑️ この掃除タスクを削除", type="secondary"):
                    data["tasks"] = [
                        x for x in data["tasks"]
                        if x["id"] != selected_id
                    ]

                    save_data(data)
                    st.warning("掃除タスクを削除したよ。")
                    st.rerun()

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ 掃除タスクCSVダウンロード",
            data=csv,
            file_name="day194_cleaning_tasks.csv",
            mime="text/csv"
        )

with tab2:
    st.subheader("今日掃除した記録")

    df = to_task_df(data)

    if df.empty:
        st.info("まず掃除タスクを登録してね。")
    else:
        selected_id = st.selectbox(
            "掃除したタスク",
            df["id"].tolist(),
            format_func=lambda x: f"{find_task(data, x)['place']} / {find_task(data, x)['cleaning']}",
            key="done_task"
        )

        task = find_task(data, selected_id)

        if task:
            done_date = st.date_input(
                "掃除した日",
                value=date.today()
            )

            memo = st.text_area(
                "掃除メモ",
                height=90,
                placeholder="例：しっかり掃除できた / 次回は洗剤を買う"
            )

            if st.button("✅ 今日掃除した", type="primary"):
                old_last = task.get("last_cleaned", today_str())
                task["last_cleaned"] = done_date.isoformat()
                task["updated_at"] = now_str()

                log = {
                    "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "date": done_date.isoformat(),
                    "task_id": task["id"],
                    "place": task["place"],
                    "category": task["category"],
                    "cleaning": task["cleaning"],
                    "old_last_cleaned": old_last,
                    "memo": memo.strip(),
                }

                data["logs"].append(log)
                save_data(data)

                st.success("掃除完了を記録したよ。")
                st.rerun()

with tab3:
    st.subheader("掃除履歴")

    log_df = to_log_df(data)

    if log_df.empty:
        st.write("まだ掃除履歴がないよ。")
    else:
        st.dataframe(
            log_df[[
                "date",
                "place",
                "category",
                "cleaning",
                "memo",
            ]],
            use_container_width=True,
            height=320
        )

        csv = log_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ 掃除履歴CSVダウンロード",
            data=csv,
            file_name="day194_cleaning_logs.csv",
            mime="text/csv"
        )
