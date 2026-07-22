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
    page_title="給油・燃費記録",
    page_icon="🚗",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "fuel_data.json"
)

DEFAULT_DATA = {
    "vehicles": [],
    "records": []
}


# =====================================
# データ保存・読み込み
# =====================================

def create_empty_data():
    """初期データを返す。"""

    return {
        "vehicles": [],
        "records": []
    }


def save_data(data):
    """データをJSONファイルへ保存する。"""

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
            "vehicles",
            []
        )

        data.setdefault(
            "records",
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
# 車両管理
# =====================================

def add_vehicle(
    data,
    vehicle_name,
    vehicle_type,
    fuel_type,
    memo
):
    """車両を登録する。"""

    vehicle = {
        "id": str(uuid.uuid4()),
        "name": vehicle_name,
        "vehicle_type": vehicle_type,
        "fuel_type": fuel_type,
        "memo": memo,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["vehicles"].append(
        vehicle
    )

    save_data(data)


def update_vehicle(
    data,
    vehicle_id,
    vehicle_name,
    vehicle_type,
    fuel_type,
    memo
):
    """車両情報を更新する。"""

    for vehicle in data["vehicles"]:
        if vehicle.get("id") == vehicle_id:
            vehicle["name"] = vehicle_name
            vehicle["vehicle_type"] = (
                vehicle_type
            )
            vehicle["fuel_type"] = fuel_type
            vehicle["memo"] = memo
            vehicle["updated_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )
            break

    save_data(data)


def delete_vehicle(
    data,
    vehicle_id
):
    """車両と関連する給油記録を削除する。"""

    data["vehicles"] = [
        vehicle
        for vehicle in data["vehicles"]
        if vehicle.get("id") != vehicle_id
    ]

    data["records"] = [
        record
        for record in data["records"]
        if record.get("vehicle_id")
        != vehicle_id
    ]

    save_data(data)


# =====================================
# 給油記録管理
# =====================================

def calculate_fuel_economy(
    distance,
    fuel_amount
):
    """燃費を計算する。"""

    if fuel_amount <= 0:
        return 0.0

    return round(
        distance / fuel_amount,
        2
    )


def calculate_unit_price(
    total_price,
    fuel_amount
):
    """1リットルあたりの単価を計算する。"""

    if fuel_amount <= 0:
        return 0.0

    return round(
        total_price / fuel_amount,
        1
    )


def add_fuel_record(
    data,
    vehicle_id,
    fuel_date,
    distance,
    odometer,
    fuel_amount,
    total_price,
    fuel_type,
    fill_type,
    station,
    memo
):
    """給油記録を追加する。"""

    fuel_economy = calculate_fuel_economy(
        distance,
        fuel_amount
    )

    unit_price = calculate_unit_price(
        total_price,
        fuel_amount
    )

    record = {
        "id": str(uuid.uuid4()),
        "vehicle_id": vehicle_id,
        "fuel_date": str(fuel_date),
        "distance": float(distance),
        "odometer": float(odometer),
        "fuel_amount": float(fuel_amount),
        "total_price": int(total_price),
        "fuel_type": fuel_type,
        "fill_type": fill_type,
        "station": station,
        "memo": memo,
        "fuel_economy": fuel_economy,
        "unit_price": unit_price,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["records"].append(
        record
    )

    save_data(data)


def update_fuel_record(
    data,
    record_id,
    fuel_date,
    distance,
    odometer,
    fuel_amount,
    total_price,
    fuel_type,
    fill_type,
    station,
    memo
):
    """給油記録を更新する。"""

    for record in data["records"]:
        if record.get("id") == record_id:
            record["fuel_date"] = str(
                fuel_date
            )
            record["distance"] = float(
                distance
            )
            record["odometer"] = float(
                odometer
            )
            record["fuel_amount"] = float(
                fuel_amount
            )
            record["total_price"] = int(
                total_price
            )
            record["fuel_type"] = fuel_type
            record["fill_type"] = fill_type
            record["station"] = station
            record["memo"] = memo

            record["fuel_economy"] = (
                calculate_fuel_economy(
                    distance,
                    fuel_amount
                )
            )

            record["unit_price"] = (
                calculate_unit_price(
                    total_price,
                    fuel_amount
                )
            )

            record["updated_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )

            break

    save_data(data)


def delete_fuel_record(
    data,
    record_id
):
    """給油記録を削除する。"""

    data["records"] = [
        record
        for record in data["records"]
        if record.get("id") != record_id
    ]

    save_data(data)


# =====================================
# 補助関数
# =====================================

def get_vehicle_name(
    data,
    vehicle_id
):
    """車両IDから車両名を取得する。"""

    for vehicle in data["vehicles"]:
        if vehicle.get("id") == vehicle_id:
            return vehicle.get(
                "name",
                "名称未設定"
            )

    return "不明な車両"


def get_vehicle_by_id(
    data,
    vehicle_id
):
    """車両IDから車両情報を取得する。"""

    for vehicle in data["vehicles"]:
        if vehicle.get("id") == vehicle_id:
            return vehicle

    return None


def parse_date(date_text):
    """文字列の日付をdate型へ変換する。"""

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


def format_price(value):
    """日本円形式で表示する。"""

    return f"¥{int(value):,}"


def format_number(
    value,
    decimal_places=1
):
    """数値を見やすく整形する。"""

    return (
        f"{float(value):,.{decimal_places}f}"
    )


def get_record_month(record):
    """記録の日付から年月を取得する。"""

    fuel_date = record.get(
        "fuel_date",
        ""
    )

    try:
        return datetime.strptime(
            fuel_date,
            "%Y-%m-%d"
        ).strftime("%Y-%m")

    except ValueError:
        return ""


def calculate_average(
    values
):
    """平均値を計算する。"""

    valid_values = [
        float(value)
        for value in values
        if float(value) > 0
    ]

    if not valid_values:
        return 0.0

    return sum(valid_values) / len(
        valid_values
    )


# =====================================
# データ読み込み
# =====================================

data = load_data()

vehicles = data["vehicles"]
records = data["records"]


# =====================================
# タイトル
# =====================================

st.title("🚗 給油・燃費記録")

st.caption(
    "給油量・ガソリン代・走行距離を記録して、"
    "車の燃費と維持費を見える化します。"
)


# =====================================
# 車両選択
# =====================================

if vehicles:
    vehicle_options = {
        vehicle.get(
            "name",
            "名称未設定"
        ): vehicle.get(
            "id",
            ""
        )
        for vehicle in vehicles
    }

    selected_vehicle_name = (
        st.selectbox(
            "🚘 表示する車両",
            list(
                vehicle_options.keys()
            )
        )
    )

    selected_vehicle_id = (
        vehicle_options[
            selected_vehicle_name
        ]
    )

else:
    selected_vehicle_name = ""
    selected_vehicle_id = ""


selected_records = [
    record
    for record in records
    if record.get(
        "vehicle_id"
    ) == selected_vehicle_id
]


# =====================================
# 集計
# =====================================

today = date.today()

current_month = today.strftime(
    "%Y-%m"
)

current_month_records = [
    record
    for record in selected_records
    if get_record_month(record)
    == current_month
]

total_distance = sum(
    float(
        record.get(
            "distance",
            0
        )
    )
    for record in selected_records
)

total_fuel = sum(
    float(
        record.get(
            "fuel_amount",
            0
        )
    )
    for record in selected_records
)

total_cost = sum(
    int(
        record.get(
            "total_price",
            0
        )
    )
    for record in selected_records
)

monthly_cost = sum(
    int(
        record.get(
            "total_price",
            0
        )
    )
    for record in current_month_records
)

monthly_fuel = sum(
    float(
        record.get(
            "fuel_amount",
            0
        )
    )
    for record in current_month_records
)

monthly_distance = sum(
    float(
        record.get(
            "distance",
            0
        )
    )
    for record in current_month_records
)

average_fuel_economy = calculate_average(
    [
        record.get(
            "fuel_economy",
            0
        )
        for record in selected_records
    ]
)

average_unit_price = calculate_average(
    [
        record.get(
            "unit_price",
            0
        )
        for record in selected_records
    ]
)


# =====================================
# ダッシュボード
# =====================================

st.divider()

st.header("📊 ダッシュボード")

if not vehicles:
    st.info(
        "最初に「車両管理」タブから"
        "車両を登録してください。"
    )

else:
    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    with metric_col1:
        st.metric(
            "平均燃費",
            (
                f"{average_fuel_economy:.1f}"
                " km/L"
            )
        )

    with metric_col2:
        st.metric(
            "今月の給油代",
            format_price(
                monthly_cost
            )
        )

    with metric_col3:
        st.metric(
            "今月の給油量",
            (
                f"{monthly_fuel:.1f}"
                " L"
            )
        )

    with metric_col4:
        st.metric(
            "今月の走行距離",
            (
                f"{monthly_distance:.1f}"
                " km"
            )
        )

    metric_col5, metric_col6, metric_col7, metric_col8 = (
        st.columns(4)
    )

    with metric_col5:
        st.metric(
            "累計給油代",
            format_price(
                total_cost
            )
        )

    with metric_col6:
        st.metric(
            "累計給油量",
            (
                f"{total_fuel:.1f}"
                " L"
            )
        )

    with metric_col7:
        st.metric(
            "累計走行距離",
            (
                f"{total_distance:.1f}"
                " km"
            )
        )

    with metric_col8:
        st.metric(
            "平均ガソリン単価",
            (
                f"{average_unit_price:.1f}"
                " 円/L"
            )
        )


# =====================================
# 最新給油記録
# =====================================

st.divider()

st.header("⛽ 最新の給油記録")

if not selected_records:
    st.info(
        "この車両にはまだ給油記録がありません。"
    )

else:
    latest_record = sorted(
        selected_records,
        key=lambda record: (
            record.get(
                "fuel_date",
                ""
            ),
            record.get(
                "created_at",
                ""
            )
        ),
        reverse=True
    )[0]

    with st.container(border=True):
        latest_col1, latest_col2 = (
            st.columns([3, 1])
        )

        with latest_col1:
            st.subheader(
                f"⛽ "
                f"{latest_record.get('fuel_date', '')}"
            )

            station = latest_record.get(
                "station",
                ""
            )

            if station:
                st.write(
                    f"給油所：**{station}**"
                )

            st.caption(
                f"{latest_record.get('fuel_type', '')} "
                f"／ "
                f"{latest_record.get('fill_type', '')}"
            )

        with latest_col2:
            st.metric(
                "今回の燃費",
                (
                    f"{latest_record.get('fuel_economy', 0):.1f}"
                    " km/L"
                )
            )

        latest_detail_col1, latest_detail_col2, latest_detail_col3 = (
            st.columns(3)
        )

        with latest_detail_col1:
            st.metric(
                "走行距離",
                (
                    f"{latest_record.get('distance', 0):.1f}"
                    " km"
                )
            )

        with latest_detail_col2:
            st.metric(
                "給油量",
                (
                    f"{latest_record.get('fuel_amount', 0):.1f}"
                    " L"
                )
            )

        with latest_detail_col3:
            st.metric(
                "支払金額",
                format_price(
                    latest_record.get(
                        "total_price",
                        0
                    )
                )
            )

        st.write(
            f"ガソリン単価："
            f"**{latest_record.get('unit_price', 0):.1f}円/L**"
        )

        memo = latest_record.get(
            "memo",
            ""
        )

        if memo:
            st.write(
                f"📝 {memo}"
            )


# =====================================
# タブ
# =====================================

st.divider()

vehicle_tab, register_tab, graph_tab, history_tab = (
    st.tabs(
        [
            "🚘 車両管理",
            "⛽ 給油を記録",
            "📈 グラフ",
            "📋 給油履歴"
        ]
    )
)


# =====================================
# 車両管理タブ
# =====================================

with vehicle_tab:
    st.header("🚘 車両を登録")

    with st.form(
        "vehicle_form",
        clear_on_submit=True
    ):
        vehicle_col1, vehicle_col2 = (
            st.columns(2)
        )

        with vehicle_col1:
            vehicle_name = st.text_input(
                "車両名",
                placeholder=(
                    "例：家族用ミニバン"
                )
            )

            vehicle_type = st.selectbox(
                "車両タイプ",
                [
                    "普通車",
                    "軽自動車",
                    "ミニバン",
                    "SUV",
                    "スポーツカー",
                    "バイク",
                    "その他"
                ]
            )

        with vehicle_col2:
            vehicle_fuel_type = (
                st.selectbox(
                    "燃料タイプ",
                    [
                        "レギュラー",
                        "ハイオク",
                        "軽油",
                        "電気",
                        "その他"
                    ]
                )
            )

            vehicle_memo = st.text_area(
                "メモ",
                placeholder=(
                    "車種、年式、ナンバーなど"
                )
            )

        vehicle_submit = (
            st.form_submit_button(
                "🚘 車両を登録",
                use_container_width=True
            )
        )

        if vehicle_submit:
            cleaned_vehicle_name = (
                vehicle_name.strip()
            )

            duplicate_exists = any(
                vehicle.get(
                    "name",
                    ""
                ).lower()
                == cleaned_vehicle_name.lower()
                for vehicle in vehicles
            )

            if not cleaned_vehicle_name:
                st.error(
                    "車両名を入力してください。"
                )

            elif duplicate_exists:
                st.warning(
                    "同じ名前の車両が"
                    "すでに登録されています。"
                )

            else:
                add_vehicle(
                    data=data,
                    vehicle_name=(
                        cleaned_vehicle_name
                    ),
                    vehicle_type=vehicle_type,
                    fuel_type=(
                        vehicle_fuel_type
                    ),
                    memo=(
                        vehicle_memo.strip()
                    )
                )

                st.success(
                    f"「{cleaned_vehicle_name}」を"
                    "登録しました！"
                )

                st.rerun()

    st.divider()

    st.header("🚗 登録済み車両")

    if not vehicles:
        st.info(
            "登録済みの車両はありません。"
        )

    for vehicle in vehicles:
        vehicle_id = vehicle.get(
            "id",
            ""
        )

        vehicle_name_display = vehicle.get(
            "name",
            "名称未設定"
        )

        vehicle_records = [
            record
            for record in records
            if record.get(
                "vehicle_id"
            ) == vehicle_id
        ]

        vehicle_total_cost = sum(
            int(
                record.get(
                    "total_price",
                    0
                )
            )
            for record in vehicle_records
        )

        vehicle_average_fuel = calculate_average(
            [
                record.get(
                    "fuel_economy",
                    0
                )
                for record in vehicle_records
            ]
        )

        with st.container(border=True):
            vehicle_info_col, vehicle_metric_col = (
                st.columns([3, 1])
            )

            with vehicle_info_col:
                st.subheader(
                    f"🚗 {vehicle_name_display}"
                )

                st.caption(
                    f"{vehicle.get('vehicle_type', '')} "
                    f"／ "
                    f"{vehicle.get('fuel_type', '')}"
                )

            with vehicle_metric_col:
                st.metric(
                    "平均燃費",
                    (
                        f"{vehicle_average_fuel:.1f}"
                        " km/L"
                    )
                )

            vehicle_stat_col1, vehicle_stat_col2 = (
                st.columns(2)
            )

            with vehicle_stat_col1:
                st.metric(
                    "給油回数",
                    f"{len(vehicle_records)}回"
                )

            with vehicle_stat_col2:
                st.metric(
                    "累計給油代",
                    format_price(
                        vehicle_total_cost
                    )
                )

            vehicle_memo_display = (
                vehicle.get(
                    "memo",
                    ""
                )
            )

            if vehicle_memo_display:
                st.write(
                    f"📝 {vehicle_memo_display}"
                )

            with st.expander(
                "✏️ 車両情報を編集"
            ):
                edit_vehicle_name = (
                    st.text_input(
                        "車両名",
                        value=(
                            vehicle_name_display
                        ),
                        key=(
                            f"edit_vehicle_name_"
                            f"{vehicle_id}"
                        )
                    )
                )

                vehicle_type_options = [
                    "普通車",
                    "軽自動車",
                    "ミニバン",
                    "SUV",
                    "スポーツカー",
                    "バイク",
                    "その他"
                ]

                current_type = vehicle.get(
                    "vehicle_type",
                    "普通車"
                )

                type_index = (
                    vehicle_type_options.index(
                        current_type
                    )
                    if current_type
                    in vehicle_type_options
                    else 0
                )

                edit_vehicle_type = (
                    st.selectbox(
                        "車両タイプ",
                        vehicle_type_options,
                        index=type_index,
                        key=(
                            f"edit_vehicle_type_"
                            f"{vehicle_id}"
                        )
                    )
                )

                fuel_type_options = [
                    "レギュラー",
                    "ハイオク",
                    "軽油",
                    "電気",
                    "その他"
                ]

                current_fuel_type = vehicle.get(
                    "fuel_type",
                    "レギュラー"
                )

                fuel_type_index = (
                    fuel_type_options.index(
                        current_fuel_type
                    )
                    if current_fuel_type
                    in fuel_type_options
                    else 0
                )

                edit_fuel_type = (
                    st.selectbox(
                        "燃料タイプ",
                        fuel_type_options,
                        index=fuel_type_index,
                        key=(
                            f"edit_fuel_type_"
                            f"{vehicle_id}"
                        )
                    )
                )

                edit_vehicle_memo = (
                    st.text_area(
                        "メモ",
                        value=vehicle.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_vehicle_memo_"
                            f"{vehicle_id}"
                        )
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_vehicle_"
                        f"{vehicle_id}"
                    ),
                    use_container_width=True
                ):
                    cleaned_edit_name = (
                        edit_vehicle_name.strip()
                    )

                    if not cleaned_edit_name:
                        st.error(
                            "車両名を入力してください。"
                        )

                    else:
                        update_vehicle(
                            data=data,
                            vehicle_id=vehicle_id,
                            vehicle_name=(
                                cleaned_edit_name
                            ),
                            vehicle_type=(
                                edit_vehicle_type
                            ),
                            fuel_type=(
                                edit_fuel_type
                            ),
                            memo=(
                                edit_vehicle_memo.strip()
                            )
                        )

                        st.success(
                            "車両情報を更新しました！"
                        )

                        st.rerun()

            with st.expander(
                "🗑️ この車両を削除"
            ):
                st.warning(
                    "この車両に登録された"
                    "すべての給油記録も削除されます。"
                )

                confirm_vehicle_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_vehicle_"
                            f"{vehicle_id}"
                        )
                    )
                )

                if st.button(
                    "車両を削除",
                    key=(
                        f"delete_vehicle_"
                        f"{vehicle_id}"
                    ),
                    disabled=(
                        not confirm_vehicle_delete
                    ),
                    use_container_width=True
                ):
                    delete_vehicle(
                        data,
                        vehicle_id
                    )

                    st.rerun()


# =====================================
# 給油登録タブ
# =====================================

with register_tab:
    st.header("⛽ 給油記録を追加")

    if not vehicles:
        st.info(
            "先に「車両管理」タブから"
            "車両を登録してください。"
        )

    else:
        register_vehicle_options = {
            vehicle.get(
                "name",
                "名称未設定"
            ): vehicle.get(
                "id",
                ""
            )
            for vehicle in vehicles
        }

        with st.form(
            "fuel_record_form",
            clear_on_submit=True
        ):
            fuel_col1, fuel_col2 = (
                st.columns(2)
            )

            with fuel_col1:
                record_vehicle_name = (
                    st.selectbox(
                        "車両",
                        list(
                            register_vehicle_options.keys()
                        )
                    )
                )

                fuel_date = st.date_input(
                    "給油日",
                    value=date.today()
                )

                distance = st.number_input(
                    "前回給油からの走行距離（km）",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    format="%.1f"
                )

                odometer = st.number_input(
                    "現在の総走行距離（km）",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    format="%.1f"
                )

                fuel_amount = st.number_input(
                    "給油量（L）",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    format="%.2f"
                )

            with fuel_col2:
                total_price_input = (
                    st.number_input(
                        "支払金額（円）",
                        min_value=0,
                        value=0,
                        step=100
                    )
                )

                selected_vehicle = (
                    get_vehicle_by_id(
                        data,
                        register_vehicle_options[
                            record_vehicle_name
                        ]
                    )
                )

                default_fuel_type = (
                    selected_vehicle.get(
                        "fuel_type",
                        "レギュラー"
                    )
                    if selected_vehicle
                    else "レギュラー"
                )

                fuel_types = [
                    "レギュラー",
                    "ハイオク",
                    "軽油",
                    "電気",
                    "その他"
                ]

                fuel_index = (
                    fuel_types.index(
                        default_fuel_type
                    )
                    if default_fuel_type
                    in fuel_types
                    else 0
                )

                record_fuel_type = (
                    st.selectbox(
                        "燃料タイプ",
                        fuel_types,
                        index=fuel_index
                    )
                )

                fill_type = st.selectbox(
                    "給油方式",
                    [
                        "満タン",
                        "指定量",
                        "指定金額",
                        "その他"
                    ]
                )

                station = st.text_input(
                    "給油所",
                    placeholder=(
                        "例：○○サービスステーション"
                    )
                )

                record_memo = st.text_area(
                    "メモ",
                    placeholder=(
                        "高速道路を多く走った、"
                        "エアコンを多く使ったなど"
                    )
                )

            if (
                fuel_amount > 0
                and total_price_input > 0
            ):
                preview_unit_price = (
                    calculate_unit_price(
                        total_price_input,
                        fuel_amount
                    )
                )

                st.info(
                    f"ガソリン単価："
                    f"{preview_unit_price:.1f}円/L"
                )

            if (
                distance > 0
                and fuel_amount > 0
            ):
                preview_fuel_economy = (
                    calculate_fuel_economy(
                        distance,
                        fuel_amount
                    )
                )

                st.success(
                    f"今回の燃費："
                    f"{preview_fuel_economy:.2f}km/L"
                )

            fuel_submit = (
                st.form_submit_button(
                    "⛽ 給油記録を保存",
                    use_container_width=True
                )
            )

            if fuel_submit:
                if fuel_amount <= 0:
                    st.error(
                        "給油量を入力してください。"
                    )

                elif total_price_input <= 0:
                    st.error(
                        "支払金額を入力してください。"
                    )

                elif (
                    fill_type == "満タン"
                    and distance <= 0
                ):
                    st.error(
                        "満タン法で燃費を計算するため、"
                        "走行距離を入力してください。"
                    )

                else:
                    add_fuel_record(
                        data=data,
                        vehicle_id=(
                            register_vehicle_options[
                                record_vehicle_name
                            ]
                        ),
                        fuel_date=fuel_date,
                        distance=distance,
                        odometer=odometer,
                        fuel_amount=fuel_amount,
                        total_price=(
                            total_price_input
                        ),
                        fuel_type=(
                            record_fuel_type
                        ),
                        fill_type=fill_type,
                        station=station.strip(),
                        memo=record_memo.strip()
                    )

                    st.success(
                        "給油記録を保存しました！"
                    )

                    st.rerun()


# =====================================
# グラフタブ
# =====================================

with graph_tab:
    st.header("📈 燃費・給油代の推移")

    if not selected_records:
        st.info(
            "グラフを表示するための"
            "給油記録がありません。"
        )

    else:
        sorted_records = sorted(
            selected_records,
            key=lambda record: record.get(
                "fuel_date",
                ""
            )
        )

        graph_rows = []

        for record in sorted_records:
            graph_rows.append(
                {
                    "給油日": pd.to_datetime(
                        record.get(
                            "fuel_date",
                            ""
                        )
                    ),
                    "燃費": float(
                        record.get(
                            "fuel_economy",
                            0
                        )
                    ),
                    "ガソリン単価": float(
                        record.get(
                            "unit_price",
                            0
                        )
                    ),
                    "給油代": int(
                        record.get(
                            "total_price",
                            0
                        )
                    ),
                    "走行距離": float(
                        record.get(
                            "distance",
                            0
                        )
                    )
                }
            )

        graph_df = pd.DataFrame(
            graph_rows
        )

        st.subheader("🚗 燃費の推移")

        st.line_chart(
            graph_df.set_index(
                "給油日"
            )[["燃費"]]
        )

        st.subheader(
            "⛽ ガソリン単価の推移"
        )

        st.line_chart(
            graph_df.set_index(
                "給油日"
            )[["ガソリン単価"]]
        )

        st.subheader(
            "💰 月ごとの給油代"
        )

        monthly_rows = []

        for record in selected_records:
            month = get_record_month(
                record
            )

            monthly_rows.append(
                {
                    "年月": month,
                    "給油代": int(
                        record.get(
                            "total_price",
                            0
                        )
                    ),
                    "給油量": float(
                        record.get(
                            "fuel_amount",
                            0
                        )
                    ),
                    "走行距離": float(
                        record.get(
                            "distance",
                            0
                        )
                    )
                }
            )

        monthly_df = pd.DataFrame(
            monthly_rows
        )

        monthly_summary = (
            monthly_df.groupby(
                "年月",
                as_index=False
            ).sum()
        )

        monthly_summary = (
            monthly_summary.sort_values(
                "年月"
            )
        )

        st.bar_chart(
            monthly_summary.set_index(
                "年月"
            )[["給油代"]]
        )

        st.subheader(
            "🛣️ 月ごとの走行距離"
        )

        st.bar_chart(
            monthly_summary.set_index(
                "年月"
            )[["走行距離"]]
        )

        st.subheader(
            "📊 月別集計表"
        )

        display_monthly_df = (
            monthly_summary.copy()
        )

        display_monthly_df[
            "給油代"
        ] = display_monthly_df[
            "給油代"
        ].map(
            lambda value: format_price(
                value
            )
        )

        display_monthly_df[
            "給油量"
        ] = display_monthly_df[
            "給油量"
        ].map(
            lambda value: (
                f"{value:.1f} L"
            )
        )

        display_monthly_df[
            "走行距離"
        ] = display_monthly_df[
            "走行距離"
        ].map(
            lambda value: (
                f"{value:.1f} km"
            )
        )

        st.dataframe(
            display_monthly_df,
            use_container_width=True,
            hide_index=True
        )


# =====================================
# 履歴タブ
# =====================================

with history_tab:
    st.header("📋 給油履歴")

    if not selected_records:
        st.info(
            "給油履歴はまだありません。"
        )

    else:
        history_filter_col1, history_filter_col2 = (
            st.columns(2)
        )

        with history_filter_col1:
            history_search = (
                st.text_input(
                    "🔍 検索",
                    placeholder=(
                        "給油所やメモを検索"
                    )
                )
            )

        with history_filter_col2:
            history_fuel_type = (
                st.selectbox(
                    "燃料タイプ",
                    [
                        "すべて",
                        "レギュラー",
                        "ハイオク",
                        "軽油",
                        "電気",
                        "その他"
                    ],
                    key="history_fuel_type"
                )
            )

        sort_order = st.selectbox(
            "並び順",
            [
                "新しい順",
                "古い順",
                "燃費が良い順",
                "給油代が高い順"
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
                in record.get(
                    "station",
                    ""
                ).lower()
                or keyword
                in record.get(
                    "memo",
                    ""
                ).lower()
            ]

        if history_fuel_type != "すべて":
            filtered_records = [
                record
                for record in filtered_records
                if record.get(
                    "fuel_type"
                ) == history_fuel_type
            ]

        if sort_order == "新しい順":
            filtered_records = sorted(
                filtered_records,
                key=lambda record: (
                    record.get(
                        "fuel_date",
                        ""
                    ),
                    record.get(
                        "created_at",
                        ""
                    )
                ),
                reverse=True
            )

        elif sort_order == "古い順":
            filtered_records = sorted(
                filtered_records,
                key=lambda record: (
                    record.get(
                        "fuel_date",
                        ""
                    ),
                    record.get(
                        "created_at",
                        ""
                    )
                )
            )

        elif sort_order == "燃費が良い順":
            filtered_records = sorted(
                filtered_records,
                key=lambda record: float(
                    record.get(
                        "fuel_economy",
                        0
                    )
                ),
                reverse=True
            )

        else:
            filtered_records = sorted(
                filtered_records,
                key=lambda record: int(
                    record.get(
                        "total_price",
                        0
                    )
                ),
                reverse=True
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

            record_date = parse_date(
                record.get(
                    "fuel_date",
                    ""
                )
            )

            with st.container(border=True):
                history_col1, history_col2 = (
                    st.columns([3, 1])
                )

                with history_col1:
                    st.subheader(
                        f"⛽ "
                        f"{record_date.strftime('%Y年%m月%d日')}"
                    )

                    station_display = (
                        record.get(
                            "station",
                            ""
                        )
                    )

                    if station_display:
                        st.caption(
                            station_display
                        )

                    else:
                        st.caption(
                            "給油所未設定"
                        )

                with history_col2:
                    st.metric(
                        "燃費",
                        (
                            f"{record.get('fuel_economy', 0):.1f}"
                            " km/L"
                        )
                    )

                record_metric_col1, record_metric_col2, record_metric_col3, record_metric_col4 = (
                    st.columns(4)
                )

                with record_metric_col1:
                    st.metric(
                        "走行距離",
                        (
                            f"{record.get('distance', 0):.1f}"
                            " km"
                        )
                    )

                with record_metric_col2:
                    st.metric(
                        "給油量",
                        (
                            f"{record.get('fuel_amount', 0):.1f}"
                            " L"
                        )
                    )

                with record_metric_col3:
                    st.metric(
                        "給油代",
                        format_price(
                            record.get(
                                "total_price",
                                0
                            )
                        )
                    )

                with record_metric_col4:
                    st.metric(
                        "単価",
                        (
                            f"{record.get('unit_price', 0):.1f}"
                            " 円/L"
                        )
                    )

                st.caption(
                    f"{record.get('fuel_type', '')} "
                    f"／ "
                    f"{record.get('fill_type', '')}"
                )

                if record.get(
                    "odometer",
                    0
                ) > 0:
                    st.write(
                        f"総走行距離："
                        f"{record.get('odometer', 0):,.1f}km"
                    )

                record_memo_display = (
                    record.get(
                        "memo",
                        ""
                    )
                )

                if record_memo_display:
                    st.write(
                        f"📝 {record_memo_display}"
                    )

                with st.expander(
                    "✏️ この記録を編集"
                ):
                    edit_col1, edit_col2 = (
                        st.columns(2)
                    )

                    with edit_col1:
                        edit_fuel_date = (
                            st.date_input(
                                "給油日",
                                value=record_date,
                                key=(
                                    f"edit_date_"
                                    f"{record_id}"
                                )
                            )
                        )

                        edit_distance = (
                            st.number_input(
                                "走行距離（km）",
                                min_value=0.0,
                                value=float(
                                    record.get(
                                        "distance",
                                        0
                                    )
                                ),
                                step=1.0,
                                key=(
                                    f"edit_distance_"
                                    f"{record_id}"
                                )
                            )
                        )

                        edit_odometer = (
                            st.number_input(
                                "総走行距離（km）",
                                min_value=0.0,
                                value=float(
                                    record.get(
                                        "odometer",
                                        0
                                    )
                                ),
                                step=1.0,
                                key=(
                                    f"edit_odometer_"
                                    f"{record_id}"
                                )
                            )
                        )

                        edit_fuel_amount = (
                            st.number_input(
                                "給油量（L）",
                                min_value=0.0,
                                value=float(
                                    record.get(
                                        "fuel_amount",
                                        0
                                    )
                                ),
                                step=0.1,
                                key=(
                                    f"edit_fuel_amount_"
                                    f"{record_id}"
                                )
                            )
                        )

                    with edit_col2:
                        edit_total_price = (
                            st.number_input(
                                "支払金額（円）",
                                min_value=0,
                                value=int(
                                    record.get(
                                        "total_price",
                                        0
                                    )
                                ),
                                step=100,
                                key=(
                                    f"edit_total_price_"
                                    f"{record_id}"
                                )
                            )
                        )

                        fuel_options = [
                            "レギュラー",
                            "ハイオク",
                            "軽油",
                            "電気",
                            "その他"
                        ]

                        current_fuel = (
                            record.get(
                                "fuel_type",
                                "レギュラー"
                            )
                        )

                        fuel_option_index = (
                            fuel_options.index(
                                current_fuel
                            )
                            if current_fuel
                            in fuel_options
                            else 0
                        )

                        edit_record_fuel_type = (
                            st.selectbox(
                                "燃料タイプ",
                                fuel_options,
                                index=(
                                    fuel_option_index
                                ),
                                key=(
                                    f"edit_fuel_type_"
                                    f"{record_id}"
                                )
                            )
                        )

                        fill_options = [
                            "満タン",
                            "指定量",
                            "指定金額",
                            "その他"
                        ]

                        current_fill = (
                            record.get(
                                "fill_type",
                                "満タン"
                            )
                        )

                        fill_index = (
                            fill_options.index(
                                current_fill
                            )
                            if current_fill
                            in fill_options
                            else 0
                        )

                        edit_fill_type = (
                            st.selectbox(
                                "給油方式",
                                fill_options,
                                index=fill_index,
                                key=(
                                    f"edit_fill_type_"
                                    f"{record_id}"
                                )
                            )
                        )

                        edit_station = (
                            st.text_input(
                                "給油所",
                                value=record.get(
                                    "station",
                                    ""
                                ),
                                key=(
                                    f"edit_station_"
                                    f"{record_id}"
                                )
                            )
                        )

                        edit_memo = (
                            st.text_area(
                                "メモ",
                                value=record.get(
                                    "memo",
                                    ""
                                ),
                                key=(
                                    f"edit_memo_"
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
                        if edit_fuel_amount <= 0:
                            st.error(
                                "給油量を入力してください。"
                            )

                        elif edit_total_price <= 0:
                            st.error(
                                "支払金額を入力してください。"
                            )

                        else:
                            update_fuel_record(
                                data=data,
                                record_id=record_id,
                                fuel_date=(
                                    edit_fuel_date
                                ),
                                distance=(
                                    edit_distance
                                ),
                                odometer=(
                                    edit_odometer
                                ),
                                fuel_amount=(
                                    edit_fuel_amount
                                ),
                                total_price=(
                                    edit_total_price
                                ),
                                fuel_type=(
                                    edit_record_fuel_type
                                ),
                                fill_type=(
                                    edit_fill_type
                                ),
                                station=(
                                    edit_station.strip()
                                ),
                                memo=(
                                    edit_memo.strip()
                                )
                            )

                            st.success(
                                "給油記録を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ この記録を削除"
                ):
                    st.warning(
                        "削除した記録は"
                        "元に戻せません。"
                    )

                    confirm_record_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_record_"
                                f"{record_id}"
                            )
                        )
                    )

                    if st.button(
                        "給油記録を削除",
                        key=(
                            f"delete_record_"
                            f"{record_id}"
                        ),
                        disabled=(
                            not confirm_record_delete
                        ),
                        use_container_width=True
                    ):
                        delete_fuel_record(
                            data,
                            record_id
                        )

                        st.rerun()


st.divider()

st.success(
    "給油を記録して、"
    "愛車の燃費と維持費を"
    "無理なく見える化しよう！🚗"
)
