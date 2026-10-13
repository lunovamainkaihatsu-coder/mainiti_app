import json
import os
import random
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日、何を諦めなかった？",
    page_icon="🔥",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "challenges.json",
)

CATEGORIES = [
    "📚 勉強",
    "💻 開発",
    "💼 仕事",
    "🏃 運動",
    "🎨 創作",
    "🏠 生活",
    "👥 人間関係",
    "🎯 目標",
    "✨ その他",
]

START_STATES = [
    "😵 全然できなかった",
    "😣 うまくいかなかった",
    "🤔 分からなかった",
    "🚧 途中で止まった",
    "😴 やる気が出なかった",
    "💥 失敗した",
    "✨ その他",
]

ACTIONS = [
    "🔄 もう一回やった",
    "📖 調べた",
    "💬 誰かに聞いた",
    "🧩 やり方を変えた",
    "🪜 小さく分けた",
    "⏰ 時間を変えた",
    "🛠️ 道具を変えた",
    "🧘 一度休んで戻った",
    "✨ その他",
]

RESULTS = [
    "🏆 できた！",
    "🌱 少し進んだ",
    "🔄 まだ挑戦中",
    "🍃 今回はここまで",
]

ACTIVE_RESULTS = [
    "🌱 少し進んだ",
    "🔄 まだ挑戦中",
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


def days_between_dates(
    start_value,
    end_value=None,
):
    start_date = parse_date(
        start_value
    )

    end_date = (
        parse_date(end_value)
        if end_value
        else date.today()
    )

    if not start_date:
        return 0

    if not end_date:
        end_date = date.today()

    return max(
        (end_date - start_date).days,
        0,
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "challenges": [],
        "attempts": [],
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
            "challenges",
            [],
        )

        data.setdefault(
            "attempts",
            [],
        )

        for challenge in data[
            "challenges"
        ]:
            challenge.setdefault(
                "id",
                create_id(),
            )
            challenge.setdefault(
                "title",
                "",
            )
            challenge.setdefault(
                "category",
                "✨ その他",
            )
            challenge.setdefault(
                "start_state",
                "😣 うまくいかなかった",
            )
            challenge.setdefault(
                "first_date",
                today_text(),
            )
            challenge.setdefault(
                "last_date",
                challenge.get(
                    "first_date",
                    today_text(),
                ),
            )
            challenge.setdefault(
                "status",
                "🔄 まだ挑戦中",
            )
            challenge.setdefault(
                "memo",
                "",
            )
            challenge.setdefault(
                "favorite",
                False,
            )
            challenge.setdefault(
                "completed_date",
                None,
            )
            challenge.setdefault(
                "created_at",
                now_text(),
            )
            challenge.setdefault(
                "updated_at",
                challenge.get(
                    "created_at",
                    now_text(),
                ),
            )

        for attempt in data[
            "attempts"
        ]:
            attempt.setdefault(
                "id",
                create_id(),
            )
            attempt.setdefault(
                "challenge_id",
                "",
            )
            attempt.setdefault(
                "attempt_date",
                today_text(),
            )
            attempt.setdefault(
                "actions",
                [],
            )
            attempt.setdefault(
                "count",
                1,
            )
            attempt.setdefault(
                "result",
                "🔄 まだ挑戦中",
            )
            attempt.setdefault(
                "note",
                "",
            )
            attempt.setdefault(
                "created_at",
                now_text(),
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
# 取得関数
# =========================================================

def get_challenge(
    data,
    challenge_id,
):
    return next(
        (
            challenge
            for challenge
            in data["challenges"]
            if challenge.get(
                "id"
            ) == challenge_id
        ),
        None,
    )


def get_attempts(
    data,
    challenge_id,
):
    return [
        attempt
        for attempt
        in data["attempts"]
        if attempt.get(
            "challenge_id"
        ) == challenge_id
    ]


def sorted_attempts(
    data,
    challenge_id,
):
    return sorted(
        get_attempts(
            data,
            challenge_id,
        ),
        key=lambda attempt: (
            attempt.get(
                "attempt_date",
                "",
            ),
            attempt.get(
                "created_at",
                "",
            ),
        ),
    )


def total_attempt_count(
    data,
    challenge_id,
):
    return sum(
        int(
            attempt.get(
                "count",
                1,
            )
        )
        for attempt
        in get_attempts(
            data,
            challenge_id,
        )
    )


def challenge_days(
    data,
    challenge_id,
):
    dates = {
        attempt.get(
            "attempt_date"
        )
        for attempt
        in get_attempts(
            data,
            challenge_id,
        )
        if attempt.get(
            "attempt_date"
        )
    }

    return len(dates)


def comeback_count(
    data,
    challenge_id,
):
    # 最初に挑戦した日は
    # 「戻ってきた」には含めない
    return max(
        challenge_days(
            data,
            challenge_id,
        ) - 1,
        0,
    )


def small_progress_count(
    data,
    challenge_id,
):
    return sum(
        1
        for attempt
        in get_attempts(
            data,
            challenge_id,
        )
        if attempt.get(
            "result"
        ) == "🌱 少し進んだ"
    )


# =========================================================
# CRUD
# =========================================================

def add_challenge(
    data,
    title,
    category,
    start_state,
    first_date,
    first_actions,
    attempt_count,
    result,
    note,
    memo,
):
    challenge_id = create_id()

    challenge = {
        "id": challenge_id,
        "title": title,
        "category": category,
        "start_state": (
            start_state
        ),
        "first_date": str(
            first_date
        ),
        "last_date": str(
            first_date
        ),
        "status": result,
        "memo": memo,
        "favorite": False,
        "completed_date": (
            str(first_date)
            if result
            == "🏆 できた!"
            else None
        ),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    # 表記ゆれ防止
    if result == "🏆 できた！":
        challenge[
            "completed_date"
        ] = str(
            first_date
        )

    data["challenges"].append(
        challenge
    )

    attempt = {
        "id": create_id(),
        "challenge_id": (
            challenge_id
        ),
        "attempt_date": str(
            first_date
        ),
        "actions": (
            first_actions
        ),
        "count": int(
            attempt_count
        ),
        "result": result,
        "note": note,
        "created_at": now_text(),
    }

    data["attempts"].append(
        attempt
    )

    save_data(data)


def add_attempt(
    data,
    challenge_id,
    attempt_date,
    actions,
    count,
    result,
    note,
):
    challenge = get_challenge(
        data,
        challenge_id,
    )

    if not challenge:
        return

    attempt = {
        "id": create_id(),
        "challenge_id": (
            challenge_id
        ),
        "attempt_date": str(
            attempt_date
        ),
        "actions": actions,
        "count": int(count),
        "result": result,
        "note": note,
        "created_at": now_text(),
    }

    data["attempts"].append(
        attempt
    )

    challenge[
        "last_date"
    ] = str(
        attempt_date
    )

    challenge[
        "status"
    ] = result

    if result == "🏆 できた！":
        challenge[
            "completed_date"
        ] = str(
            attempt_date
        )

    elif result in ACTIVE_RESULTS:
        challenge[
            "completed_date"
        ] = None

    challenge[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_challenge(
    data,
    challenge_id,
    title,
    category,
    start_state,
    first_date,
    memo,
):
    challenge = get_challenge(
        data,
        challenge_id,
    )

    if not challenge:
        return

    challenge["title"] = title
    challenge[
        "category"
    ] = category
    challenge[
        "start_state"
    ] = start_state
    challenge[
        "first_date"
    ] = str(
        first_date
    )
    challenge["memo"] = memo
    challenge[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    challenge_id,
):
    challenge = get_challenge(
        data,
        challenge_id,
    )

    if not challenge:
        return

    challenge[
        "favorite"
    ] = not challenge.get(
        "favorite",
        False,
    )

    challenge[
        "updated_at"
    ] = now_text()

    save_data(data)


def reopen_challenge(
    data,
    challenge_id,
):
    challenge = get_challenge(
        data,
        challenge_id,
    )

    if not challenge:
        return

    challenge[
        "status"
    ] = "🔄 まだ挑戦中"

    challenge[
        "completed_date"
    ] = None

    challenge[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_challenge(
    data,
    challenge_id,
):
    data[
        "challenges"
    ] = [
        challenge
        for challenge
        in data["challenges"]
        if challenge.get(
            "id"
        ) != challenge_id
    ]

    data[
        "attempts"
    ] = [
        attempt
        for attempt
        in data["attempts"]
        if attempt.get(
            "challenge_id"
        ) != challenge_id
    ]

    save_data(data)


def delete_attempt(
    data,
    attempt_id,
):
    target = next(
        (
            attempt
            for attempt
            in data["attempts"]
            if attempt.get(
                "id"
            ) == attempt_id
        ),
        None,
    )

    if not target:
        return

    challenge_id = target.get(
        "challenge_id"
    )

    data[
        "attempts"
    ] = [
        attempt
        for attempt
        in data["attempts"]
        if attempt.get(
            "id"
        ) != attempt_id
    ]

    challenge = get_challenge(
        data,
        challenge_id,
    )

    if challenge:
        remaining = sorted_attempts(
            data,
            challenge_id,
        )

        if remaining:
            latest = remaining[-1]

            challenge[
                "last_date"
            ] = latest.get(
                "attempt_date"
            )

            challenge[
                "status"
            ] = latest.get(
                "result",
                "🔄 まだ挑戦中",
            )

            if (
                latest.get(
                    "result"
                )
                == "🏆 できた！"
            ):
                challenge[
                    "completed_date"
                ] = latest.get(
                    "attempt_date"
                )
            else:
                challenge[
                    "completed_date"
                ] = None

        challenge[
            "updated_at"
        ] = now_text()

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
        background: rgba(255, 120, 70, 0.07);
        border: 1px solid rgba(255, 120, 70, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(255, 110, 60, 0.18),
                rgba(255, 195, 80, 0.10)
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

challenges = data[
    "challenges"
]

attempts = data[
    "attempts"
]

active_challenges = [
    challenge
    for challenge
    in challenges
    if challenge.get(
        "status"
    )
    in ACTIVE_RESULTS
]

completed_challenges = [
    challenge
    for challenge
    in challenges
    if challenge.get(
        "status"
    ) == "🏆 できた！"
]

archived_challenges = [
    challenge
    for challenge
    in challenges
    if challenge.get(
        "status"
    ) == "🍃 今回はここまで"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🔥 今日、何を諦めなかった？</h1>
        <p>
            できた回数ではなく、
            戻ってきた回数を数える。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

all_attempts = sum(
    int(
        attempt.get(
            "count",
            1,
        )
    )
    for attempt in attempts
)

all_comebacks = sum(
    comeback_count(
        data,
        challenge.get(
            "id"
        ),
    )
    for challenge
    in challenges
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🔥 挑戦テーマ",
    f"{len(challenges)}個",
)

col2.metric(
    "🔄 総挑戦回数",
    f"{all_attempts}回",
)

col3.metric(
    "🌱 戻ってきた",
    f"{all_comebacks}回",
)

col4.metric(
    "🏆 達成",
    f"{len(completed_challenges)}個",
)


# =========================================================
# 新しい挑戦
# =========================================================

st.divider()

st.subheader(
    "🔥 今日、諦めなかったこと"
)

with st.form(
    "new_challenge",
    clear_on_submit=True,
):
    title = st.text_input(
        "何に挑戦した？",
        placeholder=(
            "例：Pythonの問題が"
            "分からなかった"
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

        start_state = (
            st.selectbox(
                "最初はどうだった？",
                START_STATES,
            )
        )

        first_date = (
            st.date_input(
                "📅 挑戦した日",
                value=date.today(),
                max_value=date.today(),
            )
        )

    with col2:
        selected_actions = (
            st.multiselect(
                "今日はどうした？",
                ACTIONS,
                default=[
                    "🔄 もう一回やった"
                ],
            )
        )

        attempt_count = (
            st.number_input(
                "🔥 今日の挑戦回数",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
            )
        )

        result = (
            st.selectbox(
                "今日どうなった？",
                RESULTS,
                index=1,
            )
        )

    note = st.text_area(
        "🌱 今日の記録",
        placeholder=(
            "例：continueの意味までは"
            "分かってきた"
        ),
    )

    memo = st.text_area(
        "📝 テーマ全体のメモ",
        placeholder=(
            "この挑戦について"
            "覚えておきたいこと"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🔥 挑戦を記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "挑戦したことを入力してね。"
            )

        else:
            add_challenge(
                data=data,
                title=title.strip(),
                category=category,
                start_state=(
                    start_state
                ),
                first_date=(
                    first_date
                ),
                first_actions=(
                    selected_actions
                ),
                attempt_count=(
                    attempt_count
                ),
                result=result,
                note=note.strip(),
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# 挑戦中
# =========================================================

st.divider()

st.subheader(
    "🌱 今も挑戦していること"
)

if not active_challenges:
    st.info(
        "現在挑戦中のテーマはありません。"
    )

else:
    active_sorted = sorted(
        active_challenges,
        key=lambda challenge: (
            challenge.get(
                "last_date",
                "",
            )
        ),
        reverse=True,
    )

    for challenge in active_sorted:
        challenge_id = (
            challenge.get(
                "id",
                "",
            )
        )

        total = (
            total_attempt_count(
                data,
                challenge_id,
            )
        )

        days_count = (
            challenge_days(
                data,
                challenge_id,
            )
        )

        comebacks = (
            comeback_count(
                data,
                challenge_id,
            )
        )

        duration = (
            days_between_dates(
                challenge.get(
                    "first_date"
                )
            )
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
                    challenge.get(
                        "title",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if challenge.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "fav_active_"
                        + challenge_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        challenge_id,
                    )

                    st.rerun()

            st.caption(
                f"{challenge.get('category', '')}"
                f" ｜ "
                f"{challenge.get('status', '')}"
            )

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            col1.metric(
                "🔥 挑戦",
                f"{total}回",
            )

            col2.metric(
                "📅 挑戦した日",
                f"{days_count}日",
            )

            col3.metric(
                "🌱 戻ってきた",
                f"{comebacks}回",
            )

            col4.metric(
                "⏳ 継続期間",
                f"{duration}日",
            )

            st.write(
                "最初："
                f"**{challenge.get('start_state', '')}**"
            )

            if challenge.get(
                "memo"
            ):
                st.write(
                    "📝 "
                    + challenge.get(
                        "memo",
                        "",
                    )
                )

            # -----------------------------------------
            # また挑戦
            # -----------------------------------------

            with st.expander(
                "🔥 また挑戦した！"
            ):
                attempt_date = (
                    st.date_input(
                        "挑戦日",
                        value=date.today(),
                        max_value=date.today(),
                        key=(
                            "attempt_date_"
                            + challenge_id
                        ),
                    )
                )

                action = (
                    st.multiselect(
                        "今日はどうした？",
                        ACTIONS,
                        key=(
                            "actions_"
                            + challenge_id
                        ),
                    )
                )

                count = (
                    st.number_input(
                        "今日の挑戦回数",
                        min_value=1,
                        max_value=100,
                        value=1,
                        step=1,
                        key=(
                            "attempt_count_"
                            + challenge_id
                        ),
                    )
                )

                attempt_result = (
                    st.selectbox(
                        "結果",
                        RESULTS,
                        index=1,
                        key=(
                            "attempt_result_"
                            + challenge_id
                        ),
                    )
                )

                attempt_note = (
                    st.text_area(
                        "今日の記録",
                        placeholder=(
                            "何が分かった？"
                            "何が変わった？"
                        ),
                        key=(
                            "attempt_note_"
                            + challenge_id
                        ),
                    )
                )

                if st.button(
                    "🔥 挑戦を追加",
                    key=(
                        "add_attempt_"
                        + challenge_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    add_attempt(
                        data=data,
                        challenge_id=(
                            challenge_id
                        ),
                        attempt_date=(
                            attempt_date
                        ),
                        actions=action,
                        count=count,
                        result=(
                            attempt_result
                        ),
                        note=(
                            attempt_note.strip()
                        ),
                    )

                    st.rerun()

            # -----------------------------------------
            # タイムライン
            # -----------------------------------------

            with st.expander(
                "📖 挑戦タイムライン"
            ):
                history = (
                    sorted_attempts(
                        data,
                        challenge_id,
                    )
                )

                for index, attempt in enumerate(
                    history
                ):
                    if index > 0:
                        st.write("↓")

                    st.markdown(
                        f"**{format_date(attempt.get('attempt_date'))}**"
                    )

                    actions_text = (
                        " / ".join(
                            attempt.get(
                                "actions",
                                [],
                            )
                        )
                    )

                    if actions_text:
                        st.write(
                            actions_text
                        )

                    st.write(
                        f"🔥 "
                        f"{attempt.get('count', 1)}回挑戦"
                    )

                    st.write(
                        attempt.get(
                            "result",
                            "",
                        )
                    )

                    if attempt.get(
                        "note"
                    ):
                        st.caption(
                            attempt.get(
                                "note",
                                "",
                            )
                        )


# =========================================================
# 達成した挑戦
# =========================================================

if completed_challenges:
    st.divider()

    st.subheader(
        "🏆 できた！"
    )

    for challenge in sorted(
        completed_challenges,
        key=lambda row: (
            row.get(
                "completed_date",
                "",
            )
        ),
        reverse=True,
    ):
        challenge_id = (
            challenge.get(
                "id",
                "",
            )
        )

        total = (
            total_attempt_count(
                data,
                challenge_id,
            )
        )

        days_count = (
            challenge_days(
                data,
                challenge_id,
            )
        )

        comebacks = (
            comeback_count(
                data,
                challenge_id,
            )
        )

        with st.container(
            border=True
        ):
            st.subheader(
                "🏆 "
                + challenge.get(
                    "title",
                    "",
                )
            )

            st.caption(
                challenge.get(
                    "category",
                    "",
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "🔥 総挑戦回数",
                f"{total}回",
            )

            col2.metric(
                "📅 挑戦した日",
                f"{days_count}日",
            )

            col3.metric(
                "🌱 戻ってきた",
                f"{comebacks}回",
            )

            st.success(
                "🔥 この成功まで、"
                f"あなたは{comebacks}回"
                "戻ってきました。"
            )

            st.caption(
                f"最初："
                f"{format_date(challenge.get('first_date'))}"
                f" ｜ 達成："
                f"{format_date(challenge.get('completed_date'))}"
            )

            st.write(
                "**最初はできなかった。"
                "でも、ここまで来た。**"
            )


# =========================================================
# 今回はここまで
# =========================================================

if archived_challenges:
    st.divider()

    st.subheader(
        "🍃 今回はここまで"
    )

    st.caption(
        "やめることも、ひとつの判断。"
        "また挑戦したくなったら戻れます。"
    )

    for challenge in (
        archived_challenges
    ):
        challenge_id = (
            challenge.get(
                "id",
                "",
            )
        )

        with st.container(
            border=True
        ):
            st.write(
                "**"
                + challenge.get(
                    "title",
                    "",
                )
                + "**"
            )

            st.caption(
                f"{challenge.get('category', '')}"
                f" ｜ "
                f"🔥 {total_attempt_count(data, challenge_id)}回挑戦"
            )

            if st.button(
                "🔥 もう一度挑戦する",
                key=(
                    "reopen_"
                    + challenge_id
                ),
                use_container_width=True,
            ):
                reopen_challenge(
                    data,
                    challenge_id,
                )

                st.rerun()


# =========================================================
# 月間分析
# =========================================================

st.divider()

month_prefix = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_attempts = [
    attempt
    for attempt in attempts
    if (
        attempt.get(
            "attempt_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_challenge_ids = {
    attempt.get(
        "challenge_id"
    )
    for attempt in month_attempts
}

month_total_attempts = sum(
    int(
        attempt.get(
            "count",
            1,
        )
    )
    for attempt in month_attempts
)

month_dates = {
    attempt.get(
        "attempt_date"
    )
    for attempt in month_attempts
}

month_completed_ids = {
    challenge.get(
        "id"
    )
    for challenge
    in completed_challenges
    if (
        challenge.get(
            "completed_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
}

month_progress = sum(
    1
    for attempt in month_attempts
    if attempt.get(
        "result"
    ) == "🌱 少し進んだ"
)

st.subheader(
    f"📊 {date.today().month}月の"
    "「諦めなかった」"
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🔥 挑戦テーマ",
    f"{len(month_challenge_ids)}個",
)

col2.metric(
    "📅 挑戦した日",
    f"{len(month_dates)}日",
)

col3.metric(
    "🔄 総挑戦回数",
    f"{month_total_attempts}回",
)

col4.metric(
    "🏆 達成",
    f"{len(month_completed_ids)}個",
)

st.metric(
    "🌱 「少し進んだ」",
    f"{month_progress}回",
)


# =========================================================
# カテゴリー別
# =========================================================

if month_attempts:
    category_counts = {}

    for attempt in (
        month_attempts
    ):
        challenge = get_challenge(
            data,
            attempt.get(
                "challenge_id"
            ),
        )

        if not challenge:
            continue

        category = (
            challenge.get(
                "category",
                "✨ その他",
            )
        )

        category_counts[
            category
        ] = (
            category_counts.get(
                category,
                0,
            )
            + int(
                attempt.get(
                    "count",
                    1,
                )
            )
        )

    if category_counts:
        category_df = (
            pd.DataFrame(
                [
                    {
                        "カテゴリー": key,
                        "挑戦回数": value,
                    }
                    for key, value
                    in category_counts.items()
                ]
            )
            .sort_values(
                "挑戦回数",
                ascending=False,
            )
        )

        st.markdown(
            "### 🧭 今月の挑戦分野"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# ランキング
# =========================================================

if challenges:
    st.divider()

    st.subheader(
        "🏅 諦めなかったランキング"
    )

    ranking = sorted(
        challenges,
        key=lambda challenge: (
            comeback_count(
                data,
                challenge.get(
                    "id"
                ),
            ),
            total_attempt_count(
                data,
                challenge.get(
                    "id"
                ),
            ),
        ),
        reverse=True,
    )

    for rank, challenge in enumerate(
        ranking[:10],
        start=1,
    ):
        challenge_id = (
            challenge.get(
                "id",
                "",
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

        st.write(
            f"{medal} "
            f"**{challenge.get('title', '')}**"
            f" — 🌱 "
            f"{comeback_count(data, challenge_id)}回戻った"
            f" / 🔥 "
            f"{total_attempt_count(data, challenge_id)}回挑戦"
        )


# =========================================================
# 小さな前進
# =========================================================

progress_attempts = [
    attempt
    for attempt in attempts
    if attempt.get(
        "result"
    ) == "🌱 少し進んだ"
]

if progress_attempts:
    progress_challenge_ids = {
        attempt.get(
            "challenge_id"
        )
        for attempt
        in progress_attempts
    }

    eventually_completed = sum(
        1
        for challenge_id
        in progress_challenge_ids
        if (
            get_challenge(
                data,
                challenge_id,
            )
            and get_challenge(
                data,
                challenge_id,
            ).get(
                "status"
            ) == "🏆 できた！"
        )
    )

    st.divider()

    st.subheader(
        "🌱 小さな前進の積み重ね"
    )

    col1, col2 = (
        st.columns(2)
    )

    col1.metric(
        "🌱 少し進んだ",
        f"{len(progress_attempts)}回",
    )

    col2.metric(
        "🏆 後から達成したテーマ",
        f"{eventually_completed}個",
    )

    st.caption(
        "「少し進んだ」は、"
        "成果ゼロではありません。"
    )


# =========================================================
# 過去の挑戦
# =========================================================

old_attempts = [
    attempt
    for attempt in attempts
    if (
        parse_date(
            attempt.get(
                "attempt_date"
            )
        )
        and (
            date.today()
            - parse_date(
                attempt.get(
                    "attempt_date"
                )
            )
        ).days >= 14
    )
]

if old_attempts:
    st.divider()

    st.subheader(
        "🎲 昔、諦めなかった自分"
    )

    attempt_ids = [
        attempt.get(
            "id"
        )
        for attempt
        in old_attempts
    ]

    random_id = (
        st.session_state.get(
            "random_attempt_id"
        )
    )

    if random_id not in (
        attempt_ids
    ):
        random_id = random.choice(
            attempt_ids
        )

        st.session_state[
            "random_attempt_id"
        ] = random_id

    random_attempt = next(
        (
            attempt
            for attempt
            in old_attempts
            if attempt.get(
                "id"
            ) == random_id
        ),
        None,
    )

    if random_attempt:
        challenge = get_challenge(
            data,
            random_attempt.get(
                "challenge_id"
            ),
        )

        if challenge:
            with st.container(
                border=True
            ):
                st.write(
                    format_date(
                        random_attempt.get(
                            "attempt_date"
                        )
                    )
                )

                st.subheader(
                    "🔥 "
                    + challenge.get(
                        "title",
                        "",
                    )
                )

                actions_text = (
                    " / ".join(
                        random_attempt.get(
                            "actions",
                            [],
                        )
                    )
                )

                if actions_text:
                    st.write(
                        actions_text
                    )

                st.write(
                    random_attempt.get(
                        "result",
                        "",
                    )
                )

                if random_attempt.get(
                    "note"
                ):
                    st.info(
                        random_attempt.get(
                            "note",
                            "",
                        )
                    )

                if (
                    challenge.get(
                        "status"
                    )
                    == "🏆 できた！"
                ):
                    st.success(
                        "🏆 この挑戦は、"
                        "その後達成しました。"
                    )

        if st.button(
            "🎲 別の記録を見る",
            use_container_width=True,
        ):
            alternatives = [
                attempt_id
                for attempt_id
                in attempt_ids
                if attempt_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_attempt_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 挑戦図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 挑戦図鑑"
)

search_text = st.text_input(
    "🔎 挑戦を検索",
    placeholder=(
        "Python、筋トレ、アプリ……"
    ),
)

col1, col2 = (
    st.columns(2)
)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key=(
                "library_category"
            ),
        )
    )

with col2:
    status_filter = (
        st.selectbox(
            "状態",
            ["すべて"]
            + RESULTS,
            key=(
                "library_status"
            ),
        )
    )


filtered = []

for challenge in challenges:
    if (
        category_filter
        != "すべて"
        and challenge.get(
            "category"
        )
        != category_filter
    ):
        continue

    if (
        status_filter
        != "すべて"
        and challenge.get(
            "status"
        )
        != status_filter
    ):
        continue

    searchable = " ".join(
        [
            challenge.get(
                "title",
                "",
            ),
            challenge.get(
                "category",
                "",
            ),
            challenge.get(
                "memo",
                "",
            ),
            challenge.get(
                "start_state",
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
        challenge
    )


if not filtered:
    st.info(
        "条件に合う挑戦はありません。"
    )

else:
    library_rows = []

    for challenge in filtered:
        challenge_id = (
            challenge.get(
                "id"
            )
        )

        library_rows.append(
            {
                "挑戦": (
                    challenge.get(
                        "title",
                        "",
                    )
                ),
                "カテゴリー": (
                    challenge.get(
                        "category",
                        "",
                    )
                ),
                "状態": (
                    challenge.get(
                        "status",
                        "",
                    )
                ),
                "挑戦回数": (
                    total_attempt_count(
                        data,
                        challenge_id,
                    )
                ),
                "挑戦日数": (
                    challenge_days(
                        data,
                        challenge_id,
                    )
                ),
                "戻った回数": (
                    comeback_count(
                        data,
                        challenge_id,
                    )
                ),
                "⭐": (
                    "⭐"
                    if challenge.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    library_df = pd.DataFrame(
        library_rows
    )

    library_df = (
        library_df.sort_values(
            [
                "戻った回数",
                "挑戦回数",
            ],
            ascending=False,
        )
    )

    st.dataframe(
        library_df,
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
    if not challenges:
        st.caption(
            "まだ挑戦がありません。"
        )

    for challenge in sorted(
        challenges,
        key=lambda row: (
            row.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    ):
        challenge_id = (
            challenge.get(
                "id",
                "",
            )
        )

        with st.expander(
            challenge.get(
                "title",
                "",
            )
        ):
            edit_title = (
                st.text_input(
                    "挑戦",
                    value=challenge.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + challenge_id
                    ),
                )
            )

            old_category = (
                challenge.get(
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
                        + challenge_id
                    ),
                )
            )

            old_start_state = (
                challenge.get(
                    "start_state",
                    "😣 うまくいかなかった",
                )
            )

            start_index = (
                START_STATES.index(
                    old_start_state
                )
                if old_start_state
                in START_STATES
                else 0
            )

            edit_start_state = (
                st.selectbox(
                    "最初の状態",
                    START_STATES,
                    index=start_index,
                    key=(
                        "edit_start_"
                        + challenge_id
                    ),
                )
            )

            first_value = (
                parse_date(
                    challenge.get(
                        "first_date"
                    )
                )
                or date.today()
            )

            edit_first_date = (
                st.date_input(
                    "最初の挑戦日",
                    value=first_value,
                    max_value=date.today(),
                    key=(
                        "edit_first_date_"
                        + challenge_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "テーマメモ",
                    value=challenge.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + challenge_id
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
                        "save_challenge_"
                        + challenge_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "挑戦名を入力してね。"
                        )

                    else:
                        update_challenge(
                            data,
                            challenge_id,
                            edit_title.strip(),
                            edit_category,
                            edit_start_state,
                            edit_first_date,
                            edit_memo.strip(),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if challenge.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "manage_fav_"
                        + challenge_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        challenge_id,
                    )

                    st.rerun()

            st.markdown(
                "#### 📖 挑戦履歴"
            )

            history = sorted_attempts(
                data,
                challenge_id,
            )

            for attempt in reversed(
                history
            ):
                attempt_id = (
                    attempt.get(
                        "id",
                        "",
                    )
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
                            + format_date(
                                attempt.get(
                                    "attempt_date"
                                )
                            )
                            + "**"
                        )

                        st.write(
                            f"🔥 "
                            f"{attempt.get('count', 1)}回"
                            f" ｜ "
                            f"{attempt.get('result', '')}"
                        )

                        actions_text = (
                            " / ".join(
                                attempt.get(
                                    "actions",
                                    [],
                                )
                            )
                        )

                        if actions_text:
                            st.caption(
                                actions_text
                            )

                        if attempt.get(
                            "note"
                        ):
                            st.caption(
                                "💭 "
                                + attempt.get(
                                    "note",
                                    "",
                                )
                            )

                    with col2:
                        if st.button(
                            "🗑️",
                            key=(
                                "delete_attempt_"
                                + attempt_id
                            ),
                        ):
                            delete_attempt(
                                data,
                                attempt_id,
                            )

                            st.rerun()

            confirm_delete = (
                st.checkbox(
                    "このテーマと"
                    "すべての挑戦履歴を削除する",
                    key=(
                        "confirm_delete_"
                        + challenge_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_challenge_"
                    + challenge_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_challenge(
                    data,
                    challenge_id,
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
            "never_gave_up_"
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
    "🔥 できなかった日は、"
    "終わった日じゃない。"
    "もう一度戻ってきたなら、"
    "物語は続いている。"
)
