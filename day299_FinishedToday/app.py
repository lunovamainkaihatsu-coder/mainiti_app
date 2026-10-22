import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日、何を終わらせた？",
    page_icon="🏁",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "completions.json",
)

SIZES = [
    "🌱 小さい",
    "🔨 普通",
    "🏆 大きい",
]

CATEGORIES = [
    "📚 勉強",
    "💻 開発",
    "💼 仕事",
    "🏠 生活",
    "📄 手続き",
    "👨‍👩‍👧 家族",
    "🏃 運動",
    "🎨 創作",
    "💰 お金",
    "✨ その他",
]

WEEKDAY_NAMES = {
    0: "月曜日",
    1: "火曜日",
    2: "水曜日",
    3: "木曜日",
    4: "金曜日",
    5: "土曜日",
    6: "日曜日",
}


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


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

    return parsed.strftime(
        "%Y/%m/%d"
    )


def days_to_finish(
    completion,
):
    start = parse_date(
        completion.get(
            "start_date"
        )
    )

    end = parse_date(
        completion.get(
            "date"
        )
    )

    if not start or not end:
        return None

    if start > end:
        return None

    return (
        end - start
    ).days + 1


def duration_text(
    completion,
):
    days = days_to_finish(
        completion
    )

    if days is None:
        return "-"

    if days == 1:
        return "1日"

    return f"{days}日"


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "completions": [],
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
            "completions",
            [],
        )

        for item in data[
            "completions"
        ]:
            item.setdefault(
                "id",
                create_id(),
            )
            item.setdefault(
                "title",
                "",
            )
            item.setdefault(
                "date",
                str(date.today()),
            )
            item.setdefault(
                "start_date",
                "",
            )
            item.setdefault(
                "size",
                "🌱 小さい",
            )
            item.setdefault(
                "category",
                "✨ その他",
            )
            item.setdefault(
                "minutes",
                0,
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

def get_completion(
    data,
    completion_id,
):
    return next(
        (
            item
            for item
            in data[
                "completions"
            ]
            if item.get(
                "id"
            ) == completion_id
        ),
        None,
    )


def sorted_completions(
    data,
    reverse=True,
):
    return sorted(
        data["completions"],
        key=lambda item: (
            item.get(
                "date",
                "",
            ),
            item.get(
                "created_at",
                "",
            ),
        ),
        reverse=reverse,
    )


def completions_for_date(
    items,
    target_date,
):
    target_text = str(
        target_date
    )

    return [
        item
        for item in items
        if item.get(
            "date"
        ) == target_text
    ]


def completions_for_month(
    items,
    year,
    month,
):
    result = []

    for item in items:
        parsed = parse_date(
            item.get(
                "date"
            )
        )

        if (
            parsed
            and parsed.year == year
            and parsed.month == month
        ):
            result.append(item)

    return result


def completions_for_year(
    items,
    year,
):
    result = []

    for item in items:
        parsed = parse_date(
            item.get(
                "date"
            )
        )

        if (
            parsed
            and parsed.year == year
        ):
            result.append(item)

    return result


# =========================================================
# CRUD
# =========================================================

def add_completion(
    data,
    title,
    completion_date,
    start_date,
    size,
    category,
    minutes,
    memo,
    favorite,
):
    item = {
        "id": create_id(),
        "title": title,
        "date": str(
            completion_date
        ),
        "start_date": (
            str(start_date)
            if start_date
            else ""
        ),
        "size": size,
        "category": category,
        "minutes": int(
            minutes
        ),
        "memo": memo,
        "favorite": favorite,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["completions"].append(
        item
    )

    save_data(data)

    return item


def update_completion(
    data,
    completion_id,
    title,
    completion_date,
    start_date,
    size,
    category,
    minutes,
    memo,
):
    item = get_completion(
        data,
        completion_id,
    )

    if not item:
        return False

    item["title"] = title
    item["date"] = str(
        completion_date
    )
    item["start_date"] = (
        str(start_date)
        if start_date
        else ""
    )
    item["size"] = size
    item["category"] = category
    item["minutes"] = int(
        minutes
    )
    item["memo"] = memo
    item[
        "updated_at"
    ] = now_text()

    save_data(data)

    return True


def toggle_favorite(
    data,
    completion_id,
):
    item = get_completion(
        data,
        completion_id,
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


def delete_completion(
    data,
    completion_id,
):
    data["completions"] = [
        item
        for item
        in data["completions"]
        if item.get(
            "id"
        ) != completion_id
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
        background: rgba(70, 170, 110, 0.07);
        border: 1px solid rgba(70, 170, 110, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(70, 180, 110, 0.18),
                rgba(230, 180, 70, 0.12)
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

    .completion-card {
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(80, 150, 100, 0.16);
        background: rgba(80, 150, 100, 0.05);
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 準備
# =========================================================

data = load_data()
items = data["completions"]

today = date.today()

today_items = completions_for_date(
    items,
    today,
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🏁 今日、何を終わらせた？</h1>
        <p>
            やることではなく、
            もう終えたものを残しておこう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 新規完了
# =========================================================

st.subheader(
    "🏁 完了を記録"
)

with st.form(
    "new_completion",
    clear_on_submit=True,
):
    title = st.text_input(
        "何を終わらせた？",
        placeholder=(
            "例：299本目の"
            "アプリを完成させた"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        completion_date = (
            st.date_input(
                "🏁 完了日",
                value=today,
                max_value=today,
            )
        )

    with col2:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

    size = st.radio(
        "大きさ",
        SIZES,
        horizontal=True,
        index=1,
    )

    has_start_date = (
        st.checkbox(
            "📅 開始日も記録する"
        )
    )

    start_date = None

    if has_start_date:
        start_date = st.date_input(
            "開始日",
            value=completion_date,
            max_value=(
                completion_date
            ),
        )

    minutes = st.number_input(
        "⏱️ かかった時間（分・任意）",
        min_value=0,
        max_value=100000,
        value=0,
        step=5,
        help=(
            "分からなければ0でOK。"
        ),
    )

    memo = st.text_area(
        "💭 一言メモ（任意）",
        placeholder=(
            "例：300本まであと1本。"
        ),
    )

    favorite = st.checkbox(
        "⭐ 忘れたくない完了にする"
    )

    submitted = (
        st.form_submit_button(
            "🏁 完了を記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        clean_title = (
            title.strip()
        )

        if not clean_title:
            st.warning(
                "終わらせたことを"
                "入力してね。"
            )

        else:
            item = add_completion(
                data=data,
                title=clean_title,
                completion_date=(
                    completion_date
                ),
                start_date=(
                    start_date
                ),
                size=size,
                category=category,
                minutes=minutes,
                memo=memo.strip(),
                favorite=favorite,
            )

            st.session_state[
                "last_completion"
            ] = item.get(
                "id"
            )

            st.rerun()


# =========================================================
# 保存直後
# =========================================================

last_completion_id = (
    st.session_state.get(
        "last_completion"
    )
)

if last_completion_id:
    last_item = get_completion(
        data,
        last_completion_id,
    )

    if last_item:
        same_day_items = (
            completions_for_date(
                items,
                parse_date(
                    last_item.get(
                        "date"
                    )
                ),
            )
        )

        st.success(
            "🎉 完了！\n\n"
            f"{last_item.get('size')} "
            f"**{last_item.get('title')}**\n\n"
            f"この日 {len(same_day_items)}個目の"
            "完了です。\n\n"
            "🏁 またひとつ、"
            "自分の手から離れました。"
        )

    if st.button(
        "OK",
        key="clear_last_completion",
    ):
        del st.session_state[
            "last_completion"
        ]

        st.rerun()


# =========================================================
# 今日
# =========================================================

st.divider()

st.subheader(
    "🌙 今日終わらせたこと"
)

today_items = completions_for_date(
    items,
    today,
)

if not today_items:
    st.info(
        "今日はまだ完了記録がありません。\n\n"
        "小さなことでも、"
        "終わったらここに置いておこう。"
    )

else:
    for item in sorted(
        today_items,
        key=lambda row: row.get(
            "created_at",
            "",
        ),
        reverse=True,
    ):
        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [8, 1]
            )

            with col1:
                st.write(
                    f"{item.get('size')} "
                    f"**{item.get('title')}**"
                )

                st.caption(
                    item.get(
                        "category",
                        ""
                    )
                )

                if item.get(
                    "memo"
                ):
                    st.caption(
                        "💭 "
                        + item.get(
                            "memo"
                        )
                    )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "today_fav_"
                        + item.get(
                            "id"
                        )
                    ),
                ):
                    toggle_favorite(
                        data,
                        item.get(
                            "id"
                        ),
                    )

                    st.rerun()

    st.success(
        f"🏁 今日の完了："
        f"{len(today_items)}個"
    )


# =========================================================
# ダッシュボード
# =========================================================

st.divider()

st.subheader(
    "📊 完了ダッシュボード"
)

month_items = completions_for_month(
    items,
    today.year,
    today.month,
)

week_start = (
    today
    - timedelta(
        days=6
    )
)

week_items = []

for item in items:
    parsed = parse_date(
        item.get(
            "date"
        )
    )

    if (
        parsed
        and week_start
        <= parsed
        <= today
    ):
        week_items.append(
            item
        )

big_items = [
    item
    for item in items
    if item.get(
        "size"
    ) == "🏆 大きい"
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🏁 総完了",
    f"{len(items)}個",
)

col2.metric(
    "🌙 今日",
    f"{len(today_items)}個",
)

col3.metric(
    "📅 今月",
    f"{len(month_items)}個",
)

col4.metric(
    "🏆 大きな完了",
    f"{len(big_items)}個",
)

st.caption(
    f"🔥 最近7日で"
    f"{len(week_items)}個完了しています。"
)


# =========================================================
# 大きな完了
# =========================================================

if big_items:
    st.divider()

    st.subheader(
        "🏆 大きな完了"
    )

    for item in sorted(
        big_items,
        key=lambda row: row.get(
            "date",
            "",
        ),
        reverse=True,
    )[:10]:
        with st.container(
            border=True
        ):
            st.write(
                f"🏆 **{item.get('title')}**"
            )

            st.caption(
                f"{format_date(item.get('date'))}"
                f" ｜ "
                f"{item.get('category', '')}"
            )

            days = days_to_finish(
                item
            )

            if days:
                st.caption(
                    f"⏳ {days}日かけて完了"
                )

            if item.get(
                "memo"
            ):
                st.write(
                    item.get(
                        "memo"
                    )
                )


# =========================================================
# 月間レポート
# =========================================================

if items:
    st.divider()

    st.subheader(
        "📅 月間完了レポート"
    )

    available_years = sorted(
        {
            parsed.year
            for item in items
            if (
                parsed := parse_date(
                    item.get(
                        "date"
                    )
                )
            )
        }
        | {today.year},
        reverse=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        report_year = (
            st.selectbox(
                "年",
                available_years,
                index=(
                    available_years.index(
                        today.year
                    )
                    if today.year
                    in available_years
                    else 0
                ),
                key="report_year",
            )
        )

    with col2:
        report_month = (
            st.selectbox(
                "月",
                list(
                    range(1, 13)
                ),
                index=(
                    today.month - 1
                ),
                format_func=lambda x: (
                    f"{x}月"
                ),
                key="report_month",
            )
        )

    report_items = (
        completions_for_month(
            items,
            report_year,
            report_month,
        )
    )

    st.metric(
        "🏁 この月の完了",
        f"{len(report_items)}個",
    )

    if not report_items:
        st.info(
            "この月の完了記録は"
            "ありません。"
        )

    else:
        size_counts = Counter(
            item.get(
                "size"
            )
            for item in report_items
        )

        c1, c2, c3 = (
            st.columns(3)
        )

        c1.metric(
            "🌱 小さい",
            size_counts.get(
                "🌱 小さい",
                0,
            ),
        )

        c2.metric(
            "🔨 普通",
            size_counts.get(
                "🔨 普通",
                0,
            ),
        )

        c3.metric(
            "🏆 大きい",
            size_counts.get(
                "🏆 大きい",
                0,
            ),
        )

        category_counts = Counter(
            item.get(
                "category"
            )
            for item in report_items
        )

        category_df = pd.DataFrame(
            {
                "カテゴリー": (
                    list(
                        category_counts.keys()
                    )
                ),
                "完了数": (
                    list(
                        category_counts.values()
                    )
                ),
            }
        ).set_index(
            "カテゴリー"
        )

        st.markdown(
            "#### 📊 カテゴリー別"
        )

        st.bar_chart(
            category_df
        )


# =========================================================
# 月別推移
# =========================================================

if items:
    st.divider()

    st.subheader(
        "📈 完了の積み重ね"
    )

    trend_year = st.selectbox(
        "表示する年",
        available_years,
        key="trend_year",
    )

    trend_rows = []

    for month in range(
        1,
        13,
    ):
        count = len(
            completions_for_month(
                items,
                trend_year,
                month,
            )
        )

        trend_rows.append(
            {
                "月": f"{month}月",
                "完了数": count,
            }
        )

    trend_df = pd.DataFrame(
        trend_rows
    ).set_index(
        "月"
    )

    st.bar_chart(
        trend_df
    )

    st.caption(
        "多い・少ないを評価するグラフではなく、"
        "終わらせてきたものの記録です。"
    )


# =========================================================
# 曜日傾向
# =========================================================

if items:
    st.divider()

    st.subheader(
        "🗓️ 完了した曜日"
    )

    weekday_counts = Counter()

    for item in items:
        parsed = parse_date(
            item.get(
                "date"
            )
        )

        if parsed:
            weekday_counts[
                parsed.weekday()
            ] += 1

    weekday_rows = []

    for weekday in range(7):
        weekday_rows.append(
            {
                "曜日": (
                    WEEKDAY_NAMES[
                        weekday
                    ]
                ),
                "完了数": (
                    weekday_counts.get(
                        weekday,
                        0,
                    )
                ),
            }
        )

    weekday_df = pd.DataFrame(
        weekday_rows
    ).set_index(
        "曜日"
    )

    st.bar_chart(
        weekday_df
    )

    if weekday_counts:
        best_weekday = max(
            weekday_counts,
            key=(
                weekday_counts.get
            ),
        )

        st.caption(
            "これまで最も完了記録が"
            f"多いのは"
            f"「{WEEKDAY_NAMES[best_weekday]}」"
            "です。"
        )


# =========================================================
# 年間
# =========================================================

if items:
    st.divider()

    st.subheader(
        "🏅 今年終わらせたもの"
    )

    yearly_year = st.selectbox(
        "年",
        available_years,
        key="yearly_year",
    )

    yearly_items = (
        completions_for_year(
            items,
            yearly_year,
        )
    )

    yearly_big = [
        item
        for item in yearly_items
        if item.get(
            "size"
        ) == "🏆 大きい"
    ]

    yearly_categories = Counter(
        item.get(
            "category"
        )
        for item in yearly_items
    )

    top_category = (
        yearly_categories.most_common(
            1
        )[0]
        if yearly_categories
        else None
    )

    c1, c2, c3 = (
        st.columns(3)
    )

    c1.metric(
        "🏁 完了",
        f"{len(yearly_items)}個",
    )

    c2.metric(
        "🏆 大きな完了",
        f"{len(yearly_big)}個",
    )

    c3.metric(
        "最多カテゴリー",
        (
            top_category[0]
            if top_category
            else "-"
        ),
    )

    if yearly_big:
        st.markdown(
            "#### 🏆 この年の大きな完了"
        )

        for item in sorted(
            yearly_big,
            key=lambda row: row.get(
                "date",
                "",
            ),
            reverse=True,
        ):
            st.write(
                f"**{format_date(item.get('date'))}** "
                f"— {item.get('title')}"
            )


# =========================================================
# 昔の完了ガチャ
# =========================================================

old_items = []

for item in items:
    parsed = parse_date(
        item.get(
            "date"
        )
    )

    if (
        parsed
        and (
            today - parsed
        ).days >= 30
    ):
        old_items.append(
            item
        )

if old_items:
    st.divider()

    st.subheader(
        "🎲 昔こんなこと終わらせた"
    )

    old_ids = [
        item.get("id")
        for item in old_items
    ]

    random_id = (
        st.session_state.get(
            "random_completion"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_completion"
        ] = random_id

    random_item = get_completion(
        data,
        random_id,
    )

    if random_item:
        parsed = parse_date(
            random_item.get(
                "date"
            )
        )

        days_ago = (
            (today - parsed).days
            if parsed
            else 0
        )

        with st.container(
            border=True
        ):
            st.caption(
                f"🎲 {days_ago}日前"
            )

            st.subheader(
                f"{random_item.get('size')} "
                f"{random_item.get('title')}"
            )

            st.caption(
                f"{format_date(random_item.get('date'))}"
                f" ｜ "
                f"{random_item.get('category', '')}"
            )

            if random_item.get(
                "memo"
            ):
                st.write(
                    f"💭 {random_item.get('memo')}"
                )

            st.success(
                "🏁 あの時も、"
                "ちゃんと終わらせた。"
            )

        if st.button(
            "🎲 別の完了を見る",
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
                    "random_completion"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# お気に入り
# =========================================================

favorites = [
    item
    for item in items
    if item.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ 忘れたくない完了"
    )

    for item in sorted(
        favorites,
        key=lambda row: row.get(
            "date",
            "",
        ),
        reverse=True,
    ):
        st.write(
            f"{item.get('size')} "
            f"**{item.get('title')}**"
        )

        st.caption(
            f"{format_date(item.get('date'))}"
            f" ｜ "
            f"{item.get('category', '')}"
        )


# =========================================================
# 完了図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 完了図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "Python、アプリ、書類……"
    ),
)

filter_col1, filter_col2 = (
    st.columns(2)
)

with filter_col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="library_category",
        )
    )

with filter_col2:
    size_filter = st.selectbox(
        "大きさ",
        ["すべて"]
        + SIZES,
        key="library_size",
    )

favorite_only = st.checkbox(
    "⭐ 忘れたくない完了だけ",
    key="library_favorite",
)

filtered_items = []

for item in items:
    if (
        category_filter
        != "すべて"
        and item.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        size_filter
        != "すべて"
        and item.get(
            "size"
        ) != size_filter
    ):
        continue

    if (
        favorite_only
        and not item.get(
            "favorite",
            False,
        )
    ):
        continue

    searchable = " ".join(
        [
            item.get(
                "title",
                "",
            ),
            item.get(
                "memo",
                "",
            ),
            item.get(
                "category",
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

    filtered_items.append(
        item
    )

if not filtered_items:
    st.info(
        "条件に合う完了は"
        "ありません。"
    )

else:
    rows = []

    for item in sorted(
        filtered_items,
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
                "完了したこと": (
                    item.get(
                        "title",
                        "",
                    )
                ),
                "大きさ": (
                    item.get(
                        "size",
                        "",
                    )
                ),
                "カテゴリー": (
                    item.get(
                        "category",
                        "",
                    )
                ),
                "所要日数": (
                    duration_text(
                        item
                    )
                ),
                "時間": (
                    (
                        f"{item.get('minutes')}分"
                    )
                    if item.get(
                        "minutes",
                        0,
                    ) > 0
                    else "-"
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
    if not items:
        st.caption(
            "まだ完了記録がありません。"
        )

    else:
        edit_options = {}

        for item in sorted_completions(
            data
        ):
            short_title = item.get(
                "title",
                "",
            )

            if len(
                short_title
            ) > 30:
                short_title = (
                    short_title[:30]
                    + "…"
                )

            label = (
                f"{format_date(item.get('date'))}"
                f" ｜ "
                f"{short_title}"
            )

            edit_options[
                label
            ] = item.get(
                "id"
            )

        selected_label = (
            st.selectbox(
                "編集する完了",
                list(
                    edit_options.keys()
                ),
            )
        )

        selected_id = (
            edit_options[
                selected_label
            ]
        )

        selected = get_completion(
            data,
            selected_id,
        )

        if selected:
            edit_title = st.text_input(
                "完了したこと",
                value=selected.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + selected_id
                ),
            )

            selected_date = (
                parse_date(
                    selected.get(
                        "date"
                    )
                )
                or today
            )

            edit_date = st.date_input(
                "完了日",
                value=selected_date,
                max_value=today,
                key=(
                    "edit_date_"
                    + selected_id
                ),
            )

            has_old_start = bool(
                selected.get(
                    "start_date"
                )
            )

            edit_has_start = (
                st.checkbox(
                    "開始日を記録する",
                    value=(
                        has_old_start
                    ),
                    key=(
                        "edit_has_start_"
                        + selected_id
                    ),
                )
            )

            edit_start_date = None

            if edit_has_start:
                old_start = (
                    parse_date(
                        selected.get(
                            "start_date"
                        )
                    )
                    or edit_date
                )

                if old_start > edit_date:
                    old_start = edit_date

                edit_start_date = (
                    st.date_input(
                        "開始日",
                        value=old_start,
                        max_value=(
                            edit_date
                        ),
                        key=(
                            "edit_start_"
                            + selected_id
                        ),
                    )
                )

            old_size = selected.get(
                "size",
                "🌱 小さい",
            )

            size_index = (
                SIZES.index(
                    old_size
                )
                if old_size
                in SIZES
                else 0
            )

            edit_size = st.selectbox(
                "大きさ",
                SIZES,
                index=size_index,
                key=(
                    "edit_size_"
                    + selected_id
                ),
            )

            old_category = (
                selected.get(
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
                        + selected_id
                    ),
                )
            )

            edit_minutes = (
                st.number_input(
                    "時間（分）",
                    min_value=0,
                    max_value=100000,
                    value=int(
                        selected.get(
                            "minutes",
                            0,
                        )
                    ),
                    step=5,
                    key=(
                        "edit_minutes_"
                        + selected_id
                    ),
                )
            )

            edit_memo = st.text_area(
                "メモ",
                value=selected.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + selected_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + selected_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "完了したことを"
                            "入力してね。"
                        )

                    else:
                        update_completion(
                            data=data,
                            completion_id=(
                                selected_id
                            ),
                            title=(
                                edit_title.strip()
                            ),
                            completion_date=(
                                edit_date
                            ),
                            start_date=(
                                edit_start_date
                            ),
                            size=edit_size,
                            category=(
                                edit_category
                            ),
                            minutes=(
                                edit_minutes
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
                        if selected.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "edit_favorite_"
                        + selected_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        selected_id,
                    )

                    st.rerun()

            st.divider()

            st.warning(
                "削除すると元には戻せません。"
            )

            delete_confirm = (
                st.checkbox(
                    "この完了記録を削除する",
                    key=(
                        "delete_confirm_"
                        + selected_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + selected_id
                ),
                disabled=(
                    not delete_confirm
                ),
                use_container_width=True,
            ):
                delete_completion(
                    data,
                    selected_id,
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
            "finished_today_"
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
    "🏁 終わったことは、"
    "もう目の前にはない。"
    "だからこそ、記録しておこう。"
)

st.caption(
    "✨ 振り返れば、"
    "自分が思っていたより"
    "たくさんのものを"
    "終わらせてきた。"
)
