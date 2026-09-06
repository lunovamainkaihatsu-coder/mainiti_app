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
    page_title="今日の小さな勝ち",
    page_icon="🏆",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "small_wins.json",
)

CATEGORIES = [
    "🤖 AI・プログラミング",
    "🎨 イラスト",
    "📚 勉強",
    "💼 仕事",
    "🏠 生活",
    "💪 運動",
    "👨‍👩‍👧 家族",
    "🧹 整理整頓",
    "🧠 気持ち",
    "🔥 挑戦",
    "✨ その他",
]

MAX_WINS_PER_DAY = 3


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "wins": []
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
            "wins",
            [],
        )

        for win in data["wins"]:
            win.setdefault(
                "id",
                create_id(),
            )

            win.setdefault(
                "title",
                "",
            )

            win.setdefault(
                "category",
                "✨ その他",
            )

            win.setdefault(
                "date",
                str(date.today()),
            )

            win.setdefault(
                "memo",
                "",
            )

            win.setdefault(
                "favorite",
                False,
            )

            win.setdefault(
                "created_at",
                "",
            )

            win.setdefault(
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
        save_data(data)
        return data


# =========================================================
# 補助関数
# =========================================================

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

    except (
        ValueError,
        TypeError,
    ):
        return date_text


def get_today_wins(
    data,
):
    today_text = str(
        date.today()
    )

    return [
        win
        for win in data["wins"]
        if win.get(
            "date"
        )
        == today_text
    ]


def get_win_by_id(
    data,
    win_id,
):
    return next(
        (
            win
            for win in data[
                "wins"
            ]
            if win.get(
                "id"
            )
            == win_id
        ),
        None,
    )


def calculate_streak(
    data,
):
    recorded_dates = {
        win.get(
            "date"
        )
        for win in data[
            "wins"
        ]
        if win.get(
            "date"
        )
    }

    if not recorded_dates:
        return 0

    current = date.today()

    if str(
        current
    ) not in recorded_dates:
        current -= timedelta(
            days=1
        )

        if str(
            current
        ) not in recorded_dates:
            return 0

    streak = 0

    while str(
        current
    ) in recorded_dates:
        streak += 1

        current -= timedelta(
            days=1
        )

    return streak


# =========================================================
# CRUD
# =========================================================

def add_win(
    data,
    title,
    category,
    memo,
    favorite,
):
    today_wins = get_today_wins(
        data
    )

    if len(
        today_wins
    ) >= MAX_WINS_PER_DAY:
        return False

    data[
        "wins"
    ].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "date": str(
                date.today()
            ),
            "memo": memo,
            "favorite": favorite,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)

    return True


