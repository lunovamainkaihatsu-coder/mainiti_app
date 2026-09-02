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
    page_title="今から10分なにする？",
    page_icon="⏱️",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "mission_data.json",
)

CATEGORIES = [
    "勉強",
    "AI・プログラミング",
    "イラスト",
    "仕事",
    "家事",
    "運動",
    "整理整頓",
    "趣味",
    "その他",
]

DURATIONS = [
    5,
    10,
    15,
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


def create_empty_data():
    return {
        "missions": [],
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
            "missions",
            [],
        )

        data.setdefault(
            "history",
            [],
        )

        for mission in data[
            "missions"
        ]:
            mission.setdefault(
                "id",
                create_id(),
            )

            mission.setdefault(
                "title",
                "",
            )

            mission.setdefault(
                "category",
                "その他",
            )

            mission.setdefault(
                "minutes",
                10,
            )

            mission.setdefault(
                "memo",
                "",
            )

            mission.setdefault(
                "active",
                True,
            )

            mission.setdefault(
                "created_at",
                "",
            )

            mission.setdefault(
                "updated_at",
                "",
            )

        for record in data[
            "history"
        ]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "mission_id",
                "",
            )

            record.setdefault(
                "title",
                "",
            )

            record.setdefault(
                "category",
                "その他",
            )

            record.setdefault(
                "minutes",
                10,
            )

            record.setdefault(
                "date",
                str(date.today()),
            )

            record.setdefault(
                "completed_at",
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

def get_mission_by_id(
    data,
    mission_id,
):
    return next(
        (
            mission
            for mission in data[
                "missions"
            ]
            if mission.get(
                "id"
            )
            == mission_id
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

    except (
        ValueError,
        TypeError,
    ):
        return date_text


def start_of_week():
    today = date.today()

    return (
        today
        - timedelta(
            days=today.weekday()
        )
    )


# =========================================================
# データ操作
# =========================================================

def add_mission(
    data,
    title,
    category,
    minutes,
    memo,
):
    data["missions"].append(
        {
            "id": create_id(),
            "title": title,
            "category": category,
            "minutes": int(
                minutes
            ),
            "memo": memo,
            "active": True,
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def update_mission(
    data,
    mission_id,
    title,
    category,
    minutes,
    memo,
    active,
):
    mission = get_mission_by_id(
        data,
        mission_id,
    )

    if not mission:
        return

    mission["title"] = title
    mission["category"] = category
    mission["minutes"] = int(
        minutes
    )
    mission["memo"] = memo
    mission["active"] = active
    mission["updated_at"] = now_text()

    save_data(data)


def delete_mission(
    data,
    mission_id,
):
    data["missions"] = [
        mission
        for mission in data[
            "missions"
        ]
        if mission.get(
            "id"
        )
        != mission_id
    ]

    save_data(data)


def complete_mission(
    data,
    mission,
):
    data["history"].append(
        {
            "id": create_id(),
            "mission_id": mission.get(
                "id",
                "",
            ),
            "title": mission.get(
                "title",
                "",
            ),
            "category": mission.get(
                "category",
                "その他",
            ),
            "minutes": mission.get(
                "minutes",
                10,
            ),
            "date": str(
                date.today()
            ),
            "completed_at": now_text(),
        }
    )

    save_data(data)


def delete_history_record(
    data,
    record_id,
):
    data["history"] = [
        record
        for record in data[
            "history"
        ]
        if record.get(
            "id"
        )
        != record_id
    ]

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
        background: rgba(90, 150, 255, 0.07);
        border: 1px solid rgba(90, 150, 255, 0.15);
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
                rgba(90, 150, 255, 0.17),
                rgba(110, 210, 170, 0.10)
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

    .mission-box {
        padding: 28px;
        border-radius: 20px;
        text-align: center;
        background: rgba(90, 150, 255, 0.07);
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .mission-title {
        font-size: 1.45rem;
        font-weight: 800;
        line-height: 1.6;
    }

    .minute-badge {
        margin-top: 12px;
        font-size: 1.05rem;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

missions = data[
    "missions"
]

history = data[
    "history"
]

active_missions = [
    mission
    for mission in missions
    if mission.get(
        "active",
        True,
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⏱️ 今から10分なにする？</h1>

        <p>
            迷ったら、短いミッションを1個だけ。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

today_text = str(
    date.today()
)

week_start_text = str(
    start_of_week()
)

today_history = [
    record
    for record in history
    if record.get(
        "date"
    )
    == today_text
]

week_history = [
    record
    for record in history
    if record.get(
        "date",
        "",
    )
    >= week_start_text
]

today_minutes = sum(
    int(
        record.get(
            "minutes",
            0,
        )
    )
    for record in today_history
)

columns = st.columns(
    4
)

columns[0].metric(
    "候補",
    f"{len(active_missions)}個",
)

columns[1].metric(
    "今日",
    f"{len(today_history)}回",
)

columns[2].metric(
    "今週",
    f"{len(week_history)}回",
)

columns[3].metric(
    "今日の時間",
    f"{today_minutes}分",
)


# =========================================================
# ミッション抽選
# =========================================================

st.divider()

st.subheader(
    "🎲 今なにする？"
)

if not active_missions:
    st.info(
        "まずは下からミッション候補を登録してみよう！"
    )

else:
    selected_minutes = st.radio(
        "今使える時間",
        [
            "全部",
            "5分",
            "10分",
            "15分",
        ],
        horizontal=True,
    )

    if selected_minutes == "全部":
        filtered_missions = (
            active_missions
        )
    else:
        minute_value = int(
            selected_minutes.replace(
                "分",
                "",
            )
        )

        filtered_missions = [
            mission
            for mission in active_missions
            if int(
                mission.get(
                    "minutes",
                    10,
                )
            )
            == minute_value
        ]

    if not filtered_missions:
        st.warning(
            "この時間の候補がまだありません。"
        )

    else:
        valid_ids = {
            mission.get(
                "id"
            )
            for mission
            in filtered_missions
        }

        if (
            "picked_mission_id"
            not in st.session_state
            or st.session_state[
                "picked_mission_id"
            ]
            not in valid_ids
        ):
            st.session_state[
                "picked_mission_id"
            ] = random.choice(
                filtered_missions
            ).get(
                "id"
            )

        picked_mission = next(
            (
                mission
                for mission
                in filtered_missions
                if mission.get(
                    "id"
                )
                == st.session_state[
                    "picked_mission_id"
                ]
            ),
            random.choice(
                filtered_missions
            ),
        )

        st.markdown(
            f"""
            <div class="mission-box">

                <div class="mission-title">
                    🎯 {picked_mission.get('title', '')}
                </div>

                <div class="minute-badge">
                    ⏱️ {picked_mission.get('minutes', 10)}分
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            f"{picked_mission.get('category', '')}"
        )

        if picked_mission.get(
            "memo",
            "",
        ):
            st.write(
                f"💬 "
                f"{picked_mission.get('memo', '')}"
            )

        col1, col2, col3 = st.columns(
            3
        )

        with col1:
            if st.button(
                "▶ やる！",
                use_container_width=True,
            ):
                st.session_state[
                    "doing_mission_id"
                ] = picked_mission.get(
                    "id"
                )

                st.success(
                    "よし、スタート！"
                )

        with col2:
            if st.button(
                "🔄 別の候補",
                use_container_width=True,
            ):
                candidates = [
                    mission
                    for mission
                    in filtered_missions
                    if mission.get(
                        "id"
                    )
                    != picked_mission.get(
                        "id"
                    )
                ]

                if candidates:
                    st.session_state[
                        "picked_mission_id"
                    ] = random.choice(
                        candidates
                    ).get(
                        "id"
                    )

                st.rerun()

        with col3:
            if st.button(
                "⏭ パス",
                use_container_width=True,
            ):
                candidates = [
                    mission
                    for mission
                    in filtered_missions
                    if mission.get(
                        "id"
                    )
                    != picked_mission.get(
                        "id"
                    )
                ]

                if candidates:
                    st.session_state[
                        "picked_mission_id"
                    ] = random.choice(
                        candidates
                    ).get(
                        "id"
                    )

                st.rerun()


# =========================================================
# 実行中ミッション
# =========================================================

doing_id = st.session_state.get(
    "doing_mission_id"
)

if doing_id:
    doing_mission = (
        get_mission_by_id(
            data,
            doing_id,
        )
    )

    if doing_mission:
        st.divider()

        st.subheader(
            "🔥 今これをやる"
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### 🎯 "
                f"{doing_mission.get('title', '')}"
            )

            st.write(
                f"⏱️ "
                f"{doing_mission.get('minutes', 10)}分"
            )

            if doing_mission.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{doing_mission.get('memo', '')}"
                )

            col1, col2 = st.columns(
                2
            )

            with col1:
                if st.button(
                    "✅ できた！",
                    use_container_width=True,
                ):
                    complete_mission(
                        data,
                        doing_mission,
                    )

                    st.session_state.pop(
                        "doing_mission_id",
                        None,
                    )

                    st.session_state.pop(
                        "picked_mission_id",
                        None,
                    )

                    st.rerun()

            with col2:
                if st.button(
                    "↩ やめる",
                    use_container_width=True,
                ):
                    st.session_state.pop(
                        "doing_mission_id",
                        None,
                    )

                    st.rerun()


# =========================================================
# 今日の達成
# =========================================================

if today_history:
    st.divider()

    st.subheader(
        "✨ 今日できたこと"
    )

    for record in reversed(
        today_history
    ):
        with st.container(
            border=True,
        ):
            st.markdown(
                f"✅ "
                f"**{record.get('title', '')}**"
            )

            st.caption(
                f"{record.get('category', '')}"
                f" ／ "
                f"{record.get('minutes', 10)}分"
            )


# =========================================================
# 新しい候補
# =========================================================

st.divider()

st.subheader(
    "➕ 10分候補を追加"
)

with st.form(
    "add_mission_form"
):
    title = st.text_input(
        "何をする？",
        placeholder=(
            "例：AIのコードを1か所読む"
        ),
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    minutes = st.selectbox(
        "目安時間",
        DURATIONS,
        index=1,
        format_func=lambda value: (
            f"{value}分"
        ),
    )

    memo = st.text_input(
        "ひとことメモ",
        placeholder=(
            "例：全部理解しなくてOK"
        ),
    )

    submitted = (
        st.form_submit_button(
            "➕ 候補に追加",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.error(
                "やることを入力してください。"
            )

        else:
            add_mission(
                data,
                title.strip(),
                category,
                minutes,
                memo.strip(),
            )

            st.success(
                "候補を追加しました！"
            )

            st.rerun()


# =========================================================
# カテゴリー別集計
# =========================================================

if history:
    st.divider()

    st.subheader(
        "📊 何をよくやってる？"
    )

    category_rows = []

    for category_name in CATEGORIES:
        count = len(
            [
                record
                for record in history
                if record.get(
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
                    "達成回数": count,
                }
            )

    if category_rows:
        category_df = pd.DataFrame(
            category_rows
        ).sort_values(
            "達成回数",
            ascending=False,
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 候補管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ ミッション候補を管理"
):
    if not missions:
        st.info(
            "まだ候補がありません。"
        )

    else:
        sorted_missions = sorted(
            missions,
            key=lambda mission: (
                mission.get(
                    "created_at",
                    "",
                )
            ),
            reverse=True,
        )

        for mission in sorted_missions:
            mission_id = mission.get(
                "id",
                "",
            )

            with st.container(
                border=True,
            ):
                active_text = (
                    "🟢 使用中"
                    if mission.get(
                        "active",
                        True,
                    )
                    else "⚪ お休み"
                )

                st.markdown(
                    f"### "
                    f"{mission.get('title', '')}"
                )

                st.caption(
                    f"{active_text}"
                    f" ／ "
                    f"{mission.get('category', '')}"
                    f" ／ "
                    f"{mission.get('minutes', 10)}分"
                )

                if mission.get(
                    "memo",
                    "",
                ):
                    st.write(
                        f"💬 "
                        f"{mission.get('memo', '')}"
                    )

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = st.text_input(
                        "やること",
                        value=mission.get(
                            "title",
                            "",
                        ),
                        key=(
                            f"edit_title_"
                            f"{mission_id}"
                        ),
                    )

                    current_category = (
                        mission.get(
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
                                else 0
                            ),
                            key=(
                                f"edit_category_"
                                f"{mission_id}"
                            ),
                        )
                    )

                    current_minutes = int(
                        mission.get(
                            "minutes",
                            10,
                        )
                    )

                    edit_minutes = (
                        st.selectbox(
                            "目安時間",
                            DURATIONS,
                            index=(
                                DURATIONS.index(
                                    current_minutes
                                )
                                if current_minutes
                                in DURATIONS
                                else 1
                            ),
                            format_func=lambda value: (
                                f"{value}分"
                            ),
                            key=(
                                f"edit_minutes_"
                                f"{mission_id}"
                            ),
                        )
                    )

                    edit_memo = st.text_input(
                        "メモ",
                        value=mission.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_memo_"
                            f"{mission_id}"
                        ),
                    )

                    edit_active = st.checkbox(
                        "抽選候補に入れる",
                        value=mission.get(
                            "active",
                            True,
                        ),
                        key=(
                            f"edit_active_"
                            f"{mission_id}"
                        ),
                    )

                    if st.button(
                        "💾 変更を保存",
                        key=(
                            f"save_edit_"
                            f"{mission_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_title.strip():
                            st.error(
                                "やることを入力してください。"
                            )

                        else:
                            update_mission(
                                data,
                                mission_id,
                                edit_title.strip(),
                                edit_category,
                                edit_minutes,
                                edit_memo.strip(),
                                edit_active,
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 削除"
                ):
                    if st.button(
                        "この候補を削除",
                        key=(
                            f"delete_mission_"
                            f"{mission_id}"
                        ),
                        use_container_width=True,
                    ):
                        delete_mission(
                            data,
                            mission_id,
                        )

                        if (
                            st.session_state.get(
                                "picked_mission_id"
                            )
                            == mission_id
                        ):
                            st.session_state.pop(
                                "picked_mission_id",
                                None,
                            )

                        if (
                            st.session_state.get(
                                "doing_mission_id"
                            )
                            == mission_id
                        ):
                            st.session_state.pop(
                                "doing_mission_id",
                                None,
                            )

                        st.rerun()


# =========================================================
# 達成履歴
# =========================================================

st.divider()

with st.expander(
    "📚 達成履歴"
):
    if not history:
        st.caption(
            "まだ達成記録がありません。"
        )

    else:
        sorted_history = sorted(
            history,
            key=lambda record: (
                record.get(
                    "completed_at",
                    "",
                )
            ),
            reverse=True,
        )

        rows = []

        for record in sorted_history:
            rows.append(
                {
                    "日付": record.get(
                        "date",
                        "",
                    ),
                    "内容": record.get(
                        "title",
                        "",
                    ),
                    "カテゴリー": record.get(
                        "category",
                        "",
                    ),
                    "時間": (
                        f"{record.get('minutes', 10)}分"
                    ),
                }
            )

        history_df = pd.DataFrame(
            rows
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            "#### 🗑️ 履歴を削除"
        )

        for record in sorted_history:
            record_id = record.get(
                "id",
                "",
            )

            col1, col2 = st.columns(
                [4, 1]
            )

            with col1:
                st.write(
                    f"✅ {record.get('date', '')} "
                    f"{record.get('title', '')}"
                )

            with col2:
                if st.button(
                    "削除",
                    key=(
                        f"delete_history_"
                        f"{record_id}"
                    ),
                ):
                    delete_history_record(
                        data,
                        record_id,
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
            f"mission_backup_"
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
    "10分あれば、少しだけ前に進める。⏱️✨"
)
