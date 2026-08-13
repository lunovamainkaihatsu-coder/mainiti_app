import json
import os
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="家事ローテーション",
    page_icon="🧹",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "housework_data.json",
)

CATEGORIES = [
    "掃除",
    "洗濯",
    "キッチン",
    "お風呂",
    "トイレ",
    "寝具",
    "ゴミ",
    "整理整頓",
    "車",
    "季節家事",
    "メンテナンス",
    "その他",
]

IMPORTANCE_LEVELS = [
    "低",
    "普通",
    "高",
    "最優先",
]

IMPORTANCE_ORDER = {
    "最優先": 0,
    "高": 1,
    "普通": 2,
    "低": 3,
}

IMPORTANCE_ICONS = {
    "最優先": "🔥",
    "高": "🔴",
    "普通": "🟡",
    "低": "🟢",
}

STATUS_ICONS = {
    "まだ余裕": "🟢",
    "そろそろ": "🟡",
    "今日やる": "🔴",
    "期限超過": "⚠️",
}

DEFAULT_MEMBERS = [
    "自分",
    "家族",
    "誰でも",
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "chores": [],
        "history": [],
    }


def save_data(data):
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def normalize_data(data):
    if not isinstance(
        data,
        dict,
    ):
        data = create_empty_data()

    data.setdefault(
        "chores",
        [],
    )

    data.setdefault(
        "history",
        [],
    )

    for chore in data["chores"]:
        chore.setdefault(
            "id",
            create_id(),
        )

        chore.setdefault(
            "name",
            "",
        )

        chore.setdefault(
            "category",
            "その他",
        )

        chore.setdefault(
            "interval_days",
            7,
        )

        chore.setdefault(
            "last_done_date",
            "",
        )

        chore.setdefault(
            "assignee",
            "誰でも",
        )

        chore.setdefault(
            "importance",
            "普通",
        )

        chore.setdefault(
            "estimated_minutes",
            10,
        )

        chore.setdefault(
            "active",
            True,
        )

        chore.setdefault(
            "memo",
            "",
        )

        chore.setdefault(
            "created_at",
            "",
        )

        chore.setdefault(
            "updated_at",
            "",
        )

    for record in data["history"]:
        record.setdefault(
            "id",
            create_id(),
        )

        record.setdefault(
            "chore_id",
            "",
        )

        record.setdefault(
            "chore_name",
            "",
        )

        record.setdefault(
            "category",
            "その他",
        )

        record.setdefault(
            "done_date",
            str(date.today()),
        )

        record.setdefault(
            "assignee",
            "",
        )

        record.setdefault(
            "actual_minutes",
            0,
        )

        record.setdefault(
            "memo",
            "",
        )

        record.setdefault(
            "created_at",
            "",
        )

    return data


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE,
    ):
        data = create_empty_data()
        save_data(data)

        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE,
            ):
                os.replace(
                    DATA_FILE,
                    broken_file,
                )

        except OSError:
            pass

        data = create_empty_data()
        save_data(data)

        return data


# =========================================================
# 補助関数
# =========================================================

def parse_date(date_text):
    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

    except (
        TypeError,
        ValueError,
    ):
        return None


def format_date(date_text):
    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "未実施"

    weekdays = [
        "月",
        "火",
        "水",
        "木",
        "金",
        "土",
        "日",
    ]

    weekday = weekdays[
        parsed.weekday()
    ]

    return parsed.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_chore_by_id(
    data,
    chore_id,
):
    for chore in data["chores"]:
        if chore.get(
            "id"
        ) == chore_id:
            return chore

    return None


def get_chore_history(
    history,
    chore_id,
):
    return [
        record
        for record in history
        if record.get(
            "chore_id"
        ) == chore_id
    ]


