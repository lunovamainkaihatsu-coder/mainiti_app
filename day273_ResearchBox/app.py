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
    page_title="あとで調べる箱",
    page_icon="🔍",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "research_box.json",
)

CATEGORIES = [
    "🤖 AI・技術",
    "📚 勉強",
    "💼 仕事",
    "💰 お金",
    "🏠 生活",
    "🍳 食べ物",
    "🌍 世界・社会",
    "🎮 趣味",
    "💡 アイデア",
    "❓ その他",
]

STATUS_LABELS = {
    "waiting": "📦 未調査",
    "done": "🧠 調査済み",
    "dropped": "🗑️ 興味終了",
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


def days_since(value):
    target = parse_date(value)

    return max(
        (
            date.today()
            - target
        ).days,
        0,
    )


def stars(level):
    level = max(
        1,
        min(
            int(level),
            5,
        ),
    )

    return (
        "★" * level
        + "☆" * (5 - level)
    )


def create_empty_data():
    return {
        "questions": [],
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
            "questions",
            [],
        )

        for question in data[
            "questions"
        ]:
            question.setdefault(
                "id",
                create_id(),
            )

            question.setdefault(
                "question",
                "",
            )

            question.setdefault(
                "category",
                "❓ その他",
            )

            question.setdefault(
                "memo",
                "",
            )

            question.setdefault(
                "status",
                "waiting",
            )

            question.setdefault(
                "answer",
                "",
            )

            question.setdefault(
                "understanding",
                3,
            )

            question.setdefault(
                "favorite",
                False,
            )

            question.setdefault(
                "parent_id",
                None,
            )

            question.setdefault(
                "created_date",
                today_text(),
            )

            question.setdefault(
                "researched_date",
                None,
            )

            question.setdefault(
                "created_at",
                now_text(),
            )

            question.setdefault(
                "updated_at",
                question.get(
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

def get_question(
    data,
    question_id,
):
    return next(
        (
            question
            for question
            in data["questions"]
            if question.get(
                "id"
            ) == question_id
        ),
        None,
    )


def add_question(
    data,
    question_text,
    category,
    memo="",
    parent_id=None,
):
    data["questions"].append(
        {
            "id": create_id(),
            "question": question_text,
            "category": category,
            "memo": memo,
            "status": "waiting",
            "answer": "",
            "understanding": 3,
            "favorite": False,
            "parent_id": parent_id,
            "created_date": today_text(),
            "researched_date": None,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def complete_question(
    data,
    question_id,
    answer,
    understanding,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["status"] = "done"
    question["answer"] = answer
    question["understanding"] = int(
        understanding
    )

    question[
        "researched_date"
    ] = today_text()

    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def drop_question(
    data,
    question_id,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["status"] = "dropped"
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def restore_question(
    data,
    question_id,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["status"] = "waiting"
    question["answer"] = ""
    question["researched_date"] = None
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_favorite(
    data,
    question_id,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["favorite"] = not (
        question.get(
            "favorite",
            False,
        )
    )

    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def update_question(
    data,
    question_id,
    question_text,
    category,
    memo,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["question"] = (
        question_text
    )

    question["category"] = (
        category
    )

    question["memo"] = memo
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_question(
    data,
    question_id,
):
    data["questions"] = [
        question
        for question
        in data["questions"]
        if question.get(
            "id"
        ) != question_id
    ]

    # 子質問の親リンクだけ解除
    for question in data[
        "questions"
    ]:
        if question.get(
            "parent_id"
        ) == question_id:
            question[
                "parent_id"
            ] = None

    save_data(data)


# =========================================================
# ストリーク
# =========================================================

def research_streak(
    questions,
):
    dates = {
        parse_date(
            question.get(
                "researched_date"
            )
        )
        for question in questions
        if (
            question.get(
                "status"
            ) == "done"
            and question.get(
                "researched_date"
            )
        )
    }

    if not dates:
        return 0

    today = date.today()

    if (
        today not in dates
        and (
            today
            - timedelta(days=1)
        ) not in dates
    ):
        return 0

    current = (
        today
        if today in dates
        else today
        - timedelta(days=1)
    )

    streak = 0

    while current in dates:
        streak += 1

        current -= timedelta(
            days=1
        )

    return streak


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
            rgba(80, 130, 220, 0.07);

        border:
            1px solid
            rgba(80, 130, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(70, 130, 230, 0.18),
                rgba(130, 100, 220, 0.08)
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

    .question-card {
        padding: 28px;
        border-radius: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(70, 140, 230, 0.11),
                rgba(140, 100, 220, 0.06)
            );
    }

    .question-title {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    .knowledge-card {
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 15px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 180, 140, 0.10),
                rgba(70, 130, 230, 0.05)
            );
    }

    .old-card {
        padding: 22px;
        border-radius: 20px;

        background:
            rgba(240, 170, 60, 0.08);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

questions = data[
    "questions"
]

waiting_questions = [
    question
    for question in questions
    if question.get(
        "status"
    ) == "waiting"
]

done_questions = [
    question
    for question in questions
    if question.get(
        "status"
    ) == "done"
]

dropped_questions = [
    question
    for question in questions
    if question.get(
        "status"
    ) == "dropped"
]

today = date.today()

month_prefix = today.strftime(
    "%Y-%m"
)

month_done = [
    question
    for question in done_questions
    if (
        question.get(
            "researched_date",
            ""
        )
        or ""
    ).startswith(
        month_prefix
    )
]

old_questions = [
    question
    for question in waiting_questions
    if days_since(
        question.get(
            "created_date"
        )
    ) >= 30
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            🔍 あとで調べる箱
        </h1>

        <p>
            疑問を、忘れる前に入れておく。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

streak = research_streak(
    questions
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "📦 未調査",
    f"{len(waiting_questions)}個",
)

col2.metric(
    "🔍 今月調べた",
    f"{len(month_done)}個",
)

col3.metric(
    "🧠 学んだこと",
    f"{len(done_questions)}個",
)

col4.metric(
    "🔥 調査ストリーク",
    f"{streak}日",
)


# =========================================================
# 疑問追加
# =========================================================

st.divider()

st.subheader(
    "📦 気になったことを入れる"
)

st.caption(
    "答えはまだ分からなくてOK。"
    "疑問だけ残しておこう。"
)

with st.form(
    "new_question_form",
    clear_on_submit=True,
):
    question_text = st.text_input(
        "❓ 何が気になった？",
        placeholder=(
            "例：RAGって"
            "具体的にどう動く？"
        ),
    )

    category = st.selectbox(
        "🏷️ カテゴリー",
        CATEGORIES,
    )

    memo = st.text_area(
        "📝 メモ（任意）",
        placeholder=(
            "どこで気になったか、"
            "なぜ調べたいかなど"
        ),
    )

    submitted = (
        st.form_submit_button(
            "📦 あとで調べる箱に入れる",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not (
            question_text.strip()
        ):
            st.warning(
                "疑問を入力してね。"
            )

        else:
            add_question(
                data,
                question_text.strip(),
                category,
                memo.strip(),
            )

            st.rerun()


# =========================================================
# 今ひとつ調べる
# =========================================================

st.divider()

st.subheader(
    "🎲 今ひとつ調べる"
)

if not waiting_questions:
    st.success(
        "🎉 未調査の疑問はありません！"
    )

else:
    if st.button(
        "🎲 疑問をひとつ選ぶ",
        type="primary",
        use_container_width=True,
    ):
        st.session_state[
            "research_question_id"
        ] = random.choice(
            waiting_questions
        ).get(
            "id"
        )

    selected_id = (
        st.session_state.get(
            "research_question_id"
        )
    )

    selected_question = (
        get_question(
            data,
            selected_id,
        )
        if selected_id
        else None
    )

    if (
        selected_question
        and selected_question.get(
            "status"
        ) == "waiting"
    ):
        elapsed = days_since(
            selected_question.get(
                "created_date"
            )
        )

        st.markdown(
            f"""
            <div class="question-card">

                <div>
                    {
                        selected_question.get(
                            "category",
                            ""
                        )
                    }
                </div>

                <div class="question-title">
                    {
                        selected_question.get(
                            "question",
                            ""
                        )
                    }
                </div>

                <div>
                    📅 登録：
                    {elapsed}日前
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if selected_question.get(
            "memo"
        ):
            st.caption(
                "📝 "
                + selected_question.get(
                    "memo",
                    "",
                )
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🎲 別の疑問",
                key="another_question",
                use_container_width=True,
            ):
                alternatives = [
                    question
                    for question
                    in waiting_questions
                    if question.get(
                        "id"
                    ) != selected_id
                ]

                if alternatives:
                    st.session_state[
                        "research_question_id"
                    ] = random.choice(
                        alternatives
                    ).get(
                        "id"
                    )

                st.rerun()

        with col2:
            if st.button(
                "🗑️ もう気にならない",
                key="drop_selected",
                use_container_width=True,
            ):
                drop_question(
                    data,
                    selected_id,
                )

                st.session_state.pop(
                    "research_question_id",
                    None,
                )

                st.rerun()

        st.markdown(
            "#### 🔍 調べて分かったこと"
        )

        with st.form(
            "research_result_form"
        ):
            answer = st.text_area(
                "💡 分かったこと",
                height=180,
                placeholder=(
                    "調べて理解した内容を"
                    "自分の言葉で残そう。"
                ),
            )

            understanding = st.slider(
                "🧠 理解度",
                1,
                5,
                4,
            )

            st.caption(
                stars(
                    understanding
                )
            )

            next_question = (
                st.text_input(
                    "🌱 次に気になったこと（任意）",
                    placeholder=(
                        "例：ジェネレーターと"
                        "普通の関数は何が違う？"
                    ),
                )
            )

            add_next = st.checkbox(
                "次の疑問を"
                "「あとで調べる箱」に入れる",
                value=bool(
                    next_question.strip()
                ),
            )

            result_submit = (
                st.form_submit_button(
                    "✅ 分かった！",
                    type="primary",
                    use_container_width=True,
                )
            )

            if result_submit:
                if not answer.strip():
                    st.warning(
                        "分かったことを"
                        "少しだけ書いてみよう。"
                    )

                else:
                    complete_question(
                        data,
                        selected_id,
                        answer.strip(),
                        understanding,
                    )

                    if (
                        add_next
                        and next_question.strip()
                    ):
                        add_question(
                            data,
                            next_question.strip(),
                            selected_question.get(
                                "category",
                                "❓ その他",
                            ),
                            parent_id=(
                                selected_id
                            ),
                        )

                    st.session_state.pop(
                        "research_question_id",
                        None,
                    )

                    st.rerun()


# =========================================================
# 長期未調査
# =========================================================

if old_questions:
    st.divider()

    st.subheader(
        "👀 まだ気になってる？"
    )

    st.caption(
        "30日以上、箱に入ったままの"
        "疑問があります。"
    )

    for question in sorted(
        old_questions,
        key=lambda item: (
            item.get(
                "created_date",
                ""
            )
        ),
    )[:5]:
        question_id = (
            question.get(
                "id",
                "",
            )
        )

        elapsed = days_since(
            question.get(
                "created_date"
            )
        )

        st.markdown(
            f"""
            <div class="old-card">

                <strong>
                    {
                        question.get(
                            "category",
                            ""
                        )
                    }
                    {
                        question.get(
                            "question",
                            ""
                        )
                    }
                </strong>

                <br><br>

                📅 登録から
                <strong>{elapsed}日</strong>

            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🔍 今調べる",
                key=(
                    "old_research_"
                    + question_id
                ),
                use_container_width=True,
            ):
                st.session_state[
                    "research_question_id"
                ] = question_id

                st.rerun()

        with col2:
            if st.button(
                "🗑️ もう気にならない",
                key=(
                    "old_drop_"
                    + question_id
                ),
                use_container_width=True,
            ):
                drop_question(
                    data,
                    question_id,
                )

                st.rerun()


# =========================================================
# 今月の分析
# =========================================================

st.divider()

st.subheader(
    "📊 今月の調査"
)

if not month_done:
    st.info(
        "今月調べた疑問は"
        "まだありません。"
    )

else:
    average_understanding = round(
        sum(
            int(
                question.get(
                    "understanding",
                    0,
                )
            )
            for question in month_done
        )
        / len(month_done),
        1,
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "🔍 調べた疑問",
        f"{len(month_done)}個",
    )

    col2.metric(
        "🧠 平均理解度",
        f"{average_understanding} / 5",
    )

    category_rows = []

    for category in CATEGORIES:
        category_questions = [
            question
            for question in month_done
            if question.get(
                "category"
            ) == category
        ]

        if not category_questions:
            continue

        category_rows.append(
            {
                "カテゴリー": category,
                "調査数": len(
                    category_questions
                ),
                "平均理解度": round(
                    sum(
                        int(
                            question.get(
                                "understanding",
                                0,
                            )
                        )
                        for question
                        in category_questions
                    )
                    / len(
                        category_questions
                    ),
                    1,
                ),
            }
        )

    category_df = pd.DataFrame(
        category_rows
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "#### 🔍 調査数"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )[
                ["調査数"]
            ]
        )

    with col2:
        st.markdown(
            "#### 🧠 理解度"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )[
                ["平均理解度"]
            ]
        )


# =========================================================
# 知識箱
# =========================================================

st.divider()

st.subheader(
    "🧠 調べて分かったこと"
)

knowledge_search = st.text_input(
    "🔎 知識を検索",
    placeholder=(
        "Python、AI、料理……"
    ),
)

knowledge_category = st.selectbox(
    "カテゴリー",
    ["すべて"] + CATEGORIES,
    key="knowledge_category",
)

filtered_knowledge = []

for question in done_questions:
    if (
        knowledge_category
        != "すべて"
        and question.get(
            "category"
        )
        != knowledge_category
    ):
        continue

    if knowledge_search.strip():
        target = " ".join(
            [
                question.get(
                    "question",
                    "",
                ),
                question.get(
                    "answer",
                    "",
                ),
                question.get(
                    "memo",
                    "",
                ),
            ]
        ).lower()

        if (
            knowledge_search
            .strip()
            .lower()
            not in target
        ):
            continue

    filtered_knowledge.append(
        question
    )


if not filtered_knowledge:
    st.info(
        "条件に合う知識はありません。"
    )

else:
    for question in sorted(
        filtered_knowledge,
        key=lambda item: (
            item.get(
                "researched_date",
                "",
            )
        ),
        reverse=True,
    ):
        question_id = question.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [6, 1]
            )

            with col1:
                st.markdown(
                    "### 🔍 "
                    + question.get(
                        "question",
                        "",
                    )
                )

            with col2:
                icon = (
                    "⭐"
                    if question.get(
                        "favorite",
                        False,
                    )
                    else "☆"
                )

                if st.button(
                    icon,
                    key=(
                        "knowledge_fav_"
                        + question_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        question_id,
                    )

                    st.rerun()

            st.caption(
                question.get(
                    "category",
                    "",
                )
                + " ｜ "
                + str(
                    question.get(
                        "researched_date",
                        "",
                    )
                )
            )

            st.success(
                "💡 "
                + question.get(
                    "answer",
                    "",
                )
            )

            st.write(
                "🧠 理解度："
                + stars(
                    question.get(
                        "understanding",
                        3,
                    )
                )
            )

            # この疑問から生まれた子質問
            child_questions = [
                child
                for child in questions
                if child.get(
                    "parent_id"
                ) == question_id
            ]

            if child_questions:
                with st.expander(
                    "🌱 この疑問から"
                    "生まれた次の疑問"
                ):
                    for child in (
                        child_questions
                    ):
                        st.write(
                            "→ "
                            + child.get(
                                "question",
                                "",
                            )
                        )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    question
    for question in done_questions
    if question.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 残しておきたい知識"
    )

    for question in sorted(
        favorites,
        key=lambda item: (
            item.get(
                "researched_date",
                "",
            )
        ),
        reverse=True,
    )[:10]:
        st.markdown(
            "**🔍 "
            + question.get(
                "question",
                "",
            )
            + "**"
        )

        st.caption(
            "💡 "
            + question.get(
                "answer",
                "",
            )
        )


# =========================================================
# 未調査一覧
# =========================================================

st.divider()

st.subheader(
    "📦 あとで調べる箱"
)

waiting_search = st.text_input(
    "🔎 未調査を検索",
    placeholder=(
        "気になっていた疑問を検索"
    ),
)

waiting_category = st.selectbox(
    "未調査カテゴリー",
    ["すべて"] + CATEGORIES,
)

filtered_waiting = []

for question in waiting_questions:
    if (
        waiting_category
        != "すべて"
        and question.get(
            "category"
        )
        != waiting_category
    ):
        continue

    if waiting_search.strip():
        target = " ".join(
            [
                question.get(
                    "question",
                    "",
                ),
                question.get(
                    "memo",
                    "",
                ),
            ]
        ).lower()

        if (
            waiting_search
            .strip()
            .lower()
            not in target
        ):
            continue

    filtered_waiting.append(
        question
    )


if not filtered_waiting:
    st.info(
        "条件に合う疑問はありません。"
    )

else:
    rows = []

    for question in sorted(
        filtered_waiting,
        key=lambda item: (
            item.get(
                "created_date",
                "",
            )
        ),
        reverse=True,
    ):
        rows.append(
            {
                "登録日": question.get(
                    "created_date",
                    "",
                ),
                "疑問": question.get(
                    "question",
                    "",
                ),
                "カテゴリー": question.get(
                    "category",
                    "",
                ),
                "経過日数": (
                    str(
                        days_since(
                            question.get(
                                "created_date"
                            )
                        )
                    )
                    + "日"
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            rows
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 疑問を編集・削除"
):
    if not questions:
        st.caption(
            "まだ疑問がありません。"
        )

    for question in sorted(
        questions,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        question_id = question.get(
            "id",
            "",
        )

        label = (
            STATUS_LABELS.get(
                question.get(
                    "status",
                    "waiting",
                ),
                "",
            )
            + " ｜ "
            + question.get(
                "question",
                "",
            )
        )

        with st.expander(
            label
        ):
            edit_question = (
                st.text_input(
                    "疑問",
                    value=question.get(
                        "question",
                        "",
                    ),
                    key=(
                        "edit_question_"
                        + question_id
                    ),
                )
            )

            current_category = (
                question.get(
                    "category",
                    "❓ その他",
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
                        + question_id
                    ),
                )
            )

            edit_memo = st.text_area(
                "メモ",
                value=question.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + question_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_question.strip()
                    ):
                        st.warning(
                            "疑問を入力してね。"
                        )

                    else:
                        update_question(
                            data,
                            question_id,
                            edit_question.strip(),
                            edit_category,
                            edit_memo.strip(),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    "🗑️ 完全削除",
                    key=(
                        "delete_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    delete_question(
                        data,
                        question_id,
                    )

                    if (
                        st.session_state.get(
                            "research_question_id"
                        )
                        == question_id
                    ):
                        st.session_state.pop(
                            "research_question_id",
                            None,
                        )

                    st.rerun()

            if (
                question.get(
                    "status"
                ) == "dropped"
            ):
                if st.button(
                    "♻️ 未調査に戻す",
                    key=(
                        "restore_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    restore_question(
                        data,
                        question_id,
                    )

                    st.rerun()


# =========================================================
# 興味終了
# =========================================================

if dropped_questions:
    st.divider()

    with st.expander(
        f"🗑️ もう気にならなくなった疑問 "
        f"({len(dropped_questions)})"
    ):
        for question in (
            dropped_questions
        ):
            st.write(
                "・"
                + question.get(
                    "question",
                    "",
                )
            )


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
            "research_box_"
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
    "「分からない」は、"
    "新しい知識の入口。🔍📦"
)
