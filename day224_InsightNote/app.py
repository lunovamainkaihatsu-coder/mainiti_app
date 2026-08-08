import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日の気づきノート",
    page_icon="💡",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "insight_data.json",
)

CATEGORIES = [
    "仕事",
    "アプリ開発",
    "AI",
    "学習",
    "読書",
    "健康",
    "運動",
    "お金",
    "家族",
    "人間関係",
    "メンタル",
    "生活",
    "趣味",
    "その他",
]

SOURCES = [
    "仕事中",
    "アプリ開発中",
    "読書",
    "動画",
    "SNS",
    "会話",
    "失敗",
    "成功",
    "散歩",
    "運動",
    "家族との時間",
    "ふと思いついた",
    "その他",
]

PRACTICE_STATUSES = [
    "まだ",
    "実践予定",
    "実践中",
    "実践済み",
    "保留",
]

PRACTICE_ICONS = {
    "まだ": "⚪",
    "実践予定": "📅",
    "実践中": "🔄",
    "実践済み": "✅",
    "保留": "⏸️",
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
    """空データを返す。"""

    return {
        "insights": []
    }


def save_data(data):
    """JSONへ保存する。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def normalize_data(data):
    """古いデータに不足項目を補う。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "insights",
        []
    )

    for insight in data["insights"]:
        insight.setdefault(
            "id",
            create_id()
        )

        insight.setdefault(
            "insight_date",
            str(date.today())
        )

        insight.setdefault(
            "title",
            ""
        )

        insight.setdefault(
            "trigger",
            ""
        )

        insight.setdefault(
            "source",
            "その他"
        )

        insight.setdefault(
            "category",
            "その他"
        )

        insight.setdefault(
            "importance",
            3
        )

        insight.setdefault(
            "meaning",
            ""
        )

        insight.setdefault(
            "action",
            ""
        )

        insight.setdefault(
            "practice_status",
            "まだ"
        )

        insight.setdefault(
            "practice_result",
            ""
        )

        insight.setdefault(
            "practice_learning",
            ""
        )

        insight.setdefault(
            "favorite",
            False
        )

        insight.setdefault(
            "tags",
            []
        )

        insight.setdefault(
            "memo",
            ""
        )

        insight.setdefault(
            "created_at",
            ""
        )

        insight.setdefault(
            "updated_at",
            ""
        )

    return data


