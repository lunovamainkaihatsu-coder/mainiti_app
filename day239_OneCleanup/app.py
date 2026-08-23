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
    page_title="今日ひとつ片付けた",
    page_icon="🧺",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "cleanup_data.json",
)

PLACES = [
    "デスク",
    "リビング",
    "キッチン",
    "寝室",
    "玄関",
    "クローゼット",
    "洗面所",
    "お風呂",
    "車",
    "収納",
    "その他",
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
                "item",
                "",
            )

            record.setdefault(
                "place",
                "その他",
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


def calculate_streak(
    records,
):
    recorded_dates = {
        record.get(
            "date"
        )
        for record in records
        if record.get(
            "date"
        )
    }

    if not recorded_dates:
        return 0

    current = date.today()

    if str(current) not in recorded_dates:
        current -= timedelta(
            days=1
        )

        if str(current) not in recorded_dates:
            return 0

    streak = 0

    while str(current) in recorded_dates:
        streak += 1

        current -= timedelta(
            days=1
        )

    return streak


# =========================================================
# データ操作
# =========================================================

def add_record(
    data,
    item,
    place,
    comment,
):
    record = {
        "id": create_id(),
        "date": str(
            date.today()
        ),
        "item": item,
        "place": place,
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
    item,
    place,
    comment,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    record[
        "item"
    ] = item

    record[
        "place"
    ] = place

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
        background: rgba(110, 180, 140, 0.08);
        border: 1px solid rgba(110, 180, 140, 0.18);
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
                rgba(110, 180, 140, 0.18),
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

current_month = today.strftime(
    "%Y-%m"
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧺 今日ひとつ片付けた</h1>
        <p>
            一気にやらなくていい。
            今日ひとつだけ整えよう。
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


streak = calculate_streak(
    records
)


# =========================================================
# ダッシュボード
# =========================================================

columns = st.columns(
    4
)

columns[0].metric(
    "今日",
    f"{len(today_records)}個",
)

columns[1].metric(
    "今月",
    f"{len(monthly_records)}個",
)

columns[2].metric(
    "累計",
    f"{len(records)}個",
)

columns[3].metric(
    "連続",
    f"{streak}日",
)


# =========================================================
# 今日の達成
# =========================================================

if today_records:
    st.success(
        "🎉 今日の片付け達成！1個だけでも十分。"
    )


# =========================================================
# 入力
# =========================================================

st.divider()

st.subheader(
    "➕ 今日片付けたもの"
)

with st.form(
    "cleanup_form",
    clear_on_submit=True,
):
    item = st.text_input(
        "何を片付けた？",
        placeholder=(
            "例：机の上の書類"
        ),
    )

    place = st.selectbox(
        "場所",
        PLACES,
    )

    comment = st.text_input(
        "ひとこと",
        placeholder=(
            "例：5分で終わった！"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🧺 記録する",
            use_container_width=True,
        )
    )

    if submitted:
        if not item.strip():
            st.error(
                "片付けたものを入力してください。"
            )

        else:
            add_record(
                data,
                item.strip(),
                place,
                comment.strip(),
            )

            st.success(
                "片付けを記録しました！"
            )

            st.balloons()
            st.rerun()


# =========================================================
# 今日片付けたもの
# =========================================================

st.divider()

st.subheader(
    "✨ 今日片付けたもの"
)

if not today_records:
    st.info(
        "今日はまだ記録がありません。"
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
                f"### ✅ "
                f"{record.get('item', '')}"
            )

            st.caption(
                f"📍 "
                f"{record.get('place', '')}"
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
                edit_item = (
                    st.text_input(
                        "片付けたもの",
                        value=record.get(
                            "item",
                            "",
                        ),
                        key=(
                            f"item_"
                            f"{record_id}"
                        ),
                    )
                )

                current_place = (
                    record.get(
                        "place",
                        "その他",
                    )
                )

                edit_place = (
                    st.selectbox(
                        "場所",
                        PLACES,
                        index=(
                            PLACES.index(
                                current_place
                            )
                            if current_place
                            in PLACES
                            else (
                                len(
                                    PLACES
                                )
                                - 1
                            )
                        ),
                        key=(
                            f"place_"
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
                    if not edit_item.strip():
                        st.error(
                            "片付けたものを入力してください。"
                        )

                    else:
                        update_record(
                            data,
                            record_id,
                            edit_item.strip(),
                            edit_place,
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
# 最近7日間
# =========================================================

st.divider()

st.subheader(
    "📅 最近7日間"
)

week_start = (
    today
    - timedelta(
        days=6
    )
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

    count = len(
        [
            record
            for record in records
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
            "日付": target_date.strftime(
                "%m/%d"
            ),
            "片付けた数": count,
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
# 今月の場所別
# =========================================================

st.divider()

st.subheader(
    "📊 今月どこを片付けた？"
)

if not monthly_records:
    st.info(
        "今月の記録はありません。"
    )

else:
    place_rows = []

    for place in PLACES:
        count = len(
            [
                record
                for record
                in monthly_records
                if record.get(
                    "place"
                )
                == place
            ]
        )

        if count > 0:
            place_rows.append(
                {
                    "場所": place,
                    "個数": count,
                }
            )

    place_df = pd.DataFrame(
        place_rows
    ).sort_values(
        "個数",
        ascending=False,
    )

    st.bar_chart(
        place_df.set_index(
            "場所"
        )
    )

    st.dataframe(
        place_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の片付けを見る"
):
    if not records:
        st.info(
            "片付け履歴はありません。"
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
                    "片付けたもの": (
                        record.get(
                            "item",
                            "",
                        )
                    ),
                    "場所": (
                        record.get(
                            "place",
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
            f"cleanup_backup_"
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
    "1日1個なら、部屋は少しずつ整っていく。🧺"
)
