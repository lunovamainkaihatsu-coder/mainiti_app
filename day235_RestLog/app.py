import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日は休んだ？",
    page_icon="☕",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "rest_data.json",
)

REST_TYPES = [
    "☕ のんびり",
    "😴 昼寝",
    "🚶 散歩",
    "🛀 お風呂",
    "🎮 趣味",
    "📱 ぼーっとした",
    "🌿 その他",
]

REST_LEVELS = [
    "😫 あまり休めなかった",
    "🙂 少し休めた",
    "😌 しっかり休めた",
]

REST_SCORES = {
    "😫 あまり休めなかった": 1,
    "🙂 少し休めた": 2,
    "😌 しっかり休めた": 3,
}


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
        "records": []
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
            "records",
            [],
        )

        for record in data[
            "records"
        ]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "date",
                str(
                    date.today()
                ),
            )

            record.setdefault(
                "rest_type",
                "☕ のんびり",
            )

            record.setdefault(
                "minutes",
                0,
            )

            record.setdefault(
                "rest_level",
                "🙂 少し休めた",
            )

            record.setdefault(
                "comment",
                "",
            )

            record.setdefault(
                "created_at",
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

def format_date(
    date_text,
):
    try:
        target_date = (
            datetime.strptime(
                date_text,
                "%Y-%m-%d",
            ).date()
        )

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
            target_date.weekday()
        ]

        return target_date.strftime(
            f"%Y年%m月%d日（{weekday}）"
        )

    except ValueError:
        return date_text


def get_record_by_id(
    data,
    record_id,
):
    for record in data[
        "records"
    ]:
        if record.get(
            "id"
        ) == record_id:
            return record

    return None


# =========================================================
# データ操作
# =========================================================

def add_record(
    data,
    rest_type,
    minutes,
    rest_level,
    comment,
):
    record = {
        "id": create_id(),
        "date": str(
            date.today()
        ),
        "rest_type": (
            rest_type
        ),
        "minutes": int(
            minutes
        ),
        "rest_level": (
            rest_level
        ),
        "comment": (
            comment
        ),
        "created_at": (
            now_text()
        ),
    }

    data[
        "records"
    ].append(
        record
    )

    save_data(
        data
    )


def update_record(
    data,
    record_id,
    rest_type,
    minutes,
    rest_level,
    comment,
):
    record = (
        get_record_by_id(
            data,
            record_id,
        )
    )

    if not record:
        return

    record[
        "rest_type"
    ] = rest_type

    record[
        "minutes"
    ] = int(
        minutes
    )

    record[
        "rest_level"
    ] = rest_level

    record[
        "comment"
    ] = comment

    save_data(
        data
    )


