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
    page_title="1日1アイデア",
    page_icon="💡",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "idea_data.json",
)

CATEGORIES = [
    "アプリ",
    "AI",
    "仕事",
    "副業",
    "イラスト",
    "生活改善",
    "コンテンツ",
    "LuNova",
    "その他",
]

STATUSES = [
    "💡 未整理",
    "🌱 育てる",
    "⏸ 保留",
    "🗑 ボツ",
]


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(
        uuid.uuid4()
    )


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "ideas": []
    }


# =========================================================
# 保存
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


# =========================================================
# 読み込み
# =========================================================

def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = create_empty_data()

        save_data(
            data
        )

        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

        if not isinstance(
            data,
            dict,
        ):
            data = create_empty_data()

        data.setdefault(
            "ideas",
            [],
        )

        for idea in data[
            "ideas"
        ]:
            idea.setdefault(
                "id",
                create_id(),
            )

            idea.setdefault(
                "date",
                str(
                    date.today()
                ),
            )

            idea.setdefault(
                "title",
                "",
            )

            idea.setdefault(
                "category",
                "その他",
            )

            idea.setdefault(
                "memo",
                "",
            )

            idea.setdefault(
                "status",
                "💡 未整理",
            )

            idea.setdefault(
                "created_at",
                "",
            )

            idea.setdefault(
                "updated_at",
                "",
            )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = create_empty_data()

        save_data(
            data
        )

        return data


# =========================================================
# 補助関数
# =========================================================

def get_today_idea(
    data,
):
    today_text = str(
        date.today()
    )

    return next(
        (
            idea
            for idea in data[
                "ideas"
            ]
            if idea.get(
                "date"
            )
            == today_text
        ),
        None,
    )


def get_idea_by_id(
    data,
    idea_id,
):
    return next(
        (
            idea
            for idea in data[
                "ideas"
            ]
            if idea.get(
                "id"
            )
            == idea_id
        ),
        None,
    )


def format_date(
    date_text,
):
    try:
        target = datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

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
            target.weekday()
        ]

        return target.strftime(
            f"%Y年%m月%d日（{weekday}）"
        )

    except ValueError:
        return date_text


def days_ago(
    date_text,
):
    try:
        target = datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

        diff = (
            date.today()
            - target
        ).days

        if diff == 0:
            return "今日"

        if diff == 1:
            return "昨日"

        return f"{diff}日前"

    except ValueError:
        return ""


# =========================================================
# データ操作
# =========================================================

def save_today_idea(
    data,
    title,
    category,
    memo,
):
    today_idea = get_today_idea(
        data
    )

    if today_idea:
        today_idea[
            "title"
        ] = title

        today_idea[
            "category"
        ] = category

        today_idea[
            "memo"
        ] = memo

        today_idea[
            "updated_at"
        ] = now_text()

    else:
        data[
            "ideas"
        ].append(
            {
                "id": create_id(),
                "date": str(
                    date.today()
                ),
                "title": title,
                "category": category,
                "memo": memo,
                "status": "💡 未整理",
                "created_at": now_text(),
                "updated_at": "",
            }
        )

    save_data(
        data
    )


def update_status(
    data,
    idea_id,
    status,
):
    idea = get_idea_by_id(
        data,
        idea_id,
    )

    if not idea:
        return

    idea[
        "status"
    ] = status

    idea[
        "updated_at"
    ] = now_text()

    save_data(
        data
    )


def update_idea(
    data,
    idea_id,
    title,
    category,
    memo,
):
    idea = get_idea_by_id(
        data,
        idea_id,
    )

    if not idea:
        return

    idea[
        "title"
    ] = title

    idea[
        "category"
    ] = category

    idea[
        "memo"
    ] = memo

    idea[
        "updated_at"
    ] = now_text()

    save_data(
        data
    )


