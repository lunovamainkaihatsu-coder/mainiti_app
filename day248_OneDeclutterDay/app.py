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
    page_title="今日ひとつ捨てる",
    page_icon="🗑️",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "declutter_data.json",
)

CATEGORIES = [
    "モノ",
    "データ",
    "写真・ファイル",
    "予定",
    "習慣",
    "考え方",
    "その他",
]

SPACES = [
    "📦 スペース",
    "⏰ 時間",
    "🧠 頭の余白",
    "💰 お金",
    "❤️ 気持ち",
    "✨ その他",
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
        "records": []
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
            "records",
            [],
        )

        for record in data["records"]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "date",
                str(date.today()),
            )

            record.setdefault(
                "item",
                "",
            )

            record.setdefault(
                "category",
                "その他",
            )

            record.setdefault(
                "memo",
                "",
            )

            record.setdefault(
                "space",
                "📦 スペース",
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
        save_data(data)
        return data


# =========================================================
# 補助関数
# =========================================================

def get_record_by_id(
    data,
    record_id,
):
    return next(
        (
            record
            for record in data["records"]
            if record.get("id")
            == record_id
        ),
        None,
    )


def get_today_record(
    data,
):
    today_text = str(
        date.today()
    )

    return next(
        (
            record
            for record in data["records"]
            if record.get("date")
            == today_text
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


def calculate_streak(
    records,
):
    recorded_dates = {
        record.get("date")
        for record in records
        if record.get("date")
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
    item,
    category,
    memo,
    space,
):
    today_record = get_today_record(
        data
    )

    if today_record:
        today_record[
            "item"
        ] = item

        today_record[
            "category"
        ] = category

        today_record[
            "memo"
        ] = memo

        today_record[
            "space"
        ] = space

        today_record[
            "updated_at"
        ] = now_text()

    else:
        data["records"].append(
            {
                "id": create_id(),
                "date": str(
                    date.today()
                ),
                "item": item,
                "category": category,
                "memo": memo,
                "space": space,
                "created_at": now_text(),
                "updated_at": "",
            }
        )

    save_data(data)


def update_record(
    data,
    record_id,
    item,
    category,
    memo,
    space,
):
    record = get_record_by_id(
        data,
        record_id,
    )

    if not record:
        return

    record["item"] = item
    record["category"] = category
    record["memo"] = memo
    record["space"] = space
    record["updated_at"] = now_text()

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record in data["records"]
        if record.get("id")
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
        background: rgba(100, 190, 150, 0.07);
        border: 1px solid rgba(100, 190, 150, 0.16);
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
                rgba(100, 190, 150, 0.18),
                rgba(120, 160, 255, 0.10)
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

    .declutter-box {
        padding: 24px;
        border-radius: 18px;
        text-align: center;
        background: rgba(100, 190, 150, 0.07);
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .declutter-text {
        font-size: 1.35rem;
        font-weight: 700;
        line-height: 1.6;
    }

    .total-box {
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        background: rgba(100, 190, 150, 0.08);
        margin-top: 15px;
    }

    .total-number {
        font-size: 2rem;
        font-weight: 800;
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

today_record = get_today_record(
    data
)

current_month = date.today().strftime(
    "%Y-%m"
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🗑️ 今日ひとつ捨てる</h1>

        <p>
            毎日ひとつ手放して、
            少しずつ身軽になろう。
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
        "✅ 1個"
        if today_record
        else "未記録"
    ),
)

columns[1].metric(
    "今月",
    f"{len(monthly_records)}個",
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
    "🗑️ 今日手放したもの"
)

default_item = (
    today_record.get(
        "item",
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

default_memo = (
    today_record.get(
        "memo",
        "",
    )
    if today_record
    else ""
)

default_space = (
    today_record.get(
        "space",
        "📦 スペース",
    )
    if today_record
    else "📦 スペース"
)


with st.form(
    "declutter_form"
):
    item = st.text_area(
        "何を手放した？",
        value=default_item,
        placeholder=(
            "例：使っていないUSBケーブル"
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
            else 0
        ),
    )

    space = st.selectbox(
        "✨ 何が空いた？",
        SPACES,
        index=(
            SPACES.index(
                default_space
            )
            if default_space
            in SPACES
            else 0
        ),
    )

    memo = st.text_input(
        "ひとこと",
        value=default_memo,
        placeholder=(
            "例：引き出しが少しスッキリした"
        ),
    )

    submitted = (
        st.form_submit_button(
            (
                "💾 更新する"
                if today_record
                else "🗑️ 今日の1個を記録"
            ),
            use_container_width=True,
        )
    )

    if submitted:
        if not item.strip():
            st.error(
                "手放したものを入力してください。"
            )

        else:
            save_today_record(
                data,
                item.strip(),
                category,
                memo.strip(),
                space,
            )

            st.success(
                "今日の1個を記録しました！"
            )

            st.rerun()


# =========================================================
# 今日の記録
# =========================================================

if today_record:
    st.divider()

    st.subheader(
        "✨ 今日、身軽になったこと"
    )

    st.markdown(
        f"""
        <div class="declutter-box">

            <div class="declutter-text">
                🗑️ {today_record.get('item', '')}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"{today_record.get('category', '')}"
        f" ／ "
        f"{today_record.get('space', '')}"
    )

    if today_record.get(
        "memo",
        "",
    ):
        st.write(
            f"💬 "
            f"{today_record.get('memo', '')}"
        )


# =========================================================
# 累計メッセージ
# =========================================================

if records:
    st.markdown(
        f"""
        <div class="total-box">

            <div class="total-number">
                ✨ {len(records)}個
            </div>

            <div>
                ぶん、身軽になりました。
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 今月のカテゴリー
# =========================================================

st.divider()

st.subheader(
    "📊 今月は何を手放した？"
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
                for record in monthly_records
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
                    "個数": count,
                }
            )

    category_df = pd.DataFrame(
        category_rows
    ).sort_values(
        "個数",
        ascending=False,
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )


# =========================================================
# 何が空いた？
# =========================================================

if records:
    st.divider()

    st.subheader(
        "✨ 手放して空いたもの"
    )

    space_rows = []

    for space_name in SPACES:
        count = len(
            [
                record
                for record in records
                if record.get(
                    "space"
                )
                == space_name
            ]
        )

        if count > 0:
            space_rows.append(
                {
                    "空いたもの": (
                        space_name
                    ),
                    "回数": count,
                }
            )

    if space_rows:
        space_df = pd.DataFrame(
            space_rows
        ).sort_values(
            "回数",
            ascending=False,
        )

        st.bar_chart(
            space_df.set_index(
                "空いたもの"
            )
        )


# =========================================================
# 最近7日
# =========================================================

st.divider()

st.subheader(
    "📅 最近7日間"
)

week_start = (
    date.today()
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

    target_text = str(
        target_date
    )

    target_record = next(
        (
            record
            for record in records
            if record.get(
                "date"
            )
            == target_text
        ),
        None,
    )

    week_rows.append(
        {
            "日付": target_date.strftime(
                "%m/%d"
            ),
            "記録": (
                "🗑️"
                if target_record
                else "—"
            ),
            "手放したもの": (
                target_record.get(
                    "item",
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
# 履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の記録を見る"
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
            record_id = record.get(
                "id",
                "",
            )

            with st.container(
                border=True,
            ):
                st.markdown(
                    f"### 🗑️ "
                    f"{record.get('item', '')}"
                )

                st.caption(
                    f"{format_date(record.get('date', ''))}"
                    f" ／ "
                    f"{record.get('category', '')}"
                )

                st.write(
                    f"✨ "
                    f"{record.get('space', '')}"
                )

                if record.get(
                    "memo",
                    "",
                ):
                    st.write(
                        f"💬 "
                        f"{record.get('memo', '')}"
                    )

                # -----------------------------------------
                # 編集
                # -----------------------------------------

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_item = st.text_area(
                        "手放したもの",
                        value=record.get(
                            "item",
                            "",
                        ),
                        key=(
                            f"edit_item_"
                            f"{record_id}"
                        ),
                    )

                    current_category = (
                        record.get(
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
                                f"{record_id}"
                            ),
                        )
                    )

                    current_space = (
                        record.get(
                            "space",
                            "📦 スペース",
                        )
                    )

                    edit_space = st.selectbox(
                        "何が空いた？",
                        SPACES,
                        index=(
                            SPACES.index(
                                current_space
                            )
                            if current_space
                            in SPACES
                            else 0
                        ),
                        key=(
                            f"edit_space_"
                            f"{record_id}"
                        ),
                    )

                    edit_memo = st.text_input(
                        "ひとこと",
                        value=record.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_memo_"
                            f"{record_id}"
                        ),
                    )

                    if st.button(
                        "💾 変更を保存",
                        key=(
                            f"save_edit_"
                            f"{record_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_item.strip():
                            st.error(
                                "手放したものを入力してください。"
                            )

                        else:
                            update_record(
                                data,
                                record_id,
                                edit_item.strip(),
                                edit_category,
                                edit_memo.strip(),
                                edit_space,
                            )

                            st.rerun()

                # -----------------------------------------
                # 削除
                # -----------------------------------------

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
            f"declutter_backup_"
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
    "ひとつ手放すたびに、少しだけ余白が増えていく。✨"
)
