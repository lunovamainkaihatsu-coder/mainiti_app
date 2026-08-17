import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日は何点？",
    page_icon="📊",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "score_data.json",
)


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

def score_label(score):
    if score >= 90:
        return "🌟 最高の日！"

    if score >= 75:
        return "😊 良い日"

    if score >= 60:
        return "🙂 まずまず"

    if score >= 40:
        return "☕ ちょっと大変"

    return "🌙 今日は休もう"


def format_date(date_text):
    try:
        target_date = datetime.strptime(
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
            target_date.weekday()
        ]

        return target_date.strftime(
            f"%Y年%m月%d日（{weekday}）"
        )

    except ValueError:
        return date_text


def save_today_record(
    data,
    score,
    comment,
):
    today_text = str(
        date.today()
    )

    existing_record = next(
        (
            record
            for record
            in data["records"]
            if record.get(
                "date"
            )
            == today_text
        ),
        None,
    )

    if existing_record:
        existing_record[
            "score"
        ] = int(
            score
        )

        existing_record[
            "comment"
        ] = comment

        existing_record[
            "updated_at"
        ] = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

    else:
        data[
            "records"
        ].append(
            {
                "date": today_text,
                "score": int(
                    score
                ),
                "comment": comment,
                "created_at": (
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
                ),
            }
        )

    save_data(
        data
    )


def delete_record(
    data,
    target_date,
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
            "date"
        )
        != target_date
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
                rgba(140, 100, 255, 0.10)
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

    .score-box {
        text-align: center;
        padding: 20px;
        border-radius: 18px;
        margin-top: 10px;
        margin-bottom: 10px;
        background: rgba(100, 150, 255, 0.07);
    }

    .score-number {
        font-size: 3.5rem;
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

today_record = next(
    (
        record
        for record in records
        if record.get(
            "date"
        )
        == today_text
    ),
    None,
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📊 今日は何点？</h1>
        <p>
            今日という1日を100点満点で、
            ひとことだけ振り返るアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日の入力
# =========================================================

st.subheader(
    "🌱 今日を採点"
)

default_score = (
    int(
        today_record.get(
            "score",
            70,
        )
    )
    if today_record
    else 70
)

score = st.slider(
    "今日は何点？",
    min_value=0,
    max_value=100,
    value=default_score,
    step=1,
)

st.markdown(
    f"""
    <div class="score-box">
        <div class="score-number">
            {score}点
        </div>
        <div>
            {score_label(score)}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
        "例：疲れたけど、少し勉強できた！"
    ),
)

if st.button(
    "💾 今日の点数を保存",
    use_container_width=True,
):
    save_today_record(
        data,
        score,
        comment.strip(),
    )

    st.success(
        "今日の点数を保存しました！"
    )

    st.rerun()


# =========================================================
# 集計
# =========================================================

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
        for record
        in weekly_records
    )
    / len(
        weekly_records
    )
    if weekly_records
    else 0
)


monthly_average = (
    sum(
        int(
            record.get(
                "score",
                0,
            )
        )
        for record
        in monthly_records
    )
    / len(
        monthly_records
    )
    if monthly_records
    else 0
)


# =========================================================
# ダッシュボード
# =========================================================

st.divider()

st.subheader(
    "📊 最近の調子"
)

columns = st.columns(
    3
)

columns[0].metric(
    "今日",
    (
        f"{today_record.get('score', 0)}点"
        if today_record
        else "未記録"
    ),
)

columns[1].metric(
    "今週平均",
    (
        f"{weekly_average:.1f}点"
        if weekly_records
        else "未記録"
    ),
)

columns[2].metric(
    "今月平均",
    (
        f"{monthly_average:.1f}点"
        if monthly_records
        else "未記録"
    ),
)


# =========================================================
# 最高点・最低点
# =========================================================

if records:
    scores = [
        int(
            record.get(
                "score",
                0,
            )
        )
        for record in records
    ]

    score_columns = st.columns(
        3
    )

    score_columns[0].metric(
        "最高点",
        f"{max(scores)}点",
    )

    score_columns[1].metric(
        "最低点",
        f"{min(scores)}点",
    )

    score_columns[2].metric(
        "記録日数",
        f"{len(records)}日",
    )


# =========================================================
# 最近7日間グラフ
# =========================================================

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

    matching_record = next(
        (
            record
            for record
            in records
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
            "点数": (
                int(
                    matching_record.get(
                        "score",
                        0,
                    )
                )
                if matching_record
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
    "記録していない日は空欄になります。"
)


# =========================================================
# 今月の記録
# =========================================================

st.divider()

st.subheader(
    "📅 今月"
)

if not monthly_records:
    st.info(
        "今月の記録はまだありません。"
    )

else:
    monthly_sorted = sorted(
        monthly_records,
        key=lambda record: (
            record.get(
                "date",
                "",
            )
        ),
        reverse=True,
    )

    for record in monthly_sorted:
        with st.container(
            border=True,
        ):
            column1, column2 = (
                st.columns(
                    [
                        3,
                        1,
                    ]
                )
            )

            with column1:
                st.markdown(
                    f"### "
                    f"{score_label(int(record.get('score', 0)))}"
                )

                st.caption(
                    format_date(
                        record.get(
                            "date",
                            "",
                        )
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

            with column2:
                st.metric(
                    "点数",
                    f"{record.get('score', 0)}点",
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
# 全履歴
# =========================================================

st.divider()

with st.expander(
    "📚 全履歴を見る"
):
    if not records:
        st.info(
            "まだ記録がありません。"
        )

    else:
        history_rows = []

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
            history_rows.append(
                {
                    "日付": (
                        record.get(
                            "date",
                            "",
                        )
                    ),
                    "点数": int(
                        record.get(
                            "score",
                            0,
                        )
                    ),
                    "評価": (
                        score_label(
                            int(
                                record.get(
                                    "score",
                                    0,
                                )
                            )
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
            f"daily_score_backup_"
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
    "100点じゃなくても大丈夫。"
    "今日が何点だったか、自分なりに残しておこう。📊"
)
