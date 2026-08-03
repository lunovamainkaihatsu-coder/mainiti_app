import json
import os
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="おでかけ持ち物リスト",
    page_icon="🧳",
    layout="wide"
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "outing_data.json"
)

OUTING_TYPES = [
    "旅行",
    "日帰りレジャー",
    "公園",
    "映画",
    "イベント",
    "病院",
    "買い物",
    "仕事",
    "Amazon Flex",
    "帰省",
    "温泉",
    "子どもとの外出",
    "その他",
]

ITEM_GROUPS = [
    "必須",
    "あると便利",
    "緊急用",
    "その他",
]

OWNERS = [
    "共通",
    "自分",
    "妻",
    "子ども",
    "その他",
]

STATUSES = [
    "準備前",
    "準備中",
    "準備完了",
    "おでかけ済み",
    "中止",
]

STATUS_ICONS = {
    "準備前": "⚪",
    "準備中": "🟡",
    "準備完了": "✅",
    "おでかけ済み": "🏁",
    "中止": "⛔",
}

PRIORITIES = [
    "必須",
    "高",
    "中",
    "低",
]

PRIORITY_ORDER = {
    "必須": 0,
    "高": 1,
    "中": 2,
    "低": 3,
}

PRIORITY_ICONS = {
    "必須": "🚨",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵",
}