def delete_record(
    data,
    record_id,
):
    data[
        "records"
    ] = [
        record
        for record
        in data[
            "records"
        ]
        if record.get(
            "id"
        )
        != record_id
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
        background: rgba(100, 180, 150, 0.08);
        border: 1px solid rgba(100, 180, 150, 0.18);
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
                rgba(100, 180, 150, 0.18),
                rgba(120, 170, 255, 0.10)
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

records = data[
    "records"
]

today = date.today()

today_text = str(
    today
)

week_start = (
    today
    - timedelta(
        days=6
    )
)

current_month = today.strftime(
    "%Y-%m"
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>☕ 今日は休んだ？</h1>
        <p>
            休息もちゃんと記録する、
            シンプルな休み時間ログ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

today_records = [
    record
    for record in records
    if record.get(
        "date"
    )
    == today_text
]


weekly_records = []

for record in records:
    try:
        record_date = (
            datetime.strptime(
                record.get(
                    "date",
                    "",
                ),
                "%Y-%m-%d",
            ).date()
        )

        if (
            week_start
            <= record_date
            <= today
        ):
            weekly_records.append(
                record
            )

    except ValueError:
        pass


monthly_records = [
    record
    for record in records
    if record.get(
        "date",
        "",
    ).startswith(
        current_month
    )
]


today_minutes = sum(
    int(
        record.get(
            "minutes",
            0,
        )
    )
    for record in today_records
)


weekly_minutes = sum(
    int(
        record.get(
            "minutes",
            0,
        )
    )
    for record in weekly_records
)


monthly_minutes = sum(
    int(
        record.get(
            "minutes",
            0,
        )
    )
    for record in monthly_records
)


# =========================================================
# ダッシュボード
# =========================================================

columns = st.columns(
    3
)

columns[0].metric(
    "今日の休息",
    f"{today_minutes}分",
)

columns[1].metric(
    "今週の休息",
    f"{weekly_minutes}分",
)

columns[2].metric(
    "今月の休息",
    f"{monthly_minutes}分",
)


# =========================================================
# 入力
# =========================================================

st.divider()

st.subheader(
    "🌿 休息を記録"
)

with st.form(
    "rest_form",
    clear_on_submit=True,
):
    rest_type = st.selectbox(
        "どんな休み方をした？",
        REST_TYPES,
    )

    minutes = st.number_input(
        "何分くらい休んだ？",
        min_value=0,
        max_value=1440,
        value=30,
        step=5,
    )

    rest_level = st.selectbox(
        "どれくらい休めた？",
        REST_LEVELS,
        index=1,
    )

    comment = st.text_input(
        "ひとこと",
        placeholder=(
            "例：仕事のあと何もせずゆっくりした"
        ),
    )

    submitted = (
        st.form_submit_button(
            "☕ 休息を記録",
            use_container_width=True,
        )
    )

    if submitted:
        add_record(
            data,
            rest_type,
            minutes,
            rest_level,
            comment.strip(),
        )

        st.success(
            "休息を記録しました！"
        )

        st.rerun()


# =========================================================
# 今日の休息
# =========================================================

st.divider()

st.subheader(
    "✨ 今日の休息"
)

if not today_records:
    st.info(
        "今日はまだ休息を記録していません。"
    )

else:
    today_records = sorted(
        today_records,
        key=lambda record: (
            record.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )

    for record in today_records:
        record_id = record[
            "id"
        ]

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### "
                f"{record.get('rest_type', '')}"
            )

            st.write(
                f"**{record.get('minutes', 0)}分**"
            )

            st.write(
                record.get(
                    "rest_level",
                    "",
                )
            )

            if record.get(
                "comment",
                "",
            ):
                st.write(
                    f"「"
                    f"{record.get('comment', '')}"
                    f"」"
                )

            with st.expander(
                "✏️ 編集"
            ):
                current_type = (
                    record.get(
                        "rest_type",
                        "☕ のんびり",
                    )
                )

                edit_type = (
                    st.selectbox(
                        "休息タイプ",
                        REST_TYPES,
                        index=(
                            REST_TYPES.index(
                                current_type
                            )
                            if current_type
                            in REST_TYPES
                            else 0
                        ),
                        key=(
                            f"type_"
                            f"{record_id}"
                        ),
                    )
                )

                edit_minutes = (
                    st.number_input(
                        "休息時間",
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
                            f"minutes_"
                            f"{record_id}"
                        ),
                    )
                )

                current_level = (
                    record.get(
                        "rest_level",
                        "🙂 少し休めた",
                    )
                )

                edit_level = (
                    st.selectbox(
                        "休めた感覚",
                        REST_LEVELS,
                        index=(
                            REST_LEVELS.index(
                                current_level
                            )
                            if current_level
                            in REST_LEVELS
                            else 1
                        ),
                        key=(
                            f"level_"
                            f"{record_id}"
                        ),
                    )
                )

                edit_comment = (
                    st.text_input(
                        "ひとこと",
                        value=record.get(
                            "comment",
                            "",
                        ),
                        key=(
                            f"comment_"
                            f"{record_id}"
                        ),
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_"
                        f"{record_id}"
                    ),
                    use_container_width=True,
                ):
                    update_record(
                        data,
                        record_id,
                        edit_type,
                        edit_minutes,
                        edit_level,
                        edit_comment.strip(),
                    )

                    st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この記録を削除",
                    key=(
                        f"delete_"
                        f"{record_id}"
                    ),
                    use_container_width=True,
                ):
                    delete_record(
                        data,
                        record_id,
                    )

                    st.rerun()

    st.metric(
        "今日の合計休息",
        f"{today_minutes}分",
    )


