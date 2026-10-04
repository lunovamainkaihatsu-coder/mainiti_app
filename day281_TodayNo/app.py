import json
import os
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日、何を断った？",
    page_icon="🛡️",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "no_records.json",
)

CATEGORIES = [
    "💼 仕事",
    "🛒 買い物",
    "👥 人付き合い",
    "📱 スマホ・SNS",
    "🍔 食事",
    "🎮 娯楽",
    "🏠 家事・生活",
    "📅 予定",
    "✨ その他",
]

PROTECTED_ITEMS = [
    "⏰ 時間",
    "💰 お金",
    "🧠 集中力",
    "🔋 体力",
    "🌿 心の余裕",
    "👨‍👩‍👧 家族との時間",
    "😴 睡眠",
    "🎯 優先事項",
    "✨ その他",
]

REASONS = [
    "🎯 今やるべきことではない",
    "⏰ 時間がない",
    "🔋 余力がない",
    "💰 必要ない",
    "😣 負担が大きい",
    "🧠 集中を守りたい",
    "👨‍👩‍👧 大切な予定を優先",
    "💭 なんとなく違うと思った",
    "✨ その他",
]

RESULTS = [
    "⏳ まだ分からない",
    "😊 断ってよかった",
    "😐 どちらでもない",
    "😣 断らなければよかった",
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


def today_text():
    return str(date.today())


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value
        )
    except (ValueError, TypeError):
        return None


def format_datetime(value):
    dt = parse_datetime(value)

    if not dt:
        return "-"

    return dt.strftime(
        "%Y/%m/%d %H:%M"
    )


