import json
import os
import random
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="思ったより早かった！",
    page_icon="⏱️",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "tasks.json",
)

CATEGORIES = [
    "💻 開発",
    "📚 勉強",
    "💼 仕事",
    "🏠 家事・生活",
    "🛒 買い物・用事",
    "🚗 移動",
    "🎨 創作",
    "🏃 運動",
    "✨ その他",
]

STATUS_WAITING = "⏳ 未完了"
STATUS_DONE = "✅ 完了"

RESULT_EARLY = "😲 思ったより早かった"
RESULT_CLOSE = "🎯 だいたい予想通り"
RESULT_LATE = "🐢 思ったよりかかった"


# =========================================================
# 共通関数
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
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()
    except (ValueError, TypeError):
        return None


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime("%Y/%m/%d")


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value
        )
    except (ValueError, TypeError):
        return None


def format_minutes(minutes):
    if minutes is None:
        return "-"

    minutes = int(
        round(minutes)
    )

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    rest = minutes % 60

    if rest == 0:
        return f"{hours}時間"

    return (
        f"{hours}時間{rest}分"
    )


def classify_result(
    estimate,
    actual,
):
    if not estimate or estimate <= 0:
        return ""

    ratio = actual / estimate

    if ratio < 0.9:
        return RESULT_EARLY

    if ratio <= 1.1:
        return RESULT_CLOSE

    return RESULT_LATE


def difference_text(
    estimate,
    actual,
):
    difference = actual - estimate

    if difference < 0:
        return (
            f"😲 予想より"
            f"{format_minutes(abs(difference))}"
            "早かった！"
        )

    if difference > 0:
        return (
            f"🐢 予想より"
            f"{format_minutes(difference)}"
            "長くかかった"
        )

    return "🎯 予想ぴったり！"


def ratio_percent(
    estimate,
    actual,
):
    if not estimate:
        return 0

    return (
        actual
        / estimate
        * 100
    )


def correction_factor(
    items,
):
    completed = [
        item
        for item in items
        if item.get(
            "status"
        ) == STATUS_DONE
        and item.get(
            "estimate_minutes",
            0,
        ) > 0
        and item.get(
            "actual_minutes",
            0,
        ) > 0
    ]

    if not completed:
        return None

    total_estimate = sum(
        item.get(
            "estimate_minutes",
            0,
        )
        for item in completed
    )

    total_actual = sum(
        item.get(
            "actual_minutes",
            0,
        )
        for item in completed
    )

    if total_estimate == 0:
        return None

    return (
        total_actual
        / total_estimate
    )


