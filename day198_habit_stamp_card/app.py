import calendar
import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


APP_TITLE = "Day198：習慣スタンプカード"
DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day198_habit_stamp_card.json",
)

CATEGORIES = [
    "健康",
    "運動",
    "勉強",
    "読書",
    "仕事",
    "開発",
    "家事",
    "メンタル",
    "お金",
    "その他",
]

ICONS = [
    "⭐",
    "💪",
    "📚",
    "🧘",
    "🚶",
    "💧",
    "💻",
    "🧹",
    "🌙",
    "🔥",
]

TARGET_TYPES = [
    "毎日",
    "週に指定回数",
    "月に指定回数",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "habits": [],
                    "stamps": [],
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
            "habits": [],
            "stamps": [],
        }

    data.setdefault("habits", [])
    data.setdefault("stamps", [])

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


def find_habit(data, habit_id):
    for habit in data["habits"]:
        if habit["id"] == habit_id:
            return habit

    return None


def find_stamp(data, stamp_id):
    for stamp in data["stamps"]:
        if stamp["id"] == stamp_id:
            return stamp

    return None


def get_habit_stamps(data, habit_id):
    return [
        stamp
        for stamp in data["stamps"]
        if stamp.get("habit_id") == habit_id
    ]


def has_stamp_on_date(data, habit_id, target_date):
    target_text = target_date.isoformat()

    return any(
        stamp.get("habit_id") == habit_id
        and stamp.get("date") == target_text
        for stamp in data["stamps"]
    )


def total_stamps(data, habit_id=None):
    if habit_id is None:
        return len(data["stamps"])

    return len(get_habit_stamps(data, habit_id))


def current_streak(data, habit_id):
    stamp_dates = {
        parse_date(stamp["date"])
        for stamp in get_habit_stamps(data, habit_id)
    }

    if not stamp_dates:
        return 0

    current = date.today()

    if current not in stamp_dates:
        current -= timedelta(days=1)

    streak = 0

    while current in stamp_dates:
        streak += 1
        current -= timedelta(days=1)

    return streak


def longest_streak(data, habit_id):
    stamp_dates = sorted(
        {
            parse_date(stamp["date"])
            for stamp in get_habit_stamps(data, habit_id)
        }
    )

    if not stamp_dates:
        return 0

    longest = 1
    current = 1

    for index in range(1, len(stamp_dates)):
        difference = (
            stamp_dates[index]
            - stamp_dates[index - 1]
        ).days

        if difference == 1:
            current += 1
            longest = max(longest, current)
        elif difference > 1:
            current = 1

    return longest


def habit_level(stamp_count):
    if stamp_count >= 300:
        return 10
    if stamp_count >= 200:
        return 9
    if stamp_count >= 150:
        return 8
    if stamp_count >= 100:
        return 7
    if stamp_count >= 70:
        return 6
    if stamp_count >= 50:
        return 5
    if stamp_count >= 30:
        return 4
    if stamp_count >= 15:
        return 3
    if stamp_count >= 5:
        return 2

    return 1


def next_level_target(stamp_count):
    targets = [
        5,
        15,
        30,
        50,
        70,
        100,
        150,
        200,
        300,
    ]

    for target in targets:
        if stamp_count < target:
            return target

    return None


def unlocked_badges(streak, stamp_count):
    badges = []

    if streak >= 7:
        badges.append("🥉 7日連続")

    if streak >= 30:
        badges.append("🥈 30日連続")

    if streak >= 100:
        badges.append("🥇 100日連続")

    if streak >= 365:
        badges.append("💎 365日連続")

    if stamp_count >= 10:
        badges.append("⭐ スタンプ10個")

    if stamp_count >= 50:
        badges.append("🌟 スタンプ50個")

    if stamp_count >= 100:
        badges.append("🏆 スタンプ100個")

    if not badges:
        badges.append("🌱 はじめの一歩")

    return badges


def month_stamp_count(data, habit_id, year, month):
    return len(
        [
            stamp
            for stamp in get_habit_stamps(data, habit_id)
            if parse_date(stamp["date"]).year == year
            and parse_date(stamp["date"]).month == month
        ]
    )


