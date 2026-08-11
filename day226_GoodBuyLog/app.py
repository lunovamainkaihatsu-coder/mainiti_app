import json
import os
import uuid
from collections import Counter
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="買ってよかった物ログ",
    page_icon="🛍️",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "good_buy_data.json",
)

CATEGORIES = [
    "食品",
    "外食",
    "服",
    "家電",
    "PC・ガジェット",
    "日用品",
    "車",
    "趣味",
    "ゲーム",
    "本",
    "子ども用品",
    "健康",
    "美容",
    "サブスク",
    "旅行",
    "その他",
]

USAGE_FREQUENCIES = [
    "まだ使っていない",
    "ほとんど使わない",
    "月に数回",
    "週に1〜2回",
    "週に3〜5回",
    "ほぼ毎日",
]

REPURCHASE_OPTIONS = [
    "絶対また買いたい",
    "また買いたい",
    "どちらでもない",
    "たぶん買わない",
    "もう買わない",
]

REPURCHASE_SCORES = {
    "絶対また買いたい": 5,
    "また買いたい": 4,
    "どちらでもない": 3,
    "たぶん買わない": 2,
    "もう買わない": 1,
}


# =========================================================
# データ管理
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "items": []
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


def normalize_data(data):
    if not isinstance(
        data,
        dict,
    ):
        data = create_empty_data()

    data.setdefault(
        "items",
        [],
    )

    for item in data["items"]:
        item.setdefault(
            "id",
            create_id(),
        )

        item.setdefault(
            "name",
            "",
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
            "category",
            "その他",
        )

        item.setdefault(
            "shop",
            "",
        )

        item.setdefault(
            "purchase_reason",
            "",
        )

        item.setdefault(
            "satisfaction",
            3,
        )

        item.setdefault(
            "cost_performance",
            3,
        )

        item.setdefault(
            "usage_frequency",
            "まだ使っていない",
        )

        item.setdefault(
            "usage_count",
            0,
        )

        item.setdefault(
            "repurchase",
            "どちらでもない",
        )

        item.setdefault(
            "good_points",
            "",
        )

        item.setdefault(
            "regret_points",
            "",
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
            "review_history",
            [],
        )

        item.setdefault(
            "created_at",
            "",
        )

        item.setdefault(
            "updated_at",
            "",
        )

    return data


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE,
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

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE,
            ):
                os.replace(
                    DATA_FILE,
                    broken_file,
                )

        except OSError:
            pass

        data = create_empty_data()
        save_data(data)

        return data


# =========================================================
# 補助関数
# =========================================================

def parse_date(date_text):
    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

    except (
        TypeError,
        ValueError,
    ):
        return None


def format_date(date_text):
    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "未設定"

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
        parsed.weekday()
    ]

    return parsed.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_item_by_id(
    data,
    item_id,
):
    for item in data["items"]:
        if item.get(
            "id"
        ) == item_id:
            return item

    return None


def average_value(
    items,
    key,
):
    if not items:
        return 0

    values = [
        float(
            item.get(
                key,
                0,
            )
        )
        for item in items
    ]

    if not values:
        return 0

    return (
        sum(values)
        / len(values)
    )


def cost_per_use(
    item,
):
    usage_count = int(
        item.get(
            "usage_count",
            0,
        )
    )

    price = int(
        item.get(
            "price",
            0,
        )
    )

    if usage_count <= 0:
        return None

    return (
        price
        / usage_count
    )


def days_since_purchase(
    item,
):
    purchase_date = parse_date(
        item.get(
            "purchase_date",
            "",
        )
    )

    if not purchase_date:
        return None

    return (
        date.today()
        - purchase_date
    ).days


# =========================================================
# データ操作
# =========================================================

