import json
import os
import random
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="まだ使ってる？",
    page_icon="📦",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "items.json",
)

CATEGORIES = [
    "📱 ガジェット",
    "👕 衣類",
    "🏠 家具・家電",
    "🎮 趣味",
    "📚 本・学習",
    "🍳 キッチン",
    "🚗 車",
    "💼 仕事",
    "💄 美容・ケア",
    "✨ その他",
]

FREQUENCIES = [
    "🔥 ほぼ毎日",
    "😊 週に数回",
    "🙂 月に数回",
    "😴 ほぼ使わない",
    "📦 使っていない",
]

REBUY_OPTIONS = [
    "◎ また買う",
    "△ 分からない",
    "× 買わない",
]

MILESTONES = [
    30,
    90,
    180,
    365,
]

ACTIVE_FREQUENCIES = [
    "🔥 ほぼ毎日",
    "😊 週に数回",
    "🙂 月に数回",
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


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            str(value),
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


def format_money(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    return f"¥{value:,.0f}"


def stars(value):
    try:
        value = int(
            round(float(value))
        )
    except (TypeError, ValueError):
        return "-"

    value = max(
        0,
        min(
            value,
            5,
        ),
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def short_text(
    text,
    length=35,
):
    text = text or ""

    if len(text) <= length:
        return text

    return (
        text[:length]
        + "…"
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "items": [],
        "reviews": [],
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
            data = json.load(
                file
            )

        if not isinstance(
            data,
            dict,
        ):
            data = empty_data()

        data.setdefault(
            "items",
            [],
        )

        data.setdefault(
            "reviews",
            [],
        )

        for item in data["items"]:
            if not item.get("id"):
                item["id"] = (
                    create_id()
                )

            item.setdefault(
                "name",
                "",
            )
            item.setdefault(
                "category",
                "✨ その他",
            )
            item.setdefault(
                "purchase_date",
                str(date.today()),
            )
            item.setdefault(
                "price",
                0,
            )
            item.setdefault(
                "expectation",
                "",
            )
            item.setdefault(
                "initial_rating",
                3,
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

        for review in data[
            "reviews"
        ]:
            if not review.get("id"):
                review["id"] = (
                    create_id()
                )

            review.setdefault(
                "item_id",
                "",
            )
            review.setdefault(
                "date",
                str(date.today()),
            )
            review.setdefault(
                "frequency",
                "🙂 月に数回",
            )
            review.setdefault(
                "rating",
                3,
            )
            review.setdefault(
                "usefulness",
                3,
            )
            review.setdefault(
                "rebuy",
                "△ 分からない",
            )
            review.setdefault(
                "estimated_uses",
                0,
            )
            review.setdefault(
                "memo",
                "",
            )
            review.setdefault(
                "created_at",
                now_text(),
            )
            review.setdefault(
                "updated_at",
                review.get(
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

def get_item(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data["items"]
            if item.get("id")
            == item_id
        ),
        None,
    )


def get_review(
    data,
    review_id,
):
    return next(
        (
            review
            for review
            in data["reviews"]
            if review.get("id")
            == review_id
        ),
        None,
    )


def item_reviews(
    data,
    item_id,
):
    return sorted(
        [
            review
            for review
            in data["reviews"]
            if review.get(
                "item_id"
            ) == item_id
        ],
        key=lambda review: (
            review.get(
                "date",
                "",
            ),
            review.get(
                "created_at",
                "",
            ),
        ),
    )


def latest_review(
    data,
    item_id,
):
    reviews = item_reviews(
        data,
        item_id,
    )

    if not reviews:
        return None

    return reviews[-1]


def days_owned(
    item,
    target_date=None,
):
    if target_date is None:
        target_date = date.today()

    purchase_date = parse_date(
        item.get(
            "purchase_date"
        )
    )

    if not purchase_date:
        return 0

    return max(
        0,
        (
            target_date
            - purchase_date
        ).days,
    )


def item_label(item):
    return (
        f"{item.get('name', '')}"
        f" ｜ "
        f"{format_date(item.get('purchase_date'))}"
    )


# =========================================================
# 再評価
# =========================================================

def completed_milestones(
    item,
    reviews,
):
    purchase_date = parse_date(
        item.get(
            "purchase_date"
        )
    )

    completed = set()

    if not purchase_date:
        return completed

    for review in reviews:
        review_date = parse_date(
            review.get("date")
        )

        if not review_date:
            continue

        review_day = (
            review_date
            - purchase_date
        ).days

        for milestone in (
            MILESTONES
        ):
            if (
                review_day
                >= milestone
            ):
                completed.add(
                    milestone
                )

    return completed


def next_milestone(
    item,
    reviews,
):
    age = days_owned(
        item
    )

    completed = (
        completed_milestones(
            item,
            reviews,
        )
    )

    for milestone in (
        MILESTONES
    ):
        if (
            age >= milestone
            and milestone
            not in completed
        ):
            return milestone

    return None


# =========================================================
# CRUD
# =========================================================

def add_item(
    data,
    name,
    category,
    purchase_date,
    price,
    expectation,
    initial_rating,
    memo,
    favorite,
):
    item = {
        "id": create_id(),
        "name": name,
        "category": category,
        "purchase_date": str(
            purchase_date
        ),
        "price": float(price),
        "expectation": expectation,
        "initial_rating": int(
            initial_rating
        ),
        "memo": memo,
        "favorite": favorite,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["items"].append(
        item
    )

    save_data(data)

    return item


def add_review(
    data,
    item_id,
    review_date,
    frequency,
    rating,
    usefulness,
    rebuy,
    estimated_uses,
    memo,
):
    review = {
        "id": create_id(),
        "item_id": item_id,
        "date": str(
            review_date
        ),
        "frequency": frequency,
        "rating": int(
            rating
        ),
        "usefulness": int(
            usefulness
        ),
        "rebuy": rebuy,
        "estimated_uses": int(
            estimated_uses
        ),
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["reviews"].append(
        review
    )

    save_data(data)

    return review


def toggle_favorite(
    data,
    item_id,
):
    item = get_item(
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


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item in data["items"]
        if item.get(
            "id"
        ) != item_id
    ]

    data["reviews"] = [
        review
        for review
        in data["reviews"]
        if review.get(
            "item_id"
        ) != item_id
    ]

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background:
            rgba(90, 150, 210, .06);
        border:
            1px solid
            rgba(90, 150, 210, .15);
    }

    .hero {
        text-align: center;
        padding: 38px 25px;
        margin-bottom: 25px;
        border-radius: 28px;
        background:
            linear-gradient(
                135deg,
                rgba(80, 160, 230, .13),
                rgba(220, 170, 70, .10)
            );
    }

    .footer-card {
        text-align: center;
        padding: 28px;
        border-radius: 24px;
        margin-top: 30px;
        background:
            rgba(100, 150, 180, .05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 準備
# =========================================================

data = load_data()

items = data["items"]
reviews = data["reviews"]

today = date.today()


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>📅 DAY 302 / 365</div>
        <h1>📦 まだ使ってる？</h1>
        <p>
            買った瞬間ではなく、
            時間が経ったあとに
            本当の価値を確かめる。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# タブ
# =========================================================

(
    tab_home,
    tab_review,
    tab_analysis,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🏠 ホーム",
        "👀 再評価",
        "📊 分析",
        "📚 買ったもの図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    # -----------------------------------------------------
    # ダッシュボード
    # -----------------------------------------------------

    st.subheader(
        "📊 買い物ダッシュボード"
    )

    total_price = sum(
        float(
            item.get(
                "price",
                0,
            )
        )
        for item in items
    )

    active_items = []

    sleeping_items = []

    latest_ratings = []

    active_value = 0

    for item in items:
        review = latest_review(
            data,
            item.get("id"),
        )

        if review:
            latest_ratings.append(
                int(
                    review.get(
                        "rating",
                        0,
                    )
                )
            )

            frequency = (
                review.get(
                    "frequency"
                )
            )

            if (
                frequency
                in ACTIVE_FREQUENCIES
            ):
                active_items.append(
                    item
                )

                active_value += float(
                    item.get(
                        "price",
                        0,
                    )
                )

            elif frequency in [
                "😴 ほぼ使わない",
                "📦 使っていない",
            ]:
                sleeping_items.append(
                    item
                )

    average_rating = (
        sum(latest_ratings)
        / len(latest_ratings)
        if latest_ratings
        else 0
    )

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "📦 登録",
        f"{len(items)}個",
    )

    c2.metric(
        "💰 購入総額",
        format_money(
            total_price
        ),
    )

    c3.metric(
        "😊 今も使用中",
        f"{len(active_items)}個",
    )

    c4.metric(
        "⭐ 平均満足度",
        (
            f"{average_rating:.1f}/5"
            if latest_ratings
            else "-"
        ),
    )

    if items:
        st.caption(
            "💰 現在も使っている物の"
            "購入総額："
            f"**{format_money(active_value)}**"
        )

    # -----------------------------------------------------
    # 新規登録
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "📦 買ったものを登録"
    )

    with st.form(
        "new_item",
        clear_on_submit=True,
    ):
        item_name = st.text_input(
            "商品名",
            placeholder=(
                "例：ワイヤレスイヤホン"
            ),
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            item_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                )
            )

        with col2:
            purchase_date = (
                st.date_input(
                    "購入日",
                    value=today,
                    max_value=today,
                )
            )

        price = st.number_input(
            "購入価格",
            min_value=0,
            value=0,
            step=100,
        )

        expectation = (
            st.text_area(
                "何を期待して買った？",
                placeholder=(
                    "仕事中に快適に"
                    "音楽を聴きたい"
                ),
            )
        )

        initial_rating = (
            st.slider(
                "購入直後の満足度",
                min_value=1,
                max_value=5,
                value=4,
            )
        )

        item_memo = st.text_area(
            "メモ（任意）"
        )

        favorite = st.checkbox(
            "⭐ 特別な買い物として残す"
        )

        if st.form_submit_button(
            "📦 登録",
            type="primary",
            use_container_width=True,
        ):
            if not item_name.strip():
                st.warning(
                    "商品名を入力してね。"
                )

            else:
                add_item(
                    data=data,
                    name=item_name.strip(),
                    category=(
                        item_category
                    ),
                    purchase_date=(
                        purchase_date
                    ),
                    price=price,
                    expectation=(
                        expectation.strip()
                    ),
                    initial_rating=(
                        initial_rating
                    ),
                    memo=(
                        item_memo.strip()
                    ),
                    favorite=favorite,
                )

                st.rerun()

    # -----------------------------------------------------
    # 再評価時期
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "⏰ そろそろ振り返ろう"
    )

    due_items = []

    for item in items:
        milestone = (
            next_milestone(
                item,
                item_reviews(
                    data,
                    item.get("id"),
                ),
            )
        )

        if milestone:
            due_items.append(
                (
                    item,
                    milestone,
                )
            )

    if not due_items:
        st.caption(
            "今のところ、"
            "節目の再評価待ちは"
            "ありません。"
        )

    else:
        for (
            item,
            milestone,
        ) in due_items:
            with st.container(
                border=True
            ):
                st.write(
                    f"**{item.get('name')}**"
                )

                st.caption(
                    f"購入から "
                    f"{days_owned(item)}日"
                )

                st.info(
                    f"🎯 {milestone}日レビュー"
                )

    # -----------------------------------------------------
    # 最近登録した物
    # -----------------------------------------------------

    if items:
        st.divider()

        st.subheader(
            "🛍️ 最近登録したもの"
        )

        sorted_items = sorted(
            items,
            key=lambda item: (
                item.get(
                    "purchase_date",
                    ""
                ),
                item.get(
                    "created_at",
                    ""
                ),
            ),
            reverse=True,
        )

        for item in sorted_items[
            :8
        ]:
            review = latest_review(
                data,
                item.get("id"),
            )

            with st.container(
                border=True
            ):
                col1, col2 = (
                    st.columns(
                        [8, 1]
                    )
                )

                with col1:
                    st.write(
                        f"**{item.get('name')}**"
                    )

                    st.caption(
                        f"{item.get('category')}"
                        f" ｜ "
                        f"{format_money(item.get('price'))}"
                        f" ｜ "
                        f"購入から{days_owned(item)}日"
                    )

                    if review:
                        st.write(
                            f"{review.get('frequency')} "
                            f"｜ "
                            f"{stars(review.get('rating'))}"
                        )

                    else:
                        st.write(
                            "👀 まだ再評価していません"
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
                            "home_fav_"
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


# =========================================================
# REVIEW
# =========================================================

with tab_review:

    st.subheader(
        "👀 まだ使ってる？"
    )

    if not items:
        st.info(
            "まず買ったものを"
            "登録してみよう。"
        )

    else:
        review_options = {
            item_label(item):
            item.get("id")
            for item in items
        }

        selected_label = (
            st.selectbox(
                "振り返るもの",
                list(
                    review_options.keys()
                ),
                key="review_item",
            )
        )

        selected_id = (
            review_options[
                selected_label
            ]
        )

        selected_item = get_item(
            data,
            selected_id,
        )

        selected_reviews = (
            item_reviews(
                data,
                selected_id,
            )
        )

        age = days_owned(
            selected_item
        )

        st.markdown(
            f"### 📦 "
            f"{selected_item.get('name')}"
        )

        c1, c2, c3 = (
            st.columns(3)
        )

        c1.metric(
            "購入から",
            f"{age}日",
        )

        c2.metric(
            "購入価格",
            format_money(
                selected_item.get(
                    "price"
                )
            ),
        )

        c3.metric(
            "購入時評価",
            (
                f"{selected_item.get('initial_rating')}/5"
            ),
        )

        milestone = next_milestone(
            selected_item,
            selected_reviews,
        )

        if milestone:
            st.info(
                f"🎯 現在 "
                f"{milestone}日レビューの"
                "タイミングです。"
            )

        with st.form(
            "new_review",
            clear_on_submit=True,
        ):
            review_date = (
                st.date_input(
                    "レビュー日",
                    value=today,
                    min_value=(
                        parse_date(
                            selected_item.get(
                                "purchase_date"
                            )
                        )
                    ),
                    max_value=today,
                )
            )

            frequency = (
                st.selectbox(
                    "現在の使用頻度",
                    FREQUENCIES,
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                rating = st.slider(
                    "現在の満足度",
                    1,
                    5,
                    4,
                )

            with col2:
                usefulness = (
                    st.slider(
                        "役に立ってる？",
                        1,
                        5,
                        4,
                    )
                )

            rebuy = st.radio(
                "もう一度買う？",
                REBUY_OPTIONS,
                horizontal=True,
            )

            estimated_uses = (
                st.number_input(
                    "これまで何回くらい使った？（任意）",
                    min_value=0,
                    value=0,
                    step=1,
                )
            )

            review_memo = (
                st.text_area(
                    "今の感想",
                    placeholder=(
                        "想像以上に"
                        "仕事で使っている"
                    ),
                )
            )

            if st.form_submit_button(
                "👀 今の状態を記録",
                type="primary",
                use_container_width=True,
            ):
                add_review(
                    data=data,
                    item_id=selected_id,
                    review_date=(
                        review_date
                    ),
                    frequency=frequency,
                    rating=rating,
                    usefulness=(
                        usefulness
                    ),
                    rebuy=rebuy,
                    estimated_uses=(
                        estimated_uses
                    ),
                    memo=(
                        review_memo.strip()
                    ),
                )

                st.rerun()

        # -------------------------------------------------
        # コスパ
        # -------------------------------------------------

        latest = latest_review(
            data,
            selected_id,
        )

        if latest:
            st.divider()

            st.subheader(
                "💰 今の価値"
            )

            c1, c2, c3 = (
                st.columns(3)
            )

            c1.metric(
                "満足度",
                f"{latest.get('rating')}/5",
            )

            c2.metric(
                "役立ち度",
                f"{latest.get('usefulness')}/5",
            )

            c3.metric(
                "再購入",
                latest.get(
                    "rebuy"
                ),
            )

            uses = int(
                latest.get(
                    "estimated_uses",
                    0,
                )
            )

            price_value = float(
                selected_item.get(
                    "price",
                    0,
                )
            )

            if uses > 0:
                cost_per_use = (
                    price_value
                    / uses
                )

                st.success(
                    "💰 推定1回あたり "
                    f"**{format_money(cost_per_use)}**"
                    f"\n\n"
                    f"{format_money(price_value)} ÷ "
                    f"{uses:,}回"
                )

        # -------------------------------------------------
        # 満足度推移
        # -------------------------------------------------

        if selected_reviews:
            st.divider()

            st.subheader(
                "📈 満足度の変化"
            )

            purchase_date = (
                parse_date(
                    selected_item.get(
                        "purchase_date"
                    )
                )
            )

            chart_rows = [
                {
                    "日付": (
                        purchase_date
                    ),
                    "満足度": int(
                        selected_item.get(
                            "initial_rating",
                            3,
                        )
                    ),
                }
            ]

            for review in (
                selected_reviews
            ):
                review_date_value = (
                    parse_date(
                        review.get(
                            "date"
                        )
                    )
                )

                if review_date_value:
                    chart_rows.append(
                        {
                            "日付": (
                                review_date_value
                            ),
                            "満足度": int(
                                review.get(
                                    "rating",
                                    3,
                                )
                            ),
                        }
                    )

            chart_df = pd.DataFrame(
                chart_rows
            )

            chart_df = (
                chart_df
                .sort_values(
                    "日付"
                )
                .set_index(
                    "日付"
                )
            )

            st.line_chart(
                chart_df
            )

            initial_rating = int(
                selected_item.get(
                    "initial_rating",
                    3,
                )
            )

            latest_rating = int(
                selected_reviews[
                    -1
                ].get(
                    "rating",
                    3,
                )
            )

            difference = (
                latest_rating
                - initial_rating
            )

            if difference > 0:
                diff_text = (
                    f"+{difference}"
                )
            else:
                diff_text = str(
                    difference
                )

            st.caption(
                f"購入直後 "
                f"{initial_rating}/5"
                f" → 現在 "
                f"{latest_rating}/5"
                f"（{diff_text}）"
            )

            st.markdown(
                "#### 📝 レビュー履歴"
            )

            for review in reversed(
                selected_reviews
            ):
                with st.container(
                    border=True
                ):
                    st.write(
                        f"**{format_date(review.get('date'))}** "
                        f"— "
                        f"{stars(review.get('rating'))}"
                    )

                    st.caption(
                        f"{review.get('frequency')}"
                        f" ｜ "
                        f"{review.get('rebuy')}"
                    )

                    if review.get(
                        "memo"
                    ):
                        st.write(
                            review.get(
                                "memo"
                            )
                        )


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    if not items:
        st.info(
            "商品とレビューが増えると、"
            "ここに分析が表示されます。"
        )

    else:
        # -------------------------------------------------
        # 買ってよかった
        # -------------------------------------------------

        st.subheader(
            "🏆 本当に買ってよかった"
        )

        ranking = []

        for item in items:
            item_review_list = (
                item_reviews(
                    data,
                    item.get("id"),
                )
            )

            if not item_review_list:
                continue

            latest = (
                item_review_list[-1]
            )

            rating_values = [
                int(
                    review.get(
                        "rating",
                        0,
                    )
                )
                for review
                in item_review_list
            ]

            avg_rating = (
                sum(rating_values)
                / len(rating_values)
            )

            longevity_bonus = min(
                days_owned(item)
                / 365,
                1,
            ) * 0.25

            score = (
                avg_rating
                + longevity_bonus
            )

            ranking.append(
                (
                    score,
                    avg_rating,
                    item,
                    latest,
                )
            )

        ranking.sort(
            key=lambda row: row[0],
            reverse=True,
        )

        if not ranking:
            st.caption(
                "レビューすると"
                "ランキングが表示されます。"
            )

        else:
            for index, (
                score,
                avg_rating,
                item,
                latest,
            ) in enumerate(
                ranking[:10],
                start=1,
            ):
                with st.container(
                    border=True
                ):
                    st.write(
                        f"**{index}. "
                        f"{item.get('name')}**"
                    )

                    st.caption(
                        f"平均満足度 "
                        f"{avg_rating:.1f}/5"
                        f" ｜ "
                        f"{latest.get('frequency')}"
                        f" ｜ "
                        f"{days_owned(item)}日"
                    )

        # -------------------------------------------------
        # 眠っているもの
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "😴 最近使っていない"
        )

        if not sleeping_items:
            st.caption(
                "現在「ほぼ使わない」"
                "「使っていない」と"
                "評価されたものはありません。"
            )

        else:
            for item in sorted(
                sleeping_items,
                key=days_owned,
                reverse=True,
            ):
                review = latest_review(
                    data,
                    item.get("id"),
                )

                with st.container(
                    border=True
                ):
                    st.write(
                        f"**{item.get('name')}**"
                    )

                    st.caption(
                        f"{format_money(item.get('price'))}"
                        f" ｜ "
                        f"購入から{days_owned(item)}日"
                    )

                    st.write(
                        review.get(
                            "frequency"
                        )
                    )

                    st.caption(
                        "今は使われていません。"
                    )

        # -------------------------------------------------
        # 長寿
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "🏅 長く使っているもの"
        )

        longevity = []

        for item in items:
            review = latest_review(
                data,
                item.get("id"),
            )

            if (
                review
                and review.get(
                    "frequency"
                )
                in ACTIVE_FREQUENCIES
            ):
                longevity.append(
                    item
                )

        longevity.sort(
            key=days_owned,
            reverse=True,
        )

        if not longevity:
            st.caption(
                "現在使用中の商品を"
                "レビューすると表示されます。"
            )

        else:
            for index, item in enumerate(
                longevity[:10],
                start=1,
            ):
                st.write(
                    f"**{index}. "
                    f"{item.get('name')}** "
                    f"— {days_owned(item)}日"
                )

        # -------------------------------------------------
        # 再購入
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "🔁 もう一度買う？"
        )

        rebuy_counts = Counter()

        for item in items:
            review = latest_review(
                data,
                item.get("id"),
            )

            if review:
                rebuy_counts[
                    review.get(
                        "rebuy"
                    )
                ] += 1

        if rebuy_counts:
            rebuy_df = (
                pd.DataFrame(
                    [
                        {
                            "判定": option,
                            "個数": (
                                rebuy_counts.get(
                                    option,
                                    0,
                                )
                            ),
                        }
                        for option
                        in REBUY_OPTIONS
                    ]
                )
                .set_index(
                    "判定"
                )
            )

            st.bar_chart(
                rebuy_df
            )

        # -------------------------------------------------
        # カテゴリー分析
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "📊 カテゴリー分析"
        )

        category_rows = []

        for category in (
            CATEGORIES
        ):
            category_items = [
                item
                for item in items
                if item.get(
                    "category"
                ) == category
            ]

            if not category_items:
                continue

            category_price = sum(
                float(
                    item.get(
                        "price",
                        0,
                    )
                )
                for item
                in category_items
            )

            reviewed = []
            active_count = 0
            rebuy_yes = 0

            for item in (
                category_items
            ):
                review = latest_review(
                    data,
                    item.get("id"),
                )

                if not review:
                    continue

                reviewed.append(
                    review
                )

                if (
                    review.get(
                        "frequency"
                    )
                    in ACTIVE_FREQUENCIES
                ):
                    active_count += 1

                if (
                    review.get(
                        "rebuy"
                    )
                    == "◎ また買う"
                ):
                    rebuy_yes += 1

            avg_rating = (
                sum(
                    int(
                        review.get(
                            "rating",
                            0,
                        )
                    )
                    for review
                    in reviewed
                )
                / len(reviewed)
                if reviewed
                else 0
            )

            active_rate = (
                active_count
                / len(reviewed)
                * 100
                if reviewed
                else 0
            )

            rebuy_rate = (
                rebuy_yes
                / len(reviewed)
                * 100
                if reviewed
                else 0
            )

            category_rows.append(
                {
                    "カテゴリー": (
                        category
                    ),
                    "登録数": len(
                        category_items
                    ),
                    "購入額": (
                        format_money(
                            category_price
                        )
                    ),
                    "平均満足度": (
                        f"{avg_rating:.1f}"
                        if reviewed
                        else "-"
                    ),
                    "現役率": (
                        f"{active_rate:.0f}%"
                        if reviewed
                        else "-"
                    ),
                    "また買う率": (
                        f"{rebuy_rate:.0f}%"
                        if reviewed
                        else "-"
                    ),
                }
            )

        if category_rows:
            st.dataframe(
                pd.DataFrame(
                    category_rows
                ),
                hide_index=True,
                use_container_width=True,
            )

        # -------------------------------------------------
        # 昔買ったこれ
        # -------------------------------------------------

        old_items = [
            item
            for item in items
            if days_owned(item)
            >= 180
        ]

        if old_items:
            st.divider()

            st.subheader(
                "🎲 昔買ったこれ、どう？"
            )

            old_ids = [
                item.get("id")
                for item in old_items
            ]

            random_id = (
                st.session_state.get(
                    "random_old_item"
                )
            )

            if random_id not in (
                old_ids
            ):
                random_id = (
                    random.choice(
                        old_ids
                    )
                )

                st.session_state[
                    "random_old_item"
                ] = random_id

            old_item = get_item(
                data,
                random_id,
            )

            old_review = latest_review(
                data,
                random_id,
            )

            with st.container(
                border=True
            ):
                st.caption(
                    f"🎲 "
                    f"{days_owned(old_item)}日前に購入"
                )

                st.markdown(
                    f"### "
                    f"{old_item.get('name')}"
                )

                st.write(
                    format_money(
                        old_item.get(
                            "price"
                        )
                    )
                )

                if old_review:
                    st.write(
                        f"{old_review.get('frequency')}"
                        f" ｜ "
                        f"{stars(old_review.get('rating'))}"
                    )

                else:
                    st.write(
                        "👀 まだ再評価していません"
                    )

            if st.button(
                "🎲 別のものを見る",
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
                        "random_old_item"
                    ] = random.choice(
                        alternatives
                    )

                st.rerun()


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 買ったもの図鑑"
    )

    search_text = st.text_input(
        "🔎 商品検索",
        key="library_search",
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
        frequency_filter = (
            st.selectbox(
                "現在の使用状態",
                ["すべて"]
                + FREQUENCIES
                + ["未評価"],
                key=(
                    "library_frequency"
                ),
            )
        )

    with col3:
        rebuy_filter = (
            st.selectbox(
                "再購入",
                ["すべて"]
                + REBUY_OPTIONS
                + ["未評価"],
                key=(
                    "library_rebuy"
                ),
            )
        )

    favorite_only = (
        st.checkbox(
            "⭐ 特別なものだけ"
        )
    )

    rows = []

    for item in items:
        review = latest_review(
            data,
            item.get("id"),
        )

        if (
            category_filter
            != "すべて"
            and item.get(
                "category"
            )
            != category_filter
        ):
            continue

        current_frequency = (
            review.get(
                "frequency"
            )
            if review
            else "未評価"
        )

        current_rebuy = (
            review.get(
                "rebuy"
            )
            if review
            else "未評価"
        )

        if (
            frequency_filter
            != "すべて"
            and current_frequency
            != frequency_filter
        ):
            continue

        if (
            rebuy_filter
            != "すべて"
            and current_rebuy
            != rebuy_filter
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
                    "name",
                    "",
                ),
                item.get(
                    "category",
                    "",
                ),
                item.get(
                    "expectation",
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

        rows.append(
            {
                "商品": (
                    item.get("name")
                ),
                "カテゴリー": (
                    item.get(
                        "category"
                    )
                ),
                "購入日": (
                    format_date(
                        item.get(
                            "purchase_date"
                        )
                    )
                ),
                "価格": (
                    format_money(
                        item.get(
                            "price"
                        )
                    )
                ),
                "使用期間": (
                    f"{days_owned(item)}日"
                ),
                "現在": (
                    current_frequency
                ),
                "満足度": (
                    (
                        f"{review.get('rating')}/5"
                    )
                    if review
                    else (
                        f"{item.get('initial_rating')}/5"
                    )
                ),
                "再購入": (
                    current_rebuy
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

    if not rows:
        st.info(
            "条件に合うものは"
            "ありません。"
        )

    else:
        st.dataframe(
            pd.DataFrame(
                rows
            ),
            hide_index=True,
            use_container_width=True,
        )

    # -----------------------------------------------------
    # お気に入り
    # -----------------------------------------------------

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
            "⭐ これは残したい"
        )

        for item in sorted(
            favorites,
            key=days_owned,
            reverse=True,
        ):
            st.write(
                f"⭐ **{item.get('name')}** "
                f"— 購入から"
                f"{days_owned(item)}日"
            )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 商品を編集"
    )

    if not items:
        st.info(
            "まだ商品がありません。"
        )

    else:
        manage_options = {
            (
                f"{item_label(item)} "
                f"[{item.get('id')[:6]}]"
            ):
            item.get("id")
            for item in items
        }

        manage_label = (
            st.selectbox(
                "商品",
                list(
                    manage_options.keys()
                ),
                key="manage_item",
            )
        )

        manage_id = (
            manage_options[
                manage_label
            ]
        )

        manage_item = get_item(
            data,
            manage_id,
        )

        edit_name = st.text_input(
            "商品名",
            value=manage_item.get(
                "name",
                "",
            ),
        )

        old_category = (
            manage_item.get(
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
                key="edit_category",
            )
        )

        edit_purchase_date = (
            st.date_input(
                "購入日",
                value=(
                    parse_date(
                        manage_item.get(
                            "purchase_date"
                        )
                    )
                    or today
                ),
                max_value=today,
                key="edit_purchase_date",
            )
        )

        edit_price = (
            st.number_input(
                "購入価格",
                min_value=0.0,
                value=float(
                    manage_item.get(
                        "price",
                        0,
                    )
                ),
                step=100.0,
            )
        )

        edit_expectation = (
            st.text_area(
                "期待していたこと",
                value=manage_item.get(
                    "expectation",
                    "",
                ),
            )
        )

        edit_initial_rating = (
            st.slider(
                "購入直後の満足度",
                1,
                5,
                int(
                    manage_item.get(
                        "initial_rating",
                        3,
                    )
                ),
            )
        )

        edit_memo = st.text_area(
            "メモ",
            value=manage_item.get(
                "memo",
                "",
            ),
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            if st.button(
                "💾 商品情報を保存",
                type="primary",
                use_container_width=True,
            ):
                if not edit_name.strip():
                    st.warning(
                        "商品名を入力してね。"
                    )

                else:
                    manage_item[
                        "name"
                    ] = edit_name.strip()

                    manage_item[
                        "category"
                    ] = edit_category

                    manage_item[
                        "purchase_date"
                    ] = str(
                        edit_purchase_date
                    )

                    manage_item[
                        "price"
                    ] = float(
                        edit_price
                    )

                    manage_item[
                        "expectation"
                    ] = (
                        edit_expectation
                        .strip()
                    )

                    manage_item[
                        "initial_rating"
                    ] = int(
                        edit_initial_rating
                    )

                    manage_item[
                        "memo"
                    ] = (
                        edit_memo.strip()
                    )

                    manage_item[
                        "updated_at"
                    ] = now_text()

                    save_data(data)

                    st.rerun()

        with col2:
            if st.button(
                (
                    "⭐ 特別から外す"
                    if manage_item.get(
                        "favorite",
                        False,
                    )
                    else "☆ 特別なものにする"
                ),
                use_container_width=True,
            ):
                toggle_favorite(
                    data,
                    manage_id,
                )

                st.rerun()

        # -------------------------------------------------
        # レビュー編集
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "📝 レビューを編集"
        )

        manage_reviews = (
            item_reviews(
                data,
                manage_id,
            )
        )

        if not manage_reviews:
            st.caption(
                "まだレビューがありません。"
            )

        else:
            review_options = {}

            for review in reversed(
                manage_reviews
            ):
                label = (
                    f"{format_date(review.get('date'))}"
                    f" ｜ "
                    f"{review.get('rating')}/5"
                    f" ｜ "
                    f"{review.get('frequency')}"
                    f" [{review.get('id')[:6]}]"
                )

                review_options[
                    label
                ] = review.get(
                    "id"
                )

            review_label = (
                st.selectbox(
                    "レビュー",
                    list(
                        review_options.keys()
                    ),
                    key=(
                        "manage_review"
                    ),
                )
            )

            review_id = (
                review_options[
                    review_label
                ]
            )

            review = get_review(
                data,
                review_id,
            )

            edit_review_date = (
                st.date_input(
                    "レビュー日",
                    value=(
                        parse_date(
                            review.get(
                                "date"
                            )
                        )
                        or today
                    ),
                    min_value=(
                        parse_date(
                            manage_item.get(
                                "purchase_date"
                            )
                        )
                    ),
                    max_value=today,
                    key=(
                        "edit_review_date"
                    ),
                )
            )

            frequency_index = (
                FREQUENCIES.index(
                    review.get(
                        "frequency"
                    )
                )
                if review.get(
                    "frequency"
                )
                in FREQUENCIES
                else 0
            )

            edit_frequency = (
                st.selectbox(
                    "使用頻度",
                    FREQUENCIES,
                    index=frequency_index,
                    key=(
                        "edit_frequency"
                    ),
                )
            )

            edit_rating = (
                st.slider(
                    "満足度",
                    1,
                    5,
                    int(
                        review.get(
                            "rating",
                            3,
                        )
                    ),
                    key=(
                        "edit_rating"
                    ),
                )
            )

            edit_usefulness = (
                st.slider(
                    "役立ち度",
                    1,
                    5,
                    int(
                        review.get(
                            "usefulness",
                            3,
                        )
                    ),
                    key=(
                        "edit_usefulness"
                    ),
                )
            )

            rebuy_index = (
                REBUY_OPTIONS.index(
                    review.get(
                        "rebuy"
                    )
                )
                if review.get(
                    "rebuy"
                )
                in REBUY_OPTIONS
                else 1
            )

            edit_rebuy = (
                st.selectbox(
                    "もう一度買う？",
                    REBUY_OPTIONS,
                    index=rebuy_index,
                    key=(
                        "edit_rebuy"
                    ),
                )
            )

            edit_uses = (
                st.number_input(
                    "推定使用回数",
                    min_value=0,
                    value=int(
                        review.get(
                            "estimated_uses",
                            0,
                        )
                    ),
                    step=1,
                    key="edit_uses",
                )
            )

            edit_review_memo = (
                st.text_area(
                    "感想",
                    value=review.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_review_memo"
                    ),
                )
            )

            if st.button(
                "💾 レビューを保存",
                use_container_width=True,
            ):
                review[
                    "date"
                ] = str(
                    edit_review_date
                )

                review[
                    "frequency"
                ] = edit_frequency

                review[
                    "rating"
                ] = int(
                    edit_rating
                )

                review[
                    "usefulness"
                ] = int(
                    edit_usefulness
                )

                review[
                    "rebuy"
                ] = edit_rebuy

                review[
                    "estimated_uses"
                ] = int(
                    edit_uses
                )

                review[
                    "memo"
                ] = (
                    edit_review_memo
                    .strip()
                )

                review[
                    "updated_at"
                ] = now_text()

                save_data(data)

                st.rerun()

            delete_review_confirm = (
                st.checkbox(
                    "このレビューを削除する",
                    key=(
                        "delete_review_confirm_"
                        + review_id
                    ),
                )
            )

            if st.button(
                "🗑️ レビューを削除",
                disabled=(
                    not delete_review_confirm
                ),
                key=(
                    "delete_review_"
                    + review_id
                ),
                use_container_width=True,
            ):
                data["reviews"] = [
                    row
                    for row
                    in data["reviews"]
                    if row.get(
                        "id"
                    ) != review_id
                ]

                save_data(data)

                st.rerun()

        # -------------------------------------------------
        # 商品削除
        # -------------------------------------------------

        st.divider()

        st.warning(
            "商品を削除すると、"
            "この商品に紐づくレビューも"
            "すべて削除されます。"
        )

        delete_item_confirm = (
            st.checkbox(
                "商品ごと削除する",
                key=(
                    "delete_item_confirm_"
                    + manage_id
                ),
            )
        )

        if st.button(
            "🗑️ 商品を完全削除",
            disabled=(
                not delete_item_confirm
            ),
            key=(
                "delete_item_"
                + manage_id
            ),
            use_container_width=True,
        ):
            delete_item(
                data,
                manage_id,
            )

            st.rerun()

    # -----------------------------------------------------
    # バックアップ
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            "still_using_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer-card">
        <p>
            📦 <b>
            買った瞬間のワクワクより、
            半年後も使っているか。
            </b>
        </p>

        <p>
            👀 時間が経ってから分かる
            「買ってよかった」もある。
        </p>

        <br>

        <b>DAY 302 / 365 — COMPLETE 🔥</b>
    </div>
    """,
    unsafe_allow_html=True,
)
