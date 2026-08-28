import json
import os
import random
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日なに覚えた？",
    page_icon="📚",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "learning_data.json",
)

CATEGORIES = [
    "AI・プログラミング",
    "イラスト",
    "仕事",
    "資格・勉強",
    "読書",
    "お金",
    "健康",
    "生活",
    "その他",
]


# =========================================================
# データ管理
# =========================================================

def create_empty_data():
    return {
        "records": []
    }


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


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
                "date",
                str(
                    date.today()
                ),
            )

            record.setdefault(
                "learning",
                "",
            )

            record.setdefault(
                "category",
                "その他",
            )

            record.setdefault(
                "note",
                "",
            )

            record.setdefault(
                "created_at",
                "",
            )

            record.setdefault(
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

def get_record_for_date(
    data,
    target_date,
):
    target_text = str(
        target_date
    )

    return next(
        (
            record
            for record
            in data["records"]
            if record.get(
                "date"
            )
            == target_text
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

def save_today_record(
    data,
    learning,
    category,
    note,
):
    today = date.today()

    existing = get_record_for_date(
        data,
        today,
    )

    if existing:
        existing[
            "learning"
        ] = learning

        existing[
            "category"
        ] = category

        existing[
            "note"
        ] = note

        existing[
            "updated_at"
        ] = now_text()

    else:
        data[
            "records"
        ].append(
            {
                "date": str(
                    today
                ),
                "learning": learning,
                "category": category,
                "note": note,
                "created_at": now_text(),
                "updated_at": "",
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
        background: rgba(90, 140, 255, 0.07);
        border: 1px solid rgba(90, 140, 255, 0.15);
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
                rgba(90, 140, 255, 0.18),
                rgba(120, 210, 180, 0.10)
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

    .learning-box {
        padding: 24px;
        border-radius: 18px;
        text-align: center;
        background: rgba(90, 140, 255, 0.06);
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .learning-text {
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

records = data[
    "records"
]

today = date.today()

today_record = get_record_for_date(
    data,
    today,
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
        <h1>📚 今日なに覚えた？</h1>
        <p>
            今日覚えたことを、1つだけ残そう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

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


columns = st.columns(
    4
)

columns[0].metric(
    "今日",
    (
        "✅ 記録済み"
        if today_record
        else "未記録"
    ),
)

columns[1].metric(
    "今月",
    f"{len(monthly_records)}日",
)

columns[2].metric(
    "連続",
    f"{streak}日",
)

columns[3].metric(
    "累計",
    f"{len(records)}個",
)


# =========================================================
# 今日の入力
# =========================================================

st.divider()

st.subheader(
    "✏️ 今日覚えたこと"
)

default_learning = (
    today_record.get(
        "learning",
        "",
    )
    if today_record
    else ""
)

default_category = (
    today_record.get(
        "category",
        "その他",
    )
    if today_record
    else "その他"
)

default_note = (
    today_record.get(
        "note",
        "",
    )
    if today_record
    else ""
)


with st.form(
    "learning_form"
):
    learning = st.text_area(
        "今日、何を覚えた？",
        value=default_learning,
        placeholder=(
            "例：NumPyのbroadcastは末尾の次元から比較する"
        ),
        height=100,
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

    note = st.text_input(
        "ひとこと補足",
        value=default_note,
        placeholder=(
            "例：昨日よりイメージできるようになった"
        ),
    )

    submitted = (
        st.form_submit_button(
            (
                "💾 更新する"
                if today_record
                else "📚 記録する"
            ),
            use_container_width=True,
        )
    )

    if submitted:
        if not learning.strip():
            st.error(
                "今日覚えたことを入力してください。"
            )

        else:
            save_today_record(
                data,
                learning.strip(),
                category,
                note.strip(),
            )

            st.success(
                "今日の学びを保存しました！"
            )

            st.rerun()


# =========================================================
# 今日の学び
# =========================================================

if today_record:
    st.divider()

    st.subheader(
        "✨ 今日の学び"
    )

    st.markdown(
        f"""
        <div class="learning-box">
            <div class="learning-text">
                📚 {today_record.get('learning', '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"カテゴリー："
        f"{today_record.get('category', '')}"
    )

    if today_record.get(
        "note",
        "",
    ):
        st.write(
            f"💬 "
            f"{today_record.get('note', '')}"
        )


# =========================================================
# ランダム復習
# =========================================================

past_records = [
    record
    for record in records
    if record.get(
        "date"
    )
    != str(
        today
    )
]

if past_records:
    st.divider()

    st.subheader(
        "🎲 今日のランダム復習"
    )

    if (
        "random_learning_date"
        not in st.session_state
        or not any(
            record.get(
                "date"
            )
            == st.session_state[
                "random_learning_date"
            ]
            for record
            in past_records
        )
    ):
        st.session_state[
            "random_learning_date"
        ] = random.choice(
            past_records
        ).get(
            "date"
        )

    random_record = next(
        (
            record
            for record
            in past_records
            if record.get(
                "date"
            )
            == st.session_state[
                "random_learning_date"
            ]
        ),
        random.choice(
            past_records
        ),
    )

    with st.container(
        border=True,
    ):
        st.markdown(
            f"### 🧠 "
            f"{random_record.get('learning', '')}"
        )

        st.caption(
            format_date(
                random_record.get(
                    "date",
                    "",
                )
            )
            + " ／ "
            + random_record.get(
                "category",
                "",
            )
        )

        if random_record.get(
            "note",
            "",
        ):
            st.write(
                f"💬 "
                f"{random_record.get('note', '')}"
            )

    if st.button(
        "🎲 別の学びを復習",
        use_container_width=True,
    ):
        st.session_state[
            "random_learning_date"
        ] = random.choice(
            past_records
        ).get(
            "date"
        )

        st.rerun()


# =========================================================
# 今月のカテゴリー
# =========================================================

st.divider()

st.subheader(
    "📊 今月は何を学んでる？"
)

if not monthly_records:
    st.info(
        "今月の記録はまだありません。"
    )

else:
    category_rows = []

    for category_name in CATEGORIES:
        count = len(
            [
                record
                for record
                in monthly_records
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
                    "記録数": count,
                }
            )

    category_df = pd.DataFrame(
        category_rows
    ).sort_values(
        "記録数",
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
# 最近7日
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

week_rows = []

for i in range(
    7
):
    target_date = (
        week_start
        + timedelta(
            days=i
        )
    )

    target_record = (
        get_record_for_date(
            data,
            target_date,
        )
    )

    week_rows.append(
        {
            "日付": (
                target_date.strftime(
                    "%m/%d"
                )
            ),
            "記録": (
                "📚"
                if target_record
                else "—"
            ),
            "覚えたこと": (
                target_record.get(
                    "learning",
                    "",
                )
                if target_record
                else ""
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
# 全履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の学びを見る"
):
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
            record_date = record.get(
                "date",
                "",
            )

            with st.container(
                border=True,
            ):
                st.markdown(
                    f"### 🧠 "
                    f"{record.get('learning', '')}"
                )

                st.caption(
                    format_date(
                        record_date
                    )
                    + " ／ "
                    + record.get(
                        "category",
                        "",
                    )
                )

                if record.get(
                    "note",
                    "",
                ):
                    st.write(
                        f"💬 "
                        f"{record.get('note', '')}"
                    )

                with st.expander(
                    "🗑️ 削除"
                ):
                    if st.button(
                        "この記録を削除",
                        key=(
                            "delete_"
                            + record_date
                        ),
                        use_container_width=True,
                    ):
                        delete_record(
                            data,
                            record_date,
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
            f"learning_backup_"
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
    "今日ひとつ覚えれば、1年で365個。📚✨"
)
