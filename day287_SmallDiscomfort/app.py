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
    page_title="今日の小さな違和感",
    page_icon="🤔",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "discomfort.json",
)

CATEGORIES = [
    "🏠 生活",
    "💼 仕事",
    "📚 勉強",
    "💻 アプリ・開発",
    "👥 人間関係",
    "💰 お金",
    "🧠 自分",
    "🛠️ モノ・環境",
    "✨ その他",
]

STATUSES = [
    "👀 様子を見る",
    "🔧 改善中",
    "💭 あとで考える",
    "🎉 解消",
]

EXPERIMENT_RESULTS = [
    "🎉 改善した",
    "🌱 少し改善",
    "😐 変わらない",
    "😣 悪化した",
]


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


def days_from(value):
    parsed = parse_date(value)

    if not parsed:
        return 0

    return max(
        (date.today() - parsed).days,
        0,
    )


def average(values):
    values = [
        float(value)
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1,
    )


def level_stars(level):
    level = int(level or 0)

    return (
        "★" * level
        + "☆" * (5 - level)
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "items": [],
        "occurrences": [],
        "experiments": [],
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
            "items",
            [],
        )
        data.setdefault(
            "occurrences",
            [],
        )
        data.setdefault(
            "experiments",
            [],
        )

        for item in data["items"]:
            item.setdefault(
                "id",
                create_id(),
            )
            item.setdefault(
                "title",
                "",
            )
            item.setdefault(
                "category",
                "✨ その他",
            )
            item.setdefault(
                "first_date",
                today_text(),
            )
            item.setdefault(
                "last_date",
                item.get(
                    "first_date",
                    today_text(),
                ),
            )
            item.setdefault(
                "level",
                3,
            )
            item.setdefault(
                "status",
                "👀 様子を見る",
            )
            item.setdefault(
                "memo",
                "",
            )
            item.setdefault(
                "resolution_note",
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
# CRUD
# =========================================================

def get_item(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data["items"]
            if item.get("id") == item_id
        ),
        None,
    )


def get_occurrences(
    data,
    item_id,
):
    return [
        occurrence
        for occurrence
        in data["occurrences"]
        if occurrence.get(
            "item_id"
        ) == item_id
    ]


def get_experiments(
    data,
    item_id,
):
    return [
        experiment
        for experiment
        in data["experiments"]
        if experiment.get(
            "item_id"
        ) == item_id
    ]


def occurrence_count(
    data,
    item_id,
):
    # 初回登録も1回として数える
    return (
        len(
            get_occurrences(
                data,
                item_id,
            )
        )
        + 1
    )


