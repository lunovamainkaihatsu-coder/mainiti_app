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
    page_title="これ、誰かに聞く？",
    page_icon="❓",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "questions.json",
)

CATEGORIES = [
    "💼 仕事",
    "💻 開発",
    "📚 勉強",
    "🏠 生活",
    "💰 お金",
    "👥 人",
    "🛒 買い物",
    "✨ その他",
]

STATUSES = [
    "📝 まだ聞いてない",
    "⏳ 回答待ち",
    "💡 回答あり",
    "✅ 解決",
]

ASK_RESULTS = [
    "😊 聞いてよかった",
    "😐 どちらでもない",
    "😣 自分で調べればよかった",
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


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)

    except (ValueError, TypeError):
        return None


def format_datetime(value):
    dt = parse_datetime(value)

    if not dt:
        return "-"

    return dt.strftime(
        "%Y/%m/%d %H:%M"
    )


def days_from(value):
    dt = parse_datetime(value)

    if not dt:
        return 0

    return max(
        (
            datetime.now().date()
            - dt.date()
        ).days,
        0,
    )


def duration_minutes(
    start_value,
    end_value,
):
    start = parse_datetime(
        start_value
    )

    end = parse_datetime(
        end_value
    )

    if not start or not end:
        return None

    return max(
        int(
            (
                end - start
            ).total_seconds()
            // 60
        ),
        0,
    )


def duration_text(minutes):
    if minutes is None:
        return "-"

    minutes = int(minutes)

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    remaining = minutes % 60

    if hours < 24:
        if remaining:
            return (
                f"{hours}時間"
                f"{remaining}分"
            )

        return f"{hours}時間"

    days = hours // 24
    remaining_hours = hours % 24

    if remaining_hours:
        return (
            f"{days}日"
            f"{remaining_hours}時間"
        )

    return f"{days}日"


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


def average(values):
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


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "questions": []
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
            "questions",
            [],
        )

        # 古いデータでも動くように補完
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
                "person",
                "",
            )

            question.setdefault(
                "category",
                "✨ その他",
            )

            question.setdefault(
                "importance",
                3,
            )

            question.setdefault(
                "reason",
                "",
            )

            question.setdefault(
                "status",
                "📝 まだ聞いてない",
            )

            question.setdefault(
                "asked_at",
                None,
            )

            question.setdefault(
                "followup_at",
                None,
            )

            question.setdefault(
                "answer",
                "",
            )

            question.setdefault(
                "answered_by",
                "",
            )

            question.setdefault(
                "answered_at",
                None,
            )

            question.setdefault(
                "understanding",
                3,
            )

            question.setdefault(
                "faq",
                False,
            )

            question.setdefault(
                "favorite",
                False,
            )

            question.setdefault(
                "resolved_at",
                None,
            )

            question.setdefault(
                "ask_result",
                "",
            )

            question.setdefault(
                "parent_id",
                None,
            )

            question.setdefault(
                "memo",
                "",
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
        data = empty_data()
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
            if question.get("id")
            == question_id
        ),
        None,
    )


