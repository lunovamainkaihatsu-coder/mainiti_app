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
    page_title="何食べた？",
    page_icon="🍚",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "meal_data.json",
)

MEAL_TYPES = [
    "🌅 朝食",
    "☀️ 昼食",
    "🌙 夕食",
    "🍪 間食",
    "🥤 飲み物",
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
        save_data(data)
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
                "meal_type",
                "☀️ 昼食",
            )

            record.setdefault(
                "food",
                "",
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
        save_data(data)
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
    meal_type,
    food,
    comment,
):
    record = {
        "id": create_id(),
        "date": str(
            date.today()
        ),
        "meal_type": (
            meal_type
        ),
        "food": food,
        "comment": comment,
        "created_at": now_text(),
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
    meal_type,
    food,
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
        "meal_type"
    ] = meal_type

    record[
        "food"
    ] = food

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
        background: rgba(255, 170, 90, 0.08);
        border: 1px solid rgba(255, 170, 90, 0.18);
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
                rgba(255, 170, 90, 0.18),
                rgba(255, 220, 120, 0.11)
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

current_month = (
    today.strftime(
        "%Y-%m"
    )
)

week_start = (
    today
    - timedelta(
        days=6
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🍚 何食べた？</h1>
        <p>
            カロリー計算なし。
            食べたものを一言だけ残すミニ食事メモ
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


# =========================================================
# ダッシュボード
# =========================================================

columns = st.columns(
    3
)

columns[0].metric(
    "今日",
    f"{len(today_records)}件",
)

columns[1].metric(
    "今週",
    f"{len(weekly_records)}件",
)

columns[2].metric(
    "今月",
    f"{len(monthly_records)}件",
)


# =========================================================
# 入力
# =========================================================

st.divider()

st.subheader(
    "➕ 食べたものを記録"
)

with st.form(
    "meal_form",
    clear_on_submit=True,
):
    meal_type = st.selectbox(
        "食事",
        MEAL_TYPES,
    )

    food = st.text_input(
        "何食べた？",
        placeholder=(
            "例：ハンバーグ定食"
        ),
    )

    comment = st.text_input(
        "ひとこと",
        placeholder=(
            "例：ご飯は小盛り"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🍚 記録する",
            use_container_width=True,
        )
    )

    if submitted:
        if not food.strip():
            st.error(
                "食べたものを入力してください。"
            )

        else:
            add_record(
                data,
                meal_type,
                food.strip(),
                comment.strip(),
            )

            st.success(
                "食事を記録しました！"
            )

            st.rerun()


# =========================================================
# 今日の食事
# =========================================================

st.divider()

st.subheader(
    "🍴 今日の食事"
)

if not today_records:
    st.info(
        "今日はまだ食事を記録していません。"
    )

else:
    meal_order = {
        meal_type: index
        for index, meal_type
        in enumerate(
            MEAL_TYPES
        )
    }

    today_records = sorted(
        today_records,
        key=lambda record: (
            meal_order.get(
                record.get(
                    "meal_type",
                    "",
                ),
                99,
            ),
            record.get(
                "created_at",
                "",
            ),
        ),
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
                f"{record.get('meal_type', '')}"
            )

            st.markdown(
                f"**{record.get('food', '')}**"
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
                        "meal_type",
                        "☀️ 昼食",
                    )
                )

                edit_type = (
                    st.selectbox(
                        "食事",
                        MEAL_TYPES,
                        index=(
                            MEAL_TYPES.index(
                                current_type
                            )
                            if current_type
                            in MEAL_TYPES
                            else 1
                        ),
                        key=(
                            f"type_"
                            f"{record_id}"
                        ),
                    )
                )

                edit_food = (
                    st.text_input(
                        "食べたもの",
                        value=record.get(
                            "food",
                            "",
                        ),
                        key=(
                            f"food_"
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
                    if not edit_food.strip():
                        st.error(
                            "食べたものを入力してください。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_type,
                            edit_food.strip(),
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


# =========================================================
# 最近7日
# =========================================================

st.divider()

st.subheader(
    "📅 最近7日間"
)

if not weekly_records:
    st.info(
        "最近7日間の記録はありません。"
    )

else:
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

        count = len(
            [
                record
                for record
                in records
                if record.get(
                    "date"
                )
                == str(
                    target_date
                )
            ]
        )

        daily_rows.append(
            {
                "日付": (
                    target_date.strftime(
                        "%m/%d"
                    )
                ),
                "記録数": count,
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
# 食事区分別
# =========================================================

st.divider()

st.subheader(
    "📊 今月の食事区分"
)

if not monthly_records:
    st.info(
        "今月の記録はありません。"
    )

else:
    meal_rows = []

    for meal_type in MEAL_TYPES:
        count = len(
            [
                record
                for record
                in monthly_records
                if record.get(
                    "meal_type"
                )
                == meal_type
            ]
        )

        if count > 0:
            meal_rows.append(
                {
                    "食事": meal_type,
                    "回数": count,
                }
            )

    meal_df = pd.DataFrame(
        meal_rows
    )

    st.bar_chart(
        meal_df.set_index(
            "食事"
        )
    )

    st.dataframe(
        meal_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の食事を見る"
):
    if not records:
        st.info(
            "食事履歴はありません。"
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
                    "食事": (
                        record.get(
                            "meal_type",
                            "",
                        )
                    ),
                    "食べたもの": (
                        record.get(
                            "food",
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
            f"meal_backup_"
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
    "細かい栄養計算はなし。"
    "今日何を食べたか、それだけ残しておこう。🍚"
)
