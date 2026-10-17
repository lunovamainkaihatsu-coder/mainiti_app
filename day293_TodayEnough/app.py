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
    page_title="今日はどこまででOK？",
    page_icon="🏁",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "days.json",
)

CATEGORIES = [
    "📚 勉強",
    "💻 開発",
    "💼 仕事",
    "🏃 運動",
    "🏠 生活",
    "🎨 創作",
    "🌿 休息",
    "✨ その他",
]

RESULTS = [
    "⏳ まだ判定していない",
    "🌙 届かなかった",
    "🌱 最低ライン達成！",
    "🎯 理想ライン達成！",
    "🔥 最高ライン達成！",
]

LINE_FEELINGS = [
    "未回答",
    "😵 高すぎた",
    "👍 ちょうどよかった",
    "😴 低すぎた",
]

RESULT_RANK = {
    "⏳ まだ判定していない": -1,
    "🌙 届かなかった": 0,
    "🌱 最低ライン達成！": 1,
    "🎯 理想ライン達成！": 2,
    "🔥 最高ライン達成！": 3,
}


# =========================================================
# 共通関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def today_text():
    return str(date.today())


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()
    except (ValueError, TypeError):
        return None


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime("%Y/%m/%d")


def safe_percent(
    numerator,
    denominator,
):
    if denominator == 0:
        return 0.0

    return (
        numerator
        / denominator
        * 100
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "days": [],
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
            "days",
            [],
        )

        for item in data["days"]:
            item.setdefault(
                "id",
                create_id(),
            )
            item.setdefault(
                "date",
                today_text(),
            )
            item.setdefault(
                "category",
                "✨ その他",
            )
            item.setdefault(
                "minimum",
                "",
            )
            item.setdefault(
                "ideal",
                "",
            )
            item.setdefault(
                "maximum",
                "",
            )
            item.setdefault(
                "result",
                "⏳ まだ判定していない",
            )
            item.setdefault(
                "actual",
                "",
            )
            item.setdefault(
                "line_feeling",
                "未回答",
            )
            item.setdefault(
                "memo",
                "",
            )
            item.setdefault(
                "favorite",
                False,
            )
            item.setdefault(
                "created_at",
                now_text(),
            )
            item.setdefault(
                "updated_at",
                item.get(
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
# 取得
# =========================================================

def get_day(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data["days"]
            if item.get("id")
            == item_id
        ),
        None,
    )


def get_day_by_date(
    data,
    target_date,
):
    target = str(
        target_date
    )

    return next(
        (
            item
            for item in data["days"]
            if item.get("date")
            == target
        ),
        None,
    )


# =========================================================
# CRUD
# =========================================================

def add_day(
    data,
    target_date,
    category,
    minimum,
    ideal,
    maximum,
    memo,
):
    if get_day_by_date(
        data,
        target_date,
    ):
        return False

    item = {
        "id": create_id(),
        "date": str(target_date),
        "category": category,
        "minimum": minimum,
        "ideal": ideal,
        "maximum": maximum,
        "result": (
            "⏳ まだ判定していない"
        ),
        "actual": "",
        "line_feeling": "未回答",
        "memo": memo,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["days"].append(
        item
    )

    save_data(data)

    return True


def judge_day(
    data,
    item_id,
    result,
    actual,
    line_feeling,
):
    item = get_day(
        data,
        item_id,
    )

    if not item:
        return

    item["result"] = result
    item["actual"] = actual
    item[
        "line_feeling"
    ] = line_feeling
    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def update_day(
    data,
    item_id,
    category,
    minimum,
    ideal,
    maximum,
    result,
    actual,
    line_feeling,
    memo,
):
    item = get_day(
        data,
        item_id,
    )

    if not item:
        return

    item[
        "category"
    ] = category
    item[
        "minimum"
    ] = minimum
    item[
        "ideal"
    ] = ideal
    item[
        "maximum"
    ] = maximum
    item[
        "result"
    ] = result
    item[
        "actual"
    ] = actual
    item[
        "line_feeling"
    ] = line_feeling
    item[
        "memo"
    ] = memo
    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    item_id,
):
    item = get_day(
        data,
        item_id,
    )

    if not item:
        return

    item[
        "favorite"
    ] = not item.get(
        "favorite",
        False,
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_day(
    data,
    item_id,
):
    data["days"] = [
        item
        for item in data["days"]
        if item.get("id")
        != item_id
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
        background: rgba(100, 180, 130, 0.07);
        border: 1px solid rgba(100, 180, 130, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(90, 180, 120, 0.18),
                rgba(100, 150, 230, 0.10)
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

    .line-card {
        padding: 18px;
        border-radius: 18px;
        margin-bottom: 10px;
        border: 1px solid rgba(130, 130, 130, 0.20);
    }

    .clear-card {
        padding: 20px;
        border-radius: 20px;
        background: rgba(80, 190, 120, 0.10);
        border: 1px solid rgba(80, 190, 120, 0.25);
        margin-top: 15px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

days = data["days"]

today = date.today()
today_string = today_text()
month_prefix = today.strftime(
    "%Y-%m"
)

today_item = get_day_by_date(
    data,
    today_string,
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🏁 今日はどこまででOK？</h1>
        <p>
            全部できなくてもいい。
            今日の合格ラインを、
            自分で決めよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日のダッシュボード
# =========================================================

st.subheader(
    "🏁 今日"
)

if not today_item:
    st.info(
        "今日はまだ合格ラインを"
        "決めていません。"
    )

else:
    col1, col2 = st.columns(
        [8, 1]
    )

    with col1:
        st.caption(
            today_item.get(
                "category",
                "",
            )
        )

    with col2:
        if st.button(
            (
                "⭐"
                if today_item.get(
                    "favorite",
                    False,
                )
                else "☆"
            ),
            key="today_favorite",
        ):
            toggle_favorite(
                data,
                today_item.get(
                    "id"
                ),
            )
            st.rerun()

    st.markdown(
        f"""
        <div class="line-card">
            <b>🌱 最低ライン</b><br>
            {today_item.get("minimum", "")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="line-card">
            <b>🎯 理想ライン</b><br>
            {today_item.get("ideal", "")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="line-card">
            <b>🔥 最高ライン</b><br>
            {today_item.get("maximum", "")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    result = today_item.get(
        "result",
        "⏳ まだ判定していない",
    )

    rank = RESULT_RANK.get(
        result,
        -1,
    )

    if rank >= 1:
        st.markdown(
            """
            <div class="clear-card">
                <b>🎉 今日の合格ライン CLEAR！</b><br>
                自分で決めた「ここまで」に
                届きました。
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif rank == 0:
        st.info(
            "🌙 今日はここまで。"
            "明日の合格ラインは、"
            "また明日決めよう。"
        )

    else:
        st.caption(
            "⏳ まだ今日の結果を"
            "判定していません。"
        )

    st.write(
        "**現在の結果：** "
        + result
    )

    if today_item.get(
        "actual"
    ):
        st.write(
            "**✍️ 実際どこまでできた？**"
        )
        st.write(
            today_item.get(
                "actual",
                "",
            )
        )


# =========================================================
# 今日のライン設定
# =========================================================

if not today_item:
    st.divider()

    st.subheader(
        "🌅 今日の合格ラインを決める"
    )

    with st.form(
        "today_line_form"
    ):
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

        minimum = st.text_input(
            "🌱 最低ライン",
            placeholder=(
                "例：Pythonを10分やる"
            ),
        )

        ideal = st.text_input(
            "🎯 理想ライン",
            placeholder=(
                "例：課題を1問終える"
            ),
        )

        maximum = st.text_input(
            "🔥 最高ライン",
            placeholder=(
                "例：課題を3問終える"
            ),
        )

        memo = st.text_area(
            "📝 今日のメモ",
            placeholder=(
                "体調、予定、"
                "今日意識したいことなど"
            ),
        )

        submitted = (
            st.form_submit_button(
                "🏁 今日のラインを決める",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not minimum.strip():
                st.warning(
                    "最低ラインを"
                    "入力してね。"
                )

            elif not ideal.strip():
                st.warning(
                    "理想ラインを"
                    "入力してね。"
                )

            elif not maximum.strip():
                st.warning(
                    "最高ラインを"
                    "入力してね。"
                )

            else:
                added = add_day(
                    data=data,
                    target_date=today,
                    category=category,
                    minimum=minimum.strip(),
                    ideal=ideal.strip(),
                    maximum=maximum.strip(),
                    memo=memo.strip(),
                )

                if added:
                    st.rerun()
                else:
                    st.warning(
                        "今日はすでに"
                        "記録があります。"
                    )


# =========================================================
# 今日の判定
# =========================================================

if today_item:
    st.divider()

    st.subheader(
        "🌙 今日どこまでいった？"
    )

    with st.form(
        "judge_today_form"
    ):
        current_result = (
            today_item.get(
                "result",
                "⏳ まだ判定していない",
            )
        )

        result_options = [
            "🌙 届かなかった",
            "🌱 最低ライン達成！",
            "🎯 理想ライン達成！",
            "🔥 最高ライン達成！",
        ]

        if (
            current_result
            in result_options
        ):
            result_index = (
                result_options.index(
                    current_result
                )
            )
        else:
            result_index = 1

        result = st.radio(
            "今日の結果",
            result_options,
            index=result_index,
        )

        actual = st.text_area(
            "✍️ 実際どこまでできた？",
            value=today_item.get(
                "actual",
                "",
            ),
            placeholder=(
                "例：Pythonを20分やって、"
                "課題は半分まで進んだ"
            ),
        )

        current_feeling = (
            today_item.get(
                "line_feeling",
                "未回答",
            )
        )

        feeling_options = [
            "😵 高すぎた",
            "👍 ちょうどよかった",
            "😴 低すぎた",
        ]

        if (
            current_feeling
            in feeling_options
        ):
            feeling_index = (
                feeling_options.index(
                    current_feeling
                )
            )
        else:
            feeling_index = 1

        line_feeling = st.radio(
            "💭 今日のライン設定は？",
            feeling_options,
            index=feeling_index,
            horizontal=True,
        )

        submitted = (
            st.form_submit_button(
                "🌙 今日を記録する",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            judge_day(
                data=data,
                item_id=today_item.get(
                    "id"
                ),
                result=result,
                actual=actual.strip(),
                line_feeling=(
                    line_feeling
                ),
            )

            st.rerun()


# =========================================================
# 今月の分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {today.month}月"
)

month_items = [
    item
    for item in days
    if (
        item.get(
            "date",
            "",
        )
        or ""
    ).startswith(
        month_prefix
    )
]

judged_month = [
    item
    for item in month_items
    if RESULT_RANK.get(
        item.get(
            "result",
            "",
        ),
        -1,
    ) >= 0
]

passed_month = [
    item
    for item in judged_month
    if RESULT_RANK.get(
        item.get(
            "result",
            "",
        ),
        0,
    ) >= 1
]

ideal_month = [
    item
    for item in judged_month
    if RESULT_RANK.get(
        item.get(
            "result",
            "",
        ),
        0,
    ) >= 2
]

maximum_month = [
    item
    for item in judged_month
    if RESULT_RANK.get(
        item.get(
            "result",
            "",
        ),
        0,
    ) >= 3
]

missed_month = [
    item
    for item in judged_month
    if RESULT_RANK.get(
        item.get(
            "result",
            "",
        ),
        0,
    ) == 0
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "📅 記録した日",
    f"{len(month_items)}日",
)

col2.metric(
    "🌱 合格",
    f"{len(passed_month)}日",
)

col3.metric(
    "🎯 理想以上",
    f"{len(ideal_month)}日",
)

col4.metric(
    "🔥 最高",
    f"{len(maximum_month)}日",
)

if judged_month:
    pass_rate = safe_percent(
        len(passed_month),
        len(judged_month),
    )

    ideal_rate = safe_percent(
        len(ideal_month),
        len(judged_month),
    )

    maximum_rate = safe_percent(
        len(maximum_month),
        len(judged_month),
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    col1.metric(
        "🏁 合格率",
        f"{pass_rate:.0f}%",
    )

    col2.metric(
        "🎯 理想到達率",
        f"{ideal_rate:.0f}%",
    )

    col3.metric(
        "🔥 最高到達率",
        f"{maximum_rate:.0f}%",
    )

    st.caption(
        "※ 達成率は自分を評価する"
        "点数ではありません。"
        "ライン設定が今の自分に"
        "合っているかを見るための数字です。"
    )


# =========================================================
# 結果グラフ
# =========================================================

if judged_month:
    st.markdown(
        "### 🏁 今月の到達ライン"
    )

    result_counts = {
        "🌙 未達": 0,
        "🌱 最低": 0,
        "🎯 理想": 0,
        "🔥 最高": 0,
    }

    for item in judged_month:
        rank = RESULT_RANK.get(
            item.get(
                "result",
                "",
            ),
            0,
        )

        if rank == 0:
            result_counts[
                "🌙 未達"
            ] += 1

        elif rank == 1:
            result_counts[
                "🌱 最低"
            ] += 1

        elif rank == 2:
            result_counts[
                "🎯 理想"
            ] += 1

        elif rank == 3:
            result_counts[
                "🔥 最高"
            ] += 1

    result_df = pd.DataFrame(
        [
            {
                "到達ライン": key,
                "日数": value,
            }
            for key, value
            in result_counts.items()
        ]
    )

    st.bar_chart(
        result_df.set_index(
            "到達ライン"
        )
    )


# =========================================================
# 直近30日のライン設定分析
# =========================================================

st.divider()

st.subheader(
    "🧠 ライン設定、今の自分に合ってる？"
)

thirty_days_ago = (
    today
    - timedelta(days=29)
)

recent_items = []

for item in days:
    item_date = parse_date(
        item.get(
            "date"
        )
    )

    if (
        item_date
        and thirty_days_ago
        <= item_date
        <= today
        and item.get(
            "line_feeling"
        ) in [
            "😵 高すぎた",
            "👍 ちょうどよかった",
            "😴 低すぎた",
        ]
    ):
        recent_items.append(
            item
        )

if not recent_items:
    st.info(
        "まだ分析できる記録がありません。"
    )

else:
    high_count = sum(
        1
        for item in recent_items
        if item.get(
            "line_feeling"
        ) == "😵 高すぎた"
    )

    good_count = sum(
        1
        for item in recent_items
        if item.get(
            "line_feeling"
        ) == "👍 ちょうどよかった"
    )

    low_count = sum(
        1
        for item in recent_items
        if item.get(
            "line_feeling"
        ) == "😴 低すぎた"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    col1.metric(
        "😵 高すぎた",
        f"{high_count}回",
    )

    col2.metric(
        "👍 ちょうどいい",
        f"{good_count}回",
    )

    col3.metric(
        "😴 低すぎた",
        f"{low_count}回",
    )

    total_feelings = len(
        recent_items
    )

    if (
        high_count
        / total_feelings
        >= 0.4
    ):
        st.info(
            "💡 最近「高すぎた」が"
            "少し多いようです。"
            "最低ラインをもう少し"
            "小さくしてもよさそうです。"
        )

    elif (
        low_count
        / total_feelings
        >= 0.4
    ):
        st.info(
            "🚀 最近「低すぎた」が"
            "少し多いようです。"
            "余力があるなら、"
            "理想ラインを少し上げても"
            "よさそうです。"
        )

    elif (
        good_count
        / total_feelings
        >= 0.5
    ):
        st.success(
            "👍 最近のライン設定は、"
            "今の自分にかなり"
            "合っていそうです。"
        )


# =========================================================
# カテゴリー別合格率
# =========================================================

judged_all = [
    item
    for item in days
    if RESULT_RANK.get(
        item.get(
            "result",
            "",
        ),
        -1,
    ) >= 0
]

if judged_all:
    st.divider()

    st.subheader(
        "🏷️ カテゴリー別の合格率"
    )

    category_rows = []

    for category in CATEGORIES:
        category_items = [
            item
            for item in judged_all
            if item.get(
                "category"
            ) == category
        ]

        if not category_items:
            continue

        category_passed = [
            item
            for item
            in category_items
            if RESULT_RANK.get(
                item.get(
                    "result",
                    "",
                ),
                0,
            ) >= 1
        ]

        rate = safe_percent(
            len(category_passed),
            len(category_items),
        )

        category_rows.append(
            {
                "カテゴリー": category,
                "記録日数": len(
                    category_items
                ),
                "合格日数": len(
                    category_passed
                ),
                "合格率": round(
                    rate,
                    1,
                ),
            }
        )

    if category_rows:
        category_df = (
            pd.DataFrame(
                category_rows
            )
            .sort_values(
                "合格率",
                ascending=False,
            )
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        chart_df = (
            category_df[
                [
                    "カテゴリー",
                    "合格率",
                ]
            ]
            .set_index(
                "カテゴリー"
            )
        )

        st.bar_chart(
            chart_df
        )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    item
    for item in days
    if item.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 残しておきたい日"
    )

    for item in sorted(
        favorites,
        key=lambda row: row.get(
            "date",
            "",
        ),
        reverse=True,
    )[:10]:
        st.write(
            f"⭐ **{format_date(item.get('date'))}**"
            f" — {item.get('minimum', '')}"
            f" → {item.get('result', '')}"
        )


# =========================================================
# ランダム振り返り
# =========================================================

old_items = []

for item in days:
    item_date = parse_date(
        item.get(
            "date"
        )
    )

    if (
        item_date
        and (
            today
            - item_date
        ).days >= 30
    ):
        old_items.append(
            item
        )

if old_items:
    st.divider()

    st.subheader(
        "🎲 こんな日もあった"
    )

    old_ids = [
        item.get(
            "id"
        )
        for item in old_items
    ]

    random_id = (
        st.session_state.get(
            "random_day_id"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_day_id"
        ] = random_id

    random_item = get_day(
        data,
        random_id,
    )

    if random_item:
        with st.container(
            border=True
        ):
            st.caption(
                format_date(
                    random_item.get(
                        "date"
                    )
                )
                + " ｜ "
                + random_item.get(
                    "category",
                    "",
                )
            )

            st.write(
                "**🌱 最低ライン**"
            )
            st.write(
                random_item.get(
                    "minimum",
                    "",
                )
            )

            st.write(
                "**🎯 理想ライン**"
            )
            st.write(
                random_item.get(
                    "ideal",
                    "",
                )
            )

            st.write(
                "**🔥 最高ライン**"
            )
            st.write(
                random_item.get(
                    "maximum",
                    "",
                )
            )

            st.write(
                "**結果**"
            )
            st.write(
                random_item.get(
                    "result",
                    "",
                )
            )

            if random_item.get(
                "actual"
            ):
                st.write(
                    "**✍️ あの日はここまで**"
                )
                st.write(
                    random_item.get(
                        "actual",
                        "",
                    )
                )

        if st.button(
            "🎲 別の日を見る",
            use_container_width=True,
        ):
            alternatives = [
                item_id
                for item_id
                in old_ids
                if item_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_day_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 最低ライン図鑑
# =========================================================

st.divider()

st.subheader(
    "🌱 最低ライン図鑑"
)

search_text = st.text_input(
    "🔎 過去のラインを検索",
    placeholder=(
        "Python、運動、読書……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="history_category",
        )
    )

with col2:
    result_filter = (
        st.selectbox(
            "結果",
            ["すべて"]
            + RESULTS,
            key="history_result",
        )
    )

filtered = []

for item in days:
    if (
        category_filter
        != "すべて"
        and item.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        result_filter
        != "すべて"
        and item.get(
            "result"
        ) != result_filter
    ):
        continue

    searchable = " ".join(
        [
            item.get(
                "minimum",
                "",
            ),
            item.get(
                "ideal",
                "",
            ),
            item.get(
                "maximum",
                "",
            ),
            item.get(
                "actual",
                "",
            ),
            item.get(
                "memo",
                "",
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

    filtered.append(
        item
    )

if not filtered:
    st.info(
        "条件に合う記録はありません。"
    )

else:
    rows = []

    for item in sorted(
        filtered,
        key=lambda row: row.get(
            "date",
            "",
        ),
        reverse=True,
    ):
        rows.append(
            {
                "日付": format_date(
                    item.get(
                        "date"
                    )
                ),
                "カテゴリー": item.get(
                    "category",
                    "",
                ),
                "🌱 最低": item.get(
                    "minimum",
                    "",
                ),
                "🎯 理想": item.get(
                    "ideal",
                    "",
                ),
                "🔥 最高": item.get(
                    "maximum",
                    "",
                ),
                "結果": item.get(
                    "result",
                    "",
                ),
                "ライン設定": item.get(
                    "line_feeling",
                    "",
                ),
                "⭐": (
                    "⭐"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            rows
        ),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・削除"
):
    if not days:
        st.caption(
            "まだ記録がありません。"
        )

    for item in sorted(
        days,
        key=lambda row: row.get(
            "date",
            "",
        ),
        reverse=True,
    ):
        item_id = item.get(
            "id",
            "",
        )

        with st.expander(
            f"{format_date(item.get('date'))}"
            f" ｜ "
            f"{item.get('minimum', '')}"
        ):
            old_category = (
                item.get(
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
                    index=category_index,
                    key=(
                        "edit_category_"
                        + item_id
                    ),
                )
            )

            edit_minimum = (
                st.text_input(
                    "🌱 最低ライン",
                    value=item.get(
                        "minimum",
                        "",
                    ),
                    key=(
                        "edit_minimum_"
                        + item_id
                    ),
                )
            )

            edit_ideal = (
                st.text_input(
                    "🎯 理想ライン",
                    value=item.get(
                        "ideal",
                        "",
                    ),
                    key=(
                        "edit_ideal_"
                        + item_id
                    ),
                )
            )

            edit_maximum = (
                st.text_input(
                    "🔥 最高ライン",
                    value=item.get(
                        "maximum",
                        "",
                    ),
                    key=(
                        "edit_maximum_"
                        + item_id
                    ),
                )
            )

            current_result = (
                item.get(
                    "result",
                    RESULTS[0],
                )
            )

            result_index = (
                RESULTS.index(
                    current_result
                )
                if current_result
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
                        + item_id
                    ),
                )
            )

            edit_actual = (
                st.text_area(
                    "実際どこまでできた？",
                    value=item.get(
                        "actual",
                        "",
                    ),
                    key=(
                        "edit_actual_"
                        + item_id
                    ),
                )
            )

            current_feeling = (
                item.get(
                    "line_feeling",
                    "未回答",
                )
            )

            feeling_index = (
                LINE_FEELINGS.index(
                    current_feeling
                )
                if current_feeling
                in LINE_FEELINGS
                else 0
            )

            edit_feeling = (
                st.selectbox(
                    "ライン設定",
                    LINE_FEELINGS,
                    index=feeling_index,
                    key=(
                        "edit_feeling_"
                        + item_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "メモ",
                    value=item.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + item_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if (
                        not edit_minimum.strip()
                        or not edit_ideal.strip()
                        or not edit_maximum.strip()
                    ):
                        st.warning(
                            "3つのラインを"
                            "入力してね。"
                        )

                    else:
                        update_day(
                            data=data,
                            item_id=item_id,
                            category=(
                                edit_category
                            ),
                            minimum=(
                                edit_minimum.strip()
                            ),
                            ideal=(
                                edit_ideal.strip()
                            ),
                            maximum=(
                                edit_maximum.strip()
                            ),
                            result=(
                                edit_result
                            ),
                            actual=(
                                edit_actual.strip()
                            ),
                            line_feeling=(
                                edit_feeling
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "fav_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )
                    st.rerun()

            st.markdown(
                "#### 🗑️ 完全削除"
            )

            confirm = st.checkbox(
                "この日の記録を削除する",
                key=(
                    "confirm_"
                    + item_id
                ),
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + item_id
                ),
                disabled=not confirm,
                use_container_width=True,
            ):
                delete_day(
                    data,
                    item_id,
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
            "today_enough_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "🏁 全部できなくてもいい。"
    "自分で決めた「ここまで」に届けば、"
    "今日は合格。"
)

st.caption(
    "🌱 最低ラインは、妥協じゃない。"
    "今日も前へ進むためのスタートライン。"
)
