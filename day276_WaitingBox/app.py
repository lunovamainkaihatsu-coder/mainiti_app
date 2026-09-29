import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日は何を待ってる？",
    page_icon="📬",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "waiting.json")

CATEGORIES = [
    "📩 返信・連絡",
    "📦 荷物",
    "💰 入金・返金",
    "📄 審査・手続き",
    "👥 人",
    "💼 仕事",
    "🏠 生活",
    "🛒 注文",
    "✨ その他",
]

RESULT_MOODS = [
    "😊 よかった",
    "😐 普通",
    "😣 微妙",
]

STATUS_LABELS = {
    "waiting": "⏳ 待機中",
    "action": "📩 確認する",
    "completed": "✅ 完了",
}


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def today_text():
    return str(date.today())


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return None


def create_empty_data():
    return {
        "records": []
    }


def stars(value):
    value = max(1, min(int(value), 5))
    return "★" * value + "☆" * (5 - value)


# =========================================================
# 保存・読み込み
# =========================================================

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


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(DATA_FILE):
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

        if not isinstance(data, dict):
            data = create_empty_data()

        data.setdefault(
            "records",
            [],
        )

        for record in data["records"]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "title",
                "",
            )

            record.setdefault(
                "category",
                "✨ その他",
            )

            record.setdefault(
                "target",
                "",
            )

            record.setdefault(
                "importance",
                3,
            )

            record.setdefault(
                "start_date",
                today_text(),
            )

            record.setdefault(
                "expected_date",
                None,
            )

            record.setdefault(
                "can_do",
                "",
            )

            record.setdefault(
                "memo",
                "",
            )

            record.setdefault(
                "status",
                "waiting",
            )

            record.setdefault(
                "action_date",
                None,
            )

            record.setdefault(
                "action_memo",
                "",
            )

            record.setdefault(
                "completed_date",
                None,
            )

            record.setdefault(
                "result",
                "",
            )

            record.setdefault(
                "result_mood",
                "",
            )

            record.setdefault(
                "result_memo",
                "",
            )

            record.setdefault(
                "favorite",
                False,
            )

            record.setdefault(
                "created_at",
                now_text(),
            )

            record.setdefault(
                "updated_at",
                record.get(
                    "created_at",
                    now_text(),
                ),
            )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = create_empty_data()
        save_data(data)
        return data


# =========================================================
# CRUD
# =========================================================

def get_record(
    data,
    record_id,
):
    return next(
        (
            record
            for record in data["records"]
            if record.get("id") == record_id
        ),
        None,
    )


