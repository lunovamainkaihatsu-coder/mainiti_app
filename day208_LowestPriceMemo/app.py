import json
import os
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =====================================
# ページ設定
# =====================================

st.set_page_config(
    page_title="最安値メモ",
    page_icon="🛒",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "price_data.json"
)

CATEGORIES = [
    "食品",
    "飲料",
    "日用品",
    "洗剤",
    "ベビー用品",
    "ペット用品",
    "衣類",
    "家電",
    "その他"
]

UNIT_TYPES = [
    "個",
    "g",
    "kg",
    "ml",
    "L",
    "枚",
    "本",
    "袋",
    "箱",
    "パック"
]


# =====================================
# データの保存・読み込み
# =====================================

def create_empty_data():
    """初期データを作成する。"""

    return {
        "products": [],
        "stores": [],
        "price_records": []
    }


def save_data(data):
    """データをJSONファイルに保存する。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "データ形式が正しくありません。"
            )

        data.setdefault(
            "products",
            []
        )

        data.setdefault(
            "stores",
            []
        )

        data.setdefault(
            "price_records",
            []
        )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data


# =====================================
# 商品管理
# =====================================

def add_product(
    data,
    product_name,
    category,
    standard_amount,
    unit_type,
    target_price,
    memo
):
    """商品を登録する。"""

    product = {
        "id": str(uuid.uuid4()),
        "name": product_name,
        "category": category,
        "standard_amount": float(
            standard_amount
        ),
        "unit_type": unit_type,
        "target_price": int(
            target_price
        ),
        "memo": memo,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["products"].append(
        product
    )

    save_data(data)


def update_product(
    data,
    product_id,
    product_name,
    category,
    standard_amount,
    unit_type,
    target_price,
    memo
):
    """商品情報を更新する。"""

    for product in data["products"]:
        if product.get("id") == product_id:
            product["name"] = product_name
            product["category"] = category
            product["standard_amount"] = float(
                standard_amount
            )
            product["unit_type"] = unit_type
            product["target_price"] = int(
                target_price
            )
            product["memo"] = memo
            product["updated_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )
            break

    save_data(data)


def delete_product(
    data,
    product_id
):
    """商品と関連する価格記録を削除する。"""

    data["products"] = [
        product
        for product in data["products"]
        if product.get("id") != product_id
    ]

    data["price_records"] = [
        record
        for record in data["price_records"]
        if record.get("product_id")
        != product_id
    ]

    save_data(data)


# =====================================
# 店舗管理
# =====================================

def add_store(
    data,
    store_name,
    store_type,
    location,
    memo
):
    """店舗を登録する。"""

    store = {
        "id": str(uuid.uuid4()),
        "name": store_name,
        "store_type": store_type,
        "location": location,
        "memo": memo,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["stores"].append(
        store
    )

    save_data(data)


def update_store(
    data,
    store_id,
    store_name,
    store_type,
    location,
    memo
):
    """店舗情報を更新する。"""

    for store in data["stores"]:
        if store.get("id") == store_id:
            store["name"] = store_name
            store["store_type"] = store_type
            store["location"] = location
            store["memo"] = memo
            store["updated_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )
            break

    save_data(data)


def delete_store(
    data,
    store_id
):
    """店舗と関連する価格記録を削除する。"""

    data["stores"] = [
        store
        for store in data["stores"]
        if store.get("id") != store_id
    ]

    data["price_records"] = [
        record
        for record in data["price_records"]
        if record.get("store_id")
        != store_id
    ]

    save_data(data)


# =====================================
# 価格記録管理
# =====================================

def calculate_unit_price(
    price,
    amount
):
    """1単位あたりの価格を計算する。"""

    if amount <= 0:
        return 0.0

    return round(
        price / amount,
        3
    )


def calculate_comparison_price(
    price,
    amount,
    unit_type
):
    """
    比較しやすい単価を計算する。

    g・mlは100単位あたり、
    kg・Lは1単位あたり、
    それ以外は1個・1枚などの単価。
    """

    if amount <= 0:
        return 0.0, ""

    if unit_type == "g":
        comparison_price = (
            price / amount
        ) * 100

        return round(
            comparison_price,
            2
        ), "100g"

    if unit_type == "ml":
        comparison_price = (
            price / amount
        ) * 100

        return round(
            comparison_price,
            2
        ), "100ml"

    if unit_type == "kg":
        comparison_price = (
            price / amount
        )

        return round(
            comparison_price,
            2
        ), "1kg"

    if unit_type == "L":
        comparison_price = (
            price / amount
        )

        return round(
            comparison_price,
            2
        ), "1L"

    comparison_price = (
        price / amount
    )

    return round(
        comparison_price,
        2
    ), f"1{unit_type}"


def add_price_record(
    data,
    product_id,
    store_id,
    record_date,
    price,
    amount,
    unit_type,
    sale_name,
    sale_end_date,
    memo
):
    """価格記録を追加する。"""

    unit_price = calculate_unit_price(
        price,
        amount
    )

    comparison_price, comparison_unit = (
        calculate_comparison_price(
            price,
            amount,
            unit_type
        )
    )

    record = {
        "id": str(uuid.uuid4()),
        "product_id": product_id,
        "store_id": store_id,
        "record_date": str(record_date),
        "price": int(price),
        "amount": float(amount),
        "unit_type": unit_type,
        "unit_price": unit_price,
        "comparison_price": comparison_price,
        "comparison_unit": comparison_unit,
        "sale_name": sale_name,
        "sale_end_date": (
            str(sale_end_date)
            if sale_end_date
            else ""
        ),
        "memo": memo,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["price_records"].append(
        record
    )

    save_data(data)


def update_price_record(
    data,
    record_id,
    record_date,
    price,
    amount,
    unit_type,
    sale_name,
    sale_end_date,
    memo
):
    """価格記録を更新する。"""

    unit_price = calculate_unit_price(
        price,
        amount
    )

    comparison_price, comparison_unit = (
        calculate_comparison_price(
            price,
            amount,
            unit_type
        )
    )

    for record in data["price_records"]:
        if record.get("id") == record_id:
            record["record_date"] = str(
                record_date
            )
            record["price"] = int(
                price
            )
            record["amount"] = float(
                amount
            )
            record["unit_type"] = unit_type
            record["unit_price"] = (
                unit_price
            )
            record["comparison_price"] = (
                comparison_price
            )
            record["comparison_unit"] = (
                comparison_unit
            )
            record["sale_name"] = sale_name
            record["sale_end_date"] = (
                str(sale_end_date)
                if sale_end_date
                else ""
            )
            record["memo"] = memo
            record["updated_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )
            break

    save_data(data)


def delete_price_record(
    data,
    record_id
):
    """価格記録を削除する。"""

    data["price_records"] = [
        record
        for record in data["price_records"]
        if record.get("id") != record_id
    ]

    save_data(data)


# =====================================
# 補助関数
# =====================================

def get_product_by_id(
    data,
    product_id
):
    """商品IDから商品情報を取得する。"""

    for product in data["products"]:
        if product.get("id") == product_id:
            return product

    return None


def get_store_by_id(
    data,
    store_id
):
    """店舗IDから店舗情報を取得する。"""

    for store in data["stores"]:
        if store.get("id") == store_id:
            return store

    return None


def get_product_name(
    data,
    product_id
):
    """商品IDから商品名を取得する。"""

    product = get_product_by_id(
        data,
        product_id
    )

    if product:
        return product.get(
            "name",
            "名称未設定"
        )

    return "不明な商品"


def get_store_name(
    data,
    store_id
):
    """店舗IDから店舗名を取得する。"""

    store = get_store_by_id(
        data,
        store_id
    )

    if store:
        return store.get(
            "name",
            "名称未設定"
        )

    return "不明な店舗"


def parse_date(
    date_text
):
    """文字列の日付をdate型に変換する。"""

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d"
        ).date()

    except (
        ValueError,
        TypeError
    ):
        return date.today()


def format_price(
    value
):
    """金額を日本円形式で表示する。"""

    return f"¥{int(value):,}"


def calculate_average(
    values
):
    """平均値を計算する。"""

    valid_values = [
        float(value)
        for value in values
        if value is not None
    ]

    if not valid_values:
        return 0.0

    return sum(valid_values) / len(
        valid_values
    )


def get_buying_judgement(
    current_price,
    average_price,
    target_price=0
):
    """現在価格から買い時を判定する。"""

    if current_price <= 0:
        return (
            "価格情報なし",
            "価格を記録すると判定できます。"
        )

    if target_price > 0:
        if current_price <= target_price:
            return (
                "🎉 目標価格以下！",
                "登録した目標価格を下回っています。"
            )

    if average_price <= 0:
        return (
            "📊 記録を増やそう",
            "比較できる過去データがまだありません。"
        )

    difference_rate = (
        (
            current_price
            - average_price
        )
        / average_price
    ) * 100

    if difference_rate <= -15:
        return (
            "🔥 かなり安い！",
            (
                f"過去平均より"
                f"{abs(difference_rate):.1f}%安い価格です。"
            )
        )

    if difference_rate <= -5:
        return (
            "👍 買い時",
            (
                f"過去平均より"
                f"{abs(difference_rate):.1f}%安い価格です。"
            )
        )

    if difference_rate < 5:
        return (
            "🙂 平均的",
            "過去平均に近い価格です。"
        )

    if difference_rate < 15:
        return (
            "🤔 少し高め",
            (
                f"過去平均より"
                f"{difference_rate:.1f}%高い価格です。"
            )
        )

    return (
        "⚠️ かなり高め",
        (
            f"過去平均より"
            f"{difference_rate:.1f}%高い価格です。"
        )
    )


def get_product_records(
    data,
    product_id
):
    """指定商品の価格記録を取得する。"""

    return [
        record
        for record in data["price_records"]
        if record.get(
            "product_id"
        ) == product_id
    ]


def get_latest_record(
    records
):
    """最新の価格記録を取得する。"""

    if not records:
        return None

    return sorted(
        records,
        key=lambda record: (
            record.get(
                "record_date",
                ""
            ),
            record.get(
                "created_at",
                ""
            )
        ),
        reverse=True
    )[0]


# =====================================
# データ読み込み
# =====================================

data = load_data()

products = data["products"]
stores = data["stores"]
price_records = data["price_records"]


# =====================================
# タイトル
# =====================================

st.title("🛒 最安値メモ")

st.caption(
    "商品の価格を店舗ごとに記録して、"
    "一番安い店や買い時を見つけます。"
)


# =====================================
# 商品選択
# =====================================

if products:
    product_options = {
        product.get(
            "name",
            "名称未設定"
        ): product.get(
            "id",
            ""
        )
        for product in products
    }

    selected_product_name = st.selectbox(
        "📦 表示する商品",
        list(
            product_options.keys()
        )
    )

    selected_product_id = (
        product_options[
            selected_product_name
        ]
    )

    selected_product = get_product_by_id(
        data,
        selected_product_id
    )

else:
    selected_product_name = ""
    selected_product_id = ""
    selected_product = None


selected_records = get_product_records(
    data,
    selected_product_id
)


# =====================================
# ダッシュボード集計
# =====================================

all_prices = [
    int(
        record.get(
            "price",
            0
        )
    )
    for record in selected_records
    if int(
        record.get(
            "price",
            0
        )
    ) > 0
]

all_comparison_prices = [
    float(
        record.get(
            "comparison_price",
            0
        )
    )
    for record in selected_records
    if float(
        record.get(
            "comparison_price",
            0
        )
    ) > 0
]

lowest_price = (
    min(all_prices)
    if all_prices
    else 0
)

highest_price = (
    max(all_prices)
    if all_prices
    else 0
)

average_price = calculate_average(
    all_prices
)

lowest_comparison_price = (
    min(all_comparison_prices)
    if all_comparison_prices
    else 0
)

latest_record = get_latest_record(
    selected_records
)

latest_price = (
    int(
        latest_record.get(
            "price",
            0
        )
    )
    if latest_record
    else 0
)

target_price = (
    int(
        selected_product.get(
            "target_price",
            0
        )
    )
    if selected_product
    else 0
)


# =====================================
# ダッシュボード
# =====================================

st.divider()

st.header("📊 ダッシュボード")

if not products:
    st.info(
        "最初に「商品管理」タブから"
        "商品を登録してください。"
    )

else:
    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    with metric_col1:
        st.metric(
            "最安値",
            format_price(
                lowest_price
            )
            if lowest_price
            else "未記録"
        )

    with metric_col2:
        st.metric(
            "平均価格",
            format_price(
                round(
                    average_price
                )
            )
            if average_price
            else "未記録"
        )

    with metric_col3:
        st.metric(
            "最高価格",
            format_price(
                highest_price
            )
            if highest_price
            else "未記録"
        )

    with metric_col4:
        st.metric(
            "価格記録数",
            f"{len(selected_records)}件"
        )

    if latest_record:
        latest_store_name = get_store_name(
            data,
            latest_record.get(
                "store_id",
                ""
            )
        )

        judgement_title, judgement_text = (
            get_buying_judgement(
                current_price=latest_price,
                average_price=average_price,
                target_price=target_price
            )
        )

        with st.container(border=True):
            latest_col1, latest_col2 = (
                st.columns([3, 1])
            )

            with latest_col1:
                st.subheader(
                    f"🛍️ 最新価格："
                    f"{format_price(latest_price)}"
                )

                st.write(
                    f"店舗：**{latest_store_name}**"
                )

                st.caption(
                    f"記録日："
                    f"{latest_record.get('record_date', '')}"
                )

                st.write(
                    f"内容量："
                    f"{latest_record.get('amount', 0):g}"
                    f"{latest_record.get('unit_type', '')}"
                )

                st.write(
                    f"{latest_record.get('comparison_unit', '')}"
                    f"あたり："
                    f"**{latest_record.get('comparison_price', 0):.2f}円**"
                )

            with latest_col2:
                st.metric(
                    "買い時判定",
                    judgement_title
                )

            st.info(
                judgement_text
            )

            sale_name = latest_record.get(
                "sale_name",
                ""
            )

            if sale_name:
                st.write(
                    f"🏷️ {sale_name}"
                )

            sale_end_date = latest_record.get(
                "sale_end_date",
                ""
            )

            if sale_end_date:
                end_date = parse_date(
                    sale_end_date
                )

                remaining_days = (
                    end_date - date.today()
                ).days

                if remaining_days > 0:
                    st.warning(
                        f"セール終了まで"
                        f"あと{remaining_days}日です。"
                    )

                elif remaining_days == 0:
                    st.error(
                        "セールは今日までです！"
                    )

                else:
                    st.caption(
                        "このセールは終了しています。"
                    )

    else:
        st.info(
            "価格を記録すると、"
            "最安値や買い時を判定できます。"
        )


# =====================================
# 最安店舗
# =====================================

st.divider()

st.header("🏆 最安店舗")

if not selected_records:
    st.info(
        "価格記録がまだありません。"
    )

else:
    lowest_record = min(
        selected_records,
        key=lambda record: float(
            record.get(
                "comparison_price",
                999999999
            )
        )
    )

    lowest_store_name = get_store_name(
        data,
        lowest_record.get(
            "store_id",
            ""
        )
    )

    with st.container(border=True):
        store_col1, store_col2 = (
            st.columns([3, 1])
        )

        with store_col1:
            st.subheader(
                f"🏪 {lowest_store_name}"
            )

            st.write(
                f"販売価格："
                f"**{format_price(lowest_record.get('price', 0))}**"
            )

            st.write(
                f"内容量："
                f"{lowest_record.get('amount', 0):g}"
                f"{lowest_record.get('unit_type', '')}"
            )

            st.caption(
                f"記録日："
                f"{lowest_record.get('record_date', '')}"
            )

        with store_col2:
            st.metric(
                f"{lowest_record.get('comparison_unit', '')}あたり",
                (
                    f"{lowest_record.get('comparison_price', 0):.2f}"
                    "円"
                )
            )


# =====================================
# タブ
# =====================================

st.divider()

product_tab, store_tab, record_tab, graph_tab, history_tab = (
    st.tabs(
        [
            "📦 商品管理",
            "🏪 店舗管理",
            "➕ 価格を記録",
            "📈 価格分析",
            "📋 価格履歴"
        ]
    )
)


# =====================================
# 商品管理タブ
# =====================================

with product_tab:
    st.header("📦 商品を登録")

    with st.form(
        "product_form",
        clear_on_submit=True
    ):
        product_col1, product_col2 = (
            st.columns(2)
        )

        with product_col1:
            product_name = st.text_input(
                "商品名",
                placeholder=(
                    "例：卵 10個入り"
                )
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES
            )

            standard_amount = st.number_input(
                "基準内容量",
                min_value=0.01,
                value=1.0,
                step=1.0
            )

        with product_col2:
            unit_type = st.selectbox(
                "内容量の単位",
                UNIT_TYPES
            )

            target_price_input = (
                st.number_input(
                    "目標価格（円）",
                    min_value=0,
                    value=0,
                    step=10,
                    help=(
                        "この価格以下なら買いたい、"
                        "という金額を登録します。"
                    )
                )
            )

            product_memo = st.text_area(
                "メモ",
                placeholder=(
                    "例：Mサイズ、10個入り"
                )
            )

        product_submit = (
            st.form_submit_button(
                "📦 商品を登録",
                use_container_width=True
            )
        )

        if product_submit:
            cleaned_product_name = (
                product_name.strip()
            )

            duplicate_exists = any(
                product.get(
                    "name",
                    ""
                ).lower()
                == cleaned_product_name.lower()
                for product in products
            )

            if not cleaned_product_name:
                st.error(
                    "商品名を入力してください。"
                )

            elif duplicate_exists:
                st.warning(
                    "同じ名前の商品が"
                    "すでに登録されています。"
                )

            else:
                add_product(
                    data=data,
                    product_name=(
                        cleaned_product_name
                    ),
                    category=category,
                    standard_amount=(
                        standard_amount
                    ),
                    unit_type=unit_type,
                    target_price=(
                        target_price_input
                    ),
                    memo=(
                        product_memo.strip()
                    )
                )

                st.success(
                    f"「{cleaned_product_name}」を"
                    "登録しました！"
                )

                st.rerun()

    st.divider()

    st.header("📋 登録済み商品")

    if not products:
        st.info(
            "登録済みの商品はありません。"
        )

    product_search = st.text_input(
        "🔍 商品を検索",
        placeholder="商品名やメモ",
        key="product_search"
    )

    filtered_products = list(
        products
    )

    if product_search:
        keyword = (
            product_search.strip().lower()
        )

        filtered_products = [
            product
            for product in filtered_products
            if keyword
            in product.get(
                "name",
                ""
            ).lower()
            or keyword
            in product.get(
                "memo",
                ""
            ).lower()
        ]

    for product in filtered_products:
        product_id = product.get(
            "id",
            ""
        )

        product_name_display = (
            product.get(
                "name",
                "名称未設定"
            )
        )

        product_records = (
            get_product_records(
                data,
                product_id
            )
        )

        product_prices = [
            record.get(
                "price",
                0
            )
            for record in product_records
        ]

        product_lowest = (
            min(product_prices)
            if product_prices
            else 0
        )

        with st.container(border=True):
            info_col, metric_col = (
                st.columns([3, 1])
            )

            with info_col:
                st.subheader(
                    f"📦 {product_name_display}"
                )

                st.caption(
                    f"{product.get('category', '')} "
                    f"／ "
                    f"{product.get('standard_amount', 0):g}"
                    f"{product.get('unit_type', '')}"
                )

            with metric_col:
                st.metric(
                    "最安値",
                    (
                        format_price(
                            product_lowest
                        )
                        if product_lowest
                        else "未記録"
                    )
                )

            target = product.get(
                "target_price",
                0
            )

            if target:
                st.write(
                    f"🎯 目標価格："
                    f"**{format_price(target)}**"
                )

            product_memo_display = (
                product.get(
                    "memo",
                    ""
                )
            )

            if product_memo_display:
                st.write(
                    f"📝 {product_memo_display}"
                )

            with st.expander(
                "✏️ 商品情報を編集"
            ):
                edit_product_name = (
                    st.text_input(
                        "商品名",
                        value=(
                            product_name_display
                        ),
                        key=(
                            f"edit_product_name_"
                            f"{product_id}"
                        )
                    )
                )

                category_index = (
                    CATEGORIES.index(
                        product.get(
                            "category",
                            "その他"
                        )
                    )
                    if product.get(
                        "category"
                    )
                    in CATEGORIES
                    else 0
                )

                edit_category = (
                    st.selectbox(
                        "カテゴリー",
                        CATEGORIES,
                        index=category_index,
                        key=(
                            f"edit_category_"
                            f"{product_id}"
                        )
                    )
                )

                edit_standard_amount = (
                    st.number_input(
                        "基準内容量",
                        min_value=0.01,
                        value=float(
                            product.get(
                                "standard_amount",
                                1
                            )
                        ),
                        step=1.0,
                        key=(
                            f"edit_amount_"
                            f"{product_id}"
                        )
                    )
                )

                current_unit = product.get(
                    "unit_type",
                    "個"
                )

                unit_index = (
                    UNIT_TYPES.index(
                        current_unit
                    )
                    if current_unit
                    in UNIT_TYPES
                    else 0
                )

                edit_unit_type = (
                    st.selectbox(
                        "単位",
                        UNIT_TYPES,
                        index=unit_index,
                        key=(
                            f"edit_unit_"
                            f"{product_id}"
                        )
                    )
                )

                edit_target_price = (
                    st.number_input(
                        "目標価格",
                        min_value=0,
                        value=int(
                            product.get(
                                "target_price",
                                0
                            )
                        ),
                        step=10,
                        key=(
                            f"edit_target_"
                            f"{product_id}"
                        )
                    )
                )

                edit_product_memo = (
                    st.text_area(
                        "メモ",
                        value=product.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_product_memo_"
                            f"{product_id}"
                        )
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_product_"
                        f"{product_id}"
                    ),
                    use_container_width=True
                ):
                    cleaned_edit_name = (
                        edit_product_name.strip()
                    )

                    if not cleaned_edit_name:
                        st.error(
                            "商品名を入力してください。"
                        )

                    else:
                        update_product(
                            data=data,
                            product_id=product_id,
                            product_name=(
                                cleaned_edit_name
                            ),
                            category=(
                                edit_category
                            ),
                            standard_amount=(
                                edit_standard_amount
                            ),
                            unit_type=(
                                edit_unit_type
                            ),
                            target_price=(
                                edit_target_price
                            ),
                            memo=(
                                edit_product_memo.strip()
                            )
                        )

                        st.success(
                            "商品情報を更新しました！"
                        )

                        st.rerun()

            with st.expander(
                "🗑️ この商品を削除"
            ):
                st.warning(
                    "この商品に登録された"
                    "すべての価格記録も削除されます。"
                )

                confirm_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_product_"
                            f"{product_id}"
                        )
                    )
                )

                if st.button(
                    "商品を削除",
                    key=(
                        f"delete_product_"
                        f"{product_id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True
                ):
                    delete_product(
                        data,
                        product_id
                    )

                    st.rerun()


# =====================================
# 店舗管理タブ
# =====================================

with store_tab:
    st.header("🏪 店舗を登録")

    with st.form(
        "store_form",
        clear_on_submit=True
    ):
        store_col1, store_col2 = (
            st.columns(2)
        )

        with store_col1:
            store_name = st.text_input(
                "店舗名",
                placeholder=(
                    "例：スーパーA"
                )
            )

            store_type = st.selectbox(
                "店舗タイプ",
                [
                    "スーパー",
                    "ドラッグストア",
                    "コンビニ",
                    "ホームセンター",
                    "家電量販店",
                    "ネット通販",
                    "その他"
                ]
            )

        with store_col2:
            location = st.text_input(
                "場所・支店名",
                placeholder=(
                    "例：静岡駅前店"
                )
            )

            store_memo = st.text_area(
                "メモ",
                placeholder=(
                    "ポイントデー、特売日など"
                )
            )

        store_submit = (
            st.form_submit_button(
                "🏪 店舗を登録",
                use_container_width=True
            )
        )

        if store_submit:
            cleaned_store_name = (
                store_name.strip()
            )

            duplicate_exists = any(
                store.get(
                    "name",
                    ""
                ).lower()
                == cleaned_store_name.lower()
                for store in stores
            )

            if not cleaned_store_name:
                st.error(
                    "店舗名を入力してください。"
                )

            elif duplicate_exists:
                st.warning(
                    "同じ名前の店舗が"
                    "すでに登録されています。"
                )

            else:
                add_store(
                    data=data,
                    store_name=(
                        cleaned_store_name
                    ),
                    store_type=store_type,
                    location=location.strip(),
                    memo=store_memo.strip()
                )

                st.success(
                    f"「{cleaned_store_name}」を"
                    "登録しました！"
                )

                st.rerun()

    st.divider()

    st.header("🏬 登録済み店舗")

    if not stores:
        st.info(
            "登録済みの店舗はありません。"
        )

    for store in stores:
        store_id = store.get(
            "id",
            ""
        )

        store_name_display = store.get(
            "name",
            "名称未設定"
        )

        store_record_count = len(
            [
                record
                for record in price_records
                if record.get(
                    "store_id"
                ) == store_id
            ]
        )

        with st.container(border=True):
            store_info_col, store_metric_col = (
                st.columns([3, 1])
            )

            with store_info_col:
                st.subheader(
                    f"🏪 {store_name_display}"
                )

                st.caption(
                    f"{store.get('store_type', '')} "
                    f"／ "
                    f"{store.get('location', '')}"
                )

            with store_metric_col:
                st.metric(
                    "価格記録",
                    f"{store_record_count}件"
                )

            if store.get(
                "memo",
                ""
            ):
                st.write(
                    f"📝 {store.get('memo', '')}"
                )

            with st.expander(
                "✏️ 店舗情報を編集"
            ):
                edit_store_name = (
                    st.text_input(
                        "店舗名",
                        value=store_name_display,
                        key=(
                            f"edit_store_name_"
                            f"{store_id}"
                        )
                    )
                )

                store_types = [
                    "スーパー",
                    "ドラッグストア",
                    "コンビニ",
                    "ホームセンター",
                    "家電量販店",
                    "ネット通販",
                    "その他"
                ]

                current_store_type = (
                    store.get(
                        "store_type",
                        "スーパー"
                    )
                )

                store_type_index = (
                    store_types.index(
                        current_store_type
                    )
                    if current_store_type
                    in store_types
                    else 0
                )

                edit_store_type = (
                    st.selectbox(
                        "店舗タイプ",
                        store_types,
                        index=(
                            store_type_index
                        ),
                        key=(
                            f"edit_store_type_"
                            f"{store_id}"
                        )
                    )
                )

                edit_location = (
                    st.text_input(
                        "場所・支店名",
                        value=store.get(
                            "location",
                            ""
                        ),
                        key=(
                            f"edit_location_"
                            f"{store_id}"
                        )
                    )
                )

                edit_store_memo = (
                    st.text_area(
                        "メモ",
                        value=store.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_store_memo_"
                            f"{store_id}"
                        )
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_store_"
                        f"{store_id}"
                    ),
                    use_container_width=True
                ):
                    cleaned_edit_store_name = (
                        edit_store_name.strip()
                    )

                    if not cleaned_edit_store_name:
                        st.error(
                            "店舗名を入力してください。"
                        )

                    else:
                        update_store(
                            data=data,
                            store_id=store_id,
                            store_name=(
                                cleaned_edit_store_name
                            ),
                            store_type=(
                                edit_store_type
                            ),
                            location=(
                                edit_location.strip()
                            ),
                            memo=(
                                edit_store_memo.strip()
                            )
                        )

                        st.success(
                            "店舗情報を更新しました！"
                        )

                        st.rerun()

            with st.expander(
                "🗑️ この店舗を削除"
            ):
                st.warning(
                    "この店舗に登録された"
                    "すべての価格記録も削除されます。"
                )

                confirm_store_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_store_"
                            f"{store_id}"
                        )
                    )
                )

                if st.button(
                    "店舗を削除",
                    key=(
                        f"delete_store_"
                        f"{store_id}"
                    ),
                    disabled=(
                        not confirm_store_delete
                    ),
                    use_container_width=True
                ):
                    delete_store(
                        data,
                        store_id
                    )

                    st.rerun()


# =====================================
# 価格登録タブ
# =====================================

with record_tab:
    st.header("➕ 商品価格を記録")

    if not products:
        st.info(
            "先に商品を登録してください。"
        )

    elif not stores:
        st.info(
            "先に店舗を登録してください。"
        )

    else:
        record_product_options = {
            product.get(
                "name",
                "名称未設定"
            ): product.get(
                "id",
                ""
            )
            for product in products
        }

        record_store_options = {
            store.get(
                "name",
                "名称未設定"
            ): store.get(
                "id",
                ""
            )
            for store in stores
        }

        with st.form(
            "price_record_form",
            clear_on_submit=True
        ):
            record_col1, record_col2 = (
                st.columns(2)
            )

            with record_col1:
                record_product_name = (
                    st.selectbox(
                        "商品",
                        list(
                            record_product_options.keys()
                        )
                    )
                )

                record_store_name = (
                    st.selectbox(
                        "店舗",
                        list(
                            record_store_options.keys()
                        )
                    )
                )

                record_date = st.date_input(
                    "記録日",
                    value=date.today()
                )

                price = st.number_input(
                    "販売価格（円）",
                    min_value=0,
                    value=0,
                    step=10
                )

            with record_col2:
                record_product = (
                    get_product_by_id(
                        data,
                        record_product_options[
                            record_product_name
                        ]
                    )
                )

                default_amount = (
                    float(
                        record_product.get(
                            "standard_amount",
                            1
                        )
                    )
                    if record_product
                    else 1.0
                )

                default_unit = (
                    record_product.get(
                        "unit_type",
                        "個"
                    )
                    if record_product
                    else "個"
                )

                amount = st.number_input(
                    "内容量",
                    min_value=0.01,
                    value=default_amount,
                    step=1.0
                )

                default_unit_index = (
                    UNIT_TYPES.index(
                        default_unit
                    )
                    if default_unit
                    in UNIT_TYPES
                    else 0
                )

                record_unit_type = (
                    st.selectbox(
                        "単位",
                        UNIT_TYPES,
                        index=(
                            default_unit_index
                        )
                    )
                )

                sale_name = st.text_input(
                    "セール名",
                    placeholder=(
                        "例：週末特売"
                    )
                )

                has_sale_end = st.checkbox(
                    "セール終了日を登録する"
                )

                sale_end_date = None

                if has_sale_end:
                    sale_end_date = (
                        st.date_input(
                            "セール終了日",
                            value=date.today()
                        )
                    )

                price_memo = st.text_area(
                    "メモ",
                    placeholder=(
                        "税込価格、会員価格など"
                    )
                )

            if price > 0 and amount > 0:
                preview_price, preview_unit = (
                    calculate_comparison_price(
                        price,
                        amount,
                        record_unit_type
                    )
                )

                st.info(
                    f"{preview_unit}あたり："
                    f"{preview_price:.2f}円"
                )

            price_submit = (
                st.form_submit_button(
                    "💰 価格を記録",
                    use_container_width=True
                )
            )

            if price_submit:
                if price <= 0:
                    st.error(
                        "販売価格を入力してください。"
                    )

                elif amount <= 0:
                    st.error(
                        "内容量を入力してください。"
                    )

                elif (
                    sale_end_date
                    and sale_end_date
                    < record_date
                ):
                    st.error(
                        "セール終了日は"
                        "記録日以降に設定してください。"
                    )

                else:
                    add_price_record(
                        data=data,
                        product_id=(
                            record_product_options[
                                record_product_name
                            ]
                        ),
                        store_id=(
                            record_store_options[
                                record_store_name
                            ]
                        ),
                        record_date=record_date,
                        price=price,
                        amount=amount,
                        unit_type=(
                            record_unit_type
                        ),
                        sale_name=(
                            sale_name.strip()
                        ),
                        sale_end_date=(
                            sale_end_date
                        ),
                        memo=(
                            price_memo.strip()
                        )
                    )

                    st.success(
                        "価格を記録しました！"
                    )

                    st.rerun()


# =====================================
# グラフタブ
# =====================================

with graph_tab:
    st.header("📈 価格分析")

    if not selected_records:
        st.info(
            "価格分析に必要な記録がありません。"
        )

    else:
        sorted_records = sorted(
            selected_records,
            key=lambda record: record.get(
                "record_date",
                ""
            )
        )

        graph_rows = []

        for record in sorted_records:
            graph_rows.append(
                {
                    "記録日": pd.to_datetime(
                        record.get(
                            "record_date",
                            ""
                        )
                    ),
                    "販売価格": int(
                        record.get(
                            "price",
                            0
                        )
                    ),
                    "比較単価": float(
                        record.get(
                            "comparison_price",
                            0
                        )
                    ),
                    "店舗": get_store_name(
                        data,
                        record.get(
                            "store_id",
                            ""
                        )
                    )
                }
            )

        graph_df = pd.DataFrame(
            graph_rows
        )

        st.subheader(
            "💰 販売価格の推移"
        )

        st.line_chart(
            graph_df.set_index(
                "記録日"
            )[["販売価格"]]
        )

        st.subheader(
            "📏 単価の推移"
        )

        st.line_chart(
            graph_df.set_index(
                "記録日"
            )[["比較単価"]]
        )

        st.subheader(
            "🏪 店舗別平均価格"
        )

        store_summary = (
            graph_df.groupby(
                "店舗",
                as_index=False
            )
            .agg(
                {
                    "販売価格": "mean",
                    "比較単価": "mean"
                }
            )
        )

        store_summary = (
            store_summary.sort_values(
                "比較単価"
            )
        )

        st.bar_chart(
            store_summary.set_index(
                "店舗"
            )[["比較単価"]]
        )

        display_store_summary = (
            store_summary.copy()
        )

        display_store_summary[
            "販売価格"
        ] = display_store_summary[
            "販売価格"
        ].map(
            lambda value: (
                f"{value:,.0f}円"
            )
        )

        display_store_summary[
            "比較単価"
        ] = display_store_summary[
            "比較単価"
        ].map(
            lambda value: (
                f"{value:.2f}円"
            )
        )

        st.dataframe(
            display_store_summary,
            use_container_width=True,
            hide_index=True
        )


# =====================================
# 価格履歴タブ
# =====================================

with history_tab:
    st.header("📋 価格履歴")

    if not selected_records:
        st.info(
            "価格履歴はまだありません。"
        )

    else:
        filter_col1, filter_col2 = (
            st.columns(2)
        )

        with filter_col1:
            history_search = (
                st.text_input(
                    "🔍 検索",
                    placeholder=(
                        "店舗、セール、メモ"
                    )
                )
            )

        with filter_col2:
            store_filter_options = (
                ["すべて"]
                + [
                    store.get(
                        "name",
                        "名称未設定"
                    )
                    for store in stores
                ]
            )

            history_store_filter = (
                st.selectbox(
                    "店舗で絞り込み",
                    store_filter_options
                )
            )

        history_sort = st.selectbox(
            "並び順",
            [
                "新しい順",
                "古い順",
                "価格が安い順",
                "価格が高い順",
                "単価が安い順"
            ]
        )

        filtered_records = list(
            selected_records
        )

        if history_search:
            keyword = (
                history_search.strip().lower()
            )

            filtered_records = [
                record
                for record in filtered_records
                if keyword
                in get_store_name(
                    data,
                    record.get(
                        "store_id",
                        ""
                    )
                ).lower()
                or keyword
                in record.get(
                    "sale_name",
                    ""
                ).lower()
                or keyword
                in record.get(
                    "memo",
                    ""
                ).lower()
            ]

        if history_store_filter != "すべて":
            filtered_records = [
                record
                for record in filtered_records
                if get_store_name(
                    data,
                    record.get(
                        "store_id",
                        ""
                    )
                ) == history_store_filter
            ]

        if history_sort == "新しい順":
            filtered_records = sorted(
                filtered_records,
                key=lambda record: (
                    record.get(
                        "record_date",
                        ""
                    ),
                    record.get(
                        "created_at",
                        ""
                    )
                ),
                reverse=True
            )

        elif history_sort == "古い順":
            filtered_records = sorted(
                filtered_records,
                key=lambda record: (
                    record.get(
                        "record_date",
                        ""
                    ),
                    record.get(
                        "created_at",
                        ""
                    )
                )
            )

        elif history_sort == "価格が安い順":
            filtered_records = sorted(
                filtered_records,
                key=lambda record: int(
                    record.get(
                        "price",
                        0
                    )
                )
            )

        elif history_sort == "価格が高い順":
            filtered_records = sorted(
                filtered_records,
                key=lambda record: int(
                    record.get(
                        "price",
                        0
                    )
                ),
                reverse=True
            )

        else:
            filtered_records = sorted(
                filtered_records,
                key=lambda record: float(
                    record.get(
                        "comparison_price",
                        0
                    )
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_records)}件**"
        )

        for record in filtered_records:
            record_id = record.get(
                "id",
                ""
            )

            store_name_display = (
                get_store_name(
                    data,
                    record.get(
                        "store_id",
                        ""
                    )
                )
            )

            with st.container(border=True):
                history_col1, history_col2 = (
                    st.columns([3, 1])
                )

                with history_col1:
                    st.subheader(
                        f"🏪 {store_name_display}"
                    )

                    st.caption(
                        f"記録日："
                        f"{record.get('record_date', '')}"
                    )

                with history_col2:
                    st.metric(
                        "販売価格",
                        format_price(
                            record.get(
                                "price",
                                0
                            )
                        )
                    )

                history_metric_col1, history_metric_col2 = (
                    st.columns(2)
                )

                with history_metric_col1:
                    st.metric(
                        "内容量",
                        (
                            f"{record.get('amount', 0):g}"
                            f"{record.get('unit_type', '')}"
                        )
                    )

                with history_metric_col2:
                    st.metric(
                        f"{record.get('comparison_unit', '')}あたり",
                        (
                            f"{record.get('comparison_price', 0):.2f}"
                            "円"
                        )
                    )

                if record.get(
                    "sale_name",
                    ""
                ):
                    st.write(
                        f"🏷️ "
                        f"{record.get('sale_name', '')}"
                    )

                if record.get(
                    "sale_end_date",
                    ""
                ):
                    st.write(
                        f"セール終了日："
                        f"{record.get('sale_end_date', '')}"
                    )

                if record.get(
                    "memo",
                    ""
                ):
                    st.write(
                        f"📝 {record.get('memo', '')}"
                    )

                with st.expander(
                    "✏️ この価格記録を編集"
                ):
                    edit_record_date = (
                        st.date_input(
                            "記録日",
                            value=parse_date(
                                record.get(
                                    "record_date",
                                    ""
                                )
                            ),
                            key=(
                                f"edit_record_date_"
                                f"{record_id}"
                            )
                        )
                    )

                    edit_price = (
                        st.number_input(
                            "販売価格",
                            min_value=0,
                            value=int(
                                record.get(
                                    "price",
                                    0
                                )
                            ),
                            step=10,
                            key=(
                                f"edit_price_"
                                f"{record_id}"
                            )
                        )
                    )

                    edit_amount = (
                        st.number_input(
                            "内容量",
                            min_value=0.01,
                            value=float(
                                record.get(
                                    "amount",
                                    1
                                )
                            ),
                            step=1.0,
                            key=(
                                f"edit_record_amount_"
                                f"{record_id}"
                            )
                        )
                    )

                    current_unit = record.get(
                        "unit_type",
                        "個"
                    )

                    unit_index = (
                        UNIT_TYPES.index(
                            current_unit
                        )
                        if current_unit
                        in UNIT_TYPES
                        else 0
                    )

                    edit_record_unit = (
                        st.selectbox(
                            "単位",
                            UNIT_TYPES,
                            index=unit_index,
                            key=(
                                f"edit_record_unit_"
                                f"{record_id}"
                            )
                        )
                    )

                    edit_sale_name = (
                        st.text_input(
                            "セール名",
                            value=record.get(
                                "sale_name",
                                ""
                            ),
                            key=(
                                f"edit_sale_name_"
                                f"{record_id}"
                            )
                        )
                    )

                    current_sale_end = (
                        record.get(
                            "sale_end_date",
                            ""
                        )
                    )

                    edit_has_sale_end = (
                        st.checkbox(
                            "セール終了日を設定",
                            value=bool(
                                current_sale_end
                            ),
                            key=(
                                f"edit_has_sale_end_"
                                f"{record_id}"
                            )
                        )
                    )

                    edit_sale_end_date = None

                    if edit_has_sale_end:
                        edit_sale_end_date = (
                            st.date_input(
                                "セール終了日",
                                value=(
                                    parse_date(
                                        current_sale_end
                                    )
                                    if current_sale_end
                                    else date.today()
                                ),
                                key=(
                                    f"edit_sale_end_"
                                    f"{record_id}"
                                )
                            )
                        )

                    edit_record_memo = (
                        st.text_area(
                            "メモ",
                            value=record.get(
                                "memo",
                                ""
                            ),
                            key=(
                                f"edit_record_memo_"
                                f"{record_id}"
                            )
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_record_"
                            f"{record_id}"
                        ),
                        use_container_width=True
                    ):
                        if edit_price <= 0:
                            st.error(
                                "販売価格を入力してください。"
                            )

                        elif edit_amount <= 0:
                            st.error(
                                "内容量を入力してください。"
                            )

                        else:
                            update_price_record(
                                data=data,
                                record_id=record_id,
                                record_date=(
                                    edit_record_date
                                ),
                                price=edit_price,
                                amount=edit_amount,
                                unit_type=(
                                    edit_record_unit
                                ),
                                sale_name=(
                                    edit_sale_name.strip()
                                ),
                                sale_end_date=(
                                    edit_sale_end_date
                                ),
                                memo=(
                                    edit_record_memo.strip()
                                )
                            )

                            st.success(
                                "価格記録を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ この価格記録を削除"
                ):
                    st.warning(
                        "削除した記録は"
                        "元に戻せません。"
                    )

                    confirm_record_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_record_delete_"
                                f"{record_id}"
                            )
                        )
                    )

                    if st.button(
                        "価格記録を削除",
                        key=(
                            f"delete_record_"
                            f"{record_id}"
                        ),
                        disabled=(
                            not confirm_record_delete
                        ),
                        use_container_width=True
                    ):
                        delete_price_record(
                            data,
                            record_id
                        )

                        st.rerun()


st.divider()

st.success(
    "価格を記録して、"
    "本当に安いお店と買い時を見つけよう！🛒"
)