def target_progress(data, habit):
    today = date.today()
    habit_id = habit["id"]
    target_type = habit.get("target_type", "毎日")
    target_count = int(habit.get("target_count", 1))

    stamps = get_habit_stamps(data, habit_id)

    if target_type == "毎日":
        achieved = 1 if has_stamp_on_date(
            data,
            habit_id,
            today,
        ) else 0

        return achieved, 1

    if target_type == "週に指定回数":
        week_start = today - timedelta(
            days=today.weekday()
        )
        week_end = week_start + timedelta(days=6)

        achieved = len(
            [
                stamp
                for stamp in stamps
                if week_start
                <= parse_date(stamp["date"])
                <= week_end
            ]
        )

        return achieved, target_count

    achieved = month_stamp_count(
        data,
        habit_id,
        today.year,
        today.month,
    )

    return achieved, target_count


def monthly_rate(data, habit_id, year, month):
    days_in_month = calendar.monthrange(
        year,
        month,
    )[1]

    stamp_count = month_stamp_count(
        data,
        habit_id,
        year,
        month,
    )

    return round(
        min(stamp_count / days_in_month, 1) * 100,
        1,
    )


def calendar_text(data, habit_id, year, month):
    lines = []
    month_calendar = calendar.monthcalendar(
        year,
        month,
    )

    lines.append("月 火 水 木 金 土 日")

    for week in month_calendar:
        cells = []

        for day_number in week:
            if day_number == 0:
                cells.append("  ")
                continue

            target_date = date(
                year,
                month,
                day_number,
            )

            if has_stamp_on_date(
                data,
                habit_id,
                target_date,
            ):
                cells.append("⭐")
            else:
                cells.append("・")

        lines.append(" ".join(cells))

    return "\n".join(lines)


