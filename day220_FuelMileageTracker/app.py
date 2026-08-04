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
    page_title="給油・燃費記録",
    page_icon="⛽",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "fuel_data.json",
)

FUEL_TYPES = [
    "レギュラー",
    "ハイオク",
    "軽油",
    "その他",
]

OWNERSHIP_TYPES = [
    "所有",
    "ローン",
    "リース",
    "レンタル",
    "会社車両",
    "その他",
]

REFUEL_TYPES = [
    "満タン",
    "部分給油",
]

USAGE_TYPES = [
    "仕事",
    "私用",
    "仕事・私用混合",
]

PAYMENT_METHODS = [
    "現金",
    "クレジットカード",
    "デビットカード",
    "電子マネー",
    "QR決済",
    "その他",
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを生成する。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds",
    )


def create_empty_data():
    """空のデータを生成する。"""

    return {
        "vehicles": [],
        "fuel_records": [],
        "monthly_finances": [],
    }


def save_data(data):
    """JSONファイルへ保存する。"""

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
    """古い保存データへ不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "vehicles",
        [],
    )

    data.setdefault(
        "fuel_records",
        [],
    )

    data.setdefault(
        "monthly_finances",
        [],
    )

    for vehicle in data["vehicles"]:
        vehicle.setdefault(
            "id",
            create_id(),
        )

        vehicle.setdefault(
            "name",
            "",
        )

        vehicle.setdefault(
            "number",
            "",
        )

        vehicle.setdefault(
            "fuel_type",
            "レギュラー",
        )

        vehicle.setdefault(
            "ownership_type",
            "所有",
        )

        vehicle.setdefault(
            "monthly_vehicle_cost",
            0,
        )

        vehicle.setdefault(
            "initial_odometer",
            0,
        )

        vehicle.setdefault(
            "memo",
            "",
        )

        vehicle.setdefault(
            "created_at",
            "",
        )

        vehicle.setdefault(
            "updated_at",
            "",
        )

    for record in data["fuel_records"]:
        record.setdefault(
            "id",
            create_id(),
        )

        record.setdefault(
            "vehicle_id",
            "",
        )

        record.setdefault(
            "refuel_date",
            str(date.today()),
        )

        record.setdefault(
            "fuel_amount",
            0.0,
        )

        record.setdefault(
            "total_cost",
            0,
        )

        record.setdefault(
            "unit_price",
            0.0,
        )

        record.setdefault(
            "odometer",
            0.0,
        )

        record.setdefault(
            "distance",
            0.0,
        )

        record.setdefault(
            "fuel_efficiency",
            0.0,
        )

        record.setdefault(
            "refuel_type",
            "満タン",
        )

        record.setdefault(
            "usage_type",
            "私用",
        )

        record.setdefault(
            "business_ratio",
            0,
        )

        record.setdefault(
            "station",
            "",
        )

        record.setdefault(
            "payment_method",
            "現金",
        )

        record.setdefault(
            "memo",
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

    for finance in data["monthly_finances"]:
        finance.setdefault(
            "id",
            create_id(),
        )

        finance.setdefault(
            "month",
            date.today().strftime(
                "%Y-%m",
            ),
        )

        finance.setdefault(
            "vehicle_id",
            "",
        )

        finance.setdefault(
            "sales",
            0,
        )

        finance.setdefault(
            "vehicle_cost",
            0,
        )

        finance.setdefault(
            "other_expenses",
            0,
        )

        finance.setdefault(
            "memo",
            "",
        )

        finance.setdefault(
            "created_at",
            "",
        )

        finance.setdefault(
            "updated_at",
            "",
        )

    return data


def load_data():
    """JSONファイルから読み込む。"""

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
        backup_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            os.replace(
                DATA_FILE,
                backup_file,
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
    """日付文字列をdate型へ変換する。"""

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
    """日付を日本語表示にする。"""

    parsed_date = parse_date(
        date_text,
    )

    if not parsed_date:
        return "日付不明"

    return parsed_date.strftime(
        "%Y年%m月%d日",
    )


def get_vehicle_by_id(
    data,
    vehicle_id,
):
    """IDから車両を取得する。"""

    for vehicle in data["vehicles"]:
        if vehicle.get(
            "id",
        ) == vehicle_id:
            return vehicle

    return None


def vehicle_display_name(
    vehicle,
):
    """車両の表示名を生成する。"""

    name = vehicle.get(
        "name",
        "名称なし",
    )

    number = vehicle.get(
        "number",
        "",
    )

    if number:
        return f"{name}｜{number}"

    return name


def get_vehicle_records(
    data,
    vehicle_id,
):
    """指定車両の給油記録を取得する。"""

    return [
        record
        for record in data[
            "fuel_records"
        ]
        if record.get(
            "vehicle_id",
        )
        == vehicle_id
    ]


def get_previous_record(
    data,
    vehicle_id,
    refuel_date,
    current_record_id="",
):
    """指定日より前の最新給油記録を取得する。"""

    target_date = parse_date(
        refuel_date,
    )

    candidates = []

    for record in data[
        "fuel_records"
    ]:
        if (
            record.get(
                "vehicle_id",
            )
            != vehicle_id
        ):
            continue

        if (
            current_record_id
            and record.get(
                "id",
            )
            == current_record_id
        ):
            continue

        record_date = parse_date(
            record.get(
                "refuel_date",
                "",
            )
        )

        if (
            record_date
            and target_date
            and record_date
            <= target_date
        ):
            candidates.append(
                record
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda record: (
            record.get(
                "refuel_date",
                "",
            ),
            record.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    )

    return candidates[0]


def calculate_record_values(
    data,
    vehicle_id,
    refuel_date,
    fuel_amount,
    total_cost,
    odometer,
    refuel_type,
    current_record_id="",
):
    """単価・走行距離・燃費を計算する。"""

    unit_price = 0.0
    distance = 0.0
    fuel_efficiency = 0.0

    if fuel_amount > 0:
        unit_price = (
            total_cost
            / fuel_amount
        )

    previous_record = get_previous_record(
        data=data,
        vehicle_id=vehicle_id,
        refuel_date=refuel_date,
        current_record_id=(
            current_record_id
        ),
    )

    if previous_record:
        previous_odometer = float(
            previous_record.get(
                "odometer",
                0,
            )
        )

        if odometer >= previous_odometer:
            distance = (
                odometer
                - previous_odometer
            )

    else:
        vehicle = get_vehicle_by_id(
            data,
            vehicle_id,
        )

        if vehicle:
            initial_odometer = float(
                vehicle.get(
                    "initial_odometer",
                    0,
                )
            )

            if (
                initial_odometer > 0
                and odometer
                >= initial_odometer
            ):
                distance = (
                    odometer
                    - initial_odometer
                )

    if (
        refuel_type == "満タン"
        and fuel_amount > 0
        and distance > 0
    ):
        fuel_efficiency = (
            distance
            / fuel_amount
        )

    return (
        unit_price,
        distance,
        fuel_efficiency,
    )


def business_fuel_cost(
    record,
):
    """仕事分のガソリン代を計算する。"""

    usage_type = record.get(
        "usage_type",
        "私用",
    )

    total_cost = float(
        record.get(
            "total_cost",
            0,
        )
    )

    if usage_type == "仕事":
        return total_cost

    if usage_type == "仕事・私用混合":
        ratio = float(
            record.get(
                "business_ratio",
                0,
            )
        )

        return (
            total_cost
            * ratio
            / 100
        )

    return 0


def private_fuel_cost(
    record,
):
    """私用分のガソリン代を計算する。"""

    return (
        float(
            record.get(
                "total_cost",
                0,
            )
        )
        - business_fuel_cost(
            record,
        )
    )


def get_records_for_month(
    records,
    target_month,
):
    """指定月の給油記録を取得する。"""

    return [
        record
        for record in records
        if record.get(
            "refuel_date",
            "",
        ).startswith(
            target_month,
        )
    ]


def average_nonzero(
    values,
):
    """0以外の平均を計算する。"""

    valid_values = [
        float(value)
        for value in values
        if float(value) > 0
    ]

    if not valid_values:
        return 0

    return (
        sum(valid_values)
        / len(valid_values)
    )


# =========================================================
# データ操作
# =========================================================

def add_vehicle(
    data,
    values,
):
    """車両を登録する。"""

    vehicle = {
        "id": create_id(),
        "name": values["name"],
        "number": values["number"],
        "fuel_type": values["fuel_type"],
        "ownership_type": (
            values["ownership_type"]
        ),
        "monthly_vehicle_cost": int(
            values[
                "monthly_vehicle_cost"
            ]
        ),
        "initial_odometer": float(
            values["initial_odometer"]
        ),
        "memo": values["memo"],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["vehicles"].append(
        vehicle,
    )

    save_data(data)


def update_vehicle(
    data,
    vehicle_id,
    values,
):
    """車両情報を更新する。"""

    vehicle = get_vehicle_by_id(
        data,
        vehicle_id,
    )

    if not vehicle:
        return

    for key, value in values.items():
        vehicle[key] = value

    vehicle[
        "monthly_vehicle_cost"
    ] = int(
        vehicle.get(
            "monthly_vehicle_cost",
            0,
        )
    )

    vehicle[
        "initial_odometer"
    ] = float(
        vehicle.get(
            "initial_odometer",
            0,
        )
    )

    vehicle["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_vehicle(
    data,
    vehicle_id,
):
    """車両と関連記録を削除する。"""

    data["vehicles"] = [
        vehicle
        for vehicle in data[
            "vehicles"
        ]
        if vehicle.get(
            "id",
        )
        != vehicle_id
    ]

    data["fuel_records"] = [
        record
        for record in data[
            "fuel_records"
        ]
        if record.get(
            "vehicle_id",
        )
        != vehicle_id
    ]

    data["monthly_finances"] = [
        finance
        for finance in data[
            "monthly_finances"
        ]
        if finance.get(
            "vehicle_id",
        )
        != vehicle_id
    ]

    save_data(data)


def add_fuel_record(
    data,
    values,
):
    """給油記録を追加する。"""

    (
        unit_price,
        distance,
        fuel_efficiency,
    ) = calculate_record_values(
        data=data,
        vehicle_id=(
            values["vehicle_id"]
        ),
        refuel_date=(
            values["refuel_date"]
        ),
        fuel_amount=float(
            values["fuel_amount"]
        ),
        total_cost=int(
            values["total_cost"]
        ),
        odometer=float(
            values["odometer"]
        ),
        refuel_type=(
            values["refuel_type"]
        ),
    )

    record = {
        "id": create_id(),
        "vehicle_id": (
            values["vehicle_id"]
        ),
        "refuel_date": (
            values["refuel_date"]
        ),
        "fuel_amount": float(
            values["fuel_amount"]
        ),
        "total_cost": int(
            values["total_cost"]
        ),
        "unit_price": round(
            unit_price,
            2,
        ),
        "odometer": float(
            values["odometer"]
        ),
        "distance": round(
            distance,
            1,
        ),
        "fuel_efficiency": round(
            fuel_efficiency,
            2,
        ),
        "refuel_type": (
            values["refuel_type"]
        ),
        "usage_type": (
            values["usage_type"]
        ),
        "business_ratio": int(
            values["business_ratio"]
        ),
        "station": values["station"],
        "payment_method": (
            values["payment_method"]
        ),
        "memo": values["memo"],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["fuel_records"].append(
        record,
    )

    save_data(data)


def update_fuel_record(
    data,
    record_id,
    values,
):
    """給油記録を更新する。"""

    record = next(
        (
            record
            for record in data[
                "fuel_records"
            ]
            if record.get(
                "id",
            )
            == record_id
        ),
        None,
    )

    if not record:
        return

    (
        unit_price,
        distance,
        fuel_efficiency,
    ) = calculate_record_values(
        data=data,
        vehicle_id=(
            values["vehicle_id"]
        ),
        refuel_date=(
            values["refuel_date"]
        ),
        fuel_amount=float(
            values["fuel_amount"]
        ),
        total_cost=int(
            values["total_cost"]
        ),
        odometer=float(
            values["odometer"]
        ),
        refuel_type=(
            values["refuel_type"]
        ),
        current_record_id=(
            record_id
        ),
    )

    for key, value in values.items():
        record[key] = value

    record["fuel_amount"] = float(
        values["fuel_amount"]
    )

    record["total_cost"] = int(
        values["total_cost"]
    )

    record["odometer"] = float(
        values["odometer"]
    )

    record["business_ratio"] = int(
        values["business_ratio"]
    )

    record["unit_price"] = round(
        unit_price,
        2,
    )

    record["distance"] = round(
        distance,
        1,
    )

    record["fuel_efficiency"] = round(
        fuel_efficiency,
        2,
    )

    record["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_fuel_record(
    data,
    record_id,
):
    """給油記録を削除する。"""

    data["fuel_records"] = [
        record
        for record in data[
            "fuel_records"
        ]
        if record.get(
            "id",
        )
        != record_id
    ]

    save_data(data)


def save_monthly_finance(
    data,
    values,
):
    """月間収支を保存する。"""

    existing = next(
        (
            finance
            for finance in data[
                "monthly_finances"
            ]
            if (
                finance.get(
                    "month",
                )
                == values["month"]
                and finance.get(
                    "vehicle_id",
                )
                == values[
                    "vehicle_id"
                ]
            )
        ),
        None,
    )

    if existing:
        existing["sales"] = int(
            values["sales"]
        )

        existing["vehicle_cost"] = int(
            values["vehicle_cost"]
        )

        existing["other_expenses"] = int(
            values["other_expenses"]
        )

        existing["memo"] = (
            values["memo"]
        )

        existing["updated_at"] = (
            now_text()
        )

    else:
        data[
            "monthly_finances"
        ].append(
            {
                "id": create_id(),
                "month": values["month"],
                "vehicle_id": (
                    values["vehicle_id"]
                ),
                "sales": int(
                    values["sales"]
                ),
                "vehicle_cost": int(
                    values["vehicle_cost"]
                ),
                "other_expenses": int(
                    values["other_expenses"]
                ),
                "memo": values["memo"],
                "created_at": now_text(),
                "updated_at": "",
            }
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
        background: rgba(255, 145, 45, 0.08);
        border: 1px solid rgba(255, 145, 45, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(255, 145, 45, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(255, 145, 45, 0.18),
                rgba(255, 210, 70, 0.12)
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
# データ読み込み
# =========================================================

data = load_data()

vehicles = data["vehicles"]
fuel_records = data[
    "fuel_records"
]

current_month = (
    date.today().strftime(
        "%Y-%m",
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⛽ 給油・燃費記録</h1>
        <p>
            給油量・ガソリン代・走行距離・実燃費をまとめて管理
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

current_month_records = (
    get_records_for_month(
        fuel_records,
        current_month,
    )
)

monthly_refuel_count = len(
    current_month_records,
)

monthly_cost = sum(
    int(
        record.get(
            "total_cost",
            0,
        )
    )
    for record
    in current_month_records
)

monthly_fuel_amount = sum(
    float(
        record.get(
            "fuel_amount",
            0,
        )
    )
    for record
    in current_month_records
)

monthly_distance = sum(
    float(
        record.get(
            "distance",
            0,
        )
    )
    for record
    in current_month_records
)

average_efficiency = average_nonzero(
    [
        record.get(
            "fuel_efficiency",
            0,
        )
        for record
        in current_month_records
    ]
)

average_unit_price = average_nonzero(
    [
        record.get(
            "unit_price",
            0,
        )
        for record
        in current_month_records
    ]
)

monthly_business_cost = sum(
    business_fuel_cost(
        record,
    )
    for record
    in current_month_records
)

monthly_private_cost = sum(
    private_fuel_cost(
        record,
    )
    for record
    in current_month_records
)


metric_row1 = st.columns(4)

metric_row1[0].metric(
    "今月の給油",
    f"{monthly_refuel_count}回",
)

metric_row1[1].metric(
    "今月のガソリン代",
    f"{monthly_cost:,.0f}円",
)

metric_row1[2].metric(
    "今月の給油量",
    f"{monthly_fuel_amount:.1f}L",
)

metric_row1[3].metric(
    "今月の走行距離",
    f"{monthly_distance:.1f}km",
)


metric_row2 = st.columns(4)

metric_row2[0].metric(
    "平均燃費",
    (
        f"{average_efficiency:.2f}km/L"
        if average_efficiency > 0
        else "未計算"
    ),
)

metric_row2[1].metric(
    "平均ガソリン単価",
    (
        f"{average_unit_price:.1f}円/L"
        if average_unit_price > 0
        else "未計算"
    ),
)

metric_row2[2].metric(
    "仕事用燃料費",
    f"{monthly_business_cost:,.0f}円",
)

metric_row2[3].metric(
    "私用燃料費",
    f"{monthly_private_cost:,.0f}円",
)


# =========================================================
# 最新給油
# =========================================================

if fuel_records:
    latest_record = sorted(
        fuel_records,
        key=lambda record: (
            record.get(
                "refuel_date",
                "",
            ),
            record.get(
                "created_at",
                "",
            ),
        ),
        reverse=True,
    )[0]

    latest_vehicle = (
        get_vehicle_by_id(
            data,
            latest_record.get(
                "vehicle_id",
                "",
            ),
        )
    )

    st.divider()
    st.subheader(
        "🧾 最新の給油記録"
    )

    with st.container(
        border=True,
    ):
        title_column, efficiency_column = (
            st.columns(
                [
                    4,
                    1,
                ]
            )
        )

        with title_column:
            st.markdown(
                f"### "
                f"{vehicle_display_name(latest_vehicle) if latest_vehicle else '車両不明'}"
            )

            st.caption(
                f"{format_date(latest_record.get('refuel_date', ''))} ／ "
                f"{latest_record.get('station', '') or '店舗未登録'}"
            )

            st.write(
                f"給油量："
                f"**{latest_record.get('fuel_amount', 0):.2f}L**"
            )

            st.write(
                f"支払金額："
                f"**{latest_record.get('total_cost', 0):,}円**"
            )

            st.write(
                f"単価："
                f"**{latest_record.get('unit_price', 0):.1f}円/L**"
            )

        with efficiency_column:
            efficiency = float(
                latest_record.get(
                    "fuel_efficiency",
                    0,
                )
            )

            st.metric(
                "実燃費",
                (
                    f"{efficiency:.2f}km/L"
                    if efficiency > 0
                    else "未計算"
                ),
            )

            st.metric(
                "走行距離",
                f"{latest_record.get('distance', 0):.1f}km",
            )


# =========================================================
# タブ
# =========================================================

st.divider()

(
    vehicle_tab,
    add_tab,
    records_tab,
    analysis_tab,
    finance_tab,
    data_tab,
) = st.tabs(
    [
        "🚗 車両管理",
        "➕ 給油記録",
        "📋 給油履歴",
        "📈 燃費分析",
        "💰 簡易収支",
        "💾 データ管理",
    ]
)


# =========================================================
# 車両管理
# =========================================================

with vehicle_tab:
    st.header(
        "🚗 車両管理"
    )

    with st.form(
        "add_vehicle_form",
        clear_on_submit=True,
    ):
        vehicle_column1, vehicle_column2 = (
            st.columns(2)
        )

        with vehicle_column1:
            vehicle_name = st.text_input(
                "車両名",
                placeholder=(
                    "例：Amazon Flex用軽バン"
                ),
            )

            vehicle_number = st.text_input(
                "ナンバー",
                placeholder=(
                    "例：静岡 480 あ 1234"
                ),
            )

            fuel_type = st.selectbox(
                "燃料種類",
                FUEL_TYPES,
            )

        with vehicle_column2:
            ownership_type = st.selectbox(
                "所有形態",
                OWNERSHIP_TYPES,
            )

            monthly_vehicle_cost = (
                st.number_input(
                    "月額車両費",
                    min_value=0,
                    max_value=1000000,
                    value=0,
                    step=1000,
                    help=(
                        "レンタル代、リース代、ローンなど"
                    ),
                )
            )

            initial_odometer = (
                st.number_input(
                    "登録時の総走行距離",
                    min_value=0.0,
                    max_value=10000000.0,
                    value=0.0,
                    step=1.0,
                )
            )

        vehicle_memo = st.text_area(
            "メモ",
            placeholder=(
                "契約内容、注意事項、車両情報など"
            ),
        )

        vehicle_submit = (
            st.form_submit_button(
                "🚗 車両を登録",
                use_container_width=True,
            )
        )

        if vehicle_submit:
            if not vehicle_name.strip():
                st.error(
                    "車両名を入力してください。"
                )

            else:
                add_vehicle(
                    data,
                    {
                        "name": (
                            vehicle_name.strip()
                        ),
                        "number": (
                            vehicle_number.strip()
                        ),
                        "fuel_type": fuel_type,
                        "ownership_type": (
                            ownership_type
                        ),
                        "monthly_vehicle_cost": (
                            monthly_vehicle_cost
                        ),
                        "initial_odometer": (
                            initial_odometer
                        ),
                        "memo": (
                            vehicle_memo.strip()
                        ),
                    },
                )

                st.success(
                    "車両を登録しました！"
                )

                st.rerun()

    st.divider()

    if not vehicles:
        st.info(
            "車両はまだ登録されていません。"
        )

    for vehicle in vehicles:
        vehicle_id = vehicle["id"]

        vehicle_records = (
            get_vehicle_records(
                data,
                vehicle_id,
            )
        )

        with st.container(
            border=True,
        ):
            st.subheader(
                vehicle_display_name(
                    vehicle,
                )
            )

            info_columns = st.columns(4)

            info_columns[0].metric(
                "燃料",
                vehicle.get(
                    "fuel_type",
                    "",
                ),
            )

            info_columns[1].metric(
                "所有形態",
                vehicle.get(
                    "ownership_type",
                    "",
                ),
            )

            info_columns[2].metric(
                "月額車両費",
                f"{vehicle.get('monthly_vehicle_cost', 0):,}円",
            )

            info_columns[3].metric(
                "給油記録",
                f"{len(vehicle_records)}件",
            )

            if vehicle.get(
                "memo",
                "",
            ):
                st.info(
                    vehicle.get(
                        "memo",
                        "",
                    )
                )

            with st.expander(
                "✏️ 車両情報を編集"
            ):
                edit_name = st.text_input(
                    "車両名",
                    value=vehicle.get(
                        "name",
                        "",
                    ),
                    key=(
                        f"edit_vehicle_name_"
                        f"{vehicle_id}"
                    ),
                )

                edit_number = st.text_input(
                    "ナンバー",
                    value=vehicle.get(
                        "number",
                        "",
                    ),
                    key=(
                        f"edit_vehicle_number_"
                        f"{vehicle_id}"
                    ),
                )

                current_fuel_type = (
                    vehicle.get(
                        "fuel_type",
                        "レギュラー",
                    )
                )

                edit_fuel_type = st.selectbox(
                    "燃料種類",
                    FUEL_TYPES,
                    index=(
                        FUEL_TYPES.index(
                            current_fuel_type
                        )
                        if current_fuel_type
                        in FUEL_TYPES
                        else 0
                    ),
                    key=(
                        f"edit_vehicle_fuel_"
                        f"{vehicle_id}"
                    ),
                )

                current_ownership = (
                    vehicle.get(
                        "ownership_type",
                        "所有",
                    )
                )

                edit_ownership = st.selectbox(
                    "所有形態",
                    OWNERSHIP_TYPES,
                    index=(
                        OWNERSHIP_TYPES.index(
                            current_ownership
                        )
                        if current_ownership
                        in OWNERSHIP_TYPES
                        else 0
                    ),
                    key=(
                        f"edit_vehicle_ownership_"
                        f"{vehicle_id}"
                    ),
                )

                edit_monthly_cost = (
                    st.number_input(
                        "月額車両費",
                        min_value=0,
                        max_value=1000000,
                        value=int(
                            vehicle.get(
                                "monthly_vehicle_cost",
                                0,
                            )
                        ),
                        key=(
                            f"edit_vehicle_cost_"
                            f"{vehicle_id}"
                        ),
                    )
                )

                edit_initial_odometer = (
                    st.number_input(
                        "登録時走行距離",
                        min_value=0.0,
                        max_value=10000000.0,
                        value=float(
                            vehicle.get(
                                "initial_odometer",
                                0,
                            )
                        ),
                        key=(
                            f"edit_vehicle_odometer_"
                            f"{vehicle_id}"
                        ),
                    )
                )

                edit_vehicle_memo = (
                    st.text_area(
                        "メモ",
                        value=vehicle.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_vehicle_memo_"
                            f"{vehicle_id}"
                        ),
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_vehicle_"
                        f"{vehicle_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_name.strip():
                        st.error(
                            "車両名を入力してください。"
                        )

                    else:
                        update_vehicle(
                            data,
                            vehicle_id,
                            {
                                "name": (
                                    edit_name.strip()
                                ),
                                "number": (
                                    edit_number.strip()
                                ),
                                "fuel_type": (
                                    edit_fuel_type
                                ),
                                "ownership_type": (
                                    edit_ownership
                                ),
                                "monthly_vehicle_cost": (
                                    edit_monthly_cost
                                ),
                                "initial_odometer": (
                                    edit_initial_odometer
                                ),
                                "memo": (
                                    edit_vehicle_memo.strip()
                                ),
                            },
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 車両を削除"
            ):
                st.warning(
                    "この車両の給油記録もすべて削除されます。"
                )

                confirm_vehicle_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_vehicle_delete_"
                            f"{vehicle_id}"
                        ),
                    )
                )

                if st.button(
                    "この車両を削除",
                    key=(
                        f"delete_vehicle_"
                        f"{vehicle_id}"
                    ),
                    disabled=(
                        not confirm_vehicle_delete
                    ),
                    use_container_width=True,
                ):
                    delete_vehicle(
                        data,
                        vehicle_id,
                    )

                    st.rerun()


# =========================================================
# 給油記録
# =========================================================

with add_tab:
    st.header(
        "➕ 給油を記録"
    )

    if not vehicles:
        st.warning(
            "先に車両を登録してください。"
        )

    else:
        vehicle_options = {
            vehicle_display_name(
                vehicle,
            ): vehicle["id"]
            for vehicle in vehicles
        }

        with st.form(
            "add_fuel_record_form",
            clear_on_submit=True,
        ):
            record_column1, record_column2 = (
                st.columns(2)
            )

            with record_column1:
                selected_vehicle_name = (
                    st.selectbox(
                        "車両",
                        list(
                            vehicle_options.keys()
                        ),
                    )
                )

                selected_vehicle_id = (
                    vehicle_options[
                        selected_vehicle_name
                    ]
                )

                refuel_date_input = (
                    st.date_input(
                        "給油日",
                        value=date.today(),
                        max_value=date.today(),
                    )
                )

                fuel_amount = (
                    st.number_input(
                        "給油量（L）",
                        min_value=0.01,
                        max_value=1000.0,
                        value=20.0,
                        step=0.1,
                    )
                )

                total_cost = (
                    st.number_input(
                        "支払金額（円）",
                        min_value=1,
                        max_value=1000000,
                        value=3500,
                        step=1,
                    )
                )

            with record_column2:
                odometer = (
                    st.number_input(
                        "総走行距離（km）",
                        min_value=0.0,
                        max_value=10000000.0,
                        value=0.0,
                        step=1.0,
                    )
                )

                refuel_type = st.selectbox(
                    "給油方法",
                    REFUEL_TYPES,
                )

                usage_type = st.selectbox(
                    "用途",
                    USAGE_TYPES,
                )

                business_ratio = 0

                if (
                    usage_type
                    == "仕事・私用混合"
                ):
                    business_ratio = (
                        st.slider(
                            "仕事使用割合",
                            min_value=0,
                            max_value=100,
                            value=50,
                        )
                    )

                elif usage_type == "仕事":
                    business_ratio = 100

            station = st.text_input(
                "給油店舗",
                placeholder=(
                    "例：〇〇石油 静岡店"
                ),
            )

            payment_method = st.selectbox(
                "支払い方法",
                PAYMENT_METHODS,
            )

            record_memo = st.text_area(
                "メモ",
                placeholder=(
                    "エアコン使用、長距離走行など"
                ),
            )

            calculated_unit_price = (
                total_cost
                / fuel_amount
                if fuel_amount > 0
                else 0
            )

            st.info(
                f"1Lあたりの価格："
                f"**{calculated_unit_price:.1f}円/L**"
            )

            record_submit = (
                st.form_submit_button(
                    "⛽ 給油記録を保存",
                    use_container_width=True,
                )
            )

            if record_submit:
                if odometer <= 0:
                    st.error(
                        "総走行距離を入力してください。"
                    )

                else:
                    add_fuel_record(
                        data,
                        {
                            "vehicle_id": (
                                selected_vehicle_id
                            ),
                            "refuel_date": str(
                                refuel_date_input
                            ),
                            "fuel_amount": (
                                fuel_amount
                            ),
                            "total_cost": (
                                total_cost
                            ),
                            "odometer": odometer,
                            "refuel_type": (
                                refuel_type
                            ),
                            "usage_type": (
                                usage_type
                            ),
                            "business_ratio": (
                                business_ratio
                            ),
                            "station": (
                                station.strip()
                            ),
                            "payment_method": (
                                payment_method
                            ),
                            "memo": (
                                record_memo.strip()
                            ),
                        },
                    )

                    st.success(
                        "給油記録を保存しました！"
                    )

                    st.rerun()


# =========================================================
# 給油履歴
# =========================================================

with records_tab:
    st.header(
        "📋 給油履歴"
    )

    if not fuel_records:
        st.info(
            "給油記録はまだありません。"
        )

    else:
        history_vehicle_options = {
            "すべて": ""
        }

        for vehicle in vehicles:
            history_vehicle_options[
                vehicle_display_name(
                    vehicle,
                )
            ] = vehicle["id"]

        filter_column1, filter_column2 = (
            st.columns(2)
        )

        with filter_column1:
            history_vehicle_name = (
                st.selectbox(
                    "車両で絞り込み",
                    list(
                        history_vehicle_options.keys()
                    ),
                )
            )

        with filter_column2:
            usage_filter = st.selectbox(
                "用途で絞り込み",
                [
                    "すべて"
                ]
                + USAGE_TYPES,
            )

        selected_history_vehicle = (
            history_vehicle_options[
                history_vehicle_name
            ]
        )

        filtered_records = list(
            fuel_records
        )

        if selected_history_vehicle:
            filtered_records = [
                record
                for record
                in filtered_records
                if record.get(
                    "vehicle_id",
                )
                == selected_history_vehicle
            ]

        if usage_filter != "すべて":
            filtered_records = [
                record
                for record
                in filtered_records
                if record.get(
                    "usage_type",
                )
                == usage_filter
            ]

        filtered_records.sort(
            key=lambda record: (
                record.get(
                    "refuel_date",
                    "",
                ),
                record.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        st.write(
            f"表示件数："
            f"**{len(filtered_records)}件**"
        )

        for record in filtered_records:
            record_id = record["id"]

            vehicle = get_vehicle_by_id(
                data,
                record.get(
                    "vehicle_id",
                    "",
                ),
            )

            with st.container(
                border=True,
            ):
                title_column, efficiency_column = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with title_column:
                    st.markdown(
                        f"### "
                        f"{vehicle_display_name(vehicle) if vehicle else '車両不明'}"
                    )

                    st.caption(
                        f"{format_date(record.get('refuel_date', ''))} ／ "
                        f"{record.get('station', '') or '店舗未登録'}"
                    )

                with efficiency_column:
                    fuel_efficiency = float(
                        record.get(
                            "fuel_efficiency",
                            0,
                        )
                    )

                    st.metric(
                        "燃費",
                        (
                            f"{fuel_efficiency:.2f}km/L"
                            if fuel_efficiency > 0
                            else "未計算"
                        ),
                    )

                detail_columns = st.columns(4)

                detail_columns[0].metric(
                    "給油量",
                    f"{record.get('fuel_amount', 0):.2f}L",
                )

                detail_columns[1].metric(
                    "金額",
                    f"{record.get('total_cost', 0):,}円",
                )

                detail_columns[2].metric(
                    "単価",
                    f"{record.get('unit_price', 0):.1f}円/L",
                )

                detail_columns[3].metric(
                    "走行距離",
                    f"{record.get('distance', 0):.1f}km",
                )

                st.write(
                    f"総走行距離："
                    f"**{record.get('odometer', 0):,.1f}km**"
                )

                st.write(
                    f"用途："
                    f"**{record.get('usage_type', '')}**"
                )

                if (
                    record.get(
                        "usage_type",
                    )
                    == "仕事・私用混合"
                ):
                    st.write(
                        f"仕事使用割合："
                        f"**{record.get('business_ratio', 0)}%**"
                    )

                if record.get(
                    "memo",
                    "",
                ):
                    st.info(
                        record.get(
                            "memo",
                            "",
                        )
                    )

                with st.expander(
                    "✏️ 給油記録を編集"
                ):
                    edit_date = st.date_input(
                        "給油日",
                        value=(
                            parse_date(
                                record.get(
                                    "refuel_date",
                                    "",
                                )
                            )
                            or date.today()
                        ),
                        max_value=date.today(),
                        key=(
                            f"edit_record_date_"
                            f"{record_id}"
                        ),
                    )

                    edit_fuel_amount = (
                        st.number_input(
                            "給油量",
                            min_value=0.01,
                            max_value=1000.0,
                            value=float(
                                record.get(
                                    "fuel_amount",
                                    0,
                                )
                            ),
                            key=(
                                f"edit_record_amount_"
                                f"{record_id}"
                            ),
                        )
                    )

                    edit_total_cost = (
                        st.number_input(
                            "支払金額",
                            min_value=1,
                            max_value=1000000,
                            value=int(
                                record.get(
                                    "total_cost",
                                    0,
                                )
                            ),
                            key=(
                                f"edit_record_cost_"
                                f"{record_id}"
                            ),
                        )
                    )

                    edit_odometer = (
                        st.number_input(
                            "総走行距離",
                            min_value=0.0,
                            max_value=10000000.0,
                            value=float(
                                record.get(
                                    "odometer",
                                    0,
                                )
                            ),
                            key=(
                                f"edit_record_odometer_"
                                f"{record_id}"
                            ),
                        )
                    )

                    current_refuel_type = (
                        record.get(
                            "refuel_type",
                            "満タン",
                        )
                    )

                    edit_refuel_type = (
                        st.selectbox(
                            "給油方法",
                            REFUEL_TYPES,
                            index=(
                                REFUEL_TYPES.index(
                                    current_refuel_type
                                )
                                if current_refuel_type
                                in REFUEL_TYPES
                                else 0
                            ),
                            key=(
                                f"edit_refuel_type_"
                                f"{record_id}"
                            ),
                        )
                    )

                    current_usage = record.get(
                        "usage_type",
                        "私用",
                    )

                    edit_usage = st.selectbox(
                        "用途",
                        USAGE_TYPES,
                        index=(
                            USAGE_TYPES.index(
                                current_usage
                            )
                            if current_usage
                            in USAGE_TYPES
                            else 1
                        ),
                        key=(
                            f"edit_usage_"
                            f"{record_id}"
                        ),
                    )

                    edit_business_ratio = 0

                    if (
                        edit_usage
                        == "仕事・私用混合"
                    ):
                        edit_business_ratio = (
                            st.slider(
                                "仕事使用割合",
                                min_value=0,
                                max_value=100,
                                value=int(
                                    record.get(
                                        "business_ratio",
                                        50,
                                    )
                                ),
                                key=(
                                    f"edit_business_ratio_"
                                    f"{record_id}"
                                ),
                            )
                        )

                    elif edit_usage == "仕事":
                        edit_business_ratio = 100

                    edit_station = st.text_input(
                        "給油店舗",
                        value=record.get(
                            "station",
                            "",
                        ),
                        key=(
                            f"edit_station_"
                            f"{record_id}"
                        ),
                    )

                    current_payment = (
                        record.get(
                            "payment_method",
                            "現金",
                        )
                    )

                    edit_payment = st.selectbox(
                        "支払い方法",
                        PAYMENT_METHODS,
                        index=(
                            PAYMENT_METHODS.index(
                                current_payment
                            )
                            if current_payment
                            in PAYMENT_METHODS
                            else 0
                        ),
                        key=(
                            f"edit_payment_"
                            f"{record_id}"
                        ),
                    )

                    edit_memo = st.text_area(
                        "メモ",
                        value=record.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_record_memo_"
                            f"{record_id}"
                        ),
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_record_"
                            f"{record_id}"
                        ),
                        use_container_width=True,
                    ):
                        update_fuel_record(
                            data,
                            record_id,
                            {
                                "vehicle_id": (
                                    record.get(
                                        "vehicle_id",
                                        "",
                                    )
                                ),
                                "refuel_date": str(
                                    edit_date
                                ),
                                "fuel_amount": (
                                    edit_fuel_amount
                                ),
                                "total_cost": (
                                    edit_total_cost
                                ),
                                "odometer": (
                                    edit_odometer
                                ),
                                "refuel_type": (
                                    edit_refuel_type
                                ),
                                "usage_type": (
                                    edit_usage
                                ),
                                "business_ratio": (
                                    edit_business_ratio
                                ),
                                "station": (
                                    edit_station.strip()
                                ),
                                "payment_method": (
                                    edit_payment
                                ),
                                "memo": (
                                    edit_memo.strip()
                                ),
                            },
                        )

                        st.rerun()

                with st.expander(
                    "🗑️ 給油記録を削除"
                ):
                    confirm_record_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_record_delete_"
                                f"{record_id}"
                            ),
                        )
                    )

                    if st.button(
                        "この給油記録を削除",
                        key=(
                            f"delete_record_"
                            f"{record_id}"
                        ),
                        disabled=(
                            not confirm_record_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_fuel_record(
                            data,
                            record_id,
                        )

                        st.rerun()


# =========================================================
# 燃費分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 燃費・ガソリン代分析"
    )

    if not fuel_records:
        st.info(
            "分析できる給油記録がありません。"
        )

    else:
        analysis_rows = []

        for record in fuel_records:
            vehicle = get_vehicle_by_id(
                data,
                record.get(
                    "vehicle_id",
                    "",
                ),
            )

            analysis_rows.append(
                {
                    "日付": record.get(
                        "refuel_date",
                        "",
                    ),
                    "月": record.get(
                        "refuel_date",
                        "",
                    )[:7],
                    "車両": (
                        vehicle_display_name(
                            vehicle,
                        )
                        if vehicle
                        else "車両不明"
                    ),
                    "店舗": (
                        record.get(
                            "station",
                            "",
                        )
                        or "未登録"
                    ),
                    "給油量": float(
                        record.get(
                            "fuel_amount",
                            0,
                        )
                    ),
                    "金額": int(
                        record.get(
                            "total_cost",
                            0,
                        )
                    ),
                    "単価": float(
                        record.get(
                            "unit_price",
                            0,
                        )
                    ),
                    "走行距離": float(
                        record.get(
                            "distance",
                            0,
                        )
                    ),
                    "燃費": float(
                        record.get(
                            "fuel_efficiency",
                            0,
                        )
                    ),
                    "仕事燃料費": round(
                        business_fuel_cost(
                            record,
                        ),
                        0,
                    ),
                    "私用燃料費": round(
                        private_fuel_cost(
                            record,
                        ),
                        0,
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows,
        )

        st.subheader(
            "月別ガソリン代"
        )

        monthly_cost_df = (
            analysis_df.groupby(
                "月",
                as_index=False,
            )
            .agg(
                ガソリン代=(
                    "金額",
                    "sum",
                ),
                給油量=(
                    "給油量",
                    "sum",
                ),
                走行距離=(
                    "走行距離",
                    "sum",
                ),
                仕事燃料費=(
                    "仕事燃料費",
                    "sum",
                ),
                私用燃料費=(
                    "私用燃料費",
                    "sum",
                ),
            )
            .sort_values(
                "月",
            )
        )

        st.bar_chart(
            monthly_cost_df.set_index(
                "月",
            )[
                [
                    "仕事燃料費",
                    "私用燃料費",
                ]
            ]
        )

        st.dataframe(
            monthly_cost_df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "燃費の推移"
        )

        efficiency_df = (
            analysis_df[
                analysis_df[
                    "燃費"
                ]
                > 0
            ]
            .sort_values(
                "日付",
            )
        )

        if efficiency_df.empty:
            st.info(
                "満タン給油が2回以上記録されると燃費を表示できます。"
            )

        else:
            st.line_chart(
                efficiency_df.set_index(
                    "日付",
                )[["燃費"]]
            )

            st.dataframe(
                efficiency_df[
                    [
                        "日付",
                        "車両",
                        "燃費",
                        "走行距離",
                        "給油量",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "店舗別ガソリン価格"
        )

        station_df = (
            analysis_df.groupby(
                "店舗",
                as_index=False,
            )
            .agg(
                平均単価=(
                    "単価",
                    "mean",
                ),
                最安単価=(
                    "単価",
                    "min",
                ),
                最高単価=(
                    "単価",
                    "max",
                ),
                給油回数=(
                    "単価",
                    "count",
                ),
            )
            .sort_values(
                "平均単価",
            )
        )

        station_df[
            "平均単価"
        ] = station_df[
            "平均単価"
        ].round(1)

        station_df[
            "最安単価"
        ] = station_df[
            "最安単価"
        ].round(1)

        station_df[
            "最高単価"
        ] = station_df[
            "最高単価"
        ].round(1)

        st.bar_chart(
            station_df.set_index(
                "店舗",
            )[["平均単価"]]
        )

        st.dataframe(
            station_df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "車両別集計"
        )

        vehicle_df = (
            analysis_df.groupby(
                "車両",
                as_index=False,
            )
            .agg(
                給油回数=(
                    "金額",
                    "count",
                ),
                ガソリン代=(
                    "金額",
                    "sum",
                ),
                給油量=(
                    "給油量",
                    "sum",
                ),
                走行距離=(
                    "走行距離",
                    "sum",
                ),
                平均燃費=(
                    "燃費",
                    lambda values: (
                        values[
                            values > 0
                        ].mean()
                    ),
                ),
            )
        )

        vehicle_df[
            "平均燃費"
        ] = vehicle_df[
            "平均燃費"
        ].fillna(
            0,
        ).round(
            2,
        )

        st.dataframe(
            vehicle_df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 簡易収支
# =========================================================

with finance_tab:
    st.header(
        "💰 Amazon Flex・仕事用簡易収支"
    )

    if not vehicles:
        st.info(
            "先に車両を登録してください。"
        )

    else:
        finance_vehicle_options = {
            vehicle_display_name(
                vehicle,
            ): vehicle["id"]
            for vehicle in vehicles
        }

        finance_vehicle_name = (
            st.selectbox(
                "車両",
                list(
                    finance_vehicle_options.keys()
                ),
                key="finance_vehicle",
            )
        )

        finance_vehicle_id = (
            finance_vehicle_options[
                finance_vehicle_name
            ]
        )

        finance_month = st.text_input(
            "対象月",
            value=current_month,
            placeholder="2026-08",
        )

        selected_vehicle = (
            get_vehicle_by_id(
                data,
                finance_vehicle_id,
            )
        )

        existing_finance = next(
            (
                finance
                for finance in data[
                    "monthly_finances"
                ]
                if (
                    finance.get(
                        "month",
                    )
                    == finance_month
                    and finance.get(
                        "vehicle_id",
                    )
                    == finance_vehicle_id
                )
            ),
            None,
        )

        month_vehicle_records = [
            record
            for record in fuel_records
            if (
                record.get(
                    "vehicle_id",
                )
                == finance_vehicle_id
                and record.get(
                    "refuel_date",
                    "",
                ).startswith(
                    finance_month,
                )
            )
        ]

        business_cost = sum(
            business_fuel_cost(
                record,
            )
            for record
            in month_vehicle_records
        )

        total_distance = sum(
            float(
                record.get(
                    "distance",
                    0,
                )
            )
            for record
            in month_vehicle_records
        )

        default_vehicle_cost = int(
            (
                existing_finance.get(
                    "vehicle_cost",
                    0,
                )
                if existing_finance
                else selected_vehicle.get(
                    "monthly_vehicle_cost",
                    0,
                )
            )
        )

        with st.form(
            "monthly_finance_form",
        ):
            sales = st.number_input(
                "月間売上",
                min_value=0,
                max_value=100000000,
                value=int(
                    existing_finance.get(
                        "sales",
                        0,
                    )
                    if existing_finance
                    else 0
                ),
                step=1000,
            )

            vehicle_cost = st.number_input(
                "車両レンタル・リース代",
                min_value=0,
                max_value=10000000,
                value=default_vehicle_cost,
                step=1000,
            )

            other_expenses = (
                st.number_input(
                    "その他経費",
                    min_value=0,
                    max_value=10000000,
                    value=int(
                        existing_finance.get(
                            "other_expenses",
                            0,
                        )
                        if existing_finance
                        else 0
                    ),
                    step=1000,
                    help=(
                        "駐車場、高速代、備品代など"
                    ),
                )
            )

            finance_memo = st.text_area(
                "メモ",
                value=(
                    existing_finance.get(
                        "memo",
                        "",
                    )
                    if existing_finance
                    else ""
                ),
            )

            finance_submit = (
                st.form_submit_button(
                    "収支データを保存",
                    use_container_width=True,
                )
            )

            if finance_submit:
                save_monthly_finance(
                    data,
                    {
                        "month": (
                            finance_month.strip()
                        ),
                        "vehicle_id": (
                            finance_vehicle_id
                        ),
                        "sales": sales,
                        "vehicle_cost": (
                            vehicle_cost
                        ),
                        "other_expenses": (
                            other_expenses
                        ),
                        "memo": (
                            finance_memo.strip()
                        ),
                    },
                )

                st.success(
                    "収支データを保存しました！"
                )

                st.rerun()

        estimated_profit = (
            sales
            - business_cost
            - vehicle_cost
            - other_expenses
        )

        fuel_cost_rate = (
            business_cost
            / sales
            * 100
            if sales > 0
            else 0
        )

        fuel_cost_per_km = (
            business_cost
            / total_distance
            if total_distance > 0
            else 0
        )

        finance_columns = st.columns(4)

        finance_columns[0].metric(
            "仕事用燃料費",
            f"{business_cost:,.0f}円",
        )

        finance_columns[1].metric(
            "概算利益",
            f"{estimated_profit:,.0f}円",
        )

        finance_columns[2].metric(
            "燃料費率",
            f"{fuel_cost_rate:.1f}%",
        )

        finance_columns[3].metric(
            "1kmあたり燃料費",
            (
                f"{fuel_cost_per_km:.1f}円"
                if fuel_cost_per_km > 0
                else "未計算"
            ),
        )

        st.info(
            "概算利益 ＝ 売上 − 仕事用燃料費 − 車両費 − その他経費"
        )

        st.caption(
            "税金・社会保険料・減価償却などは含まれていない簡易計算です。"
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
            f"fuel_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = (
        st.file_uploader(
            "バックアップJSONを選択",
            type=[
                "json"
            ],
        )
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file,
            )

            if (
                not isinstance(
                    imported_data,
                    dict,
                )
                or "vehicles"
                not in imported_data
                or "fuel_records"
                not in imported_data
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
                        imported_data,
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
        "車両・給油記録・収支データがすべて削除されます。"
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
            create_empty_data(),
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
    "給油と走行を記録して、車にかかる本当のコストを見える化しよう。⛽"
)