# =========================================================
# 最近7日間
# =========================================================

st.divider()

st.subheader(
    "📊 最近7日間"
)

daily_rows = []

for i in range(
    7
):
    target_date = (
        week_start
        + timedelta(
            days=i
        )
    )

    target_records = [
        record
        for record in records
        if record.get(
            "date"
        )
        == str(
            target_date
        )
    ]

    total_minutes = sum(
        int(
            record.get(
                "minutes",
                0,
            )
        )
        for record in target_records
    )

    daily_rows.append(
        {
            "日付": target_date.strftime(
                "%m/%d"
            ),
            "休息時間": total_minutes,
        }
    )


daily_df = pd.DataFrame(
    daily_rows
).set_index(
    "日付"
)

st.bar_chart(
    daily_df
)


# =========================================================
# 休めた感覚
# =========================================================

st.divider()

st.subheader(
    "😌 今週どれくらい休めた？"
)

if not weekly_records:
    st.info(
        "今週の記録はまだありません。"
    )

else:
    level_rows = []

    for rest_level in REST_LEVELS:
        count = len(
            [
                record
                for record
                in weekly_records
                if record.get(
                    "rest_level"
                )
                == rest_level
            ]
        )

        if count > 0:
            level_rows.append(
                {
                    "休めた感覚": (
                        rest_level
                    ),
                    "回数": count,
                }
            )

    level_df = pd.DataFrame(
        level_rows
    )

    st.dataframe(
        level_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 休息タイプ別
# =========================================================

st.divider()

st.subheader(
    "🌿 今月の休み方"
)

if not monthly_records:
    st.info(
        "今月の記録はありません。"
    )

else:
    type_rows = []

    for rest_type in REST_TYPES:
        type_records = [
            record
            for record
            in monthly_records
            if record.get(
                "rest_type"
            )
            == rest_type
        ]

        if type_records:
            total_minutes = sum(
                int(
                    record.get(
                        "minutes",
                        0,
                    )
                )
                for record
                in type_records
            )

            type_rows.append(
                {
                    "休息タイプ": (
                        rest_type
                    ),
                    "回数": len(
                        type_records
                    ),
                    "合計時間": (
                        total_minutes
                    ),
                }
            )

    type_df = pd.DataFrame(
        type_rows
    )

    type_df = (
        type_df.sort_values(
            "合計時間",
            ascending=False,
        )
    )

    st.bar_chart(
        type_df.set_index(
            "休息タイプ"
        )[["合計時間"]]
    )

    st.dataframe(
        type_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 過去履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の休息を見る"
):
    if not records:
        st.info(
            "休息履歴はありません。"
        )

    else:
        sorted_records = sorted(
            records,
            key=lambda record: (
                record.get(
                    "date",
                    "",
                ),
                record.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        history_rows = []

        for record in sorted_records:
            history_rows.append(
                {
                    "日付": (
                        format_date(
                            record.get(
                                "date",
                                "",
                            )
                        )
                    ),
                    "休息": (
                        record.get(
                            "rest_type",
                            "",
                        )
                    ),
                    "時間": (
                        int(
                            record.get(
                                "minutes",
                                0,
                            )
                        )
                    ),
                    "休めた感覚": (
                        record.get(
                            "rest_level",
                            "",
                        )
                    ),
                    "ひとこと": (
                        record.get(
                            "comment",
                            "",
                        )
                    ),
                }
            )

        history_df = pd.DataFrame(
            history_rows
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
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
        file_name=(
            f"rest_backup_"
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
    "何もしない時間も、ちゃんと今日の一部。☕🌿"
)