def to_habit_df(data):
    rows = []

    for habit in data["habits"]:
        stamp_count = total_stamps(
            data,
            habit["id"],
        )

        current = current_streak(
            data,
            habit["id"],
        )

        longest = longest_streak(
            data,
            habit["id"],
        )

        achieved, target = target_progress(
            data,
            habit,
        )

        progress = min(
            achieved / target,
            1,
        ) if target > 0 else 0

        rows.append(
            {
                "id": habit["id"],
                "created_at": habit["created_at"],
                "name": habit["name"],
                "icon": habit.get("icon", "⭐"),
                "category": habit["category"],
                "target_type": habit.get(
                    "target_type",
                    "毎日",
                ),
                "target_count": int(
                    habit.get("target_count", 1)
                ),
                "start_date": habit.get(
                    "start_date",
                    today_text(),
                ),
                "total_stamps": stamp_count,
                "current_streak": current,
                "longest_streak": longest,
                "level": habit_level(stamp_count),
                "today_done": has_stamp_on_date(
                    data,
                    habit["id"],
                    date.today(),
                ),
                "target_progress": (
                    f"{achieved}/{target}"
                ),
                "progress_rate": round(
                    progress * 100,
                    1,
                ),
                "favorite": bool(
                    habit.get("favorite", False)
                ),
                "memo": habit.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(
            [
                "today_done",
                "favorite",
                "current_streak",
                "created_at",
            ],
            ascending=[
                True,
                False,
                False,
                False,
            ],
        )

    return df


def to_stamp_df(data):
    rows = []

    for stamp in data["stamps"]:
        rows.append(
            {
                "id": stamp["id"],
                "created_at": stamp["created_at"],
                "date": stamp["date"],
                "habit_id": stamp["habit_id"],
                "habit_name": stamp["habit_name"],
                "icon": stamp.get("icon", "⭐"),
                "memo": stamp.get("memo", ""),
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
    page_icon="⭐",
    layout="wide",
)

st.title("⭐ Day198：習慣スタンプカード")
st.caption(
    "毎日の習慣をスタンプで記録し、連続日数・レベル・バッジを楽しむアプリ。"
)

data = load_data()

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "⭐ 今日のスタンプ",
        "➕ 習慣管理",
        "📅 カレンダー",
        "📜 履歴",
    ]
)

with tab1:
    st.subheader("今日の習慣")

    habit_df = to_habit_df(data)

    if habit_df.empty:
        st.info(
            "まだ習慣がないよ。先に習慣を登録してね。"
        )
    else:
        today_done_count = len(
            habit_df[
                habit_df["today_done"] == True
            ]
        )

        total_count = len(habit_df)
        total_stamp_count = total_stamps(data)
        best_streak = int(
            habit_df["longest_streak"].max()
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "習慣数",
            total_count,
        )

        c2.metric(
            "今日達成",
            f"{today_done_count}/{total_count}",
        )

        c3.metric(
            "総スタンプ",
            total_stamp_count,
        )

        c4.metric(
            "最高連続",
            f"{best_streak}日",
        )

        today_rate = (
            today_done_count / total_count
            if total_count > 0
            else 0
        )

        st.progress(today_rate)
        st.info(
            f"今日の達成率："
            f"{round(today_rate * 100, 1)}%"
        )

        st.divider()

        for _, row in habit_df.iterrows():
            habit = find_habit(
                data,
                row["id"],
            )

            with st.container(border=True):
                left, center, right = st.columns(
                    [2, 2, 1],
                )

                with left:
                    st.markdown(
                        f"### {row['icon']} {row['name']}"
                    )

                    st.write(
                        f"カテゴリ：{row['category']}"
                    )

                    st.write(
                        f"目標：{row['target_type']} "
                        f"／ {row['target_progress']}"
                    )

                with center:
                    st.write(
                        f"🔥 現在の連続："
                        f"{row['current_streak']}日"
                    )

                    st.write(
                        f"🏆 最長連続："
                        f"{row['longest_streak']}日"
                    )

                    st.write(
                        f"⭐ 累計："
                        f"{row['total_stamps']}個"
                    )

                    st.write(
                        f"Lv.{row['level']}"
                    )

                with right:
                    if row["today_done"]:
                        st.success("今日達成済み")

                        if st.button(
                            "↩️ 今日のスタンプ取消",
                            key=f"cancel_{row['id']}",
                        ):
                            data["stamps"] = [
                                stamp
                                for stamp in data["stamps"]
                                if not (
                                    stamp.get("habit_id")
                                    == row["id"]
                                    and stamp.get("date")
                                    == today_text()
                                )
                            ]

                            save_data(data)
                            st.rerun()
                    else:
                        if st.button(
                            "⭐ スタンプ",
                            type="primary",
                            key=f"stamp_{row['id']}",
                        ):
                            stamp = {
                                "id": (
                                    "stamp_"
                                    + datetime.now().strftime(
                                        "%Y%m%d%H%M%S%f"
                                    )
                                ),
                                "created_at": now_text(),
                                "date": today_text(),
                                "habit_id": habit["id"],
                                "habit_name": habit["name"],
                                "icon": habit.get(
                                    "icon",
                                    "⭐",
                                ),
                                "memo": "",
                            }

                            data["stamps"].append(stamp)
                            save_data(data)

                            st.success(
                                "スタンプを押したよ！"
                            )
                            st.rerun()

                progress_rate = min(
                    float(row["progress_rate"]) / 100,
                    1,
                )

                st.progress(progress_rate)

                next_target = next_level_target(
                    int(row["total_stamps"])
                )

                if next_target:
                    st.caption(
                        f"次のレベルまであと "
                        f"{next_target - int(row['total_stamps'])}"
                        f"スタンプ"
                    )
                else:
                    st.caption(
                        "最高レベル到達！"
                    )

                badges = unlocked_badges(
                    int(row["current_streak"]),
                    int(row["total_stamps"]),
                )

                st.write(
                    " ".join(badges)
                )

with tab2:
    left, right = st.columns(
        [1, 1],
        gap="large",
    )

    with left:
        st.subheader("習慣を登録")

        habit_name = st.text_input(
            "習慣名",
            placeholder=(
                "例：筋トレ / 読書 / 瞑想 / アプリ開発"
            ),
        )

        category = st.selectbox(
            "カテゴリ",
            CATEGORIES,
        )

        icon = st.selectbox(
            "アイコン",
            ICONS,
        )

        target_type = st.selectbox(
            "目標タイプ",
            TARGET_TYPES,
        )

        if target_type == "毎日":
            target_count = 1
            st.info(
                "毎日1回の達成を目標にするよ。"
            )
        elif target_type == "週に指定回数":
            target_count = st.number_input(
                "週の目標回数",
                min_value=1,
                max_value=7,
                value=3,
                step=1,
            )
        else:
            target_count = st.number_input(
                "月の目標回数",
                min_value=1,
                max_value=31,
                value=10,
                step=1,
            )

        start_date = st.date_input(
            "開始日",
            value=date.today(),
        )

        memo = st.text_area(
            "メモ",
            height=90,
            placeholder=(
                "例：無理のない範囲で継続する"
            ),
        )

        favorite = st.checkbox(
            "⭐ 大切な習慣"
        )

        if st.button(
            "➕ 習慣を登録",
            type="primary",
        ):
            if not habit_name.strip():
                st.warning(
                    "習慣名を入れてね。"
                )
            else:
                habit = {
                    "id": (
                        "habit_"
                        + datetime.now().strftime(
                            "%Y%m%d%H%M%S%f"
                        )
                    ),
                    "created_at": now_text(),
                    "name": habit_name.strip(),
                    "category": category,
                    "icon": icon,
                    "target_type": target_type,
                    "target_count": int(
                        target_count
                    ),
                    "start_date": (
                        start_date.isoformat()
                    ),
                    "memo": memo.strip(),
                    "favorite": favorite,
                }

                data["habits"].append(habit)
                save_data(data)

                st.success(
                    "習慣を登録したよ。"
                )
                st.rerun()

    with right:
        st.subheader("習慣一覧")

        habit_df = to_habit_df(data)

        if habit_df.empty:
            st.info(
                "まだ習慣が登録されていないよ。"
            )
        else:
            st.dataframe(
                habit_df[
                    [
                        "icon",
                        "name",
                        "category",
                        "target_type",
                        "target_count",
                        "total_stamps",
                        "current_streak",
                        "longest_streak",
                        "level",
                        "today_done",
                        "favorite",
                    ]
                ],
                use_container_width=True,
                height=300,
            )

            st.divider()
            st.subheader("詳細・更新")

            selected_habit_id = st.selectbox(
                "習慣を選ぶ",
                habit_df["id"].tolist(),
                format_func=lambda habit_id: (
                    f"{find_habit(data, habit_id).get('icon', '⭐')} "
                    f"{find_habit(data, habit_id)['name']}"
                ),
            )

            selected_habit = find_habit(
                data,
                selected_habit_id,
            )

            if selected_habit:
                stamp_count = total_stamps(
                    data,
                    selected_habit_id,
                )

                current = current_streak(
                    data,
                    selected_habit_id,
                )

                longest = longest_streak(
                    data,
                    selected_habit_id,
                )

                st.markdown(
                    f"## "
                    f"{selected_habit.get('icon', '⭐')} "
                    f"{selected_habit['name']}"
                )

                st.write(
                    f"カテゴリ："
                    f"{selected_habit['category']}"
                )

                st.write(
                    f"目標："
                    f"{selected_habit.get('target_type', '毎日')}"
                )

                st.write(
                    f"累計スタンプ：{stamp_count}"
                )

                st.write(
                    f"現在の連続：{current}日"
                )

                st.write(
                    f"最長連続：{longest}日"
                )

                st.write(
                    f"レベル："
                    f"Lv.{habit_level(stamp_count)}"
                )

                if selected_habit.get("memo"):
                    st.info(
                        selected_habit["memo"]
                    )

                new_category = st.selectbox(
                    "カテゴリ更新",
                    CATEGORIES,
                    index=CATEGORIES.index(
                        selected_habit.get(
                            "category",
                            "その他",
                        )
                    ),
                    key=(
                        f"category_"
                        f"{selected_habit_id}"
                    ),
                )

                new_favorite = st.checkbox(
                    "⭐ 大切な習慣",
                    value=bool(
                        selected_habit.get(
                            "favorite",
                            False,
                        )
                    ),
                    key=(
                        f"favorite_"
                        f"{selected_habit_id}"
                    ),
                )

                new_memo = st.text_area(
                    "メモ更新",
                    value=selected_habit.get(
                        "memo",
                        "",
                    ),
                    key=(
                        f"memo_"
                        f"{selected_habit_id}"
                    ),
                )

                if st.button(
                    "📝 習慣を更新"
                ):
                    selected_habit["category"] = (
                        new_category
                    )

                    selected_habit["favorite"] = (
                        new_favorite
                    )

                    selected_habit["memo"] = (
                        new_memo.strip()
                    )

                    selected_habit["updated_at"] = (
                        now_text()
                    )

                    save_data(data)

                    st.success(
                        "習慣を更新したよ。"
                    )
                    st.rerun()

                if st.button(
                    "🗑️ この習慣を削除",
                    type="secondary",
                ):
                    data["habits"] = [
                        habit
                        for habit in data["habits"]
                        if habit["id"]
                        != selected_habit_id
                    ]

                    data["stamps"] = [
                        stamp
                        for stamp in data["stamps"]
                        if stamp.get("habit_id")
                        != selected_habit_id
                    ]

                    save_data(data)

                    st.warning(
                        "習慣とスタンプ履歴を削除したよ。"
                    )
                    st.rerun()

            csv = habit_df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "⬇️ 習慣一覧CSV",
                data=csv,
                file_name=(
                    "day198_habit_stamp_habits.csv"
                ),
                mime="text/csv",
            )