def factor_message(factor):
    if factor is None:
        return "まだデータがありません"

    if factor < 0.9:
        return "予想より短く終わる傾向"

    if factor <= 1.1:
        return "かなり正確！"

    return "予想より長くかかる傾向"


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "tasks": [],
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


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = empty_data()
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
            data = empty_data()

        data.setdefault(
            "tasks",
            [],
        )

        for item in data["tasks"]:
            if not item.get("id"):
                item["id"] = create_id()

            item.setdefault(
                "task",
                "",
            )
            item.setdefault(
                "category",
                "✨ その他",
            )
            item.setdefault(
                "task_date",
                today_text(),
            )
            item.setdefault(
                "estimate_minutes",
                30,
            )
            item.setdefault(
                "actual_minutes",
                None,
            )
            item.setdefault(
                "difficulty",
                3,
            )
            item.setdefault(
                "status",
                STATUS_WAITING,
            )
            item.setdefault(
                "result",
                "",
            )
            item.setdefault(
                "started_at",
                None,
            )
            item.setdefault(
                "completed_at",
                None,
            )
            item.setdefault(
                "memo",
                "",
            )
            item.setdefault(
                "favorite",
                False,
            )
            item.setdefault(
                "created_at",
                now_text(),
            )
            item.setdefault(
                "updated_at",
                item.get(
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
        data = empty_data()
        save_data(data)
        return data


# =========================================================
# 取得
# =========================================================

def get_task(
    data,
    task_id,
):
    return next(
        (
            item
            for item in data["tasks"]
            if item.get("id")
            == task_id
        ),
        None,
    )


def completed_tasks(data):
    return [
        item
        for item in data["tasks"]
        if item.get(
            "status"
        ) == STATUS_DONE
        and item.get(
            "actual_minutes"
        ) is not None
    ]


# =========================================================
# CRUD
# =========================================================

def add_task(
    data,
    task,
    category,
    task_date,
    estimate_minutes,
    difficulty,
    memo,
):
    item = {
        "id": create_id(),
        "task": task,
        "category": category,
        "task_date": str(
            task_date
        ),
        "estimate_minutes": int(
            estimate_minutes
        ),
        "actual_minutes": None,
        "difficulty": int(
            difficulty
        ),
        "status": STATUS_WAITING,
        "result": "",
        "started_at": None,
        "completed_at": None,
        "memo": memo,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["tasks"].append(
        item
    )

    save_data(data)


def start_timer(
    data,
    task_id,
):
    item = get_task(
        data,
        task_id,
    )

    if not item:
        return

    item[
        "started_at"
    ] = now_text()

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def cancel_timer(
    data,
    task_id,
):
    item = get_task(
        data,
        task_id,
    )

    if not item:
        return

    item[
        "started_at"
    ] = None

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def complete_task(
    data,
    task_id,
    actual_minutes,
):
    item = get_task(
        data,
        task_id,
    )

    if not item:
        return

    actual_minutes = max(
        1,
        int(
            round(
                actual_minutes
            )
        ),
    )

    estimate = item.get(
        "estimate_minutes",
        0,
    )

    item[
        "actual_minutes"
    ] = actual_minutes

    item[
        "result"
    ] = classify_result(
        estimate,
        actual_minutes,
    )

    item[
        "status"
    ] = STATUS_DONE

    item[
        "completed_at"
    ] = now_text()

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def complete_from_timer(
    data,
    task_id,
):
    item = get_task(
        data,
        task_id,
    )

    if not item:
        return

    started_at = parse_datetime(
        item.get(
            "started_at"
        )
    )

    if not started_at:
        return

    elapsed_seconds = (
        datetime.now()
        - started_at
    ).total_seconds()

    elapsed_minutes = max(
        1,
        round(
            elapsed_seconds
            / 60
        ),
    )

    complete_task(
        data,
        task_id,
        elapsed_minutes,
    )


def toggle_favorite(
    data,
    task_id,
):
    item = get_task(
        data,
        task_id,
    )

    if not item:
        return

    item[
        "favorite"
    ] = not item.get(
        "favorite",
        False,
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_task(
    data,
    task_id,
    task,
    category,
    task_date,
    estimate_minutes,
    actual_minutes,
    difficulty,
    memo,
):
    item = get_task(
        data,
        task_id,
    )

    if not item:
        return

    item["task"] = task
    item[
        "category"
    ] = category
    item[
        "task_date"
    ] = str(
        task_date
    )
    item[
        "estimate_minutes"
    ] = int(
        estimate_minutes
    )
    item[
        "difficulty"
    ] = int(
        difficulty
    )
    item["memo"] = memo

    if (
        actual_minutes is not None
        and actual_minutes > 0
    ):
        actual_minutes = int(
            actual_minutes
        )

        item[
            "actual_minutes"
        ] = actual_minutes

        item[
            "status"
        ] = STATUS_DONE

        item[
            "result"
        ] = classify_result(
            int(
                estimate_minutes
            ),
            actual_minutes,
        )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_task(
    data,
    task_id,
):
    data["tasks"] = [
        item
        for item in data["tasks"]
        if item.get("id")
        != task_id
    ]

    save_data(data)


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
        background: rgba(90, 150, 220, 0.07);
        border: 1px solid rgba(90, 150, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(70, 150, 230, 0.18),
                rgba(250, 180, 80, 0.10)
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

    .result-card {
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(120, 120, 120, 0.18);
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

tasks = data["tasks"]
done_tasks = completed_tasks(
    data
)

today = date.today()
month_prefix = today.strftime(
    "%Y-%m"
)

waiting_tasks = [
    item
    for item in tasks
    if item.get(
        "status"
    ) == STATUS_WAITING
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⏱️ 思ったより早かった！</h1>
        <p>
            「時間がかかりそう」と、
            実際にかかった時間を比べてみよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

st.subheader(
    "🧠 あなたの時間感覚"
)

overall_factor = (
    correction_factor(
        done_tasks
    )
)

if done_tasks:
    average_estimate = sum(
        item.get(
            "estimate_minutes",
            0,
        )
        for item in done_tasks
    ) / len(done_tasks)

    average_actual = sum(
        item.get(
            "actual_minutes",
            0,
        )
        for item in done_tasks
    ) / len(done_tasks)

else:
    average_estimate = 0
    average_actual = 0

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "✅ 完了",
    f"{len(done_tasks)}件",
)

col2.metric(
    "🧠 平均予想",
    format_minutes(
        average_estimate
    ),
)

col3.metric(
    "⏱️ 平均実績",
    format_minutes(
        average_actual
    ),
)

col4.metric(
    "🔧 補正値",
    (
        f"×{overall_factor:.2f}"
        if overall_factor
        is not None
        else "-"
    ),
)

if overall_factor is not None:
    st.info(
        f"💡 全体では、実際の時間は"
        f"予想の約"
        f"{overall_factor * 100:.0f}%です。"
        f" {factor_message(overall_factor)}"
    )


# =========================================================
# 新しい作業
# =========================================================

st.divider()

st.subheader(
    "➕ 新しい時間予想"
)

with st.form(
    "new_task_form",
    clear_on_submit=True,
):
    task = st.text_input(
        "📝 何をする？",
        placeholder=(
            "例：部屋を片付ける"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

        task_date = st.date_input(
            "📅 日付",
            value=today,
            max_value=today,
        )

    with col2:
        estimate_minutes = (
            st.number_input(
                "🧠 何分かかると思う？",
                min_value=1,
                max_value=1440,
                value=30,
                step=5,
            )
        )

        difficulty = st.slider(
            "😵 やる前の面倒くささ",
            min_value=1,
            max_value=5,
            value=3,
        )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "予想した理由や"
            "作業条件など"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🧠 予想を記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not task.strip():
            st.warning(
                "作業名を入力してね。"
            )

        else:
            add_task(
                data=data,
                task=task.strip(),
                category=category,
                task_date=task_date,
                estimate_minutes=(
                    estimate_minutes
                ),
                difficulty=difficulty,
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# 未完了
# =========================================================

st.divider()

st.subheader(
    "⏳ これからやる"
)

if not waiting_tasks:
    st.success(
        "現在、未完了の作業はありません！"
    )

else:
    for item in sorted(
        waiting_tasks,
        key=lambda row: (
            row.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        task_id = item.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [8, 1]
                )
            )

            with col1:
                st.subheader(
                    item.get(
                        "task",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "waiting_fav_"
                        + task_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        task_id,
                    )
                    st.rerun()

            st.caption(
                format_date(
                    item.get(
                        "task_date"
                    )
                )
                + " ｜ "
                + item.get(
                    "category",
                    "",
                )
                + " ｜ "
                + (
                    "😵"
                    * item.get(
                        "difficulty",
                        3,
                    )
                )
            )

            st.metric(
                "🧠 予想時間",
                format_minutes(
                    item.get(
                        "estimate_minutes"
                    )
                ),
            )

            category_items = [
                done
                for done in done_tasks
                if done.get(
                    "category"
                ) == item.get(
                    "category"
                )
            ]

            category_factor = (
                correction_factor(
                    category_items
                )
            )

            if category_factor:
                adjusted = (
                    item.get(
                        "estimate_minutes",
                        0,
                    )
                    * category_factor
                )

                st.caption(
                    f"🔮 過去の"
                    f"{item.get('category', '')}"
                    f"補正値 ×{category_factor:.2f}"
                    f" → 約"
                    f"{format_minutes(adjusted)}"
                )

            started_at = (
                parse_datetime(
                    item.get(
                        "started_at"
                    )
                )
            )

            if started_at:
                elapsed = (
                    datetime.now()
                    - started_at
                ).total_seconds() / 60

                st.warning(
                    "⏱️ タイマー計測中"
                    f" ｜ 現在約"
                    f"{format_minutes(elapsed)}"
                )

                col1, col2 = (
                    st.columns(2)
                )

                with col1:
                    if st.button(
                        "🏁 タイマーで完了",
                        key=(
                            "timer_finish_"
                            + task_id
                        ),
                        type="primary",
                        use_container_width=True,
                    ):
                        complete_from_timer(
                            data,
                            task_id,
                        )
                        st.rerun()

                with col2:
                    if st.button(
                        "↩️ タイマー取消",
                        key=(
                            "timer_cancel_"
                            + task_id
                        ),
                        use_container_width=True,
                    ):
                        cancel_timer(
                            data,
                            task_id,
                        )
                        st.rerun()

            else:
                if st.button(
                    "▶️ タイマー開始",
                    key=(
                        "timer_start_"
                        + task_id
                    ),
                    use_container_width=True,
                ):
                    start_timer(
                        data,
                        task_id,
                    )
                    st.rerun()

            with st.expander(
                "✍️ 実際の時間を手動入力"
            ):
                actual_minutes = (
                    st.number_input(
                        "⏱️ 実際は何分？",
                        min_value=1,
                        max_value=1440,
                        value=int(
                            item.get(
                                "estimate_minutes",
                                30,
                            )
                        ),
                        step=1,
                        key=(
                            "actual_"
                            + task_id
                        ),
                    )
                )

                if st.button(
                    "✅ 完了する",
                    key=(
                        "manual_finish_"
                        + task_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    complete_task(
                        data,
                        task_id,
                        actual_minutes,
                    )
                    st.rerun()


# =========================================================
# 最近の結果
# =========================================================

if done_tasks:
    st.divider()

    st.subheader(
        "📋 最近の結果"
    )

    recent = sorted(
        done_tasks,
        key=lambda row: (
            row.get(
                "completed_at",
                "",
            )
        ),
        reverse=True,
    )[:10]

    for item in recent:
        task_id = item.get(
            "id",
            "",
        )

        estimate = item.get(
            "estimate_minutes",
            0,
        )

        actual = item.get(
            "actual_minutes",
            0,
        )

        ratio = ratio_percent(
            estimate,
            actual,
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [8, 1]
                )
            )

            with col1:
                st.write(
                    "**"
                    + item.get(
                        "task",
                        ""
                    )
                    + "**"
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "done_fav_"
                        + task_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        task_id,
                    )
                    st.rerun()

            st.caption(
                item.get(
                    "category",
                    "",
                )
                + " ｜ "
                + format_date(
                    item.get(
                        "task_date"
                    )
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "🧠 予想",
                format_minutes(
                    estimate
                ),
            )

            col2.metric(
                "⏱️ 実際",
                format_minutes(
                    actual
                ),
            )

            col3.metric(
                "📊 実際 / 予想",
                f"{ratio:.0f}%",
            )

            st.write(
                "**"
                + item.get(
                    "result",
                    ""
                )
                + "**"
            )

            st.caption(
                difference_text(
                    estimate,
                    actual,
                )
            )


# =========================================================
# カテゴリー別補正値
# =========================================================

if done_tasks:
    st.divider()

    st.subheader(
        "🏷️ カテゴリー別の時間感覚"
    )

    category_rows = []

    for category in CATEGORIES:
        category_items = [
            item
            for item in done_tasks
            if item.get(
                "category"
            ) == category
        ]

        if not category_items:
            continue

        factor = correction_factor(
            category_items
        )

        average_est = sum(
            item.get(
                "estimate_minutes",
                0,
            )
            for item in category_items
        ) / len(
            category_items
        )

        average_act = sum(
            item.get(
                "actual_minutes",
                0,
            )
            for item in category_items
        ) / len(
            category_items
        )

        category_rows.append(
            {
                "カテゴリー": category,
                "件数": len(
                    category_items
                ),
                "平均予想(分)": round(
                    average_est,
                    1,
                ),
                "平均実績(分)": round(
                    average_act,
                    1,
                ),
                "補正値": round(
                    factor,
                    2,
                ),
                "傾向": factor_message(
                    factor
                ),
            }
        )

    if category_rows:
        category_df = (
            pd.DataFrame(
                category_rows
            )
            .sort_values(
                "補正値"
            )
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        chart_df = (
            category_df[
                [
                    "カテゴリー",
                    "補正値",
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
# 補正後予測
# =========================================================

st.divider()

st.subheader(
    "🔮 じゃあ実際どれくらい？"
)

predict_col1, predict_col2 = (
    st.columns(2)
)

with predict_col1:
    predict_category = (
        st.selectbox(
            "カテゴリー",
            CATEGORIES,
            key="predict_category",
        )
    )

with predict_col2:
    predict_minutes = (
        st.number_input(
            "自分の予想（分）",
            min_value=1,
            max_value=1440,
            value=60,
            step=5,
            key="predict_minutes",
        )
    )

predict_items = [
    item
    for item in done_tasks
    if item.get(
        "category"
    ) == predict_category
]

predict_factor = (
    correction_factor(
        predict_items
    )
)

if predict_factor is None:
    st.info(
        "🌱 このカテゴリーは"
        "まだデータがありません。"
        "まず何件か記録してみよう。"
    )

else:
    predicted_actual = (
        predict_minutes
        * predict_factor
    )

    st.metric(
        "💡 補正後の予測",
        format_minutes(
            predicted_actual
        ),
    )

    st.caption(
        f"{predict_category}の"
        f"過去{len(predict_items)}件から"
        f"補正値 ×{predict_factor:.2f} "
        "で計算しています。"
    )

    if len(
        predict_items
    ) < 5:
        st.caption(
            "🌱 まだデータが少ないので、"
            "参考程度に見てね。"
        )


# =========================================================
# 面倒度分析
# =========================================================

if done_tasks:
    st.divider()

    st.subheader(
        "😵 面倒くささと時間予想"
    )

    difficulty_rows = []

    for difficulty in range(
        1,
        6,
    ):
        items = [
            item
            for item in done_tasks
            if item.get(
                "difficulty"
            ) == difficulty
        ]

        if not items:
            continue

        factor = correction_factor(
            items
        )

        average_est = sum(
            item.get(
                "estimate_minutes",
                0,
            )
            for item in items
        ) / len(items)

        average_act = sum(
            item.get(
                "actual_minutes",
                0,
            )
            for item in items
        ) / len(items)

        difficulty_rows.append(
            {
                "面倒度": (
                    "★" * difficulty
                ),
                "件数": len(items),
                "平均予想(分)": round(
                    average_est,
                    1,
                ),
                "平均実績(分)": round(
                    average_act,
                    1,
                ),
                "補正値": round(
                    factor,
                    2,
                ),
            }
        )

    if difficulty_rows:
        st.dataframe(
            pd.DataFrame(
                difficulty_rows
            ),
            hide_index=True,
            use_container_width=True,
        )

        high_difficulty = [
            item
            for item in done_tasks
            if item.get(
                "difficulty",
                0,
            ) >= 4
        ]

        high_factor = (
            correction_factor(
                high_difficulty
            )
        )

        if (
            high_factor is not None
            and len(
                high_difficulty
            ) >= 3
        ):
            if high_factor < 0.8:
                st.info(
                    "💡 面倒度★★★★以上の"
                    "作業は、実際には予想より"
                    "かなり短く終わる傾向があります。"
                )

            elif high_factor > 1.2:
                st.info(
                    "💡 面倒度★★★★以上の"
                    "作業は、実際にも"
                    "長くかかる傾向があります。"
                )


# =========================================================
# ランキング
# =========================================================

if done_tasks:
    st.divider()

    col1, col2 = st.columns(2)

    early_items = [
        item
        for item in done_tasks
        if (
            item.get(
                "estimate_minutes",
                0,
            )
            - item.get(
                "actual_minutes",
                0,
            )
        ) > 0
    ]

    early_items.sort(
        key=lambda item: (
            item.get(
                "estimate_minutes",
                0,
            )
            - item.get(
                "actual_minutes",
                0,
            )
        ),
        reverse=True,
    )

    late_items = [
        item
        for item in done_tasks
        if (
            item.get(
                "actual_minutes",
                0,
            )
            - item.get(
                "estimate_minutes",
                0,
            )
        ) > 0
    ]

    late_items.sort(
        key=lambda item: (
            item.get(
                "actual_minutes",
                0,
            )
            - item.get(
                "estimate_minutes",
                0,
            )
        ),
        reverse=True,
    )

    with col1:
        st.subheader(
            "🏆 思ったより早かった"
        )

        if not early_items:
            st.caption(
                "まだ記録がありません。"
            )

        for rank, item in enumerate(
            early_items[:5],
            start=1,
        ):
            difference = (
                item.get(
                    "estimate_minutes",
                    0,
                )
                - item.get(
                    "actual_minutes",
                    0,
                )
            )

            st.write(
                f"**{rank}. "
                f"{item.get('task', '')}**"
            )

            st.caption(
                f"予想 "
                f"{format_minutes(item.get('estimate_minutes'))}"
                f" → 実際 "
                f"{format_minutes(item.get('actual_minutes'))}"
                f" ｜ "
                f"{format_minutes(difference)}短い"
            )

    with col2:
        st.subheader(
            "🐢 思ったよりかかった"
        )

        if not late_items:
            st.caption(
                "まだ記録がありません。"
            )

        for rank, item in enumerate(
            late_items[:5],
            start=1,
        ):
            difference = (
                item.get(
                    "actual_minutes",
                    0,
                )
                - item.get(
                    "estimate_minutes",
                    0,
                )
            )

            st.write(
                f"**{rank}. "
                f"{item.get('task', '')}**"
            )

            st.caption(
                f"予想 "
                f"{format_minutes(item.get('estimate_minutes'))}"
                f" → 実際 "
                f"{format_minutes(item.get('actual_minutes'))}"
                f" ｜ +"
                f"{format_minutes(difference)}"
            )


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {today.month}月"
)

month_tasks = [
    item
    for item in done_tasks
    if (
        item.get(
            "task_date",
            "",
        )
        or ""
    ).startswith(
        month_prefix
    )
]

if not month_tasks:
    st.info(
        "今月の完了記録は"
        "まだありません。"
    )

else:
    month_estimate = sum(
        item.get(
            "estimate_minutes",
            0,
        )
        for item in month_tasks
    )

    month_actual = sum(
        item.get(
            "actual_minutes",
            0,
        )
        for item in month_tasks
    )

    early_count = sum(
        1
        for item in month_tasks
        if item.get(
            "result"
        ) == RESULT_EARLY
    )

    close_count = sum(
        1
        for item in month_tasks
        if item.get(
            "result"
        ) == RESULT_CLOSE
    )

    late_count = sum(
        1
        for item in month_tasks
        if item.get(
            "result"
        ) == RESULT_LATE
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    col1.metric(
        "✅ 完了",
        f"{len(month_tasks)}件",
    )

    col2.metric(
        "🧠 予想合計",
        format_minutes(
            month_estimate
        ),
    )

    col3.metric(
        "⏱️ 実績合計",
        format_minutes(
            month_actual
        ),
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    col1.metric(
        "😲 早かった",
        f"{early_count}件",
    )

    col2.metric(
        "🎯 予想通り",
        f"{close_count}件",
    )

    col3.metric(
        "🐢 長かった",
        f"{late_count}件",
    )

    difference = (
        month_actual
        - month_estimate
    )

    if difference < 0:
        st.caption(
            "📊 今月の実績合計は、"
            "予想合計より"
            f"{format_minutes(abs(difference))}"
            "短くなっています。"
        )

    elif difference > 0:
        st.caption(
            "📊 今月の実績合計は、"
            "予想合計より"
            f"{format_minutes(difference)}"
            "長くなっています。"
        )

    else:
        st.caption(
            "🎯 今月の予想合計と"
            "実績合計は同じです。"
        )


# =========================================================
# 過去ガチャ
# =========================================================

old_tasks = []

for item in done_tasks:
    task_date = parse_date(
        item.get(
            "task_date"
        )
    )

    if (
        task_date
        and (
            today
            - task_date
        ).days >= 30
    ):
        old_tasks.append(
            item
        )

if old_tasks:
    st.divider()

    st.subheader(
        "🎲 昔こんな予想してました"
    )

    old_ids = [
        item.get(
            "id"
        )
        for item in old_tasks
    ]

    random_id = (
        st.session_state.get(
            "random_time_task"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_time_task"
        ] = random_id

    random_item = get_task(
        data,
        random_id,
    )

    if random_item:
        with st.container(
            border=True
        ):
            st.caption(
                format_date(
                    random_item.get(
                        "task_date"
                    )
                )
                + " ｜ "
                + random_item.get(
                    "category",
                    "",
                )
            )

            st.subheader(
                random_item.get(
                    "task",
                    "",
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            col1.metric(
                "🧠 当時の予想",
                format_minutes(
                    random_item.get(
                        "estimate_minutes"
                    )
                ),
            )

            col2.metric(
                "⏱️ 実際",
                format_minutes(
                    random_item.get(
                        "actual_minutes"
                    )
                ),
            )

            st.write(
                "**"
                + random_item.get(
                    "result",
                    ""
                )
                + "**"
            )

            st.caption(
                difference_text(
                    random_item.get(
                        "estimate_minutes",
                        0,
                    ),
                    random_item.get(
                        "actual_minutes",
                        0,
                    ),
                )
            )

            st.write(
                "😵 当時の面倒度："
                + "★"
                * random_item.get(
                    "difficulty",
                    3,
                )
            )

        if st.button(
            "🎲 別の記録を見る",
            use_container_width=True,
        ):
            alternatives = [
                item_id
                for item_id in old_ids
                if item_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_time_task"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 時間予想図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 時間予想図鑑"
)

search_text = st.text_input(
    "🔎 作業を検索",
    placeholder=(
        "掃除、Python、買い物……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="library_category",
        )
    )

with col2:
    result_filter = (
        st.selectbox(
            "結果",
            [
                "すべて",
                RESULT_EARLY,
                RESULT_CLOSE,
                RESULT_LATE,
                STATUS_WAITING,
            ],
            key="library_result",
        )
    )

filtered = []

for item in tasks:
    if (
        category_filter
        != "すべて"
        and item.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        result_filter
        == STATUS_WAITING
        and item.get(
            "status"
        ) != STATUS_WAITING
    ):
        continue

    if (
        result_filter
        not in [
            "すべて",
            STATUS_WAITING,
        ]
        and item.get(
            "result"
        ) != result_filter
    ):
        continue

    searchable = " ".join(
        [
            item.get(
                "task",
                "",
            ),
            item.get(
                "memo",
                "",
            ),
            item.get(
                "category",
                "",
            ),
        ]
    ).lower()

    if (
        search_text.strip()
        and search_text
        .strip()
        .lower()
        not in searchable
    ):
        continue

    filtered.append(
        item
    )

if not filtered:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    rows = []

    for item in sorted(
        filtered,
        key=lambda row: (
            row.get(
                "task_date",
                "",
            )
        ),
        reverse=True,
    ):
        estimate = item.get(
            "estimate_minutes",
            0,
        )

        actual = item.get(
            "actual_minutes"
        )

        if actual:
            difference = (
                actual
                - estimate
            )

            difference_value = (
                f"{difference:+d}分"
            )

            ratio_value = (
                f"{ratio_percent(estimate, actual):.0f}%"
            )

        else:
            difference_value = "-"
            ratio_value = "-"

        rows.append(
            {
                "日付": format_date(
                    item.get(
                        "task_date"
                    )
                ),
                "作業": item.get(
                    "task",
                    "",
                ),
                "カテゴリー": item.get(
                    "category",
                    "",
                ),
                "予想": format_minutes(
                    estimate
                ),
                "実際": (
                    format_minutes(
                        actual
                    )
                    if actual
                    else "-"
                ),
                "差": difference_value,
                "比率": ratio_value,
                "結果": (
                    item.get(
                        "result",
                        ""
                    )
                    or STATUS_WAITING
                ),
                "⭐": (
                    "⭐"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            rows
        ),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・削除"
):
    if not tasks:
        st.caption(
            "まだ記録がありません。"
        )

    for item in sorted(
        tasks,
        key=lambda row: (
            row.get(
                "task_date",
                "",
            ),
            row.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    ):
        task_id = item.get(
            "id",
            "",
        )

        with st.expander(
            f"{format_date(item.get('task_date'))}"
            f" ｜ "
            f"{item.get('task', '')}"
        ):
            edit_task = (
                st.text_input(
                    "作業名",
                    value=item.get(
                        "task",
                        "",
                    ),
                    key=(
                        "edit_task_"
                        + task_id
                    ),
                )
            )

            old_category = (
                item.get(
                    "category",
                    "✨ その他",
                )
            )

            category_index = (
                CATEGORIES.index(
                    old_category
                )
                if old_category
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
                        + task_id
                    ),
                )
            )

            current_date = (
                parse_date(
                    item.get(
                        "task_date"
                    )
                )
                or today
            )

            edit_date = (
                st.date_input(
                    "日付",
                    value=current_date,
                    max_value=today,
                    key=(
                        "edit_date_"
                        + task_id
                    ),
                )
            )

            edit_estimate = (
                st.number_input(
                    "予想時間（分）",
                    min_value=1,
                    max_value=1440,
                    value=int(
                        item.get(
                            "estimate_minutes",
                            30,
                        )
                    ),
                    key=(
                        "edit_estimate_"
                        + task_id
                    ),
                )
            )

            current_actual = (
                item.get(
                    "actual_minutes"
                )
            )

            edit_actual = (
                st.number_input(
                    "実際の時間（分）",
                    min_value=0,
                    max_value=1440,
                    value=int(
                        current_actual
                        or 0
                    ),
                    help=(
                        "未完了なら0のままでOK"
                    ),
                    key=(
                        "edit_actual_"
                        + task_id
                    ),
                )
            )

            edit_difficulty = (
                st.slider(
                    "面倒度",
                    min_value=1,
                    max_value=5,
                    value=int(
                        item.get(
                            "difficulty",
                            3,
                        )
                    ),
                    key=(
                        "edit_difficulty_"
                        + task_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "メモ",
                    value=item.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + task_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_"
                        + task_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not edit_task.strip():
                        st.warning(
                            "作業名を入力してね。"
                        )

                    else:
                        update_task(
                            data=data,
                            task_id=task_id,
                            task=(
                                edit_task.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            task_date=(
                                edit_date
                            ),
                            estimate_minutes=(
                                edit_estimate
                            ),
                            actual_minutes=(
                                edit_actual
                                if edit_actual > 0
                                else None
                            ),
                            difficulty=(
                                edit_difficulty
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "fav_"
                        + task_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        task_id,
                    )
                    st.rerun()

            st.markdown(
                "#### 🗑️ 完全削除"
            )

            confirm = st.checkbox(
                "この記録を削除する",
                key=(
                    "confirm_"
                    + task_id
                ),
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + task_id
                ),
                disabled=not confirm,
                use_container_width=True,
            ):
                delete_task(
                    data,
                    task_id,
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
            "time_estimate_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "⏱️ 「時間がかかりそう」は、"
    "まだ予想にすぎない。"
)

st.caption(
    "🧠 記録するほど、"
    "自分の時間感覚は正確になっていく。"
)