def next_due_date(
    chore,
):
    last_done = parse_date(
        chore.get(
            "last_done_date",
            "",
        )
    )

    interval_days = int(
        chore.get(
            "interval_days",
            7,
        )
    )

    if not last_done:
        return date.today()

    return (
        last_done
        + timedelta(
            days=interval_days
        )
    )


def days_until_due(
    chore,
):
    due_date = next_due_date(
        chore
    )

    return (
        due_date
        - date.today()
    ).days


def chore_status(
    chore,
):
    days = days_until_due(
        chore
    )

    interval_days = max(
        int(
            chore.get(
                "interval_days",
                7,
            )
        ),
        1,
    )

    warning_days = max(
        round(
            interval_days
            * 0.25
        ),
        1,
    )

    if days < 0:
        return "期限超過"

    if days == 0:
        return "今日やる"

    if days <= warning_days:
        return "そろそろ"

    return "まだ余裕"


def status_sort_value(
    status,
):
    values = {
        "期限超過": 0,
        "今日やる": 1,
        "そろそろ": 2,
        "まだ余裕": 3,
    }

    return values.get(
        status,
        99,
    )


def total_estimated_minutes(
    chores,
):
    return sum(
        int(
            chore.get(
                "estimated_minutes",
                0,
            )
        )
        for chore in chores
    )


# =========================================================
# データ操作
# =========================================================