with tab3:
    st.subheader("スタンプカレンダー")

    habit_df = to_habit_df(data)

    if habit_df.empty:
        st.info(
            "先に習慣を登録してね。"
        )
    else:
        selected_habit_id = st.selectbox(
            "表示する習慣",
            habit_df["id"].tolist(),
            format_func=lambda habit_id: (
                f"{find_habit(data, habit_id).get('icon', '⭐')} "
                f"{find_habit(data, habit_id)['name']}"
            ),
            key="calendar_habit",
        )

        selected_year = st.number_input(
            "年",
            min_value=2020,
            max_value=2100,
            value=date.today().year,
            step=1,
        )

        selected_month = st.selectbox(
            "月",
            list(range(1, 13)),
            index=date.today().month - 1,
            format_func=lambda value: (
                f"{value}月"
            ),
        )

        stamp_count = month_stamp_count(
            data,
            selected_habit_id,
            int(selected_year),
            int(selected_month),
        )

        rate = monthly_rate(
            data,
            selected_habit_id,
            int(selected_year),
            int(selected_month),
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "今月のスタンプ",
            f"{stamp_count}個",
        )

        c2.metric(
            "月間達成率",
            f"{rate}%",
        )

        st.progress(
            min(rate / 100, 1)
        )

        st.code(
            calendar_text(
                data,
                selected_habit_id,
                int(selected_year),
                int(selected_month),
            ),
            language="text",
        )

        selected_habit = find_habit(
            data,
            selected_habit_id,
        )

        st.markdown(
            f"### "
            f"{selected_habit.get('icon', '⭐')} "
            f"{selected_habit['name']}の記録"
        )

        habit_stamps = get_habit_stamps(
            data,
            selected_habit_id,
        )

        month_rows = [
            stamp
            for stamp in habit_stamps
            if parse_date(stamp["date"]).year
            == int(selected_year)
            and parse_date(stamp["date"]).month
            == int(selected_month)
        ]

        if month_rows:
            month_df = pd.DataFrame(
                month_rows
            ).sort_values(
                "date",
                ascending=False,
            )

            st.dataframe(
                month_df[
                    [
                        "date",
                        "memo",
                    ]
                ],
                use_container_width=True,
                height=220,
            )
        else:
            st.write(
                "この月のスタンプはまだないよ。"
            )

