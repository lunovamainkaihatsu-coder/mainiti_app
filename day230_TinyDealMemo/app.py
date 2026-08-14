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
    page_title="ちょい得メモ",
    page_icon="💡",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "deal_data.json",
)

DEAL_TYPES = [
    "クーポン",
    "ポイント還元",
    "セール",
    "無料キャンペーン",
    "キャッシュバック",
    "送料無料",
    "誕生日特典",
    "会員特典",
    "期間限定ポイント",
    "その他",
]

STATUS_OPTIONS = [
    "未使用",
    "利用済み",
    "見送り",
]

BENEFIT_TYPES = [
    "金額",
    "還元率",
    "割引率",
    "無料",
    "その他",
]

PRIORITIES = [
    "高",
    "普通",
    "低",
]

PRIORITY_ORDER = {
    "高": 0,
    "普通": 1,
    "低": 2,
}

PRIORITY_ICONS = {
    "高": "🔥",
    "普通": "🟡",
    "低": "🟢",
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
        "deals": []
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
        "deals",
        [],
    )

    for deal in data["deals"]:
        deal.setdefault(
            "id",
            create_id(),
        )

        deal.setdefault(
            "title",
            "",
        )

        deal.setdefault(
            "deal_type",
            "クーポン",
        )

        deal.setdefault(
            "shop",
            "",
        )

        deal.setdefault(
            "start_date",
            "",
        )

        deal.setdefault(
            "expiry_date",
            "",
        )

        deal.setdefault(
            "benefit_type",
            "金額",
        )

        deal.setdefault(
            "benefit_value",
            0.0,
        )

        deal.setdefault(
            "estimated_value",
            0,
        )

        deal.setdefault(
            "minimum_spend",
            0,
        )

        deal.setdefault(
            "conditions",
            "",
        )

        deal.setdefault(
            "target",
            "",
        )

        deal.setdefault(
            "priority",
            "普通",
        )

        deal.setdefault(
            "status",
            "未使用",
        )

        deal.setdefault(
            "used_date",
            "",
        )

        deal.setdefault(
            "actual_saving",
            0,
        )

        deal.setdefault(
            "memo",
            "",
        )

        deal.setdefault(
            "favorite",
            False,
        )

        deal.setdefault(
            "created_at",
            "",
        )

        deal.setdefault(
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


def get_deal_by_id(
    data,
    deal_id,
):
    for deal in data["deals"]:
        if deal.get(
            "id"
        ) == deal_id:
            return deal

    return None


def days_until_expiry(
    deal,
):
    expiry_date = parse_date(
        deal.get(
            "expiry_date",
            "",
        )
    )

    if not expiry_date:
        return None

    return (
        expiry_date
        - date.today()
    ).days


def deal_status_label(
    deal,
):
    if deal.get(
        "status"
    ) == "利用済み":
        return "利用済み"

    if deal.get(
        "status"
    ) == "見送り":
        return "見送り"

    days = days_until_expiry(
        deal
    )

    if days is None:
        return "期限なし"

    if days < 0:
        return "期限切れ"

    if days == 0:
        return "今日まで"

    if days <= 3:
        return "3日以内"

    if days <= 7:
        return "7日以内"

    return "まだ余裕"


def deal_status_icon(
    label,
):
    icons = {
        "利用済み": "✅",
        "見送り": "➖",
        "期限なし": "🔵",
        "期限切れ": "⚫",
        "今日まで": "🔴",
        "3日以内": "🟠",
        "7日以内": "🟡",
        "まだ余裕": "🟢",
    }

    return icons.get(
        label,
        "🔵",
    )


def usable_deals(
    deals,
):
    return [
        deal
        for deal in deals
        if (
            deal.get(
                "status"
            )
            == "未使用"
            and deal_status_label(
                deal
            )
            != "期限切れ"
        )
    ]


def expired_deals(
    deals,
):
    return [
        deal
        for deal in deals
        if (
            deal.get(
                "status"
            )
            == "未使用"
            and deal_status_label(
                deal
            )
            == "期限切れ"
        )
    ]


def total_actual_saving(
    deals,
):
    return sum(
        int(
            deal.get(
                "actual_saving",
                0,
            )
        )
        for deal in deals
        if deal.get(
            "status"
        ) == "利用済み"
    )


def usage_rate(
    deals,
):
    completed = [
        deal
        for deal in deals
        if deal.get(
            "status"
        )
        in [
            "利用済み",
            "見送り",
        ]
        or deal_status_label(
            deal
        )
        == "期限切れ"
    ]

    if not completed:
        return 0

    used = [
        deal
        for deal in completed
        if deal.get(
            "status"
        ) == "利用済み"
    ]

    return (
        len(used)
        / len(completed)
        * 100
    )


def benefit_text(
    deal,
):
    benefit_type = deal.get(
        "benefit_type",
        "金額",
    )

    benefit_value = float(
        deal.get(
            "benefit_value",
            0,
        )
    )

    if benefit_type == "金額":
        return (
            f"{benefit_value:,.0f}円"
        )

    if benefit_type in [
        "還元率",
        "割引率",
    ]:
        return (
            f"{benefit_value:g}%"
        )

    if benefit_type == "無料":
        return "無料"

    return (
        f"{benefit_value:g}"
        if benefit_value > 0
        else "条件参照"
    )


# =========================================================
# データ操作
# =========================================================

def add_deal(
    data,
    values,
):
    deal = {
        "id": create_id(),
        "title": values["title"],
        "deal_type": (
            values["deal_type"]
        ),
        "shop": values["shop"],
        "start_date": (
            values["start_date"]
        ),
        "expiry_date": (
            values["expiry_date"]
        ),
        "benefit_type": (
            values["benefit_type"]
        ),
        "benefit_value": float(
            values["benefit_value"]
        ),
        "estimated_value": int(
            values["estimated_value"]
        ),
        "minimum_spend": int(
            values["minimum_spend"]
        ),
        "conditions": (
            values["conditions"]
        ),
        "target": values["target"],
        "priority": (
            values["priority"]
        ),
        "status": "未使用",
        "used_date": "",
        "actual_saving": 0,
        "memo": values["memo"],
        "favorite": False,
        "created_at": now_text(),
        "updated_at": "",
    }

    data["deals"].append(
        deal
    )

    save_data(data)


def update_deal(
    data,
    deal_id,
    values,
):
    deal = get_deal_by_id(
        data,
        deal_id
    )

    if not deal:
        return

    for key, value in values.items():
        deal[key] = value

    deal["benefit_value"] = float(
        deal.get(
            "benefit_value",
            0,
        )
    )

    deal["estimated_value"] = int(
        deal.get(
            "estimated_value",
            0,
        )
    )

    deal["minimum_spend"] = int(
        deal.get(
            "minimum_spend",
            0,
        )
    )

    deal["actual_saving"] = int(
        deal.get(
            "actual_saving",
            0,
        )
    )

    deal["updated_at"] = (
        now_text()
    )

    save_data(data)


def mark_deal_used(
    data,
    deal_id,
    used_date,
    actual_saving,
    memo,
):
    deal = get_deal_by_id(
        data,
        deal_id
    )

    if not deal:
        return

    deal["status"] = (
        "利用済み"
    )

    deal["used_date"] = str(
        used_date
    )

    deal["actual_saving"] = int(
        actual_saving
    )

    if memo.strip():
        old_memo = deal.get(
            "memo",
            "",
        )

        if old_memo:
            deal["memo"] = (
                old_memo
                + "\n"
                + memo.strip()
            )

        else:
            deal["memo"] = (
                memo.strip()
            )

    deal["updated_at"] = (
        now_text()
    )

    save_data(data)


def toggle_favorite(
    data,
    deal_id,
):
    deal = get_deal_by_id(
        data,
        deal_id
    )

    if not deal:
        return

    deal["favorite"] = not bool(
        deal.get(
            "favorite",
            False,
        )
    )

    deal["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_deal(
    data,
    deal_id,
):
    data["deals"] = [
        deal
        for deal in data[
            "deals"
        ]
        if deal.get(
            "id"
        ) != deal_id
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
        background: rgba(255, 185, 50, 0.08);
        border: 1px solid rgba(255, 185, 50, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(255, 185, 50, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(255, 185, 50, 0.18),
                rgba(120, 190, 255, 0.11)
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

deals = data[
    "deals"
]

usable = usable_deals(
    deals
)

expired = expired_deals(
    deals
)

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
        <h1>💡 ちょい得メモ</h1>
        <p>
            クーポン・ポイント・キャンペーンを忘れず使って、
            小さなお得をしっかり残す
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

today_expiring = [
    deal
    for deal in usable
    if deal_status_label(
        deal
    )
    == "今日まで"
]

week_expiring = [
    deal
    for deal in usable
    if (
        days_until_expiry(
            deal
        )
        is not None
        and 0
        <= days_until_expiry(
            deal
        )
        <= 7
    )
]

monthly_used = [
    deal
    for deal in deals
    if (
        deal.get(
            "status"
        )
        == "利用済み"
        and deal.get(
            "used_date",
            "",
        ).startswith(
            current_month
        )
    )
]

monthly_saving = (
    total_actual_saving(
        monthly_used
    )
)

all_saving = (
    total_actual_saving(
        deals
    )
)

favorite_count = len(
    [
        deal
        for deal in deals
        if deal.get(
            "favorite",
            False,
        )
    ]
)


metric_row1 = st.columns(
    4
)

metric_row1[0].metric(
    "利用可能",
    f"{len(usable)}件"
)

metric_row1[1].metric(
    "今日まで",
    f"{len(today_expiring)}件"
)

metric_row1[2].metric(
    "7日以内",
    f"{len(week_expiring)}件"
)

metric_row1[3].metric(
    "期限切れ",
    f"{len(expired)}件"
)


metric_row2 = st.columns(
    4
)

metric_row2[0].metric(
    "今月使った",
    f"{len(monthly_used)}件"
)

metric_row2[1].metric(
    "今月のお得",
    f"{monthly_saving:,}円"
)

metric_row2[2].metric(
    "累計お得",
    f"{all_saving:,}円"
)

metric_row2[3].metric(
    "利用率",
    f"{usage_rate(deals):.1f}%"
)


# =========================================================
# 期限が近いお得
# =========================================================

urgent_deals = [
    deal
    for deal in usable
    if (
        days_until_expiry(
            deal
        )
        is not None
        and days_until_expiry(
            deal
        )
        <= 7
    )
]

urgent_deals.sort(
    key=lambda deal: (
        days_until_expiry(
            deal
        ),
        PRIORITY_ORDER.get(
            deal.get(
                "priority",
                "普通",
            ),
            99,
        ),
    )
)

st.divider()

st.header(
    "⏰ 期限が近いお得"
)

if not urgent_deals:
    st.success(
        "7日以内に期限が切れる特典はありません！"
    )

else:
    for deal in urgent_deals:
        deal_id = deal[
            "id"
        ]

        status_label = (
            deal_status_label(
                deal
            )
        )

        days = days_until_expiry(
            deal
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
                    f"{deal_status_icon(status_label)} "
                    f"{PRIORITY_ICONS.get(deal.get('priority', ''), '')} "
                    f"{deal.get('title', '')}"
                )

                st.caption(
                    f"{deal.get('deal_type', '')} ／ "
                    f"{deal.get('shop', '') or '店舗未設定'}"
                )

                st.write(
                    f"特典："
                    f"**{benefit_text(deal)}**"
                )

                if int(
                    deal.get(
                        "estimated_value",
                        0,
                    )
                ) > 0:
                    st.write(
                        f"想定お得額："
                        f"**{deal.get('estimated_value', 0):,}円**"
                    )

                if deal.get(
                    "conditions",
                    "",
                ):
                    st.info(
                        "利用条件\n\n"
                        + deal.get(
                            "conditions",
                            "",
                        )
                    )

            with column2:
                if days == 0:
                    st.metric(
                        "期限",
                        "今日まで"
                    )

                elif days is not None:
                    st.metric(
                        "期限",
                        f"あと{days}日"
                    )

                st.write(
                    format_date(
                        deal.get(
                            "expiry_date",
                            "",
                        )
                    )
                )

            with st.expander(
                "✅ 利用済みにする"
            ):
                used_date_input = (
                    st.date_input(
                        "利用日",
                        value=date.today(),
                        max_value=date.today(),
                        key=(
                            f"urgent_used_date_"
                            f"{deal_id}"
                        ),
                    )
                )

                actual_saving = (
                    st.number_input(
                        "実際に得した金額",
                        min_value=0,
                        max_value=100000000,
                        value=int(
                            deal.get(
                                "estimated_value",
                                0,
                            )
                        ),
                        step=10,
                        key=(
                            f"urgent_actual_saving_"
                            f"{deal_id}"
                        ),
                    )
                )

                used_memo = (
                    st.text_area(
                        "利用メモ",
                        placeholder=(
                            "例：日用品購入時に使用"
                        ),
                        key=(
                            f"urgent_used_memo_"
                            f"{deal_id}"
                        ),
                    )
                )

                if st.button(
                    "利用済みとして保存",
                    key=(
                        f"urgent_mark_used_"
                        f"{deal_id}"
                    ),
                    use_container_width=True,
                ):
                    mark_deal_used(
                        data,
                        deal_id,
                        used_date_input,
                        actual_saving,
                        used_memo,
                    )

                    st.success(
                        "お得を記録しました！"
                    )

                    st.balloons()
                    st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    used_tab,
    favorite_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ お得を登録",
        "🎫 お得一覧",
        "✅ 利用履歴",
        "⭐ お気に入り",
        "📈 お得分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 登録
# =========================================================

with add_tab:
    st.header(
        "➕ お得情報を登録"
    )

    with st.form(
        "add_deal_form",
        clear_on_submit=True,
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            title = st.text_input(
                "キャンペーン・特典名",
                placeholder=(
                    "例：ドラッグストア500円OFF"
                ),
            )

            deal_type = st.selectbox(
                "種類",
                DEAL_TYPES,
            )

            shop = st.text_input(
                "店舗・サービス",
                placeholder=(
                    "例：○○ドラッグ"
                ),
            )

            priority = st.selectbox(
                "優先度",
                PRIORITIES,
                index=1,
            )

        with column2:
            set_start_date = (
                st.checkbox(
                    "開始日を設定する"
                )
            )

            start_date_text = ""

            if set_start_date:
                start_date_text = str(
                    st.date_input(
                        "開始日",
                        value=date.today(),
                    )
                )

            set_expiry = st.checkbox(
                "期限を設定する",
                value=True,
            )

            expiry_date_text = ""

            if set_expiry:
                expiry_date_text = str(
                    st.date_input(
                        "利用期限",
                        value=date.today(),
                    )
                )

        benefit_column1, benefit_column2 = (
            st.columns(2)
        )

        with benefit_column1:
            benefit_type = st.selectbox(
                "特典タイプ",
                BENEFIT_TYPES,
            )

            if benefit_type == "無料":
                benefit_value = 0.0

                st.info(
                    "無料特典として登録します。"
                )

            else:
                benefit_value = (
                    st.number_input(
                        (
                            "特典値"
                            + (
                                "（円）"
                                if benefit_type
                                == "金額"
                                else "（%）"
                                if benefit_type
                                in [
                                    "還元率",
                                    "割引率",
                                ]
                                else ""
                            )
                        ),
                        min_value=0.0,
                        max_value=100000000.0,
                        value=500.0,
                        step=1.0,
                    )
                )

        with benefit_column2:
            estimated_value = (
                st.number_input(
                    "想定お得額（円）",
                    min_value=0,
                    max_value=100000000,
                    value=0,
                    step=100,
                    help=(
                        "還元率や送料無料などを、おおよその円換算で記録できます。"
                    ),
                )
            )

            minimum_spend = (
                st.number_input(
                    "最低利用金額",
                    min_value=0,
                    max_value=100000000,
                    value=0,
                    step=100,
                )
            )

        conditions = st.text_area(
            "利用条件",
            placeholder=(
                "例：3,000円以上購入、1人1回まで"
            ),
            height=100,
        )

        target = st.text_area(
            "対象商品・サービス",
            placeholder=(
                "例：日用品・食品"
            ),
            height=80,
        )

        memo = st.text_area(
            "メモ",
            placeholder=(
                "使いたい予定や注意点"
            ),
            height=80,
        )

        submitted = (
            st.form_submit_button(
                "💡 お得情報を保存",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.error(
                    "キャンペーン・特典名を入力してください。"
                )

            elif (
                start_date_text
                and expiry_date_text
                and parse_date(
                    expiry_date_text
                )
                < parse_date(
                    start_date_text
                )
            ):
                st.error(
                    "利用期限は開始日以降にしてください。"
                )

            else:
                add_deal(
                    data,
                    {
                        "title": (
                            title.strip()
                        ),
                        "deal_type": (
                            deal_type
                        ),
                        "shop": (
                            shop.strip()
                        ),
                        "start_date": (
                            start_date_text
                        ),
                        "expiry_date": (
                            expiry_date_text
                        ),
                        "benefit_type": (
                            benefit_type
                        ),
                        "benefit_value": (
                            benefit_value
                        ),
                        "estimated_value": (
                            estimated_value
                        ),
                        "minimum_spend": (
                            minimum_spend
                        ),
                        "conditions": (
                            conditions.strip()
                        ),
                        "target": (
                            target.strip()
                        ),
                        "priority": (
                            priority
                        ),
                        "memo": (
                            memo.strip()
                        ),
                    }
                )

                st.success(
                    "お得情報を登録しました！"
                )

                st.rerun()


# =========================================================
# 一覧
# =========================================================

with list_tab:
    st.header(
        "🎫 お得一覧"
    )

    if not deals:
        st.info(
            "お得情報はまだありません。"
        )

    else:
        filter_columns = (
            st.columns(3)
        )

        with filter_columns[0]:
            keyword = st.text_input(
                "🔍 検索",
                placeholder=(
                    "特典名・店舗・条件"
                ),
            )

        with filter_columns[1]:
            type_filter = (
                st.selectbox(
                    "種類",
                    [
                        "すべて"
                    ]
                    + DEAL_TYPES,
                )
            )

        with filter_columns[2]:
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて",
                        "未使用",
                        "利用済み",
                        "見送り",
                        "期限切れ",
                    ],
                )
            )

        priority_filter = (
            st.multiselect(
                "優先度",
                PRIORITIES,
                default=PRIORITIES,
            )
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "期限が近い順",
                "新しい順",
                "想定お得額が高い順",
                "優先度順",
            ],
        )

        filtered = list(
            deals
        )

        if keyword.strip():
            word = (
                keyword.strip().lower()
            )

            filtered = [
                deal
                for deal in filtered
                if (
                    word
                    in deal.get(
                        "title",
                        "",
                    ).lower()
                    or word
                    in deal.get(
                        "shop",
                        "",
                    ).lower()
                    or word
                    in deal.get(
                        "conditions",
                        "",
                    ).lower()
                    or word
                    in deal.get(
                        "target",
                        "",
                    ).lower()
                )
            ]

        if type_filter != "すべて":
            filtered = [
                deal
                for deal in filtered
                if deal.get(
                    "deal_type"
                )
                == type_filter
            ]

        if status_filter != "すべて":
            if status_filter == "期限切れ":
                filtered = [
                    deal
                    for deal in filtered
                    if deal_status_label(
                        deal
                    )
                    == "期限切れ"
                ]

            else:
                filtered = [
                    deal
                    for deal in filtered
                    if deal.get(
                        "status"
                    )
                    == status_filter
                ]

        filtered = [
            deal
            for deal in filtered
            if deal.get(
                "priority",
                "普通",
            )
            in priority_filter
        ]

        if sort_option == "期限が近い順":
            filtered.sort(
                key=lambda deal: (
                    days_until_expiry(
                        deal
                    )
                    if days_until_expiry(
                        deal
                    )
                    is not None
                    else 999999,
                    PRIORITY_ORDER.get(
                        deal.get(
                            "priority",
                            "普通",
                        ),
                        99,
                    ),
                )
            )

        elif sort_option == "新しい順":
            filtered.sort(
                key=lambda deal: (
                    deal.get(
                        "created_at",
                        "",
                    )
                ),
                reverse=True,
            )

        elif sort_option == "想定お得額が高い順":
            filtered.sort(
                key=lambda deal: int(
                    deal.get(
                        "estimated_value",
                        0,
                    )
                ),
                reverse=True,
            )

        else:
            filtered.sort(
                key=lambda deal: (
                    PRIORITY_ORDER.get(
                        deal.get(
                            "priority",
                            "普通",
                        ),
                        99,
                    )
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered)}件**"
        )

        for deal in filtered:
            deal_id = deal[
                "id"
            ]

            status_label = (
                deal_status_label(
                    deal
                )
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
                    favorite_icon = (
                        "⭐ "
                        if deal.get(
                            "favorite",
                            False,
                        )
                        else ""
                    )

                    st.markdown(
                        f"### "
                        f"{favorite_icon}"
                        f"{deal_status_icon(status_label)} "
                        f"{deal.get('title', '')}"
                    )

                    st.caption(
                        f"{deal.get('deal_type', '')} ／ "
                        f"{deal.get('shop', '') or '店舗未設定'}"
                    )

                with column2:
                    st.metric(
                        "状態",
                        status_label
                    )

                info_columns = st.columns(
                    4
                )

                info_columns[0].metric(
                    "特典",
                    benefit_text(
                        deal
                    )
                )

                info_columns[1].metric(
                    "想定お得額",
                    f"{deal.get('estimated_value', 0):,}円"
                )

                info_columns[2].metric(
                    "最低利用額",
                    f"{deal.get('minimum_spend', 0):,}円"
                )

                info_columns[3].metric(
                    "優先度",
                    deal.get(
                        "priority",
                        ""
                    )
                )

                if deal.get(
                    "expiry_date",
                    "",
                ):
                    st.write(
                        f"期限："
                        f"**{format_date(deal.get('expiry_date', ''))}**"
                    )

                if deal.get(
                    "conditions",
                    "",
                ):
                    st.info(
                        "利用条件\n\n"
                        + deal.get(
                            "conditions",
                            "",
                        )
                    )

                if deal.get(
                    "target",
                    "",
                ):
                    st.write(
                        f"対象："
                        f"{deal.get('target', '')}"
                    )

                if deal.get(
                    "memo",
                    "",
                ):
                    st.write(
                        deal.get(
                            "memo",
                            "",
                        )
                    )

                if deal.get(
                    "status"
                ) == "利用済み":
                    st.success(
                        f"✅ "
                        f"{format_date(deal.get('used_date', ''))} に利用\n\n"
                        f"実際のお得："
                        f"**{deal.get('actual_saving', 0):,}円**"
                    )

                action_columns = (
                    st.columns(2)
                )

                with action_columns[0]:
                    if st.button(
                        (
                            "⭐ お気に入り解除"
                            if deal.get(
                                "favorite",
                                False,
                            )
                            else "☆ お気に入り"
                        ),
                        key=(
                            f"favorite_"
                            f"{deal_id}"
                        ),
                        use_container_width=True,
                    ):
                        toggle_favorite(
                            data,
                            deal_id,
                        )

                        st.rerun()

                with action_columns[1]:
                    if (
                        deal.get(
                            "status"
                        )
                        == "未使用"
                    ):
                        if st.button(
                            "➖ 見送る",
                            key=(
                                f"skip_"
                                f"{deal_id}"
                            ),
                            use_container_width=True,
                        ):
                            update_deal(
                                data,
                                deal_id,
                                {
                                    "status": (
                                        "見送り"
                                    )
                                }
                            )

                            st.rerun()

                if (
                    deal.get(
                        "status"
                    )
                    == "未使用"
                ):
                    with st.expander(
                        "✅ 利用済みにする"
                    ):
                        used_date_input = (
                            st.date_input(
                                "利用日",
                                value=date.today(),
                                max_value=date.today(),
                                key=(
                                    f"used_date_"
                                    f"{deal_id}"
                                ),
                            )
                        )

                        actual_saving = (
                            st.number_input(
                                "実際に得した金額",
                                min_value=0,
                                max_value=100000000,
                                value=int(
                                    deal.get(
                                        "estimated_value",
                                        0,
                                    )
                                ),
                                key=(
                                    f"actual_saving_"
                                    f"{deal_id}"
                                ),
                            )
                        )

                        usage_memo = (
                            st.text_area(
                                "利用メモ",
                                key=(
                                    f"usage_memo_"
                                    f"{deal_id}"
                                ),
                            )
                        )

                        if st.button(
                            "利用済みとして保存",
                            key=(
                                f"mark_used_"
                                f"{deal_id}"
                            ),
                            use_container_width=True,
                        ):
                            mark_deal_used(
                                data,
                                deal_id,
                                used_date_input,
                                actual_saving,
                                usage_memo,
                            )

                            st.rerun()

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = st.text_input(
                        "特典名",
                        value=deal.get(
                            "title",
                            "",
                        ),
                        key=(
                            f"edit_title_"
                            f"{deal_id}"
                        ),
                    )

                    current_type = deal.get(
                        "deal_type",
                        "クーポン",
                    )

                    edit_type = st.selectbox(
                        "種類",
                        DEAL_TYPES,
                        index=(
                            DEAL_TYPES.index(
                                current_type
                            )
                            if current_type
                            in DEAL_TYPES
                            else 0
                        ),
                        key=(
                            f"edit_type_"
                            f"{deal_id}"
                        ),
                    )

                    edit_shop = st.text_input(
                        "店舗・サービス",
                        value=deal.get(
                            "shop",
                            "",
                        ),
                        key=(
                            f"edit_shop_"
                            f"{deal_id}"
                        ),
                    )

                    expiry_value = (
                        parse_date(
                            deal.get(
                                "expiry_date",
                                "",
                            )
                        )
                    )

                    edit_has_expiry = (
                        st.checkbox(
                            "期限を設定",
                            value=bool(
                                expiry_value
                            ),
                            key=(
                                f"edit_has_expiry_"
                                f"{deal_id}"
                            ),
                        )
                    )

                    edit_expiry = ""

                    if edit_has_expiry:
                        edit_expiry = str(
                            st.date_input(
                                "期限",
                                value=(
                                    expiry_value
                                    or date.today()
                                ),
                                key=(
                                    f"edit_expiry_"
                                    f"{deal_id}"
                                ),
                            )
                        )

                    current_benefit_type = (
                        deal.get(
                            "benefit_type",
                            "金額",
                        )
                    )

                    edit_benefit_type = (
                        st.selectbox(
                            "特典タイプ",
                            BENEFIT_TYPES,
                            index=(
                                BENEFIT_TYPES.index(
                                    current_benefit_type
                                )
                                if current_benefit_type
                                in BENEFIT_TYPES
                                else 0
                            ),
                            key=(
                                f"edit_benefit_type_"
                                f"{deal_id}"
                            ),
                        )
                    )

                    edit_benefit_value = (
                        st.number_input(
                            "特典値",
                            min_value=0.0,
                            max_value=100000000.0,
                            value=float(
                                deal.get(
                                    "benefit_value",
                                    0,
                                )
                            ),
                            key=(
                                f"edit_benefit_value_"
                                f"{deal_id}"
                            ),
                        )
                    )

                    edit_estimated = (
                        st.number_input(
                            "想定お得額",
                            min_value=0,
                            max_value=100000000,
                            value=int(
                                deal.get(
                                    "estimated_value",
                                    0,
                                )
                            ),
                            key=(
                                f"edit_estimated_"
                                f"{deal_id}"
                            ),
                        )
                    )

                    edit_minimum = (
                        st.number_input(
                            "最低利用金額",
                            min_value=0,
                            max_value=100000000,
                            value=int(
                                deal.get(
                                    "minimum_spend",
                                    0,
                                )
                            ),
                            key=(
                                f"edit_minimum_"
                                f"{deal_id}"
                            ),
                        )
                    )

                    current_priority = (
                        deal.get(
                            "priority",
                            "普通",
                        )
                    )

                    edit_priority = (
                        st.selectbox(
                            "優先度",
                            PRIORITIES,
                            index=(
                                PRIORITIES.index(
                                    current_priority
                                )
                                if current_priority
                                in PRIORITIES
                                else 1
                            ),
                            key=(
                                f"edit_priority_"
                                f"{deal_id}"
                            ),
                        )
                    )

                    edit_conditions = (
                        st.text_area(
                            "利用条件",
                            value=deal.get(
                                "conditions",
                                "",
                            ),
                            key=(
                                f"edit_conditions_"
                                f"{deal_id}"
                            ),
                        )
                    )

                    edit_target = st.text_area(
                        "対象",
                        value=deal.get(
                            "target",
                            "",
                        ),
                        key=(
                            f"edit_target_"
                            f"{deal_id}"
                        ),
                    )

                    edit_memo = st.text_area(
                        "メモ",
                        value=deal.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_memo_"
                            f"{deal_id}"
                        ),
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_deal_"
                            f"{deal_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_title.strip():
                            st.error(
                                "特典名を入力してください。"
                            )

                        else:
                            update_deal(
                                data,
                                deal_id,
                                {
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "deal_type": (
                                        edit_type
                                    ),
                                    "shop": (
                                        edit_shop.strip()
                                    ),
                                    "expiry_date": (
                                        edit_expiry
                                    ),
                                    "benefit_type": (
                                        edit_benefit_type
                                    ),
                                    "benefit_value": (
                                        edit_benefit_value
                                    ),
                                    "estimated_value": (
                                        edit_estimated
                                    ),
                                    "minimum_spend": (
                                        edit_minimum
                                    ),
                                    "priority": (
                                        edit_priority
                                    ),
                                    "conditions": (
                                        edit_conditions.strip()
                                    ),
                                    "target": (
                                        edit_target.strip()
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
                                f"{deal_id}"
                            ),
                        )
                    )

                    if st.button(
                        "この特典を削除",
                        key=(
                            f"delete_deal_"
                            f"{deal_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_deal(
                            data,
                            deal_id,
                        )

                        st.rerun()


# =========================================================
# 利用履歴
# =========================================================

with used_tab:
    st.header(
        "✅ 利用したお得"
    )

    used_deals = [
        deal
        for deal in deals
        if deal.get(
            "status"
        ) == "利用済み"
    ]

    if not used_deals:
        st.info(
            "利用履歴はまだありません。"
        )

    else:
        used_deals.sort(
            key=lambda deal: (
                deal.get(
                    "used_date",
                    "",
                )
            ),
            reverse=True,
        )

        for deal in used_deals:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### ✅ "
                    f"{deal.get('title', '')}"
                )

                st.caption(
                    f"{format_date(deal.get('used_date', ''))} ／ "
                    f"{deal.get('deal_type', '')} ／ "
                    f"{deal.get('shop', '') or '店舗未設定'}"
                )

                columns = st.columns(
                    3
                )

                columns[0].metric(
                    "実際のお得",
                    f"{deal.get('actual_saving', 0):,}円"
                )

                columns[1].metric(
                    "想定お得",
                    f"{deal.get('estimated_value', 0):,}円"
                )

                difference = (
                    int(
                        deal.get(
                            "actual_saving",
                            0,
                        )
                    )
                    - int(
                        deal.get(
                            "estimated_value",
                            0,
                        )
                    )
                )

                columns[2].metric(
                    "想定との差",
                    f"{difference:+,}円"
                )

                if deal.get(
                    "memo",
                    "",
                ):
                    st.info(
                        deal.get(
                            "memo",
                            "",
                        )
                    )


# =========================================================
# お気に入り
# =========================================================

with favorite_tab:
    st.header(
        "⭐ お気に入り特典"
    )

    favorites = [
        deal
        for deal in deals
        if deal.get(
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
            key=lambda deal: (
                int(
                    deal.get(
                        "actual_saving",
                        0,
                    )
                ),
                int(
                    deal.get(
                        "estimated_value",
                        0,
                    )
                ),
            ),
            reverse=True,
        )

        for deal in favorites:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### ⭐ "
                    f"{deal.get('title', '')}"
                )

                st.caption(
                    f"{deal.get('deal_type', '')} ／ "
                    f"{deal.get('shop', '') or '店舗未設定'}"
                )

                st.write(
                    f"特典："
                    f"**{benefit_text(deal)}**"
                )

                if deal.get(
                    "status"
                ) == "利用済み":
                    st.success(
                        f"実際のお得："
                        f"{deal.get('actual_saving', 0):,}円"
                    )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 お得分析"
    )

    if not deals:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for deal in deals:
            analysis_rows.append(
                {
                    "特典": (
                        deal.get(
                            "title",
                            "",
                        )
                    ),
                    "種類": (
                        deal.get(
                            "deal_type",
                            "",
                        )
                    ),
                    "店舗": (
                        deal.get(
                            "shop",
                            "",
                        )
                        or "未設定"
                    ),
                    "状態": (
                        deal_status_label(
                            deal
                        )
                    ),
                    "利用状態": (
                        deal.get(
                            "status",
                            "",
                        )
                    ),
                    "想定お得額": int(
                        deal.get(
                            "estimated_value",
                            0,
                        )
                    ),
                    "実際のお得額": int(
                        deal.get(
                            "actual_saving",
                            0,
                        )
                    ),
                    "利用月": (
                        deal.get(
                            "used_date",
                            "",
                        )[:7]
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "月別のお得額"
        )

        used_df = analysis_df[
            analysis_df[
                "利用状態"
            ]
            == "利用済み"
        ]

        if used_df.empty:
            st.info(
                "利用済みの特典がありません。"
            )

        else:
            monthly_summary = (
                used_df.groupby(
                    "利用月",
                    as_index=False,
                )
                .agg(
                    お得額=(
                        "実際のお得額",
                        "sum",
                    ),
                    利用数=(
                        "特典",
                        "count",
                    ),
                )
                .sort_values(
                    "利用月"
                )
            )

            st.bar_chart(
                monthly_summary.set_index(
                    "利用月"
                )[["お得額"]]
            )

            st.dataframe(
                monthly_summary,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "種類別のお得額"
        )

        if not used_df.empty:
            type_summary = (
                used_df.groupby(
                    "種類",
                    as_index=False,
                )
                .agg(
                    お得額=(
                        "実際のお得額",
                        "sum",
                    ),
                    利用数=(
                        "特典",
                        "count",
                    ),
                )
                .sort_values(
                    "お得額",
                    ascending=False,
                )
            )

            st.bar_chart(
                type_summary.set_index(
                    "種類"
                )[["お得額"]]
            )

            st.dataframe(
                type_summary,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "店舗別のお得額"
        )

        if not used_df.empty:
            shop_summary = (
                used_df.groupby(
                    "店舗",
                    as_index=False,
                )
                .agg(
                    お得額=(
                        "実際のお得額",
                        "sum",
                    ),
                    利用数=(
                        "特典",
                        "count",
                    ),
                )
                .sort_values(
                    "お得額",
                    ascending=False,
                )
            )

            st.bar_chart(
                shop_summary.set_index(
                    "店舗"
                )[["お得額"]]
            )

            st.dataframe(
                shop_summary,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "使えず期限切れになった特典"
        )

        expired_df = analysis_df[
            analysis_df[
                "状態"
            ]
            == "期限切れ"
        ]

        if expired_df.empty:
            st.success(
                "現在、期限切れになった未使用特典はありません！"
            )

        else:
            missed_value = int(
                expired_df[
                    "想定お得額"
                ].sum()
            )

            columns = st.columns(
                2
            )

            columns[0].metric(
                "期限切れ",
                f"{len(expired_df)}件"
            )

            columns[1].metric(
                "逃した想定お得",
                f"{missed_value:,}円"
            )

            st.dataframe(
                expired_df[
                    [
                        "特典",
                        "種類",
                        "店舗",
                        "想定お得額",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "利用率"
        )

        rate_columns = st.columns(
            3
        )

        used_count = len(
            [
                deal
                for deal in deals
                if deal.get(
                    "status"
                )
                == "利用済み"
            ]
        )

        missed_count = len(
            expired
        )

        skipped_count = len(
            [
                deal
                for deal in deals
                if deal.get(
                    "status"
                )
                == "見送り"
            ]
        )

        rate_columns[0].metric(
            "利用済み",
            f"{used_count}件"
        )

        rate_columns[1].metric(
            "期限切れ",
            f"{missed_count}件"
        )

        rate_columns[2].metric(
            "見送り",
            f"{skipped_count}件"
        )

        st.metric(
            "全体利用率",
            f"{usage_rate(deals):.1f}%"
        )

        st.divider()

        st.subheader(
            "よく登録する特典"
        )

        type_counter = Counter(
            deal.get(
                "deal_type",
                "その他",
            )
            for deal in deals
        )

        if type_counter:
            type_count_df = pd.DataFrame(
                [
                    {
                        "種類": deal_type,
                        "登録数": count,
                    }
                    for deal_type, count
                    in type_counter.most_common()
                ]
            )

            st.bar_chart(
                type_count_df.set_index(
                    "種類"
                )[["登録数"]]
            )

            st.dataframe(
                type_count_df,
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
            f"tiny_deal_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONから復元"
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
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict,
                )
                or "deals"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "deals"
                    ],
                    list,
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
        "クーポン・キャンペーン・利用履歴がすべて削除されます。"
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
    "お得だから買うのではなく、買う予定のものを少しお得に。💡"
)