def add_item(
    data,
    values,
):
    item = {
        "id": create_id(),
        "name": values["name"],
        "purchase_date": (
            values["purchase_date"]
        ),
        "price": int(
            values["price"]
        ),
        "category": values["category"],
        "shop": values["shop"],
        "purchase_reason": (
            values["purchase_reason"]
        ),
        "satisfaction": int(
            values["satisfaction"]
        ),
        "cost_performance": int(
            values["cost_performance"]
        ),
        "usage_frequency": (
            values["usage_frequency"]
        ),
        "usage_count": int(
            values["usage_count"]
        ),
        "repurchase": (
            values["repurchase"]
        ),
        "good_points": (
            values["good_points"]
        ),
        "regret_points": (
            values["regret_points"]
        ),
        "memo": values["memo"],
        "favorite": False,
        "review_history": [],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["items"].append(
        item
    )

    save_data(data)


def update_item(
    data,
    item_id,
    values,
):
    item = get_item_by_id(
        data,
        item_id
    )

    if not item:
        return

    for key, value in values.items():
        item[key] = value

    item["price"] = int(
        item.get(
            "price",
            0,
        )
    )

    item["satisfaction"] = int(
        item.get(
            "satisfaction",
            3,
        )
    )

    item["cost_performance"] = int(
        item.get(
            "cost_performance",
            3,
        )
    )

    item["usage_count"] = int(
        item.get(
            "usage_count",
            0,
        )
    )

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item in data[
            "items"
        ]
        if item.get(
            "id"
        ) != item_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    item_id,
):
    item = get_item_by_id(
        data,
        item_id
    )

    if not item:
        return

    item["favorite"] = not bool(
        item.get(
            "favorite",
            False,
        )
    )

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def add_review(
    data,
    item_id,
    values,
):
    item = get_item_by_id(
        data,
        item_id
    )

    if not item:
        return

    review = {
        "id": create_id(),
        "review_date": (
            values["review_date"]
        ),
        "satisfaction": int(
            values["satisfaction"]
        ),
        "cost_performance": int(
            values["cost_performance"]
        ),
        "usage_frequency": (
            values["usage_frequency"]
        ),
        "usage_count": int(
            values["usage_count"]
        ),
        "repurchase": (
            values["repurchase"]
        ),
        "comment": values["comment"],
        "created_at": now_text(),
    }

    item["review_history"].append(
        review
    )

    item["satisfaction"] = int(
        values["satisfaction"]
    )

    item["cost_performance"] = int(
        values["cost_performance"]
    )

    item["usage_frequency"] = (
        values["usage_frequency"]
    )

    item["usage_count"] = int(
        values["usage_count"]
    )

    item["repurchase"] = (
        values["repurchase"]
    )

    item["updated_at"] = (
        now_text()
    )

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
        background: rgba(255, 155, 80, 0.08);
        border: 1px solid rgba(255, 155, 80, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(255, 155, 80, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(255, 155, 80, 0.18),
                rgba(255, 210, 100, 0.12)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 読み込み
# =========================================================

data = load_data()

items = data[
    "items"
]

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🛍️ 買ってよかった物ログ</h1>
        <p>
            お金を使ってよかった物を記録して、
            自分に合う買い物を見つけるアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

monthly_items = [
    item
    for item in items
    if item.get(
        "purchase_date",
        "",
    ).startswith(
        current_month
    )
]

favorite_items = [
    item
    for item in items
    if item.get(
        "favorite",
        False,
    )
]

high_satisfaction_items = [
    item
    for item in items
    if int(
        item.get(
            "satisfaction",
            0,
        )
    ) == 5
]

repurchase_items = [
    item
    for item in items
    if item.get(
        "repurchase"
    )
    in [
        "絶対また買いたい",
        "また買いたい",
    ]
]

total_spent = sum(
    int(
        item.get(
            "price",
            0,
        )
    )
    for item in items
)

monthly_spent = sum(
    int(
        item.get(
            "price",
            0,
        )
    )
    for item in monthly_items
)

average_satisfaction = (
    average_value(
        items,
        "satisfaction",
    )
)

repurchase_rate = (
    len(
        repurchase_items
    )
    / len(items)
    * 100
    if items
    else 0
)


category_scores = {}

for item in items:
    category = item.get(
        "category",
        "その他",
    )

    category_scores.setdefault(
        category,
        [],
    ).append(
        int(
            item.get(
                "satisfaction",
                0,
            )
        )
    )

best_category = "なし"
best_category_score = 0

for category, scores in category_scores.items():
    if scores:
        score = (
            sum(scores)
            / len(scores)
        )

        if score > best_category_score:
            best_category = category
            best_category_score = score


metric_row1 = st.columns(4)

metric_row1[0].metric(
    "総購入数",
    f"{len(items)}件"
)

metric_row1[1].metric(
    "総購入金額",
    f"{total_spent:,}円"
)

metric_row1[2].metric(
    "今月の購入額",
    f"{monthly_spent:,}円"
)

metric_row1[3].metric(
    "平均満足度",
    (
        f"{average_satisfaction:.1f}/5"
        if items
        else "未記録"
    )
)


metric_row2 = st.columns(4)

metric_row2[0].metric(
    "満足度5",
    f"{len(high_satisfaction_items)}件"
)

metric_row2[1].metric(
    "また買いたい割合",
    f"{repurchase_rate:.1f}%"
)

metric_row2[2].metric(
    "お気に入り",
    f"{len(favorite_items)}件"
)

metric_row2[3].metric(
    "満足度トップ分類",
    best_category
)


# =========================================================
# ベストバイ
# =========================================================

if items:
    best_items = sorted(
        items,
        key=lambda item: (
            int(
                item.get(
                    "satisfaction",
                    0,
                )
            ),
            int(
                item.get(
                    "cost_performance",
                    0,
                )
            ),
            REPURCHASE_SCORES.get(
                item.get(
                    "repurchase",
                    "",
                ),
                0,
            ),
        ),
        reverse=True,
    )

    best_item = best_items[0]

    st.divider()

    st.subheader(
        "🏆 現在のベストバイ"
    )

    with st.container(
        border=True
    ):
        column1, column2 = (
            st.columns(
                [
                    4,
                    1,
                ]
            )
        )

        with column1:
            st.markdown(
                f"### "
                f"{best_item.get('name', '')}"
            )

            st.caption(
                f"{best_item.get('category', '')} ／ "
                f"{format_date(best_item.get('purchase_date', ''))}"
            )

            if best_item.get(
                "good_points",
                "",
            ):
                st.success(
                    "買ってよかった理由\n\n"
                    + best_item.get(
                        "good_points",
                        "",
                    )
                )

        with column2:
            st.metric(
                "満足度",
                f"{best_item.get('satisfaction', 0)}/5"
            )

            st.metric(
                "コスパ",
                f"{best_item.get('cost_performance', 0)}/5"
            )


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    review_tab,
    favorite_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 購入記録",
        "📚 買った物一覧",
        "🔄 再評価",
        "⭐ お気に入り",
        "📈 買い物分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 購入記録
# =========================================================

with add_tab:
    st.header(
        "➕ 買ってよかった物を登録"
    )

    with st.form(
        "add_item_form",
        clear_on_submit=True
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            purchase_date_input = (
                st.date_input(
                    "購入日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

            item_name = st.text_input(
                "商品・サービス名",
                placeholder=(
                    "例：ワイヤレスイヤホン"
                ),
            )

            price = st.number_input(
                "購入価格",
                min_value=0,
                max_value=100000000,
                value=5000,
                step=100,
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            shop = st.text_input(
                "購入場所",
                placeholder=(
                    "Amazon、家電量販店など"
                ),
            )

        with column2:
            satisfaction = st.slider(
                "満足度",
                min_value=1,
                max_value=5,
                value=4,
            )

            cost_performance = (
                st.slider(
                    "コスパ",
                    min_value=1,
                    max_value=5,
                    value=4,
                )
            )

            usage_frequency = (
                st.selectbox(
                    "使用頻度",
                    USAGE_FREQUENCIES,
                )
            )

            usage_count = st.number_input(
                "これまでの使用回数",
                min_value=0,
                max_value=1000000,
                value=0,
                step=1,
            )

            repurchase = st.selectbox(
                "また買いたい？",
                REPURCHASE_OPTIONS,
                index=1,
            )

        purchase_reason = st.text_area(
            "買った理由",
            placeholder=(
                "なぜこれを買おうと思った？"
            ),
            height=90,
        )

        good_points = st.text_area(
            "買ってよかった理由",
            placeholder=(
                "実際に使って良かったところ"
            ),
            height=110,
        )

        regret_points = st.text_area(
            "気になったところ・後悔ポイント",
            placeholder=(
                "少し惜しかった部分も残しておく"
            ),
            height=90,
        )

        memo = st.text_area(
            "メモ",
            placeholder=(
                "次に買うとき覚えておきたいこと"
            ),
            height=80,
        )

        submitted = (
            st.form_submit_button(
                "🛍️ 購入記録を保存",
                use_container_width=True,
            )
        )

        if submitted:
            if not item_name.strip():
                st.error(
                    "商品・サービス名を入力してください。"
                )

            else:
                add_item(
                    data,
                    {
                        "name": (
                            item_name.strip()
                        ),
                        "purchase_date": str(
                            purchase_date_input
                        ),
                        "price": price,
                        "category": category,
                        "shop": shop.strip(),
                        "purchase_reason": (
                            purchase_reason.strip()
                        ),
                        "satisfaction": (
                            satisfaction
                        ),
                        "cost_performance": (
                            cost_performance
                        ),
                        "usage_frequency": (
                            usage_frequency
                        ),
                        "usage_count": (
                            usage_count
                        ),
                        "repurchase": (
                            repurchase
                        ),
                        "good_points": (
                            good_points.strip()
                        ),
                        "regret_points": (
                            regret_points.strip()
                        ),
                        "memo": memo.strip(),
                    }
                )

                st.success(
                    "購入記録を保存しました！"
                )

                st.balloons()
                st.rerun()


# =========================================================
# 一覧
# =========================================================

with list_tab:
    st.header(
        "📚 買った物一覧"
    )

    if not items:
        st.info(
            "購入記録はまだありません。"
        )

    else:
        filter_columns = (
            st.columns(3)
        )

        with filter_columns[0]:
            keyword = st.text_input(
                "🔍 検索",
                placeholder=(
                    "商品名・購入理由・メモ"
                ),
            )

        with filter_columns[1]:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES,
                )
            )

        with filter_columns[2]:
            repurchase_filter = (
                st.selectbox(
                    "また買いたい？",
                    [
                        "すべて"
                    ]
                    + REPURCHASE_OPTIONS,
                )
            )

        min_satisfaction = st.slider(
            "最低満足度",
            min_value=1,
            max_value=5,
            value=1,
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "新しい順",
                "満足度が高い順",
                "コスパが高い順",
                "価格が高い順",
                "1回あたりコストが安い順",
            ],
        )

        filtered = list(
            items
        )

        if keyword.strip():
            word = (
                keyword.strip().lower()
            )

            filtered = [
                item
                for item in filtered
                if (
                    word
                    in item.get(
                        "name",
                        "",
                    ).lower()
                    or word
                    in item.get(
                        "purchase_reason",
                        "",
                    ).lower()
                    or word
                    in item.get(
                        "good_points",
                        "",
                    ).lower()
                    or word
                    in item.get(
                        "memo",
                        "",
                    ).lower()
                )
            ]

        if category_filter != "すべて":
            filtered = [
                item
                for item in filtered
                if item.get(
                    "category"
                )
                == category_filter
            ]

        if repurchase_filter != "すべて":
            filtered = [
                item
                for item in filtered
                if item.get(
                    "repurchase"
                )
                == repurchase_filter
            ]

        filtered = [
            item
            for item in filtered
            if int(
                item.get(
                    "satisfaction",
                    0,
                )
            )
            >= min_satisfaction
        ]

        if sort_option == "新しい順":
            filtered.sort(
                key=lambda item: (
                    item.get(
                        "purchase_date",
                        "",
                    ),
                    item.get(
                        "created_at",
                        "",
                    ),
                ),
                reverse=True,
            )

        elif sort_option == "満足度が高い順":
            filtered.sort(
                key=lambda item: (
                    int(
                        item.get(
                            "satisfaction",
                            0,
                        )
                    ),
                    int(
                        item.get(
                            "cost_performance",
                            0,
                        )
                    ),
                ),
                reverse=True,
            )

        elif sort_option == "コスパが高い順":
            filtered.sort(
                key=lambda item: int(
                    item.get(
                        "cost_performance",
                        0,
                    )
                ),
                reverse=True,
            )

        elif sort_option == "価格が高い順":
            filtered.sort(
                key=lambda item: int(
                    item.get(
                        "price",
                        0,
                    )
                ),
                reverse=True,
            )

        else:
            filtered.sort(
                key=lambda item: (
                    cost_per_use(
                        item
                    )
                    if cost_per_use(
                        item
                    )
                    is not None
                    else float("inf")
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered)}件**"
        )

        for item in filtered:
            item_id = item[
                "id"
            ]

            with st.container(
                border=True
            ):
                column1, column2 = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with column1:
                    favorite_icon = (
                        "⭐ "
                        if item.get(
                            "favorite",
                            False,
                        )
                        else ""
                    )

                    st.markdown(
                        f"### "
                        f"{favorite_icon}"
                        f"{item.get('name', '')}"
                    )

                    st.caption(
                        f"{item.get('category', '')} ／ "
                        f"{format_date(item.get('purchase_date', ''))}"
                    )

                    if item.get(
                        "shop",
                        "",
                    ):
                        st.write(
                            f"🏪 "
                            f"{item.get('shop', '')}"
                        )

                with column2:
                    st.metric(
                        "価格",
                        f"{item.get('price', 0):,}円"
                    )

                info_columns = (
                    st.columns(4)
                )

                info_columns[0].metric(
                    "満足度",
                    f"{item.get('satisfaction', 0)}/5"
                )

                info_columns[1].metric(
                    "コスパ",
                    f"{item.get('cost_performance', 0)}/5"
                )

                info_columns[2].metric(
                    "使用回数",
                    f"{item.get('usage_count', 0)}回"
                )

                cpu = cost_per_use(
                    item
                )

                info_columns[3].metric(
                    "1回あたり",
                    (
                        f"{cpu:,.0f}円"
                        if cpu is not None
                        else "未計算"
                    )
                )

                st.write(
                    f"使用頻度："
                    f"**{item.get('usage_frequency', '')}**"
                )

                st.write(
                    f"また買いたい？："
                    f"**{item.get('repurchase', '')}**"
                )

                if item.get(
                    "purchase_reason",
                    "",
                ):
                    st.info(
                        "買った理由\n\n"
                        + item.get(
                            "purchase_reason",
                            "",
                        )
                    )

                if item.get(
                    "good_points",
                    "",
                ):
                    st.success(
                        "👍 買ってよかった理由\n\n"
                        + item.get(
                            "good_points",
                            "",
                        )
                    )

                if item.get(
                    "regret_points",
                    "",
                ):
                    st.warning(
                        "🤔 惜しかったところ\n\n"
                        + item.get(
                            "regret_points",
                            "",
                        )
                    )

                if item.get(
                    "memo",
                    "",
                ):
                    st.write(
                        item.get(
                            "memo",
                            "",
                        )
                    )

                action_columns = (
                    st.columns(2)
                )

                with action_columns[0]:
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
                            f"favorite_"
                            f"{item_id}"
                        ),
                        use_container_width=True,
                    ):
                        toggle_favorite(
                            data,
                            item_id,
                        )

                        st.rerun()

                with action_columns[1]:
                    days = days_since_purchase(
                        item
                    )

                    if days is not None:
                        st.caption(
                            f"購入から {days}日"
                        )

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_name = st.text_input(
                        "商品名",
                        value=item.get(
                            "name",
                            "",
                        ),
                        key=(
                            f"edit_name_"
                            f"{item_id}"
                        ),
                    )

                    edit_price = st.number_input(
                        "購入価格",
                        min_value=0,
                        max_value=100000000,
                        value=int(
                            item.get(
                                "price",
                                0,
                            )
                        ),
                        key=(
                            f"edit_price_"
                            f"{item_id}"
                        ),
                    )

                    current_category = (
                        item.get(
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
                                else (
                                    len(CATEGORIES)
                                    - 1
                                )
                            ),
                            key=(
                                f"edit_category_"
                                f"{item_id}"
                            ),
                        )
                    )

                    edit_shop = st.text_input(
                        "購入場所",
                        value=item.get(
                            "shop",
                            "",
                        ),
                        key=(
                            f"edit_shop_"
                            f"{item_id}"
                        ),
                    )

                    edit_satisfaction = (
                        st.slider(
                            "満足度",
                            min_value=1,
                            max_value=5,
                            value=int(
                                item.get(
                                    "satisfaction",
                                    3,
                                )
                            ),
                            key=(
                                f"edit_satisfaction_"
                                f"{item_id}"
                            ),
                        )
                    )

                    edit_cost_performance = (
                        st.slider(
                            "コスパ",
                            min_value=1,
                            max_value=5,
                            value=int(
                                item.get(
                                    "cost_performance",
                                    3,
                                )
                            ),
                            key=(
                                f"edit_cost_performance_"
                                f"{item_id}"
                            ),
                        )
                    )

                    current_frequency = (
                        item.get(
                            "usage_frequency",
                            "まだ使っていない",
                        )
                    )

                    edit_frequency = (
                        st.selectbox(
                            "使用頻度",
                            USAGE_FREQUENCIES,
                            index=(
                                USAGE_FREQUENCIES.index(
                                    current_frequency
                                )
                                if current_frequency
                                in USAGE_FREQUENCIES
                                else 0
                            ),
                            key=(
                                f"edit_frequency_"
                                f"{item_id}"
                            ),
                        )
                    )

                    edit_usage_count = (
                        st.number_input(
                            "使用回数",
                            min_value=0,
                            max_value=1000000,
                            value=int(
                                item.get(
                                    "usage_count",
                                    0,
                                )
                            ),
                            key=(
                                f"edit_usage_count_"
                                f"{item_id}"
                            ),
                        )
                    )

                    current_repurchase = (
                        item.get(
                            "repurchase",
                            "どちらでもない",
                        )
                    )

                    edit_repurchase = (
                        st.selectbox(
                            "また買いたい？",
                            REPURCHASE_OPTIONS,
                            index=(
                                REPURCHASE_OPTIONS.index(
                                    current_repurchase
                                )
                                if current_repurchase
                                in REPURCHASE_OPTIONS
                                else 2
                            ),
                            key=(
                                f"edit_repurchase_"
                                f"{item_id}"
                            ),
                        )
                    )

                    edit_good_points = (
                        st.text_area(
                            "買ってよかった理由",
                            value=item.get(
                                "good_points",
                                "",
                            ),
                            key=(
                                f"edit_good_points_"
                                f"{item_id}"
                            ),
                        )
                    )

                    edit_regret_points = (
                        st.text_area(
                            "後悔ポイント",
                            value=item.get(
                                "regret_points",
                                "",
                            ),
                            key=(
                                f"edit_regret_points_"
                                f"{item_id}"
                            ),
                        )
                    )

                    edit_memo = st.text_area(
                        "メモ",
                        value=item.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_memo_"
                            f"{item_id}"
                        ),
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_item_"
                            f"{item_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_name.strip():
                            st.error(
                                "商品名を入力してください。"
                            )

                        else:
                            update_item(
                                data,
                                item_id,
                                {
                                    "name": (
                                        edit_name.strip()
                                    ),
                                    "price": (
                                        edit_price
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "shop": (
                                        edit_shop.strip()
                                    ),
                                    "satisfaction": (
                                        edit_satisfaction
                                    ),
                                    "cost_performance": (
                                        edit_cost_performance
                                    ),
                                    "usage_frequency": (
                                        edit_frequency
                                    ),
                                    "usage_count": (
                                        edit_usage_count
                                    ),
                                    "repurchase": (
                                        edit_repurchase
                                    ),
                                    "good_points": (
                                        edit_good_points.strip()
                                    ),
                                    "regret_points": (
                                        edit_regret_points.strip()
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                }
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 削除"
                ):
                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_delete_"
                                f"{item_id}"
                            ),
                        )
                    )

                    if st.button(
                        "この記録を削除",
                        key=(
                            f"delete_item_"
                            f"{item_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_item(
                            data,
                            item_id,
                        )

                        st.rerun()


# =========================================================
# 再評価
# =========================================================

with review_tab:
    st.header(
        "🔄 しばらく使った後に再評価"
    )

    if not items:
        st.info(
            "購入記録がありません。"
        )

    else:
        review_options = {
            (
                f"{item.get('name', '')}"
                f"｜購入から"
                f"{days_since_purchase(item) or 0}日"
            ): item["id"]
            for item in items
        }

        selected_label = st.selectbox(
            "再評価する商品",
            list(
                review_options.keys()
            ),
        )

        selected_item = (
            get_item_by_id(
                data,
                review_options[
                    selected_label
                ],
            )
        )

        selected_item_id = (
            selected_item["id"]
        )

        with st.container(
            border=True
        ):
            st.subheader(
                selected_item.get(
                    "name",
                    "",
                )
            )

            st.write(
                f"購入時価格："
                f"**{selected_item.get('price', 0):,}円**"
            )

            st.write(
                f"現在の満足度："
                f"**{selected_item.get('satisfaction', 0)}/5**"
            )

            st.write(
                f"現在の使用回数："
                f"**{selected_item.get('usage_count', 0)}回**"
            )

        with st.form(
            f"review_form_{selected_item_id}"
        ):
            review_date_input = (
                st.date_input(
                    "再評価日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

            review_columns = (
                st.columns(2)
            )

            with review_columns[0]:
                new_satisfaction = (
                    st.slider(
                        "今の満足度",
                        min_value=1,
                        max_value=5,
                        value=int(
                            selected_item.get(
                                "satisfaction",
                                3,
                            )
                        ),
                    )
                )

                new_cost_performance = (
                    st.slider(
                        "今のコスパ評価",
                        min_value=1,
                        max_value=5,
                        value=int(
                            selected_item.get(
                                "cost_performance",
                                3,
                            )
                        ),
                    )
                )

            with review_columns[1]:
                current_frequency = (
                    selected_item.get(
                        "usage_frequency",
                        "まだ使っていない",
                    )
                )

                new_frequency = (
                    st.selectbox(
                        "現在の使用頻度",
                        USAGE_FREQUENCIES,
                        index=(
                            USAGE_FREQUENCIES.index(
                                current_frequency
                            )
                            if current_frequency
                            in USAGE_FREQUENCIES
                            else 0
                        ),
                    )
                )

                new_usage_count = (
                    st.number_input(
                        "現在までの使用回数",
                        min_value=0,
                        max_value=1000000,
                        value=int(
                            selected_item.get(
                                "usage_count",
                                0,
                            )
                        ),
                    )
                )

            current_repurchase = (
                selected_item.get(
                    "repurchase",
                    "どちらでもない",
                )
            )

            new_repurchase = (
                st.selectbox(
                    "今でもまた買いたい？",
                    REPURCHASE_OPTIONS,
                    index=(
                        REPURCHASE_OPTIONS.index(
                            current_repurchase
                        )
                        if current_repurchase
                        in REPURCHASE_OPTIONS
                        else 2
                    ),
                )
            )

            review_comment = (
                st.text_area(
                    "再評価コメント",
                    placeholder=(
                        "しばらく使って分かったこと"
                    ),
                    height=120,
                )
            )

            submitted = (
                st.form_submit_button(
                    "🔄 再評価を保存",
                    use_container_width=True,
                )
            )

            if submitted:
                add_review(
                    data,
                    selected_item_id,
                    {
                        "review_date": str(
                            review_date_input
                        ),
                        "satisfaction": (
                            new_satisfaction
                        ),
                        "cost_performance": (
                            new_cost_performance
                        ),
                        "usage_frequency": (
                            new_frequency
                        ),
                        "usage_count": (
                            new_usage_count
                        ),
                        "repurchase": (
                            new_repurchase
                        ),
                        "comment": (
                            review_comment.strip()
                        ),
                    }
                )

                st.success(
                    "再評価を保存しました！"
                )

                st.rerun()

        review_history = (
            selected_item.get(
                "review_history",
                [],
            )
        )

        if review_history:
            st.divider()

            st.subheader(
                "📜 評価の変化"
            )

            review_rows = []

            for review in review_history:
                review_rows.append(
                    {
                        "再評価日": (
                            review.get(
                                "review_date",
                                "",
                            )
                        ),
                        "満足度": (
                            review.get(
                                "satisfaction",
                                0,
                            )
                        ),
                        "コスパ": (
                            review.get(
                                "cost_performance",
                                0,
                            )
                        ),
                        "使用回数": (
                            review.get(
                                "usage_count",
                                0,
                            )
                        ),
                        "また買う？": (
                            review.get(
                                "repurchase",
                                "",
                            )
                        ),
                        "コメント": (
                            review.get(
                                "comment",
                                "",
                            )
                        ),
                    }
                )

            review_df = pd.DataFrame(
                review_rows
            )

            st.line_chart(
                review_df.set_index(
                    "再評価日"
                )[
                    [
                        "満足度",
                        "コスパ",
                    ]
                ]
            )

            st.dataframe(
                review_df,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# お気に入り
# =========================================================

with favorite_tab:
    st.header(
        "⭐ 本当に買ってよかった物"
    )

    favorites = [
        item
        for item in items
        if item.get(
            "favorite",
            False,
        )
    ]

    if not favorites:
        st.info(
            "お気に入りはまだありません。"
        )

    else:
        favorites.sort(
            key=lambda item: (
                int(
                    item.get(
                        "satisfaction",
                        0,
                    )
                ),
                int(
                    item.get(
                        "cost_performance",
                        0,
                    )
                ),
            ),
            reverse=True,
        )

        for item in favorites:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### ⭐ "
                    f"{item.get('name', '')}"
                )

                st.caption(
                    f"{item.get('category', '')} ／ "
                    f"{item.get('price', 0):,}円"
                )

                st.write(
                    f"満足度："
                    f"**{item.get('satisfaction', 0)}/5**"
                )

                if item.get(
                    "good_points",
                    "",
                ):
                    st.success(
                        item.get(
                            "good_points",
                            "",
                        )
                    )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 買い物分析"
    )

    if not items:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for item in items:
            analysis_rows.append(
                {
                    "商品": (
                        item.get(
                            "name",
                            "",
                        )
                    ),
                    "月": (
                        item.get(
                            "purchase_date",
                            "",
                        )[:7]
                    ),
                    "カテゴリー": (
                        item.get(
                            "category",
                            "",
                        )
                    ),
                    "価格": int(
                        item.get(
                            "price",
                            0,
                        )
                    ),
                    "満足度": int(
                        item.get(
                            "satisfaction",
                            0,
                        )
                    ),
                    "コスパ": int(
                        item.get(
                            "cost_performance",
                            0,
                        )
                    ),
                    "使用回数": int(
                        item.get(
                            "usage_count",
                            0,
                        )
                    ),
                    "1回あたりコスト": (
                        cost_per_use(
                            item
                        )
                    ),
                    "また買う度": (
                        REPURCHASE_SCORES.get(
                            item.get(
                                "repurchase",
                                "",
                            ),
                            0,
                        )
                    ),
                    "また買う？": (
                        item.get(
                            "repurchase",
                            "",
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "月別購入額"
        )

        monthly_summary = (
            analysis_df.groupby(
                "月",
                as_index=False,
            )
            .agg(
                購入額=(
                    "価格",
                    "sum",
                ),
                購入数=(
                    "商品",
                    "count",
                ),
            )
            .sort_values(
                "月"
            )
        )

        st.bar_chart(
            monthly_summary.set_index(
                "月"
            )[["購入額"]]
        )

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "カテゴリー別購入金額"
        )

        category_amount = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False,
            )
            .agg(
                購入金額=(
                    "価格",
                    "sum",
                ),
                購入数=(
                    "商品",
                    "count",
                ),
            )
            .sort_values(
                "購入金額",
                ascending=False,
            )
        )

        st.bar_chart(
            category_amount.set_index(
                "カテゴリー"
            )[["購入金額"]]
        )

        st.dataframe(
            category_amount,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "カテゴリー別平均満足度"
        )

        category_satisfaction = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False,
            )
            .agg(
                平均満足度=(
                    "満足度",
                    "mean",
                ),
                平均コスパ=(
                    "コスパ",
                    "mean",
                ),
            )
            .sort_values(
                "平均満足度",
                ascending=False,
            )
        )

        category_satisfaction[
            "平均満足度"
        ] = category_satisfaction[
            "平均満足度"
        ].round(2)

        category_satisfaction[
            "平均コスパ"
        ] = category_satisfaction[
            "平均コスパ"
        ].round(2)

        st.bar_chart(
            category_satisfaction.set_index(
                "カテゴリー"
            )[
                [
                    "平均満足度",
                    "平均コスパ",
                ]
            ]
        )

        st.dataframe(
            category_satisfaction,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "1回あたりコスト"
        )

        cost_use_df = analysis_df.dropna(
            subset=[
                "1回あたりコスト"
            ]
        ).copy()

        if cost_use_df.empty:
            st.info(
                "使用回数を登録すると1回あたりコストを比較できます。"
            )

        else:
            cost_use_df = (
                cost_use_df.sort_values(
                    "1回あたりコスト"
                )
            )

            cost_use_df[
                "1回あたりコスト"
            ] = cost_use_df[
                "1回あたりコスト"
            ].round(0)

            st.dataframe(
                cost_use_df[
                    [
                        "商品",
                        "価格",
                        "使用回数",
                        "1回あたりコスト",
                        "満足度",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "価格帯別の満足度"
        )

        price_df = analysis_df.copy()

        price_df[
            "価格帯"
        ] = pd.cut(
            price_df["価格"],
            bins=[
                -1,
                1000,
                5000,
                10000,
                30000,
                100000,
                float("inf"),
            ],
            labels=[
                "〜1,000円",
                "1,001〜5,000円",
                "5,001〜10,000円",
                "10,001〜30,000円",
                "30,001〜100,000円",
                "100,001円〜",
            ],
        )

        price_summary = (
            price_df.groupby(
                "価格帯",
                observed=True,
                as_index=False,
            )
            .agg(
                平均満足度=(
                    "満足度",
                    "mean",
                ),
                購入数=(
                    "商品",
                    "count",
                ),
            )
        )

        price_summary[
            "平均満足度"
        ] = price_summary[
            "平均満足度"
        ].round(2)

        st.bar_chart(
            price_summary.set_index(
                "価格帯"
            )[["平均満足度"]]
        )

        st.dataframe(
            price_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "また買いたい商品"
        )

        repurchase_df = (
            analysis_df[
                analysis_df[
                    "また買う度"
                ]
                >= 4
            ]
            .sort_values(
                [
                    "また買う度",
                    "満足度",
                ],
                ascending=False,
            )
        )

        if repurchase_df.empty:
            st.info(
                "また買いたい商品はまだありません。"
            )

        else:
            st.dataframe(
                repurchase_df[
                    [
                        "商品",
                        "カテゴリー",
                        "価格",
                        "満足度",
                        "コスパ",
                        "また買う？",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "後悔しやすい買い物候補"
        )

        regret_df = (
            analysis_df[
                (
                    analysis_df[
                        "満足度"
                    ]
                    <= 2
                )
                | (
                    analysis_df[
                        "また買う度"
                    ]
                    <= 2
                )
            ]
            .sort_values(
                "満足度"
            )
        )

        if regret_df.empty:
            st.success(
                "現在、満足度の低い買い物はありません！"
            )

        else:
            st.dataframe(
                regret_df[
                    [
                        "商品",
                        "カテゴリー",
                        "価格",
                        "満足度",
                        "コスパ",
                        "また買う？",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# データ管理
# =========================================================

with data_tab:
    st.header(
        "💾 データ管理"
    )

    st.subheader(
        "JSONバックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"good_buy_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = st.file_uploader(
        "バックアップJSONを選択",
        type=[
            "json"
        ],
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict
                )
                or "items"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "items"
                    ],
                    list
                )
            ):
                st.error(
                    "対応していないJSON形式です。"
                )

            else:
                imported_data = (
                    normalize_data(
                        imported_data
                    )
                )

                st.warning(
                    "復元すると現在のデータが上書きされます。"
                )

                confirm_restore = (
                    st.checkbox(
                        "上書き復元を確認しました"
                    )
                )

                if st.button(
                    "JSONから復元",
                    disabled=(
                        not confirm_restore
                    ),
                    use_container_width=True,
                ):
                    save_data(
                        imported_data
                    )

                    st.success(
                        "データを復元しました！"
                    )

                    st.rerun()

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "購入記録・再評価履歴がすべて削除されます。"
    )

    confirm_delete_all = (
        st.checkbox(
            "全データ削除を確認しました"
        )
    )

    if st.button(
        "すべて削除",
        disabled=(
            not confirm_delete_all
        ),
        use_container_width=True,
    ):
        save_data(
            create_empty_data()
        )

        st.success(
            "すべてのデータを削除しました。"
        )

        st.rerun()


# =========================================================
# フッター
# =========================================================

st.divider()

st.success(
    "節約だけじゃなく、使ってよかったお金も知っておこう。🛍️"
)