def add_question(
    data,
    question,
    person,
    category,
    importance,
    reason,
    memo="",
    parent_id=None,
):
    data["questions"].append(
        {
            "id": create_id(),
            "question": question,
            "person": person,
            "category": category,
            "importance": int(
                importance
            ),
            "reason": reason,
            "status": (
                "📝 まだ聞いてない"
            ),
            "asked_at": None,
            "followup_at": None,
            "answer": "",
            "answered_by": "",
            "answered_at": None,
            "understanding": 3,
            "faq": False,
            "favorite": False,
            "resolved_at": None,
            "ask_result": "",
            "parent_id": parent_id,
            "memo": memo,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def mark_asked(
    data,
    question_id,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["status"] = (
        "⏳ 回答待ち"
    )
    question["asked_at"] = (
        now_text()
    )
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def mark_followup(
    data,
    question_id,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["followup_at"] = (
        now_text()
    )
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def save_answer(
    data,
    question_id,
    answer,
    answered_by,
    understanding,
    faq,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["answer"] = answer
    question["answered_by"] = (
        answered_by
    )
    question["understanding"] = int(
        understanding
    )
    question["faq"] = faq
    question["answered_at"] = (
        now_text()
    )
    question["status"] = (
        "💡 回答あり"
    )
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def resolve_question(
    data,
    question_id,
    ask_result,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["status"] = "✅ 解決"
    question["resolved_at"] = (
        now_text()
    )
    question["ask_result"] = (
        ask_result
    )
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def reopen_question(
    data,
    question_id,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    if question.get("answer"):
        question["status"] = (
            "💡 回答あり"
        )
    else:
        question["status"] = (
            "📝 まだ聞いてない"
        )

    question["resolved_at"] = None
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

    question["favorite"] = (
        not question.get(
            "favorite",
            False,
        )
    )

    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_faq(
    data,
    question_id,
):
    question = get_question(
        data,
        question_id,
    )

    if not question:
        return

    question["faq"] = (
        not question.get(
            "faq",
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
    person,
    category,
    importance,
    reason,
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
    question["person"] = person
    question["category"] = category
    question["importance"] = int(
        importance
    )
    question["reason"] = reason
    question["memo"] = memo
    question["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_question(
    data,
    question_id,
):
    # 子質問の親IDは解除して残す
    for question in data[
        "questions"
    ]:
        if question.get(
            "parent_id"
        ) == question_id:
            question["parent_id"] = None

    data["questions"] = [
        question
        for question
        in data["questions"]
        if question.get("id")
        != question_id
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
        background: rgba(80, 150, 230, 0.07);
        border: 1px solid rgba(80, 150, 230, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 150, 240, 0.20),
                rgba(120, 210, 210, 0.08)
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
questions = data["questions"]

unasked = [
    question
    for question in questions
    if question.get("status")
    == "📝 まだ聞いてない"
]

waiting = [
    question
    for question in questions
    if question.get("status")
    == "⏳ 回答待ち"
]

answered = [
    question
    for question in questions
    if question.get("status")
    == "💡 回答あり"
]

resolved = [
    question
    for question in questions
    if question.get("status")
    == "✅ 解決"
]

faq_questions = [
    question
    for question in questions
    if question.get("faq")
    and question.get("answer")
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>💬 これ、誰かに聞く？</h1>
        <p>
            分からないまま止まる前に、
            「誰に・何を聞くか」を外へ出してみよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "❓ 未質問",
    len(unasked),
)

col2.metric(
    "⏳ 回答待ち",
    len(waiting),
)

col3.metric(
    "💡 回答あり",
    len(answered),
)

col4.metric(
    "📚 FAQ",
    len(faq_questions),
)


# =========================================================
# 質問登録
# =========================================================

st.divider()

st.subheader(
    "❓ 聞きたいことを追加"
)

with st.form(
    "new_question_form",
    clear_on_submit=True,
):
    question_text = st.text_area(
        "❓ 何を聞きたい？",
        placeholder=(
            "例：この仕様で提出して大丈夫？"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        person = st.text_input(
            "👤 誰に聞く？",
            placeholder=(
                "例：担当者"
            ),
        )

        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

    with col2:
        importance = st.slider(
            "⭐ 重要度",
            1,
            5,
            3,
        )

        st.caption(
            stars(importance)
        )

    reason = st.text_area(
        "💭 なぜ聞きたい？",
        placeholder=(
            "例：ここが決まらないと"
            "次へ進めない"
        ),
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder="任意",
    )

    submitted = (
        st.form_submit_button(
            "📌 質問リストに入れる",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not question_text.strip():
            st.warning(
                "聞きたいことを入力してね。"
            )

        else:
            add_question(
                data=data,
                question=(
                    question_text.strip()
                ),
                person=person.strip(),
                category=category,
                importance=importance,
                reason=reason.strip(),
                memo=memo.strip(),
            )

            st.session_state[
                "question_added"
            ] = True

            st.rerun()


if st.session_state.pop(
    "question_added",
    False,
):
    st.success(
        "📌 質問リストに追加しました！"
    )


# =========================================================
# まだ聞いていない
# =========================================================

st.divider()

st.subheader(
    "🧠 まだ聞いていない質問"
)

if not unasked:
    st.info(
        "今のところ、聞かずに止まっている質問はありません。"
    )

else:
    unasked_sorted = sorted(
        unasked,
        key=lambda item: (
            days_from(
                item.get("created_at")
            ),
            item.get(
                "importance",
                3,
            ),
        ),
        reverse=True,
    )

    for question in unasked_sorted:
        question_id = question.get(
            "id",
            "",
        )

        age = days_from(
            question.get(
                "created_at"
            )
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [7, 1]
            )

            with col1:
                st.subheader(
                    question.get(
                        "question",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if question.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "unasked_fav_"
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
                + stars(
                    question.get(
                        "importance",
                        3,
                    )
                )
            )

            if question.get("person"):
                st.write(
                    "👤 **聞く相手：** "
                    + question.get(
                        "person",
                        "",
                    )
                )

            if question.get("reason"):
                st.write(
                    "💭 **聞きたい理由：**"
                )
                st.write(
                    question.get(
                        "reason",
                        "",
                    )
                )

            if age >= 14:
                st.error(
                    f"🔴 登録から{age}日。"
                    "かなり長く質問箱に残っています。"
                )

            elif age >= 7:
                st.warning(
                    f"🟠 登録から{age}日。"
                    "聞けば前へ進めるかもしれません。"
                )

            elif age >= 3:
                st.info(
                    f"🟡 登録から{age}日。"
                )

            else:
                st.caption(
                    f"登録から {age}日"
                )

            if st.button(
                "📤 聞いた！",
                key=(
                    "asked_"
                    + question_id
                ),
                type="primary",
                use_container_width=True,
            ):
                mark_asked(
                    data,
                    question_id,
                )

                st.rerun()


# =========================================================
# 回答待ち
# =========================================================

st.divider()

st.subheader(
    "⏳ 回答待ち"
)

if not waiting:
    st.caption(
        "回答待ちの質問はありません。"
    )

else:
    for question in sorted(
        waiting,
        key=lambda item: (
            item.get(
                "asked_at",
                "",
            )
        ),
    ):
        question_id = question.get(
            "id",
            "",
        )

        wait_days = days_from(
            question.get(
                "asked_at"
            )
        )

        with st.container(
            border=True
        ):
            st.subheader(
                question.get(
                    "question",
                    "",
                )
            )

            st.caption(
                "📤 "
                + format_datetime(
                    question.get(
                        "asked_at"
                    )
                )
            )

            if question.get("person"):
                st.write(
                    "👤 **回答待ち：** "
                    + question.get(
                        "person",
                        "",
                    )
                )

            st.write(
                f"⏱️ **待っている期間：{wait_days}日**"
            )

            if wait_days >= 7:
                st.warning(
                    "📩 そろそろ確認してもいいかもしれません。"
                )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "📩 確認した",
                    key=(
                        "followup_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    mark_followup(
                        data,
                        question_id,
                    )
                    st.rerun()

            with col2:
                if question.get(
                    "followup_at"
                ):
                    st.caption(
                        "最終確認："
                        + format_datetime(
                            question.get(
                                "followup_at"
                            )
                        )
                    )

            with st.expander(
                "💡 回答が来た"
            ):
                with st.form(
                    "answer_form_"
                    + question_id
                ):
                    answer_text = (
                        st.text_area(
                            "💡 回答",
                            placeholder=(
                                "もらった回答を残そう"
                            ),
                        )
                    )

                    answered_by = (
                        st.text_input(
                            "👤 誰から？",
                            value=question.get(
                                "person",
                                "",
                            ),
                        )
                    )

                    understanding = (
                        st.slider(
                            "🧠 理解できた？",
                            1,
                            5,
                            4,
                        )
                    )

                    make_faq = (
                        st.checkbox(
                            "📚 次回も使える知識としてFAQに残す"
                        )
                    )

                    answer_submit = (
                        st.form_submit_button(
                            "💡 回答を保存",
                            use_container_width=True,
                        )
                    )

                    if answer_submit:
                        if not (
                            answer_text.strip()
                        ):
                            st.warning(
                                "回答を入力してね。"
                            )
                        else:
                            save_answer(
                                data=data,
                                question_id=(
                                    question_id
                                ),
                                answer=(
                                    answer_text.strip()
                                ),
                                answered_by=(
                                    answered_by.strip()
                                ),
                                understanding=(
                                    understanding
                                ),
                                faq=make_faq,
                            )

                            st.rerun()


# =========================================================
# 回答あり
# =========================================================

st.divider()

st.subheader(
    "💡 回答が来た質問"
)

if not answered:
    st.caption(
        "解決確認待ちの質問はありません。"
    )

else:
    for question in answered:
        question_id = question.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.subheader(
                question.get(
                    "question",
                    "",
                )
            )

            st.write(
                "💡 **回答**"
            )

            st.write(
                question.get(
                    "answer",
                    "",
                )
            )

            if question.get(
                "answered_by"
            ):
                st.caption(
                    "回答："
                    + question.get(
                        "answered_by",
                        "",
                    )
                    + " ｜ "
                    + format_datetime(
                        question.get(
                            "answered_at"
                        )
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

            with st.form(
                "resolve_form_"
                + question_id
            ):
                ask_result = (
                    st.selectbox(
                        "この質問、聞いてどうだった？",
                        ASK_RESULTS,
                    )
                )

                resolve_submit = (
                    st.form_submit_button(
                        "✅ 解決した",
                        type="primary",
                        use_container_width=True,
                    )
                )

                if resolve_submit:
                    resolve_question(
                        data,
                        question_id,
                        ask_result,
                    )

                    st.rerun()

            with st.expander(
                "❓ まだ分からない・追加で聞く"
            ):
                with st.form(
                    "child_question_"
                    + question_id
                ):
                    child_text = (
                        st.text_area(
                            "追加で聞きたいこと",
                            placeholder=(
                                "例：エラー時の処理も"
                                "この仕様でいい？"
                            ),
                        )
                    )

                    child_person = (
                        st.text_input(
                            "誰に聞く？",
                            value=question.get(
                                "person",
                                "",
                            ),
                        )
                    )

                    child_submit = (
                        st.form_submit_button(
                            "🔁 追加質問を作る",
                            use_container_width=True,
                        )
                    )

                    if child_submit:
                        if not (
                            child_text.strip()
                        ):
                            st.warning(
                                "追加質問を入力してね。"
                            )
                        else:
                            add_question(
                                data=data,
                                question=(
                                    child_text.strip()
                                ),
                                person=(
                                    child_person.strip()
                                ),
                                category=(
                                    question.get(
                                        "category",
                                        "✨ その他",
                                    )
                                ),
                                importance=(
                                    question.get(
                                        "importance",
                                        3,
                                    )
                                ),
                                reason=(
                                    "追加質問"
                                ),
                                parent_id=(
                                    question_id
                                ),
                            )

                            st.rerun()


# =========================================================
# 自分専用FAQ
# =========================================================

st.divider()

st.subheader(
    "📚 自分専用FAQ"
)

faq_search = st.text_input(
    "🔎 FAQ検索",
    placeholder=(
        "API、提出、勉強……"
    ),
    key="faq_search",
)

faq_category = st.selectbox(
    "FAQカテゴリー",
    ["すべて"] + CATEGORIES,
    key="faq_category",
)

filtered_faq = []

for question in faq_questions:
    if (
        faq_category != "すべて"
        and question.get(
            "category"
        )
        != faq_category
    ):
        continue

    searchable = " ".join(
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
                "answered_by",
                "",
            ),
            question.get(
                "category",
                "",
            ),
        ]
    ).lower()

    if (
        faq_search.strip()
        and faq_search.strip().lower()
        not in searchable
    ):
        continue

    filtered_faq.append(
        question
    )


if not filtered_faq:
    st.info(
        "条件に合うFAQはありません。"
    )

else:
    for question in sorted(
        filtered_faq,
        key=lambda item: (
            item.get(
                "answered_at",
                "",
            )
        ),
        reverse=True,
    ):
        with st.container(
            border=True
        ):
            st.caption(
                question.get(
                    "category",
                    "",
                )
            )

            st.write(
                "**Q. "
                + question.get(
                    "question",
                    "",
                )
                + "**"
            )

            st.write(
                "A. "
                + question.get(
                    "answer",
                    "",
                )
            )

            if question.get(
                "answered_by"
            ):
                st.caption(
                    "回答："
                    + question.get(
                        "answered_by",
                        "",
                    )
                )


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月の質問"
)

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_questions = [
    question
    for question in questions
    if (
        question.get(
            "created_at",
            "",
        )
        or ""
    ).startswith(
        current_month
    )
]

month_asked = [
    question
    for question in questions
    if (
        question.get(
            "asked_at",
            "",
        )
        or ""
    ).startswith(
        current_month
    )
]

month_answered = [
    question
    for question in questions
    if (
        question.get(
            "answered_at",
            "",
        )
        or ""
    ).startswith(
        current_month
    )
]

month_resolved = [
    question
    for question in questions
    if (
        question.get(
            "resolved_at",
            "",
        )
        or ""
    ).startswith(
        current_month
    )
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "❓ 登録",
    f"{len(month_questions)}件",
)

col2.metric(
    "📤 質問した",
    f"{len(month_asked)}件",
)

col3.metric(
    "💡 回答あり",
    f"{len(month_answered)}件",
)

col4.metric(
    "✅ 解決",
    f"{len(month_resolved)}件",
)


# =========================================================
# 所要時間分析
# =========================================================

register_to_ask = []

ask_to_answer = []

register_to_resolve = []

for question in questions:
    if question.get(
        "asked_at"
    ):
        value = duration_minutes(
            question.get(
                "created_at"
            ),
            question.get(
                "asked_at"
            ),
        )

        if value is not None:
            register_to_ask.append(
                value
            )

    if (
        question.get("asked_at")
        and question.get(
            "answered_at"
        )
    ):
        value = duration_minutes(
            question.get(
                "asked_at"
            ),
            question.get(
                "answered_at"
            ),
        )

        if value is not None:
            ask_to_answer.append(
                value
            )

    if question.get(
        "resolved_at"
    ):
        value = duration_minutes(
            question.get(
                "created_at"
            ),
            question.get(
                "resolved_at"
            ),
        )

        if value is not None:
            register_to_resolve.append(
                value
            )


if (
    register_to_ask
    or ask_to_answer
    or register_to_resolve
):
    st.markdown(
        "### ⏱️ 平均時間"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    col1.metric(
        "登録 → 質問",
        duration_text(
            average(
                register_to_ask
            )
        )
        if register_to_ask
        else "-",
    )

    col2.metric(
        "質問 → 回答",
        duration_text(
            average(
                ask_to_answer
            )
        )
        if ask_to_answer
        else "-",
    )

    col3.metric(
        "登録 → 解決",
        duration_text(
            average(
                register_to_resolve
            )
        )
        if register_to_resolve
        else "-",
    )


# =========================================================
# カテゴリー分析
# =========================================================

if month_questions:
    category_rows = []

    for category in CATEGORIES:
        count = len(
            [
                question
                for question
                in month_questions
                if question.get(
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
        st.markdown(
            "### 🏷️ 何について聞いた？"
        )

        category_df = (
            pd.DataFrame(
                category_rows
            )
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 誰に聞いている？
# =========================================================

person_counts = {}

for question in questions:
    person = question.get(
        "answered_by"
    ) or question.get(
        "person"
    )

    if not person:
        continue

    person_counts[person] = (
        person_counts.get(
            person,
            0,
        )
        + 1
    )


if person_counts:
    st.markdown(
        "### 👥 誰によく聞いている？"
    )

    person_df = pd.DataFrame(
        [
            {
                "相手": person,
                "質問数": count,
            }
            for person, count
            in person_counts.items()
        ]
    )

    person_df = person_df.sort_values(
        "質問数",
        ascending=False,
    )

    st.bar_chart(
        person_df.set_index(
            "相手"
        )
    )


# =========================================================
# 聞いてよかった分析
# =========================================================

result_questions = [
    question
    for question in resolved
    if question.get(
        "ask_result"
    )
]

if result_questions:
    st.markdown(
        "### 😊 聞いてよかった？"
    )

    good_count = len(
        [
            question
            for question
            in result_questions
            if question.get(
                "ask_result"
            )
            == "😊 聞いてよかった"
        ]
    )

    good_rate = round(
        good_count
        / len(result_questions)
        * 100
    )

    st.metric(
        "「聞いてよかった」の割合",
        f"{good_rate}%",
    )

    result_rows = []

    for result in ASK_RESULTS:
        result_rows.append(
            {
                "結果": result,
                "件数": len(
                    [
                        question
                        for question
                        in result_questions
                        if question.get(
                            "ask_result"
                        )
                        == result
                    ]
                ),
            }
        )

    result_df = pd.DataFrame(
        result_rows
    )

    st.bar_chart(
        result_df.set_index(
            "結果"
        )
    )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    question
    for question in questions
    if question.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 大事な質問"
    )

    for question in sorted(
        favorites,
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

        with st.container(
            border=True
        ):
            st.write(
                "⭐ **"
                + question.get(
                    "question",
                    "",
                )
                + "**"
            )

            st.caption(
                question.get(
                    "category",
                    "",
                )
                + " ｜ "
                + question.get(
                    "status",
                    "",
                )
            )

            if question.get(
                "answer"
            ):
                st.write(
                    "💡 "
                    + question.get(
                        "answer",
                        "",
                    )
                )

            if st.button(
                "⭐ お気に入り解除",
                key=(
                    "fav_remove_"
                    + question_id
                ),
            ):
                toggle_favorite(
                    data,
                    question_id,
                )

                st.rerun()


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📜 質問履歴"
)

history_search = st.text_input(
    "🔎 履歴検索",
    placeholder=(
        "質問、回答、相手……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    history_category = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key=(
                "history_category"
            ),
        )
    )

with col2:
    history_status = (
        st.selectbox(
            "状態",
            ["すべて"]
            + STATUSES,
            key="history_status",
        )
    )


history_rows = []

for question in questions:
    if (
        history_category
        != "すべて"
        and question.get(
            "category"
        )
        != history_category
    ):
        continue

    if (
        history_status
        != "すべて"
        and question.get(
            "status"
        )
        != history_status
    ):
        continue

    searchable = " ".join(
        [
            question.get(
                "question",
                "",
            ),
            question.get(
                "person",
                "",
            ),
            question.get(
                "answer",
                "",
            ),
            question.get(
                "answered_by",
                "",
            ),
            question.get(
                "reason",
                "",
            ),
        ]
    ).lower()

    if (
        history_search.strip()
        and history_search
        .strip()
        .lower()
        not in searchable
    ):
        continue

    history_rows.append(
        {
            "登録日": (
                format_datetime(
                    question.get(
                        "created_at"
                    )
                )
            ),
            "質問": question.get(
                "question",
                "",
            ),
            "相手": question.get(
                "person",
                "",
            ),
            "カテゴリー": (
                question.get(
                    "category",
                    "",
                )
            ),
            "重要度": stars(
                question.get(
                    "importance",
                    3,
                )
            ),
            "状態": question.get(
                "status",
                "",
            ),
            "FAQ": (
                "📚"
                if question.get(
                    "faq"
                )
                else ""
            ),
            "⭐": (
                "⭐"
                if question.get(
                    "favorite"
                )
                else ""
            ),
        }
    )


if history_rows:
    st.dataframe(
        pd.DataFrame(
            history_rows
        ),
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info(
        "条件に合う質問はありません。"
    )


# =========================================================
# 編集・管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・管理"
):
    if not questions:
        st.caption(
            "まだ質問がありません。"
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

        with st.expander(
            question.get(
                "status",
                "",
            )
            + " ｜ "
            + question.get(
                "question",
                "",
            )
        ):
            edit_question = (
                st.text_area(
                    "質問",
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

            edit_person = (
                st.text_input(
                    "聞く相手",
                    value=question.get(
                        "person",
                        "",
                    ),
                    key=(
                        "edit_person_"
                        + question_id
                    ),
                )
            )

            old_category = (
                question.get(
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
                    index=(
                        category_index
                    ),
                    key=(
                        "edit_category_"
                        + question_id
                    ),
                )
            )

            edit_importance = (
                st.slider(
                    "重要度",
                    1,
                    5,
                    int(
                        question.get(
                            "importance",
                            3,
                        )
                    ),
                    key=(
                        "edit_importance_"
                        + question_id
                    ),
                )
            )

            edit_reason = (
                st.text_area(
                    "聞きたい理由",
                    value=question.get(
                        "reason",
                        "",
                    ),
                    key=(
                        "edit_reason_"
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

            if question.get(
                "answer"
            ):
                st.write(
                    "💡 **現在の回答**"
                )
                st.write(
                    question.get(
                        "answer",
                        "",
                    )
                )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_edit_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_question
                        .strip()
                    ):
                        st.warning(
                            "質問を入力してね。"
                        )

                    else:
                        update_question(
                            data=data,
                            question_id=(
                                question_id
                            ),
                            question_text=(
                                edit_question
                                .strip()
                            ),
                            person=(
                                edit_person
                                .strip()
                            ),
                            category=(
                                edit_category
                            ),
                            importance=(
                                edit_importance
                            ),
                            reason=(
                                edit_reason
                                .strip()
                            ),
                            memo=(
                                edit_memo
                                .strip()
                            ),
                        )

                        st.rerun()

            with col2:
                favorite_label = (
                    "⭐ お気に入り解除"
                    if question.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "manage_favorite_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        question_id,
                    )

                    st.rerun()

            if question.get(
                "answer"
            ):
                faq_label = (
                    "📚 FAQから外す"
                    if question.get(
                        "faq",
                        False,
                    )
                    else "📚 FAQに追加"
                )

                if st.button(
                    faq_label,
                    key=(
                        "faq_toggle_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    toggle_faq(
                        data,
                        question_id,
                    )

                    st.rerun()

            if (
                question.get(
                    "status"
                )
                == "✅ 解決"
            ):
                if st.button(
                    "↩️ 再び開く",
                    key=(
                        "reopen_"
                        + question_id
                    ),
                    use_container_width=True,
                ):
                    reopen_question(
                        data,
                        question_id,
                    )

                    st.rerun()

            confirm_delete = (
                st.checkbox(
                    "削除を確認",
                    key=(
                        "confirm_delete_"
                        + question_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + question_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_question(
                    data,
                    question_id,
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
            "ask_someone_"
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
    "💬 「分からない」は、"
    "まだ誰かに聞いていないだけかもしれない。"
)
