import json
import os
import random
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="これ、誰に教えてもらった？",
    page_icon="👤",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "lessons.json")

CATEGORIES = [
    "💻 プログラミング",
    "💼 仕事",
    "💰 お金",
    "🧠 考え方",
    "🌱 人生",
    "🤝 人間関係",
    "🏠 生活",
    "💪 健康・運動",
    "🎨 趣味",
    "📦 その他",
]

SOURCE_TYPES = [
    "👤 人",
    "📚 本",
    "🤖 AI",
    "🎥 YouTube・動画",
    "🌐 Web・SNS",
    "🎓 学校・講座",
    "💼 仕事",
    "🎮 作品",
    "💭 自分で気づいた",
    "📦 その他",
]


# =========================================================
# HELPERS
# =========================================================

def new_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d",
        ).date()
    except (ValueError, TypeError):
        return None


def stars(value):
    if value is None:
        return "-"

    value = int(value)
    value = max(0, min(5, value))

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def lesson_label(lesson):
    return (
        f"{lesson.get('title', '')} "
        f"｜{lesson.get('source_name', '')} "
        f"[{lesson.get('id', '')[:6]}]"
    )


def days_since(value):
    learned = parse_date(value)

    if not learned:
        return None

    return max(
        0,
        (date.today() - learned).days,
    )


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "lessons": [],
        "reviews": [],
    }


def save_data(data):
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    temp_path = DATA_FILE + ".tmp"

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    os.replace(
        temp_path,
        DATA_FILE,
    )


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            data = default_data()

        data.setdefault(
            "lessons",
            [],
        )

        data.setdefault(
            "reviews",
            [],
        )

        # 古いデータにも対応
        for lesson in data["lessons"]:
            lesson.setdefault(
                "id",
                new_id(),
            )
            lesson.setdefault(
                "title",
                "",
            )
            lesson.setdefault(
                "category",
                "📦 その他",
            )
            lesson.setdefault(
                "source_type",
                "📦 その他",
            )
            lesson.setdefault(
                "source_name",
                "",
            )
            lesson.setdefault(
                "useful_expectation",
                3,
            )
            lesson.setdefault(
                "emotional_impact",
                3,
            )
            lesson.setdefault(
                "note",
                "",
            )
            lesson.setdefault(
                "learned_date",
                str(date.today()),
            )
            lesson.setdefault(
                "favorite",
                False,
            )
            lesson.setdefault(
                "created_at",
                now_text(),
            )
            lesson.setdefault(
                "updated_at",
                lesson["created_at"],
            )

        for review in data["reviews"]:
            review.setdefault(
                "id",
                new_id(),
            )
            review.setdefault(
                "lesson_id",
                "",
            )
            review.setdefault(
                "review_date",
                str(date.today()),
            )
            review.setdefault(
                "usefulness",
                3,
            )
            review.setdefault(
                "still_using",
                3,
            )
            review.setdefault(
                "note",
                "",
            )
            review.setdefault(
                "created_at",
                now_text(),
            )

        return data

    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        data = default_data()
        save_data(data)
        return data


# =========================================================
# GETTERS
# =========================================================

def get_lesson(data, lesson_id):
    return next(
        (
            lesson
            for lesson in data["lessons"]
            if lesson.get("id")
            == lesson_id
        ),
        None,
    )


def get_review(data, review_id):
    return next(
        (
            review
            for review in data["reviews"]
            if review.get("id")
            == review_id
        ),
        None,
    )


def reviews_for_lesson(
    data,
    lesson_id,
):
    reviews = [
        review
        for review in data["reviews"]
        if review.get("lesson_id")
        == lesson_id
    ]

    return sorted(
        reviews,
        key=lambda r: (
            r.get("review_date", ""),
            r.get("created_at", ""),
        ),
    )


def latest_review(
    data,
    lesson_id,
):
    reviews = reviews_for_lesson(
        data,
        lesson_id,
    )

    if not reviews:
        return None

    return reviews[-1]


def max_usefulness(
    data,
    lesson_id,
):
    reviews = reviews_for_lesson(
        data,
        lesson_id,
    )

    if not reviews:
        return None

    return max(
        int(
            review.get(
                "usefulness",
                0,
            )
        )
        for review in reviews
    )


# =========================================================
# CRUD
# =========================================================