def add_chore(
    data,
    values,
):
    chore = {
        "id": create_id(),
        "name": values["name"],
        "category": (
            values["category"]
        ),
        "interval_days": int(
            values["interval_days"]
        ),
        "last_done_date": (
            values["last_done_date"]
        ),
        "assignee": (
            values["assignee"]
        ),
        "importance": (
            values["importance"]
        ),
        "estimated_minutes": int(
            values["estimated_minutes"]
        ),
        "active": True,
        "memo": values["memo"],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["chores"].append(
        chore
    )

    save_data(data)


def update_chore(
    data,
    chore_id,
    values,
):
    chore = get_chore_by_id(
        data,
        chore_id
    )

    if not chore:
        return

    for key, value in values.items():
        chore[key] = value

    chore["interval_days"] = int(
        chore.get(
            "interval_days",
            7,
        )
    )

    chore["estimated_minutes"] = int(
        chore.get(
            "estimated_minutes",
            10,
        )
    )

    chore["updated_at"] = (
        now_text()
    )

    save_data(data)


def complete_chore(
    data,
    chore_id,
    done_date,
    actual_minutes,
    assignee,
    memo,
):
    chore = get_chore_by_id(
        data,
        chore_id
    )

    if not chore:
        return

    history_record = {
        "id": create_id(),
        "chore_id": chore_id,
        "chore_name": (
            chore.get(
                "name",
                "",
            )
        ),
        "category": (
            chore.get(
                "category",
                "その他",
            )
        ),
        "done_date": str(
            done_date
        ),
        "assignee": assignee,
        "actual_minutes": int(
            actual_minutes
        ),
        "memo": memo,
        "created_at": now_text(),
    }

    data["history"].append(
        history_record
    )

    chore["last_done_date"] = str(
        done_date
    )

    chore["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_chore(
    data,
    chore_id,
):
    data["chores"] = [
        chore
        for chore in data[
            "chores"
        ]
        if chore.get(
            "id"
        ) != chore_id
    ]

    data["history"] = [
        record
        for record in data[
            "history"
        ]
        if record.get(
            "chore_id"
        ) != chore_id
    ]

    save_data(data)


def delete_history_record(
    data,
    record_id,
):
    target_record = next(
        (
            record
            for record in data[
                "history"
            ]
            if record.get(
                "id"
            ) == record_id
        ),
        None,
    )

    if not target_record:
        return

    chore_id = target_record.get(
        "chore_id",
        "",
    )

    data["history"] = [
        record
        for record in data[
            "history"
        ]
        if record.get(
            "id"
        ) != record_id
    ]

    chore = get_chore_by_id(
        data,
        chore_id
    )

    if chore:
        remaining_history = (
            get_chore_history(
                data["history"],
                chore_id,
            )
        )

        if remaining_history:
            latest = max(
                remaining_history,
                key=lambda record: (
                    record.get(
                        "done_date",
                        "",
                    ),
                    record.get(
                        "created_at",
                        "",
                    ),
                ),
            )

            chore["last_done_date"] = (
                latest.get(
                    "done_date",
                    "",
                )
            )

        else:
            chore["last_done_date"] = ""

        chore["updated_at"] = (
            now_text()
        )

    save_data(data)


# =========================================================
# デザイン
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(90, 160, 210, 0.08);
        border: 1px solid rgba(90, 160, 210, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(90, 160, 210, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(90, 160, 210, 0.18),
                rgba(110, 210, 170, 0.11)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 読み込み
# =========================================================

data = load_data()

chores = data[
    "chores"
]

history = data[
    "history"
]

active_chores = [
    chore
    for chore in chores
    if chore.get(
        "active",
        True,
    )
]

today_text = str(
    date.today()
)

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧹 家事ローテーション</h1>
        <p>
            最後にやった日を覚えなくても大丈夫。
            家事の次回タイミングを自動で管理
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

today_chores = [
    chore
    for chore in active_chores
    if chore_status(
        chore
    )
    == "今日やる"
]

overdue_chores = [
    chore
    for chore in active_chores
    if chore_status(
        chore
    )
    == "期限超過"
]

week_chores = [
    chore
    for chore in active_chores
    if 0
    <= days_until_due(
        chore
    )
    <= 7
]

today_completed = [
    record
    for record in history
    if record.get(
        "done_date"
    )
    == today_text
]

monthly_history = [
    record
    for record in history
    if record.get(
        "done_date",
        "",
    ).startswith(
        current_month
    )
]

today_work_list = (
    overdue_chores
    + [
        chore
        for chore in today_chores
        if chore.get(
            "id"
        )
        not in {
            overdue.get(
                "id"
            )
            for overdue
            in overdue_chores
        }
    ]
)


metric_row1 = st.columns(
    4
)

metric_row1[0].metric(
    "今日やる家事",
    f"{len(today_chores)}件"
)

metric_row1[1].metric(
    "期限超過",
    f"{len(overdue_chores)}件"
)

metric_row1[2].metric(
    "今週予定",
    f"{len(week_chores)}件"
)

metric_row1[3].metric(
    "今日完了",
    f"{len(today_completed)}件"
)


metric_row2 = st.columns(
    4
)

metric_row2[0].metric(
    "登録家事",
    f"{len(active_chores)}件"
)

metric_row2[1].metric(
    "今月実行",
    f"{len(monthly_history)}回"
)

metric_row2[2].metric(
    "今日の予定時間",
    f"{total_estimated_minutes(today_work_list)}分"
)

metric_row2[3].metric(
    "累計実行",
    f"{len(history)}回"
)


# =========================================================
# 今日の家事
# =========================================================

st.divider()

st.header(
    "🏠 今日の家事"
)

priority_chores = [
    chore
    for chore in active_chores
    if chore_status(
        chore
    )
    in [
        "期限超過",
        "今日やる",
        "そろそろ",
    ]
]

priority_chores.sort(
    key=lambda chore: (
        status_sort_value(
            chore_status(
                chore
            )
        ),
        IMPORTANCE_ORDER.get(
            chore.get(
                "importance",
                "普通",
            ),
            99,
        ),
        days_until_due(
            chore
        ),
    )
)

if not priority_chores:
    st.success(
        "今日は急いでやる家事はありません！✨"
    )

else:
    for chore in priority_chores:
        chore_id = chore[
            "id"
        ]

        status = chore_status(
            chore
        )

        days = days_until_due(
            chore
        )

        due_date = next_due_date(
            chore
        )

        with st.container(
            border=True
        ):
            column1, column2 = (
                st.columns(
                    [
                        4,
                        1,
                    ]
                )
            )

            with column1:
                st.markdown(
                    f"### "
                    f"{STATUS_ICONS.get(status, '')} "
                    f"{chore.get('name', '')}"
                )

                st.caption(
                    f"{chore.get('category', '')} ／ "
                    f"{IMPORTANCE_ICONS.get(chore.get('importance', ''), '')} "
                    f"{chore.get('importance', '')} ／ "
                    f"担当：{chore.get('assignee', '')}"
                )

                st.write(
                    f"前回："
                    f"**{format_date(chore.get('last_done_date', ''))}**"
                )

                st.write(
                    f"次回予定："
                    f"**{due_date.strftime('%Y年%m月%d日')}**"
                )

                if chore.get(
                    "memo",
                    "",
                ):
                    st.info(
                        chore.get(
                            "memo",
                            "",
                        )
                    )

            with column2:
                st.metric(
                    "状態",
                    status
                )

                if days < 0:
                    st.metric(
                        "予定から",
                        f"{-days}日超過"
                    )

                elif days == 0:
                    st.metric(
                        "予定まで",
                        "今日"
                    )

                else:
                    st.metric(
                        "予定まで",
                        f"あと{days}日"
                    )

                st.metric(
                    "目安時間",
                    f"{chore.get('estimated_minutes', 0)}分"
                )

            with st.expander(
                "✅ この家事を完了"
            ):
                done_date_input = (
                    st.date_input(
                        "実行日",
                        value=date.today(),
                        max_value=date.today(),
                        key=(
                            f"done_date_"
                            f"{chore_id}"
                        ),
                    )
                )

                completion_assignee = (
                    st.text_input(
                        "実際にやった人",
                        value=chore.get(
                            "assignee",
                            "",
                        ),
                        key=(
                            f"done_assignee_"
                            f"{chore_id}"
                        ),
                    )
                )

                actual_minutes = (
                    st.number_input(
                        "実際にかかった時間",
                        min_value=0,
                        max_value=1440,
                        value=int(
                            chore.get(
                                "estimated_minutes",
                                10,
                            )
                        ),
                        key=(
                            f"actual_minutes_"
                            f"{chore_id}"
                        ),
                    )
                )

                completion_memo = (
                    st.text_area(
                        "完了メモ",
                        placeholder=(
                            "例：洗剤を補充した"
                        ),
                        key=(
                            f"completion_memo_"
                            f"{chore_id}"
                        ),
                    )
                )

                if st.button(
                    "✅ 完了として記録",
                    key=(
                        f"complete_chore_"
                        f"{chore_id}"
                    ),
                    use_container_width=True,
                ):
                    complete_chore(
                        data,
                        chore_id,
                        done_date_input,
                        actual_minutes,
                        completion_assignee.strip(),
                        completion_memo.strip(),
                    )

                    st.success(
                        "家事を完了しました！"
                    )

                    st.balloons()
                    st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    chore_tab,
    schedule_tab,
    history_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 家事管理",
        "📅 ローテーション",
        "📚 実行履歴",
        "📈 家事分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 家事管理
# =========================================================

with chore_tab:
    st.header(
        "➕ 家事を登録"
    )

    with st.form(
        "add_chore_form",
        clear_on_submit=True,
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            chore_name = st.text_input(
                "家事名",
                placeholder=(
                    "例：シーツ交換"
                ),
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            interval_days = (
                st.number_input(
                    "実行間隔（日）",
                    min_value=1,
                    max_value=3650,
                    value=7,
                    step=1,
                )
            )

            set_last_done = (
                st.checkbox(
                    "最終実行日を設定する",
                    value=True,
                )
            )

            last_done_date = ""

            if set_last_done:
                last_done_date = str(
                    st.date_input(
                        "最終実行日",
                        value=date.today(),
                        max_value=date.today(),
                    )
                )

        with column2:
            assignee = st.text_input(
                "担当",
                value="誰でも",
                placeholder=(
                    "自分、家族、誰でも"
                ),
            )

            importance = st.selectbox(
                "重要度",
                IMPORTANCE_LEVELS,
                index=1,
            )

            estimated_minutes = (
                st.number_input(
                    "目安時間（分）",
                    min_value=1,
                    max_value=1440,
                    value=10,
                    step=5,
                )
            )

        memo = st.text_area(
            "メモ",
            placeholder=(
                "必要な道具や注意点など"
            ),
            height=100,
        )

        submitted = (
            st.form_submit_button(
                "🧹 家事を登録",
                use_container_width=True,
            )
        )

        if submitted:
            if not chore_name.strip():
                st.error(
                    "家事名を入力してください。"
                )

            else:
                add_chore(
                    data,
                    {
                        "name": (
                            chore_name.strip()
                        ),
                        "category": (
                            category
                        ),
                        "interval_days": (
                            interval_days
                        ),
                        "last_done_date": (
                            last_done_date
                        ),
                        "assignee": (
                            assignee.strip()
                            or "誰でも"
                        ),
                        "importance": (
                            importance
                        ),
                        "estimated_minutes": (
                            estimated_minutes
                        ),
                        "memo": (
                            memo.strip()
                        ),
                    }
                )

                st.success(
                    "家事を登録しました！"
                )

                st.rerun()

    st.divider()

    if not chores:
        st.info(
            "登録された家事はまだありません。"
        )

    for chore in chores:
        chore_id = chore[
            "id"
        ]

        chore_history = (
            get_chore_history(
                history,
                chore_id,
            )
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### "
                f"{'🧹' if chore.get('active', True) else '⏸️'} "
                f"{chore.get('name', '')}"
            )

            st.caption(
                f"{chore.get('category', '')} ／ "
                f"{chore.get('interval_days', 7)}日ごと"
            )

            columns = st.columns(
                4
            )

            columns[0].metric(
                "状態",
                chore_status(
                    chore
                )
            )

            columns[1].metric(
                "次回",
                next_due_date(
                    chore
                ).strftime(
                    "%m/%d"
                )
            )

            columns[2].metric(
                "担当",
                chore.get(
                    "assignee",
                    ""
                )
            )

            columns[3].metric(
                "実行回数",
                f"{len(chore_history)}回"
            )

            with st.expander(
                "✏️ 家事を編集"
            ):
                edit_name = st.text_input(
                    "家事名",
                    value=chore.get(
                        "name",
                        "",
                    ),
                    key=(
                        f"edit_name_"
                        f"{chore_id}"
                    ),
                )

                current_category = (
                    chore.get(
                        "category",
                        "その他",
                    )
                )

                edit_category = st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=(
                        CATEGORIES.index(
                            current_category
                        )
                        if current_category
                        in CATEGORIES
                        else (
                            len(CATEGORIES)
                            - 1
                        )
                    ),
                    key=(
                        f"edit_category_"
                        f"{chore_id}"
                    ),
                )

                edit_interval = (
                    st.number_input(
                        "実行間隔（日）",
                        min_value=1,
                        max_value=3650,
                        value=int(
                            chore.get(
                                "interval_days",
                                7,
                            )
                        ),
                        key=(
                            f"edit_interval_"
                            f"{chore_id}"
                        ),
                    )
                )

                edit_assignee = (
                    st.text_input(
                        "担当",
                        value=chore.get(
                            "assignee",
                            "",
                        ),
                        key=(
                            f"edit_assignee_"
                            f"{chore_id}"
                        ),
                    )
                )

                current_importance = (
                    chore.get(
                        "importance",
                        "普通",
                    )
                )

                edit_importance = (
                    st.selectbox(
                        "重要度",
                        IMPORTANCE_LEVELS,
                        index=(
                            IMPORTANCE_LEVELS.index(
                                current_importance
                            )
                            if current_importance
                            in IMPORTANCE_LEVELS
                            else 1
                        ),
                        key=(
                            f"edit_importance_"
                            f"{chore_id}"
                        ),
                    )
                )

                edit_minutes = (
                    st.number_input(
                        "目安時間",
                        min_value=1,
                        max_value=1440,
                        value=int(
                            chore.get(
                                "estimated_minutes",
                                10,
                            )
                        ),
                        key=(
                            f"edit_minutes_"
                            f"{chore_id}"
                        ),
                    )
                )

                edit_active = st.checkbox(
                    "この家事を有効にする",
                    value=bool(
                        chore.get(
                            "active",
                            True,
                        )
                    ),
                    key=(
                        f"edit_active_"
                        f"{chore_id}"
                    ),
                )

                edit_memo = st.text_area(
                    "メモ",
                    value=chore.get(
                        "memo",
                        "",
                    ),
                    key=(
                        f"edit_memo_"
                        f"{chore_id}"
                    ),
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_chore_"
                        f"{chore_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_name.strip():
                        st.error(
                            "家事名を入力してください。"
                        )

                    else:
                        update_chore(
                            data,
                            chore_id,
                            {
                                "name": (
                                    edit_name.strip()
                                ),
                                "category": (
                                    edit_category
                                ),
                                "interval_days": (
                                    edit_interval
                                ),
                                "assignee": (
                                    edit_assignee.strip()
                                    or "誰でも"
                                ),
                                "importance": (
                                    edit_importance
                                ),
                                "estimated_minutes": (
                                    edit_minutes
                                ),
                                "active": (
                                    edit_active
                                ),
                                "memo": (
                                    edit_memo.strip()
                                ),
                            }
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 家事を削除"
            ):
                st.warning(
                    "この家事の実行履歴も削除されます。"
                )

                confirm_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_"
                            f"{chore_id}"
                        ),
                    )
                )

                if st.button(
                    "この家事を削除",
                    key=(
                        f"delete_chore_"
                        f"{chore_id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True,
                ):
                    delete_chore(
                        data,
                        chore_id,
                    )

                    st.rerun()


# =========================================================
# ローテーション
# =========================================================

with schedule_tab:
    st.header(
        "📅 家事ローテーション"
    )

    if not active_chores:
        st.info(
            "有効な家事がありません。"
        )

    else:
        schedule_rows = []

        for chore in active_chores:
            status = chore_status(
                chore
            )

            schedule_rows.append(
                {
                    "家事": (
                        chore.get(
                            "name",
                            "",
                        )
                    ),
                    "カテゴリー": (
                        chore.get(
                            "category",
                            "",
                        )
                    ),
                    "状態": (
                        f"{STATUS_ICONS.get(status, '')} "
                        f"{status}"
                    ),
                    "担当": (
                        chore.get(
                            "assignee",
                            "",
                        )
                    ),
                    "間隔": (
                        f"{chore.get('interval_days', 0)}日"
                    ),
                    "前回": (
                        chore.get(
                            "last_done_date",
                            ""
                        )
                        or "未実施"
                    ),
                    "次回予定": (
                        str(
                            next_due_date(
                                chore
                            )
                        )
                    ),
                    "残り日数": (
                        days_until_due(
                            chore
                        )
                    ),
                    "目安時間": (
                        chore.get(
                            "estimated_minutes",
                            0,
                        )
                    ),
                    "重要度": (
                        chore.get(
                            "importance",
                            "",
                        )
                    ),
                }
            )

        schedule_df = pd.DataFrame(
            schedule_rows
        )

        schedule_df = (
            schedule_df.sort_values(
                [
                    "残り日数",
                    "目安時間",
                ]
            )
        )

        st.dataframe(
            schedule_df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "今後7日間の予定"
        )

        upcoming_df = schedule_df[
            schedule_df[
                "残り日数"
            ].between(
                0,
                7,
            )
        ]

        if upcoming_df.empty:
            st.success(
                "今後7日間に予定されている家事はありません。"
            )

        else:
            st.dataframe(
                upcoming_df[
                    [
                        "家事",
                        "次回予定",
                        "残り日数",
                        "担当",
                        "目安時間",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# 実行履歴
# =========================================================

with history_tab:
    st.header(
        "📚 家事の実行履歴"
    )

    if not history:
        st.info(
            "実行履歴はまだありません。"
        )

    else:
        chore_options = {
            "すべて": ""
        }

        for chore in chores:
            chore_options[
                chore.get(
                    "name",
                    ""
                )
            ] = chore[
                "id"
            ]

        selected_chore_name = (
            st.selectbox(
                "家事で絞り込み",
                list(
                    chore_options.keys()
                ),
            )
        )

        selected_chore_id = (
            chore_options[
                selected_chore_name
            ]
        )

        filtered_history = list(
            history
        )

        if selected_chore_id:
            filtered_history = [
                record
                for record
                in filtered_history
                if record.get(
                    "chore_id"
                )
                == selected_chore_id
            ]

        filtered_history.sort(
            key=lambda record: (
                record.get(
                    "done_date",
                    "",
                ),
                record.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        for record in filtered_history:
            record_id = record[
                "id"
            ]

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### ✅ "
                    f"{record.get('chore_name', '')}"
                )

                st.caption(
                    f"{format_date(record.get('done_date', ''))} ／ "
                    f"{record.get('category', '')}"
                )

                columns = st.columns(
                    3
                )

                columns[0].metric(
                    "担当",
                    record.get(
                        "assignee",
                        ""
                    )
                )

                columns[1].metric(
                    "実際の時間",
                    f"{record.get('actual_minutes', 0)}分"
                )

                columns[2].metric(
                    "実行日",
                    record.get(
                        "done_date",
                        "",
                    )
                )

                if record.get(
                    "memo",
                    "",
                ):
                    st.info(
                        record.get(
                            "memo",
                            "",
                        )
                    )

                with st.expander(
                    "🗑️ 履歴を削除"
                ):
                    confirm_history_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_history_delete_"
                                f"{record_id}"
                            ),
                        )
                    )

                    if st.button(
                        "この履歴を削除",
                        key=(
                            f"delete_history_"
                            f"{record_id}"
                        ),
                        disabled=(
                            not confirm_history_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_history_record(
                            data,
                            record_id,
                        )

                        st.rerun()


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 家事分析"
    )

    if not history:
        st.info(
            "分析できる実行履歴がありません。"
        )

    else:
        analysis_rows = []

        for record in history:
            analysis_rows.append(
                {
                    "日付": (
                        record.get(
                            "done_date",
                            "",
                        )
                    ),
                    "月": (
                        record.get(
                            "done_date",
                            "",
                        )[:7]
                    ),
                    "家事": (
                        record.get(
                            "chore_name",
                            "",
                        )
                    ),
                    "カテゴリー": (
                        record.get(
                            "category",
                            "",
                        )
                    ),
                    "担当": (
                        record.get(
                            "assignee",
                            "",
                        )
                    ),
                    "時間": int(
                        record.get(
                            "actual_minutes",
                            0,
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "月別実行回数"
        )

        monthly_summary = (
            analysis_df.groupby(
                "月",
                as_index=False,
            )
            .agg(
                実行回数=(
                    "家事",
                    "count",
                ),
                家事時間=(
                    "時間",
                    "sum",
                ),
            )
            .sort_values(
                "月"
            )
        )

        st.bar_chart(
            monthly_summary.set_index(
                "月"
            )[["実行回数"]]
        )

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "カテゴリー別"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False,
            )
            .agg(
                実行回数=(
                    "家事",
                    "count",
                ),
                合計時間=(
                    "時間",
                    "sum",
                ),
                平均時間=(
                    "時間",
                    "mean",
                ),
            )
            .sort_values(
                "実行回数",
                ascending=False,
            )
        )

        category_summary[
            "平均時間"
        ] = category_summary[
            "平均時間"
        ].round(
            1
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["実行回数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "よくやる家事"
        )

        chore_summary = (
            analysis_df.groupby(
                "家事",
                as_index=False,
            )
            .agg(
                実行回数=(
                    "家事",
                    "count",
                ),
                合計時間=(
                    "時間",
                    "sum",
                ),
                平均時間=(
                    "時間",
                    "mean",
                ),
            )
            .sort_values(
                "実行回数",
                ascending=False,
            )
        )

        chore_summary[
            "平均時間"
        ] = chore_summary[
            "平均時間"
        ].round(
            1
        )

        st.dataframe(
            chore_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "担当別"
        )

        assignee_summary = (
            analysis_df.groupby(
                "担当",
                as_index=False,
            )
            .agg(
                実行回数=(
                    "家事",
                    "count",
                ),
                合計時間=(
                    "時間",
                    "sum",
                ),
            )
            .sort_values(
                "実行回数",
                ascending=False,
            )
        )

        st.bar_chart(
            assignee_summary.set_index(
                "担当"
            )[["実行回数"]]
        )

        st.dataframe(
            assignee_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "期限超過しやすい家事"
        )

        overdue_rows = []

        for chore in active_chores:
            days = days_until_due(
                chore
            )

            if days < 0:
                overdue_rows.append(
                    {
                        "家事": (
                            chore.get(
                                "name",
                                "",
                            )
                        ),
                        "カテゴリー": (
                            chore.get(
                                "category",
                                "",
                            )
                        ),
                        "超過日数": (
                            -days
                        ),
                        "担当": (
                            chore.get(
                                "assignee",
                                "",
                            )
                        ),
                        "重要度": (
                            chore.get(
                                "importance",
                                "",
                            )
                        ),
                    }
                )

        if not overdue_rows:
            st.success(
                "現在、期限超過している家事はありません！"
            )

        else:
            overdue_df = (
                pd.DataFrame(
                    overdue_rows
                )
                .sort_values(
                    "超過日数",
                    ascending=False,
                )
            )

            st.dataframe(
                overdue_df,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# データ管理
# =========================================================

with data_tab:
    st.header(
        "💾 データ管理"
    )

    st.subheader(
        "JSONバックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"housework_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONから復元"
    )

    uploaded_file = (
        st.file_uploader(
            "バックアップJSONを選択",
            type=[
                "json"
            ],
        )
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict,
                )
                or "chores"
                not in imported_data
                or "history"
                not in imported_data
            ):
                st.error(
                    "対応していないJSON形式です。"
                )

            else:
                imported_data = (
                    normalize_data(
                        imported_data
                    )
                )

                st.warning(
                    "復元すると現在のデータが上書きされます。"
                )

                confirm_restore = (
                    st.checkbox(
                        "上書き復元を確認しました"
                    )
                )

                if st.button(
                    "JSONから復元",
                    disabled=(
                        not confirm_restore
                    ),
                    use_container_width=True,
                ):
                    save_data(
                        imported_data
                    )

                    st.success(
                        "データを復元しました！"
                    )

                    st.rerun()

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "家事・実行履歴がすべて削除されます。"
    )

    confirm_delete_all = (
        st.checkbox(
            "全データ削除を確認しました"
        )
    )

    if st.button(
        "すべて削除",
        disabled=(
            not confirm_delete_all
        ),
        use_container_width=True,
    ):
        save_data(
            create_empty_data()
        )

        st.success(
            "すべてのデータを削除しました。"
        )

        st.rerun()


# =========================================================
# フッター
# =========================================================

st.divider()

st.success(
    "「最後にいつやった？」を覚えなくても大丈夫。家事はローテーションに任せよう。🧹"
)