DEFAULT_TEMPLATES = [
    {
        "name": "Amazon Flex",
        "outing_type": "Amazon Flex",
        "items": [
            ("スマホ", "自分", "必須", "必須"),
            ("免許証", "自分", "必須", "必須"),
            ("充電ケーブル", "自分", "必須", "高"),
            ("モバイルバッテリー", "自分", "必須", "高"),
            ("飲み物", "自分", "必須", "高"),
            ("タオル", "自分", "あると便利", "中"),
            ("軽食", "自分", "あると便利", "中"),
            ("軍手", "自分", "あると便利", "中"),
            ("雨具", "自分", "緊急用", "中"),
        ],
    },
    {
        "name": "子どもとの外出",
        "outing_type": "子どもとの外出",
        "items": [
            ("財布", "共通", "必須", "必須"),
            ("スマホ", "共通", "必須", "必須"),
            ("飲み物", "共通", "必須", "高"),
            ("着替え", "子ども", "必須", "高"),
            ("おむつ", "子ども", "必須", "必須"),
            ("おしりふき", "子ども", "必須", "必須"),
            ("お菓子", "子ども", "あると便利", "中"),
            ("タオル", "共通", "あると便利", "中"),
            ("ビニール袋", "共通", "あると便利", "中"),
            ("お気に入りのおもちゃ", "子ども", "あると便利", "低"),
        ],
    },
    {
        "name": "旅行",
        "outing_type": "旅行",
        "items": [
            ("財布", "共通", "必須", "必須"),
            ("スマホ", "共通", "必須", "必須"),
            ("充電器", "共通", "必須", "高"),
            ("着替え", "共通", "必須", "高"),
            ("洗面用品", "共通", "必須", "高"),
            ("薬", "共通", "必須", "高"),
            ("予約確認", "共通", "必須", "必須"),
            ("モバイルバッテリー", "共通", "あると便利", "中"),
            ("折りたたみ傘", "共通", "緊急用", "中"),
        ],
    },
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作成する。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    """初期データを作成する。"""

    return {
        "templates": [],
        "outings": [],
    }


def create_item(
    name,
    owner="共通",
    group="必須",
    priority="中",
    checked=False,
    source_template="",
):
    """持ち物データを作成する。"""

    return {
        "id": create_id(),
        "name": name,
        "owner": owner,
        "group": group,
        "priority": priority,
        "checked": checked,
        "forgotten": False,
        "source_template": source_template,
        "memo": "",
        "created_at": now_text(),
        "updated_at": "",
    }


def create_default_templates():
    """初期テンプレートを作成する。"""

    templates = []

    for template_data in DEFAULT_TEMPLATES:
        template_id = create_id()

        items = []

        for name, owner, group, priority in template_data["items"]:
            items.append(
                create_item(
                    name=name,
                    owner=owner,
                    group=group,
                    priority=priority,
                    source_template=template_data["name"],
                )
            )

        templates.append(
            {
                "id": template_id,
                "name": template_data["name"],
                "outing_type": template_data["outing_type"],
                "items": items,
                "created_at": now_text(),
                "updated_at": "",
            }
        )

    return templates


def save_data(data):
    """JSONファイルへ保存する。"""

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


def normalize_item(item):
    """持ち物データへ不足項目を追加する。"""

    item.setdefault(
        "id",
        create_id()
    )

    item.setdefault(
        "name",
        ""
    )

    item.setdefault(
        "owner",
        "共通"
    )

    item.setdefault(
        "group",
        "必須"
    )

    item.setdefault(
        "priority",
        "中"
    )

    item.setdefault(
        "checked",
        False
    )

    item.setdefault(
        "forgotten",
        False
    )

    item.setdefault(
        "source_template",
        ""
    )

    item.setdefault(
        "memo",
        ""
    )

    item.setdefault(
        "created_at",
        ""
    )

    item.setdefault(
        "updated_at",
        ""
    )


def normalize_data(data):
    """古いデータへ不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "templates",
        []
    )

    data.setdefault(
        "outings",
        []
    )

    for template in data["templates"]:
        template.setdefault(
            "id",
            create_id()
        )

        template.setdefault(
            "name",
            ""
        )

        template.setdefault(
            "outing_type",
            "その他"
        )

        template.setdefault(
            "items",
            []
        )

        template.setdefault(
            "created_at",
            ""
        )

        template.setdefault(
            "updated_at",
            ""
        )

        for item in template["items"]:
            normalize_item(item)

    for outing in data["outings"]:
        outing.setdefault(
            "id",
            create_id()
        )

        outing.setdefault(
            "name",
            ""
        )

        outing.setdefault(
            "outing_date",
            str(date.today())
        )

        outing.setdefault(
            "destination",
            ""
        )

        outing.setdefault(
            "outing_type",
            "その他"
        )

        outing.setdefault(
            "status",
            "準備前"
        )

        outing.setdefault(
            "template_name",
            ""
        )

        outing.setdefault(
            "memo",
            ""
        )

        outing.setdefault(
            "improvement_memo",
            ""
        )

        outing.setdefault(
            "forgotten_items",
            []
        )

        outing.setdefault(
            "items",
            []
        )

        outing.setdefault(
            "created_at",
            ""
        )

        outing.setdefault(
            "updated_at",
            ""
        )

        for item in outing["items"]:
            normalize_item(item)

    return data


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = create_empty_data()
        data["templates"] = (
            create_default_templates()
        )

        save_data(data)

        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        data = normalize_data(data)

        if not data["templates"]:
            data["templates"] = (
                create_default_templates()
            )

        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE
            ):
                os.replace(
                    DATA_FILE,
                    broken_file
                )

        except OSError:
            pass

        data = create_empty_data()
        data["templates"] = (
            create_default_templates()
        )

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
            "%Y-%m-%d"
        ).date()

    except (
        TypeError,
        ValueError
    ):
        return None


def format_date(date_text):
    """日付を日本語表示にする。"""

    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "日付不明"

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


def get_template_by_id(
    data,
    template_id,
):
    """IDからテンプレートを取得する。"""

    for template in data["templates"]:
        if template.get(
            "id"
        ) == template_id:
            return template

    return None


def get_outing_by_id(
    data,
    outing_id,
):
    """IDからおでかけを取得する。"""

    for outing in data["outings"]:
        if outing.get(
            "id"
        ) == outing_id:
            return outing

    return None


def get_item_by_id(
    item_list,
    item_id,
):
    """IDから持ち物を取得する。"""

    for item in item_list:
        if item.get(
            "id"
        ) == item_id:
            return item

    return None


def preparation_rate(outing):
    """準備率を計算する。"""

    items = outing.get(
        "items",
        []
    )

    if not items:
        return 0

    checked_count = len(
        [
            item
            for item in items
            if item.get(
                "checked",
                False
            )
        ]
    )

    return (
        checked_count
        / len(items)
        * 100
    )


def checked_count(outing):
    """準備済み数を返す。"""

    return len(
        [
            item
            for item in outing.get(
                "items",
                []
            )
            if item.get(
                "checked",
                False
            )
        ]
    )


def unchecked_items(outing):
    """未準備の持ち物を返す。"""

    return [
        item
        for item in outing.get(
            "items",
            []
        )
        if not item.get(
            "checked",
            False
        )
    ]


def update_outing_status(
    outing
):
    """準備状況から状態を更新する。"""

    if outing.get(
        "status"
    ) in [
        "おでかけ済み",
        "中止",
    ]:
        return

    items = outing.get(
        "items",
        []
    )

    if not items:
        outing["status"] = (
            "準備前"
        )

        return

    rate = preparation_rate(
        outing
    )

    if rate >= 100:
        outing["status"] = (
            "準備完了"
        )

    elif rate > 0:
        outing["status"] = (
            "準備中"
        )

    else:
        outing["status"] = (
            "準備前"
        )


def copy_template_items(
    template,
):
    """テンプレートから持ち物を複製する。"""

    copied_items = []

    for item in template.get(
        "items",
        []
    ):
        copied_items.append(
            create_item(
                name=item.get(
                    "name",
                    ""
                ),
                owner=item.get(
                    "owner",
                    "共通"
                ),
                group=item.get(
                    "group",
                    "必須"
                ),
                priority=item.get(
                    "priority",
                    "中"
                ),
                checked=False,
                source_template=(
                    template.get(
                        "name",
                        ""
                    )
                ),
            )
        )

    return copied_items


def frequent_forgotten_items(
    outings,
):
    """忘れ物ランキングを返す。"""

    counter = Counter()

    for outing in outings:
        for item_name in outing.get(
            "forgotten_items",
            []
        ):
            if item_name.strip():
                counter[
                    item_name.strip()
                ] += 1

    return counter


# =========================================================
# データ操作
# =========================================================

def add_template(
    data,
    name,
    outing_type,
):
    """テンプレートを追加する。"""

    template = {
        "id": create_id(),
        "name": name,
        "outing_type": outing_type,
        "items": [],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["templates"].append(
        template
    )

    save_data(data)


def delete_template(
    data,
    template_id,
):
    """テンプレートを削除する。"""

    data["templates"] = [
        template
        for template in data[
            "templates"
        ]
        if template.get(
            "id"
        ) != template_id
    ]

    save_data(data)


def add_template_item(
    data,
    template_id,
    values,
):
    """テンプレートへ持ち物を追加する。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    template["items"].append(
        create_item(
            name=values["name"],
            owner=values["owner"],
            group=values["group"],
            priority=values["priority"],
            source_template=(
                template.get(
                    "name",
                    ""
                )
            ),
        )
    )

    template["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_template_item(
    data,
    template_id,
    item_id,
):
    """テンプレートの持ち物を削除する。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    template["items"] = [
        item
        for item in template.get(
            "items",
            []
        )
        if item.get(
            "id"
        ) != item_id
    ]

    template["updated_at"] = (
        now_text()
    )

    save_data(data)


def add_outing(
    data,
    values,
):
    """おでかけ予定を追加する。"""

    items = []

    template_name = ""

    if values["template_id"]:
        template = get_template_by_id(
            data,
            values["template_id"]
        )

        if template:
            items = copy_template_items(
                template
            )

            template_name = (
                template.get(
                    "name",
                    ""
                )
            )

            forgotten_counter = (
                frequent_forgotten_items(
                    data["outings"]
                )
            )

            existing_names = {
                item.get(
                    "name",
                    ""
                ).strip().lower()
                for item in items
            }

            for forgotten_name, count in forgotten_counter.items():
                if (
                    count > 0
                    and forgotten_name.lower()
                    not in existing_names
                ):
                    items.append(
                        create_item(
                            name=forgotten_name,
                            owner="共通",
                            group="必須",
                            priority="高",
                            source_template=(
                                "過去の忘れ物"
                            ),
                        )
                    )

    outing = {
        "id": create_id(),
        "name": values["name"],
        "outing_date": (
            values["outing_date"]
        ),
        "destination": (
            values["destination"]
        ),
        "outing_type": (
            values["outing_type"]
        ),
        "status": "準備前",
        "template_name": (
            template_name
        ),
        "memo": values["memo"],
        "improvement_memo": "",
        "forgotten_items": [],
        "items": items,
        "created_at": now_text(),
        "updated_at": "",
    }

    update_outing_status(
        outing
    )

    data["outings"].append(
        outing
    )

    save_data(data)


def update_outing(
    data,
    outing_id,
    values,
):
    """おでかけ情報を更新する。"""

    outing = get_outing_by_id(
        data,
        outing_id
    )

    if not outing:
        return

    for key, value in values.items():
        outing[key] = value

    update_outing_status(
        outing
    )

    outing["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_outing(
    data,
    outing_id,
):
    """おでかけ予定を削除する。"""

    data["outings"] = [
        outing
        for outing in data[
            "outings"
        ]
        if outing.get(
            "id"
        ) != outing_id
    ]

    save_data(data)


def add_outing_item(
    data,
    outing_id,
    values,
):
    """おでかけへ持ち物を追加する。"""

    outing = get_outing_by_id(
        data,
        outing_id
    )

    if not outing:
        return

    outing["items"].append(
        create_item(
            name=values["name"],
            owner=values["owner"],
            group=values["group"],
            priority=values["priority"],
        )
    )

    update_outing_status(
        outing
    )

    outing["updated_at"] = (
        now_text()
    )

    save_data(data)


def update_item_check(
    data,
    outing_id,
    item_id,
    checked,
):
    """持ち物のチェックを更新する。"""

    outing = get_outing_by_id(
        data,
        outing_id
    )

    if not outing:
        return

    item = get_item_by_id(
        outing.get(
            "items",
            []
        ),
        item_id,
    )

    if not item:
        return

    item["checked"] = bool(
        checked
    )

    item["updated_at"] = (
        now_text()
    )

    update_outing_status(
        outing
    )

    outing["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_outing_item(
    data,
    outing_id,
    item_id,
):
    """おでかけの持ち物を削除する。"""

    outing = get_outing_by_id(
        data,
        outing_id
    )

    if not outing:
        return

    outing["items"] = [
        item
        for item in outing.get(
            "items",
            []
        )
        if item.get(
            "id"
        ) != item_id
    ]

    update_outing_status(
        outing
    )

    outing["updated_at"] = (
        now_text()
    )

    save_data(data)


def reset_outing_checks(
    data,
    outing_id,
):
    """全チェックを外す。"""

    outing = get_outing_by_id(
        data,
        outing_id
    )

    if not outing:
        return

    for item in outing.get(
        "items",
        []
    ):
        item["checked"] = False
        item["updated_at"] = (
            now_text()
        )

    update_outing_status(
        outing
    )

    outing["updated_at"] = (
        now_text()
    )

    save_data(data)


def complete_outing(
    data,
    outing_id,
):
    """おでかけ済みにする。"""

    outing = get_outing_by_id(
        data,
        outing_id
    )

    if not outing:
        return

    outing["status"] = (
        "おでかけ済み"
    )

    outing["updated_at"] = (
        now_text()
    )

    save_data(data)


def save_outing_review(
    data,
    outing_id,
    forgotten_items,
    improvement_memo,
):
    """忘れ物と改善メモを保存する。"""

    outing = get_outing_by_id(
        data,
        outing_id
    )

    if not outing:
        return

    outing["forgotten_items"] = list(
        dict.fromkeys(
            forgotten_items
        )
    )

    outing["improvement_memo"] = (
        improvement_memo
    )

    for item in outing.get(
        "items",
        []
    ):
        item["forgotten"] = (
            item.get(
                "name",
                ""
            )
            in forgotten_items
        )

    outing["updated_at"] = (
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
        background: rgba(70, 170, 150, 0.08);
        border: 1px solid rgba(70, 170, 150, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(70, 170, 150, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(70, 170, 150, 0.18),
                rgba(90, 130, 255, 0.12)
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
    unsafe_allow_html=True
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

templates = data[
    "templates"
]

outings = data[
    "outings"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧳 おでかけ持ち物リスト</h1>
        <p>
            外出前の準備をテンプレート化して、
            家族みんなの忘れ物を減らすアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ダッシュボード
# =========================================================

today_outings = [
    outing
    for outing in outings
    if outing.get(
        "outing_date"
    ) == str(
        date.today()
    )
    and outing.get(
        "status"
    )
    not in [
        "中止",
        "おでかけ済み",
    ]
]

week_end = (
    date.today()
    + timedelta(
        days=7
    )
)

this_week_outings = [
    outing
    for outing in outings
    if (
        parse_date(
            outing.get(
                "outing_date",
                ""
            )
        )
        and date.today()
        <= parse_date(
            outing.get(
                "outing_date",
                ""
            )
        )
        <= week_end
        and outing.get(
            "status"
        )
        not in [
            "中止",
            "おでかけ済み",
        ]
    )
]

preparing_count = len(
    [
        outing
        for outing in outings
        if outing.get(
            "status"
        )
        in [
            "準備前",
            "準備中",
        ]
    ]
)

ready_count = len(
    [
        outing
        for outing in outings
        if outing.get(
            "status"
        )
        == "準備完了"
    ]
)

average_preparation_rate = (
    sum(
        preparation_rate(
            outing
        )
        for outing in outings
    )
    / len(outings)
    if outings
    else 0
)

forgotten_counter = (
    frequent_forgotten_items(
        outings
    )
)

most_forgotten = (
    forgotten_counter.most_common(
        1
    )[0][0]
    if forgotten_counter
    else "なし"
)

template_counter = Counter(
    outing.get(
        "template_name",
        ""
    )
    for outing in outings
    if outing.get(
        "template_name",
        ""
    )
)

most_used_template = (
    template_counter.most_common(
        1
    )[0][0]
    if template_counter
    else "なし"
)


metric_row1 = st.columns(4)

metric_row1[0].metric(
    "今日のおでかけ",
    f"{len(today_outings)}件"
)

metric_row1[1].metric(
    "今週の予定",
    f"{len(this_week_outings)}件"
)

metric_row1[2].metric(
    "準備中",
    f"{preparing_count}件"
)

metric_row1[3].metric(
    "準備完了",
    f"{ready_count}件"
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "平均準備率",
    f"{average_preparation_rate:.1f}%"
)

metric_row2[1].metric(
    "テンプレート数",
    f"{len(templates)}件"
)

metric_row2[2].metric(
    "よく忘れる物",
    most_forgotten
)

metric_row2[3].metric(
    "よく使う型",
    most_used_template
)


# =========================================================
# 次のおでかけ
# =========================================================

upcoming_outings = [
    outing
    for outing in outings
    if (
        parse_date(
            outing.get(
                "outing_date",
                ""
            )
        )
        and parse_date(
            outing.get(
                "outing_date",
                ""
            )
        )
        >= date.today()
        and outing.get(
            "status"
        )
        not in [
            "中止",
            "おでかけ済み",
        ]
    )
]

if upcoming_outings:
    st.divider()

    upcoming_outings.sort(
        key=lambda outing: (
            parse_date(
                outing.get(
                    "outing_date",
                    ""
                )
            )
            or date.max
        )
    )

    next_outing = (
        upcoming_outings[0]
    )

    st.subheader(
        "🚗 次のおでかけ"
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
                f"{next_outing.get('name', '')}"
            )

            st.caption(
                f"{format_date(next_outing.get('outing_date', ''))} ／ "
                f"{next_outing.get('outing_type', '')}"
            )

            if next_outing.get(
                "destination",
                ""
            ):
                st.write(
                    f"📍 "
                    f"{next_outing.get('destination', '')}"
                )

            if next_outing.get(
                "template_name",
                ""
            ):
                st.write(
                    f"📋 テンプレート："
                    f"{next_outing.get('template_name', '')}"
                )

        with column2:
            st.metric(
                "準備率",
                f"{preparation_rate(next_outing):.0f}%"
            )

        st.progress(
            preparation_rate(
                next_outing
            )
            / 100
        )

        unprepared = unchecked_items(
            next_outing
        )

        if not unprepared:
            st.success(
                "準備完了！気をつけていってらっしゃい！"
            )

        else:
            st.warning(
                "未準備："
                + "、".join(
                    item.get(
                        "name",
                        ""
                    )
                    for item in unprepared[
                        :5
                    ]
                )
            )


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    checklist_tab,
    outing_list_tab,
    template_tab,
    review_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ おでかけ登録",
        "✅ 出発前チェック",
        "📅 おでかけ一覧",
        "📋 テンプレート",
        "📝 忘れ物・振り返り",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# おでかけ登録
# =========================================================

with add_tab:
    st.header(
        "➕ 新しいおでかけを登録"
    )

    template_options = {
        "テンプレートなし": ""
    }

    for template in templates:
        template_options[
            (
                f"{template.get('name', '')}"
                f"（{len(template.get('items', []))}個）"
            )
        ] = template.get(
            "id"
        )

    with st.form(
        "add_outing_form",
        clear_on_submit=True
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            outing_name = st.text_input(
                "おでかけ名",
                placeholder=(
                    "例：娘とプリキュアショー"
                )
            )

            outing_date_input = (
                st.date_input(
                    "おでかけ日",
                    value=(
                        date.today()
                        + timedelta(
                            days=1
                        )
                    )
                )
            )

            destination = st.text_input(
                "行き先",
                placeholder=(
                    "例：ショッピングモール"
                )
            )

        with column2:
            outing_type = st.selectbox(
                "おでかけ種類",
                OUTING_TYPES
            )

            selected_template_label = (
                st.selectbox(
                    "持ち物テンプレート",
                    list(
                        template_options.keys()
                    )
                )
            )

            selected_template_id = (
                template_options[
                    selected_template_label
                ]
            )

        outing_memo = st.text_area(
            "メモ",
            placeholder=(
                "集合時間、予約内容、注意事項など"
            ),
            height=110
        )

        submitted = (
            st.form_submit_button(
                "🧳 おでかけを登録",
                use_container_width=True
            )
        )

        if submitted:
            if not outing_name.strip():
                st.error(
                    "おでかけ名を入力してください。"
                )

            else:
                add_outing(
                    data,
                    {
                        "name": (
                            outing_name.strip()
                        ),
                        "outing_date": str(
                            outing_date_input
                        ),
                        "destination": (
                            destination.strip()
                        ),
                        "outing_type": (
                            outing_type
                        ),
                        "template_id": (
                            selected_template_id
                        ),
                        "memo": (
                            outing_memo.strip()
                        ),
                    }
                )

                st.success(
                    "おでかけを登録しました！"
                )

                st.rerun()


# =========================================================
# 出発前チェック
# =========================================================

with checklist_tab:
    st.header(
        "✅ 出発前チェック"
    )

    active_outings = [
        outing
        for outing in outings
        if outing.get(
            "status"
        )
        not in [
            "中止",
            "おでかけ済み",
        ]
    ]

    if not active_outings:
        st.info(
            "準備中のおでかけはありません。"
        )

    else:
        active_outings.sort(
            key=lambda outing: (
                parse_date(
                    outing.get(
                        "outing_date",
                        ""
                    )
                )
                or date.max
            )
        )

        outing_options = {
            (
                f"{outing.get('name', '')}"
                f"｜{format_date(outing.get('outing_date', ''))}"
            ): outing.get(
                "id"
            )
            for outing in active_outings
        }

        selected_outing_label = (
            st.selectbox(
                "おでかけを選択",
                list(
                    outing_options.keys()
                )
            )
        )

        selected_outing = (
            get_outing_by_id(
                data,
                outing_options[
                    selected_outing_label
                ]
            )
        )

        selected_outing_id = (
            selected_outing.get(
                "id"
            )
        )

        with st.container(
            border=True
        ):
            st.subheader(
                selected_outing.get(
                    "name",
                    ""
                )
            )

            st.caption(
                f"{format_date(selected_outing.get('outing_date', ''))} ／ "
                f"{selected_outing.get('destination', '')}"
            )

            progress = preparation_rate(
                selected_outing
            )

            st.progress(
                progress / 100
            )

            st.write(
                f"準備状況："
                f"**{checked_count(selected_outing)}"
                f" / {len(selected_outing.get('items', []))}**"
            )

            if progress >= 100:
                st.success(
                    "準備完了！気をつけていってらっしゃい！"
                )

        with st.form(
            f"add_outing_item_{selected_outing_id}",
            clear_on_submit=True
        ):
            st.subheader(
                "➕ 持ち物を追加"
            )

            add_column1, add_column2 = (
                st.columns(2)
            )

            with add_column1:
                item_name = st.text_input(
                    "持ち物",
                    placeholder=(
                        "例：モバイルバッテリー"
                    )
                )

                item_owner = st.selectbox(
                    "持ち主",
                    OWNERS
                )

            with add_column2:
                item_group = st.selectbox(
                    "分類",
                    ITEM_GROUPS
                )

                item_priority = (
                    st.selectbox(
                        "重要度",
                        PRIORITIES,
                        index=2
                    )
                )

            add_item_submitted = (
                st.form_submit_button(
                    "持ち物を追加",
                    use_container_width=True
                )
            )

            if add_item_submitted:
                cleaned_item_name = (
                    item_name.strip()
                )

                duplicate_exists = any(
                    item.get(
                        "name",
                        ""
                    ).strip().lower()
                    == cleaned_item_name.lower()
                    for item in selected_outing.get(
                        "items",
                        []
                    )
                )

                if not cleaned_item_name:
                    st.error(
                        "持ち物を入力してください。"
                    )

                elif duplicate_exists:
                    st.warning(
                        "同じ持ち物が登録されています。"
                    )

                else:
                    add_outing_item(
                        data,
                        selected_outing_id,
                        {
                            "name": (
                                cleaned_item_name
                            ),
                            "owner": (
                                item_owner
                            ),
                            "group": (
                                item_group
                            ),
                            "priority": (
                                item_priority
                            ),
                        }
                    )

                    st.rerun()

        st.divider()

        items = sorted(
            selected_outing.get(
                "items",
                []
            ),
            key=lambda item: (
                OWNERS.index(
                    item.get(
                        "owner",
                        "共通"
                    )
                )
                if item.get(
                    "owner"
                )
                in OWNERS
                else 99,
                PRIORITY_ORDER.get(
                    item.get(
                        "priority",
                        "中"
                    ),
                    99
                ),
                item.get(
                    "name",
                    ""
                ),
            )
        )

        if not items:
            st.info(
                "持ち物がまだ登録されていません。"
            )

        else:
            selected_owner_filter = (
                st.selectbox(
                    "持ち主で絞り込み",
                    [
                        "すべて"
                    ]
                    + OWNERS
                )
            )

            if selected_owner_filter != "すべて":
                items = [
                    item
                    for item in items
                    if item.get(
                        "owner"
                    )
                    == selected_owner_filter
                ]

            for owner in OWNERS:
                owner_items = [
                    item
                    for item in items
                    if item.get(
                        "owner"
                    )
                    == owner
                ]

                if not owner_items:
                    continue

                st.subheader(
                    f"👤 {owner}"
                )

                for item in owner_items:
                    item_id = item.get(
                        "id"
                    )

                    with st.container(
                        border=True
                    ):
                        item_column1, item_column2 = (
                            st.columns(
                                [
                                    5,
                                    1,
                                ]
                            )
                        )

                        with item_column1:
                            checked = st.checkbox(
                                (
                                    f"{PRIORITY_ICONS.get(item.get('priority', ''), '')} "
                                    f"{item.get('name', '')} "
                                    f"｜{item.get('group', '')}"
                                ),
                                value=bool(
                                    item.get(
                                        "checked",
                                        False
                                    )
                                ),
                                key=(
                                    f"check_item_"
                                    f"{item_id}"
                                )
                            )

                            if (
                                checked
                                != item.get(
                                    "checked",
                                    False
                                )
                            ):
                                update_item_check(
                                    data,
                                    selected_outing_id,
                                    item_id,
                                    checked,
                                )

                                st.rerun()

                            if item.get(
                                "source_template"
                            ) == "過去の忘れ物":
                                st.warning(
                                    "前回までに忘れたことがある持ち物です。"
                                )

                        with item_column2:
                            if st.button(
                                "削除",
                                key=(
                                    f"delete_item_"
                                    f"{item_id}"
                                )
                            ):
                                delete_outing_item(
                                    data,
                                    selected_outing_id,
                                    item_id,
                                )

                                st.rerun()

            action_columns = (
                st.columns(2)
            )

            with action_columns[0]:
                if st.button(
                    "🔄 全チェックを外す",
                    use_container_width=True
                ):
                    reset_outing_checks(
                        data,
                        selected_outing_id
                    )

                    st.rerun()

            with action_columns[1]:
                if st.button(
                    "🏁 おでかけ済みにする",
                    use_container_width=True
                ):
                    complete_outing(
                        data,
                        selected_outing_id
                    )

                    st.success(
                        "おでかけ済みにしました！"
                    )

                    st.rerun()


# =========================================================
# おでかけ一覧
# =========================================================

with outing_list_tab:
    st.header(
        "📅 おでかけ一覧"
    )

    if not outings:
        st.info(
            "おでかけはまだ登録されていません。"
        )

    else:
        filter_column1, filter_column2, filter_column3 = (
            st.columns(3)
        )

        with filter_column1:
            keyword = st.text_input(
                "🔍 検索",
                placeholder=(
                    "おでかけ名・行き先"
                )
            )

        with filter_column2:
            type_filter = st.selectbox(
                "おでかけ種類",
                [
                    "すべて"
                ]
                + OUTING_TYPES
            )

        with filter_column3:
            status_filter = st.selectbox(
                "状態",
                [
                    "すべて"
                ]
                + STATUSES
            )

        filtered_outings = list(
            outings
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_outings = [
                outing
                for outing in filtered_outings
                if (
                    search_word
                    in outing.get(
                        "name",
                        ""
                    ).lower()
                    or search_word
                    in outing.get(
                        "destination",
                        ""
                    ).lower()
                    or search_word
                    in outing.get(
                        "memo",
                        ""
                    ).lower()
                )
            ]

        if type_filter != "すべて":
            filtered_outings = [
                outing
                for outing in filtered_outings
                if outing.get(
                    "outing_type"
                )
                == type_filter
            ]

        if status_filter != "すべて":
            filtered_outings = [
                outing
                for outing in filtered_outings
                if outing.get(
                    "status"
                )
                == status_filter
            ]

        filtered_outings.sort(
            key=lambda outing: (
                parse_date(
                    outing.get(
                        "outing_date",
                        ""
                    )
                )
                or date.min
            ),
            reverse=True
        )

        st.write(
            f"表示件数："
            f"**{len(filtered_outings)}件**"
        )

        for outing in filtered_outings:
            outing_id = outing.get(
                "id"
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
                        f"{outing.get('name', '')}"
                    )

                    st.caption(
                        f"{format_date(outing.get('outing_date', ''))} ／ "
                        f"{outing.get('outing_type', '')}"
                    )

                    if outing.get(
                        "destination",
                        ""
                    ):
                        st.write(
                            f"📍 "
                            f"{outing.get('destination', '')}"
                        )

                with column2:
                    status = outing.get(
                        "status",
                        "準備前"
                    )

                    st.metric(
                        "状態",
                        f"{STATUS_ICONS.get(status, '')} "
                        f"{status}"
                    )

                st.progress(
                    preparation_rate(
                        outing
                    )
                    / 100
                )

                st.caption(
                    f"準備："
                    f"{checked_count(outing)}"
                    f" / {len(outing.get('items', []))}"
                )

                if outing.get(
                    "forgotten_items",
                    []
                ):
                    st.warning(
                        "忘れ物："
                        + "、".join(
                            outing.get(
                                "forgotten_items",
                                []
                            )
                        )
                    )

                if outing.get(
                    "improvement_memo",
                    ""
                ):
                    st.info(
                        "次回の改善\n\n"
                        + outing.get(
                            "improvement_memo",
                            ""
                        )
                    )

                with st.expander(
                    "✏️ おでかけ情報を編集"
                ):
                    edit_name = st.text_input(
                        "おでかけ名",
                        value=outing.get(
                            "name",
                            ""
                        ),
                        key=(
                            f"edit_name_"
                            f"{outing_id}"
                        )
                    )

                    edit_date = st.date_input(
                        "おでかけ日",
                        value=(
                            parse_date(
                                outing.get(
                                    "outing_date",
                                    ""
                                )
                            )
                            or date.today()
                        ),
                        key=(
                            f"edit_date_"
                            f"{outing_id}"
                        )
                    )

                    edit_destination = st.text_input(
                        "行き先",
                        value=outing.get(
                            "destination",
                            ""
                        ),
                        key=(
                            f"edit_destination_"
                            f"{outing_id}"
                        )
                    )

                    current_type = outing.get(
                        "outing_type",
                        "その他"
                    )

                    edit_type = st.selectbox(
                        "おでかけ種類",
                        OUTING_TYPES,
                        index=(
                            OUTING_TYPES.index(
                                current_type
                            )
                            if current_type
                            in OUTING_TYPES
                            else (
                                len(
                                    OUTING_TYPES
                                )
                                - 1
                            )
                        ),
                        key=(
                            f"edit_type_"
                            f"{outing_id}"
                        )
                    )

                    current_status = outing.get(
                        "status",
                        "準備前"
                    )

                    edit_status = st.selectbox(
                        "状態",
                        STATUSES,
                        index=(
                            STATUSES.index(
                                current_status
                            )
                            if current_status
                            in STATUSES
                            else 0
                        ),
                        key=(
                            f"edit_status_"
                            f"{outing_id}"
                        )
                    )

                    edit_memo = st.text_area(
                        "メモ",
                        value=outing.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_memo_"
                            f"{outing_id}"
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_outing_"
                            f"{outing_id}"
                        ),
                        use_container_width=True
                    ):
                        if not edit_name.strip():
                            st.error(
                                "おでかけ名を入力してください。"
                            )

                        else:
                            update_outing(
                                data,
                                outing_id,
                                {
                                    "name": (
                                        edit_name.strip()
                                    ),
                                    "outing_date": str(
                                        edit_date
                                    ),
                                    "destination": (
                                        edit_destination.strip()
                                    ),
                                    "outing_type": (
                                        edit_type
                                    ),
                                    "status": (
                                        edit_status
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
                    confirm_delete = st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_"
                            f"{outing_id}"
                        )
                    )

                    if st.button(
                        "このおでかけを削除",
                        key=(
                            f"delete_outing_"
                            f"{outing_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_outing(
                            data,
                            outing_id
                        )

                        st.rerun()


# =========================================================
# テンプレート
# =========================================================

with template_tab:
    st.header(
        "📋 持ち物テンプレート"
    )

    with st.form(
        "add_template_form",
        clear_on_submit=True
    ):
        template_column1, template_column2 = (
            st.columns(2)
        )

        with template_column1:
            new_template_name = (
                st.text_input(
                    "新しいテンプレート名",
                    placeholder=(
                        "例：病院セット"
                    )
                )
            )

        with template_column2:
            new_template_type = (
                st.selectbox(
                    "おでかけ種類",
                    OUTING_TYPES,
                    key="new_template_type"
                )
            )

        template_submit = (
            st.form_submit_button(
                "テンプレートを作成",
                use_container_width=True
            )
        )

        if template_submit:
            cleaned_template_name = (
                new_template_name.strip()
            )

            duplicate_template = any(
                template.get(
                    "name",
                    ""
                ).strip().lower()
                == cleaned_template_name.lower()
                for template in templates
            )

            if not cleaned_template_name:
                st.error(
                    "テンプレート名を入力してください。"
                )

            elif duplicate_template:
                st.warning(
                    "同じテンプレート名があります。"
                )

            else:
                add_template(
                    data,
                    cleaned_template_name,
                    new_template_type,
                )

                st.rerun()

    if templates:
        template_options = {
            template.get(
                "name",
                ""
            ): template.get(
                "id"
            )
            for template in templates
        }

        selected_template_name = (
            st.selectbox(
                "編集するテンプレート",
                list(
                    template_options.keys()
                )
            )
        )

        selected_template = (
            get_template_by_id(
                data,
                template_options[
                    selected_template_name
                ]
            )
        )

        selected_template_id = (
            selected_template.get(
                "id"
            )
        )

        st.write(
            f"登録済み持ち物："
            f"**{len(selected_template.get('items', []))}個**"
        )

        with st.form(
            f"add_template_item_{selected_template_id}",
            clear_on_submit=True
        ):
            item_column1, item_column2 = (
                st.columns(2)
            )

            with item_column1:
                template_item_name = (
                    st.text_input(
                        "持ち物",
                        placeholder=(
                            "例：保険証"
                        )
                    )
                )

                template_item_owner = (
                    st.selectbox(
                        "持ち主",
                        OWNERS,
                        key="template_item_owner"
                    )
                )

            with item_column2:
                template_item_group = (
                    st.selectbox(
                        "分類",
                        ITEM_GROUPS,
                        key="template_item_group"
                    )
                )

                template_item_priority = (
                    st.selectbox(
                        "重要度",
                        PRIORITIES,
                        index=2,
                        key="template_item_priority"
                    )
                )

            add_template_item_submit = (
                st.form_submit_button(
                    "テンプレートへ追加",
                    use_container_width=True
                )
            )

            if add_template_item_submit:
                cleaned_name = (
                    template_item_name.strip()
                )

                if not cleaned_name:
                    st.error(
                        "持ち物を入力してください。"
                    )

                else:
                    add_template_item(
                        data,
                        selected_template_id,
                        {
                            "name": (
                                cleaned_name
                            ),
                            "owner": (
                                template_item_owner
                            ),
                            "group": (
                                template_item_group
                            ),
                            "priority": (
                                template_item_priority
                            ),
                        }
                    )

                    st.rerun()

        for item in selected_template.get(
            "items",
            []
        ):
            item_id = item.get(
                "id"
            )

            with st.container(
                border=True
            ):
                column1, column2 = (
                    st.columns(
                        [
                            5,
                            1,
                        ]
                    )
                )

                column1.write(
                    f"{PRIORITY_ICONS.get(item.get('priority', ''), '')} "
                    f"**{item.get('name', '')}** "
                    f"｜{item.get('owner', '')} "
                    f"｜{item.get('group', '')}"
                )

                if column2.button(
                    "削除",
                    key=(
                        f"delete_template_item_"
                        f"{item_id}"
                    )
                ):
                    delete_template_item(
                        data,
                        selected_template_id,
                        item_id,
                    )

                    st.rerun()

        with st.expander(
            "テンプレートを削除"
        ):
            st.warning(
                "このテンプレート自体を削除します。"
            )

            confirm_template_delete = (
                st.checkbox(
                    "削除を確認しました",
                    key=(
                        f"confirm_template_delete_"
                        f"{selected_template_id}"
                    )
                )
            )

            if st.button(
                "テンプレートを削除",
                disabled=(
                    not confirm_template_delete
                ),
                use_container_width=True
            ):
                delete_template(
                    data,
                    selected_template_id
                )

                st.rerun()


# =========================================================
# 忘れ物・振り返り
# =========================================================

with review_tab:
    st.header(
        "📝 忘れ物・振り返り"
    )

    completed_outings = [
        outing
        for outing in outings
        if outing.get(
            "status"
        )
        == "おでかけ済み"
    ]

    if not completed_outings:
        st.info(
            "おでかけ済みの記録がありません。"
        )

    else:
        completed_outings.sort(
            key=lambda outing: (
                parse_date(
                    outing.get(
                        "outing_date",
                        ""
                    )
                )
                or date.min
            ),
            reverse=True
        )

        review_options = {
            (
                f"{outing.get('name', '')}"
                f"｜{format_date(outing.get('outing_date', ''))}"
            ): outing.get(
                "id"
            )
            for outing in completed_outings
        }

        selected_review_label = (
            st.selectbox(
                "振り返るおでかけ",
                list(
                    review_options.keys()
                )
            )
        )

        review_outing = (
            get_outing_by_id(
                data,
                review_options[
                    selected_review_label
                ]
            )
        )

        review_outing_id = (
            review_outing.get(
                "id"
            )
        )

        existing_item_names = [
            item.get(
                "name",
                ""
            )
            for item in review_outing.get(
                "items",
                []
            )
        ]

        forgotten_from_list = (
            st.multiselect(
                "今回忘れた物",
                existing_item_names,
                default=[
                    item_name
                    for item_name
                    in review_outing.get(
                        "forgotten_items",
                        []
                    )
                    if item_name
                    in existing_item_names
                ],
            )
        )

        custom_forgotten_text = (
            st.text_input(
                "リストになかった忘れ物",
                placeholder=(
                    "複数ある場合はカンマ区切り"
                )
            )
        )

        improvement_memo = (
            st.text_area(
                "次回への改善メモ",
                value=review_outing.get(
                    "improvement_memo",
                    ""
                ),
                placeholder=(
                    "次回は何を追加するか、準備方法をどう変えるか"
                ),
                height=130
            )
        )

        if st.button(
            "振り返りを保存",
            use_container_width=True
        ):
            custom_forgotten = [
                item.strip()
                for item
                in custom_forgotten_text.split(
                    ","
                )
                if item.strip()
            ]

            final_forgotten_items = list(
                dict.fromkeys(
                    forgotten_from_list
                    + custom_forgotten
                )
            )

            save_outing_review(
                data,
                review_outing_id,
                final_forgotten_items,
                improvement_memo.strip(),
            )

            st.success(
                "振り返りを保存しました！"
            )

            st.rerun()

        if review_outing.get(
            "forgotten_items",
            []
        ):
            st.warning(
                "今回の忘れ物："
                + "、".join(
                    review_outing.get(
                        "forgotten_items",
                        []
                    )
                )
            )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 おでかけ準備の分析"
    )

    if not outings:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for outing in outings:
            analysis_rows.append(
                {
                    "おでかけ名": (
                        outing.get(
                            "name",
                            ""
                        )
                    ),
                    "日付": parse_date(
                        outing.get(
                            "outing_date",
                            ""
                        )
                    ),
                    "種類": (
                        outing.get(
                            "outing_type",
                            ""
                        )
                    ),
                    "状態": (
                        outing.get(
                            "status",
                            ""
                        )
                    ),
                    "テンプレート": (
                        outing.get(
                            "template_name",
                            ""
                        )
                        or "なし"
                    ),
                    "持ち物数": len(
                        outing.get(
                            "items",
                            []
                        )
                    ),
                    "準備率": round(
                        preparation_rate(
                            outing
                        ),
                        1
                    ),
                    "忘れ物数": len(
                        outing.get(
                            "forgotten_items",
                            []
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "おでかけ種類別"
        )

        type_summary = (
            analysis_df.groupby(
                "種類",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "回数"
                }
            )
            .sort_values(
                "回数",
                ascending=False
            )
        )

        st.bar_chart(
            type_summary.set_index(
                "種類"
            )[["回数"]]
        )

        st.dataframe(
            type_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "テンプレート利用回数"
        )

        template_summary = (
            analysis_df.groupby(
                "テンプレート",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "利用回数"
                }
            )
            .sort_values(
                "利用回数",
                ascending=False
            )
        )

        st.bar_chart(
            template_summary.set_index(
                "テンプレート"
            )[["利用回数"]]
        )

        st.dataframe(
            template_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "よく忘れる物"
        )

        if forgotten_counter:
            forgotten_df = pd.DataFrame(
                [
                    {
                        "持ち物": item_name,
                        "忘れた回数": count,
                    }
                    for item_name, count
                    in forgotten_counter.most_common()
                ]
            )

            st.bar_chart(
                forgotten_df.set_index(
                    "持ち物"
                )[["忘れた回数"]]
            )

            st.dataframe(
                forgotten_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "忘れ物の記録はありません。"
            )

        st.divider()

        st.subheader(
            "おでかけ別準備率"
        )

        preparation_df = (
            analysis_df.sort_values(
                "日付"
            )[
                [
                    "おでかけ名",
                    "日付",
                    "準備率",
                    "持ち物数",
                    "忘れ物数",
                ]
            ]
        )

        st.dataframe(
            preparation_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "家族別の持ち物数"
        )

        owner_counter = Counter()

        for outing in outings:
            for item in outing.get(
                "items",
                []
            ):
                owner_counter[
                    item.get(
                        "owner",
                        "共通"
                    )
                ] += 1

        if owner_counter:
            owner_df = pd.DataFrame(
                [
                    {
                        "持ち主": owner,
                        "持ち物数": count,
                    }
                    for owner, count
                    in owner_counter.items()
                ]
            ).sort_values(
                "持ち物数",
                ascending=False
            )

            st.bar_chart(
                owner_df.set_index(
                    "持ち主"
                )[["持ち物数"]]
            )

            st.dataframe(
                owner_df,
                use_container_width=True,
                hide_index=True
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
        indent=2
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"outing_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True
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
            ]
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
                    dict
                )
                or "templates"
                not in imported_data
                or "outings"
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
                    use_container_width=True
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
            UnicodeDecodeError
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "おでかけ・持ち物・テンプレートがすべて削除されます。"
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
        use_container_width=True
    ):
        new_data = create_empty_data()
        new_data["templates"] = (
            create_default_templates()
        )

        save_data(
            new_data
        )

        st.success(
            "データを削除し、初期テンプレートへ戻しました。"
        )

        st.rerun()


# =========================================================
# フッター
# =========================================================

st.divider()

st.success(
    "準備ができたら、あとは楽しいおでかけへ！🧳"
)