def add_lesson(
    data,
    title,
    category,
    source_type,
    source_name,
    useful_expectation,
    emotional_impact,
    note,
    learned_date,
    favorite,
):
    lesson = {
        "id": new_id(),
        "title": title,
        "category": category,
        "source_type": source_type,
        "source_name": source_name,
        "useful_expectation": int(
            useful_expectation
        ),
        "emotional_impact": int(
            emotional_impact
        ),
        "note": note,
        "learned_date": str(
            learned_date
        ),
        "favorite": bool(
            favorite
        ),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["lessons"].append(
        lesson
    )

    save_data(data)


def add_review(
    data,
    lesson_id,
    review_date,
    usefulness,
    still_using,
    note,
):
    review = {
        "id": new_id(),
        "lesson_id": lesson_id,
        "review_date": str(
            review_date
        ),
        "usefulness": int(
            usefulness
        ),
        "still_using": int(
            still_using
        ),
        "note": note,
        "created_at": now_text(),
    }

    data["reviews"].append(
        review
    )

    lesson = get_lesson(
        data,
        lesson_id,
    )

    if lesson:
        lesson["updated_at"] = (
            now_text()
        )

    save_data(data)


def delete_lesson(
    data,
    lesson_id,
):
    data["lessons"] = [
        lesson
        for lesson in data["lessons"]
        if lesson.get("id")
        != lesson_id
    ]

    # 再評価も一緒に削除
    data["reviews"] = [
        review
        for review in data["reviews"]
        if review.get("lesson_id")
        != lesson_id
    ]

    save_data(data)


def delete_review(
    data,
    review_id,
):
    data["reviews"] = [
        review
        for review in data["reviews"]
        if review.get("id")
        != review_id
    ]

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .hero {
        padding: 42px 25px;
        text-align: center;
        border-radius: 28px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(255, 205, 90, .13),
                rgba(100, 170, 255, .10),
                rgba(255, 255, 255, .02)
            );
    }

    .lesson-card {
        padding: 20px;
        border-radius: 20px;
        border:
            1px solid rgba(
                255,
                200,
                90,
                .20
            );
        margin-bottom: 12px;
    }

    .quote-card {
        padding: 28px;
        border-radius: 24px;
        margin: 15px 0;
        text-align: center;
        background:
            linear-gradient(
                135deg,
                rgba(255, 205, 90, .10),
                rgba(120, 170, 255, .08)
            );
    }

    .timeline-item {
        padding: 16px 20px;
        margin: 10px 0;
        border-left:
            4px solid rgba(
                255,
                190,
                70,
                .45
            );
        border-radius: 8px;
        background:
            rgba(
                255,
                205,
                90,
                .04
            );
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background:
            rgba(
                255,
                205,
                90,
                .05
            );
        border:
            1px solid rgba(
                255,
                205,
                90,
                .12
            );
    }

    .footer {
        text-align: center;
        padding: 34px;
        margin-top: 35px;
        border-radius: 25px;
        background:
            rgba(
                255,
                205,
                90,
                .06
            );
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()

lessons = data["lessons"]
reviews = data["reviews"]

today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>👤💡 DAY 308 / 365</div>
        <h1>
            これ、誰に教えてもらった？
        </h1>
        <p>
            今日もらった知識や言葉の
            出どころを残しておこう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

(
    tab_home,
    tab_add,
    tab_review,
    tab_teachers,
    tab_lineage,
    tab_analysis,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🏠 ホーム",
        "💡 教えを記録",
        "🌱 今も使ってる？",
        "👤 先生図鑑",
        "🧬 知識の系譜",
        "📊 分析",
        "📚 教え図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    source_names = {
        lesson.get(
            "source_name",
            ""
        ).strip()
        for lesson in lessons
        if lesson.get(
            "source_name",
            ""
        ).strip()
    }

    reviewed_ids = {
        review.get(
            "lesson_id"
        )
        for review in reviews
    }

    favorite_count = sum(
        1
        for lesson in lessons
        if lesson.get(
            "favorite",
            False
        )
    )

    st.subheader(
        "💡 今までにもらったもの"
    )

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "💡 教わったこと",
        f"{len(lessons)}個",
    )

    c2.metric(
        "👤 教えてくれた存在",
        f"{len(source_names)}",
    )

    c3.metric(
        "🌱 再評価した教え",
        f"{len(reviewed_ids)}個",
    )

    c4.metric(
        "❤️ お気に入り",
        f"{favorite_count}個",
    )

    # -----------------------------------------------------
    # RECENT
    # -----------------------------------------------------

    if lessons:
        st.divider()

        st.subheader(
            "🆕 最近教わったこと"
        )

        recent = sorted(
            lessons,
            key=lambda x: x.get(
                "learned_date",
                "",
            ),
            reverse=True,
        )

        for lesson in recent[:5]:
            latest = latest_review(
                data,
                lesson.get("id"),
            )

            st.markdown(
                f"""
                <div class="lesson-card">
                    <b>
                        {lesson.get("category")}
                        {lesson.get("title")}
                    </b>
                    <br><br>

                    {lesson.get("source_type")}
                    {lesson.get("source_name")}
                    <br>

                    📅
                    {lesson.get("learned_date")}
                    <br><br>

                    💡 役立ちそう：
                    {stars(
                        lesson.get(
                            "useful_expectation"
                        )
                    )}
                    <br>

                    ❤️ 心に残った：
                    {stars(
                        lesson.get(
                            "emotional_impact"
                        )
                    )}
                    <br>

                    🌱 最新実用度：
                    {
                        stars(
                            latest.get(
                                "usefulness"
                            )
                        )
                        if latest
                        else "未評価"
                    }
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------
    # HEART
    # -----------------------------------------------------

    heart_lessons = [
        lesson
        for lesson in lessons
        if int(
            lesson.get(
                "emotional_impact",
                0,
            )
        ) >= 4
    ]

    if heart_lessons:
        st.divider()

        st.subheader(
            "❤️ 今でも残っている言葉・教え"
        )

        selected = random.choice(
            heart_lessons
        )

        st.markdown(
            f"""
            <div class="quote-card">
                <h3>
                    「{selected.get("title")}」
                </h3>

                <p>
                    {selected.get("source_type")}
                    {selected.get("source_name")}
                </p>

                <p>
                    {stars(
                        selected.get(
                            "emotional_impact"
                        )
                    )}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# ADD LESSON
# =========================================================

with tab_add:

    st.subheader(
        "💡 今日、何を教えてもらった？"
    )

    st.caption(
        "人、本、AI、動画。"
        "先生は人間だけとは限りません。"
    )

    with st.form(
        "add_lesson_form",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "教わったこと",
            placeholder=(
                "例：エラー文は上から読む"
            ),
        )

        category = st.selectbox(
            "ジャンル",
            CATEGORIES,
        )

        source_type = st.selectbox(
            "誰・何から？",
            SOURCE_TYPES,
        )

        source_name = st.text_input(
            "名前",
            placeholder=(
                "例：会社の先輩 / "
                "ChatGPT / 本のタイトル"
            ),
        )

        learned_date = st.date_input(
            "教わった日",
            value=today,
            max_value=today,
        )

        useful = st.slider(
            "💡 役立ちそう度",
            1,
            5,
            3,
        )

        st.write(
            stars(useful)
        )

        emotional = st.slider(
            "❤️ 心に残った度",
            1,
            5,
            3,
        )

        st.write(
            stars(emotional)
        )

        note = st.text_area(
            "ひとこと・メモ",
            placeholder=(
                "例：エラーを見るのが"
                "少し怖くなくなった"
            ),
        )

        favorite = st.checkbox(
            "❤️ お気に入りにする"
        )

        submitted = (
            st.form_submit_button(
                "💡 教えを残す",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.warning(
                    "教わったことを"
                    "入力してね。"
                )

            elif not source_name.strip():
                st.warning(
                    "誰・何から教わったのか"
                    "入力してね。"
                )

            else:
                add_lesson(
                    data=data,
                    title=title.strip(),
                    category=category,
                    source_type=(
                        source_type
                    ),
                    source_name=(
                        source_name.strip()
                    ),
                    useful_expectation=(
                        useful
                    ),
                    emotional_impact=(
                        emotional
                    ),
                    note=note.strip(),
                    learned_date=(
                        learned_date
                    ),
                    favorite=favorite,
                )

                st.rerun()


# =========================================================
# REVIEW
# =========================================================

with tab_review:

    st.subheader(
        "🌱 今も使ってる？"
    )

    if not lessons:
        st.info(
            "まずは教わったことを"
            "登録してみよう。"
        )

    else:
        options = {
            lesson_label(lesson):
            lesson.get("id")
            for lesson in lessons
        }

        selected_label = (
            st.selectbox(
                "振り返る教え",
                list(
                    options.keys()
                ),
                key="review_lesson",
            )
        )

        selected_id = options[
            selected_label
        ]

        lesson = get_lesson(
            data,
            selected_id,
        )

        st.markdown(
            f"### {lesson.get('category')} "
            f"{lesson.get('title')}"
        )

        st.caption(
            f"{lesson.get('source_type')} "
            f"{lesson.get('source_name')} "
            f"｜{lesson.get('learned_date')}"
        )

        days = days_since(
            lesson.get(
                "learned_date"
            )
        )

        if days is not None:
            st.info(
                f"教わってから "
                f"**{days}日** 経ちました。"
            )

        c1, c2 = st.columns(2)

        c1.metric(
            "当時の期待",
            (
                f"{lesson.get('useful_expectation')}"
                " / 5"
            ),
        )

        latest = latest_review(
            data,
            selected_id,
        )

        c2.metric(
            "最新の実用度",
            (
                f"{latest.get('usefulness')} / 5"
                if latest
                else "-"
            ),
        )

        with st.form(
            "add_review_form"
        ):
            review_date = st.date_input(
                "振り返る日",
                value=today,
                max_value=today,
            )

            usefulness = st.slider(
                "💡 実際どれくらい役立ってる？",
                1,
                5,
                3,
            )

            still_using = st.slider(
                "🌱 今も使ってる度",
                1,
                5,
                3,
            )

            note = st.text_area(
                "実際どう役立った？",
                placeholder=(
                    "例：エラーが出たら"
                    "まず自分で読む癖がついた"
                ),
            )

            submitted = (
                st.form_submit_button(
                    "🌱 再評価を追加",
                    type="primary",
                    use_container_width=True,
                )
            )

            if submitted:
                learned = parse_date(
                    lesson.get(
                        "learned_date"
                    )
                )

                if (
                    learned
                    and review_date < learned
                ):
                    st.warning(
                        "教わった日より"
                        "前にはできません。"
                    )

                else:
                    add_review(
                        data=data,
                        lesson_id=(
                            selected_id
                        ),
                        review_date=(
                            review_date
                        ),
                        usefulness=(
                            usefulness
                        ),
                        still_using=(
                            still_using
                        ),
                        note=note.strip(),
                    )

                    st.rerun()

        # REVIEW HISTORY
        lesson_reviews = (
            reviews_for_lesson(
                data,
                selected_id,
            )
        )

        if lesson_reviews:
            st.divider()

            st.markdown(
                "### 🕰️ この教えの変化"
            )

            st.markdown(
                f"""
                <div class="timeline-item">
                    <b>
                        💡 {lesson.get("learned_date")}
                    </b>
                    <br>
                    教わった
                    <br>
                    期待：
                    {stars(
                        lesson.get(
                            "useful_expectation"
                        )
                    )}
                    <br>
                    {lesson.get("note", "")}
                </div>
                """,
                unsafe_allow_html=True,
            )

            for review in lesson_reviews:
                st.markdown(
                    f"""
                    <div class="timeline-item">
                        <b>
                            🌱 {review.get("review_date")}
                        </b>
                        <br>
                        実用度：
                        {stars(
                            review.get(
                                "usefulness"
                            )
                        )}
                        <br>
                        今も使う：
                        {stars(
                            review.get(
                                "still_using"
                            )
                        )}
                        <br>
                        {review.get("note", "")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =========================================================
# TEACHERS
# =========================================================

with tab_teachers:

    st.subheader(
        "👤 先生図鑑"
    )

    if not lessons:
        st.info(
            "記録が増えると、"
            "ここに先生たちが並びます。"
        )

    else:
        teacher_groups = (
            defaultdict(list)
        )

        for lesson in lessons:
            key = (
                lesson.get(
                    "source_type",
                    ""
                ),
                lesson.get(
                    "source_name",
                    ""
                ),
            )

            teacher_groups[
                key
            ].append(
                lesson
            )

        teacher_rows = []

        for (
            source_type,
            source_name,
        ), teacher_lessons in (
            teacher_groups.items()
        ):
            expectations = [
                int(
                    lesson.get(
                        "useful_expectation",
                        0,
                    )
                )
                for lesson
                in teacher_lessons
            ]

            emotional = [
                int(
                    lesson.get(
                        "emotional_impact",
                        0,
                    )
                )
                for lesson
                in teacher_lessons
            ]

            review_values = []

            for lesson in (
                teacher_lessons
            ):
                latest = latest_review(
                    data,
                    lesson.get("id"),
                )

                if latest:
                    review_values.append(
                        int(
                            latest.get(
                                "usefulness",
                                0,
                            )
                        )
                    )

            teacher_rows.append(
                {
                    "種類":
                        source_type,
                    "先生":
                        source_name,
                    "教わった数":
                        len(
                            teacher_lessons
                        ),
                    "平均期待":
                        round(
                            sum(
                                expectations
                            )
                            / len(
                                expectations
                            ),
                            1,
                        ),
                    "平均心残り":
                        round(
                            sum(emotional)
                            / len(emotional),
                            1,
                        ),
                    "最新平均実用度":
                        (
                            round(
                                sum(
                                    review_values
                                )
                                / len(
                                    review_values
                                ),
                                1,
                            )
                            if review_values
                            else None
                        ),
                }
            )

        teacher_df = (
            pd.DataFrame(
                teacher_rows
            )
            .sort_values(
                "教わった数",
                ascending=False,
            )
        )

        st.dataframe(
            teacher_df,
            hide_index=True,
            use_container_width=True,
        )

        st.divider()

        st.markdown(
            "### 👑 記録上たくさん学んだ存在"
        )

        top_teachers = sorted(
            teacher_groups.items(),
            key=lambda x: len(
                x[1]
            ),
            reverse=True,
        )

        for rank, (
            (
                source_type,
                source_name,
            ),
            teacher_lessons,
        ) in enumerate(
            top_teachers[:10],
            start=1,
        ):
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### {rank}. "
                    f"{source_type} "
                    f"{source_name}"
                )

                st.caption(
                    f"教わったこと："
                    f"{len(teacher_lessons)}個"
                )

                category_counter = Counter(
                    lesson.get(
                        "category"
                    )
                    for lesson
                    in teacher_lessons
                )

                category_text = " / ".join(
                    f"{category} {count}"
                    for category, count
                    in category_counter
                    .most_common()
                )

                st.write(
                    category_text
                )

                with st.expander(
                    "教わったことを見る"
                ):
                    for lesson in sorted(
                        teacher_lessons,
                        key=lambda x:
                        x.get(
                            "learned_date",
                            "",
                        ),
                        reverse=True,
                    ):
                        st.write(
                            f"・{lesson.get('title')}"
                        )

        st.caption(
            "※教わった数が多いことは、"
            "先生としての優劣を"
            "表すものではありません。"
        )


# =========================================================
# LINEAGE
# =========================================================

with tab_lineage:

    st.subheader(
        "🧬 知識の系譜"
    )

    st.caption(
        "自分がその分野を"
        "どこから学んできたのか、"
        "時系列で見てみよう。"
    )

    if not lessons:
        st.info(
            "まだ教えがありません。"
        )

    else:
        existing_categories = [
            category
            for category
            in CATEGORIES
            if any(
                lesson.get(
                    "category"
                ) == category
                for lesson in lessons
            )
        ]

        selected_category = (
            st.selectbox(
                "分野",
                existing_categories,
            )
        )

        category_lessons = [
            lesson
            for lesson in lessons
            if lesson.get(
                "category"
            )
            == selected_category
        ]

        category_lessons.sort(
            key=lambda x: (
                x.get(
                    "learned_date",
                    ""
                ),
                x.get(
                    "created_at",
                    ""
                ),
            )
        )

        st.markdown(
            f"## {selected_category}"
        )

        for index, lesson in enumerate(
            category_lessons
        ):
            st.markdown(
                f"""
                <div class="timeline-item">
                    <b>
                        {lesson.get("learned_date")}
                    </b>
                    <br>
                    {lesson.get("source_type")}
                    <b>
                        {lesson.get("source_name")}
                    </b>
                    <br><br>
                    💡
                    {lesson.get("title")}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if (
                index
                < len(
                    category_lessons
                ) - 1
            ):
                st.markdown(
                    "<div style='text-align:center;'>↓</div>",
                    unsafe_allow_html=True,
                )


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 自分は何から学んできた？"
    )

    if not lessons:
        st.info(
            "記録が増えると"
            "分析が表示されます。"
        )

    else:
        # -------------------------------------------------
        # METRICS
        # -------------------------------------------------

        expectations = [
            int(
                lesson.get(
                    "useful_expectation",
                    0,
                )
            )
            for lesson in lessons
        ]

        emotional_values = [
            int(
                lesson.get(
                    "emotional_impact",
                    0,
                )
            )
            for lesson in lessons
        ]

        latest_values = []

        for lesson in lessons:
            latest = latest_review(
                data,
                lesson.get("id"),
            )

            if latest:
                latest_values.append(
                    int(
                        latest.get(
                            "usefulness",
                            0,
                        )
                    )
                )

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "💡 教え",
            len(lessons),
        )

        c2.metric(
            "平均期待",
            (
                f"{sum(expectations) / len(expectations):.1f}"
                if expectations
                else "-"
            ),
        )

        c3.metric(
            "平均心残り",
            (
                f"{sum(emotional_values) / len(emotional_values):.1f}"
                if emotional_values
                else "-"
            ),
        )

        c4.metric(
            "最新平均実用度",
            (
                f"{sum(latest_values) / len(latest_values):.1f}"
                if latest_values
                else "-"
            ),
        )

        # -------------------------------------------------
        # SOURCE TYPES
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🧭 誰・何から学んでいる？"
        )

        source_counter = Counter(
            lesson.get(
                "source_type"
            )
            for lesson in lessons
        )

        source_df = pd.DataFrame(
            [
                {
                    "情報源": source,
                    "教わった数": count,
                }
                for source, count
                in source_counter
                .most_common()
            ]
        )

        st.dataframe(
            source_df,
            hide_index=True,
            use_container_width=True,
        )

        if not source_df.empty:
            st.bar_chart(
                source_df.set_index(
                    "情報源"
                )
            )

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 📚 分野別"
        )

        category_rows = []

        for category in CATEGORIES:
            category_lessons = [
                lesson
                for lesson in lessons
                if lesson.get(
                    "category"
                ) == category
            ]

            if not category_lessons:
                continue

            source_counts = Counter(
                lesson.get(
                    "source_type"
                )
                for lesson
                in category_lessons
            )

            top_source = (
                source_counts
                .most_common(1)[0][0]
            )

            category_rows.append(
                {
                    "分野": category,
                    "教え": len(
                        category_lessons
                    ),
                    "一番多い情報源":
                        top_source,
                }
            )

        category_df = pd.DataFrame(
            category_rows
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        # -------------------------------------------------
        # SURPRISE
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 😲 思った以上に役立った"
        )

        surprises = []

        for lesson in lessons:
            initial = int(
                lesson.get(
                    "useful_expectation",
                    0,
                )
            )

            maximum = max_usefulness(
                data,
                lesson.get("id"),
            )

            if (
                initial <= 2
                and maximum is not None
                and maximum >= 4
            ):
                surprises.append(
                    (
                        maximum - initial,
                        lesson,
                        maximum,
                    )
                )

        surprises.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        if not surprises:
            st.caption(
                "まだ該当する教えは"
                "ありません。"
            )

        for (
            difference,
            lesson,
            maximum,
        ) in surprises:
            with st.container(
                border=True
            ):
                st.write(
                    f"**{lesson.get('title')}**"
                )

                st.caption(
                    f"{lesson.get('source_type')} "
                    f"{lesson.get('source_name')}"
                )

                st.write(
                    f"{stars(lesson.get('useful_expectation'))}"
                    f" → "
                    f"{stars(maximum)}"
                )

                st.success(
                    f"+{difference}"
                )

        # -------------------------------------------------
        # HEART
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### ❤️ 心に残った教え"
        )

        heart = sorted(
            [
                lesson
                for lesson in lessons
                if int(
                    lesson.get(
                        "emotional_impact",
                        0,
                    )
                ) >= 4
            ],
            key=lambda x: int(
                x.get(
                    "emotional_impact",
                    0,
                )
            ),
            reverse=True,
        )

        if not heart:
            st.caption(
                "まだ該当する教えは"
                "ありません。"
            )

        for lesson in heart[:10]:
            st.write(
                f"**「{lesson.get('title')}」**"
            )

            st.caption(
                f"{lesson.get('source_type')} "
                f"{lesson.get('source_name')} "
                f"｜"
                f"{stars(lesson.get('emotional_impact'))}"
            )

        # -------------------------------------------------
        # RANDOM OLD
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🎲 昔教えてもらったこと"
        )

        old_lessons = [
            lesson
            for lesson in lessons
            if (
                days_since(
                    lesson.get(
                        "learned_date"
                    )
                )
                is not None
                and days_since(
                    lesson.get(
                        "learned_date"
                    )
                ) >= 30
            )
        ]

        candidates = (
            old_lessons
            if old_lessons
            else lessons
        )

        candidate_ids = [
            lesson.get("id")
            for lesson in candidates
        ]

        random_id = (
            st.session_state.get(
                "random_old_lesson"
            )
        )

        if random_id not in candidate_ids:
            random_id = random.choice(
                candidate_ids
            )

            st.session_state[
                "random_old_lesson"
            ] = random_id

        random_lesson = get_lesson(
            data,
            random_id,
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### 💡 "
                f"{random_lesson.get('title')}"
            )

            random_days = days_since(
                random_lesson.get(
                    "learned_date"
                )
            )

            if random_days is not None:
                st.caption(
                    f"{random_days}日前"
                )

            st.write(
                f"{random_lesson.get('source_type')} "
                f"**{random_lesson.get('source_name')}**"
            )

            st.write(
                "当時の期待："
                + stars(
                    random_lesson.get(
                        "useful_expectation"
                    )
                )
            )

            if random_lesson.get(
                "note"
            ):
                st.info(
                    random_lesson.get(
                        "note"
                    )
                )

        if st.button(
            "🎲 別の教えを見る",
            use_container_width=True,
        ):
            alternatives = [
                lesson_id
                for lesson_id
                in candidate_ids
                if lesson_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_old_lesson"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 教え図鑑"
    )

    search = st.text_input(
        "🔎 検索",
        key="library_search",
    )

    c1, c2 = st.columns(2)

    with c1:
        category_filter = (
            st.selectbox(
                "ジャンル",
                ["すべて"]
                + CATEGORIES,
                key=(
                    "library_category"
                ),
            )
        )

    with c2:
        source_filter = (
            st.selectbox(
                "情報源",
                ["すべて"]
                + SOURCE_TYPES,
                key=(
                    "library_source"
                ),
            )
        )

    favorite_only = st.checkbox(
        "❤️ お気に入りだけ",
        key="library_favorite",
    )

    rows = []

    for lesson in lessons:
        if (
            category_filter
            != "すべて"
            and lesson.get(
                "category"
            )
            != category_filter
        ):
            continue

        if (
            source_filter
            != "すべて"
            and lesson.get(
                "source_type"
            )
            != source_filter
        ):
            continue

        if (
            favorite_only
            and not lesson.get(
                "favorite",
                False,
            )
        ):
            continue

        searchable = " ".join(
            [
                lesson.get(
                    "title",
                    "",
                ),
                lesson.get(
                    "source_name",
                    "",
                ),
                lesson.get(
                    "note",
                    "",
                ),
            ]
        ).lower()

        if (
            search.strip()
            and search.strip().lower()
            not in searchable
        ):
            continue

        latest = latest_review(
            data,
            lesson.get("id"),
        )

        rows.append(
            {
                "教わったこと":
                    lesson.get(
                        "title"
                    ),
                "誰から":
                    (
                        f"{lesson.get('source_type')} "
                        f"{lesson.get('source_name')}"
                    ),
                "分野":
                    lesson.get(
                        "category"
                    ),
                "教わった日":
                    lesson.get(
                        "learned_date"
                    ),
                "期待":
                    lesson.get(
                        "useful_expectation"
                    ),
                "心残り":
                    lesson.get(
                        "emotional_impact"
                    ),
                "最新実用度":
                    (
                        latest.get(
                            "usefulness"
                        )
                        if latest
                        else "-"
                    ),
                "再評価":
                    len(
                        reviews_for_lesson(
                            data,
                            lesson.get("id"),
                        )
                    ),
                "❤️":
                    (
                        "❤️"
                        if lesson.get(
                            "favorite"
                        )
                        else ""
                    ),
            }
        )

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "条件に合う教えは"
            "ありません。"
        )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 記録を管理"
    )

    if not lessons:
        st.info(
            "まだ教えがありません。"
        )

    else:
        options = {
            lesson_label(lesson):
            lesson.get("id")
            for lesson in lessons
        }

        selected_label = (
            st.selectbox(
                "編集する教え",
                list(
                    options.keys()
                ),
                key="manage_lesson",
            )
        )

        selected_id = options[
            selected_label
        ]

        lesson = get_lesson(
            data,
            selected_id,
        )

        edit_title = st.text_input(
            "教わったこと",
            value=lesson.get(
                "title",
                "",
            ),
        )

        old_category = lesson.get(
            "category",
            "📦 その他",
        )

        category_index = (
            CATEGORIES.index(
                old_category
            )
            if old_category
            in CATEGORIES
            else len(CATEGORIES) - 1
        )

        edit_category = st.selectbox(
            "ジャンル",
            CATEGORIES,
            index=category_index,
            key="manage_category",
        )

        old_source = lesson.get(
            "source_type",
            "📦 その他",
        )

        source_index = (
            SOURCE_TYPES.index(
                old_source
            )
            if old_source
            in SOURCE_TYPES
            else len(SOURCE_TYPES) - 1
        )

        edit_source = st.selectbox(
            "情報源",
            SOURCE_TYPES,
            index=source_index,
            key="manage_source",
        )

        edit_source_name = (
            st.text_input(
                "名前",
                value=lesson.get(
                    "source_name",
                    "",
                ),
            )
        )

        learned = (
            parse_date(
                lesson.get(
                    "learned_date"
                )
            )
            or today
        )

        edit_date = st.date_input(
            "教わった日",
            value=learned,
            max_value=today,
            key="manage_date",
        )

        edit_useful = st.slider(
            "役立ちそう度",
            1,
            5,
            int(
                lesson.get(
                    "useful_expectation",
                    3,
                )
            ),
            key="manage_useful",
        )

        edit_emotional = (
            st.slider(
                "心に残った度",
                1,
                5,
                int(
                    lesson.get(
                        "emotional_impact",
                        3,
                    )
                ),
                key=(
                    "manage_emotional"
                ),
            )
        )

        edit_note = st.text_area(
            "メモ",
            value=lesson.get(
                "note",
                "",
            ),
            key="manage_note",
        )

        edit_favorite = st.checkbox(
            "❤️ お気に入り",
            value=lesson.get(
                "favorite",
                False,
            ),
            key="manage_favorite",
        )

        if st.button(
            "💾 教えを保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_title.strip():
                st.warning(
                    "教わったことを"
                    "入力してね。"
                )

            elif not (
                edit_source_name.strip()
            ):
                st.warning(
                    "誰・何から教わったか"
                    "入力してね。"
                )

            else:
                lesson["title"] = (
                    edit_title.strip()
                )
                lesson["category"] = (
                    edit_category
                )
                lesson["source_type"] = (
                    edit_source
                )
                lesson["source_name"] = (
                    edit_source_name.strip()
                )
                lesson[
                    "learned_date"
                ] = str(
                    edit_date
                )
                lesson[
                    "useful_expectation"
                ] = int(
                    edit_useful
                )
                lesson[
                    "emotional_impact"
                ] = int(
                    edit_emotional
                )
                lesson["note"] = (
                    edit_note.strip()
                )
                lesson["favorite"] = (
                    edit_favorite
                )
                lesson["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # -------------------------------------------------
        # REVIEW MANAGEMENT
        # -------------------------------------------------

        lesson_reviews = (
            reviews_for_lesson(
                data,
                selected_id,
            )
        )

        st.divider()

        st.subheader(
            "🌱 再評価を管理"
        )

        if not lesson_reviews:
            st.caption(
                "この教えにはまだ"
                "再評価がありません。"
            )

        else:
            review_options = {
                (
                    f"{review.get('review_date')} "
                    f"｜実用度 "
                    f"{review.get('usefulness')} "
                    f"[{review.get('id', '')[:6]}]"
                ):
                review.get("id")
                for review
                in lesson_reviews
            }

            review_label = (
                st.selectbox(
                    "編集する再評価",
                    list(
                        review_options.keys()
                    ),
                    key=(
                        "manage_review"
                    ),
                )
            )

            review_id = (
                review_options[
                    review_label
                ]
            )

            review = get_review(
                data,
                review_id,
            )

            current_review_date = (
                parse_date(
                    review.get(
                        "review_date"
                    )
                )
                or today
            )

            edit_review_date = (
                st.date_input(
                    "再評価日",
                    value=(
                        current_review_date
                    ),
                    max_value=today,
                    key=(
                        "manage_review_date"
                    ),
                )
            )

            edit_review_useful = (
                st.slider(
                    "実用度",
                    1,
                    5,
                    int(
                        review.get(
                            "usefulness",
                            3,
                        )
                    ),
                    key=(
                        "manage_review_useful"
                    ),
                )
            )

            edit_still_using = (
                st.slider(
                    "今も使ってる度",
                    1,
                    5,
                    int(
                        review.get(
                            "still_using",
                            3,
                        )
                    ),
                    key=(
                        "manage_still_using"
                    ),
                )
            )

            edit_review_note = (
                st.text_area(
                    "再評価メモ",
                    value=review.get(
                        "note",
                        "",
                    ),
                    key=(
                        "manage_review_note"
                    ),
                )
            )

            if st.button(
                "💾 再評価を保存",
                use_container_width=True,
            ):
                learned_date = (
                    parse_date(
                        lesson.get(
                            "learned_date"
                        )
                    )
                )

                if (
                    learned_date
                    and edit_review_date
                    < learned_date
                ):
                    st.warning(
                        "教わった日より"
                        "前にはできません。"
                    )

                else:
                    review[
                        "review_date"
                    ] = str(
                        edit_review_date
                    )

                    review[
                        "usefulness"
                    ] = int(
                        edit_review_useful
                    )

                    review[
                        "still_using"
                    ] = int(
                        edit_still_using
                    )

                    review["note"] = (
                        edit_review_note.strip()
                    )

                    lesson[
                        "updated_at"
                    ] = now_text()

                    save_data(data)
                    st.rerun()

            confirm_review_delete = (
                st.checkbox(
                    "この再評価を削除する",
                    key=(
                        "confirm_review_"
                        + review_id
                    ),
                )
            )

            if st.button(
                "🗑️ 再評価を削除",
                disabled=(
                    not confirm_review_delete
                ),
                key=(
                    "delete_review_"
                    + review_id
                ),
                use_container_width=True,
            ):
                delete_review(
                    data,
                    review_id,
                )

                st.rerun()

        # -------------------------------------------------
        # LESSON DELETE
        # -------------------------------------------------

        st.divider()

        st.warning(
            "教えを削除すると、"
            "この教えの再評価も"
            "すべて削除されます。"
        )

        confirm_delete = st.checkbox(
            "この教えを完全に削除する",
            key=(
                "confirm_lesson_"
                + selected_id
            ),
        )

        if st.button(
            "🗑️ 教えを完全削除",
            disabled=(
                not confirm_delete
            ),
            key=(
                "delete_lesson_"
                + selected_id
            ),
            use_container_width=True,
        ):
            delete_lesson(
                data,
                selected_id,
            )

            st.rerun()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    backup_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=backup_text,
        file_name=(
            f"who_taught_me_{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        <p>
            <b>
                今の自分は、
                自分ひとりで作ったものじゃない。
            </b>
        </p>

        <p>
            誰かにもらった言葉。
            <br>
            本で読んだ一文。
            <br>
            何気なく教えてもらったコツ。
        </p>

        <p>
            忘れてしまっても、
            その教えは今の自分の
            どこかに残っている。
        </p>

        <p>
            <b>
                今日もらったものを、
                ひとつ残しておこう。👤💡
            </b>
        </p>

        <br>

        <b>
            DAY 308 / 365 — COMPLETE 🔥
        </b>

    </div>
    """,
    unsafe_allow_html=True,
)
