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
    page_title="あれ、前より楽じゃない？",
    page_icon="📈",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "growth.json",
)

CATEGORIES = [
    "📚 勉強",
    "💻 開発",
    "💼 仕事",
    "🏃 運動",
    "🏠 生活",
    "🎨 創作",
    "🗣️ コミュニケーション",
    "🚗 運転・移動",
    "✨ その他",
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

    return parsed.strftime(
        "%Y/%m/%d"
    )


def star_text(value):
    value = int(
        max(
            1,
            min(5, value),
        )
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def change_text(
    old,
    new,
    lower_is_better=False,
):
    difference = new - old

    if difference == 0:
        return "→ 変化なし"

    if lower_is_better:
        if difference < 0:
            return (
                f"↓ {abs(difference)}"
            )

        return f"↑ +{difference}"

    if difference > 0:
        return f"↑ +{difference}"

    return f"↓ {abs(difference)}"


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "skills": [],
        "records": [],
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
            "skills",
            [],
        )
        data.setdefault(
            "records",
            [],
        )

        for skill in data["skills"]:
            skill.setdefault(
                "id",
                create_id(),
            )
            skill.setdefault(
                "title",
                "",
            )
            skill.setdefault(
                "category",
                "✨ その他",
            )
            skill.setdefault(
                "description",
                "",
            )
            skill.setdefault(
                "favorite",
                False,
            )
            skill.setdefault(
                "created_at",
                now_text(),
            )
            skill.setdefault(
                "updated_at",
                skill.get(
                    "created_at",
                    now_text(),
                ),
            )

        for record in data[
            "records"
        ]:
            record.setdefault(
                "id",
                create_id(),
            )
            record.setdefault(
                "skill_id",
                "",
            )
            record.setdefault(
                "date",
                today_text(),
            )
            record.setdefault(
                "difficulty",
                3,
            )
            record.setdefault(
                "confidence",
                3,
            )
            record.setdefault(
                "fatigue",
                3,
            )
            record.setdefault(
                "minutes",
                0,
            )
            record.setdefault(
                "memo",
                "",
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
        data = empty_data()
        save_data(data)
        return data


# =========================================================
# 取得
# =========================================================

def get_skill(
    data,
    skill_id,
):
    return next(
        (
            skill
            for skill
            in data["skills"]
            if skill.get("id")
            == skill_id
        ),
        None,
    )


def get_record(
    data,
    record_id,
):
    return next(
        (
            record
            for record
            in data["records"]
            if record.get("id")
            == record_id
        ),
        None,
    )


def skill_records(
    data,
    skill_id,
):
    records = [
        record
        for record
        in data["records"]
        if record.get(
            "skill_id"
        ) == skill_id
    ]

    return sorted(
        records,
        key=lambda row: (
            row.get(
                "date",
                "",
            ),
            row.get(
                "created_at",
                "",
            ),
        ),
    )


# =========================================================
# 成長分析
# =========================================================

def growth_score(
    first,
    latest,
):
    if not first or not latest:
        return 0

    scores = []

    # 難しさ
    difficulty_change = (
        first["difficulty"]
        - latest["difficulty"]
    )

    difficulty_score = (
        50
        + difficulty_change * 12.5
    )

    scores.append(
        max(
            0,
            min(
                100,
                difficulty_score,
            ),
        )
    )

    # 自信
    confidence_change = (
        latest["confidence"]
        - first["confidence"]
    )

    confidence_score = (
        50
        + confidence_change * 12.5
    )

    scores.append(
        max(
            0,
            min(
                100,
                confidence_score,
            ),
        )
    )

    # 疲労
    fatigue_change = (
        first["fatigue"]
        - latest["fatigue"]
    )

    fatigue_score = (
        50
        + fatigue_change * 12.5
    )

    scores.append(
        max(
            0,
            min(
                100,
                fatigue_score,
            ),
        )
    )

    # 時間
    first_minutes = first.get(
        "minutes",
        0,
    )

    latest_minutes = latest.get(
        "minutes",
        0,
    )

    if (
        first_minutes > 0
        and latest_minutes > 0
    ):
        time_ratio = (
            latest_minutes
            / first_minutes
        )

        if time_ratio <= 0.5:
            time_score = 100

        elif time_ratio >= 1.5:
            time_score = 0

        else:
            time_score = (
                100
                - (
                    time_ratio
                    - 0.5
                )
                * 100
            )

        # 時間は参考値なので
        # 少し軽く扱う
        total = (
            sum(scores) * 0.9
            + time_score * 0.3
        ) / 3.0

        return int(
            max(
                0,
                min(100, total),
            )
        )

    return int(
        sum(scores)
        / len(scores)
    )


def growth_stage(
    records,
):
    if not records:
        return "🌱 はじめたばかり"

    latest = records[-1]

    count = len(records)

    difficulty = latest.get(
        "difficulty",
        3,
    )

    confidence = latest.get(
        "confidence",
        3,
    )

    if (
        count >= 8
        and difficulty <= 2
        and confidence >= 4
    ):
        return "✨ かなり慣れてきた"

    if (
        count >= 5
        and confidence >= 3
    ):
        return (
            "💪 自力でできることが増えた"
        )

    if (
        count >= 3
        and difficulty <= 4
    ):
        return "🧩 少し分かってきた"

    if count >= 2:
        return "👀 見覚えが出てきた"

    return "🌱 はじめたばかり"


def comparison_result(
    previous,
    current,
):
    if not previous or not current:
        return "first"

    points = 0

    if (
        current["difficulty"]
        < previous["difficulty"]
    ):
        points += 1

    elif (
        current["difficulty"]
        > previous["difficulty"]
    ):
        points -= 1

    if (
        current["confidence"]
        > previous["confidence"]
    ):
        points += 1

    elif (
        current["confidence"]
        < previous["confidence"]
    ):
        points -= 1

    if (
        current["fatigue"]
        < previous["fatigue"]
    ):
        points += 1

    elif (
        current["fatigue"]
        > previous["fatigue"]
    ):
        points -= 1

    old_minutes = previous.get(
        "minutes",
        0,
    )

    new_minutes = current.get(
        "minutes",
        0,
    )

    if (
        old_minutes > 0
        and new_minutes > 0
    ):
        if new_minutes < old_minutes:
            points += 1

        elif new_minutes > old_minutes:
            points -= 1

    if points >= 1:
        return "easier"

    if points <= -1:
        return "harder"

    return "same"


def consecutive_difficulty_growth(
    records,
):
    if len(records) < 2:
        return 0

    count = 0

    for index in range(
        len(records) - 1,
        0,
        -1,
    ):
        current = records[index]
        previous = records[
            index - 1
        ]

        if (
            current["difficulty"]
            < previous["difficulty"]
        ):
            count += 1
        else:
            break

    return count


def consecutive_confidence_growth(
    records,
):
    if len(records) < 2:
        return 0

    count = 0

    for index in range(
        len(records) - 1,
        0,
        -1,
    ):
        current = records[index]
        previous = records[
            index - 1
        ]

        if (
            current["confidence"]
            > previous["confidence"]
        ):
            count += 1
        else:
            break

    return count


# =========================================================
# CRUD
# =========================================================

def add_skill(
    data,
    title,
    category,
    description,
    record_date,
    difficulty,
    confidence,
    fatigue,
    minutes,
    memo,
):
    skill_id = create_id()

    skill = {
        "id": skill_id,
        "title": title,
        "category": category,
        "description": description,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["skills"].append(
        skill
    )

    record = {
        "id": create_id(),
        "skill_id": skill_id,
        "date": str(
            record_date
        ),
        "difficulty": int(
            difficulty
        ),
        "confidence": int(
            confidence
        ),
        "fatigue": int(
            fatigue
        ),
        "minutes": int(
            minutes
        ),
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["records"].append(
        record
    )

    save_data(data)


def add_record(
    data,
    skill_id,
    record_date,
    difficulty,
    confidence,
    fatigue,
    minutes,
    memo,
):
    record = {
        "id": create_id(),
        "skill_id": skill_id,
        "date": str(
            record_date
        ),
        "difficulty": int(
            difficulty
        ),
        "confidence": int(
            confidence
        ),
        "fatigue": int(
            fatigue
        ),
        "minutes": int(
            minutes
        ),
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["records"].append(
        record
    )

    skill = get_skill(
        data,
        skill_id,
    )

    if skill:
        skill[
            "updated_at"
        ] = now_text()

    save_data(data)

    return record


def update_skill(
    data,
    skill_id,
    title,
    category,
    description,
):
    skill = get_skill(
        data,
        skill_id,
    )

    if not skill:
        return

    skill["title"] = title
    skill["category"] = category
    skill[
        "description"
    ] = description
    skill[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    skill_id,
):
    skill = get_skill(
        data,
        skill_id,
    )

    if not skill:
        return

    skill[
        "favorite"
    ] = not skill.get(
        "favorite",
        False,
    )

    skill[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_record(
    data,
    record_id,
    record_date,
    difficulty,
    confidence,
    fatigue,
    minutes,
    memo,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["date"] = str(
        record_date
    )
    record[
        "difficulty"
    ] = int(difficulty)
    record[
        "confidence"
    ] = int(confidence)
    record[
        "fatigue"
    ] = int(fatigue)
    record[
        "minutes"
    ] = int(minutes)
    record["memo"] = memo
    record[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record
        in data["records"]
        if record.get("id")
        != record_id
    ]

    save_data(data)


def delete_skill(
    data,
    skill_id,
):
    data["skills"] = [
        skill
        for skill
        in data["skills"]
        if skill.get("id")
        != skill_id
    ]

    data["records"] = [
        record
        for record
        in data["records"]
        if record.get(
            "skill_id"
        ) != skill_id
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
        background: rgba(80, 170, 120, 0.07);
        border: 1px solid rgba(80, 170, 120, 0.16);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 190, 120, 0.18),
                rgba(80, 150, 220, 0.12)
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

    .growth-box {
        padding: 20px;
        border-radius: 20px;
        background: rgba(80, 180, 120, 0.08);
        border: 1px solid rgba(80, 180, 120, 0.18);
        margin: 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

skills = data["skills"]
records = data["records"]

today = date.today()


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📈 あれ、前より楽じゃない？</h1>
        <p>
            「できるようになった」だけじゃない。
            前より少し楽なら、それもちゃんと成長。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

st.subheader(
    "🌱 成長ダッシュボード"
)

total_comparisons = 0
easier_count = 0
same_count = 0
harder_count = 0

for skill in skills:
    skill_items = skill_records(
        data,
        skill.get("id"),
    )

    for index in range(
        1,
        len(skill_items),
    ):
        result = comparison_result(
            skill_items[
                index - 1
            ],
            skill_items[index],
        )

        total_comparisons += 1

        if result == "easier":
            easier_count += 1

        elif result == "same":
            same_count += 1

        elif result == "harder":
            harder_count += 1


col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🌱 成長テーマ",
    f"{len(skills)}個",
)

col2.metric(
    "📝 記録",
    f"{len(records)}回",
)

col3.metric(
    "📈 前より楽",
    f"{easier_count}回",
)

col4.metric(
    "🌿 変化なし",
    f"{same_count}回",
)


if total_comparisons:
    easier_rate = (
        easier_count
        / total_comparisons
        * 100
    )

    st.caption(
        f"これまでの比較のうち "
        f"{easier_rate:.0f}%で"
        "「前より楽」が見つかっています。"
    )


# =========================================================
# 新しい成長テーマ
# =========================================================

st.divider()

st.subheader(
    "➕ 成長を見たいこと"
)

with st.form(
    "new_skill_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "🌱 何の成長を見てみる？",
        placeholder=(
            "例：Pythonのクラス・継承"
        ),
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    description = st.text_area(
        "📝 どんなこと？",
        placeholder=(
            "長く追いかけたいことを"
            "簡単に書いておこう。"
        ),
    )

    st.markdown(
        "#### 🌱 最初の記録"
    )

    record_date = st.date_input(
        "📅 日付",
        value=today,
        max_value=today,
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:
        difficulty = st.slider(
            "😵 難しさ",
            1,
            5,
            5,
        )

        st.caption(
            star_text(
                difficulty
            )
        )

    with col2:
        confidence = st.slider(
            "💪 自信",
            1,
            5,
            1,
        )

        st.caption(
            star_text(
                confidence
            )
        )

    with col3:
        fatigue = st.slider(
            "🔋 疲労",
            1,
            5,
            3,
        )

        st.caption(
            star_text(
                fatigue
            )
        )

    minutes = st.number_input(
        "⏱️ かかった時間（分）",
        min_value=0,
        max_value=1440,
        value=0,
        step=5,
        help=(
            "分からなければ0でOK。"
            "時間は成長判定では参考値です。"
        ),
    )

    memo = st.text_area(
        "💭 今の自分の一言",
        placeholder=(
            "例：説明を読んでも"
            "まだよく分からない"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🌱 成長記録を始める",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "テーマ名を入力してね。"
            )

        else:
            add_skill(
                data=data,
                title=title.strip(),
                category=category,
                description=(
                    description.strip()
                ),
                record_date=(
                    record_date
                ),
                difficulty=(
                    difficulty
                ),
                confidence=(
                    confidence
                ),
                fatigue=fatigue,
                minutes=minutes,
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# 成長テーマ一覧
# =========================================================

st.divider()

st.subheader(
    "👀 成長を見守る"
)

if not skills:
    st.info(
        "まだ成長テーマがありません。"
        "まず一つ登録してみよう！"
    )

else:
    sorted_skills = sorted(
        skills,
        key=lambda item: (
            item.get(
                "favorite",
                False,
            ),
            item.get(
                "updated_at",
                "",
            ),
        ),
        reverse=True,
    )

    for skill in sorted_skills:
        skill_id = skill.get(
            "id",
            "",
        )

        skill_items = skill_records(
            data,
            skill_id,
        )

        if not skill_items:
            continue

        first = skill_items[0]
        latest = skill_items[-1]

        score = growth_score(
            first,
            latest,
        )

        stage = growth_stage(
            skill_items
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [8, 1]
            )

            with col1:
                st.subheader(
                    skill.get(
                        "title",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if skill.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "favorite_"
                        + skill_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        skill_id,
                    )
                    st.rerun()

            st.caption(
                skill.get(
                    "category",
                    ""
                )
                + " ｜ "
                + stage
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "📝 記録",
                f"{len(skill_items)}回",
            )

            col2.metric(
                "😵 今の難しさ",
                f"{latest['difficulty']} / 5",
                delta=(
                    first[
                        "difficulty"
                    ]
                    - latest[
                        "difficulty"
                    ]
                ),
                delta_color="normal",
            )

            col3.metric(
                "💪 今の自信",
                f"{latest['confidence']} / 5",
                delta=(
                    latest[
                        "confidence"
                    ]
                    - first[
                        "confidence"
                    ]
                ),
            )

            st.progress(
                score / 100
            )

            st.caption(
                f"🌱 成長スコア "
                f"{score} / 100"
                "（変化を見るための目安）"
            )

            # ---------------------------------------------
            # 初回 → 現在
            # ---------------------------------------------

            if len(
                skill_items
            ) >= 2:
                st.markdown(
                    "#### 📈 最初 → 今"
                )

                c1, c2, c3, c4 = (
                    st.columns(4)
                )

                c1.metric(
                    "😵 難しさ",
                    (
                        f"{first['difficulty']}"
                        f" → "
                        f"{latest['difficulty']}"
                    ),
                    delta=(
                        first[
                            "difficulty"
                        ]
                        - latest[
                            "difficulty"
                        ]
                    ),
                )

                c2.metric(
                    "💪 自信",
                    (
                        f"{first['confidence']}"
                        f" → "
                        f"{latest['confidence']}"
                    ),
                    delta=(
                        latest[
                            "confidence"
                        ]
                        - first[
                            "confidence"
                        ]
                    ),
                )

                c3.metric(
                    "🔋 疲労",
                    (
                        f"{first['fatigue']}"
                        f" → "
                        f"{latest['fatigue']}"
                    ),
                    delta=(
                        first[
                            "fatigue"
                        ]
                        - latest[
                            "fatigue"
                        ]
                    ),
                )

                first_minutes = (
                    first.get(
                        "minutes",
                        0,
                    )
                )

                latest_minutes = (
                    latest.get(
                        "minutes",
                        0,
                    )
                )

                if (
                    first_minutes > 0
                    and latest_minutes > 0
                ):
                    c4.metric(
                        "⏱️ 時間",
                        (
                            f"{first_minutes}"
                            f" → "
                            f"{latest_minutes}分"
                        ),
                        delta=(
                            first_minutes
                            - latest_minutes
                        ),
                    )

                else:
                    c4.metric(
                        "⏱️ 時間",
                        "-",
                    )

                if (
                    latest["difficulty"]
                    < first["difficulty"]
                    or latest[
                        "confidence"
                    ]
                    > first[
                        "confidence"
                    ]
                ):
                    st.success(
                        "🌱 最初の頃より、"
                        "ちゃんと変化が"
                        "積み重なっています。"
                    )

            # ---------------------------------------------
            # 連続成長
            # ---------------------------------------------

            difficulty_streak = (
                consecutive_difficulty_growth(
                    skill_items
                )
            )

            confidence_streak = (
                consecutive_confidence_growth(
                    skill_items
                )
            )

            if difficulty_streak >= 2:
                st.success(
                    f"🔥 {difficulty_streak}回連続で"
                    "難しさが下がっています！"
                )

            if confidence_streak >= 2:
                st.success(
                    f"💪 {confidence_streak}回連続で"
                    "自信が上がっています！"
                )

            # ---------------------------------------------
            # 今回を記録
            # ---------------------------------------------

            with st.expander(
                "🌱 今回を記録"
            ):
                new_date = (
                    st.date_input(
                        "📅 日付",
                        value=today,
                        max_value=today,
                        key=(
                            "new_date_"
                            + skill_id
                        ),
                    )
                )

                c1, c2, c3 = (
                    st.columns(3)
                )

                with c1:
                    new_difficulty = (
                        st.slider(
                            "😵 難しさ",
                            1,
                            5,
                            latest[
                                "difficulty"
                            ],
                            key=(
                                "new_diff_"
                                + skill_id
                            ),
                        )
                    )

                with c2:
                    new_confidence = (
                        st.slider(
                            "💪 自信",
                            1,
                            5,
                            latest[
                                "confidence"
                            ],
                            key=(
                                "new_conf_"
                                + skill_id
                            ),
                        )
                    )

                with c3:
                    new_fatigue = (
                        st.slider(
                            "🔋 疲労",
                            1,
                            5,
                            latest[
                                "fatigue"
                            ],
                            key=(
                                "new_fatigue_"
                                + skill_id
                            ),
                        )
                    )

                new_minutes = (
                    st.number_input(
                        "⏱️ 時間（分）",
                        min_value=0,
                        max_value=1440,
                        value=0,
                        step=5,
                        key=(
                            "new_minutes_"
                            + skill_id
                        ),
                    )
                )

                new_memo = (
                    st.text_area(
                        "💭 今回どうだった？",
                        key=(
                            "new_memo_"
                            + skill_id
                        ),
                    )
                )

                if st.button(
                    "🌱 記録する",
                    key=(
                        "save_record_"
                        + skill_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    new_record = add_record(
                        data=data,
                        skill_id=(
                            skill_id
                        ),
                        record_date=(
                            new_date
                        ),
                        difficulty=(
                            new_difficulty
                        ),
                        confidence=(
                            new_confidence
                        ),
                        fatigue=(
                            new_fatigue
                        ),
                        minutes=(
                            new_minutes
                        ),
                        memo=(
                            new_memo.strip()
                        ),
                    )

                    result = (
                        comparison_result(
                            latest,
                            new_record,
                        )
                    )

                    st.session_state[
                        "growth_result"
                    ] = {
                        "skill_id": (
                            skill_id
                        ),
                        "result": result,
                    }

                    st.rerun()

            # ---------------------------------------------
            # グラフ
            # ---------------------------------------------

            with st.expander(
                "📊 成長グラフ"
            ):
                chart_rows = []

                for index, record in enumerate(
                    skill_items,
                    start=1,
                ):
                    chart_rows.append(
                        {
                            "記録": index,
                            "日付": format_date(
                                record.get(
                                    "date"
                                )
                            ),
                            "難しさ": (
                                record[
                                    "difficulty"
                                ]
                            ),
                            "自信": (
                                record[
                                    "confidence"
                                ]
                            ),
                            "疲労": (
                                record[
                                    "fatigue"
                                ]
                            ),
                            "時間": (
                                record.get(
                                    "minutes",
                                    0,
                                )
                            ),
                        }
                    )

                chart_df = pd.DataFrame(
                    chart_rows
                )

                metric = st.selectbox(
                    "表示する項目",
                    [
                        "難しさ",
                        "自信",
                        "疲労",
                        "時間",
                    ],
                    key=(
                        "chart_metric_"
                        + skill_id
                    ),
                )

                if not chart_df.empty:
                    graph_df = (
                        chart_df[
                            [
                                "記録",
                                metric,
                            ]
                        ]
                        .set_index(
                            "記録"
                        )
                    )

                    st.line_chart(
                        graph_df
                    )

                    st.dataframe(
                        chart_df,
                        hide_index=True,
                        use_container_width=True,
                    )


# =========================================================
# 記録直後の比較
# =========================================================

growth_result = (
    st.session_state.get(
        "growth_result"
    )
)

if growth_result:
    result_skill = get_skill(
        data,
        growth_result.get(
            "skill_id"
        ),
    )

    if result_skill:
        result_records = (
            skill_records(
                data,
                result_skill.get(
                    "id"
                ),
            )
        )

        if len(
            result_records
        ) >= 2:
            previous = result_records[-2]
            current = result_records[-1]

            st.divider()

            result = growth_result.get(
                "result"
            )

            if result == "easier":
                st.success(
                    "🌱 前より楽になった！"
                )

            elif result == "harder":
                st.info(
                    "🌧️ 今回は前より"
                    "大変だったみたい。"
                    "そんな回も成長記録の一部。"
                )

            else:
                st.info(
                    "🌿 今回はほぼ変化なし。"
                    "続けていること自体も"
                    "大事な記録です。"
                )

            st.subheader(
                result_skill.get(
                    "title",
                    "",
                )
            )

            c1, c2, c3, c4 = (
                st.columns(4)
            )

            c1.metric(
                "😵 難しさ",
                (
                    f"{previous['difficulty']}"
                    f" → "
                    f"{current['difficulty']}"
                ),
                delta=(
                    previous[
                        "difficulty"
                    ]
                    - current[
                        "difficulty"
                    ]
                ),
            )

            c2.metric(
                "💪 自信",
                (
                    f"{previous['confidence']}"
                    f" → "
                    f"{current['confidence']}"
                ),
                delta=(
                    current[
                        "confidence"
                    ]
                    - previous[
                        "confidence"
                    ]
                ),
            )

            c3.metric(
                "🔋 疲労",
                (
                    f"{previous['fatigue']}"
                    f" → "
                    f"{current['fatigue']}"
                ),
                delta=(
                    previous[
                        "fatigue"
                    ]
                    - current[
                        "fatigue"
                    ]
                ),
            )

            old_minutes = (
                previous.get(
                    "minutes",
                    0,
                )
            )

            new_minutes = (
                current.get(
                    "minutes",
                    0,
                )
            )

            if (
                old_minutes > 0
                and new_minutes > 0
            ):
                c4.metric(
                    "⏱️ 時間",
                    (
                        f"{old_minutes}"
                        f" → "
                        f"{new_minutes}分"
                    ),
                    delta=(
                        old_minutes
                        - new_minutes
                    ),
                )

    if st.button(
        "OK",
        key="clear_growth_result",
    ):
        del st.session_state[
            "growth_result"
        ]
        st.rerun()


# =========================================================
# ランキング
# =========================================================

if skills:
    st.divider()

    st.subheader(
        "🏆 成長ランキング"
    )

    ranking = []

    for skill in skills:
        items = skill_records(
            data,
            skill.get("id"),
        )

        if len(items) < 2:
            continue

        first = items[0]
        latest = items[-1]

        ranking.append(
            {
                "skill": skill,
                "difficulty_change": (
                    first[
                        "difficulty"
                    ]
                    - latest[
                        "difficulty"
                    ]
                ),
                "confidence_change": (
                    latest[
                        "confidence"
                    ]
                    - first[
                        "confidence"
                    ]
                ),
                "time_change": (
                    first.get(
                        "minutes",
                        0,
                    )
                    - latest.get(
                        "minutes",
                        0,
                    )
                    if (
                        first.get(
                            "minutes",
                            0,
                        ) > 0
                        and latest.get(
                            "minutes",
                            0,
                        ) > 0
                    )
                    else None
                ),
            }
        )

    if ranking:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                "#### 🌱 一番楽になった"
            )

            easier_ranking = sorted(
                ranking,
                key=lambda row: row[
                    "difficulty_change"
                ],
                reverse=True,
            )

            for rank, row in enumerate(
                easier_ranking[:5],
                start=1,
            ):
                st.write(
                    f"**{rank}. "
                    f"{row['skill'].get('title', '')}**"
                )

                st.caption(
                    "難しさ "
                    f"{row['difficulty_change']:+d}"
                )

        with col2:
            st.markdown(
                "#### 💪 自信が伸びた"
            )

            confidence_ranking = (
                sorted(
                    ranking,
                    key=lambda row: row[
                        "confidence_change"
                    ],
                    reverse=True,
                )
            )

            for rank, row in enumerate(
                confidence_ranking[:5],
                start=1,
            ):
                st.write(
                    f"**{rank}. "
                    f"{row['skill'].get('title', '')}**"
                )

                st.caption(
                    "自信 "
                    f"{row['confidence_change']:+d}"
                )

        time_ranking = [
            row
            for row in ranking
            if row[
                "time_change"
            ] is not None
            and row[
                "time_change"
            ] > 0
        ]

        if time_ranking:
            st.markdown(
                "#### ⏱️ 最初より早くなった"
            )

            time_ranking = sorted(
                time_ranking,
                key=lambda row: row[
                    "time_change"
                ],
                reverse=True,
            )

            for row in time_ranking[:5]:
                items = skill_records(
                    data,
                    row[
                        "skill"
                    ].get("id"),
                )

                first = items[0]
                latest = items[-1]

                st.write(
                    f"**{row['skill'].get('title', '')}**"
                    f"　"
                    f"{first.get('minutes', 0)}分"
                    f" → "
                    f"{latest.get('minutes', 0)}分"
                    f"　"
                    f"(-{row['time_change']}分)"
                )


# =========================================================
# 月間レポート
# =========================================================

if records:
    st.divider()

    st.subheader(
        "📅 今月の成長"
    )

    month_key = today.strftime(
        "%Y-%m"
    )

    month_records = [
        record
        for record in records
        if record.get(
            "date",
            ""
        ).startswith(
            month_key
        )
    ]

    month_easier = 0
    month_same = 0
    month_harder = 0

    for skill in skills:
        items = skill_records(
            data,
            skill.get("id"),
        )

        for index in range(
            1,
            len(items),
        ):
            current = items[index]

            if not current.get(
                "date",
                ""
            ).startswith(
                month_key
            ):
                continue

            result = comparison_result(
                items[index - 1],
                current,
            )

            if result == "easier":
                month_easier += 1

            elif result == "same":
                month_same += 1

            elif result == "harder":
                month_harder += 1

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "📝 記録",
        f"{len(month_records)}回",
    )

    c2.metric(
        "🌱 前より楽",
        f"{month_easier}回",
    )

    c3.metric(
        "🌿 変化なし",
        f"{month_same}回",
    )

    c4.metric(
        "🌧️ 前より大変",
        f"{month_harder}回",
    )


# =========================================================
# 昔の自分ガチャ
# =========================================================

old_skills = []

for skill in skills:
    items = skill_records(
        data,
        skill.get("id"),
    )

    if not items:
        continue

    first_date = parse_date(
        items[0].get(
            "date"
        )
    )

    if (
        first_date
        and (
            today
            - first_date
        ).days >= 30
    ):
        old_skills.append(
            skill
        )

if old_skills:
    st.divider()

    st.subheader(
        "🎲 昔はこんなに大変だった"
    )

    old_ids = [
        skill.get("id")
        for skill in old_skills
    ]

    random_id = (
        st.session_state.get(
            "random_growth_skill"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_growth_skill"
        ] = random_id

    random_skill = get_skill(
        data,
        random_id,
    )

    if random_skill:
        items = skill_records(
            data,
            random_id,
        )

        first = items[0]
        latest = items[-1]

        first_date = parse_date(
            first.get(
                "date"
            )
        )

        age = (
            (
                today
                - first_date
            ).days
            if first_date
            else 0
        )

        with st.container(
            border=True
        ):
            st.caption(
                f"🎲 {age}日前の自分"
            )

            st.subheader(
                random_skill.get(
                    "title",
                    "",
                )
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    "#### 🕰️ あの頃"
                )

                st.write(
                    "😵 難しさ "
                    + star_text(
                        first[
                            "difficulty"
                        ]
                    )
                )

                st.write(
                    "💪 自信 "
                    + star_text(
                        first[
                            "confidence"
                        ]
                    )
                )

                if first.get(
                    "memo"
                ):
                    st.write(
                        f"「{first.get('memo')}」"
                    )

            with col2:
                st.markdown(
                    "#### 🌱 今"
                )

                st.write(
                    "😵 難しさ "
                    + star_text(
                        latest[
                            "difficulty"
                        ]
                    )
                )

                st.write(
                    "💪 自信 "
                    + star_text(
                        latest[
                            "confidence"
                        ]
                    )
                )

                if latest.get(
                    "memo"
                ):
                    st.write(
                        f"「{latest.get('memo')}」"
                    )

            st.success(
                "🌱 あの頃より、"
                "ちゃんと前にいる。"
            )

        if st.button(
            "🎲 別の成長を見る",
            use_container_width=True,
        ):
            alternatives = [
                skill_id
                for skill_id
                in old_ids
                if skill_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_growth_skill"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 見守り中
# =========================================================

favorites = [
    skill
    for skill in skills
    if skill.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 見守り中"
    )

    for skill in favorites:
        items = skill_records(
            data,
            skill.get("id"),
        )

        st.write(
            f"⭐ **{skill.get('title', '')}**"
        )

        st.caption(
            f"{skill.get('category', '')}"
            f" ｜ {len(items)}回記録"
            f" ｜ {growth_stage(items)}"
        )


# =========================================================
# 成長図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 成長図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "Python、筋トレ、運転……"
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
    favorite_only = (
        st.checkbox(
            "⭐ 見守り中だけ",
        )
    )

filtered_skills = []

for skill in skills:
    if (
        category_filter
        != "すべて"
        and skill.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        favorite_only
        and not skill.get(
            "favorite",
            False,
        )
    ):
        continue

    searchable = " ".join(
        [
            skill.get(
                "title",
                "",
            ),
            skill.get(
                "description",
                "",
            ),
            skill.get(
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

    filtered_skills.append(
        skill
    )

if not filtered_skills:
    st.info(
        "条件に合う成長テーマは"
        "ありません。"
    )

else:
    rows = []

    for skill in filtered_skills:
        items = skill_records(
            data,
            skill.get("id"),
        )

        if not items:
            continue

        first = items[0]
        latest = items[-1]

        rows.append(
            {
                "テーマ": skill.get(
                    "title",
                    "",
                ),
                "カテゴリー": (
                    skill.get(
                        "category",
                        "",
                    )
                ),
                "回数": len(items),
                "初回難度": (
                    star_text(
                        first[
                            "difficulty"
                        ]
                    )
                ),
                "現在難度": (
                    star_text(
                        latest[
                            "difficulty"
                        ]
                    )
                ),
                "自信変化": (
                    latest[
                        "confidence"
                    ]
                    - first[
                        "confidence"
                    ]
                ),
                "ステージ": (
                    growth_stage(
                        items
                    )
                ),
                "⭐": (
                    "⭐"
                    if skill.get(
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
    skill_options = {
        (
            f"{skill.get('title', '')}"
            f" ｜ {skill.get('category', '')}"
        ): skill.get("id")
        for skill in skills
    }

    if not skill_options:
        st.caption(
            "まだ成長テーマがありません。"
        )

    else:
        selected_label = (
            st.selectbox(
                "編集するテーマ",
                list(
                    skill_options.keys()
                ),
            )
        )

        selected_id = (
            skill_options[
                selected_label
            ]
        )

        selected = get_skill(
            data,
            selected_id,
        )

        if selected:
            st.markdown(
                "#### ✏️ テーマ編集"
            )

            edit_title = st.text_input(
                "テーマ",
                value=selected.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + selected_id
                ),
            )

            old_category = (
                selected.get(
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
                        + selected_id
                    ),
                )
            )

            edit_description = (
                st.text_area(
                    "説明",
                    value=selected.get(
                        "description",
                        "",
                    ),
                    key=(
                        "edit_description_"
                        + selected_id
                    ),
                )
            )

            if st.button(
                "💾 テーマを保存",
                key=(
                    "save_skill_"
                    + selected_id
                ),
                type="primary",
                use_container_width=True,
            ):
                if not (
                    edit_title.strip()
                ):
                    st.warning(
                        "テーマ名を入力してね。"
                    )

                else:
                    update_skill(
                        data=data,
                        skill_id=(
                            selected_id
                        ),
                        title=(
                            edit_title.strip()
                        ),
                        category=(
                            edit_category
                        ),
                        description=(
                            edit_description.strip()
                        ),
                    )

                    st.rerun()

            st.divider()

            st.markdown(
                "#### 📝 記録編集"
            )

            selected_records = (
                skill_records(
                    data,
                    selected_id,
                )
            )

            if not selected_records:
                st.caption(
                    "記録がありません。"
                )

            else:
                record_options = {}

                for index, record in enumerate(
                    selected_records,
                    start=1,
                ):
                    label = (
                        f"{index}回目 ｜ "
                        f"{format_date(record.get('date'))}"
                    )

                    record_options[
                        label
                    ] = record.get(
                        "id"
                    )

                record_label = (
                    st.selectbox(
                        "編集する記録",
                        list(
                            record_options.keys()
                        ),
                        key=(
                            "record_select_"
                            + selected_id
                        ),
                    )
                )

                record_id = (
                    record_options[
                        record_label
                    ]
                )

                record = get_record(
                    data,
                    record_id,
                )

                if record:
                    current_date = (
                        parse_date(
                            record.get(
                                "date"
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
                                + record_id
                            ),
                        )
                    )

                    c1, c2, c3 = (
                        st.columns(3)
                    )

                    with c1:
                        edit_difficulty = (
                            st.slider(
                                "難しさ",
                                1,
                                5,
                                int(
                                    record[
                                        "difficulty"
                                    ]
                                ),
                                key=(
                                    "edit_diff_"
                                    + record_id
                                ),
                            )
                        )

                    with c2:
                        edit_confidence = (
                            st.slider(
                                "自信",
                                1,
                                5,
                                int(
                                    record[
                                        "confidence"
                                    ]
                                ),
                                key=(
                                    "edit_conf_"
                                    + record_id
                                ),
                            )
                        )

                    with c3:
                        edit_fatigue = (
                            st.slider(
                                "疲労",
                                1,
                                5,
                                int(
                                    record[
                                        "fatigue"
                                    ]
                                ),
                                key=(
                                    "edit_fatigue_"
                                    + record_id
                                ),
                            )
                        )

                    edit_minutes = (
                        st.number_input(
                            "時間（分）",
                            min_value=0,
                            max_value=1440,
                            value=int(
                                record.get(
                                    "minutes",
                                    0,
                                )
                            ),
                            step=5,
                            key=(
                                "edit_minutes_"
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

                    if st.button(
                        "💾 記録を保存",
                        key=(
                            "save_record_edit_"
                            + record_id
                        ),
                        use_container_width=True,
                    ):
                        update_record(
                            data=data,
                            record_id=(
                                record_id
                            ),
                            record_date=(
                                edit_date
                            ),
                            difficulty=(
                                edit_difficulty
                            ),
                            confidence=(
                                edit_confidence
                            ),
                            fatigue=(
                                edit_fatigue
                            ),
                            minutes=(
                                edit_minutes
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

                    confirm_record_delete = (
                        st.checkbox(
                            "この記録を削除する",
                            key=(
                                "confirm_record_delete_"
                                + record_id
                            ),
                        )
                    )

                    if st.button(
                        "🗑️ 記録を削除",
                        key=(
                            "delete_record_"
                            + record_id
                        ),
                        disabled=(
                            not confirm_record_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_record(
                            data,
                            record_id,
                        )

                        st.rerun()

            st.divider()

            st.markdown(
                "#### 🗑️ テーマを完全削除"
            )

            st.warning(
                "テーマを削除すると、"
                "これまでの成長記録も"
                "すべて削除されます。"
            )

            confirm_skill_delete = (
                st.checkbox(
                    "テーマと記録を"
                    "すべて削除する",
                    key=(
                        "confirm_skill_delete_"
                        + selected_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_skill_"
                    + selected_id
                ),
                disabled=(
                    not confirm_skill_delete
                ),
                use_container_width=True,
            ):
                delete_skill(
                    data,
                    selected_id,
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
            "getting_easier_"
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
    "🌱 「できるようになった」"
    "だけが成長じゃない。"
    "前より少し楽なら、"
    "それもちゃんと前進。"
)

st.caption(
    "📈 昨日の自分には"
    "見えなかった成長を、"
    "記録なら見つけられる。"
)