with tab4:
    st.subheader("スタンプ履歴")

    stamp_df = to_stamp_df(data)

    if stamp_df.empty:
        st.write(
            "まだスタンプ履歴がないよ。"
        )
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            history_keyword = st.text_input(
                "履歴検索",
                placeholder="習慣名・メモ",
            )

        with col_b:
            habit_names = [
                habit["name"]
                for habit in data["habits"]
            ]

            history_habit = st.selectbox(
                "習慣で絞る",
                ["すべて"] + habit_names,
            )

        history_view = stamp_df.copy()

        if history_keyword.strip():
            query = history_keyword.strip()

            history_view = history_view[
                history_view["habit_name"]
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

        if history_habit != "すべて":
            history_view = history_view[
                history_view["habit_name"]
                == history_habit
            ]

        st.dataframe(
            history_view[
                [
                    "date",
                    "icon",
                    "habit_name",
                    "memo",
                ]
            ],
            use_container_width=True,
            height=320,
        )

        st.divider()
        st.subheader("履歴の編集・削除")

        if not history_view.empty:
            selected_stamp_id = st.selectbox(
                "履歴を選ぶ",
                history_view["id"].tolist(),
                format_func=lambda stamp_id: (
                    f"{find_stamp(data, stamp_id)['date']} / "
                    f"{find_stamp(data, stamp_id)['habit_name']}"
                ),
            )

            selected_stamp = find_stamp(
                data,
                selected_stamp_id,
            )

            new_stamp_memo = st.text_area(
                "メモ更新",
                value=selected_stamp.get(
                    "memo",
                    "",
                ),
                key=(
                    f"stamp_memo_"
                    f"{selected_stamp_id}"
                ),
            )

            if st.button(
                "📝 履歴メモを更新"
            ):
                selected_stamp["memo"] = (
                    new_stamp_memo.strip()
                )

                selected_stamp["updated_at"] = (
                    now_text()
                )

                save_data(data)

                st.success(
                    "履歴を更新したよ。"
                )
                st.rerun()

            if st.button(
                "🗑️ この履歴を削除",
                type="secondary",
            ):
                data["stamps"] = [
                    stamp
                    for stamp in data["stamps"]
                    if stamp["id"]
                    != selected_stamp_id
                ]

                save_data(data)

                st.warning(
                    "スタンプ履歴を削除したよ。"
                )
                st.rerun()

        csv = stamp_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ スタンプ履歴CSV",
            data=csv,
            file_name=(
                "day198_habit_stamp_logs.csv"
            ),
            mime="text/csv",
        )
