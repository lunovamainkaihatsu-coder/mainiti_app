import json
import os
import uuid
from datetime import datetime

import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="あと何回？",
    page_icon="🔢",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "counter_data.json",
)

ICONS = [
    "💪",
    "📚",
    "🏃",
    "🧹",
    "💧",
    "🧘",
    "💻",
    "✏️",
    "⭐",
    "🎯",
]


# =========================================================
# データ管理
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
        "counters": []
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
            "counters",
            [],
        )

        for counter in data[
            "counters"
        ]:
            counter.setdefault(
                "id",
                create_id(),
            )

            counter.setdefault(
                "name",
                "カウンター",
            )

            counter.setdefault(
                "icon",
                "🎯",
            )

            counter.setdefault(
                "goal",
                10,
            )

            counter.setdefault(
                "count",
                0,
            )

            counter.setdefault(
                "created_at",
                now_text(),
            )

            counter.setdefault(
                "updated_at",
                now_text(),
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

def get_counter(
    data,
    counter_id,
):
    for counter in data[
        "counters"
    ]:
        if counter.get(
            "id"
        ) == counter_id:
            return counter

    return None


def get_percentage(
    count,
    goal,
):
    if goal <= 0:
        return 0

    return min(
        count / goal,
        1.0,
    )


def get_remaining(
    count,
    goal,
):
    return max(
        goal - count,
        0,
    )


# =========================================================
# データ操作
# =========================================================

def add_counter(
    data,
    name,
    icon,
    goal,
):
    counter = {
        "id": create_id(),
        "name": name,
        "icon": icon,
        "goal": int(
            goal
        ),
        "count": 0,
        "created_at": (
            now_text()
        ),
        "updated_at": (
            now_text()
        ),
    }

    data[
        "counters"
    ].append(
        counter
    )

    save_data(
        data
    )


def change_count(
    data,
    counter_id,
    amount,
):
    counter = get_counter(
        data,
        counter_id,
    )

    if not counter:
        return

    new_count = (
        int(
            counter.get(
                "count",
                0,
            )
        )
        + amount
    )

    counter[
        "count"
    ] = max(
        new_count,
        0,
    )

    counter[
        "updated_at"
    ] = now_text()

    save_data(
        data
    )


def reset_counter(
    data,
    counter_id,
):
    counter = get_counter(
        data,
        counter_id,
    )

    if not counter:
        return

    counter[
        "count"
    ] = 0

    counter[
        "updated_at"
    ] = now_text()

    save_data(
        data
    )


def update_counter(
    data,
    counter_id,
    name,
    icon,
    goal,
):
    counter = get_counter(
        data,
        counter_id,
    )

    if not counter:
        return

    counter[
        "name"
    ] = name

    counter[
        "icon"
    ] = icon

    counter[
        "goal"
    ] = int(
        goal
    )

    counter[
        "updated_at"
    ] = now_text()

    save_data(
        data
    )


def delete_counter(
    data,
    counter_id,
):
    data[
        "counters"
    ] = [
        counter
        for counter
        in data[
            "counters"
        ]
        if counter.get(
            "id"
        )
        != counter_id
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
        background: rgba(100, 150, 255, 0.08);
        border: 1px solid rgba(100, 150, 255, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 22px;
        border-radius: 20px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 150, 255, 0.18),
                rgba(160, 100, 255, 0.10)
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

    .counter-number {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .remaining {
        text-align: center;
        font-size: 1.1rem;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .complete {
        text-align: center;
        font-size: 1.3rem;
        font-weight: bold;
        padding: 12px;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

counters = data[
    "counters"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🔢 あと何回？</h1>
        <p>
            目標を決めて、
            やったら＋1するだけ。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 全体集計
# =========================================================

total_counters = len(
    counters
)

completed_counters = len(
    [
        counter
        for counter in counters
        if int(
            counter.get(
                "count",
                0,
            )
        )
        >= int(
            counter.get(
                "goal",
                1,
            )
        )
    ]
)

total_count = sum(
    int(
        counter.get(
            "count",
            0,
        )
    )
    for counter in counters
)


columns = st.columns(
    3
)

columns[0].metric(
    "目標",
    f"{total_counters}個",
)

columns[1].metric(
    "達成",
    f"{completed_counters}個",
)

columns[2].metric(
    "合計カウント",
    f"{total_count}回",
)


# =========================================================
# 新しいカウンター
# =========================================================

st.divider()

st.subheader(
    "➕ 新しい目標"
)

with st.form(
    "new_counter_form",
    clear_on_submit=True,
):
    name = st.text_input(
        "何を数える？",
        placeholder=(
            "例：懸垂"
        ),
    )

    icon = st.selectbox(
        "アイコン",
        ICONS,
    )

    goal = st.number_input(
        "目標回数",
        min_value=1,
        max_value=100000,
        value=30,
        step=1,
    )

    submitted = (
        st.form_submit_button(
            "🎯 目標を作る",
            use_container_width=True,
        )
    )

    if submitted:
        if not name.strip():
            st.error(
                "目標名を入力してください。"
            )

        else:
            add_counter(
                data,
                name.strip(),
                icon,
                goal,
            )

            st.success(
                "新しい目標を作りました！"
            )

            st.rerun()


# =========================================================
# カウンター一覧
# =========================================================

st.divider()

st.subheader(
    "🎯 マイカウンター"
)

if not counters:
    st.info(
        "まだカウンターがありません。"
        "最初の目標を作ってみよう！"
    )

else:
    sorted_counters = sorted(
        counters,
        key=lambda counter: (
            counter.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    )

    for counter in sorted_counters:
        counter_id = counter[
            "id"
        ]

        name = counter.get(
            "name",
            "カウンター",
        )

        icon = counter.get(
            "icon",
            "🎯",
        )

        goal = int(
            counter.get(
                "goal",
                1,
            )
        )

        count = int(
            counter.get(
                "count",
                0,
            )
        )

        remaining = get_remaining(
            count,
            goal,
        )

        percentage = get_percentage(
            count,
            goal,
        )

        percent_number = int(
            percentage
            * 100
        )

        completed = (
            count >= goal
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"## {icon} {name}"
            )

            st.markdown(
                f"""
                <div class="counter-number">
                    {count} / {goal}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.progress(
                percentage
            )

            st.caption(
                f"達成率 {percent_number}%"
            )

            if completed:
                st.markdown(
                    """
                    <div class="complete">
                        🎉 目標達成！
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:
                st.markdown(
                    f"""
                    <div class="remaining">
                        あと <strong>{remaining}回</strong>！
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ---------------------------------------------
            # カウントボタン
            # ---------------------------------------------

            button_columns = (
                st.columns(
                    [
                        1,
                        2,
                        1,
                    ]
                )
            )

            with button_columns[0]:
                if st.button(
                    "−1",
                    key=(
                        f"minus_"
                        f"{counter_id}"
                    ),
                    use_container_width=True,
                ):
                    change_count(
                        data,
                        counter_id,
                        -1,
                    )

                    st.rerun()

            with button_columns[1]:
                if st.button(
                    "＋1",
                    key=(
                        f"plus_"
                        f"{counter_id}"
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    change_count(
                        data,
                        counter_id,
                        1,
                    )

                    st.rerun()

            with button_columns[2]:
                if st.button(
                    "＋5",
                    key=(
                        f"plus5_"
                        f"{counter_id}"
                    ),
                    use_container_width=True,
                ):
                    change_count(
                        data,
                        counter_id,
                        5,
                    )

                    st.rerun()

            # ---------------------------------------------
            # 編集
            # ---------------------------------------------

            with st.expander(
                "⚙️ 設定"
            ):
                current_icon = (
                    counter.get(
                        "icon",
                        "🎯",
                    )
                )

                edit_icon = (
                    st.selectbox(
                        "アイコン",
                        ICONS,
                        index=(
                            ICONS.index(
                                current_icon
                            )
                            if current_icon
                            in ICONS
                            else 0
                        ),
                        key=(
                            f"icon_"
                            f"{counter_id}"
                        ),
                    )
                )

                edit_name = (
                    st.text_input(
                        "目標名",
                        value=name,
                        key=(
                            f"name_"
                            f"{counter_id}"
                        ),
                    )
                )

                edit_goal = (
                    st.number_input(
                        "目標回数",
                        min_value=1,
                        max_value=100000,
                        value=goal,
                        step=1,
                        key=(
                            f"goal_"
                            f"{counter_id}"
                        ),
                    )
                )

                if st.button(
                    "💾 設定を保存",
                    key=(
                        f"save_"
                        f"{counter_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_name.strip():
                        st.error(
                            "目標名を入力してください。"
                        )

                    else:
                        update_counter(
                            data,
                            counter_id,
                            edit_name.strip(),
                            edit_icon,
                            edit_goal,
                        )

                        st.rerun()

            # ---------------------------------------------
            # リセット
            # ---------------------------------------------

            with st.expander(
                "🔄 カウントをリセット"
            ):
                st.warning(
                    "現在のカウントを0に戻します。"
                )

                if st.button(
                    "0に戻す",
                    key=(
                        f"reset_"
                        f"{counter_id}"
                    ),
                    use_container_width=True,
                ):
                    reset_counter(
                        data,
                        counter_id,
                    )

                    st.rerun()

            # ---------------------------------------------
            # 削除
            # ---------------------------------------------

            with st.expander(
                "🗑️ 削除"
            ):
                st.warning(
                    "このカウンターを削除します。"
                )

                if st.button(
                    "削除する",
                    key=(
                        f"delete_"
                        f"{counter_id}"
                    ),
                    use_container_width=True,
                ):
                    delete_counter(
                        data,
                        counter_id,
                    )

                    st.rerun()


# =========================================================
# 達成済み一覧
# =========================================================

completed = [
    counter
    for counter in counters
    if int(
        counter.get(
            "count",
            0,
        )
    )
    >= int(
        counter.get(
            "goal",
            1,
        )
    )
]

if completed:
    st.divider()

    st.subheader(
        "🏆 達成した目標"
    )

    for counter in completed:
        st.success(
            f"{counter.get('icon', '🎯')} "
            f"{counter.get('name', '')} "
            f"— "
            f"{counter.get('count', 0)}"
            f"/"
            f"{counter.get('goal', 0)}回"
        )


# =========================================================
# バックアップ
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
        file_name="counter_backup.json",
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "あと何回？を、ひとつずつ減らしていこう。🔢"
)
