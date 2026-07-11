import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


APP_TITLE = "Day195：ゴミ出し管理アプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day195_garbage_schedule.json")

GARBAGE_TYPES = [
    "🔥 可燃ごみ",
    "🚯 不燃ごみ",
    "♻️ 資源ごみ",
    "🥫 缶・ビン",
    "🧴 ペットボトル",
    "📄 古紙・段ボール",
    "🔋 電池・有害ごみ",
    "📦 粗大ごみ",
    "🗑️ その他",
]

WEEKDAYS = [
    "月曜日",
    "火曜日",
    "水曜日",
    "木曜日",
    "金曜日",
    "土曜日",
    "日曜日",
]

WEEKDAY_NUMBERS = {
    "月曜日": 0,
    "火曜日": 1,
    "水曜日": 2,
    "木曜日": 3,
    "金曜日": 4,
    "土曜日": 5,
    "日曜日": 6,
}

FREQUENCIES = [
    "毎週",
    "隔週",
    "第1週",
    "第2週",
    "第3週",
    "第4週",
    "毎月指定日",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(
                {"schedules": [], "logs": []},
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
        data = {"schedules": [], "logs": []}

    data.setdefault("schedules", [])
    data.setdefault("logs", [])

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_text():
    return date.today().isoformat()


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


def week_number_in_month(target_date):
    return ((target_date.day - 1) // 7) + 1


def matches_schedule(schedule, target_date):
    frequency = schedule.get("frequency", "毎週")

    if frequency == "毎月指定日":
        return target_date.day == int(schedule.get("month_day", 1))

    weekday_numbers = [
        WEEKDAY_NUMBERS[day]
        for day in schedule.get("weekdays", [])
        if day in WEEKDAY_NUMBERS
    ]

    if target_date.weekday() not in weekday_numbers:
        return False

    if frequency == "毎週":
        return True

    if frequency == "隔週":
        base_date = parse_date(schedule.get("base_date", today_text()))
        difference = (target_date - base_date).days

        return difference >= 0 and (difference // 7) % 2 == 0

    target_week = {
        "第1週": 1,
        "第2週": 2,
        "第3週": 3,
        "第4週": 4,
    }.get(frequency)

    if target_week is not None:
        return week_number_in_month(target_date) == target_week

    return False


def next_collection_date(schedule, start_date=None, search_days=370):
    start = start_date or date.today()

    for offset in range(search_days + 1):
        target = start + timedelta(days=offset)

        if matches_schedule(schedule, target):
            return target

    return None


def next_label(days):
    if days is None:
        return "予定なし"

    if days == 0:
        return "🔴 今日"

    if days == 1:
        return "🟠 明日"

    if days <= 7:
        return f"🟡 あと{days}日"

    return f"🟢 あと{days}日"


def schedule_text(schedule):
    frequency = schedule.get("frequency", "毎週")

    if frequency == "毎月指定日":
        return f"毎月{schedule.get('month_day', 1)}日"

    weekdays = "・".join(schedule.get("weekdays", []))

    if frequency == "隔週":
        return f"隔週 {weekdays}"

    if frequency in ["第1週", "第2週", "第3週", "第4週"]:
        return f"{frequency} {weekdays}"

    return f"毎週 {weekdays}"


def to_schedule_df(data):
    rows = []

    for item in data["schedules"]:
        next_date = next_collection_date(item)
        days = (next_date - date.today()).days if next_date else None

        rows.append(
            {
                "id": item["id"],
                "created_at": item["created_at"],
                "garbage_type": item["garbage_type"],
                "schedule": schedule_text(item),
                "next_date": next_date.isoformat() if next_date else "",
                "days_left": days if days is not None else "",
                "status": next_label(days),
                "favorite": bool(item.get("favorite", False)),
                "memo": item.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df["sort_days"] = pd.to_numeric(
            df["days_left"],
            errors="coerce",
        ).fillna(9999)

        df = df.sort_values(
            ["sort_days", "favorite", "created_at"],
            ascending=[True, False, False],
        )

    return df


def to_log_df(data):
    rows = []

    for item in data["logs"]:
        rows.append(
            {
                "created_at": item["created_at"],
                "date": item["date"],
                "garbage_type": item["garbage_type"],
                "memo": item.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_schedule(data, schedule_id):
    for item in data["schedules"]:
        if item["id"] == schedule_id:
            return item

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🗑️",
    layout="wide",
)

st.title("🗑️ Day195：ゴミ出し管理アプリ")
st.caption("ゴミの種類と回収日を登録して、今日・明日・今週の予定を確認するアプリ。")

data = load_data()

tab1, tab2, tab3 = st.tabs(
    [
        "🗓️ 回収予定",
        "✅ ゴミを出した",
        "📜 ゴミ出し履歴",
    ]
)

with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("回収予定を登録")

        garbage_type = st.selectbox(
            "ゴミの種類",
            GARBAGE_TYPES,
        )

        frequency = st.selectbox(
            "回収頻度",
            FREQUENCIES,
        )

        weekdays = []
        month_day = 1
        base_date = date.today()

        if frequency == "毎月指定日":
            month_day = st.number_input(
                "毎月の回収日",
                min_value=1,
                max_value=31,
                value=1,
                step=1,
            )
        else:
            weekdays = st.multiselect(
                "回収曜日",
                WEEKDAYS,
                default=["月曜日"],
            )

            if frequency == "隔週":
                base_date = st.date_input(
                    "隔週計算の基準日",
                    value=date.today(),
                )

        memo = st.text_area(
            "メモ",
            height=90,
            placeholder="例：朝8時まで / 指定袋を使う / 集積所は玄関前",
        )

        favorite = st.checkbox("⭐ よく確認するゴミ")

        preview_schedule = {
            "frequency": frequency,
            "weekdays": weekdays,
            "month_day": int(month_day),
            "base_date": base_date.isoformat(),
        }

        preview_date = next_collection_date(preview_schedule)

        if preview_date:
            preview_days = (preview_date - date.today()).days
            st.info(
                f"次回予定：{preview_date.isoformat()} "
                f"／ {next_label(preview_days)}"
            )
        else:
            st.warning("次回予定を計算できないよ。曜日などを確認してね。")

        if st.button("🗑️ 回収予定を登録", type="primary"):
            if frequency != "毎月指定日" and not weekdays:
                st.warning("回収曜日を1つ以上選んでね。")
            else:
                item = {
                    "id": f"garbage_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_text(),
                    "garbage_type": garbage_type,
                    "frequency": frequency,
                    "weekdays": weekdays,
                    "month_day": int(month_day),
                    "base_date": base_date.isoformat(),
                    "memo": memo.strip(),
                    "favorite": favorite,
                }

                data["schedules"].append(item)
                save_data(data)

                st.success("ゴミ出し予定を登録したよ。")
                st.rerun()

    with right:
        st.subheader("ゴミ出しダッシュボード")

        df = to_schedule_df(data)

        if df.empty:
            st.info("まだ回収予定が登録されていないよ。")
        else:
            today_count = len(df[df["days_left"] == 0])
            tomorrow_count = len(df[df["days_left"] == 1])

            numeric_days = pd.to_numeric(
                df["days_left"],
                errors="coerce",
            )

            week_count = len(
                df[
                    (numeric_days >= 0)
                    & (numeric_days <= 7)
                ]
            )

            c1, c2 = st.columns(2)

            with c1:
                st.metric("登録種類", len(df))
                st.metric("今日", today_count)

            with c2:
                st.metric("明日", tomorrow_count)
                st.metric("7日以内", week_count)

            st.divider()
            st.subheader("直近の回収予定")

            st.dataframe(
                df[
                    [
                        "garbage_type",
                        "schedule",
                        "next_date",
                        "status",
                        "memo",
                    ]
                ].head(8),
                use_container_width=True,
                height=260,
            )

    st.divider()
    st.subheader("回収予定一覧")

    df = to_schedule_df(data)

    if df.empty:
        st.write("まだ予定がないよ。")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            keyword = st.text_input(
                "検索",
                placeholder="ゴミの種類・メモ",
            )

        with col_b:
            garbage_filter = st.selectbox(
                "種類で絞る",
                ["すべて"] + GARBAGE_TYPES,
            )

        fav_only = st.checkbox("⭐ よく確認するものだけ表示")

        view = df.copy()

        if keyword.strip():
            query = keyword.strip()

            view = view[
                view["garbage_type"].fillna("").str.contains(
                    query,
                    case=False,
                    na=False,
                )
                | view["memo"].fillna("").str.contains(
                    query,
                    case=False,
                    na=False,
                )
            ]

        if garbage_filter != "すべて":
            view = view[view["garbage_type"] == garbage_filter]

        if fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(
            view[
                [
                    "garbage_type",
                    "schedule",
                    "next_date",
                    "days_left",
                    "status",
                    "favorite",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=320,
        )

        st.divider()
        st.subheader("詳細・更新")

        if view.empty:
            st.write("条件に合う予定がないよ。")
        else:
            selected_id = st.selectbox(
                "予定を選ぶ",
                view["id"].tolist(),
                format_func=lambda schedule_id: (
                    f"{find_schedule(data, schedule_id)['garbage_type']} / "
                    f"{schedule_text(find_schedule(data, schedule_id))}"
                ),
            )

            selected = find_schedule(data, selected_id)

            if selected:
                next_date = next_collection_date(selected)
                days = (
                    (next_date - date.today()).days
                    if next_date
                    else None
                )

                st.markdown(f"## {selected['garbage_type']}")
                st.write(f"回収予定：{schedule_text(selected)}")
                st.write(
                    f"次回："
                    f"{next_date.isoformat() if next_date else '予定なし'}"
                )
                st.info(next_label(days))

                if selected.get("memo"):
                    st.write(selected["memo"])

                new_favorite = st.checkbox(
                    "⭐ よく確認する",
                    value=bool(selected.get("favorite", False)),
                    key=f"favorite_{selected['id']}",
                )

                new_memo = st.text_area(
                    "メモを更新",
                    value=selected.get("memo", ""),
                    key=f"memo_{selected['id']}",
                )

                if st.button("📝 更新する"):
                    selected["favorite"] = new_favorite
                    selected["memo"] = new_memo.strip()
                    selected["updated_at"] = now_text()

                    save_data(data)

                    st.success("予定を更新したよ。")
                    st.rerun()

                if st.button(
                    "🗑️ この予定を削除",
                    type="secondary",
                ):
                    data["schedules"] = [
                        item
                        for item in data["schedules"]
                        if item["id"] != selected_id
                    ]

                    save_data(data)

                    st.warning("予定を削除したよ。")
                    st.rerun()

        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ 回収予定CSVダウンロード",
            data=csv,
            file_name="day195_garbage_schedule.csv",
            mime="text/csv",
        )

with tab2:
    st.subheader("ゴミを出した記録")

    df = to_schedule_df(data)

    if df.empty:
        st.info("先に回収予定を登録してね。")
    else:
        selected_id = st.selectbox(
            "出したゴミ",
            df["id"].tolist(),
            format_func=lambda schedule_id: (
                f"{find_schedule(data, schedule_id)['garbage_type']} / "
                f"{schedule_text(find_schedule(data, schedule_id))}"
            ),
            key="completed_schedule",
        )

        selected = find_schedule(data, selected_id)

        completed_date = st.date_input(
            "ゴミを出した日",
            value=date.today(),
        )

        completed_memo = st.text_area(
            "メモ",
            height=90,
            placeholder="例：朝7時に出した / 袋を2つ出した",
        )

        if st.button("✅ ゴミを出した", type="primary"):
            log = {
                "id": f"log_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_text(),
                "date": completed_date.isoformat(),
                "schedule_id": selected["id"],
                "garbage_type": selected["garbage_type"],
                "memo": completed_memo.strip(),
            }

            data["logs"].append(log)
            save_data(data)

            st.success("ゴミ出しを記録したよ。")
            st.rerun()

with tab3:
    st.subheader("ゴミ出し履歴")

    log_df = to_log_df(data)

    if log_df.empty:
        st.write("まだゴミ出し履歴がないよ。")
    else:
        st.dataframe(
            log_df[
                [
                    "date",
                    "garbage_type",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=320,
        )

        csv = log_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ ゴミ出し履歴CSVダウンロード",
            data=csv,
            file_name="day195_garbage_logs.csv",
            mime="text/csv",
        )
