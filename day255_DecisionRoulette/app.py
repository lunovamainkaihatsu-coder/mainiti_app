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
    page_title="迷ったらルーレット",
    page_icon="🎯",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "roulette_data.json",
)

MIN_OPTIONS = 2
MAX_OPTIONS = 8


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
        "sets": [],
        "history": [],
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
            "sets",
            [],
        )

        data.setdefault(
            "history",
            [],
        )

        for roulette_set in data["sets"]:
            roulette_set.setdefault(
                "id",
                create_id(),
            )

            roulette_set.setdefault(
                "name",
                "名前なしセット",
            )

            roulette_set.setdefault(
                "options",
                [],
            )

            roulette_set.setdefault(
                "favorite",
                False,
            )

            roulette_set.setdefault(
                "created_at",
                now_text(),
            )

            roulette_set.setdefault(
                "updated_at",
                now_text(),
            )

        for item in data["history"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "set_id",
                "",
            )

            item.setdefault(
                "set_name",
                "",
            )

            item.setdefault(
                "result",
                "",
            )

            item.setdefault(
                "decided_at",
                now_text(),
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

def get_set_by_id(
    data,
    set_id,
):
    return next(
        (
            roulette_set
            for roulette_set in data[
                "sets"
            ]
            if roulette_set.get(
                "id"
            )
            == set_id
        ),
        None,
    )


def format_datetime(
    text,
):
    try:
        target = datetime.fromisoformat(
            text
        )

        return target.strftime(
            "%Y/%m/%d %H:%M"
        )

    except (
        ValueError,
        TypeError,
    ):
        return "不明"


def clean_options(
    options,
):
    cleaned = []

    for option in options:
        text = option.strip()

        if (
            text
            and text not in cleaned
        ):
            cleaned.append(
                text
            )

    return cleaned


# =========================================================
# CRUD
# =========================================================

def add_set(
    data,
    name,
    options,
    favorite,
):
    data[
        "sets"
    ].append(
        {
            "id": create_id(),
            "name": name,
            "options": options,
            "favorite": favorite,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)


def update_set(
    data,
    set_id,
    name,
    options,
    favorite,
):
    roulette_set = get_set_by_id(
        data,
        set_id,
    )

    if not roulette_set:
        return

    roulette_set[
        "name"
    ] = name

    roulette_set[
        "options"
    ] = options

    roulette_set[
        "favorite"
    ] = favorite

    roulette_set[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    set_id,
):
    roulette_set = get_set_by_id(
        data,
        set_id,
    )

    if not roulette_set:
        return

    roulette_set[
        "favorite"
    ] = not roulette_set.get(
        "favorite",
        False,
    )

    roulette_set[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_set(
    data,
    set_id,
):
    data[
        "sets"
    ] = [
        roulette_set
        for roulette_set in data[
            "sets"
        ]
        if roulette_set.get(
            "id"
        )
        != set_id
    ]

    save_data(data)


def add_history(
    data,
    roulette_set,
    result,
):
    data[
        "history"
    ].append(
        {
            "id": create_id(),
            "set_id": roulette_set.get(
                "id",
                "",
            ),
            "set_name": roulette_set.get(
                "name",
                "",
            ),
            "result": result,
            "decided_at": now_text(),
        }
    )

    save_data(data)


def delete_history(
    data,
    history_id,
):
    data[
        "history"
    ] = [
        item
        for item in data[
            "history"
        ]
        if item.get(
            "id"
        )
        != history_id
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
        background: rgba(110, 130, 255, 0.07);
        border: 1px solid rgba(110, 130, 255, 0.15);
        border-radius: 16px;
        padding: 15px;
    }

    .hero {
        padding: 28px;
        border-radius: 24px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 130, 255, 0.18),
                rgba(255, 160, 80, 0.12)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.78;
    }

    .result-box {
        padding: 35px 20px;
        border-radius: 24px;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 190, 60, 0.17),
                rgba(120, 130, 255, 0.11)
            );
    }

    .result-label {
        font-size: 1rem;
        opacity: 0.7;
        font-weight: 700;
    }

    .result-text {
        font-size: 2.2rem;
        font-weight: 900;
        margin-top: 12px;
        margin-bottom: 10px;
    }

    .option-chip {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px;
        border-radius: 999px;

        background:
            rgba(110, 130, 255, 0.09);

        border:
            1px solid rgba(
                110,
                130,
                255,
                0.14
            );
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

roulette_sets = data[
    "sets"
]

history = data[
    "history"
]

favorite_sets = [
    roulette_set
    for roulette_set in roulette_sets
    if roulette_set.get(
        "favorite",
        False,
    )
]

today_history = [
    item
    for item in history
    if format_datetime(
        item.get(
            "decided_at",
            "",
        )
    ).startswith(
        date.today().strftime(
            "%Y/%m/%d"
        )
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🎯 迷ったらルーレット</h1>

        <p>
            考えても決まらないなら、
            運に一票入れてみよう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3 = st.columns(
    3
)

col1.metric(
    "🎯 セット",
    f"{len(roulette_sets)}個",
)

col2.metric(
    "⭐ お気に入り",
    f"{len(favorite_sets)}個",
)

col3.metric(
    "🎉 今日の決定",
    f"{len(today_history)}回",
)


# =========================================================
# ルーレット本体
# =========================================================

st.divider()

st.subheader(
    "🎰 ルーレットを回す"
)

if not roulette_sets:
    st.info(
        "まずは下の「新しいセットを作る」から、"
        "ルーレットを作ってみよう！"
    )

else:
    sorted_sets = sorted(
        roulette_sets,
        key=lambda roulette_set: (
            not roulette_set.get(
                "favorite",
                False,
            ),
            roulette_set.get(
                "name",
                "",
            ),
        ),
    )

    selected_id = st.selectbox(
        "使うセット",
        options=[
            roulette_set.get(
                "id"
            )
            for roulette_set in sorted_sets
        ],
        format_func=lambda set_id: (
            (
                "⭐ "
                if get_set_by_id(
                    data,
                    set_id,
                ).get(
                    "favorite",
                    False,
                )
                else ""
            )
            + get_set_by_id(
                data,
                set_id,
            ).get(
                "name",
                ""
            )
        ),
    )

    selected_set = get_set_by_id(
        data,
        selected_id,
    )

    if selected_set:
        st.caption(
            f"候補："
            f"{len(selected_set.get('options', []))}個"
        )

        options = selected_set.get(
            "options",
            [],
        )

        if options:
            option_text = ""

            for option in options:
                option_text += (
                    f'<span class="option-chip">'
                    f'{option}'
                    f'</span>'
                )

            st.markdown(
                option_text,
                unsafe_allow_html=True,
            )

        if len(
            options
        ) >= MIN_OPTIONS:
            if st.button(
                "🎯 ルーレットを回す！",
                use_container_width=True,
                type="primary",
            ):
                result = random.choice(
                    options
                )

                st.session_state[
                    "roulette_result"
                ] = result

                st.session_state[
                    "roulette_set_id"
                ] = selected_id

                st.rerun()

        else:
            st.warning(
                "候補を2個以上登録してください。"
            )


# =========================================================
# 抽選結果
# =========================================================

result = st.session_state.get(
    "roulette_result"
)

result_set_id = (
    st.session_state.get(
        "roulette_set_id"
    )
)

if (
    result
    and result_set_id
):
    result_set = get_set_by_id(
        data,
        result_set_id,
    )

    if result_set:
        st.markdown(
            f"""
            <div class="result-box">

                <div class="result-label">
                    🎉 今日の結果
                </div>

                <div class="result-text">
                    {result}
                </div>

                <div>
                    迷ったら、今日はこれ！
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(
            2
        )

        with col1:
            if st.button(
                "✅ 採用する！",
                use_container_width=True,
                type="primary",
            ):
                add_history(
                    data,
                    result_set,
                    result,
                )

                st.session_state.pop(
                    "roulette_result",
                    None,
                )

                st.session_state.pop(
                    "roulette_set_id",
                    None,
                )

                st.session_state[
                    "adopted_message"
                ] = result

                st.rerun()

        with col2:
            if st.button(
                "🔄 もう一回！",
                use_container_width=True,
            ):
                options = result_set.get(
                    "options",
                    [],
                )

                if options:
                    new_result = random.choice(
                        options
                    )

                    st.session_state[
                        "roulette_result"
                    ] = new_result

                    st.rerun()


# =========================================================
# 採用メッセージ
# =========================================================

adopted_message = (
    st.session_state.get(
        "adopted_message"
    )
)

if adopted_message:
    st.success(
        f"🎉 「{adopted_message}」に決定！"
    )

    if st.button(
        "OK",
        key="close_adopted",
    ):
        st.session_state.pop(
            "adopted_message",
            None,
        )

        st.rerun()


# =========================================================
# 新しいセット作成
# =========================================================

st.divider()

st.subheader(
    "➕ 新しいセットを作る"
)

with st.form(
    "add_set_form"
):
    set_name = st.text_input(
        "セット名",
        placeholder=(
            "例：今日なにする？"
        ),
    )

    st.caption(
        "候補は2〜8個まで。"
    )

    option_inputs = []

    for index in range(
        MAX_OPTIONS
    ):
        option = st.text_input(
            f"候補 {index + 1}",
            placeholder=(
                "例：AIの勉強"
                if index == 0
                else ""
            ),
            key=(
                f"new_option_{index}"
            ),
        )

        option_inputs.append(
            option
        )

    favorite = st.checkbox(
        "⭐ お気に入りにする"
    )

    submitted = (
        st.form_submit_button(
            "🎯 セットを保存",
            use_container_width=True,
        )
    )

    if submitted:
        cleaned_options = (
            clean_options(
                option_inputs
            )
        )

        if not set_name.strip():
            st.error(
                "セット名を入力してください。"
            )

        elif len(
            cleaned_options
        ) < MIN_OPTIONS:
            st.error(
                "候補を2個以上入力してください。"
            )

        elif len(
            cleaned_options
        ) > MAX_OPTIONS:
            st.error(
                "候補は8個までです。"
            )

        else:
            add_set(
                data,
                set_name.strip(),
                cleaned_options,
                favorite,
            )

            st.rerun()


# =========================================================
# セット一覧
# =========================================================

if roulette_sets:
    st.divider()

    st.subheader(
        "📦 保存したセット"
    )

    for roulette_set in sorted(
        roulette_sets,
        key=lambda item: (
            not item.get(
                "favorite",
                False,
            ),
            item.get(
                "name",
                "",
            ),
        ),
    ):
        set_id = roulette_set.get(
            "id",
            "",
        )

        favorite_mark = (
            "⭐"
            if roulette_set.get(
                "favorite",
                False,
            )
            else "🎯"
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### {favorite_mark} "
                f"{roulette_set.get('name', '')}"
            )

            st.caption(
                f"{len(roulette_set.get('options', []))}"
                f"個の候補"
            )

            for option in roulette_set.get(
                "options",
                [],
            ):
                st.write(
                    f"・{option}"
                )

            if st.button(
                (
                    "☆ お気に入りにする"
                    if not roulette_set.get(
                        "favorite",
                        False,
                    )
                    else "⭐ お気に入り解除"
                ),
                key=(
                    "favorite_"
                    + set_id
                ),
                use_container_width=True,
            ):
                toggle_favorite(
                    data,
                    set_id,
                )

                st.rerun()


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ セットを編集・削除"
):
    if not roulette_sets:
        st.caption(
            "まだセットがありません。"
        )

    else:
        for roulette_set in roulette_sets:
            set_id = roulette_set.get(
                "id",
                "",
            )

            st.markdown(
                f"### {roulette_set.get('name', '')}"
            )

            with st.expander(
                "✏️ 編集"
            ):
                edit_name = st.text_input(
                    "セット名",
                    value=roulette_set.get(
                        "name",
                        "",
                    ),
                    key=(
                        "edit_name_"
                        + set_id
                    ),
                )

                current_options = (
                    roulette_set.get(
                        "options",
                        [],
                    )
                )

                edit_option_inputs = []

                for index in range(
                    MAX_OPTIONS
                ):
                    current_value = (
                        current_options[
                            index
                        ]
                        if index
                        < len(
                            current_options
                        )
                        else ""
                    )

                    edit_option = (
                        st.text_input(
                            f"候補 {index + 1}",
                            value=current_value,
                            key=(
                                f"edit_option_"
                                f"{set_id}_"
                                f"{index}"
                            ),
                        )
                    )

                    edit_option_inputs.append(
                        edit_option
                    )

                edit_favorite = (
                    st.checkbox(
                        "⭐ お気に入り",
                        value=roulette_set.get(
                            "favorite",
                            False,
                        ),
                        key=(
                            "edit_favorite_"
                            + set_id
                        ),
                    )
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + set_id
                    ),
                    use_container_width=True,
                ):
                    cleaned_options = (
                        clean_options(
                            edit_option_inputs
                        )
                    )

                    if not edit_name.strip():
                        st.error(
                            "セット名を入力してください。"
                        )

                    elif len(
                        cleaned_options
                    ) < MIN_OPTIONS:
                        st.error(
                            "候補は2個以上必要です。"
                        )

                    else:
                        update_set(
                            data,
                            set_id,
                            edit_name.strip(),
                            cleaned_options,
                            edit_favorite,
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                st.warning(
                    "このセットを削除しても、"
                    "過去の決定履歴は残ります。"
                )

                if st.button(
                    "このセットを削除",
                    key=(
                        "delete_set_"
                        + set_id
                    ),
                    use_container_width=True,
                ):
                    delete_set(
                        data,
                        set_id,
                    )

                    if (
                        st.session_state.get(
                            "roulette_set_id"
                        )
                        == set_id
                    ):
                        st.session_state.pop(
                            "roulette_result",
                            None,
                        )

                        st.session_state.pop(
                            "roulette_set_id",
                            None,
                        )

                    st.rerun()

            st.divider()


# =========================================================
# 決定履歴
# =========================================================

st.divider()

st.subheader(
    "🕰️ 決定履歴"
)

if not history:
    st.info(
        "まだ採用した結果はありません。"
    )

else:
    history_sorted = sorted(
        history,
        key=lambda item: item.get(
            "decided_at",
            "",
        ),
        reverse=True,
    )

    for item in history_sorted[:20]:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 🎉 {item.get('result', '')}"
            )

            st.caption(
                f"🎯 {item.get('set_name', '')}"
                f" ｜ "
                f"{format_datetime(item.get('decided_at', ''))}"
            )

            if st.button(
                "🗑️ 履歴を削除",
                key=(
                    "delete_history_"
                    + item.get(
                        "id",
                        "",
                    )
                ),
            ):
                delete_history(
                    data,
                    item.get(
                        "id",
                        "",
                    ),
                )

                st.rerun()


# =========================================================
# よく選ばれた結果
# =========================================================

if history:
    st.divider()

    st.subheader(
        "📊 よく選ばれた結果"
    )

    history_df = pd.DataFrame(
        [
            {
                "セット": item.get(
                    "set_name",
                    "",
                ),
                "結果": item.get(
                    "result",
                    "",
                ),
            }
            for item in history
        ]
    )

    result_counts = (
        history_df[
            "結果"
        ]
        .value_counts()
        .reset_index()
    )

    result_counts.columns = [
        "結果",
        "回数",
    ]

    st.dataframe(
        result_counts,
        use_container_width=True,
        hide_index=True,
    )

    chart_df = (
        result_counts
        .set_index(
            "結果"
        )
    )

    st.bar_chart(
        chart_df,
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
            "decision_roulette_"
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
    "考えても決まらないなら、運に一票入れてみる。🎯✨"
)