def stars(value):
    value = max(
        1,
        min(int(value), 5),
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def format_minutes(minutes):
    minutes = int(minutes or 0)

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    remain = minutes % 60

    if remain:
        return (
            f"{hours}時間"
            f"{remain}分"
        )

    return f"{hours}時間"


def format_money(value):
    return f"{int(value or 0):,}円"


def average(values):
    values = [
        value
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1,
    )


# =========================================================
# データ
# =========================================================

def empty_data():
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
        data = empty_data()
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
            data = empty_data()

        data.setdefault(
            "records",
            [],
        )

        # 古いデータの補完
        for record in data["records"]:
            record.setdefault(
                "id",
                create_id(),
            )

            record.setdefault(
                "title",
                "",
            )

            record.setdefault(
                "source",
                "",
            )

            record.setdefault(
                "category",
                "✨ その他",
            )

            record.setdefault(
                "protected",
                [],
            )

            record.setdefault(
                "reason",
                REASONS[0],
            )

            record.setdefault(
                "difficulty",
                3,
            )

            record.setdefault(
                "saved_minutes",
                0,
            )

            record.setdefault(
                "saved_money",
                0,
            )

            record.setdefault(
                "result",
                RESULTS[0],
            )

            record.setdefault(
                "memo",
                "",
            )

            record.setdefault(
                "favorite",
                False,
            )

            record.setdefault(
                "record_date",
                today_text(),
            )

            record.setdefault(
                "created_at",
                now_text(),
            )

            record.setdefault(
                "updated_at",
                record.get(
                    "created_at",
                    now_text(),
                ),
            )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = empty_data()
        save_data(data)
        return data


# =========================================================
# CRUD
# =========================================================

def get_record(
    data,
    record_id,
):
    return next(
        (
            record
            for record
            in data["records"]
            if record.get("id")
            == record_id
        ),
        None,
    )


def add_record(
    data,
    title,
    source,
    category,
    protected,
    reason,
    difficulty,
    saved_minutes,
    saved_money,
    result,
    memo,
):
    record = {
        "id": create_id(),
        "title": title,
        "source": source,
        "category": category,
        "protected": protected,
        "reason": reason,
        "difficulty": int(
            difficulty
        ),
        "saved_minutes": int(
            saved_minutes
        ),
        "saved_money": int(
            saved_money
        ),
        "result": result,
        "memo": memo,
        "favorite": False,
        "record_date": today_text(),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["records"].append(
        record
    )

    save_data(data)

    return record["id"]


def update_record(
    data,
    record_id,
    title,
    source,
    category,
    protected,
    reason,
    difficulty,
    saved_minutes,
    saved_money,
    result,
    memo,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["title"] = title
    record["source"] = source
    record["category"] = category
    record["protected"] = protected
    record["reason"] = reason
    record["difficulty"] = int(
        difficulty
    )
    record["saved_minutes"] = int(
        saved_minutes
    )
    record["saved_money"] = int(
        saved_money
    )
    record["result"] = result
    record["memo"] = memo
    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def update_result(
    data,
    record_id,
    result,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["result"] = result
    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_favorite(
    data,
    record_id,
):
    record = get_record(
        data,
        record_id,
    )

    if not record:
        return

    record["favorite"] = (
        not record.get(
            "favorite",
            False,
        )
    )

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data["records"] = [
        record
        for record
        in data["records"]
        if record.get("id")
        != record_id
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
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 16px;
        background: rgba(90, 130, 220, 0.07);
        border: 1px solid rgba(90, 130, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(70, 110, 220, 0.20),
                rgba(100, 190, 180, 0.08)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.82;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()
records = data["records"]

today_records = [
    record
    for record in records
    if record.get(
        "record_date"
    ) == today_text()
]

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)

month_records = [
    record
    for record in records
    if (
        record.get(
            "record_date",
            "",
        )
        or ""
    ).startswith(
        current_month
    )
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🛡️ 今日、何を断った？</h1>
        <p>
            やったことだけが成果じゃない。
            やらなかったことで守れたものも残してみよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日のダッシュボード
# =========================================================

today_minutes = sum(
    int(
        record.get(
            "saved_minutes",
            0,
        )
    )
    for record in today_records
)

today_money = sum(
    int(
        record.get(
            "saved_money",
            0,
        )
    )
    for record in today_records
)

today_protected_count = sum(
    len(
        record.get(
            "protected",
            [],
        )
    )
    for record in today_records
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🚫 今日のNO",
    f"{len(today_records)}回",
)

col2.metric(
    "⏰ 守った時間",
    format_minutes(
        today_minutes
    ),
)

col3.metric(
    "💰 守ったお金",
    format_money(
        today_money
    ),
)

col4.metric(
    "🛡️ 守ったもの",
    f"{today_protected_count}個",
)


# =========================================================
# NO登録
# =========================================================

st.divider()

st.subheader(
    "🚫 今日のNOを記録"
)

with st.form(
    "new_no_form",
    clear_on_submit=True,
):
    title = st.text_area(
        "🚫 今日断ったこと",
        placeholder=(
            "例：急な追加作業"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        source = st.text_input(
            "👤 誰・何から？",
            placeholder=(
                "例：仕事、SNS、自分の衝動"
            ),
        )

        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

    with col2:
        difficulty = st.slider(
            "😣 断る難しさ",
            1,
            5,
            3,
        )

        st.caption(
            stars(difficulty)
        )

        reason = st.selectbox(
            "💭 なぜ断った？",
            REASONS,
        )

    protected = st.multiselect(
        "🛡️ 何を守れた？",
        PROTECTED_ITEMS,
    )

    col1, col2 = st.columns(2)

    with col1:
        saved_minutes = (
            st.number_input(
                "⏰ 守れた時間（分）",
                min_value=0,
                max_value=1440,
                value=0,
                step=10,
            )
        )

    with col2:
        saved_money = (
            st.number_input(
                "💰 使わずに済んだ金額（円）",
                min_value=0,
                max_value=100000000,
                value=0,
                step=100,
            )
        )

    result = st.selectbox(
        "😊 結果",
        RESULTS,
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "断ったときの気持ちや、"
            "後から気づいたことなど"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🛡️ NOを記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "何を断ったか入力してね。"
            )

        else:
            record_id = add_record(
                data=data,
                title=title.strip(),
                source=source.strip(),
                category=category,
                protected=protected,
                reason=reason,
                difficulty=difficulty,
                saved_minutes=(
                    saved_minutes
                ),
                saved_money=(
                    saved_money
                ),
                result=result,
                memo=memo.strip(),
            )

            st.session_state[
                "just_added_no"
            ] = record_id

            st.rerun()


# =========================================================
# 登録直後
# =========================================================

just_added_id = (
    st.session_state.pop(
        "just_added_no",
        None,
    )
)

if just_added_id:
    added = get_record(
        data,
        just_added_id,
    )

    if added:
        st.success(
            "🛡️ NOを記録しました。"
        )

        if (
            added.get(
                "saved_minutes",
                0,
            )
            or added.get(
                "saved_money",
                0,
            )
        ):
            st.write(
                "今回のNOで守れたもの："
            )

            if added.get(
                "saved_minutes",
                0,
            ):
                st.write(
                    "⏰ "
                    + format_minutes(
                        added.get(
                            "saved_minutes",
                            0,
                        )
                    )
                )

            if added.get(
                "saved_money",
                0,
            ):
                st.write(
                    "💰 "
                    + format_money(
                        added.get(
                            "saved_money",
                            0,
                        )
                    )
                )


# =========================================================
# 今日のNO
# =========================================================

st.divider()

st.subheader(
    "🛡️ 今日守ったもの"
)

if not today_records:
    st.info(
        "今日はまだNOの記録がありません。"
    )

else:
    for record in sorted(
        today_records,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            col1, col2 = (
                st.columns(
                    [7, 1]
                )
            )

            with col1:
                st.subheader(
                    record.get(
                        "title",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if record.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "today_fav_"
                        + record_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )
                    st.rerun()

            st.caption(
                record.get(
                    "category",
                    "",
                )
                + " ｜ "
                + stars(
                    record.get(
                        "difficulty",
                        3,
                    )
                )
            )

            if record.get("source"):
                st.write(
                    "👤 **誰・何から？**"
                )
                st.write(
                    record.get(
                        "source",
                        "",
                    )
                )

            if record.get(
                "protected"
            ):
                st.write(
                    "🛡️ **守れたもの**"
                )

                st.write(
                    "　".join(
                        record.get(
                            "protected",
                            [],
                        )
                    )
                )

            col1, col2 = (
                st.columns(2)
            )

            col1.metric(
                "⏰ 守った時間",
                format_minutes(
                    record.get(
                        "saved_minutes",
                        0,
                    )
                ),
            )

            col2.metric(
                "💰 守ったお金",
                format_money(
                    record.get(
                        "saved_money",
                        0,
                    )
                ),
            )

            st.write(
                "💭 **理由：** "
                + record.get(
                    "reason",
                    "",
                )
            )

            st.write(
                "😊 **結果：** "
                + record.get(
                    "result",
                    RESULTS[0],
                )
            )

            if record.get("memo"):
                st.write(
                    "📝 **メモ**"
                )
                st.write(
                    record.get(
                        "memo",
                        "",
                    )
                )


# =========================================================
# 結果待ち
# =========================================================

pending_records = [
    record
    for record in records
    if record.get(
        "result"
    ) == "⏳ まだ分からない"
]

if pending_records:
    st.divider()

    st.subheader(
        "⏳ あのNO、その後どうだった？"
    )

    st.caption(
        "結果が分かったものだけ更新してみよう。"
    )

    for record in sorted(
        pending_records,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.subheader(
                record.get(
                    "title",
                    "",
                )
            )

            st.caption(
                format_datetime(
                    record.get(
                        "created_at"
                    )
                )
            )

            new_result = (
                st.selectbox(
                    "結果",
                    RESULTS[1:],
                    key=(
                        "result_select_"
                        + record_id
                    ),
                )
            )

            if st.button(
                "😊 結果を確定",
                key=(
                    "result_update_"
                    + record_id
                ),
                use_container_width=True,
            ):
                update_result(
                    data,
                    record_id,
                    new_result,
                )

                st.rerun()


# =========================================================
# 最高のNO
# =========================================================

favorites = [
    record
    for record in records
    if record.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 最高のNO"
    )

    for record in sorted(
        favorites,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.container(
            border=True
        ):
            st.subheader(
                record.get(
                    "title",
                    "",
                )
            )

            st.caption(
                record.get(
                    "record_date",
                    "",
                )
                + " ｜ "
                + record.get(
                    "category",
                    "",
                )
            )

            if record.get(
                "protected"
            ):
                st.write(
                    "🛡️ "
                    + "　".join(
                        record.get(
                            "protected",
                            [],
                        )
                    )
                )

            col1, col2 = (
                st.columns(2)
            )

            col1.metric(
                "⏰ 時間",
                format_minutes(
                    record.get(
                        "saved_minutes",
                        0,
                    )
                ),
            )

            col2.metric(
                "💰 お金",
                format_money(
                    record.get(
                        "saved_money",
                        0,
                    )
                ),
            )

            st.write(
                record.get(
                    "result",
                    "",
                )
            )

            if record.get("memo"):
                st.write(
                    record.get(
                        "memo",
                        "",
                    )
                )

            if st.button(
                "⭐ 最高のNOから外す",
                key=(
                    "remove_best_"
                    + record_id
                ),
                use_container_width=True,
            ):
                toggle_favorite(
                    data,
                    record_id,
                )
                st.rerun()


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月のNO"
)

if not month_records:
    st.info(
        "今月のデータはまだありません。"
    )

else:
    month_minutes = sum(
        int(
            record.get(
                "saved_minutes",
                0,
            )
        )
        for record in month_records
    )

    month_money = sum(
        int(
            record.get(
                "saved_money",
                0,
            )
        )
        for record in month_records
    )

    decided_records = [
        record
        for record in month_records
        if record.get(
            "result"
        )
        != "⏳ まだ分からない"
    ]

    good_records = [
        record
        for record in decided_records
        if record.get(
            "result"
        )
        == "😊 断ってよかった"
    ]

    good_rate = (
        round(
            len(good_records)
            / len(decided_records)
            * 100
        )
        if decided_records
        else 0
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "🚫 NO",
        f"{len(month_records)}回",
    )

    col2.metric(
        "⏰ 守った時間",
        format_minutes(
            month_minutes
        ),
    )

    col3.metric(
        "💰 守ったお金",
        format_money(
            month_money
        ),
    )

    col4.metric(
        "😊 よかった率",
        (
            f"{good_rate}%"
            if decided_records
            else "-"
        ),
    )


# =========================================================
# 守ったもの分析
# =========================================================

if month_records:
    protected_counts = {}

    for record in month_records:
        for item in record.get(
            "protected",
            [],
        ):
            protected_counts[
                item
            ] = (
                protected_counts.get(
                    item,
                    0,
                )
                + 1
            )

    if protected_counts:
        st.markdown(
            "### 🛡️ 一番守ったもの"
        )

        protected_df = (
            pd.DataFrame(
                [
                    {
                        "守ったもの": item,
                        "回数": count,
                    }
                    for item, count
                    in protected_counts.items()
                ]
            )
            .sort_values(
                "回数",
                ascending=False,
            )
        )

        st.bar_chart(
            protected_df.set_index(
                "守ったもの"
            )
        )


# =========================================================
# カテゴリー分析
# =========================================================

if month_records:
    category_counts = {}

    for record in month_records:
        category = record.get(
            "category",
            "✨ その他",
        )

        category_counts[
            category
        ] = (
            category_counts.get(
                category,
                0,
            )
            + 1
        )

    if category_counts:
        st.markdown(
            "### 🚫 何にNOと言った？"
        )

        category_df = (
            pd.DataFrame(
                [
                    {
                        "カテゴリー": category,
                        "回数": count,
                    }
                    for category, count
                    in category_counts.items()
                ]
            )
            .sort_values(
                "回数",
                ascending=False,
            )
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 理由分析
# =========================================================

if month_records:
    reason_counts = {}

    for record in month_records:
        reason = record.get(
            "reason",
            "",
        )

        if not reason:
            continue

        reason_counts[
            reason
        ] = (
            reason_counts.get(
                reason,
                0,
            )
            + 1
        )

    if reason_counts:
        st.markdown(
            "### 💭 なぜ断った？"
        )

        reason_df = (
            pd.DataFrame(
                [
                    {
                        "理由": reason,
                        "回数": count,
                    }
                    for reason, count
                    in reason_counts.items()
                ]
            )
            .sort_values(
                "回数",
                ascending=False,
            )
        )

        st.bar_chart(
            reason_df.set_index(
                "理由"
            )
        )


# =========================================================
# NOの成功率
# =========================================================

decided_all = [
    record
    for record in records
    if record.get(
        "result"
    )
    != "⏳ まだ分からない"
]

if decided_all:
    st.divider()

    st.subheader(
        "🧠 NOの結果"
    )

    result_counts = {}

    for result in RESULTS[1:]:
        result_counts[
            result
        ] = len(
            [
                record
                for record in decided_all
                if record.get(
                    "result"
                )
                == result
            ]
        )

    result_df = pd.DataFrame(
        [
            {
                "結果": result,
                "回数": count,
            }
            for result, count
            in result_counts.items()
        ]
    )

    st.bar_chart(
        result_df.set_index(
            "結果"
        )
    )

    good_count = result_counts.get(
        "😊 断ってよかった",
        0,
    )

    st.metric(
        "😊 「断ってよかった」",
        (
            f"{round(good_count / len(decided_all) * 100)}%"
        ),
    )


# =========================================================
# 難しいNO分析
# =========================================================

hard_records = [
    record
    for record in decided_all
    if int(
        record.get(
            "difficulty",
            3,
        )
    )
    == 5
]

if hard_records:
    hard_good = len(
        [
            record
            for record in hard_records
            if record.get(
                "result"
            )
            == "😊 断ってよかった"
        ]
    )

    hard_rate = round(
        hard_good
        / len(hard_records)
        * 100
    )

    st.info(
        "😣 難しさ★★★★★のNOでも、"
        f" {hard_rate}% が"
        "「断ってよかった」になっています。"
    )


# =========================================================
# 一番勇気が必要だったNO
# =========================================================

if month_records:
    hardest = max(
        month_records,
        key=lambda record: (
            int(
                record.get(
                    "difficulty",
                    1,
                )
            ),
            int(
                record.get(
                    "saved_minutes",
                    0,
                )
            )
            + int(
                record.get(
                    "saved_money",
                    0,
                )
            ),
        ),
    )

    st.divider()

    st.subheader(
        "🏆 今月、勇気が必要だったNO"
    )

    with st.container(
        border=True
    ):
        st.subheader(
            hardest.get(
                "title",
                "",
            )
        )

        st.write(
            "😣 **難しさ：** "
            + stars(
                hardest.get(
                    "difficulty",
                    3,
                )
            )
        )

        if hardest.get(
            "protected"
        ):
            st.write(
                "🛡️ **守れたもの**"
            )

            st.write(
                "　".join(
                    hardest.get(
                        "protected",
                        [],
                    )
                )
            )

        st.write(
            "😊 **結果：** "
            + hardest.get(
                "result",
                "",
            )
        )


# =========================================================
# NO図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 NO図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "仕事、買い物、追加作業……"
    ),
)

col1, col2, col3 = (
    st.columns(3)
)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key=(
                "library_category"
            ),
        )
    )

with col2:
    result_filter = (
        st.selectbox(
            "結果",
            ["すべて"]
            + RESULTS,
            key=(
                "library_result"
            ),
        )
    )

with col3:
    protected_filter = (
        st.selectbox(
            "守ったもの",
            ["すべて"]
            + PROTECTED_ITEMS,
            key=(
                "library_protected"
            ),
        )
    )


filtered_records = []

for record in records:
    if (
        category_filter
        != "すべて"
        and record.get(
            "category"
        )
        != category_filter
    ):
        continue

    if (
        result_filter
        != "すべて"
        and record.get(
            "result"
        )
        != result_filter
    ):
        continue

    if (
        protected_filter
        != "すべて"
        and protected_filter
        not in record.get(
            "protected",
            [],
        )
    ):
        continue

    searchable = " ".join(
        [
            record.get(
                "title",
                "",
            ),
            record.get(
                "source",
                "",
            ),
            record.get(
                "category",
                "",
            ),
            record.get(
                "reason",
                "",
            ),
            record.get(
                "memo",
                "",
            ),
            " ".join(
                record.get(
                    "protected",
                    [],
                )
            ),
        ]
    ).lower()

    if (
        search_text.strip()
        and search_text
        .strip()
        .lower()
        not in searchable
    ):
        continue

    filtered_records.append(
        record
    )


if not filtered_records:
    st.info(
        "条件に合うNOはありません。"
    )

else:
    for record in sorted(
        filtered_records,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        with st.container(
            border=True
        ):
            st.subheader(
                record.get(
                    "title",
                    "",
                )
            )

            st.caption(
                record.get(
                    "record_date",
                    "",
                )
                + " ｜ "
                + record.get(
                    "category",
                    "",
                )
                + " ｜ "
                + stars(
                    record.get(
                        "difficulty",
                        3,
                    )
                )
            )

            if record.get(
                "protected"
            ):
                st.write(
                    "🛡️ "
                    + "　".join(
                        record.get(
                            "protected",
                            [],
                        )
                    )
                )

            st.write(
                "😊 "
                + record.get(
                    "result",
                    "",
                )
            )


# =========================================================
# 履歴テーブル
# =========================================================

st.divider()

st.subheader(
    "📜 履歴"
)

history_rows = []

for record in sorted(
    records,
    key=lambda item: (
        item.get(
            "created_at",
            "",
        )
    ),
    reverse=True,
):
    history_rows.append(
        {
            "日付": record.get(
                "record_date",
                "",
            ),
            "断ったこと": (
                record.get(
                    "title",
                    "",
                )
            ),
            "カテゴリー": (
                record.get(
                    "category",
                    "",
                )
            ),
            "難しさ": stars(
                record.get(
                    "difficulty",
                    3,
                )
            ),
            "守った時間": (
                format_minutes(
                    record.get(
                        "saved_minutes",
                        0,
                    )
                )
            ),
            "守ったお金": (
                format_money(
                    record.get(
                        "saved_money",
                        0,
                    )
                )
            ),
            "結果": record.get(
                "result",
                "",
            ),
            "⭐": (
                "⭐"
                if record.get(
                    "favorite",
                    False,
                )
                else ""
            ),
        }
    )


if history_rows:
    st.dataframe(
        pd.DataFrame(
            history_rows
        ),
        hide_index=True,
        use_container_width=True,
    )

else:
    st.caption(
        "まだ履歴はありません。"
    )


# =========================================================
# 編集・管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・管理"
):
    if not records:
        st.caption(
            "まだ記録がありません。"
        )

    for record in sorted(
        records,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        record_id = record.get(
            "id",
            "",
        )

        with st.expander(
            record.get(
                "record_date",
                "",
            )
            + " ｜ "
            + record.get(
                "title",
                "",
            )
        ):
            edit_title = (
                st.text_area(
                    "断ったこと",
                    value=record.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + record_id
                    ),
                )
            )

            edit_source = (
                st.text_input(
                    "誰・何から？",
                    value=record.get(
                        "source",
                        "",
                    ),
                    key=(
                        "edit_source_"
                        + record_id
                    ),
                )
            )

            old_category = (
                record.get(
                    "category",
                    "✨ その他",
                )
            )

            category_index = (
                CATEGORIES.index(
                    old_category
                )
                if old_category
                in CATEGORIES
                else len(
                    CATEGORIES
                ) - 1
            )

            edit_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=(
                        category_index
                    ),
                    key=(
                        "edit_category_"
                        + record_id
                    ),
                )
            )

            edit_protected = (
                st.multiselect(
                    "守れたもの",
                    PROTECTED_ITEMS,
                    default=[
                        item
                        for item
                        in record.get(
                            "protected",
                            [],
                        )
                        if item
                        in PROTECTED_ITEMS
                    ],
                    key=(
                        "edit_protected_"
                        + record_id
                    ),
                )
            )

            old_reason = (
                record.get(
                    "reason",
                    REASONS[0],
                )
            )

            reason_index = (
                REASONS.index(
                    old_reason
                )
                if old_reason
                in REASONS
                else 0
            )

            edit_reason = (
                st.selectbox(
                    "理由",
                    REASONS,
                    index=reason_index,
                    key=(
                        "edit_reason_"
                        + record_id
                    ),
                )
            )

            edit_difficulty = (
                st.slider(
                    "断る難しさ",
                    1,
                    5,
                    int(
                        record.get(
                            "difficulty",
                            3,
                        )
                    ),
                    key=(
                        "edit_difficulty_"
                        + record_id
                    ),
                )
            )

            edit_minutes = (
                st.number_input(
                    "守れた時間（分）",
                    min_value=0,
                    max_value=1440,
                    value=int(
                        record.get(
                            "saved_minutes",
                            0,
                        )
                    ),
                    key=(
                        "edit_minutes_"
                        + record_id
                    ),
                )
            )

            edit_money = (
                st.number_input(
                    "守れたお金（円）",
                    min_value=0,
                    max_value=100000000,
                    value=int(
                        record.get(
                            "saved_money",
                            0,
                        )
                    ),
                    key=(
                        "edit_money_"
                        + record_id
                    ),
                )
            )

            old_result = record.get(
                "result",
                RESULTS[0],
            )

            result_index = (
                RESULTS.index(
                    old_result
                )
                if old_result
                in RESULTS
                else 0
            )

            edit_result = (
                st.selectbox(
                    "結果",
                    RESULTS,
                    index=result_index,
                    key=(
                        "edit_result_"
                        + record_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "メモ",
                    value=record.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + record_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_edit_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "断ったことを入力してね。"
                        )

                    else:
                        update_record(
                            data=data,
                            record_id=(
                                record_id
                            ),
                            title=(
                                edit_title.strip()
                            ),
                            source=(
                                edit_source.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            protected=(
                                edit_protected
                            ),
                            reason=(
                                edit_reason
                            ),
                            difficulty=(
                                edit_difficulty
                            ),
                            saved_minutes=(
                                edit_minutes
                            ),
                            saved_money=(
                                edit_money
                            ),
                            result=(
                                edit_result
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                favorite_label = (
                    "⭐ 最高のNOから外す"
                    if record.get(
                        "favorite",
                        False,
                    )
                    else "☆ 最高のNOにする"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "manage_favorite_"
                        + record_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        record_id,
                    )

                    st.rerun()

            confirm_delete = (
                st.checkbox(
                    "削除を確認",
                    key=(
                        "confirm_delete_"
                        + record_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + record_id
                ),
                disabled=(
                    not confirm_delete
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
            "today_no_"
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
    "🛡️ やらなかったことにも、"
    "ちゃんと価値がある。"
)
