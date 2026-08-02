import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="できたログ",
    page_icon="🏆",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "achievement_data.json",
)

CATEGORIES = [
    "仕事",
    "アプリ開発",
    "学習",
    "健康",
    "運動",
    "家族",
    "家事",
    "発信",
    "人間関係",
    "メンタル",
    "趣味",
    "生活",
    "その他",
]

DIFFICULTIES = [
    "とても簡単",
    "簡単",
    "普通",
    "少し大変",
    "かなり大変",
]

DIFFICULTY_VALUES = {
    "とても簡単": 1,
    "簡単": 2,
    "普通": 3,
    "少し大変": 4,
    "かなり大変": 5,
}

DIFFICULTY_ICONS = {
    "とても簡単": "🌱",
    "簡単": "🙂",
    "普通": "✨",
    "少し大変": "💪",
    "かなり大変": "🔥",
}

ACHIEVEMENT_TYPES = [
    "小さな一歩",
    "継続できた",
    "挑戦できた",
    "完成できた",
    "乗り越えた",
    "誰かを助けた",
    "自分を大切にした",
    "その他",
]

TYPE_ICONS = {
    "小さな一歩": "👣",
    "継続できた": "🔁",
    "挑戦できた": "🚀",
    "完成できた": "🏁",
    "乗り越えた": "🌈",
    "誰かを助けた": "🤝",
    "自分を大切にした": "🌿",
    "その他": "⭐",
}


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作成する。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    """空の初期データを作成する。"""

    return {
        "achievements": []
    }