def update_win(
    data,
    win_id,
    title,
    category,
    memo,
    favorite,
):
    win = get_win_by_id(
        data,
        win_id,
    )

    if not win:
        return

    win[
        "title"
    ] = title

    win[
        "category"
    ] = category

    win[
        "memo"
    ] = memo

    win[
        "favorite"
    ] = favorite

    win[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    win_id,
):
    win = get_win_by_id(
        data,
        win_id,
    )

    if not win:
        return

    win[
        "favorite"
    ] = not win.get(
        "favorite",
        False,
    )

    win[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_win(
    data,
    win_id,
):
    data[
        "wins"
    ] = [
        win
        for win in data[
            "wins"
        ]
        if win.get(
            "id"
        )
        != win_id
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
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 190, 80, 0.08);
        border: 1px solid rgba(255, 190, 80, 0.16);
        border-radius: 16px;
        padding: 15px;
    }

    .hero {
        padding: 28px;
        border-radius: 24px;
        margin-bottom: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 80, 0.18),
                rgba(255, 120, 150, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.78;
    }

    .win-card {
        padding: 20px;
        border-radius: 18px;
        border: 1px solid rgba(255, 190, 80, 0.16);
        margin-bottom: 12px;
    }

    .win-number {
        font-size: 0.9rem;
        opacity: 0.65;
        font-weight: 700;
    }

    .win-title {
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 10px;
    }

    .three-win-box {
        padding: 28px;
        border-radius: 22px;
        text-align: center;
        background: rgba(255, 190, 80, 0.10);
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .three-win-title {
        font-size: 1.5rem;
        font-weight: 900;
    }

    .random-box {
        padding: 25px;
        border-radius: 22px;
        text-align: center;
        background: rgba(120, 150, 255, 0.07);
        margin-bottom: 15px;
    }

    .random-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 読み込み
# =========================================================

data = load_data()

wins = data[
    "wins"
]

today_wins = sorted(
    get_today_wins(
        data
    ),
    key=lambda win: (
        win.get(
            "created_at",
            ""
        )
    ),
)

today_count = len(
    today_wins
)

current_month = date.today().strftime(
    "%Y-%m"
)

month_wins = [
    win
    for win in wins
    if win.get(
        "date",
        "",
    ).startswith(
        current_month
    )
]

favorite_count = len(
    [
        win
        for win in wins
        if win.get(
            "favorite",
            False,
        )
    ]
)

streak = calculate_streak(
    data
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🏆 今日の小さな勝ち</h1>

        <p>
            大きな成果じゃなくていい。
            今日できたことを、3つだけ残そう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

col1.metric(
    "🏆 今日",
    f"{today_count} / 3",
)

col2.metric(
    "📅 今月",
    f"{len(month_wins)}勝",
)

col3.metric(
    "🔥 連続記録",
    f"{streak}日",
)

col4.metric(
    "⭐ お気に入り",
    f"{favorite_count}個",
)


progress = today_count / 3

st.write(
    f"**今日の勝ちゲージ：{round(progress * 100)}%**"
)

st.progress(
    progress
)


# =========================================================
# 3勝表示
# =========================================================

if today_count >= 3:
    st.markdown(
        """
        <div class="three-win-box">

            <div class="three-win-title">
                🎉 今日も3勝！
            </div>

            <div style="margin-top:8px;">
                大きく進まなくても、
                今日もちゃんと前に進んだ。
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 今日の勝ち
# =========================================================

st.divider()

st.subheader(
    "🌟 今日の勝ち"
)

if not today_wins:
    st.info(
        "まだ今日の勝ちはありません。"
        "小さなことでOK！"
    )

else:
    for index, win in enumerate(
        today_wins,
        start=1,
    ):
        win_id = win.get(
            "id",
            "",
        )

        favorite_mark = (
            "⭐"
            if win.get(
                "favorite",
                False,
            )
            else ""
        )

        with st.container(
            border=True,
        ):
            st.caption(
                f"今日の勝ち {index}"
            )

            st.markdown(
                f"### {favorite_mark}"
                f"{win.get('title', '')}"
            )

            st.caption(
                win.get(
                    "category",
                    "",
                )
            )

            if win.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{win.get('memo', '')}"
                )

            button_text = (
                "⭐ お気に入り解除"
                if win.get(
                    "favorite",
                    False,
                )
                else "☆ お気に入り"
            )

            if st.button(
                button_text,
                key=(
                    "favorite_today_"
                    + win_id
                ),
                use_container_width=True,
            ):
                toggle_favorite(
                    data,
                    win_id,
                )

                st.rerun()


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "➕ 小さな勝ちを追加"
)

if today_count >= MAX_WINS_PER_DAY:
    st.success(
        "今日はもう3勝！🏆"
    )

    st.caption(
        "今日はここまでで十分。"
        "また明日、新しい勝ちを残そう。"
    )

else:
    st.info(
        f"あと "
        f"{MAX_WINS_PER_DAY - today_count}"
        f" 件登録できます。"
    )

    with st.form(
        "add_win_form"
    ):
        title = st.text_input(
            "今日できたこと",
            placeholder=(
                "例：AIのコードを10分読めた"
            ),
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        memo = st.text_area(
            "ひとこと",
            placeholder=(
                "例：全部理解できなくても続けられた"
            ),
            height=90,
        )

        favorite = st.checkbox(
            "⭐ お気に入りにする"
        )

        submitted = (
            st.form_submit_button(
                "🏆 今日の勝ちに追加",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.error(
                    "できたことを入力してください。"
                )

            else:
                result = add_win(
                    data,
                    title.strip(),
                    category,
                    memo.strip(),
                    favorite,
                )

                if result:
                    st.success(
                        "今日の勝ちを記録しました！"
                    )

                st.rerun()


# =========================================================
# ランダム発掘
# =========================================================

if wins:
    st.divider()

    st.subheader(
        "🎲 あの日の勝ちを思い出す"
    )

    valid_ids = {
        win.get(
            "id"
        )
        for win in wins
    }

    if (
        "random_win_id"
        not in st.session_state
        or st.session_state[
            "random_win_id"
        ]
        not in valid_ids
    ):
        st.session_state[
            "random_win_id"
        ] = random.choice(
            wins
        ).get(
            "id"
        )

    random_win = get_win_by_id(
        data,
        st.session_state[
            "random_win_id"
        ],
    )

    if random_win:
        st.markdown(
            f"""
            <div class="random-box">

                <div>
                    {format_date(random_win.get('date', ''))}
                </div>

                <div class="random-title">
                    🏆 {random_win.get('title', '')}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            random_win.get(
                "category",
                "",
            )
        )

        if random_win.get(
            "memo",
            "",
        ):
            st.write(
                f"💬 "
                f"{random_win.get('memo', '')}"
            )

    if st.button(
        "🎲 別の勝ちを発掘",
        use_container_width=True,
    ):
        if len(
            wins
        ) > 1:
            candidates = [
                win
                for win in wins
                if win.get(
                    "id"
                )
                != st.session_state.get(
                    "random_win_id"
                )
            ]

            st.session_state[
                "random_win_id"
            ] = random.choice(
                candidates
            ).get(
                "id"
            )

        st.rerun()


# =========================================================
# 最近7日
# =========================================================

st.divider()

st.subheader(
    "📅 最近7日"
)

week_rows = []

for offset in range(
    6,
    -1,
    -1,
):
    target = (
        date.today()
        - timedelta(
            days=offset
        )
    )

    target_text = str(
        target
    )

    count = len(
        [
            win
            for win in wins
            if win.get(
                "date"
            )
            == target_text
        ]
    )

    week_rows.append(
        {
            "日付": target.strftime(
                "%m/%d"
            ),
            "勝ち数": count,
            "状態": (
                "🏆 3勝"
                if count >= 3
                else (
                    "✨ 記録あり"
                    if count > 0
                    else "—"
                )
            ),
        }
    )

week_df = pd.DataFrame(
    week_rows
)

st.dataframe(
    week_df,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# カテゴリー別グラフ
# =========================================================

if wins:
    st.divider()

    st.subheader(
        "📊 勝ちの内訳"
    )

    category_rows = []

    for category_name in CATEGORIES:
        count = len(
            [
                win
                for win in wins
                if win.get(
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
                    "勝ち数": count,
                }
            )

    if category_rows:
        category_df = pd.DataFrame(
            category_rows
        ).sort_values(
            "勝ち数",
            ascending=False,
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 過去履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の小さな勝ち"
):
    past_wins = sorted(
        wins,
        key=lambda win: (
            win.get(
                "date",
                ""
            ),
            win.get(
                "created_at",
                ""
            ),
        ),
        reverse=True,
    )

    if not past_wins:
        st.caption(
            "まだ記録がありません。"
        )

    else:
        for win in past_wins:
            favorite_mark = (
                "⭐"
                if win.get(
                    "favorite",
                    False,
                )
                else ""
            )

            st.markdown(
                f"**{favorite_mark}"
                f"🏆 {win.get('title', '')}**"
            )

            st.caption(
                f"{format_date(win.get('date', ''))}"
                f" ／ "
                f"{win.get('category', '')}"
            )

            if win.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{win.get('memo', '')}"
                )

            st.divider()


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 記録を編集・削除"
):
    if not wins:
        st.caption(
            "編集できる記録はありません。"
        )

    else:
        sorted_wins = sorted(
            wins,
            key=lambda win: (
                win.get(
                    "date",
                    ""
                ),
                win.get(
                    "created_at",
                    ""
                ),
            ),
            reverse=True,
        )

        for win in sorted_wins:
            win_id = win.get(
                "id",
                "",
            )

            st.markdown(
                f"### 🏆 "
                f"{win.get('title', '')}"
            )

            st.caption(
                f"{format_date(win.get('date', ''))}"
                f" ／ "
                f"{win.get('category', '')}"
            )

            with st.expander(
                "✏️ 編集"
            ):
                edit_title = st.text_input(
                    "できたこと",
                    value=win.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + win_id
                    ),
                )

                current_category = win.get(
                    "category",
                    "✨ その他",
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
                            else len(
                                CATEGORIES
                            ) - 1
                        ),
                        key=(
                            "edit_category_"
                            + win_id
                        ),
                    )
                )

                edit_memo = st.text_area(
                    "ひとこと",
                    value=win.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + win_id
                    ),
                )

                edit_favorite = (
                    st.checkbox(
                        "⭐ お気に入り",
                        value=win.get(
                            "favorite",
                            False,
                        ),
                        key=(
                            "edit_favorite_"
                            + win_id
                        ),
                    )
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + win_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.error(
                            "できたことを入力してください。"
                        )

                    else:
                        update_win(
                            data,
                            win_id,
                            edit_title.strip(),
                            edit_category,
                            edit_memo.strip(),
                            edit_favorite,
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この記録を削除",
                    key=(
                        "delete_"
                        + win_id
                    ),
                    use_container_width=True,
                ):
                    delete_win(
                        data,
                        win_id,
                    )

                    if (
                        st.session_state.get(
                            "random_win_id"
                        )
                        == win_id
                    ):
                        st.session_state.pop(
                            "random_win_id",
                            None,
                        )

                    st.rerun()

            st.divider()


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
            "small_wins_"
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
    "大きな一歩じゃなくていい。今日の小さな勝ちを残そう。🏆✨"
)
