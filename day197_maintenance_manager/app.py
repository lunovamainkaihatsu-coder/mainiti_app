import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


APP_TITLE = "Day197：定期メンテナンス管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day197_maintenance_manager.json"
)

CATEGORIES = [
    "家電",
    "車",
    "パソコン",
    "キッチン",
    "洗面所",
    "消耗品",
    "健康",
    "家具",
    "住宅設備",
    "その他",
]

LOCATIONS = [
    "リビング",
    "寝室",
    "キッチン",
    "洗面所",
    "お風呂",
    "玄関",
    "書斎",
    "車",
    "屋外",
    "その他",
]

INTERVAL_PRESETS = [
    7,
    14,
    30,
    60,
    90,
    180,
    365,
]

STATUS_FILTERS = [
    "すべて",
    "🔴 期限超過",
    "🟠 今日",
    "🟡 7日以内",
    "🟢 まだ大丈夫",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "tasks": [],
                    "logs": [],
                },
                file,
                ensure_ascii=False,
                indent=2,
            )


def load_data():
    ensure_storage()

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        data = {
            "tasks": [],
            "logs": [],
        }

    data.setdefault("tasks", [])
    data.setdefault("logs", [])

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_text():
    return date.today().isoformat()


def parse_date(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()
    except (TypeError, ValueError):
        return date.today()


def next_maintenance_date(last_date, interval_days):
    return parse_date(last_date) + timedelta(
        days=int(interval_days)
    )


def days_until_next(last_date, interval_days):
    next_date = next_maintenance_date(
        last_date,
        interval_days,
    )

    return (next_date - date.today()).days


def maintenance_status(days):
    if days < 0:
        return "🔴 期限超過"

    if days == 0:
        return "🟠 今日"

    if days <= 7:
        return "🟡 7日以内"

    return "🟢 まだ大丈夫"


def urgency_text(days):
    if days < 0:
        return f"{abs(days)}日超過"

    if days == 0:
        return "今日実施"

    return f"あと{days}日"


def find_task(data, task_id):
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task

    return None


def find_log(data, log_id):
    for log in data["logs"]:
        if log["id"] == log_id:
            return log

    return None


def to_task_df(data):
    rows = []

    for task in data["tasks"]:
        interval_days = int(
            task.get("interval_days", 30)
        )

        last_date = task.get(
            "last_maintenance",
            today_text(),
        )

        next_date = next_maintenance_date(
            last_date,
            interval_days,
        )

        days = days_until_next(
            last_date,
            interval_days,
        )

        rows.append(
            {
                "id": task["id"],
                "created_at": task["created_at"],
                "name": task["name"],
                "category": task["category"],
                "location": task["location"],
                "interval_days": interval_days,
                "last_maintenance": last_date,
                "next_maintenance": next_date.isoformat(),
                "days_left": days,
                "status": maintenance_status(days),
                "urgency": urgency_text(days),
                "favorite": bool(
                    task.get("favorite", False)
                ),
                "memo": task.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        status_order = {
            "🔴 期限超過": 0,
            "🟠 今日": 1,
            "🟡 7日以内": 2,
            "🟢 まだ大丈夫": 3,
        }

        df["status_order"] = (
            df["status"]
            .map(status_order)
            .fillna(9)
        )

        df = df.sort_values(
            [
                "status_order",
                "days_left",
                "favorite",
                "created_at",
            ],
            ascending=[
                True,
                True,
                False,
                False,
            ],
        )

    return df


def to_log_df(data):
    rows = []

    for log in data["logs"]:
        rows.append(
            {
                "id": log["id"],
                "created_at": log["created_at"],
                "date": log["date"],
                "task_name": log["task_name"],
                "category": log.get(
                    "category",
                    "",
                ),
                "location": log.get(
                    "location",
                    "",
                ),
                "memo": log.get(
                    "memo",
                    "",
                ),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(
            "created_at",
            ascending=False,
        )

    return df


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 Day197：定期メンテナンス管理アプリ")
st.caption(
    "家電・車・PC・消耗品などの交換日や点検日を管理するアプリ。"
)

data = load_data()

tab1, tab2, tab3 = st.tabs(
    [
        "🔧 メンテナンス管理",
        "✅ 完了記録",
        "📜 履歴",
    ]
)

with tab1:
    left, right = st.columns(
        [1, 1],
        gap="large",
    )

    with left:
        st.subheader("メンテナンス項目を登録")

        name = st.text_input(
            "項目名",
            placeholder=(
                "例：エアコンフィルター交換"
                " / PC内部清掃 / 歯ブラシ交換"
            ),
        )

        category = st.selectbox(
            "カテゴリ",
            CATEGORIES,
        )

        location = st.selectbox(
            "場所",
            LOCATIONS,
        )

        use_preset = st.checkbox(
            "よく使う間隔から選ぶ",
            value=True,
        )

        if use_preset:
            interval_days = st.selectbox(
                "メンテナンス間隔",
                INTERVAL_PRESETS,
                index=2,
                format_func=lambda value: (
                    f"{value}日ごと"
                ),
            )
        else:
            interval_days = st.number_input(
                "メンテナンス間隔（日）",
                min_value=1,
                max_value=3650,
                value=30,
                step=1,
            )

        last_maintenance = st.date_input(
            "最終実施日",
            value=date.today(),
        )

        memo = st.text_area(
            "メモ",
            height=90,
            placeholder=(
                "例：交換部品はAmazonで購入"
                " / 作業前に電源を切る"
            ),
        )

        favorite = st.checkbox(
            "⭐ 重要なメンテナンス"
        )

        preview_next = (
            last_maintenance
            + timedelta(
                days=int(interval_days)
            )
        )

        preview_days = (
            preview_next - date.today()
        ).days

        st.info(
            f"次回予定：{preview_next.isoformat()} "
            f"／ {urgency_text(preview_days)}"
        )

        if st.button(
            "🔧 項目を登録",
            type="primary",
        ):
            if not name.strip():
                st.warning(
                    "項目名を入れてね。"
                )
            else:
                task = {
                    "id": (
                        "maintenance_"
                        + datetime.now().strftime(
                            "%Y%m%d%H%M%S%f"
                        )
                    ),
                    "created_at": now_text(),
                    "name": name.strip(),
                    "category": category,
                    "location": location,
                    "interval_days": int(
                        interval_days
                    ),
                    "last_maintenance": (
                        last_maintenance.isoformat()
                    ),
                    "memo": memo.strip(),
                    "favorite": favorite,
                }

                data["tasks"].append(task)
                save_data(data)

                st.success(
                    "メンテナンス項目を登録したよ。"
                )
                st.rerun()

    with right:
        st.subheader(
            "メンテナンスダッシュボード"
        )

        df = to_task_df(data)

        if df.empty:
            st.info(
                "まだ項目が登録されていないよ。"
            )
        else:
            overdue = len(
                df[
                    df["status"]
                    == "🔴 期限超過"
                ]
            )

            today_count = len(
                df[
                    df["status"]
                    == "🟠 今日"
                ]
            )

            within_week = len(
                df[
                    df["status"]
                    == "🟡 7日以内"
                ]
            )

            safe = len(
                df[
                    df["status"]
                    == "🟢 まだ大丈夫"
                ]
            )

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "登録項目",
                    len(df),
                )

                st.metric(
                    "期限超過",
                    overdue,
                )

            with c2:
                st.metric(
                    "今日",
                    today_count,
                )

                st.metric(
                    "7日以内",
                    within_week,
                )

            st.metric(
                "まだ大丈夫",
                safe,
            )

            st.divider()
            st.subheader(
                "優先して実施する項目"
            )

            urgent = df[
                df["status"].isin(
                    [
                        "🔴 期限超過",
                        "🟠 今日",
                        "🟡 7日以内",
                    ]
                )
            ]

            if urgent.empty:
                st.success(
                    "急ぎのメンテナンスはなさそう。"
                )
            else:
                st.dataframe(
                    urgent[
                        [
                            "name",
                            "category",
                            "location",
                            "next_maintenance",
                            "urgency",
                            "status",
                            "memo",
                        ]
                    ],
                    use_container_width=True,
                    height=260,
                )

    st.divider()
    st.subheader(
        "メンテナンス一覧"
    )

    df = to_task_df(data)

    if df.empty:
        st.write(
            "まだ一覧が空だよ。"
        )
    else:
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            keyword = st.text_input(
                "検索",
                placeholder=(
                    "項目名・場所・メモ"
                ),
            )

        with col_b:
            category_filter = st.selectbox(
                "カテゴリで絞る",
                ["すべて"] + CATEGORIES,
            )

        with col_c:
            status_filter = st.selectbox(
                "状態で絞る",
                STATUS_FILTERS,
            )

        location_filter = st.selectbox(
            "場所で絞る",
            ["すべて"] + LOCATIONS,
        )

        favorite_only = st.checkbox(
            "⭐ 重要項目だけ表示"
        )

        view = df.copy()

        if keyword.strip():
            query = keyword.strip()

            view = view[
                view["name"]
                .fillna("")
                .str.contains(
                    query,
                    case=False,
                    na=False,
                )
                | view["location"]
                .fillna("")
                .str.contains(
                    query,
                    case=False,
                    na=False,
                )
                | view["memo"]
                .fillna("")
                .str.contains(
                    query,
                    case=False,
                    na=False,
                )
            ]

        if category_filter != "すべて":
            view = view[
                view["category"]
                == category_filter
            ]

        if status_filter != "すべて":
            view = view[
                view["status"]
                == status_filter
            ]

        if location_filter != "すべて":
            view = view[
                view["location"]
                == location_filter
            ]

        if favorite_only:
            view = view[
                view["favorite"] == True
            ]

        st.dataframe(
            view[
                [
                    "name",
                    "category",
                    "location",
                    "interval_days",
                    "last_maintenance",
                    "next_maintenance",
                    "days_left",
                    "urgency",
                    "status",
                    "favorite",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=340,
        )

        st.divider()
        st.subheader(
            "詳細・更新"
        )

        if view.empty:
            st.write(
                "条件に合う項目がないよ。"
            )
        else:
            selected_id = st.selectbox(
                "項目を選ぶ",
                view["id"].tolist(),
                format_func=lambda task_id: (
                    f"{find_task(data, task_id)['name']} "
                    f"/ "
                    f"{find_task(data, task_id)['location']}"
                ),
            )

            task = find_task(
                data,
                selected_id,
            )

            if task:
                days = days_until_next(
                    task.get(
                        "last_maintenance",
                        today_text(),
                    ),
                    task.get(
                        "interval_days",
                        30,
                    ),
                )

                next_date = next_maintenance_date(
                    task.get(
                        "last_maintenance",
                        today_text(),
                    ),
                    task.get(
                        "interval_days",
                        30,
                    ),
                )

                st.markdown(
                    f"## {task['name']}"
                )

                st.write(
                    f"カテゴリ："
                    f"{task['category']}"
                )

                st.write(
                    f"場所："
                    f"{task['location']}"
                )

                st.write(
                    f"実施間隔："
                    f"{task['interval_days']}日"
                )

                st.write(
                    f"最終実施日："
                    f"{task['last_maintenance']}"
                )

                st.write(
                    f"次回予定："
                    f"{next_date.isoformat()}"
                )

                st.info(
                    f"{maintenance_status(days)} "
                    f"／ {urgency_text(days)}"
                )

                if task.get("memo"):
                    st.write(
                        task["memo"]
                    )

                c1, c2 = st.columns(2)

                with c1:
                    new_interval = st.number_input(
                        "間隔更新（日）",
                        min_value=1,
                        max_value=3650,
                        value=int(
                            task.get(
                                "interval_days",
                                30,
                            )
                        ),
                        step=1,
                        key=(
                            f"interval_"
                            f"{task['id']}"
                        ),
                    )

                with c2:
                    new_last_date = st.date_input(
                        "最終実施日更新",
                        value=parse_date(
                            task.get(
                                "last_maintenance",
                                today_text(),
                            )
                        ),
                        key=(
                            f"last_date_"
                            f"{task['id']}"
                        ),
                    )

                new_memo = st.text_area(
                    "メモ更新",
                    value=task.get(
                        "memo",
                        "",
                    ),
                    key=(
                        f"memo_"
                        f"{task['id']}"
                    ),
                )

                new_favorite = st.checkbox(
                    "⭐ 重要な項目",
                    value=bool(
                        task.get(
                            "favorite",
                            False,
                        )
                    ),
                    key=(
                        f"favorite_"
                        f"{task['id']}"
                    ),
                )

                if st.button(
                    "📝 項目を更新"
                ):
                    task["interval_days"] = int(
                        new_interval
                    )

                    task["last_maintenance"] = (
                        new_last_date.isoformat()
                    )

                    task["memo"] = (
                        new_memo.strip()
                    )

                    task["favorite"] = (
                        new_favorite
                    )

                    task["updated_at"] = (
                        now_text()
                    )

                    save_data(data)

                    st.success(
                        "項目を更新したよ。"
                    )
                    st.rerun()

                if st.button(
                    "🗑️ この項目を削除",
                    type="secondary",
                ):
                    data["tasks"] = [
                        item
                        for item in data["tasks"]
                        if item["id"]
                        != selected_id
                    ]

                    data["logs"] = [
                        item
                        for item in data["logs"]
                        if item.get("task_id")
                        != selected_id
                    ]

                    save_data(data)

                    st.warning(
                        "項目を削除したよ。"
                    )
                    st.rerun()

        csv = df.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(
            "⬇️ メンテナンス一覧CSV",
            data=csv,
            file_name=(
                "day197_maintenance_tasks.csv"
            ),
            mime="text/csv",
        )

with tab2:
    st.subheader(
        "メンテナンス完了を記録"
    )

    df = to_task_df(data)

    if df.empty:
        st.info(
            "先にメンテナンス項目を登録してね。"
        )
    else:
        selected_id = st.selectbox(
            "完了した項目",
            df["id"].tolist(),
            format_func=lambda task_id: (
                f"{find_task(data, task_id)['name']} "
                f"/ "
                f"{find_task(data, task_id)['location']}"
            ),
            key="completed_task",
        )

        task = find_task(
            data,
            selected_id,
        )

        completed_date = st.date_input(
            "実施日",
            value=date.today(),
            key="completed_date",
        )

        completed_memo = st.text_area(
            "作業メモ",
            height=100,
            placeholder=(
                "例：フィルターを水洗いした"
                " / 新品に交換した"
            ),
        )

        if task:
            st.markdown(
                f"## {task['name']}"
            )

            st.write(
                f"現在の最終実施日："
                f"{task['last_maintenance']}"
            )

            future_date = (
                completed_date
                + timedelta(
                    days=int(
                        task.get(
                            "interval_days",
                            30,
                        )
                    )
                )
            )

            st.info(
                f"今回完了後の次回予定："
                f"{future_date.isoformat()}"
            )

        if st.button(
            "✅ メンテナンス完了",
            type="primary",
        ):
            old_date = task.get(
                "last_maintenance",
                today_text(),
            )

            task["last_maintenance"] = (
                completed_date.isoformat()
            )

            task["updated_at"] = now_text()

            log = {
                "id": (
                    "log_"
                    + datetime.now().strftime(
                        "%Y%m%d%H%M%S%f"
                    )
                ),
                "created_at": now_text(),
                "date": completed_date.isoformat(),
                "task_id": task["id"],
                "task_name": task["name"],
                "category": task["category"],
                "location": task["location"],
                "old_last_date": old_date,
                "memo": completed_memo.strip(),
            }

            data["logs"].append(log)
            save_data(data)

            st.success(
                "メンテナンス完了を記録したよ。"
            )
            st.rerun()

with tab3:
    st.subheader(
        "メンテナンス履歴"
    )

    log_df = to_log_df(data)

    if log_df.empty:
        st.write(
            "まだ履歴がないよ。"
        )
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            history_keyword = st.text_input(
                "履歴検索",
                placeholder=(
                    "項目名・メモ"
                ),
            )

        with col_b:
            history_category = st.selectbox(
                "履歴カテゴリ",
                ["すべて"] + CATEGORIES,
            )

        history_view = log_df.copy()

        if history_keyword.strip():
            query = (
                history_keyword.strip()
            )

            history_view = history_view[
                history_view["task_name"]
                .fillna("")
                .str.contains(
                    query,
                    case=False,
                    na=False,
                )
                | history_view["memo"]
                .fillna("")
                .str.contains(
                    query,
                    case=False,
                    na=False,
                )
            ]

        if history_category != "すべて":
            history_view = history_view[
                history_view["category"]
                == history_category
            ]

        st.dataframe(
            history_view[
                [
                    "date",
                    "task_name",
                    "category",
                    "location",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=320,
        )

        st.divider()
        st.subheader(
            "履歴の削除"
        )

        if not history_view.empty:
            selected_log_id = st.selectbox(
                "削除する履歴",
                history_view["id"].tolist(),
                format_func=lambda log_id: (
                    f"{find_log(data, log_id)['date']} "
                    f"/ "
                    f"{find_log(data, log_id)['task_name']}"
                ),
            )

            if st.button(
                "🗑️ この履歴を削除",
                type="secondary",
            ):
                data["logs"] = [
                    item
                    for item in data["logs"]
                    if item["id"]
                    != selected_log_id
                ]

                save_data(data)

                st.warning(
                    "履歴を削除したよ。"
                )
                st.rerun()

        history_csv = log_df.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(
            "⬇️ メンテナンス履歴CSV",
            data=history_csv,
            file_name=(
                "day197_maintenance_logs.csv"
            ),
            mime="text/csv",
        )