def add_record(
    data,
    title,
    category,
    target,
    importance,
    start_date,
    expected_date,
    can_do,
    memo,
):
    data["records"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "target": target,
            "importance": int(importance),
            "start_date": str(start_date),
            "expected_date": (
                str(expected_date)
                if expected_date
                else None
            ),
            "can_do": can_do,
            "memo": memo,
            "status": "waiting",
            "action_date": None,
            "action_memo": "",
            "completed_date": None,
            "result": "",
            "result_mood": "",
            "result_memo": "",
            "favorite": False,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def set_action(
    data,
    record_id,
    action_date,
    action_memo,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["status"] = "action"
    record["action_date"] = str(
        action_date
    )
    record["action_memo"] = (
        action_memo
    )
    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def wait_more(
    data,
    record_id,
    expected_date,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["status"] = "waiting"
    record["expected_date"] = str(
        expected_date
    )
    record["action_date"] = None
    record["action_memo"] = ""
    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def complete_record(
    data,
    record_id,
    result,
    result_mood,
    result_memo,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["status"] = "completed"
    record["completed_date"] = (
        today_text()
    )
    record["result"] = result
    record["result_mood"] = (
        result_mood
    )
    record["result_memo"] = (
        result_memo
    )
    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def restore_record(
    data,
    record_id,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["status"] = "waiting"
    record["completed_date"] = None
    record["result"] = ""
    record["result_mood"] = ""
    record["result_memo"] = ""
    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_favorite(
    data,
    record_id,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["favorite"] = not record.get(
        "favorite",
        False,
    )

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def update_record(
    data,
    record_id,
    title,
    category,
    target,
    importance,
    start_date,
    expected_date,
    can_do,
    memo,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["title"] = title
    record["category"] = category
    record["target"] = target
    record["importance"] = int(
        importance
    )
    record["start_date"] = str(
        start_date
    )
    record["expected_date"] = (
        str(expected_date)
        if expected_date
        else None
    )
    record["can_do"] = can_do
    record["memo"] = memo
    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record in data["records"]
        if record.get("id") != record_id
    ]

    save_data(data)


# =========================================================
# 分析関数
# =========================================================

def waiting_days(record):
    start = parse_date(
        record.get("start_date")
    )

    if not start:
        return 0

    if record.get(
        "status"
    ) == "completed":
        end = parse_date(
            record.get(
                "completed_date"
            )
        )

        if not end:
            end = date.today()

    else:
        end = date.today()

    return max(
        (end - start).days,
        0,
    )


def expected_status(record):
    expected = parse_date(
        record.get(
            "expected_date"
        )
    )

    if not expected:
        return (
            "⚪",
            "予定日なし",
        )

    diff = (
        expected
        - date.today()
    ).days

    if diff < 0:
        return (
            "🔴",
            f"予定日から{abs(diff)}日経過",
        )

    if diff == 0:
        return (
            "🟢",
            "予定：今日",
        )

    if diff == 1:
        return (
            "🟢",
            "予定：明日",
        )

    return (
        "🟡",
        f"予定：あと{diff}日",
    )


def average(values):
    if not values:
        return 0

    return round(
        sum(values)
        / len(values),
        1,
    )


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 16px;

        background:
            rgba(80, 140, 220, 0.07);

        border:
            1px solid
            rgba(80, 140, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(90, 140, 230, 0.18),
                rgba(130, 190, 220, 0.08)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.82;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

records = data["records"]

active_records = [
    record
    for record in records
    if record.get(
        "status"
    ) in [
        "waiting",
        "action",
    ]
]

waiting_records = [
    record
    for record in records
    if record.get(
        "status"
    ) == "waiting"
]

action_records = [
    record
    for record in records
    if record.get(
        "status"
    ) == "action"
]

completed_records = [
    record
    for record in records
    if record.get(
        "status"
    ) == "completed"
]

overdue_records = []

for record in active_records:
    expected = parse_date(
        record.get(
            "expected_date"
        )
    )

    if (
        expected
        and expected < date.today()
    ):
        overdue_records.append(
            record
        )


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            📬 今日は何を待ってる？
        </h1>

        <p>
            今できることがないなら、
            いったん頭の外へ。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

completed_wait_days = [
    waiting_days(record)
    for record in completed_records
]

avg_wait = average(
    completed_wait_days
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "📬 現在待ってる",
    f"{len(active_records)}件",
)

col2.metric(
    "🔴 予定日超過",
    f"{len(overdue_records)}件",
)

col3.metric(
    "📩 確認が必要",
    f"{len(action_records)}件",
)

col4.metric(
    "⏱️ 平均待ち時間",
    (
        f"{avg_wait}日"
        if completed_records
        else "-"
    ),
)


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "📥 待つ箱に入れる"
)

with st.form(
    "new_wait_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "⏳ 何を待ってる？",
        placeholder=(
            "例：会社からの返信"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

        target = st.text_input(
            "👤 誰・何を待ってる？",
            placeholder=(
                "例：○○株式会社"
            ),
        )

        importance = st.slider(
            "⭐ 重要度",
            1,
            5,
            3,
        )

        st.caption(
            stars(importance)
        )

    with col2:
        start_date = st.date_input(
            "📅 待ち始めた日",
            value=date.today(),
        )

        has_expected_date = (
            st.checkbox(
                "📅 予定日がある",
                value=True,
            )
        )

        if has_expected_date:
            expected_date = (
                st.date_input(
                    "返事・結果の予定日",
                    value=(
                        date.today()
                        + timedelta(
                            days=3
                        )
                    ),
                )
            )

        else:
            expected_date = None

    can_do = st.text_input(
        "🧠 今、自分にできること",
        placeholder=(
            "例：今は特になし"
        ),
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "必要なら詳細を残しておこう"
        ),
    )

    submitted = (
        st.form_submit_button(
            "📬 待つ箱に入れる",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "待っているものを入力してね。"
            )

        else:
            add_record(
                data,
                title.strip(),
                category,
                target.strip(),
                importance,
                start_date,
                expected_date,
                can_do.strip(),
                memo.strip(),
            )

            st.session_state[
                "just_added_wait"
            ] = True

            st.rerun()


if st.session_state.pop(
    "just_added_wait",
    False,
):
    st.success(
        "📬 待つ箱に入れました。"
        " 今あなたにできることがないなら、"
        "いったん忘れてOK。"
    )


# =========================================================
# 待っているもの
# =========================================================

st.divider()

st.subheader(
    "📬 待っているもの"
)

if not active_records:
    st.info(
        "今、待っているものはありません。"
    )

else:
    def sort_active(record):
        expected = parse_date(
            record.get(
                "expected_date"
            )
        )

        return (
            expected
            if expected
            else date.max
        )

    for record in sorted(
        active_records,
        key=sort_active,
    ):
        record_id = record.get(
            "id",
            "",
        )

        icon, status_text = (
            expected_status(
                record
            )
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [7, 1]
            )

            with col1:
                st.markdown(
                    "### "
                    + icon
                    + " "
                    + record.get(
                        "category",
                        "",
                    )
                    + " "
                    + record.get(
                        "title",
                        "",
                    )
                )

            with col2:
                favorite_icon = (
                    "⭐"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    favorite_icon,
                    key=(
                        "favorite_active_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.write(
                "📅 " + status_text
            )

            col2.write(
                "⏱️ "
                + str(
                    waiting_days(
                        record
                    )
                )
                + "日待っています"
            )

            col3.write(
                "⭐ "
                + stars(
                    record.get(
                        "importance",
                        3,
                    )
                )
            )

            if record.get(
                "target"
            ):
                st.write(
                    "👤 **待っている相手・対象：** "
                    + record.get(
                        "target",
                        "",
                    )
                )

            if record.get(
                "can_do"
            ):
                st.write(
                    "🧠 **今できること：** "
                    + record.get(
                        "can_do",
                        "",
                    )
                )

            if record.get(
                "memo"
            ):
                st.caption(
                    "📝 "
                    + record.get(
                        "memo",
                        "",
                    )
                )

            if (
                record.get(
                    "status"
                )
                == "action"
            ):
                action_date = (
                    parse_date(
                        record.get(
                            "action_date"
                        )
                    )
                )

                if action_date:
                    action_diff = (
                        action_date
                        - date.today()
                    ).days

                    if action_diff < 0:
                        action_text = (
                            f"確認予定日から"
                            f"{abs(action_diff)}日経過"
                        )

                    elif action_diff == 0:
                        action_text = (
                            "今日確認する予定"
                        )

                    elif action_diff == 1:
                        action_text = (
                            "明日確認する予定"
                        )

                    else:
                        action_text = (
                            f"あと{action_diff}日で確認"
                        )

                    st.warning(
                        "📩 "
                        + action_text
                    )

                if record.get(
                    "action_memo"
                ):
                    st.caption(
                        "📩 "
                        + record.get(
                            "action_memo",
                            "",
                        )
                    )

            # ---------------------------------------------
            # 確認する
            # ---------------------------------------------

            with st.expander(
                "📩 確認する"
            ):
                with st.form(
                    "action_form_"
                    + record_id
                ):
                    action_date = (
                        st.date_input(
                            "確認予定日",
                            value=date.today(),
                            key=(
                                "action_date_"
                                + record_id
                            ),
                        )
                    )

                    action_memo = (
                        st.text_area(
                            "何をする？",
                            placeholder=(
                                "例：担当者へメールする"
                            ),
                            key=(
                                "action_memo_"
                                + record_id
                            ),
                        )
                    )

                    if (
                        st.form_submit_button(
                            "📩 確認することにする",
                            use_container_width=True,
                        )
                    ):
                        set_action(
                            data,
                            record_id,
                            action_date,
                            action_memo.strip(),
                        )

                        st.rerun()

            # ---------------------------------------------
            # もう少し待つ
            # ---------------------------------------------

            with st.expander(
                "⏳ もう少し待つ"
            ):
                current_expected = (
                    parse_date(
                        record.get(
                            "expected_date"
                        )
                    )
                )

                default_wait_date = (
                    current_expected
                    if (
                        current_expected
                        and current_expected
                        > date.today()
                    )
                    else (
                        date.today()
                        + timedelta(
                            days=3
                        )
                    )
                )

                with st.form(
                    "wait_more_form_"
                    + record_id
                ):
                    new_expected = (
                        st.date_input(
                            "いつまで待つ？",
                            value=(
                                default_wait_date
                            ),
                            key=(
                                "wait_more_date_"
                                + record_id
                            ),
                        )
                    )

                    if (
                        st.form_submit_button(
                            "⏳ この日まで待つ",
                            use_container_width=True,
                        )
                    ):
                        wait_more(
                            data,
                            record_id,
                            new_expected,
                        )

                        st.rerun()

            # ---------------------------------------------
            # 解決
            # ---------------------------------------------

            with st.expander(
                "✅ 解決した"
            ):
                with st.form(
                    "complete_form_"
                    + record_id
                ):
                    result = st.text_input(
                        "🎉 結果",
                        placeholder=(
                            "例：返信が来た"
                        ),
                        key=(
                            "result_"
                            + record_id
                        ),
                    )

                    result_mood = (
                        st.selectbox(
                            "どうだった？",
                            RESULT_MOODS,
                            key=(
                                "result_mood_"
                                + record_id
                            ),
                        )
                    )

                    result_memo = (
                        st.text_area(
                            "📝 結果メモ",
                            key=(
                                "result_memo_"
                                + record_id
                            ),
                        )
                    )

                    if (
                        st.form_submit_button(
                            "✅ 待ち終了！",
                            type="primary",
                            use_container_width=True,
                        )
                    ):
                        complete_record(
                            data,
                            record_id,
                            result.strip(),
                            result_mood,
                            result_memo.strip(),
                        )

                        st.session_state[
                            "last_completed_wait"
                        ] = record_id

                        st.rerun()


# =========================================================
# 完了直後
# =========================================================

last_completed_id = (
    st.session_state.get(
        "last_completed_wait"
    )
)

if last_completed_id:
    last_completed = get_record(
        data,
        last_completed_id,
    )

    if (
        last_completed
        and last_completed.get(
            "status"
        ) == "completed"
    ):
        st.divider()

        st.subheader(
            "🎉 待ち終了！"
        )

        st.success(
            last_completed.get(
                "title",
                "",
            )
            + " が完了しました！"
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "⏱️ 待った期間",
            f"{waiting_days(last_completed)}日",
        )

        col2.metric(
            "結果",
            last_completed.get(
                "result_mood",
                "完了",
            ),
        )

        if last_completed.get(
            "result"
        ):
            st.write(
                "📩 **結果：** "
                + last_completed.get(
                    "result",
                    "",
                )
            )

        if st.button(
            "閉じる",
            key="close_completed",
        ):
            st.session_state.pop(
                "last_completed_wait",
                None,
            )

            st.rerun()


# =========================================================
# 待ちすぎランキング
# =========================================================

if completed_records:
    st.divider()

    st.subheader(
        "🏆 長く待ったもの"
    )

    ranking = sorted(
        completed_records,
        key=waiting_days,
        reverse=True,
    )[:5]

    ranking_rows = []

    for index, record in enumerate(
        ranking,
        start=1,
    ):
        ranking_rows.append(
            {
                "順位": index,
                "待っていたもの": (
                    record.get(
                        "title",
                        "",
                    )
                ),
                "カテゴリー": (
                    record.get(
                        "category",
                        "",
                    )
                ),
                "待った日数": (
                    waiting_days(
                        record
                    )
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            ranking_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 今月の分析
# =========================================================

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_completed = [
    record
    for record in completed_records
    if (
        record.get(
            "completed_date",
            ""
        )
        or ""
    ).startswith(
        current_month
    )
]

if month_completed:
    st.divider()

    st.subheader(
        "📊 今月の「待つ」"
    )

    month_wait_days = [
        waiting_days(record)
        for record in month_completed
    ]

    col1, col2 = st.columns(2)

    col1.metric(
        "✅ 今月完了",
        f"{len(month_completed)}件",
    )

    col2.metric(
        "⏱️ 平均待ち時間",
        f"{average(month_wait_days)}日",
    )

    category_rows = []

    for category in CATEGORIES:
        count = len(
            [
                record
                for record in month_completed
                if record.get(
                    "category"
                )
                == category
            ]
        )

        if count:
            category_rows.append(
                {
                    "カテゴリー": category,
                    "件数": count,
                }
            )

    if category_rows:
        category_df = pd.DataFrame(
            category_rows
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 待ち履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "返信、荷物、返金……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="history_category",
    )

with col2:
    status_filter = st.selectbox(
        "状態",
        [
            "すべて",
            "waiting",
            "action",
            "completed",
        ],
        format_func=lambda value: (
            "すべて"
            if value == "すべて"
            else STATUS_LABELS.get(
                value,
                value,
            )
        ),
    )


filtered_records = []

for record in records:
    if (
        category_filter
        != "すべて"
        and record.get(
            "category"
        )
        != category_filter
    ):
        continue

    if (
        status_filter
        != "すべて"
        and record.get(
            "status"
        )
        != status_filter
    ):
        continue

    if search_text.strip():
        target = " ".join(
            [
                record.get(
                    "title",
                    "",
                ),
                record.get(
                    "target",
                    "",
                ),
                record.get(
                    "memo",
                    "",
                ),
                record.get(
                    "result",
                    "",
                ),
                record.get(
                    "result_memo",
                    "",
                ),
            ]
        ).lower()

        if (
            search_text
            .strip()
            .lower()
            not in target
        ):
            continue

    filtered_records.append(
        record
    )


if not filtered_records:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    history_rows = []

    for record in sorted(
        filtered_records,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        history_rows.append(
            {
                "待ち始め": (
                    record.get(
                        "start_date",
                        "",
                    )
                ),
                "待っているもの": (
                    record.get(
                        "title",
                        "",
                    )
                ),
                "カテゴリー": (
                    record.get(
                        "category",
                        "",
                    )
                ),
                "状態": (
                    STATUS_LABELS.get(
                        record.get(
                            "status"
                        ),
                        record.get(
                            "status",
                            "",
                        ),
                    )
                ),
                "待ち日数": (
                    waiting_days(
                        record
                    )
                ),
                "重要度": (
                    stars(
                        record.get(
                            "importance",
                            3,
                        )
                    )
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            history_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    record
    for record in records
    if record.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 覚えておきたい待ち"
    )

    for record in favorites:
        with st.container(
            border=True
        ):
            st.write(
                "⭐ **"
                + record.get(
                    "title",
                    "",
                )
                + "**"
            )

            st.caption(
                record.get(
                    "category",
                    "",
                )
                + " ｜ "
                + str(
                    waiting_days(
                        record
                    )
                )
                + "日"
            )

            if record.get(
                "result"
            ):
                st.write(
                    "📩 "
                    + record.get(
                        "result",
                        "",
                    )
                )


# =========================================================
# 編集・管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 記録を編集・管理"
):
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in sorted(
        records,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.expander(
            STATUS_LABELS.get(
                record.get(
                    "status"
                ),
                "",
            )
            + " ｜ "
            + record.get(
                "title",
                "",
            )
        ):
            edit_title = st.text_input(
                "待っているもの",
                value=record.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + record_id
                ),
            )

            current_category = (
                record.get(
                    "category",
                    "✨ その他",
                )
            )

            category_index = (
                CATEGORIES.index(
                    current_category
                )
                if current_category
                in CATEGORIES
                else len(
                    CATEGORIES
                ) - 1
            )

            edit_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=category_index,
                    key=(
                        "edit_category_"
                        + record_id
                    ),
                )
            )

            edit_target = st.text_input(
                "誰・何を待ってる？",
                value=record.get(
                    "target",
                    "",
                ),
                key=(
                    "edit_target_"
                    + record_id
                ),
            )

            edit_importance = (
                st.slider(
                    "重要度",
                    1,
                    5,
                    int(
                        record.get(
                            "importance",
                            3,
                        )
                    ),
                    key=(
                        "edit_importance_"
                        + record_id
                    ),
                )
            )

            parsed_start = (
                parse_date(
                    record.get(
                        "start_date"
                    )
                )
                or date.today()
            )

            edit_start = (
                st.date_input(
                    "待ち始めた日",
                    value=parsed_start,
                    key=(
                        "edit_start_"
                        + record_id
                    ),
                )
            )

            old_expected = (
                parse_date(
                    record.get(
                        "expected_date"
                    )
                )
            )

            edit_has_expected = (
                st.checkbox(
                    "予定日あり",
                    value=(
                        old_expected
                        is not None
                    ),
                    key=(
                        "edit_has_expected_"
                        + record_id
                    ),
                )
            )

            if edit_has_expected:
                edit_expected = (
                    st.date_input(
                        "予定日",
                        value=(
                            old_expected
                            or date.today()
                        ),
                        key=(
                            "edit_expected_"
                            + record_id
                        ),
                    )
                )

            else:
                edit_expected = None

            edit_can_do = (
                st.text_input(
                    "今できること",
                    value=record.get(
                        "can_do",
                        "",
                    ),
                    key=(
                        "edit_can_do_"
                        + record_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "メモ",
                    value=record.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + record_id
                    ),
                )
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "待っているものを入力してね。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_title.strip(),
                            edit_category,
                            edit_target.strip(),
                            edit_importance,
                            edit_start,
                            edit_expected,
                            edit_can_do.strip(),
                            edit_memo.strip(),
                        )

                        st.rerun()

            with col2:
                favorite_label = (
                    "⭐ お気に入り解除"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "manage_favorite_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            if (
                record.get(
                    "status"
                )
                == "completed"
            ):
                if st.button(
                    "♻️ 待機中に戻す",
                    key=(
                        "restore_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    restore_record(
                        data,
                        record_id,
                    )

                    st.rerun()

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + record_id
                ),
                use_container_width=True,
            ):
                delete_record(
                    data,
                    record_id,
                )

                if (
                    st.session_state.get(
                        "last_completed_wait"
                    )
                    == record_id
                ):
                    st.session_state.pop(
                        "last_completed_wait",
                        None,
                    )

                st.rerun()


# =========================================================
# JSONバックアップ
# =========================================================

st.divider()

with st.expander(
    "💾 データ管理"
):
    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            "waiting_box_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "📬 今あなたにできることがないなら、"
    "いったん忘れてOK。"
)