def delete_idea(
    data,
    idea_id,
):
    data[
        "ideas"
    ] = [
        idea
        for idea
        in data[
            "ideas"
        ]
        if idea.get(
            "id"
        )
        != idea_id
    ]

    save_data(
        data
    )


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
        background: rgba(255, 190, 60, 0.08);
        border: 1px solid rgba(255, 190, 60, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 200, 70, 0.20),
                rgba(255, 130, 100, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.75;
    }

    .idea-box {
        padding: 24px;
        border-radius: 18px;
        background: rgba(255, 200, 70, 0.07);
        text-align: center;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .idea-text {
        font-size: 1.35rem;
        font-weight: 700;
        line-height: 1.6;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

ideas = data[
    "ideas"
]

today_idea = get_today_idea(
    data
)

current_month = date.today().strftime(
    "%Y-%m"
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>💡 1日1アイデア</h1>

        <p>
            思いついたら残す。
            今すぐ形にしなくてもいい。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

monthly_ideas = [
    idea
    for idea in ideas
    if idea.get(
        "date",
        "",
    ).startswith(
        current_month
    )
]

grow_ideas = [
    idea
    for idea in ideas
    if idea.get(
        "status"
    )
    == "🌱 育てる"
]


columns = st.columns(
    4
)

columns[0].metric(
    "今日",
    (
        "✅ 記録済み"
        if today_idea
        else "未記録"
    ),
)

columns[1].metric(
    "今月",
    f"{len(monthly_ideas)}個",
)

columns[2].metric(
    "🌱 育てる",
    f"{len(grow_ideas)}個",
)

columns[3].metric(
    "累計",
    f"{len(ideas)}個",
)


# =========================================================
# 今日のアイデア
# =========================================================

st.divider()

st.subheader(
    "💡 今日のアイデア"
)

default_title = (
    today_idea.get(
        "title",
        "",
    )
    if today_idea
    else ""
)

default_category = (
    today_idea.get(
        "category",
        "その他",
    )
    if today_idea
    else "その他"
)

default_memo = (
    today_idea.get(
        "memo",
        "",
    )
    if today_idea
    else ""
)


with st.form(
    "today_idea_form"
):
    title = st.text_area(
        "思いついたこと",
        value=default_title,
        placeholder=(
            "例：AIが今日の気分から、"
            "やることを1つだけ提案するアプリ"
        ),
        height=110,
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
        index=(
            CATEGORIES.index(
                default_category
            )
            if default_category
            in CATEGORIES
            else (
                len(
                    CATEGORIES
                )
                - 1
            )
        ),
    )

    memo = st.text_input(
        "ひとこと",
        value=default_memo,
        placeholder=(
            "例：シンプルなら作れそう"
        ),
    )

    submitted = (
        st.form_submit_button(
            (
                "💾 更新する"
                if today_idea
                else "💡 アイデアを残す"
            ),
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.error(
                "アイデアを入力してください。"
            )

        else:
            save_today_idea(
                data,
                title.strip(),
                category,
                memo.strip(),
            )

            st.success(
                "今日のアイデアを保存しました！"
            )

            st.rerun()


# =========================================================
# 今日の保存内容
# =========================================================

if today_idea:
    st.divider()

    st.subheader(
        "✨ 今日の1アイデア"
    )

    st.markdown(
        f"""
        <div class="idea-box">

            <div class="idea-text">
                💡 {today_idea.get('title', '')}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"{today_idea.get('category', '')}"
        f" ／ "
        f"{today_idea.get('status', '💡 未整理')}"
    )

    if today_idea.get(
        "memo",
        "",
    ):
        st.write(
            f"💬 "
            f"{today_idea.get('memo', '')}"
        )


# =========================================================
# ランダム再発掘
# =========================================================

past_ideas = [
    idea
    for idea in ideas
    if idea.get(
        "date"
    )
    != str(
        date.today()
    )
]


if past_ideas:
    st.divider()

    st.subheader(
        "🎲 眠っていたアイデア"
    )

    if (
        "random_idea_id"
        not in st.session_state
        or not any(
            idea.get(
                "id"
            )
            == st.session_state[
                "random_idea_id"
            ]
            for idea
            in past_ideas
        )
    ):
        st.session_state[
            "random_idea_id"
        ] = random.choice(
            past_ideas
        ).get(
            "id"
        )

    random_idea = next(
        (
            idea
            for idea
            in past_ideas
            if idea.get(
                "id"
            )
            == st.session_state[
                "random_idea_id"
            ]
        ),
        random.choice(
            past_ideas
        ),
    )

    with st.container(
        border=True,
    ):
        st.caption(
            f"🕰️ "
            f"{days_ago(random_idea.get('date', ''))}"
        )

        st.markdown(
            f"### 💡 "
            f"{random_idea.get('title', '')}"
        )

        st.caption(
            f"{format_date(random_idea.get('date', ''))}"
            f" ／ "
            f"{random_idea.get('category', '')}"
            f" ／ "
            f"{random_idea.get('status', '💡 未整理')}"
        )

        if random_idea.get(
            "memo",
            "",
        ):
            st.write(
                f"💬 "
                f"{random_idea.get('memo', '')}"
            )

        random_status = st.selectbox(
            "このアイデア、今どうする？",
            STATUSES,
            index=(
                STATUSES.index(
                    random_idea.get(
                        "status",
                        "💡 未整理",
                    )
                )
                if random_idea.get(
                    "status",
                    "💡 未整理",
                )
                in STATUSES
                else 0
            ),
            key=(
                "random_status_"
                + random_idea.get(
                    "id",
                    "",
                )
            ),
        )

        if st.button(
            "状態を更新",
            use_container_width=True,
        ):
            update_status(
                data,
                random_idea.get(
                    "id"
                ),
                random_status,
            )

            st.rerun()

    if st.button(
        "🎲 別のアイデアを見る",
        use_container_width=True,
    ):
        st.session_state[
            "random_idea_id"
        ] = random.choice(
            past_ideas
        ).get(
            "id"
        )

        st.rerun()


# =========================================================
# 状態別集計
# =========================================================

st.divider()

st.subheader(
    "📊 アイデアの状態"
)

if not ideas:
    st.info(
        "アイデアを記録すると集計が表示されます。"
    )

else:
    status_rows = []

    for status in STATUSES:
        count = len(
            [
                idea
                for idea in ideas
                if idea.get(
                    "status",
                    "💡 未整理",
                )
                == status
            ]
        )

        status_rows.append(
            {
                "状態": status,
                "個数": count,
            }
        )

    status_df = pd.DataFrame(
        status_rows
    )

    st.bar_chart(
        status_df.set_index(
            "状態"
        )
    )


# =========================================================
# カテゴリー集計
# =========================================================

st.divider()

st.subheader(
    "🧠 どんなアイデアが多い？"
)

if ideas:
    category_rows = []

    for category_name in CATEGORIES:
        count = len(
            [
                idea
                for idea in ideas
                if idea.get(
                    "category"
                )
                == category_name
            ]
        )

        if count > 0:
            category_rows.append(
                {
                    "カテゴリー": (
                        category_name
                    ),
                    "アイデア数": count,
                }
            )

    if category_rows:
        category_df = pd.DataFrame(
            category_rows
        ).sort_values(
            "アイデア数",
            ascending=False,
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )

        st.dataframe(
            category_df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 育てるアイデア
# =========================================================

st.divider()

st.subheader(
    "🌱 育てるアイデア"
)

if not grow_ideas:
    st.caption(
        "「🌱 育てる」にしたアイデアがここに並びます。"
    )

else:
    grow_ideas = sorted(
        grow_ideas,
        key=lambda idea: (
            idea.get(
                "date",
                "",
            )
        ),
        reverse=True,
    )

    for idea in grow_ideas:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 💡 "
                f"{idea.get('title', '')}"
            )

            st.caption(
                f"{format_date(idea.get('date', ''))}"
                f" ／ "
                f"{idea.get('category', '')}"
            )

            if idea.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{idea.get('memo', '')}"
                )


# =========================================================
# 全履歴
# =========================================================

st.divider()

with st.expander(
    "📚 アイデア一覧"
):
    if not ideas:
        st.info(
            "まだアイデアがありません。"
        )

    else:
        sorted_ideas = sorted(
            ideas,
            key=lambda idea: (
                idea.get(
                    "date",
                    "",
                )
            ),
            reverse=True,
        )

        for idea in sorted_ideas:
            idea_id = idea.get(
                "id",
                "",
            )

            with st.container(
                border=True,
            ):
                st.markdown(
                    f"### 💡 "
                    f"{idea.get('title', '')}"
                )

                st.caption(
                    f"{format_date(idea.get('date', ''))}"
                    f" ／ "
                    f"{idea.get('category', '')}"
                )

                if idea.get(
                    "memo",
                    "",
                ):
                    st.write(
                        f"💬 "
                        f"{idea.get('memo', '')}"
                    )

                # -----------------------------------------
                # 状態変更
                # -----------------------------------------

                current_status = idea.get(
                    "status",
                    "💡 未整理",
                )

                status = st.selectbox(
                    "状態",
                    STATUSES,
                    index=(
                        STATUSES.index(
                            current_status
                        )
                        if current_status
                        in STATUSES
                        else 0
                    ),
                    key=(
                        f"status_"
                        f"{idea_id}"
                    ),
                )

                if st.button(
                    "状態を保存",
                    key=(
                        f"save_status_"
                        f"{idea_id}"
                    ),
                    use_container_width=True,
                ):
                    update_status(
                        data,
                        idea_id,
                        status,
                    )

                    st.rerun()

                # -----------------------------------------
                # 編集
                # -----------------------------------------

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = st.text_area(
                        "アイデア",
                        value=idea.get(
                            "title",
                            "",
                        ),
                        key=(
                            f"edit_title_"
                            f"{idea_id}"
                        ),
                    )

                    current_category = (
                        idea.get(
                            "category",
                            "その他",
                        )
                    )

                    edit_category = st.selectbox(
                        "カテゴリー",
                        CATEGORIES,
                        index=(
                            CATEGORIES.index(
                                current_category
                            )
                            if current_category
                            in CATEGORIES
                            else 0
                        ),
                        key=(
                            f"edit_category_"
                            f"{idea_id}"
                        ),
                    )

                    edit_memo = st.text_input(
                        "ひとこと",
                        value=idea.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_memo_"
                            f"{idea_id}"
                        ),
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_edit_"
                            f"{idea_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_title.strip():
                            st.error(
                                "アイデアを入力してください。"
                            )

                        else:
                            update_idea(
                                data,
                                idea_id,
                                edit_title.strip(),
                                edit_category,
                                edit_memo.strip(),
                            )

                            st.rerun()

                # -----------------------------------------
                # 削除
                # -----------------------------------------

                with st.expander(
                    "🗑️ 削除"
                ):
                    if st.button(
                        "このアイデアを削除",
                        key=(
                            f"delete_"
                            f"{idea_id}"
                        ),
                        use_container_width=True,
                    ):
                        delete_idea(
                            data,
                            idea_id,
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
            f"idea_backup_"
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
    "今日の思いつきが、未来の何かになるかもしれない。💡"
)
