import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日の気分ひとこと",
    page_icon="😊",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "mood_data.json",
)

MOODS = {
    "😫 とても悪い": 1,
    "😕 少し悪い": 2,
    "😐 普通": 3,
    "🙂 良い": 4,
    "😄 とても良い": 5,
}


# =========================================================
# データ管理
# =========================================================

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
            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        data = create_empty_data()
        save_data(data)
        return data


def save_today_record(
    data,
    mood,
    comment,
):
    today_text = str(
        date.today()
    )

    existing = next(
        (
            record
            for record in data["records"]
            if record.get(
                "date"
            ) == today_text
        ),
        None,
    )

    if existing:
        existing["mood"] = mood
        existing["score"] = MOODS[
            mood
        ]
        existing["comment"] = (
            comment
        )
        existing["updated_at"] = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

    else:
        data["records"].append(
            {
                "date": today_text,
                "mood": mood,
                "score": MOODS[
                    mood
                ],
                "comment": comment,
                "created_at": (
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
                ),
            }
        )

    save_data(data)


def delete_record(
    data,
    target_date,
):
    data["records"] = [
        record
        for record in data[
            "records"
        ]
        if record.get(
            "date"
        ) != target_date
    ]

    save_data(data)


# =========================================================
# 読み込み
# =========================================================

data = load_data()

records = data[
    "records"
]

today_text = str(
    date.today()
)

today_record = next(
    (
        record
        for record in records
        if record.get(
            "date"
        ) == today_text
    ),
    None,
)


# =========================================================
# ヘッダー
# =========================================================

st.title(
    "😊 今日の気分ひとこと"
)

st.caption(
    "今日の気分を10秒で記録しよう。"
)

st.divider()


# =========================================================
# 今日の入力
# =========================================================

st.subheader(
    "🌱 今日の気分"
)

default_mood = (
    today_record.get(
        "mood",
        "😐 普通",
    )
    if today_record
    else "😐 普通"
)

mood_list = list(
    MOODS.keys()
)

selected_mood = st.radio(
    "今の気分は？",
    mood_list,
    index=mood_list.index(
        default_mood
    ),
)

comment = st.text_input(
    "今日のひとこと",
    value=(
        today_record.get(
            "comment",
            "",
        )
        if today_record
        else ""
    ),
    placeholder=(
        "例：朝から少し絵を描けた！"
    ),
)

if st.button(
    "💾 今日の気分を保存",
    use_container_width=True,
):
    save_today_record(
        data,
        selected_mood,
        comment.strip(),
    )

    st.success(
        "今日の気分を保存しました！"
    )

    st.rerun()


# =========================================================
# 今日の記録
# =========================================================

if today_record:
    st.divider()

    st.subheader(
        "✨ 今日の記録"
    )

    with st.container(
        border=True,
    ):
        st.markdown(
            f"## "
            f"{today_record.get('mood', '')}"
        )

        if today_record.get(
            "comment",
            "",
        ):
            st.write(
                f"「"
                f"{today_record.get('comment', '')}"
                f"」"
            )


# =========================================================
# ダッシュボード
# =========================================================

st.divider()

st.subheader(
    "📊 最近の気分"
)

today = date.today()

week_start = (
    today
    - timedelta(
        days=6
    )
)

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


current_month = today.strftime(
    "%Y-%m"
)

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


weekly_average = (
    sum(
        int(
            record.get(
                "score",
                0,
            )
        )
        for record in weekly_records
    )
    / len(
        weekly_records
    )
    if weekly_records
    else 0
)


columns = st.columns(
    3
)

columns[0].metric(
    "今日",
    (
        today_record.get(
            "mood",
            "未記録",
        )
        if today_record
        else "未記録"
    ),
)

columns[1].metric(
    "今週の平均",
    (
        f"{weekly_average:.1f} / 5"
        if weekly_records
        else "未記録"
    ),
)

columns[2].metric(
    "今月の記録",
    f"{len(monthly_records)}日",
)


# =========================================================
# 7日間グラフ
# =========================================================

if weekly_records:
    st.divider()

    st.subheader(
        "📈 最近7日間"
    )

    graph_rows = []

    for i in range(
        7
    ):
        target_date = (
            week_start
            + timedelta(
                days=i
            )
        )

        matching = next(
            (
                record
                for record
                in weekly_records
                if record.get(
                    "date"
                )
                == str(
                    target_date
                )
            ),
            None,
        )

        graph_rows.append(
            {
                "日付": target_date.strftime(
                    "%m/%d"
                ),
                "気分": (
                    matching.get(
                        "score",
                        None,
                    )
                    if matching
                    else None
                ),
            }
        )

    graph_df = pd.DataFrame(
        graph_rows
    )

    graph_df = graph_df.set_index(
        "日付"
    )

    st.line_chart(
        graph_df
    )

    st.caption(
        "1 = とても悪い / 3 = 普通 / 5 = とても良い"
    )


# =========================================================
# 履歴
# =========================================================

st.divider()

st.subheader(
    "📚 過去のひとこと"
)

if not records:
    st.info(
        "まだ記録がありません。"
    )

else:
    sorted_records = sorted(
        records,
        key=lambda record: (
            record.get(
                "date",
                "",
            )
        ),
        reverse=True,
    )

    for record in sorted_records:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### "
                f"{record.get('mood', '')}"
            )

            st.caption(
                record.get(
                    "date",
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
                "🗑️ この記録を削除"
            ):
                if st.button(
                    "削除する",
                    key=(
                        "delete_"
                        + record.get(
                            "date",
                            "",
                        )
                    ),
                    use_container_width=True,
                ):
                    delete_record(
                        data,
                        record.get(
                            "date",
                            "",
                        ),
                    )

                    st.rerun()


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
            f"mood_backup_"
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
    "気分を良くしようとしなくても大丈夫。"
    "今日はどんな日だったか、ひとこと残しておこう。"
)