def load_data():
    """JSONから読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
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
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        broken_file = DATA_FILE + ".broken"

        try:
            if os.path.exists(
                DATA_FILE
            ):
                os.replace(
                    DATA_FILE,
                    broken_file
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
    """文字列をdate型へ変換する。"""

    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except (
        TypeError,
        ValueError
    ):
        return None


def format_date(date_text):
    """日本語形式の日付表示。"""

    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "未設定"

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
        parsed.weekday()
    ]

    return parsed.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_insight_by_id(
    data,
    insight_id
):
    """IDから気づきを取得する。"""

    for insight in data[
        "insights"
    ]:
        if insight.get(
            "id"
        ) == insight_id:
            return insight

    return None


def get_all_tags(
    insights
):
    """すべてのタグを取得する。"""

    tags = set()

    for insight in insights:
        for tag in insight.get(
            "tags",
            []
        ):
            cleaned = tag.strip()

            if cleaned:
                tags.add(
                    cleaned
                )

    return sorted(
        tags
    )


def practice_rate(
    insights
):
    """実践率を計算する。"""

    actionable = [
        insight
        for insight in insights
        if insight.get(
            "action",
            ""
        ).strip()
    ]

    if not actionable:
        return 0

    practiced = [
        insight
        for insight in actionable
        if insight.get(
            "practice_status"
        ) == "実践済み"
    ]

    return (
        len(practiced)
        / len(actionable)
        * 100
    )


def average_importance(
    insights
):
    """平均重要度を返す。"""

    if not insights:
        return 0

    values = [
        int(
            insight.get(
                "importance",
                0
            )
        )
        for insight in insights
    ]

    return (
        sum(values)
        / len(values)
    )


# =========================================================
# データ操作
# =========================================================

def add_insight(
    data,
    values
):
    """気づきを追加する。"""

    insight = {
        "id": create_id(),
        "insight_date": (
            values["insight_date"]
        ),
        "title": values["title"],
        "trigger": values["trigger"],
        "source": values["source"],
        "category": values["category"],
        "importance": int(
            values["importance"]
        ),
        "meaning": values["meaning"],
        "action": values["action"],
        "practice_status": (
            values["practice_status"]
        ),
        "practice_result": "",
        "practice_learning": "",
        "favorite": False,
        "tags": values["tags"],
        "memo": values["memo"],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["insights"].append(
        insight
    )

    save_data(data)


def update_insight(
    data,
    insight_id,
    values
):
    """気づきを更新する。"""

    insight = get_insight_by_id(
        data,
        insight_id
    )

    if not insight:
        return

    for key, value in values.items():
        insight[key] = value

    insight["importance"] = int(
        insight.get(
            "importance",
            3
        )
    )

    insight["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_insight(
    data,
    insight_id
):
    """気づきを削除する。"""

    data["insights"] = [
        insight
        for insight in data[
            "insights"
        ]
        if insight.get(
            "id"
        ) != insight_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    insight_id
):
    """お気に入りを切り替える。"""

    insight = get_insight_by_id(
        data,
        insight_id
    )

    if not insight:
        return

    insight["favorite"] = not bool(
        insight.get(
            "favorite",
            False
        )
    )

    insight["updated_at"] = (
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
        background: rgba(255, 190, 50, 0.08);
        border: 1px solid rgba(255, 190, 50, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(255, 190, 50, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 50, 0.18),
                rgba(100, 180, 255, 0.11)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 読み込み
# =========================================================

data = load_data()

insights = data[
    "insights"
]

all_tags = get_all_tags(
    insights
)

today_text = str(
    date.today()
)

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>💡 今日の気づきノート</h1>
        <p>
            日常の小さな気づきを、
            学びと行動につなげるためのノート
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ダッシュボード
# =========================================================

today_insights = [
    insight
    for insight in insights
    if insight.get(
        "insight_date"
    ) == today_text
]

monthly_insights = [
    insight
    for insight in insights
    if insight.get(
        "insight_date",
        ""
    ).startswith(
        current_month
    )
]

practiced_insights = [
    insight
    for insight in insights
    if insight.get(
        "practice_status"
    ) == "実践済み"
]

favorite_insights = [
    insight
    for insight in insights
    if insight.get(
        "favorite",
        False
    )
]

category_counter = Counter(
    insight.get(
        "category",
        "その他"
    )
    for insight in insights
)

top_category = (
    category_counter.most_common(
        1
    )[0][0]
    if category_counter
    else "なし"
)


metric_row1 = st.columns(4)

metric_row1[0].metric(
    "総気づき数",
    f"{len(insights)}件"
)

metric_row1[1].metric(
    "今日の気づき",
    f"{len(today_insights)}件"
)

metric_row1[2].metric(
    "今月の気づき",
    f"{len(monthly_insights)}件"
)

metric_row1[3].metric(
    "実践済み",
    f"{len(practiced_insights)}件"
)


metric_row2 = st.columns(4)

metric_row2[0].metric(
    "実践率",
    f"{practice_rate(insights):.1f}%"
)

metric_row2[1].metric(
    "お気に入り",
    f"{len(favorite_insights)}件"
)

metric_row2[2].metric(
    "最多カテゴリー",
    top_category
)

metric_row2[3].metric(
    "平均重要度",
    (
        f"{average_importance(insights):.1f}/5"
        if insights
        else "未記録"
    )
)


# =========================================================
# 今日の気づき
# =========================================================

st.divider()

st.subheader(
    "🌱 今日の気づき"
)

if not today_insights:
    st.info(
        "今日の気づきはまだありません。"
    )

else:
    today_insights = sorted(
        today_insights,
        key=lambda insight: (
            insight.get(
                "created_at",
                ""
            )
        ),
        reverse=True
    )

    for insight in today_insights[
        :3
    ]:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### 💡 "
                f"{insight.get('title', '')}"
            )

            st.caption(
                f"{insight.get('category', '')} ／ "
                f"重要度 {insight.get('importance', 3)}/5"
            )

            if insight.get(
                "action",
                ""
            ):
                st.success(
                    "活かし方\n\n"
                    + insight.get(
                        "action",
                        ""
                    )
                )


# =========================================================
# 過去の気づきランダム表示
# =========================================================

if insights:
    st.divider()

    st.subheader(
        "🎲 以前こんなことに気づいていました"
    )

    if (
        "random_insight_id"
        not in st.session_state
    ):
        st.session_state[
            "random_insight_id"
        ] = random.choice(
            insights
        )["id"]

    random_insight = (
        get_insight_by_id(
            data,
            st.session_state[
                "random_insight_id"
            ]
        )
    )

    if random_insight:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### 💡 "
                f"{random_insight.get('title', '')}"
            )

            st.caption(
                format_date(
                    random_insight.get(
                        "insight_date",
                        ""
                    )
                )
            )

            if random_insight.get(
                "meaning",
                ""
            ):
                st.write(
                    random_insight.get(
                        "meaning",
                        ""
                    )
                )

            if random_insight.get(
                "action",
                ""
            ):
                st.success(
                    "この気づきを活かすなら\n\n"
                    + random_insight.get(
                        "action",
                        ""
                    )
                )

    if st.button(
        "🔄 別の気づきを表示"
    ):
        st.session_state[
            "random_insight_id"
        ] = random.choice(
            insights
        )["id"]

        st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    practice_tab,
    favorite_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 気づきを登録",
        "📚 気づき一覧",
        "🚀 実践・結果",
        "⭐ お気に入り",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 登録
# =========================================================

with add_tab:
    st.header(
        "➕ 今日の気づきを登録"
    )

    with st.form(
        "add_insight_form",
        clear_on_submit=True
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            insight_date_input = (
                st.date_input(
                    "日付",
                    value=date.today(),
                    max_value=date.today()
                )
            )

            title = st.text_area(
                "今日の気づき",
                placeholder=(
                    "例：最初から完璧に作ろうとすると手が止まりやすい"
                ),
                height=100
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES
            )

            source = st.selectbox(
                "気づいたきっかけ",
                SOURCES
            )

        with column2:
            importance = st.slider(
                "重要度",
                min_value=1,
                max_value=5,
                value=3
            )

            practice_status = (
                st.selectbox(
                    "実践状態",
                    PRACTICE_STATUSES
                )
            )

            selected_tags = (
                st.multiselect(
                    "既存タグ",
                    all_tags
                )
            )

            custom_tags = st.text_input(
                "新しいタグ",
                placeholder=(
                    "React, 習慣, 考え方"
                )
            )

        trigger = st.text_area(
            "具体的なきっかけ",
            placeholder=(
                "何があって、そのことに気づいた？"
            ),
            height=100
        )

        meaning = st.text_area(
            "この気づきから何が分かった？",
            placeholder=(
                "自分なりの解釈や学び"
            ),
            height=110
        )

        action = st.text_area(
            "今後どう活かす？",
            placeholder=(
                "例：まず動くものを作って、あとから改善する"
            ),
            height=110
        )

        memo = st.text_area(
            "補足メモ",
            placeholder=(
                "あとで思い出したいこと"
            ),
            height=80
        )

        submitted = (
            st.form_submit_button(
                "💡 気づきを保存",
                use_container_width=True
            )
        )

        if submitted:
            final_tags = [
                tag.strip()
                for tag in custom_tags.split(
                    ","
                )
                if tag.strip()
            ]

            final_tags = list(
                dict.fromkeys(
                    selected_tags
                    + final_tags
                )
            )

            if not title.strip():
                st.error(
                    "今日の気づきを入力してください。"
                )

            else:
                add_insight(
                    data,
                    {
                        "insight_date": str(
                            insight_date_input
                        ),
                        "title": title.strip(),
                        "trigger": trigger.strip(),
                        "source": source,
                        "category": category,
                        "importance": importance,
                        "meaning": meaning.strip(),
                        "action": action.strip(),
                        "practice_status": (
                            practice_status
                        ),
                        "tags": final_tags,
                        "memo": memo.strip(),
                    }
                )

                st.success(
                    "気づきを保存しました！"
                )

                st.rerun()


# =========================================================
# 一覧
# =========================================================

with list_tab:
    st.header(
        "📚 気づき一覧"
    )

    if not insights:
        st.info(
            "気づきはまだありません。"
        )

    else:
        filter_columns = (
            st.columns(3)
        )

        with filter_columns[0]:
            keyword = st.text_input(
                "🔍 検索",
                placeholder=(
                    "気づき・きっかけ・学び"
                )
            )

        with filter_columns[1]:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES
                )
            )

        with filter_columns[2]:
            practice_filter = (
                st.selectbox(
                    "実践状態",
                    [
                        "すべて"
                    ]
                    + PRACTICE_STATUSES
                )
            )

        importance_filter = (
            st.multiselect(
                "重要度",
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                ],
                default=[
                    1,
                    2,
                    3,
                    4,
                    5,
                ]
            )
        )

        tag_filter = st.selectbox(
            "タグ",
            [
                "すべて"
            ]
            + all_tags
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "新しい順",
                "重要度が高い順",
                "古い順",
            ]
        )

        filtered = list(
            insights
        )

        if keyword.strip():
            word = keyword.strip().lower()

            filtered = [
                insight
                for insight in filtered
                if (
                    word
                    in insight.get(
                        "title",
                        ""
                    ).lower()
                    or word
                    in insight.get(
                        "trigger",
                        ""
                    ).lower()
                    or word
                    in insight.get(
                        "meaning",
                        ""
                    ).lower()
                    or word
                    in insight.get(
                        "action",
                        ""
                    ).lower()
                )
            ]

        if category_filter != "すべて":
            filtered = [
                insight
                for insight in filtered
                if insight.get(
                    "category"
                )
                == category_filter
            ]

        if practice_filter != "すべて":
            filtered = [
                insight
                for insight in filtered
                if insight.get(
                    "practice_status"
                )
                == practice_filter
            ]

        filtered = [
            insight
            for insight in filtered
            if int(
                insight.get(
                    "importance",
                    3
                )
            )
            in importance_filter
        ]

        if tag_filter != "すべて":
            filtered = [
                insight
                for insight in filtered
                if tag_filter
                in insight.get(
                    "tags",
                    []
                )
            ]

        if sort_option == "新しい順":
            filtered.sort(
                key=lambda insight: (
                    insight.get(
                        "insight_date",
                        ""
                    ),
                    insight.get(
                        "created_at",
                        ""
                    ),
                ),
                reverse=True
            )

        elif sort_option == (
            "重要度が高い順"
        ):
            filtered.sort(
                key=lambda insight: int(
                    insight.get(
                        "importance",
                        0
                    )
                ),
                reverse=True
            )

        else:
            filtered.sort(
                key=lambda insight: (
                    insight.get(
                        "insight_date",
                        ""
                    ),
                    insight.get(
                        "created_at",
                        ""
                    ),
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered)}件**"
        )

        for insight in filtered:
            insight_id = insight[
                "id"
            ]

            with st.container(
                border=True
            ):
                column1, column2 = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with column1:
                    favorite_icon = (
                        "⭐ "
                        if insight.get(
                            "favorite",
                            False
                        )
                        else ""
                    )

                    st.markdown(
                        f"### "
                        f"{favorite_icon}"
                        f"{insight.get('title', '')}"
                    )

                    st.caption(
                        f"{format_date(insight.get('insight_date', ''))} ／ "
                        f"{insight.get('category', '')} ／ "
                        f"{insight.get('source', '')}"
                    )

                with column2:
                    st.metric(
                        "重要度",
                        f"{insight.get('importance', 3)}/5"
                    )

                if insight.get(
                    "trigger",
                    ""
                ):
                    st.write(
                        "**きっかけ**"
                    )

                    st.write(
                        insight.get(
                            "trigger",
                            ""
                        )
                    )

                if insight.get(
                    "meaning",
                    ""
                ):
                    st.info(
                        "💡 分かったこと\n\n"
                        + insight.get(
                            "meaning",
                            ""
                        )
                    )

                if insight.get(
                    "action",
                    ""
                ):
                    st.success(
                        "🚀 今後どう活かす？\n\n"
                        + insight.get(
                            "action",
                            ""
                        )
                    )

                st.write(
                    f"{PRACTICE_ICONS.get(insight.get('practice_status', ''), '')} "
                    f"実践状態："
                    f"**{insight.get('practice_status', '')}**"
                )

                if insight.get(
                    "tags",
                    []
                ):
                    st.caption(
                        "🏷️ "
                        + " / ".join(
                            insight.get(
                                "tags",
                                []
                            )
                        )
                    )

                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if insight.get(
                            "favorite",
                            False
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        f"favorite_"
                        f"{insight_id}"
                    ),
                    use_container_width=True
                ):
                    toggle_favorite(
                        data,
                        insight_id
                    )

                    st.rerun()

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = (
                        st.text_area(
                            "気づき",
                            value=insight.get(
                                "title",
                                ""
                            ),
                            key=(
                                f"edit_title_"
                                f"{insight_id}"
                            )
                        )
                    )

                    current_category = (
                        insight.get(
                            "category",
                            "その他"
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
                                    len(
                                        CATEGORIES
                                    )
                                    - 1
                                )
                            ),
                            key=(
                                f"edit_category_"
                                f"{insight_id}"
                            )
                        )
                    )

                    edit_importance = (
                        st.slider(
                            "重要度",
                            min_value=1,
                            max_value=5,
                            value=int(
                                insight.get(
                                    "importance",
                                    3
                                )
                            ),
                            key=(
                                f"edit_importance_"
                                f"{insight_id}"
                            )
                        )
                    )

                    edit_trigger = (
                        st.text_area(
                            "きっかけ",
                            value=insight.get(
                                "trigger",
                                ""
                            ),
                            key=(
                                f"edit_trigger_"
                                f"{insight_id}"
                            )
                        )
                    )

                    edit_meaning = (
                        st.text_area(
                            "分かったこと",
                            value=insight.get(
                                "meaning",
                                ""
                            ),
                            key=(
                                f"edit_meaning_"
                                f"{insight_id}"
                            )
                        )
                    )

                    edit_action = (
                        st.text_area(
                            "活かし方",
                            value=insight.get(
                                "action",
                                ""
                            ),
                            key=(
                                f"edit_action_"
                                f"{insight_id}"
                            )
                        )
                    )

                    current_status = (
                        insight.get(
                            "practice_status",
                            "まだ"
                        )
                    )

                    edit_status = (
                        st.selectbox(
                            "実践状態",
                            PRACTICE_STATUSES,
                            index=(
                                PRACTICE_STATUSES.index(
                                    current_status
                                )
                                if current_status
                                in PRACTICE_STATUSES
                                else 0
                            ),
                            key=(
                                f"edit_status_"
                                f"{insight_id}"
                            )
                        )
                    )

                    edit_tags = st.text_input(
                        "タグ",
                        value=", ".join(
                            insight.get(
                                "tags",
                                []
                            )
                        ),
                        key=(
                            f"edit_tags_"
                            f"{insight_id}"
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_"
                            f"{insight_id}"
                        ),
                        use_container_width=True
                    ):
                        final_tags = [
                            tag.strip()
                            for tag in edit_tags.split(
                                ","
                            )
                            if tag.strip()
                        ]

                        update_insight(
                            data,
                            insight_id,
                            {
                                "title": (
                                    edit_title.strip()
                                ),
                                "category": (
                                    edit_category
                                ),
                                "importance": (
                                    edit_importance
                                ),
                                "trigger": (
                                    edit_trigger.strip()
                                ),
                                "meaning": (
                                    edit_meaning.strip()
                                ),
                                "action": (
                                    edit_action.strip()
                                ),
                                "practice_status": (
                                    edit_status
                                ),
                                "tags": list(
                                    dict.fromkeys(
                                        final_tags
                                    )
                                ),
                            }
                        )

                        st.rerun()

                with st.expander(
                    "🗑️ 削除"
                ):
                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_delete_"
                                f"{insight_id}"
                            )
                        )
                    )

                    if st.button(
                        "この気づきを削除",
                        key=(
                            f"delete_"
                            f"{insight_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_insight(
                            data,
                            insight_id
                        )

                        st.rerun()


# =========================================================
# 実践・結果
# =========================================================

with practice_tab:
    st.header(
        "🚀 気づきを実践する"
    )

    actionable = [
        insight
        for insight in insights
        if insight.get(
            "action",
            ""
        ).strip()
    ]

    if not actionable:
        st.info(
            "「今後どう活かす？」を登録するとここで実践を記録できます。"
        )

    else:
        practice_options = {
            (
                f"{insight.get('title', '')}"
                f"｜{insight.get('practice_status', '')}"
            ): insight["id"]
            for insight in actionable
        }

        selected_label = (
            st.selectbox(
                "実践する気づき",
                list(
                    practice_options.keys()
                )
            )
        )

        practice_insight = (
            get_insight_by_id(
                data,
                practice_options[
                    selected_label
                ]
            )
        )

        practice_id = (
            practice_insight["id"]
        )

        with st.container(
            border=True
        ):
            st.subheader(
                practice_insight.get(
                    "title",
                    ""
                )
            )

            st.success(
                "実践すること\n\n"
                + practice_insight.get(
                    "action",
                    ""
                )
            )

        current_status = (
            practice_insight.get(
                "practice_status",
                "まだ"
            )
        )

        with st.form(
            f"practice_form_{practice_id}"
        ):
            practice_status = (
                st.selectbox(
                    "実践状態",
                    PRACTICE_STATUSES,
                    index=(
                        PRACTICE_STATUSES.index(
                            current_status
                        )
                        if current_status
                        in PRACTICE_STATUSES
                        else 0
                    )
                )
            )

            practice_result = (
                st.text_area(
                    "実践した結果",
                    value=(
                        practice_insight.get(
                            "practice_result",
                            ""
                        )
                    ),
                    placeholder=(
                        "例：5分だけ始めたら30分続けられた"
                    ),
                    height=120
                )
            )

            practice_learning = (
                st.text_area(
                    "実践して新しく分かったこと",
                    value=(
                        practice_insight.get(
                            "practice_learning",
                            ""
                        )
                    ),
                    placeholder=(
                        "実際にやってみて分かったこと"
                    ),
                    height=110
                )
            )

            submitted = (
                st.form_submit_button(
                    "🚀 実践記録を保存",
                    use_container_width=True
                )
            )

            if submitted:
                update_insight(
                    data,
                    practice_id,
                    {
                        "practice_status": (
                            practice_status
                        ),
                        "practice_result": (
                            practice_result.strip()
                        ),
                        "practice_learning": (
                            practice_learning.strip()
                        ),
                    }
                )

                st.success(
                    "実践記録を保存しました！"
                )

                st.rerun()


# =========================================================
# お気に入り
# =========================================================

with favorite_tab:
    st.header(
        "⭐ 大切な気づき"
    )

    favorites = [
        insight
        for insight in insights
        if insight.get(
            "favorite",
            False
        )
    ]

    if not favorites:
        st.info(
            "お気に入りの気づきはありません。"
        )

    else:
        favorites.sort(
            key=lambda insight: int(
                insight.get(
                    "importance",
                    0
                )
            ),
            reverse=True
        )

        for insight in favorites:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### ⭐ "
                    f"{insight.get('title', '')}"
                )

                st.caption(
                    f"{format_date(insight.get('insight_date', ''))} ／ "
                    f"{insight.get('category', '')}"
                )

                if insight.get(
                    "meaning",
                    ""
                ):
                    st.info(
                        insight.get(
                            "meaning",
                            ""
                        )
                    )

                if insight.get(
                    "action",
                    ""
                ):
                    st.success(
                        insight.get(
                            "action",
                            ""
                        )
                    )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 気づきの分析"
    )

    if not insights:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for insight in insights:
            analysis_rows.append(
                {
                    "日付": (
                        insight.get(
                            "insight_date",
                            ""
                        )
                    ),
                    "月": (
                        insight.get(
                            "insight_date",
                            ""
                        )[:7]
                    ),
                    "気づき": (
                        insight.get(
                            "title",
                            ""
                        )
                    ),
                    "カテゴリー": (
                        insight.get(
                            "category",
                            ""
                        )
                    ),
                    "きっかけ": (
                        insight.get(
                            "source",
                            ""
                        )
                    ),
                    "重要度": int(
                        insight.get(
                            "importance",
                            0
                        )
                    ),
                    "実践状態": (
                        insight.get(
                            "practice_status",
                            ""
                        )
                    ),
                    "お気に入り": (
                        1
                        if insight.get(
                            "favorite",
                            False
                        )
                        else 0
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "カテゴリー別気づき数"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "気づき数"
                }
            )
            .sort_values(
                "気づき数",
                ascending=False
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["気づき数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "月別気づき数"
        )

        monthly_summary = (
            analysis_df.groupby(
                "月",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "気づき数"
                }
            )
            .sort_values(
                "月"
            )
        )

        st.line_chart(
            monthly_summary.set_index(
                "月"
            )[["気づき数"]]
        )

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "重要度別"
        )

        importance_summary = (
            analysis_df.groupby(
                "重要度",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "重要度"
            )
        )

        st.bar_chart(
            importance_summary.set_index(
                "重要度"
            )[["件数"]]
        )

        st.dataframe(
            importance_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "実践状態"
        )

        practice_summary = (
            analysis_df.groupby(
                "実践状態",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False
            )
        )

        st.bar_chart(
            practice_summary.set_index(
                "実践状態"
            )[["件数"]]
        )

        st.dataframe(
            practice_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "気づきのきっかけ"
        )

        source_summary = (
            analysis_df.groupby(
                "きっかけ",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False
            )
        )

        st.bar_chart(
            source_summary.set_index(
                "きっかけ"
            )[["件数"]]
        )

        st.dataframe(
            source_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "よく使うタグ"
        )

        tag_counter = Counter()

        for insight in insights:
            for tag in insight.get(
                "tags",
                []
            ):
                tag_counter[
                    tag
                ] += 1

        if not tag_counter:
            st.info(
                "タグはまだありません。"
            )

        else:
            tag_df = pd.DataFrame(
                [
                    {
                        "タグ": tag,
                        "使用回数": count,
                    }
                    for tag, count
                    in tag_counter.most_common()
                ]
            )

            st.bar_chart(
                tag_df.set_index(
                    "タグ"
                )[["使用回数"]]
            )

            st.dataframe(
                tag_df,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "実践につながった気づき"
        )

        practiced_df = analysis_df[
            analysis_df[
                "実践状態"
            ]
            == "実践済み"
        ].sort_values(
            "重要度",
            ascending=False
        )

        if practiced_df.empty:
            st.info(
                "実践済みの気づきはまだありません。"
            )

        else:
            st.dataframe(
                practiced_df[
                    [
                        "気づき",
                        "カテゴリー",
                        "重要度",
                        "日付",
                    ]
                ],
                use_container_width=True,
                hide_index=True
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
        indent=2
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"insight_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = (
        st.file_uploader(
            "バックアップJSONを選択",
            type=[
                "json"
            ]
        )
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict
                )
                or "insights"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "insights"
                    ],
                    list
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
                    use_container_width=True
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
            UnicodeDecodeError
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "すべての気づき・実践記録が削除されます。"
    )

    confirm_delete_all = (
        st.checkbox(
            "全データ削除を確認しました"
        )
    )

    if st.button(
        "すべて削除",
        disabled=(
            not confirm_delete_all
        ),
        use_container_width=True
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
    "小さな気づきを残すと、昨日まで見えなかったものが少しずつ見えてくる。💡"
)