def save_data(data):
    """JSONファイルへ保存する。"""

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
    """古い保存データへ不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "achievements",
        [],
    )

    for achievement in data["achievements"]:
        achievement.setdefault(
            "id",
            create_id(),
        )

        achievement.setdefault(
            "achievement_date",
            str(date.today()),
        )

        achievement.setdefault(
            "title",
            "",
        )

        achievement.setdefault(
            "details",
            "",
        )

        achievement.setdefault(
            "category",
            "その他",
        )

        achievement.setdefault(
            "achievement_type",
            "小さな一歩",
        )

        achievement.setdefault(
            "difficulty",
            "普通",
        )

        achievement.setdefault(
            "satisfaction",
            3,
        )

        achievement.setdefault(
            "confidence",
            3,
        )

        achievement.setdefault(
            "self_praise",
            "",
        )

        achievement.setdefault(
            "next_step",
            "",
        )

        achievement.setdefault(
            "tags",
            [],
        )

        achievement.setdefault(
            "favorite",
            False,
        )

        achievement.setdefault(
            "created_at",
            "",
        )

        achievement.setdefault(
            "updated_at",
            "",
        )

    return data


def load_data():
    """JSONファイルから読み込む。"""

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
            if os.path.exists(DATA_FILE):
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
    """日付文字列をdate型へ変換する。"""

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
    """日付を日本語形式で表示する。"""

    parsed_date = parse_date(
        date_text
    )

    if not parsed_date:
        return "日付不明"

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
        parsed_date.weekday()
    ]

    return parsed_date.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_achievement_by_id(
    data,
    achievement_id,
):
    """IDから達成記録を取得する。"""

    for achievement in data["achievements"]:
        if (
            achievement.get("id")
            == achievement_id
        ):
            return achievement

    return None


def get_achievements_by_date(
    achievements,
    target_date,
):
    """指定日の達成記録を取得する。"""

    target_text = str(
        target_date
    )

    return [
        achievement
        for achievement in achievements
        if achievement.get(
            "achievement_date"
        )
        == target_text
    ]


def calculate_streak(
    achievements,
):
    """今日または昨日から続く記録日数を計算する。"""

    recorded_dates = {
        parse_date(
            achievement.get(
                "achievement_date",
                "",
            )
        )
        for achievement in achievements
    }

    recorded_dates.discard(
        None
    )

    if not recorded_dates:
        return 0

    current_date = date.today()

    if current_date not in recorded_dates:
        current_date -= timedelta(
            days=1
        )

        if current_date not in recorded_dates:
            return 0

    streak = 0

    while current_date in recorded_dates:
        streak += 1

        current_date -= timedelta(
            days=1
        )

    return streak


def average_value(
    achievements,
    key,
):
    """指定した数値項目の平均を計算する。"""

    values = [
        int(
            achievement.get(
                key,
                0,
            )
        )
        for achievement in achievements
        if int(
            achievement.get(
                key,
                0,
            )
        )
        > 0
    ]

    if not values:
        return 0

    return (
        sum(values)
        / len(values)
    )


def get_all_tags(
    achievements,
):
    """登録済みタグを取得する。"""

    tags = set()

    for achievement in achievements:
        for tag in achievement.get(
            "tags",
            [],
        ):
            cleaned_tag = tag.strip()

            if cleaned_tag:
                tags.add(
                    cleaned_tag
                )

    return sorted(tags)


def difficult_achievement_count(
    achievements,
):
    """難易度の高い達成数を返す。"""

    return len(
        [
            achievement
            for achievement in achievements
            if achievement.get(
                "difficulty"
            )
            in [
                "少し大変",
                "かなり大変",
            ]
        ]
    )


def calculate_confidence_meter(
    achievements,
):
    """最近30日間の自信メーターを計算する。"""

    start_date = (
        date.today()
        - timedelta(
            days=29
        )
    )

    recent_achievements = [
        achievement
        for achievement in achievements
        if (
            parse_date(
                achievement.get(
                    "achievement_date",
                    "",
                )
            )
            and start_date
            <= parse_date(
                achievement.get(
                    "achievement_date",
                    "",
                )
            )
            <= date.today()
        )
    ]

    if not recent_achievements:
        return 0

    average_confidence = (
        average_value(
            recent_achievements,
            "confidence",
        )
    )

    amount_bonus = min(
        len(recent_achievements)
        * 2,
        30,
    )

    meter = (
        average_confidence
        / 5
        * 70
        + amount_bonus
    )

    return min(
        meter,
        100,
    )


# =========================================================
# データ操作
# =========================================================

def add_achievement(
    data,
    values,
):
    """新しい達成記録を追加する。"""

    achievement = {
        "id": create_id(),
        "achievement_date": (
            values[
                "achievement_date"
            ]
        ),
        "title": values["title"],
        "details": values["details"],
        "category": values["category"],
        "achievement_type": (
            values[
                "achievement_type"
            ]
        ),
        "difficulty": (
            values["difficulty"]
        ),
        "satisfaction": int(
            values["satisfaction"]
        ),
        "confidence": int(
            values["confidence"]
        ),
        "self_praise": (
            values["self_praise"]
        ),
        "next_step": (
            values["next_step"]
        ),
        "tags": values["tags"],
        "favorite": False,
        "created_at": now_text(),
        "updated_at": "",
    }

    data[
        "achievements"
    ].append(
        achievement
    )

    save_data(data)


def update_achievement(
    data,
    achievement_id,
    values,
):
    """達成記録を更新する。"""

    achievement = (
        get_achievement_by_id(
            data,
            achievement_id,
        )
    )

    if not achievement:
        return

    for key, value in values.items():
        achievement[key] = value

    achievement["satisfaction"] = int(
        achievement.get(
            "satisfaction",
            3,
        )
    )

    achievement["confidence"] = int(
        achievement.get(
            "confidence",
            3,
        )
    )

    achievement["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_achievement(
    data,
    achievement_id,
):
    """達成記録を削除する。"""

    data["achievements"] = [
        achievement
        for achievement in data[
            "achievements"
        ]
        if achievement.get("id")
        != achievement_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    achievement_id,
):
    """お気に入り状態を切り替える。"""

    achievement = (
        get_achievement_by_id(
            data,
            achievement_id,
        )
    )

    if not achievement:
        return

    achievement["favorite"] = not bool(
        achievement.get(
            "favorite",
            False,
        )
    )

    achievement["updated_at"] = (
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
        background: rgba(255, 185, 50, 0.09);
        border: 1px solid rgba(255, 185, 50, 0.20);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(255, 185, 50, 0.22);
        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 55, 0.20),
                rgba(255, 120, 150, 0.11)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }

    .confidence-meter {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

achievements = data[
    "achievements"
]

all_tags = get_all_tags(
    achievements
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🏆 できたログ</h1>
        <p>
            今日できたことを残して、
            小さな自信と成長を積み上げるアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

today_achievements = (
    get_achievements_by_date(
        achievements,
        date.today(),
    )
)

this_month_achievements = [
    achievement
    for achievement in achievements
    if (
        parse_date(
            achievement.get(
                "achievement_date",
                "",
            )
        )
        and parse_date(
            achievement.get(
                "achievement_date",
                "",
            )
        ).year
        == date.today().year
        and parse_date(
            achievement.get(
                "achievement_date",
                "",
            )
        ).month
        == date.today().month
    )
]

streak_count = calculate_streak(
    achievements
)

monthly_satisfaction = average_value(
    this_month_achievements,
    "satisfaction",
)

confidence_meter = (
    calculate_confidence_meter(
        achievements
    )
)

category_counter = Counter(
    achievement.get(
        "category",
        "その他",
    )
    for achievement in achievements
)

most_common_category = (
    category_counter.most_common(
        1
    )[0][0]
    if category_counter
    else "なし"
)

metric_row1 = st.columns(4)

metric_row1[0].metric(
    "総達成数",
    f"{len(achievements)}件",
)

metric_row1[1].metric(
    "今日のできた",
    f"{len(today_achievements)}件",
)

metric_row1[2].metric(
    "今月のできた",
    f"{len(this_month_achievements)}件",
)

metric_row1[3].metric(
    "連続記録",
    f"{streak_count}日",
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "今月の平均達成感",
    (
        f"{monthly_satisfaction:.1f}/5"
        if monthly_satisfaction > 0
        else "未記録"
    ),
)

metric_row2[1].metric(
    "最多カテゴリー",
    most_common_category,
)

metric_row2[2].metric(
    "難しい達成",
    f"{difficult_achievement_count(achievements)}件",
)

metric_row2[3].metric(
    "自信メーター",
    f"{confidence_meter:.0f}/100",
)


st.subheader(
    "🌟 現在の自信メーター"
)

st.progress(
    confidence_meter / 100
)

if confidence_meter >= 80:
    st.success(
        "かなり良い積み重ねができています！"
    )

elif confidence_meter >= 50:
    st.info(
        "小さな達成が、着実に自信へ変わっています。"
    )

elif achievements:
    st.warning(
        "小さなことでも大丈夫。今日のできたを一つ残してみよう。"
    )

else:
    st.info(
        "最初のできたことを記録してみましょう。"
    )


# =========================================================
# 今日のできたこと
# =========================================================

st.divider()

st.subheader(
    "✅ 今日のできたこと"
)

if not today_achievements:
    st.info(
        "今日のできたことはまだ登録されていません。"
    )

else:
    today_achievements = sorted(
        today_achievements,
        key=lambda achievement: (
            achievement.get(
                "created_at",
                "",
            )
        ),
    )

    for achievement in today_achievements:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### ✅ "
                f"{achievement.get('title', '')}"
            )

            st.caption(
                f"{TYPE_ICONS.get(achievement.get('achievement_type', ''), '')} "
                f"{achievement.get('achievement_type', '')} ／ "
                f"{achievement.get('category', '')}"
            )

            if achievement.get(
                "self_praise",
                "",
            ):
                st.success(
                    "今日の自分へ\n\n"
                    + achievement.get(
                        "self_praise",
                        "",
                    )
                )


# =========================================================
# 過去の達成をランダム表示
# =========================================================

if achievements:
    st.divider()

    st.subheader(
        "🎲 以前こんなこともできました"
    )

    if (
        "random_achievement_id"
        not in st.session_state
    ):
        st.session_state[
            "random_achievement_id"
        ] = random.choice(
            achievements
        )["id"]

    random_achievement = (
        get_achievement_by_id(
            data,
            st.session_state[
                "random_achievement_id"
            ],
        )
    )

    if random_achievement:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 🏆 "
                f"{random_achievement.get('title', '')}"
            )

            st.caption(
                format_date(
                    random_achievement.get(
                        "achievement_date",
                        "",
                    )
                )
            )

            if random_achievement.get(
                "details",
                "",
            ):
                st.write(
                    random_achievement.get(
                        "details",
                        "",
                    )
                )

            if random_achievement.get(
                "self_praise",
                "",
            ):
                st.success(
                    random_achievement.get(
                        "self_praise",
                        "",
                    )
                )

    if st.button(
        "🔄 別の達成を表示"
    ):
        st.session_state[
            "random_achievement_id"
        ] = random.choice(
            achievements
        )["id"]

        st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    calendar_tab,
    favorite_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ できたことを登録",
        "📚 達成ログ",
        "📅 月別表示",
        "⭐ お気に入り",
        "📈 成長分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 登録
# =========================================================

with add_tab:
    st.header(
        "➕ 今日のできたことを登録"
    )

    with st.form(
        "add_achievement_form",
        clear_on_submit=True,
    ):
        form_column1, form_column2 = (
            st.columns(2)
        )

        with form_column1:
            achievement_date_input = (
                st.date_input(
                    "達成日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

            title = st.text_input(
                "できたこと",
                placeholder=(
                    "例：新しいアプリのコードを完成させた"
                ),
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            achievement_type = (
                st.selectbox(
                    "達成の種類",
                    ACHIEVEMENT_TYPES,
                )
            )

        with form_column2:
            difficulty = (
                st.select_slider(
                    "難易度",
                    options=DIFFICULTIES,
                    value="普通",
                )
            )

            satisfaction = st.slider(
                "達成感",
                min_value=1,
                max_value=5,
                value=3,
            )

            confidence = st.slider(
                "自信につながった度",
                min_value=1,
                max_value=5,
                value=3,
            )

        details = st.text_area(
            "どんなことを頑張った？",
            placeholder=(
                "取り組んだことや、工夫したことを書きます。"
            ),
            height=110,
        )

        self_praise = st.text_area(
            "自分を褒める言葉",
            placeholder=(
                "例：途中で投げ出さず、最後まで作れてえらい！"
            ),
            height=100,
        )

        next_step = st.text_area(
            "次にやってみたいこと",
            placeholder=(
                "今回の達成を次へつなげる小さな一歩"
            ),
            height=90,
        )

        selected_tags = st.multiselect(
            "タグ",
            all_tags,
        )

        custom_tags_text = st.text_input(
            "新しいタグ",
            placeholder=(
                "複数ある場合はカンマ区切り"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🏆 できたことを記録",
                use_container_width=True,
            )
        )

        if submitted:
            cleaned_title = (
                title.strip()
            )

            custom_tags = [
                tag.strip()
                for tag in custom_tags_text.split(
                    ","
                )
                if tag.strip()
            ]

            final_tags = list(
                dict.fromkeys(
                    selected_tags
                    + custom_tags
                )
            )

            if not cleaned_title:
                st.error(
                    "できたことを入力してください。"
                )

            else:
                add_achievement(
                    data,
                    {
                        "achievement_date": str(
                            achievement_date_input
                        ),
                        "title": cleaned_title,
                        "details": details.strip(),
                        "category": category,
                        "achievement_type": (
                            achievement_type
                        ),
                        "difficulty": difficulty,
                        "satisfaction": (
                            satisfaction
                        ),
                        "confidence": confidence,
                        "self_praise": (
                            self_praise.strip()
                        ),
                        "next_step": (
                            next_step.strip()
                        ),
                        "tags": final_tags,
                    },
                )

                st.success(
                    "できたことを記録しました！"
                )

                st.balloons()
                st.rerun()

    st.divider()

    st.subheader(
        "🌱 小さなことも立派な達成"
    )

    example_columns = st.columns(3)

    example_columns[0].info(
        "・朝起きられた\n\n"
        "・着替えられた\n\n"
        "・メールを1通返した"
    )

    example_columns[1].info(
        "・5分だけ作業した\n\n"
        "・散歩に出た\n\n"
        "・本を1ページ読んだ"
    )

    example_columns[2].info(
        "・家族と話せた\n\n"
        "・しっかり休めた\n\n"
        "・助けを求められた"
    )


# =========================================================
# 達成ログ
# =========================================================

with list_tab:
    st.header(
        "📚 達成ログ"
    )

    if not achievements:
        st.info(
            "できたことはまだ登録されていません。"
        )

    else:
        filter_column1, filter_column2, filter_column3 = (
            st.columns(3)
        )

        with filter_column1:
            keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "できたこと・詳細・褒め言葉"
                ),
            )

        with filter_column2:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES,
                )
            )

        with filter_column3:
            type_filter = st.selectbox(
                "達成の種類",
                [
                    "すべて"
                ]
                + ACHIEVEMENT_TYPES,
            )

        difficulty_filter = (
            st.multiselect(
                "難易度",
                DIFFICULTIES,
                default=DIFFICULTIES,
            )
        )

        tag_filter = st.selectbox(
            "タグ",
            [
                "すべて"
            ]
            + all_tags,
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "新しい順",
                "古い順",
                "達成感が高い順",
                "自信が高い順",
                "難易度が高い順",
            ],
        )

        filtered_achievements = list(
            achievements
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_achievements = [
                achievement
                for achievement
                in filtered_achievements
                if (
                    search_word
                    in achievement.get(
                        "title",
                        "",
                    ).lower()
                    or search_word
                    in achievement.get(
                        "details",
                        "",
                    ).lower()
                    or search_word
                    in achievement.get(
                        "self_praise",
                        "",
                    ).lower()
                    or search_word
                    in achievement.get(
                        "next_step",
                        "",
                    ).lower()
                )
            ]

        if category_filter != "すべて":
            filtered_achievements = [
                achievement
                for achievement
                in filtered_achievements
                if achievement.get(
                    "category"
                )
                == category_filter
            ]

        if type_filter != "すべて":
            filtered_achievements = [
                achievement
                for achievement
                in filtered_achievements
                if achievement.get(
                    "achievement_type"
                )
                == type_filter
            ]

        filtered_achievements = [
            achievement
            for achievement
            in filtered_achievements
            if achievement.get(
                "difficulty",
                "普通",
            )
            in difficulty_filter
        ]

        if tag_filter != "すべて":
            filtered_achievements = [
                achievement
                for achievement
                in filtered_achievements
                if tag_filter
                in achievement.get(
                    "tags",
                    [],
                )
            ]

        if sort_option == "新しい順":
            filtered_achievements.sort(
                key=lambda achievement: (
                    achievement.get(
                        "achievement_date",
                        "",
                    ),
                    achievement.get(
                        "created_at",
                        "",
                    ),
                ),
                reverse=True,
            )

        elif sort_option == "古い順":
            filtered_achievements.sort(
                key=lambda achievement: (
                    achievement.get(
                        "achievement_date",
                        "",
                    ),
                    achievement.get(
                        "created_at",
                        "",
                    ),
                )
            )

        elif sort_option == "達成感が高い順":
            filtered_achievements.sort(
                key=lambda achievement: int(
                    achievement.get(
                        "satisfaction",
                        0,
                    )
                ),
                reverse=True,
            )

        elif sort_option == "自信が高い順":
            filtered_achievements.sort(
                key=lambda achievement: int(
                    achievement.get(
                        "confidence",
                        0,
                    )
                ),
                reverse=True,
            )

        elif sort_option == "難易度が高い順":
            filtered_achievements.sort(
                key=lambda achievement: (
                    DIFFICULTY_VALUES.get(
                        achievement.get(
                            "difficulty",
                            "普通",
                        ),
                        3,
                    )
                ),
                reverse=True,
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_achievements)}件**"
        )

        for achievement in filtered_achievements:
            achievement_id = achievement[
                "id"
            ]

            with st.container(
                border=True,
            ):
                title_column, score_column = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with title_column:
                    favorite_icon = (
                        "⭐ "
                        if achievement.get(
                            "favorite",
                            False,
                        )
                        else ""
                    )

                    st.markdown(
                        f"### {favorite_icon}"
                        f"{achievement.get('title', '')}"
                    )

                    st.caption(
                        f"{format_date(achievement.get('achievement_date', ''))} ／ "
                        f"{TYPE_ICONS.get(achievement.get('achievement_type', ''), '')} "
                        f"{achievement.get('achievement_type', '')} ／ "
                        f"{achievement.get('category', '')}"
                    )

                with score_column:
                    st.metric(
                        "達成感",
                        f"{achievement.get('satisfaction', 3)}/5",
                    )

                detail_columns = st.columns(3)

                detail_columns[0].metric(
                    "難易度",
                    (
                        f"{DIFFICULTY_ICONS.get(achievement.get('difficulty', ''), '')} "
                        f"{achievement.get('difficulty', '')}"
                    ),
                )

                detail_columns[1].metric(
                    "自信",
                    f"{achievement.get('confidence', 3)}/5",
                )

                detail_columns[2].metric(
                    "お気に入り",
                    (
                        "登録済み"
                        if achievement.get(
                            "favorite",
                            False,
                        )
                        else "未登録"
                    ),
                )

                if achievement.get(
                    "details",
                    "",
                ):
                    st.write(
                        achievement.get(
                            "details",
                            "",
                        )
                    )

                if achievement.get(
                    "self_praise",
                    "",
                ):
                    st.success(
                        "👏 自分を褒める言葉\n\n"
                        + achievement.get(
                            "self_praise",
                            "",
                        )
                    )

                if achievement.get(
                    "next_step",
                    "",
                ):
                    st.info(
                        "➡️ 次の一歩\n\n"
                        + achievement.get(
                            "next_step",
                            "",
                        )
                    )

                if achievement.get(
                    "tags",
                    [],
                ):
                    st.caption(
                        "🏷️ "
                        + " / ".join(
                            achievement.get(
                                "tags",
                                [],
                            )
                        )
                    )

                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if achievement.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り登録"
                    ),
                    key=(
                        f"favorite_"
                        f"{achievement_id}"
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        achievement_id,
                    )

                    st.rerun()

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_date = st.date_input(
                        "達成日",
                        value=(
                            parse_date(
                                achievement.get(
                                    "achievement_date",
                                    "",
                                )
                            )
                            or date.today()
                        ),
                        max_value=date.today(),
                        key=(
                            f"edit_date_"
                            f"{achievement_id}"
                        ),
                    )

                    edit_title = st.text_input(
                        "できたこと",
                        value=achievement.get(
                            "title",
                            "",
                        ),
                        key=(
                            f"edit_title_"
                            f"{achievement_id}"
                        ),
                    )

                    edit_column1, edit_column2 = (
                        st.columns(2)
                    )

                    with edit_column1:
                        current_category = (
                            achievement.get(
                                "category",
                                "その他",
                            )
                        )

                        edit_category = (
                            st.selectbox(
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
                                    f"{achievement_id}"
                                ),
                            )
                        )

                        current_type = (
                            achievement.get(
                                "achievement_type",
                                "小さな一歩",
                            )
                        )

                        edit_type = st.selectbox(
                            "達成の種類",
                            ACHIEVEMENT_TYPES,
                            index=(
                                ACHIEVEMENT_TYPES.index(
                                    current_type
                                )
                                if current_type
                                in ACHIEVEMENT_TYPES
                                else 0
                            ),
                            key=(
                                f"edit_type_"
                                f"{achievement_id}"
                            ),
                        )

                        current_difficulty = (
                            achievement.get(
                                "difficulty",
                                "普通",
                            )
                        )

                        edit_difficulty = (
                            st.selectbox(
                                "難易度",
                                DIFFICULTIES,
                                index=(
                                    DIFFICULTIES.index(
                                        current_difficulty
                                    )
                                    if current_difficulty
                                    in DIFFICULTIES
                                    else 2
                                ),
                                key=(
                                    f"edit_difficulty_"
                                    f"{achievement_id}"
                                ),
                            )
                        )

                    with edit_column2:
                        edit_satisfaction = (
                            st.slider(
                                "達成感",
                                min_value=1,
                                max_value=5,
                                value=int(
                                    achievement.get(
                                        "satisfaction",
                                        3,
                                    )
                                ),
                                key=(
                                    f"edit_satisfaction_"
                                    f"{achievement_id}"
                                ),
                            )
                        )

                        edit_confidence = (
                            st.slider(
                                "自信につながった度",
                                min_value=1,
                                max_value=5,
                                value=int(
                                    achievement.get(
                                        "confidence",
                                        3,
                                    )
                                ),
                                key=(
                                    f"edit_confidence_"
                                    f"{achievement_id}"
                                ),
                            )
                        )

                    edit_details = st.text_area(
                        "詳細",
                        value=achievement.get(
                            "details",
                            "",
                        ),
                        key=(
                            f"edit_details_"
                            f"{achievement_id}"
                        ),
                    )

                    edit_self_praise = (
                        st.text_area(
                            "自分を褒める言葉",
                            value=achievement.get(
                                "self_praise",
                                "",
                            ),
                            key=(
                                f"edit_praise_"
                                f"{achievement_id}"
                            ),
                        )
                    )

                    edit_next_step = (
                        st.text_area(
                            "次の一歩",
                            value=achievement.get(
                                "next_step",
                                "",
                            ),
                            key=(
                                f"edit_next_"
                                f"{achievement_id}"
                            ),
                        )
                    )

                    edit_tags = st.text_input(
                        "タグ",
                        value=", ".join(
                            achievement.get(
                                "tags",
                                [],
                            )
                        ),
                        key=(
                            f"edit_tags_"
                            f"{achievement_id}"
                        ),
                        help=(
                            "複数ある場合はカンマ区切り"
                        ),
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_achievement_"
                            f"{achievement_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_title.strip():
                            st.error(
                                "できたことを入力してください。"
                            )

                        else:
                            final_edit_tags = [
                                tag.strip()
                                for tag in edit_tags.split(
                                    ","
                                )
                                if tag.strip()
                            ]

                            update_achievement(
                                data,
                                achievement_id,
                                {
                                    "achievement_date": str(
                                        edit_date
                                    ),
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "achievement_type": (
                                        edit_type
                                    ),
                                    "difficulty": (
                                        edit_difficulty
                                    ),
                                    "satisfaction": (
                                        edit_satisfaction
                                    ),
                                    "confidence": (
                                        edit_confidence
                                    ),
                                    "details": (
                                        edit_details.strip()
                                    ),
                                    "self_praise": (
                                        edit_self_praise.strip()
                                    ),
                                    "next_step": (
                                        edit_next_step.strip()
                                    ),
                                    "tags": list(
                                        dict.fromkeys(
                                            final_edit_tags
                                        )
                                    ),
                                },
                            )

                            st.success(
                                "達成記録を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 削除"
                ):
                    confirm_delete = st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_"
                            f"{achievement_id}"
                        ),
                    )

                    if st.button(
                        "この達成記録を削除",
                        key=(
                            f"delete_achievement_"
                            f"{achievement_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_achievement(
                            data,
                            achievement_id,
                        )

                        st.rerun()


# =========================================================
# 月別表示
# =========================================================

with calendar_tab:
    st.header(
        "📅 月別のできたこと"
    )

    if not achievements:
        st.info(
            "表示できる達成記録がありません。"
        )

    else:
        available_months = sorted(
            {
                (
                    parse_date(
                        achievement.get(
                            "achievement_date",
                            "",
                        )
                    ).year,
                    parse_date(
                        achievement.get(
                            "achievement_date",
                            "",
                        )
                    ).month,
                )
                for achievement in achievements
                if parse_date(
                    achievement.get(
                        "achievement_date",
                        "",
                    )
                )
            },
            reverse=True,
        )

        month_options = {
            f"{year}年{month}月": (
                year,
                month,
            )
            for year, month in available_months
        }

        selected_month_label = (
            st.selectbox(
                "表示する月",
                list(
                    month_options.keys()
                ),
            )
        )

        selected_year, selected_month = (
            month_options[
                selected_month_label
            ]
        )

        monthly_achievements = [
            achievement
            for achievement in achievements
            if (
                parse_date(
                    achievement.get(
                        "achievement_date",
                        "",
                    )
                )
                and parse_date(
                    achievement.get(
                        "achievement_date",
                        "",
                    )
                ).year
                == selected_year
                and parse_date(
                    achievement.get(
                        "achievement_date",
                        "",
                    )
                ).month
                == selected_month
            )
        ]

        monthly_achievements.sort(
            key=lambda achievement: (
                achievement.get(
                    "achievement_date",
                    "",
                ),
                achievement.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        summary_columns = st.columns(4)

        summary_columns[0].metric(
            "達成数",
            f"{len(monthly_achievements)}件",
        )

        summary_columns[1].metric(
            "記録日数",
            len(
                {
                    achievement.get(
                        "achievement_date"
                    )
                    for achievement
                    in monthly_achievements
                }
            ),
        )

        summary_columns[2].metric(
            "平均達成感",
            f"{average_value(monthly_achievements, 'satisfaction'):.1f}/5",
        )

        summary_columns[3].metric(
            "平均自信",
            f"{average_value(monthly_achievements, 'confidence'):.1f}/5",
        )

        date_groups = {}

        for achievement in monthly_achievements:
            achievement_date = achievement.get(
                "achievement_date",
                "",
            )

            date_groups.setdefault(
                achievement_date,
                [],
            ).append(
                achievement
            )

        for achievement_date, day_items in date_groups.items():
            st.subheader(
                format_date(
                    achievement_date
                )
            )

            for achievement in day_items:
                with st.container(
                    border=True,
                ):
                    st.markdown(
                        f"**✅ "
                        f"{achievement.get('title', '')}**"
                    )

                    st.caption(
                        f"{achievement.get('category', '')} ／ "
                        f"達成感 "
                        f"{achievement.get('satisfaction', 3)}/5"
                    )

                    if achievement.get(
                        "self_praise",
                        "",
                    ):
                        st.success(
                            achievement.get(
                                "self_praise",
                                "",
                            )
                        )


# =========================================================
# お気に入り
# =========================================================

with favorite_tab:
    st.header(
        "⭐ お気に入りの達成"
    )

    favorite_achievements = [
        achievement
        for achievement in achievements
        if achievement.get(
            "favorite",
            False,
        )
    ]

    if not favorite_achievements:
        st.info(
            "お気に入りに登録された達成はありません。"
        )

    else:
        favorite_achievements.sort(
            key=lambda achievement: (
                achievement.get(
                    "achievement_date",
                    "",
                )
            ),
            reverse=True,
        )

        for achievement in favorite_achievements:
            with st.container(
                border=True,
            ):
                st.markdown(
                    f"### ⭐ "
                    f"{achievement.get('title', '')}"
                )

                st.caption(
                    format_date(
                        achievement.get(
                            "achievement_date",
                            "",
                        )
                    )
                )

                if achievement.get(
                    "details",
                    "",
                ):
                    st.write(
                        achievement.get(
                            "details",
                            "",
                        )
                    )

                if achievement.get(
                    "self_praise",
                    "",
                ):
                    st.success(
                        achievement.get(
                            "self_praise",
                            "",
                        )
                    )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 成長分析"
    )

    if not achievements:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for achievement in achievements:
            achievement_date = parse_date(
                achievement.get(
                    "achievement_date",
                    "",
                )
            )

            analysis_rows.append(
                {
                    "日付": achievement_date,
                    "できたこと": (
                        achievement.get(
                            "title",
                            "",
                        )
                    ),
                    "カテゴリー": (
                        achievement.get(
                            "category",
                            "",
                        )
                    ),
                    "達成の種類": (
                        achievement.get(
                            "achievement_type",
                            "",
                        )
                    ),
                    "難易度": (
                        achievement.get(
                            "difficulty",
                            "",
                        )
                    ),
                    "難易度数値": (
                        DIFFICULTY_VALUES.get(
                            achievement.get(
                                "difficulty",
                                "普通",
                            ),
                            3,
                        )
                    ),
                    "達成感": int(
                        achievement.get(
                            "satisfaction",
                            3,
                        )
                    ),
                    "自信": int(
                        achievement.get(
                            "confidence",
                            3,
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "カテゴリー別達成数"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "達成数"
                }
            )
            .sort_values(
                "達成数",
                ascending=False,
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["達成数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "達成の種類別"
        )

        type_summary = (
            analysis_df.groupby(
                "達成の種類",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "達成数"
                }
            )
            .sort_values(
                "達成数",
                ascending=False,
            )
        )

        st.bar_chart(
            type_summary.set_index(
                "達成の種類"
            )[["達成数"]]
        )

        st.dataframe(
            type_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "月別達成数"
        )

        monthly_df = analysis_df.dropna(
            subset=[
                "日付"
            ]
        ).copy()

        monthly_df["月"] = (
            monthly_df["日付"].apply(
                lambda value: value.strftime(
                    "%Y-%m"
                )
            )
        )

        monthly_summary = (
            monthly_df.groupby(
                "月",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "達成数"
                }
            )
            .sort_values(
                "月"
            )
        )

        st.line_chart(
            monthly_summary.set_index(
                "月"
            )[["達成数"]]
        )

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "達成感と自信の推移"
        )

        score_df = (
            analysis_df.dropna(
                subset=[
                    "日付"
                ]
            )
            .sort_values(
                "日付"
            )
            .set_index(
                "日付"
            )[
                [
                    "達成感",
                    "自信",
                ]
            ]
        )

        st.line_chart(
            score_df
        )

        st.divider()

        st.subheader(
            "難易度別達成数"
        )

        difficulty_summary = (
            analysis_df.groupby(
                [
                    "難易度",
                    "難易度数値",
                ],
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "達成数"
                }
            )
            .sort_values(
                "難易度数値"
            )
        )

        st.bar_chart(
            difficulty_summary.set_index(
                "難易度"
            )[["達成数"]]
        )

        st.dataframe(
            difficulty_summary[
                [
                    "難易度",
                    "達成数",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "自信につながった達成"
        )

        confidence_ranking = (
            analysis_df.sort_values(
                [
                    "自信",
                    "達成感",
                ],
                ascending=False,
            )[
                [
                    "できたこと",
                    "カテゴリー",
                    "自信",
                    "達成感",
                    "難易度",
                ]
            ]
        )

        st.dataframe(
            confidence_ranking,
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
            f"achievement_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = st.file_uploader(
        "バックアップJSONを選択",
        type=[
            "json"
        ],
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
                or "achievements"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "achievements"
                    ],
                    list,
                )
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
        "登録した達成記録がすべて削除されます。"
    )

    confirm_delete_all = st.checkbox(
        "全データ削除を確認しました"
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
    "小さな『できた』も、積み重なれば大きな自信になる。🏆"
)
