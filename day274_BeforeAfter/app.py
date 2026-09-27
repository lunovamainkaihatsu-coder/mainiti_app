import json
import os
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="やる前・やった後",
    page_icon="🔄",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "before_after.json",
)

CATEGORIES = [
    "💪 運動",
    "📚 勉強",
    "💻 開発",
    "💼 仕事",
    "🏠 家事",
    "🎨 創作",
    "👨‍👩‍👧 家族",
    "💰 お金",
    "🚶 外出",
    "🎮 趣味",
    "🧠 その他",
]

CANCEL_REASONS = [
    "😴 疲れていた",
    "⏱️ 時間がなかった",
    "🔄 優先度が変わった",
    "😩 思ったより大変そうだった",
    "🚧 予定外のことが起きた",
    "❓ その他",
]

STATUS_LABELS = {
    "doing": "⏳ 未完了",
    "completed": "✅ 完了",
    "cancelled": "🛑 やめた",
}


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def today_text():
    return str(date.today())


def parse_date(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def stars(value):
    value = max(
        1,
        min(
            int(value),
            5,
        ),
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def create_empty_data():
    return {
        "records": [],
    }


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

    if not os.path.exists(
        DATA_FILE
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

        if not isinstance(
            data,
            dict,
        ):
            data = create_empty_data()

        data.setdefault(
            "records",
            [],
        )

        for record in data[
            "records"
        ]:
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
                "🧠 その他",
            )

            record.setdefault(
                "before_effort",
                3,
            )

            record.setdefault(
                "before_difficulty",
                3,
            )

            record.setdefault(
                "before_minutes",
                30,
            )

            record.setdefault(
                "before_satisfaction",
                3,
            )

            record.setdefault(
                "before_memo",
                "",
            )

            record.setdefault(
                "status",
                "doing",
            )

            record.setdefault(
                "after_effort",
                None,
            )

            record.setdefault(
                "after_difficulty",
                None,
            )

            record.setdefault(
                "after_minutes",
                None,
            )

            record.setdefault(
                "after_satisfaction",
                None,
            )

            record.setdefault(
                "after_memo",
                "",
            )

            record.setdefault(
                "cancel_reason",
                "",
            )

            record.setdefault(
                "cancel_memo",
                "",
            )

            record.setdefault(
                "record_date",
                today_text(),
            )

            record.setdefault(
                "completed_date",
                None,
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
            for record in data[
                "records"
            ]
            if record.get(
                "id"
            ) == record_id
        ),
        None,
    )


def add_record(
    data,
    title,
    category,
    effort,
    difficulty,
    minutes,
    satisfaction,
    memo,
    record_date,
):
    data["records"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "before_effort": int(
                effort
            ),
            "before_difficulty": int(
                difficulty
            ),
            "before_minutes": int(
                minutes
            ),
            "before_satisfaction": int(
                satisfaction
            ),
            "before_memo": memo,
            "status": "doing",
            "after_effort": None,
            "after_difficulty": None,
            "after_minutes": None,
            "after_satisfaction": None,
            "after_memo": "",
            "cancel_reason": "",
            "cancel_memo": "",
            "record_date": str(
                record_date
            ),
            "completed_date": None,
            "favorite": False,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def complete_record(
    data,
    record_id,
    effort,
    difficulty,
    minutes,
    satisfaction,
    memo,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["status"] = "completed"

    record["after_effort"] = int(
        effort
    )

    record[
        "after_difficulty"
    ] = int(
        difficulty
    )

    record["after_minutes"] = int(
        minutes
    )

    record[
        "after_satisfaction"
    ] = int(
        satisfaction
    )

    record["after_memo"] = memo

    record[
        "completed_date"
    ] = today_text()

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def cancel_record(
    data,
    record_id,
    reason,
    memo,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["status"] = "cancelled"

    record["cancel_reason"] = (
        reason
    )

    record["cancel_memo"] = memo

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

    record["status"] = "doing"
    record["cancel_reason"] = ""
    record["cancel_memo"] = ""

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

    record["favorite"] = not (
        record.get(
            "favorite",
            False,
        )
    )

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
        for record in data[
            "records"
        ]
        if record.get(
            "id"
        ) != record_id
    ]

    save_data(data)


# =========================================================
# 分析関数
# =========================================================

def average(
    values,
):
    values = [
        value
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(
        sum(values)
        / len(values),
        1,
    )


def time_difference(
    record,
):
    before = int(
        record.get(
            "before_minutes",
            0,
        )
        or 0
    )

    after = int(
        record.get(
            "after_minutes",
            0,
        )
        or 0
    )

    return after - before


def prediction_hit(
    record,
):
    before = int(
        record.get(
            "before_minutes",
            0,
        )
        or 0
    )

    after = int(
        record.get(
            "after_minutes",
            0,
        )
        or 0
    )

    if before <= 0:
        return False

    lower = before * 0.8
    upper = before * 1.2

    return (
        lower
        <= after
        <= upper
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
            rgba(90, 130, 220, 0.07);

        border:
            1px solid
            rgba(90, 130, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 130, 230, 0.18),
                rgba(180, 100, 210, 0.08)
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

    .compare-card {
        padding: 26px;
        border-radius: 22px;
        margin-bottom: 16px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 150, 230, 0.10),
                rgba(100, 200, 160, 0.06)
            );
    }

    .result-good {
        padding: 20px;
        border-radius: 18px;

        background:
            rgba(70, 190, 130, 0.10);
    }

    .result-warning {
        padding: 20px;
        border-radius: 18px;

        background:
            rgba(240, 170, 60, 0.10);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

records = data[
    "records"
]

doing_records = [
    record
    for record in records
    if record.get(
        "status"
    ) == "doing"
]

completed_records = [
    record
    for record in records
    if record.get(
        "status"
    ) == "completed"
]

cancelled_records = [
    record
    for record in records
    if record.get(
        "status"
    ) == "cancelled"
]

today = date.today()

month_prefix = today.strftime(
    "%Y-%m"
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
        month_prefix
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            🔄 やる前・やった後
        </h1>

        <p>
            「思っていた」と
            「実際」を比べてみよう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

if completed_records:
    avg_difference = average(
        [
            time_difference(
                record
            )
            for record
            in completed_records
        ]
    )

    hit_count = sum(
        1
        for record
        in completed_records
        if prediction_hit(
            record
        )
    )

    hit_rate = round(
        hit_count
        / len(
            completed_records
        )
        * 100
    )

else:
    avg_difference = 0
    hit_rate = 0


col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🔄 記録",
    f"{len(records)}件",
)

col2.metric(
    "✅ 完了",
    f"{len(completed_records)}件",
)

col3.metric(
    "⏱️ 平均時間差",
    (
        f"{avg_difference:+}分"
        if completed_records
        else "-"
    ),
)

col4.metric(
    "🎯 時間予想的中",
    (
        f"{hit_rate}%"
        if completed_records
        else "-"
    ),
)


# =========================================================
# やる前
# =========================================================

st.divider()

st.subheader(
    "▶️ やる前"
)

st.caption(
    "まだやっていない今、"
    "どれくらい大変そうに感じる？"
)

with st.form(
    "before_form",
    clear_on_submit=True,
):
    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input(
            "🎯 やること",
            placeholder=(
                "例：筋トレする"
            ),
        )

    with col2:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

    col1, col2 = st.columns(2)

    with col1:
        before_effort = st.slider(
            "😩 面倒・大変そう",
            1,
            5,
            3,
        )

        st.caption(
            stars(
                before_effort
            )
        )

        before_minutes = (
            st.number_input(
                "⏱️ 予想時間（分）",
                min_value=1,
                max_value=1440,
                value=30,
                step=5,
            )
        )

    with col2:
        before_difficulty = (
            st.slider(
                "🧠 難しそう",
                1,
                5,
                3,
            )
        )

        st.caption(
            stars(
                before_difficulty
            )
        )

        before_satisfaction = (
            st.slider(
                "😊 終わったら"
                "満足しそう",
                1,
                5,
                4,
            )
        )

        st.caption(
            stars(
                before_satisfaction
            )
        )

    before_memo = st.text_area(
        "💭 今の気持ち・予想",
        placeholder=(
            "始めるのが面倒そう、"
            "意外とすぐ終わりそう…"
        ),
    )

    record_date = st.date_input(
        "📅 日付",
        value=date.today(),
    )

    submitted = (
        st.form_submit_button(
            "▶️ やってみる",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "やることを入力してね。"
            )

        else:
            add_record(
                data,
                title.strip(),
                category,
                before_effort,
                before_difficulty,
                before_minutes,
                before_satisfaction,
                before_memo.strip(),
                record_date,
            )

            st.rerun()


# =========================================================
# 未完了
# =========================================================

st.divider()

st.subheader(
    "⏳ 実行中・未完了"
)

if not doing_records:
    st.info(
        "現在、未完了の記録はありません。"
    )

else:
    for record in sorted(
        doing_records,
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

        with st.container(
            border=True
        ):
            st.markdown(
                "### "
                + record.get(
                    "category",
                    ""
                )
                + " "
                + record.get(
                    "title",
                    "",
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "😩 大変そう",
                f"{record.get('before_effort', 3)} / 5",
            )

            col2.metric(
                "🧠 難しそう",
                f"{record.get('before_difficulty', 3)} / 5",
            )

            col3.metric(
                "⏱️ 予想",
                f"{record.get('before_minutes', 0)}分",
            )

            if record.get(
                "before_memo"
            ):
                st.caption(
                    "💭 "
                    + record.get(
                        "before_memo",
                        "",
                    )
                )

            with st.expander(
                "✅ 終わった！"
            ):
                with st.form(
                    "after_form_"
                    + record_id
                ):
                    col1, col2 = (
                        st.columns(2)
                    )

                    with col1:
                        after_effort = (
                            st.slider(
                                "😩 実際の大変さ",
                                1,
                                5,
                                3,
                                key=(
                                    "after_effort_"
                                    + record_id
                                ),
                            )
                        )

                        after_minutes = (
                            st.number_input(
                                "⏱️ 実際の時間（分）",
                                min_value=1,
                                max_value=1440,
                                value=int(
                                    record.get(
                                        "before_minutes",
                                        30,
                                    )
                                ),
                                step=5,
                                key=(
                                    "after_minutes_"
                                    + record_id
                                ),
                            )
                        )

                    with col2:
                        after_difficulty = (
                            st.slider(
                                "🧠 実際の難しさ",
                                1,
                                5,
                                3,
                                key=(
                                    "after_difficulty_"
                                    + record_id
                                ),
                            )
                        )

                        after_satisfaction = (
                            st.slider(
                                "😊 実際の満足度",
                                1,
                                5,
                                4,
                                key=(
                                    "after_satisfaction_"
                                    + record_id
                                ),
                            )
                        )

                    after_memo = (
                        st.text_area(
                            "💬 やってみた感想",
                            placeholder=(
                                "始めたら意外と"
                                "すぐ終わった！"
                            ),
                            key=(
                                "after_memo_"
                                + record_id
                            ),
                        )
                    )

                    after_submit = (
                        st.form_submit_button(
                            "✅ やった後を記録",
                            type="primary",
                            use_container_width=True,
                        )
                    )

                    if after_submit:
                        complete_record(
                            data,
                            record_id,
                            after_effort,
                            after_difficulty,
                            after_minutes,
                            after_satisfaction,
                            after_memo.strip(),
                        )

                        st.session_state[
                            "last_completed_id"
                        ] = record_id

                        st.rerun()

            with st.expander(
                "🛑 今回はやめた"
            ):
                with st.form(
                    "cancel_form_"
                    + record_id
                ):
                    cancel_reason = (
                        st.selectbox(
                            "理由",
                            CANCEL_REASONS,
                            key=(
                                "cancel_reason_"
                                + record_id
                            ),
                        )
                    )

                    cancel_memo = (
                        st.text_area(
                            "メモ（任意）",
                            key=(
                                "cancel_memo_"
                                + record_id
                            ),
                        )
                    )

                    cancel_submit = (
                        st.form_submit_button(
                            "🛑 今回はやめる",
                            use_container_width=True,
                        )
                    )

                    if cancel_submit:
                        cancel_record(
                            data,
                            record_id,
                            cancel_reason,
                            cancel_memo.strip(),
                        )

                        st.rerun()


# =========================================================
# 直前の比較結果
# =========================================================

last_completed_id = (
    st.session_state.get(
        "last_completed_id"
    )
)

if last_completed_id:
    latest = get_record(
        data,
        last_completed_id,
    )

    if (
        latest
        and latest.get(
            "status"
        ) == "completed"
    ):
        st.divider()

        st.subheader(
            "📊 予想 vs 現実"
        )

        st.markdown(
            "### "
            + latest.get(
                "title",
                "",
            )
        )

        compare_df = pd.DataFrame(
            {
                "項目": [
                    "😩 大変さ",
                    "🧠 難しさ",
                    "😊 満足度",
                ],
                "予想": [
                    latest.get(
                        "before_effort",
                        0,
                    ),
                    latest.get(
                        "before_difficulty",
                        0,
                    ),
                    latest.get(
                        "before_satisfaction",
                        0,
                    ),
                ],
                "実際": [
                    latest.get(
                        "after_effort",
                        0,
                    ),
                    latest.get(
                        "after_difficulty",
                        0,
                    ),
                    latest.get(
                        "after_satisfaction",
                        0,
                    ),
                ],
            }
        )

        st.dataframe(
            compare_df,
            use_container_width=True,
            hide_index=True,
        )

        before_minutes = int(
            latest.get(
                "before_minutes",
                0,
            )
        )

        after_minutes = int(
            latest.get(
                "after_minutes",
                0,
            )
        )

        difference = (
            after_minutes
            - before_minutes
        )

        col1, col2, col3 = (
            st.columns(3)
        )

        col1.metric(
            "予想時間",
            f"{before_minutes}分",
        )

        col2.metric(
            "実際時間",
            f"{after_minutes}分",
        )

        col3.metric(
            "差",
            f"{difference:+}分",
        )

        effort_difference = (
            int(
                latest.get(
                    "after_effort",
                    0,
                )
            )
            - int(
                latest.get(
                    "before_effort",
                    0,
                )
            )
        )

        if (
            difference < 0
            and effort_difference < 0
        ):
            st.success(
                "✨ 予想より早く、"
                "しかも思っていたより"
                "大変ではありませんでした！"
            )

        elif difference < 0:
            st.success(
                f"⏱️ 予想より"
                f"{abs(difference)}分"
                "早く終わりました！"
            )

        elif difference > 0:
            st.info(
                f"⏱️ 実際は予想より"
                f"{difference}分"
                "長くかかりました。"
            )

        else:
            st.success(
                "🎯 予想時間ぴったり！"
            )

        if st.button(
            "閉じる",
            key="close_comparison",
        ):
            st.session_state.pop(
                "last_completed_id",
                None,
            )

            st.rerun()


# =========================================================
# 自分の予想傾向
# =========================================================

if completed_records:
    st.divider()

    st.subheader(
        "🧠 自分の予想傾向"
    )

    avg_before_time = average(
        [
            int(
                record.get(
                    "before_minutes",
                    0,
                )
            )
            for record
            in completed_records
        ]
    )

    avg_after_time = average(
        [
            int(
                record.get(
                    "after_minutes",
                    0,
                )
            )
            for record
            in completed_records
        ]
    )

    avg_before_effort = average(
        [
            int(
                record.get(
                    "before_effort",
                    0,
                )
            )
            for record
            in completed_records
        ]
    )

    avg_after_effort = average(
        [
            int(
                record.get(
                    "after_effort",
                    0,
                )
            )
            for record
            in completed_records
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "#### ⏱️ 時間"
        )

        st.metric(
            "予想時間 平均",
            f"{avg_before_time}分",
        )

        st.metric(
            "実際時間 平均",
            f"{avg_after_time}分",
            delta=(
                f"{round(avg_after_time - avg_before_time, 1):+}分"
            ),
        )

    with col2:
        st.markdown(
            "#### 😩 大変さ"
        )

        st.metric(
            "予想 平均",
            f"{avg_before_effort} / 5",
        )

        st.metric(
            "実際 平均",
            f"{avg_after_effort} / 5",
            delta=(
                f"{round(avg_after_effort - avg_before_effort, 1):+}"
            ),
        )

    easier_count = sum(
        1
        for record
        in completed_records
        if int(
            record.get(
                "after_effort",
                0,
            )
        )
        < int(
            record.get(
                "before_effort",
                0,
            )
        )
    )

    harder_count = sum(
        1
        for record
        in completed_records
        if int(
            record.get(
                "after_effort",
                0,
            )
        )
        > int(
            record.get(
                "before_effort",
                0,
            )
        )
    )

    same_count = (
        len(
            completed_records
        )
        - easier_count
        - harder_count
    )

    st.markdown(
        "#### 🔍 大変さの予想結果"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    col1.metric(
        "✨ 予想より楽",
        f"{easier_count}件",
    )

    col2.metric(
        "🎯 予想通り",
        f"{same_count}件",
    )

    col3.metric(
        "🔥 予想より大変",
        f"{harder_count}件",
    )

    if (
        easier_count
        > harder_count
    ):
        st.info(
            f"📊 完了した"
            f"{len(completed_records)}件中"
            f"{easier_count}件で、"
            "実際の大変さが"
            "予想を下回っています。"
        )

    elif (
        harder_count
        > easier_count
    ):
        st.info(
            f"📊 完了した"
            f"{len(completed_records)}件中"
            f"{harder_count}件で、"
            "実際の大変さが"
            "予想を上回っています。"
        )


# =========================================================
# カテゴリー別分析
# =========================================================

if completed_records:
    st.divider()

    st.subheader(
        "📊 カテゴリー別"
    )

    category_rows = []

    for category in CATEGORIES:
        category_records = [
            record
            for record
            in completed_records
            if record.get(
                "category"
            ) == category
        ]

        if not category_records:
            continue

        before_time = average(
            [
                int(
                    record.get(
                        "before_minutes",
                        0,
                    )
                )
                for record
                in category_records
            ]
        )

        after_time = average(
            [
                int(
                    record.get(
                        "after_minutes",
                        0,
                    )
                )
                for record
                in category_records
            ]
        )

        before_effort = average(
            [
                int(
                    record.get(
                        "before_effort",
                        0,
                    )
                )
                for record
                in category_records
            ]
        )

        after_effort = average(
            [
                int(
                    record.get(
                        "after_effort",
                        0,
                    )
                )
                for record
                in category_records
            ]
        )

        category_rows.append(
            {
                "カテゴリー": category,
                "件数": len(
                    category_records
                ),
                "予想時間": before_time,
                "実際時間": after_time,
                "時間差": round(
                    after_time
                    - before_time,
                    1,
                ),
                "予想大変さ": (
                    before_effort
                ),
                "実際大変さ": (
                    after_effort
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True,
    )

    chart_df = (
        category_df[
            [
                "カテゴリー",
                "予想時間",
                "実際時間",
            ]
        ]
        .set_index(
            "カテゴリー"
        )
    )

    st.bar_chart(
        chart_df
    )


# =========================================================
# やめた理由
# =========================================================

if cancelled_records:
    st.divider()

    st.subheader(
        "🛑 やらなかった理由"
    )

    reason_rows = []

    for reason in CANCEL_REASONS:
        count = len(
            [
                record
                for record
                in cancelled_records
                if record.get(
                    "cancel_reason"
                ) == reason
            ]
        )

        if count:
            reason_rows.append(
                {
                    "理由": reason,
                    "回数": count,
                }
            )

    if reason_rows:
        reason_df = pd.DataFrame(
            reason_rows
        )

        st.bar_chart(
            reason_df.set_index(
                "理由"
            )
        )


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 記録履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "筋トレ、勉強、開発……"
    ),
)

category_filter = st.selectbox(
    "カテゴリー",
    ["すべて"] + CATEGORIES,
    key="history_category",
)

status_filter = st.selectbox(
    "状態",
    [
        "すべて",
        "doing",
        "completed",
        "cancelled",
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
                    "before_memo",
                    "",
                ),
                record.get(
                    "after_memo",
                    "",
                ),
                record.get(
                    "cancel_memo",
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
                "record_date",
                "",
            ),
            item.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        status = record.get(
            "status",
            "doing",
        )

        after_minutes = (
            record.get(
                "after_minutes"
            )
        )

        history_rows.append(
            {
                "日付": record.get(
                    "record_date",
                    "",
                ),
                "やること": record.get(
                    "title",
                    "",
                ),
                "カテゴリー": record.get(
                    "category",
                    "",
                ),
                "状態": STATUS_LABELS.get(
                    status,
                    status,
                ),
                "予想時間": (
                    f"{record.get('before_minutes', 0)}分"
                ),
                "実際時間": (
                    f"{after_minutes}分"
                    if after_minutes
                    is not None
                    else "-"
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
    for record in completed_records
    if record.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 覚えておきたい経験"
    )

    for record in favorites:
        st.write(
            "⭐ **"
            + record.get(
                "title",
                "",
            )
            + "**"
        )

        if record.get(
            "after_memo"
        ):
            st.caption(
                record.get(
                    "after_memo",
                    "",
                )
            )


# =========================================================
# 管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 記録を管理"
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

        status = record.get(
            "status",
            "doing",
        )

        label = (
            STATUS_LABELS.get(
                status,
                status,
            )
            + " ｜ "
            + record.get(
                "title",
                "",
            )
        )

        with st.expander(
            label
        ):
            st.write(
                "📅 "
                + record.get(
                    "record_date",
                    "",
                )
            )

            st.write(
                "🏷️ "
                + record.get(
                    "category",
                    "",
                )
            )

            st.write(
                "⏱️ 予想："
                + str(
                    record.get(
                        "before_minutes",
                        0,
                    )
                )
                + "分"
            )

            if (
                status
                == "completed"
            ):
                st.write(
                    "⏱️ 実際："
                    + str(
                        record.get(
                            "after_minutes",
                            0,
                        )
                    )
                    + "分"
                )

                icon = (
                    "⭐ お気に入り解除"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                )

                if st.button(
                    icon,
                    key=(
                        "favorite_"
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
                status
                == "cancelled"
            ):
                st.write(
                    "🛑 "
                    + record.get(
                        "cancel_reason",
                        "",
                    )
                )

                if st.button(
                    "♻️ 未完了に戻す",
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
            "before_after_"
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
    "「思っていた」と「実際」を比べると、"
    "自分の予想癖が見えてくる。🔄📊"
)