def add_item(
    data,
    title,
    category,
    level,
    memo,
    first_date,
    status,
):
    item = {
        "id": create_id(),
        "title": title,
        "category": category,
        "first_date": str(
            first_date
        ),
        "last_date": str(
            first_date
        ),
        "level": int(level),
        "status": status,
        "memo": memo,
        "resolution_note": "",
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["items"].append(
        item
    )

    save_data(data)


def add_occurrence(
    data,
    item_id,
    level,
    note,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    occurrence = {
        "id": create_id(),
        "item_id": item_id,
        "occurrence_date": today_text(),
        "level": int(level),
        "note": note,
        "created_at": now_text(),
    }

    data["occurrences"].append(
        occurrence
    )

    item["last_date"] = today_text()
    item["level"] = int(level)
    item["updated_at"] = now_text()

    # 解消後に再発した場合
    if item.get(
        "status"
    ) == "🎉 解消":
        item["status"] = (
            "👀 様子を見る"
        )
        item[
            "resolution_note"
        ] = ""

    save_data(data)


def update_item(
    data,
    item_id,
    title,
    category,
    level,
    memo,
    first_date,
    last_date,
    status,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["title"] = title
    item["category"] = category
    item["level"] = int(level)
    item["memo"] = memo
    item["first_date"] = str(
        first_date
    )
    item["last_date"] = str(
        last_date
    )
    item["status"] = status
    item["updated_at"] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    item_id,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["favorite"] = not item.get(
        "favorite",
        False,
    )

    item["updated_at"] = now_text()

    save_data(data)


def set_status(
    data,
    item_id,
    status,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = status
    item["updated_at"] = now_text()

    save_data(data)


def resolve_item(
    data,
    item_id,
    note,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = "🎉 解消"
    item["resolution_note"] = note
    item["updated_at"] = now_text()

    save_data(data)


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item in data["items"]
        if item.get("id") != item_id
    ]

    data["occurrences"] = [
        occurrence
        for occurrence
        in data["occurrences"]
        if occurrence.get(
            "item_id"
        ) != item_id
    ]

    data["experiments"] = [
        experiment
        for experiment
        in data["experiments"]
        if experiment.get(
            "item_id"
        ) != item_id
    ]

    save_data(data)


def delete_occurrence(
    data,
    occurrence_id,
):
    data["occurrences"] = [
        occurrence
        for occurrence
        in data["occurrences"]
        if occurrence.get(
            "id"
        ) != occurrence_id
    ]

    save_data(data)


# =========================================================
# 改善実験
# =========================================================

def start_experiment(
    data,
    item_id,
    action,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    experiment = {
        "id": create_id(),
        "item_id": item_id,
        "action": action,
        "start_date": today_text(),
        "end_date": None,
        "result": None,
        "result_note": "",
        "before_count": occurrence_count(
            data,
            item_id,
        ),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["experiments"].append(
        experiment
    )

    item["status"] = "🔧 改善中"
    item["updated_at"] = now_text()

    save_data(data)


def finish_experiment(
    data,
    experiment_id,
    result,
    result_note,
):
    experiment = next(
        (
            exp
            for exp in data["experiments"]
            if exp.get(
                "id"
            ) == experiment_id
        ),
        None,
    )

    if not experiment:
        return

    experiment["end_date"] = today_text()
    experiment["result"] = result
    experiment["result_note"] = (
        result_note
    )
    experiment["updated_at"] = now_text()

    item = get_item(
        data,
        experiment.get(
            "item_id"
        ),
    )

    if item:
        if result in [
            "🎉 改善した",
            "🌱 少し改善",
        ]:
            item["status"] = (
                "👀 様子を見る"
            )
        else:
            item["status"] = (
                "💭 あとで考える"
            )

        item["updated_at"] = now_text()

    save_data(data)


# =========================================================
# 違和感スコア
# =========================================================

def discomfort_score(
    data,
    item,
):
    item_id = item.get(
        "id",
        "",
    )

    count = occurrence_count(
        data,
        item_id,
    )

    repeats = max(
        count - 1,
        0,
    )

    repeat_score = min(
        repeats * 10,
        40,
    )

    item_occurrences = (
        get_occurrences(
            data,
            item_id,
        )
    )

    levels = [
        int(
            item.get(
                "level",
                3,
            )
        )
    ]

    levels += [
        int(
            occurrence.get(
                "level",
                3,
            )
        )
        for occurrence
        in item_occurrences
    ]

    avg_level = average(
        levels
    )

    level_score = (
        avg_level / 5
    ) * 30

    last_days = days_from(
        item.get(
            "last_date"
        )
    )

    if last_days == 0:
        recent_score = 15
    elif last_days <= 7:
        recent_score = 12
    elif last_days <= 30:
        recent_score = 6
    else:
        recent_score = 0

    duration = days_from(
        item.get(
            "first_date"
        )
    )

    if duration >= 90:
        duration_score = 15
    elif duration >= 30:
        duration_score = 10
    elif duration >= 7:
        duration_score = 5
    else:
        duration_score = 0

    score = (
        repeat_score
        + level_score
        + recent_score
        + duration_score
    )

    return min(
        round(score),
        100,
    )


def score_label(score):
    if score >= 80:
        return (
            "🚨 そろそろ向き合いたい"
        )

    if score >= 60:
        return (
            "⚠️ 繰り返しています"
        )

    if score >= 40:
        return (
            "🤔 少し気になる"
        )

    return (
        "🌱 小さな違和感"
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
        background: rgba(120, 150, 210, 0.07);
        border: 1px solid rgba(120, 150, 210, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(120, 150, 220, 0.18),
                rgba(130, 210, 180, 0.08)
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

    .score-big {
        font-size: 2rem;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

items = data["items"]
occurrences = data["occurrences"]
experiments = data["experiments"]

active_items = [
    item
    for item in items
    if item.get(
        "status"
    ) != "🎉 解消"
]

resolved_items = [
    item
    for item in items
    if item.get(
        "status"
    ) == "🎉 解消"
]

active_experiments = [
    experiment
    for experiment in experiments
    if not experiment.get(
        "result"
    )
]

finished_experiments = [
    experiment
    for experiment in experiments
    if experiment.get(
        "result"
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🤔 今日の小さな違和感</h1>
        <p>
            小さな違和感は、
            まだ言葉になっていない改善のヒント。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

high_score_items = [
    item
    for item in active_items
    if discomfort_score(
        data,
        item,
    ) >= 60
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🤔 気になる",
    f"{len(active_items)}個",
)

col2.metric(
    "⚠️ 繰り返し",
    f"{len(high_score_items)}個",
)

col3.metric(
    "🔧 改善実験中",
    f"{len(active_experiments)}件",
)

col4.metric(
    "🎉 解消",
    f"{len(resolved_items)}個",
)


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "🤔 小さな違和感を記録"
)

with st.form(
    "new_discomfort",
    clear_on_submit=True,
):
    title = st.text_input(
        "🔎 どんな違和感？",
        placeholder=(
            "例：朝、家を出るまで"
            "妙に時間がかかる"
        ),
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        category = (
            st.selectbox(
                "🏷️ カテゴリー",
                CATEGORIES,
            )
        )

        level = (
            st.select_slider(
                "🤔 違和感レベル",
                options=[
                    1,
                    2,
                    3,
                    4,
                    5,
                ],
                value=3,
                format_func=(
                    level_stars
                ),
            )
        )

    with col2:
        first_date = (
            st.date_input(
                "📅 気づいた日",
                value=date.today(),
                max_value=date.today(),
            )
        )

        initial_status = (
            st.selectbox(
                "どうする？",
                [
                    "👀 様子を見る",
                    "💭 あとで考える",
                ],
            )
        )

    memo = st.text_area(
        "📝 ひとこと",
        placeholder=(
            "例：最近10分くらい"
            "遅くなっている気がする"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🤔 違和感を記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "違和感を入力してね。"
            )

        else:
            add_item(
                data=data,
                title=title.strip(),
                category=category,
                level=level,
                memo=memo.strip(),
                first_date=first_date,
                status=initial_status,
            )

            st.rerun()


# =========================================================
# ランキング
# =========================================================

st.divider()

st.subheader(
    "🔥 今、気になる違和感"
)

if not active_items:
    st.info(
        "今のところ、記録された違和感はありません。"
    )

else:
    ranked_items = sorted(
        active_items,
        key=lambda item: (
            discomfort_score(
                data,
                item,
            ),
            occurrence_count(
                data,
                item.get(
                    "id"
                ),
            ),
        ),
        reverse=True,
    )

    for rank, item in enumerate(
        ranked_items,
        start=1,
    ):
        item_id = item.get(
            "id",
            "",
        )

        score = discomfort_score(
            data,
            item,
        )

        count = occurrence_count(
            data,
            item_id,
        )

        duration = days_from(
            item.get(
                "first_date"
            )
        )

        medal = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
        }.get(
            rank,
            f"{rank}.",
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [7, 1]
                )
            )

            with col1:
                st.subheader(
                    f"{medal} "
                    f"{item.get('title', '')}"
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
                        "favorite_"
                        + item_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )

                    st.rerun()

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ "
                f"{item.get('status', '')}"
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "⚠️ スコア",
                f"{score}pt",
            )

            col2.metric(
                "🔁 発生",
                f"{count}回",
            )

            col3.metric(
                "📅 継続",
                f"{duration}日",
            )

            st.progress(
                score / 100
            )

            st.caption(
                score_label(
                    score
                )
            )

            st.write(
                "現在の違和感："
                f" **{level_stars(item.get('level', 3))}**"
            )

            if item.get(
                "memo"
            ):
                st.write(
                    "📝 "
                    + item.get(
                        "memo",
                        "",
                    )
                )

            if score >= 60:
                st.warning(
                    "⚠️ この違和感は"
                    "繰り返しています。"
                    "一度、原因や改善方法を"
                    "考えてみてもよさそうです。"
                )

            # -----------------------------------------
            # また感じた
            # -----------------------------------------

            with st.expander(
                "🤔 また感じた"
            ):
                new_level = (
                    st.select_slider(
                        "今回の違和感",
                        options=[
                            1,
                            2,
                            3,
                            4,
                            5,
                        ],
                        value=int(
                            item.get(
                                "level",
                                3,
                            )
                        ),
                        format_func=(
                            level_stars
                        ),
                        key=(
                            "new_level_"
                            + item_id
                        ),
                    )
                )

                note = st.text_area(
                    "今回はどうだった？",
                    key=(
                        "occurrence_note_"
                        + item_id
                    ),
                    placeholder=(
                        "例：今日は特に"
                        "時間がかかった"
                    ),
                )

                if st.button(
                    "🤔 再発を記録",
                    key=(
                        "occur_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    add_occurrence(
                        data,
                        item_id,
                        new_level,
                        note.strip(),
                    )

                    st.rerun()

            # -----------------------------------------
            # 改善実験
            # -----------------------------------------

            with st.expander(
                "🔧 改善してみる"
            ):
                action = st.text_input(
                    "試してみること",
                    key=(
                        "experiment_action_"
                        + item_id
                    ),
                    placeholder=(
                        "例：前日に服を準備する"
                    ),
                )

                if st.button(
                    "🔧 改善実験スタート",
                    key=(
                        "start_exp_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    already_active = any(
                        experiment.get(
                            "item_id"
                        ) == item_id
                        and not experiment.get(
                            "result"
                        )
                        for experiment
                        in experiments
                    )

                    if already_active:
                        st.warning(
                            "この違和感では"
                            "すでに改善実験中です。"
                        )

                    elif not action.strip():
                        st.warning(
                            "試すことを入力してね。"
                        )

                    else:
                        start_experiment(
                            data,
                            item_id,
                            action.strip(),
                        )

                        st.rerun()

            # -----------------------------------------
            # 状態変更
            # -----------------------------------------

            with st.expander(
                "🧭 状態を変える"
            ):
                col1, col2 = (
                    st.columns(2)
                )

                with col1:
                    if st.button(
                        "👀 様子を見る",
                        key=(
                            "watch_"
                            + item_id
                        ),
                        use_container_width=True,
                    ):
                        set_status(
                            data,
                            item_id,
                            "👀 様子を見る",
                        )

                        st.rerun()

                with col2:
                    if st.button(
                        "💭 あとで考える",
                        key=(
                            "later_"
                            + item_id
                        ),
                        use_container_width=True,
                    ):
                        set_status(
                            data,
                            item_id,
                            "💭 あとで考える",
                        )

                        st.rerun()

            # -----------------------------------------
            # 解消
            # -----------------------------------------

            with st.expander(
                "🎉 解消した"
            ):
                resolution_note = (
                    st.text_area(
                        "どう解消した？",
                        key=(
                            "resolution_"
                            + item_id
                        ),
                        placeholder=(
                            "例：やり方を変えたら"
                            "気にならなくなった"
                        ),
                    )
                )

                if st.button(
                    "🎉 解消済みにする",
                    key=(
                        "resolve_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    resolve_item(
                        data,
                        item_id,
                        resolution_note.strip(),
                    )

                    st.rerun()


# =========================================================
# 改善実験中
# =========================================================

if active_experiments:
    st.divider()

    st.subheader(
        "🔬 改善実験中"
    )

    for experiment in (
        active_experiments
    ):
        experiment_id = (
            experiment.get(
                "id",
                "",
            )
        )

        item = get_item(
            data,
            experiment.get(
                "item_id"
            ),
        )

        if not item:
            continue

        item_id = item.get(
            "id",
            "",
        )

        start_date = (
            parse_date(
                experiment.get(
                    "start_date"
                )
            )
        )

        experiment_days = (
            (
                date.today()
                - start_date
            ).days
            if start_date
            else 0
        )

        before_count = int(
            experiment.get(
                "before_count",
                0,
            )
        )

        current_count = (
            occurrence_count(
                data,
                item_id,
            )
        )

        after_count = max(
            current_count
            - before_count,
            0,
        )

        with st.container(
            border=True
        ):
            st.subheader(
                item.get(
                    "title",
                    "",
                )
            )

            st.write(
                "🔧 **試していること**"
            )

            st.write(
                experiment.get(
                    "action",
                    "",
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "📅 経過",
                f"{experiment_days}日",
            )

            col2.metric(
                "開始前の累計",
                f"{before_count}回",
            )

            col3.metric(
                "開始後の再発",
                f"{after_count}回",
            )

            st.caption(
                "※ 開始前と開始後では"
                "期間が異なるため、"
                "回数は参考値です。"
            )

            result = (
                st.selectbox(
                    "改善した？",
                    EXPERIMENT_RESULTS,
                    key=(
                        "exp_result_"
                        + experiment_id
                    ),
                )
            )

            result_note = (
                st.text_area(
                    "結果メモ",
                    key=(
                        "exp_note_"
                        + experiment_id
                    ),
                    placeholder=(
                        "例：朝の準備が"
                        "少し早くなった"
                    ),
                )
            )

            if st.button(
                "🔬 実験結果を記録",
                key=(
                    "finish_exp_"
                    + experiment_id
                ),
                type="primary",
                use_container_width=True,
            ):
                finish_experiment(
                    data,
                    experiment_id,
                    result,
                    result_note.strip(),
                )

                st.rerun()


# =========================================================
# 最近出ていない違和感
# =========================================================

quiet_items = [
    item
    for item in active_items
    if days_from(
        item.get(
            "last_date"
        )
    ) >= 30
]

if quiet_items:
    st.divider()

    st.subheader(
        "🌿 最近、この違和感出てないね"
    )

    quiet_items = sorted(
        quiet_items,
        key=lambda item: (
            days_from(
                item.get(
                    "last_date"
                )
            )
        ),
        reverse=True,
    )

    for item in quiet_items:
        item_id = item.get(
            "id",
            "",
        )

        quiet_days = days_from(
            item.get(
                "last_date"
            )
        )

        with st.container(
            border=True
        ):
            st.write(
                f"**{item.get('title', '')}**"
            )

            st.write(
                f"最後に感じたのは"
                f" **{quiet_days}日前**"
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "🎉 解消した",
                    key=(
                        "quiet_resolve_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    resolve_item(
                        data,
                        item_id,
                        "しばらく再発していないため解消",
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "👀 まだ様子を見る",
                    key=(
                        "quiet_watch_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    set_status(
                        data,
                        item_id,
                        "👀 様子を見る",
                    )

                    st.rerun()


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月の違和感"
)

month_prefix = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_items = [
    item
    for item in items
    if (
        item.get(
            "first_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_occurrences = [
    occurrence
    for occurrence in occurrences
    if (
        occurrence.get(
            "occurrence_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_experiments = [
    experiment
    for experiment in experiments
    if (
        experiment.get(
            "start_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_resolved = [
    item
    for item in resolved_items
    if (
        item.get(
            "updated_at",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🆕 新しく発見",
    f"{len(month_items)}個",
)

col2.metric(
    "🔁 再発",
    f"{len(month_occurrences)}回",
)

col3.metric(
    "🔧 改善実験",
    f"{len(month_experiments)}件",
)

col4.metric(
    "🎉 解消",
    f"{len(month_resolved)}個",
)


# =========================================================
# カテゴリー分析
# =========================================================

if items:
    category_counts = {}

    for item in items:
        category = item.get(
            "category",
            "✨ その他",
        )

        category_counts[
            category
        ] = (
            category_counts.get(
                category,
                0,
            )
            + occurrence_count(
                data,
                item.get(
                    "id"
                ),
            )
        )

    category_df = (
        pd.DataFrame(
            [
                {
                    "カテゴリー": key,
                    "発生回数": value,
                }
                for key, value
                in category_counts.items()
            ]
        )
        .sort_values(
            "発生回数",
            ascending=False,
        )
    )

    st.markdown(
        "### 🧭 違和感が多い分野"
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )


# =========================================================
# 改善成功率
# =========================================================

if finished_experiments:
    st.divider()

    st.subheader(
        "🔬 改善実験の結果"
    )

    result_counts = {
        result: 0
        for result
        in EXPERIMENT_RESULTS
    }

    for experiment in (
        finished_experiments
    ):
        result = experiment.get(
            "result"
        )

        if result in result_counts:
            result_counts[
                result
            ] += 1

    improved_count = (
        result_counts[
            "🎉 改善した"
        ]
        + result_counts[
            "🌱 少し改善"
        ]
    )

    improvement_rate = (
        improved_count
        / len(
            finished_experiments
        )
        * 100
    )

    col1, col2 = (
        st.columns(2)
    )

    col1.metric(
        "🔬 実験数",
        f"{len(finished_experiments)}回",
    )

    col2.metric(
        "🎉 改善率",
        f"{improvement_rate:.0f}%",
    )

    result_df = pd.DataFrame(
        [
            {
                "結果": key,
                "件数": value,
            }
            for key, value
            in result_counts.items()
        ]
    )

    st.bar_chart(
        result_df.set_index(
            "結果"
        )
    )


# =========================================================
# 違和感から生まれた改善
# =========================================================

successful_experiments = [
    experiment
    for experiment
    in finished_experiments
    if experiment.get(
        "result"
    )
    in [
        "🎉 改善した",
        "🌱 少し改善",
    ]
]

if successful_experiments:
    st.divider()

    st.subheader(
        "💡 違和感から生まれた改善"
    )

    for experiment in reversed(
        successful_experiments[
            -10:
        ]
    ):
        item = get_item(
            data,
            experiment.get(
                "item_id"
            ),
        )

        if not item:
            continue

        with st.container(
            border=True
        ):
            st.write(
                "🤔 **"
                + item.get(
                    "title",
                    "",
                )
                + "**"
            )

            st.write("↓")

            st.write(
                "🔧 "
                + experiment.get(
                    "action",
                    "",
                )
            )

            st.write("↓")

            st.success(
                experiment.get(
                    "result",
                    "",
                )
            )

            if experiment.get(
                "result_note"
            ):
                st.caption(
                    experiment.get(
                        "result_note",
                        "",
                    )
                )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    item
    for item in items
    if item.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 覚えておきたい違和感"
    )

    for item in favorites:
        with st.container(
            border=True
        ):
            st.write(
                f"**{item.get('title', '')}**"
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ "
                f"{item.get('status', '')}"
                f" ｜ "
                f"⚠️ {discomfort_score(data, item)}pt"
            )


# =========================================================
# 違和感図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 違和感図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "朝、アプリ、仕事……"
    ),
)

col1, col2, col3 = (
    st.columns(3)
)

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
    status_filter = (
        st.selectbox(
            "状態",
            ["すべて"]
            + STATUSES,
            key="library_status",
        )
    )

with col3:
    level_filter = (
        st.selectbox(
            "違和感レベル",
            [
                "すべて",
                "★★★★★",
                "★★★★☆以上",
                "★★★☆☆以上",
            ],
            key="library_level",
        )
    )


filtered_items = []

for item in items:
    if (
        category_filter
        != "すべて"
        and item.get(
            "category"
        )
        != category_filter
    ):
        continue

    if (
        status_filter
        != "すべて"
        and item.get(
            "status"
        )
        != status_filter
    ):
        continue

    level = int(
        item.get(
            "level",
            0,
        )
    )

    if (
        level_filter
        == "★★★★★"
        and level != 5
    ):
        continue

    if (
        level_filter
        == "★★★★☆以上"
        and level < 4
    ):
        continue

    if (
        level_filter
        == "★★★☆☆以上"
        and level < 3
    ):
        continue

    searchable = " ".join(
        [
            item.get(
                "title",
                "",
            ),
            item.get(
                "category",
                "",
            ),
            item.get(
                "memo",
                "",
            ),
            item.get(
                "resolution_note",
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

    filtered_items.append(
        item
    )


if not filtered_items:
    st.info(
        "条件に合う違和感はありません。"
    )

else:
    rows = []

    for item in sorted(
        filtered_items,
        key=lambda row: (
            discomfort_score(
                data,
                row,
            )
        ),
        reverse=True,
    ):
        rows.append(
            {
                "違和感": item.get(
                    "title",
                    "",
                ),
                "カテゴリー": item.get(
                    "category",
                    "",
                ),
                "状態": item.get(
                    "status",
                    "",
                ),
                "レベル": level_stars(
                    item.get(
                        "level",
                        3,
                    )
                ),
                "発生": (
                    f"{occurrence_count(data, item.get('id'))}回"
                ),
                "スコア": (
                    f"{discomfort_score(data, item)}pt"
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
# 編集・履歴・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・履歴・削除"
):
    if not items:
        st.caption(
            "まだ記録がありません。"
        )

    for item in sorted(
        items,
        key=lambda row: (
            row.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    ):
        item_id = item.get(
            "id",
            "",
        )

        with st.expander(
            item.get(
                "title",
                "",
            )
        ):
            edit_title = (
                st.text_input(
                    "違和感",
                    value=item.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + item_id
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
                        + item_id
                    ),
                )
            )

            edit_level = (
                st.select_slider(
                    "現在の違和感",
                    options=[
                        1,
                        2,
                        3,
                        4,
                        5,
                    ],
                    value=int(
                        item.get(
                            "level",
                            3,
                        )
                    ),
                    format_func=(
                        level_stars
                    ),
                    key=(
                        "edit_level_"
                        + item_id
                    ),
                )
            )

            old_status = item.get(
                "status",
                "👀 様子を見る",
            )

            status_index = (
                STATUSES.index(
                    old_status
                )
                if old_status
                in STATUSES
                else 0
            )

            edit_status = (
                st.selectbox(
                    "状態",
                    STATUSES,
                    index=status_index,
                    key=(
                        "edit_status_"
                        + item_id
                    ),
                )
            )

            first_value = (
                parse_date(
                    item.get(
                        "first_date"
                    )
                )
                or date.today()
            )

            last_value = (
                parse_date(
                    item.get(
                        "last_date"
                    )
                )
                or date.today()
            )

            edit_first = (
                st.date_input(
                    "最初に気づいた日",
                    value=first_value,
                    max_value=date.today(),
                    key=(
                        "edit_first_"
                        + item_id
                    ),
                )
            )

            edit_last = (
                st.date_input(
                    "最後に感じた日",
                    value=last_value,
                    max_value=date.today(),
                    key=(
                        "edit_last_"
                        + item_id
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
                        + item_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "違和感を入力してね。"
                        )

                    elif (
                        edit_last
                        < edit_first
                    ):
                        st.warning(
                            "最後の日は"
                            "最初の日以降にしてね。"
                        )

                    else:
                        update_item(
                            data,
                            item_id,
                            edit_title.strip(),
                            edit_category,
                            edit_level,
                            edit_memo.strip(),
                            edit_first,
                            edit_last,
                            edit_status,
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
                        "manage_favorite_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )

                    st.rerun()

            # -----------------------------------------
            # 再発履歴
            # -----------------------------------------

            item_occurrences = sorted(
                get_occurrences(
                    data,
                    item_id,
                ),
                key=lambda row: (
                    row.get(
                        "created_at",
                        "",
                    )
                ),
                reverse=True,
            )

            if item_occurrences:
                st.markdown(
                    "#### 🔁 再発履歴"
                )

                for occurrence in (
                    item_occurrences
                ):
                    occurrence_id = (
                        occurrence.get(
                            "id",
                            "",
                        )
                    )

                    col1, col2 = (
                        st.columns(
                            [7, 1]
                        )
                    )

                    with col1:
                        st.write(
                            f"🤔 "
                            f"{format_date(occurrence.get('occurrence_date'))}"
                            f" ｜ "
                            f"{level_stars(occurrence.get('level', 3))}"
                        )

                        if occurrence.get(
                            "note"
                        ):
                            st.caption(
                                occurrence.get(
                                    "note",
                                    "",
                                )
                            )

                    with col2:
                        if st.button(
                            "🗑️",
                            key=(
                                "delete_occ_"
                                + occurrence_id
                            ),
                        ):
                            delete_occurrence(
                                data,
                                occurrence_id,
                            )

                            st.rerun()

            # -----------------------------------------
            # 改善実験履歴
            # -----------------------------------------

            item_experiments = (
                get_experiments(
                    data,
                    item_id,
                )
            )

            if item_experiments:
                st.markdown(
                    "#### 🔬 改善実験履歴"
                )

                for experiment in (
                    item_experiments
                ):
                    st.write(
                        "🔧 **"
                        + experiment.get(
                            "action",
                            "",
                        )
                        + "**"
                    )

                    st.caption(
                        "開始："
                        + format_date(
                            experiment.get(
                                "start_date"
                            )
                        )
                        + (
                            " ｜ 終了："
                            + format_date(
                                experiment.get(
                                    "end_date"
                                )
                            )
                            if experiment.get(
                                "end_date"
                            )
                            else " ｜ 実験中"
                        )
                    )

                    if experiment.get(
                        "result"
                    ):
                        st.write(
                            experiment.get(
                                "result",
                                "",
                            )
                        )

                    if experiment.get(
                        "result_note"
                    ):
                        st.caption(
                            experiment.get(
                                "result_note",
                                "",
                            )
                        )

            if item.get(
                "resolution_note"
            ):
                st.markdown(
                    "#### 🎉 解消メモ"
                )

                st.write(
                    item.get(
                        "resolution_note",
                        "",
                    )
                )

            confirm_delete = (
                st.checkbox(
                    "この違和感と"
                    "すべての履歴を削除する",
                    key=(
                        "confirm_delete_"
                        + item_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + item_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_item(
                    data,
                    item_id,
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
            "small_discomfort_"
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
    "🔎 小さな違和感は、"
    "まだ言葉になっていない改善のヒント。"
)
