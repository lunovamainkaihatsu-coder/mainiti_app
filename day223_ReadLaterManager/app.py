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
    page_title="あとで読む",
    page_icon="📚",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "read_later_data.json",
)

CONTENT_TYPES = [
    "Web記事",
    "YouTube",
    "SNS投稿",
    "本",
    "PDF",
    "ニュース",
    "ブログ",
    "技術記事",
    "動画",
    "その他",
]

STATUSES = [
    "未読",
    "読みかけ",
    "視聴中",
    "完了",
    "保留",
    "アーカイブ",
]

STATUS_ICONS = {
    "未読": "📥",
    "読みかけ": "📖",
    "視聴中": "▶️",
    "完了": "✅",
    "保留": "⏸️",
    "アーカイブ": "📦",
}

PRIORITIES = [
    "最優先",
    "高",
    "中",
    "低",
]

PRIORITY_ORDER = {
    "最優先": 0,
    "高": 1,
    "中": 2,
    "低": 3,
}

PRIORITY_ICONS = {
    "最優先": "🔥",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵",
}


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作る。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds",
    )


def create_empty_data():
    """空の初期データを作る。"""

    return {
        "items": [],
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
    """過去データへ不足項目を追加する。"""

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
            "title",
            "",
        )

        item.setdefault(
            "content_type",
            "Web記事",
        )

        item.setdefault(
            "url",
            "",
        )

        item.setdefault(
            "saved_date",
            str(date.today()),
        )

        item.setdefault(
            "priority",
            "中",
        )

        item.setdefault(
            "status",
            "未読",
        )

        item.setdefault(
            "favorite",
            False,
        )

        item.setdefault(
            "tags",
            [],
        )

        item.setdefault(
            "saved_reason",
            "",
        )

        item.setdefault(
            "memo",
            "",
        )

        item.setdefault(
            "summary",
            "",
        )

        item.setdefault(
            "learning",
            "",
        )

        item.setdefault(
            "action",
            "",
        )

        item.setdefault(
            "rating",
            0,
        )

        item.setdefault(
            "completed_date",
            "",
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
    """JSONファイルからデータを読み込む。"""

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

    parsed = parse_date(
        date_text,
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
    """IDから項目を取得する。"""

    for item in data["items"]:
        if item.get(
            "id",
        ) == item_id:
            return item

    return None


def get_all_tags(
    items,
):
    """登録済みタグを取得する。"""

    tags = set()

    for item in items:
        for tag in item.get(
            "tags",
            [],
        ):
            cleaned = tag.strip()

            if cleaned:
                tags.add(
                    cleaned
                )

    return sorted(
        tags
    )


def days_since_saved(
    item,
):
    """保存してからの日数を返す。"""

    saved_date = parse_date(
        item.get(
            "saved_date",
            "",
        )
    )

    if not saved_date:
        return None

    return (
        date.today()
        - saved_date
    ).days


def days_to_complete(
    item,
):
    """保存から完了までの日数を返す。"""

    saved_date = parse_date(
        item.get(
            "saved_date",
            "",
        )
    )

    completed_date = parse_date(
        item.get(
            "completed_date",
            "",
        )
    )

    if not saved_date or not completed_date:
        return None

    return (
        completed_date
        - saved_date
    ).days


def completion_rate(
    items,
):
    """消化率を計算する。"""

    if not items:
        return 0

    completed = len(
        [
            item
            for item in items
            if item.get(
                "status",
            )
            == "完了"
        ]
    )

    return (
        completed
        / len(items)
        * 100
    )


def favorite_rate(
    items,
):
    """お気に入り率を計算する。"""

    if not items:
        return 0

    favorite_count = len(
        [
            item
            for item in items
            if item.get(
                "favorite",
                False,
            )
        ]
    )

    return (
        favorite_count
        / len(items)
        * 100
    )


def average_completion_days(
    items,
):
    """平均消化日数を返す。"""

    values = [
        days_to_complete(
            item
        )
        for item in items
    ]

    values = [
        value
        for value in values
        if value is not None
        and value >= 0
    ]

    if not values:
        return 0

    return (
        sum(values)
        / len(values)
    )


def choose_next_item(
    items,
):
    """次に読む候補を選ぶ。"""

    candidates = [
        item
        for item in items
        if item.get(
            "status",
        )
        in [
            "未読",
            "読みかけ",
            "視聴中",
        ]
    ]

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            PRIORITY_ORDER.get(
                item.get(
                    "priority",
                    "中",
                ),
                99,
            ),
            item.get(
                "saved_date",
                "",
            ),
        )
    )

    return candidates[0]


# =========================================================
# データ操作
# =========================================================

def add_item(
    data,
    values,
):
    """新しい項目を追加する。"""

    item = {
        "id": create_id(),
        "title": values["title"],
        "content_type": (
            values["content_type"]
        ),
        "url": values["url"],
        "saved_date": (
            values["saved_date"]
        ),
        "priority": (
            values["priority"]
        ),
        "status": (
            values["status"]
        ),
        "favorite": False,
        "tags": values["tags"],
        "saved_reason": (
            values["saved_reason"]
        ),
        "memo": values["memo"],
        "summary": "",
        "learning": "",
        "action": "",
        "rating": 0,
        "completed_date": "",
        "created_at": now_text(),
        "updated_at": "",
    }

    data["items"].append(
        item,
    )

    save_data(data)


def update_item(
    data,
    item_id,
    values,
):
    """項目を更新する。"""

    item = get_item_by_id(
        data,
        item_id,
    )

    if not item:
        return

    previous_status = item.get(
        "status",
        "未読",
    )

    for key, value in values.items():
        item[key] = value

    if (
        item.get(
            "status",
        )
        == "完了"
        and previous_status
        != "完了"
        and not item.get(
            "completed_date",
            "",
        )
    ):
        item["completed_date"] = str(
            date.today()
        )

    elif item.get(
        "status",
    ) != "完了":
        item["completed_date"] = ""

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def mark_completed(
    data,
    item_id,
):
    """完了状態へ変更する。"""

    item = get_item_by_id(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = "完了"
    item["completed_date"] = str(
        date.today()
    )
    item["updated_at"] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    item_id,
):
    """お気に入りを切り替える。"""

    item = get_item_by_id(
        data,
        item_id,
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


def delete_item(
    data,
    item_id,
):
    """項目を削除する。"""

    data["items"] = [
        item
        for item in data[
            "items"
        ]
        if item.get(
            "id",
        ) != item_id
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
        background: rgba(70, 125, 255, 0.07);
        border: 1px solid rgba(70, 125, 255, 0.16);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(70, 125, 255, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(70, 125, 255, 0.18),
                rgba(135, 90, 255, 0.11)
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

items = data[
    "items"
]

all_tags = get_all_tags(
    items
)

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
        <h1>📚 あとで読む</h1>
        <p>
            気になった情報を保存して、
            「あとで読む」を「ちゃんと読んだ」に変えるアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

unread_items = [
    item
    for item in items
    if item.get(
        "status",
    )
    == "未読"
]

weekly_start = (
    date.today()
    - timedelta(
        days=6,
    )
)

weekly_added = [
    item
    for item in items
    if (
        parse_date(
            item.get(
                "saved_date",
                "",
            )
        )
        and weekly_start
        <= parse_date(
            item.get(
                "saved_date",
                "",
            )
        )
        <= date.today()
    )
]

monthly_completed = [
    item
    for item in items
    if item.get(
        "completed_date",
        "",
    ).startswith(
        current_month,
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

high_priority_unread = [
    item
    for item in items
    if (
        item.get(
            "status",
        )
        in [
            "未読",
            "読みかけ",
            "視聴中",
        ]
        and item.get(
            "priority",
        )
        in [
            "最優先",
            "高",
        ]
    )
]

type_counter = Counter(
    item.get(
        "content_type",
        "その他",
    )
    for item in items
)

top_type = (
    type_counter.most_common(
        1
    )[0][0]
    if type_counter
    else "なし"
)


metric_row1 = st.columns(4)

metric_row1[0].metric(
    "保存数",
    f"{len(items)}件",
)

metric_row1[1].metric(
    "未読",
    f"{len(unread_items)}件",
)

metric_row1[2].metric(
    "今週追加",
    f"{len(weekly_added)}件",
)

metric_row1[3].metric(
    "今月消化",
    f"{len(monthly_completed)}件",
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "お気に入り",
    f"{len(favorite_items)}件",
)

metric_row2[1].metric(
    "高優先度",
    f"{len(high_priority_unread)}件",
)

metric_row2[2].metric(
    "平均消化日数",
    (
        f"{average_completion_days(items):.1f}日"
        if average_completion_days(items) > 0
        else "未計算"
    ),
)

metric_row2[3].metric(
    "よく保存する種類",
    top_type,
)


# =========================================================
# 次に読む
# =========================================================

next_item = choose_next_item(
    items,
)

if next_item:
    st.divider()

    st.subheader(
        "📖 次はこれ！"
    )

    with st.container(
        border=True,
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
                f"{PRIORITY_ICONS.get(next_item.get('priority', ''), '')} "
                f"{next_item.get('title', '')}"
            )

            st.caption(
                f"{next_item.get('content_type', '')} ／ "
                f"優先度：{next_item.get('priority', '')}"
            )

            saved_days = days_since_saved(
                next_item,
            )

            if saved_days is not None:
                st.write(
                    f"保存から "
                    f"**{saved_days}日**"
                )

            if next_item.get(
                "saved_reason",
                "",
            ):
                st.info(
                    "保存した理由\n\n"
                    + next_item.get(
                        "saved_reason",
                        "",
                    )
                )

            if next_item.get(
                "url",
                "",
            ):
                st.write(
                    next_item.get(
                        "url",
                        "",
                    )
                )

        with column2:
            st.metric(
                "状態",
                f"{STATUS_ICONS.get(next_item.get('status', ''), '')} "
                f"{next_item.get('status', '')}",
            )


# =========================================================
# 積みすぎ警告
# =========================================================

if len(unread_items) >= 30:
    st.warning(
        f"未読が {len(unread_items)}件あります。"
        "新しく保存する前に、まず1件消化してみるのもおすすめです。"
    )

elif len(unread_items) >= 15:
    st.info(
        f"未読が {len(unread_items)}件あります。"
        "少しずつ消化していこう。"
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
        "➕ あとで読むに追加",
        "📚 保存一覧",
        "📝 読後メモ",
        "⭐ お気に入り",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 新規登録
# =========================================================

with add_tab:
    st.header(
        "➕ あとで読むに追加"
    )

    with st.form(
        "add_item_form",
        clear_on_submit=True,
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            title = st.text_input(
                "タイトル",
                placeholder=(
                    "例：React Hooksをわかりやすく解説した記事"
                ),
            )

            content_type = (
                st.selectbox(
                    "種類",
                    CONTENT_TYPES,
                )
            )

            url = st.text_input(
                "URL",
                placeholder=(
                    "https://..."
                ),
            )

            saved_date_input = (
                st.date_input(
                    "保存日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

        with column2:
            priority = st.selectbox(
                "優先度",
                PRIORITIES,
                index=2,
            )

            status = st.selectbox(
                "状態",
                STATUSES,
                index=0,
            )

            selected_tags = (
                st.multiselect(
                    "既存タグ",
                    all_tags,
                )
            )

            custom_tags_text = (
                st.text_input(
                    "新しいタグ",
                    placeholder=(
                        "React, JavaScript, 勉強"
                    ),
                )
            )

        saved_reason = st.text_area(
            "なぜ保存した？",
            placeholder=(
                "例：Reactのコードを読めるようになるため"
            ),
            height=100,
        )

        memo = st.text_area(
            "メモ",
            placeholder=(
                "気になった部分や、読む前に覚えておきたいこと"
            ),
            height=90,
        )

        submitted = (
            st.form_submit_button(
                "📚 あとで読むに保存",
                use_container_width=True,
            )
        )

        if submitted:
            custom_tags = [
                tag.strip()
                for tag in custom_tags_text.split(
                    ","
                )
                if tag.strip()
            ]

            final_tags = list(
                dict.fromkeys(
                    selected_tags
                    + custom_tags
                )
            )

            if not title.strip():
                st.error(
                    "タイトルを入力してください。"
                )

            else:
                duplicate = any(
                    item.get(
                        "title",
                        "",
                    ).strip().lower()
                    == title.strip().lower()
                    and (
                        not url.strip()
                        or item.get(
                            "url",
                            "",
                        ).strip()
                        == url.strip()
                    )
                    for item in items
                )

                if duplicate:
                    st.warning(
                        "似た内容がすでに保存されています。"
                    )

                else:
                    add_item(
                        data,
                        {
                            "title": (
                                title.strip()
                            ),
                            "content_type": (
                                content_type
                            ),
                            "url": (
                                url.strip()
                            ),
                            "saved_date": str(
                                saved_date_input
                            ),
                            "priority": (
                                priority
                            ),
                            "status": (
                                status
                            ),
                            "tags": final_tags,
                            "saved_reason": (
                                saved_reason.strip()
                            ),
                            "memo": (
                                memo.strip()
                            ),
                        },
                    )

                    st.success(
                        "あとで読むに追加しました！"
                    )

                    st.rerun()


# =========================================================
# 保存一覧
# =========================================================

with list_tab:
    st.header(
        "📚 保存一覧"
    )

    if not items:
        st.info(
            "保存された項目はありません。"
        )

    else:
        filter_columns = (
            st.columns(3)
        )

        with filter_columns[0]:
            keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "タイトル・メモ・学び"
                ),
            )

        with filter_columns[1]:
            type_filter = st.selectbox(
                "種類",
                [
                    "すべて"
                ]
                + CONTENT_TYPES,
            )

        with filter_columns[2]:
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて"
                    ]
                    + STATUSES,
                )
            )

        priority_filter = (
            st.multiselect(
                "優先度",
                PRIORITIES,
                default=PRIORITIES,
            )
        )

        tag_filter = st.selectbox(
            "タグ",
            [
                "すべて"
            ]
            + all_tags,
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "優先度＋古い順",
                "保存が新しい順",
                "保存が古い順",
                "評価が高い順",
                "タイトル順",
            ],
        )

        filtered_items = list(
            items,
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_items = [
                item
                for item in filtered_items
                if (
                    search_word
                    in item.get(
                        "title",
                        "",
                    ).lower()
                    or search_word
                    in item.get(
                        "memo",
                        "",
                    ).lower()
                    or search_word
                    in item.get(
                        "saved_reason",
                        "",
                    ).lower()
                    or search_word
                    in item.get(
                        "learning",
                        "",
                    ).lower()
                )
            ]

        if type_filter != "すべて":
            filtered_items = [
                item
                for item in filtered_items
                if item.get(
                    "content_type",
                )
                == type_filter
            ]

        if status_filter != "すべて":
            filtered_items = [
                item
                for item in filtered_items
                if item.get(
                    "status",
                )
                == status_filter
            ]

        filtered_items = [
            item
            for item in filtered_items
            if item.get(
                "priority",
                "中",
            )
            in priority_filter
        ]

        if tag_filter != "すべて":
            filtered_items = [
                item
                for item in filtered_items
                if tag_filter
                in item.get(
                    "tags",
                    [],
                )
            ]

        if sort_option == "優先度＋古い順":
            filtered_items.sort(
                key=lambda item: (
                    PRIORITY_ORDER.get(
                        item.get(
                            "priority",
                            "中",
                        ),
                        99,
                    ),
                    item.get(
                        "saved_date",
                        "",
                    ),
                )
            )

        elif sort_option == "保存が新しい順":
            filtered_items.sort(
                key=lambda item: (
                    item.get(
                        "saved_date",
                        "",
                    ),
                    item.get(
                        "created_at",
                        "",
                    ),
                ),
                reverse=True,
            )

        elif sort_option == "保存が古い順":
            filtered_items.sort(
                key=lambda item: (
                    item.get(
                        "saved_date",
                        "",
                    ),
                    item.get(
                        "created_at",
                        "",
                    ),
                )
            )

        elif sort_option == "評価が高い順":
            filtered_items.sort(
                key=lambda item: int(
                    item.get(
                        "rating",
                        0,
                    )
                ),
                reverse=True,
            )

        else:
            filtered_items.sort(
                key=lambda item: (
                    item.get(
                        "title",
                        "",
                    )
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_items)}件**"
        )

        for item in filtered_items:
            item_id = item["id"]

            with st.container(
                border=True,
            ):
                title_column, status_column = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with title_column:
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
                        f"{PRIORITY_ICONS.get(item.get('priority', ''), '')} "
                        f"{item.get('title', '')}"
                    )

                    st.caption(
                        f"{item.get('content_type', '')} ／ "
                        f"{format_date(item.get('saved_date', ''))}"
                    )

                with status_column:
                    status = item.get(
                        "status",
                        "未読",
                    )

                    st.metric(
                        "状態",
                        f"{STATUS_ICONS.get(status, '')} "
                        f"{status}",
                    )

                info_columns = st.columns(3)

                info_columns[0].metric(
                    "優先度",
                    item.get(
                        "priority",
                        "",
                    ),
                )

                saved_days = days_since_saved(
                    item,
                )

                info_columns[1].metric(
                    "保存から",
                    (
                        f"{saved_days}日"
                        if saved_days
                        is not None
                        else "不明"
                    ),
                )

                info_columns[2].metric(
                    "評価",
                    (
                        f"{item.get('rating', 0)}/5"
                        if int(
                            item.get(
                                "rating",
                                0,
                            )
                        )
                        > 0
                        else "未評価"
                    ),
                )

                if item.get(
                    "saved_reason",
                    "",
                ):
                    st.info(
                        "保存した理由\n\n"
                        + item.get(
                            "saved_reason",
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

                if item.get(
                    "tags",
                    [],
                ):
                    st.caption(
                        "🏷️ "
                        + " / ".join(
                            item.get(
                                "tags",
                                [],
                            )
                        )
                    )

                if item.get(
                    "url",
                    "",
                ):
                    st.write(
                        f"🔗 {item.get('url', '')}"
                    )

                if item.get(
                    "learning",
                    "",
                ):
                    st.success(
                        "💡 学んだこと\n\n"
                        + item.get(
                            "learning",
                            "",
                        )
                    )

                action_columns = st.columns(
                    2
                )

                with action_columns[0]:
                    if (
                        item.get(
                            "status",
                        )
                        != "完了"
                        and st.button(
                            "✅ 完了にする",
                            key=(
                                f"complete_"
                                f"{item_id}"
                            ),
                            use_container_width=True,
                        )
                    ):
                        mark_completed(
                            data,
                            item_id,
                        )

                        st.rerun()

                with action_columns[1]:
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

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = st.text_input(
                        "タイトル",
                        value=item.get(
                            "title",
                            "",
                        ),
                        key=(
                            f"edit_title_"
                            f"{item_id}"
                        ),
                    )

                    edit_url = st.text_input(
                        "URL",
                        value=item.get(
                            "url",
                            "",
                        ),
                        key=(
                            f"edit_url_"
                            f"{item_id}"
                        ),
                    )

                    edit_columns = (
                        st.columns(2)
                    )

                    with edit_columns[0]:
                        current_type = item.get(
                            "content_type",
                            "Web記事",
                        )

                        edit_type = st.selectbox(
                            "種類",
                            CONTENT_TYPES,
                            index=(
                                CONTENT_TYPES.index(
                                    current_type
                                )
                                if current_type
                                in CONTENT_TYPES
                                else 0
                            ),
                            key=(
                                f"edit_type_"
                                f"{item_id}"
                            ),
                        )

                        current_priority = (
                            item.get(
                                "priority",
                                "中",
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
                                    else 2
                                ),
                                key=(
                                    f"edit_priority_"
                                    f"{item_id}"
                                ),
                            )
                        )

                    with edit_columns[1]:
                        current_status = item.get(
                            "status",
                            "未読",
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
                                f"{item_id}"
                            ),
                        )

                        edit_date = st.date_input(
                            "保存日",
                            value=(
                                parse_date(
                                    item.get(
                                        "saved_date",
                                        "",
                                    )
                                )
                                or date.today()
                            ),
                            max_value=date.today(),
                            key=(
                                f"edit_date_"
                                f"{item_id}"
                            ),
                        )

                    edit_reason = st.text_area(
                        "保存した理由",
                        value=item.get(
                            "saved_reason",
                            "",
                        ),
                        key=(
                            f"edit_reason_"
                            f"{item_id}"
                        ),
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

                    edit_tags = st.text_input(
                        "タグ",
                        value=", ".join(
                            item.get(
                                "tags",
                                [],
                            )
                        ),
                        key=(
                            f"edit_tags_"
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
                        if not edit_title.strip():
                            st.error(
                                "タイトルを入力してください。"
                            )

                        else:
                            final_tags = [
                                tag.strip()
                                for tag in edit_tags.split(
                                    ","
                                )
                                if tag.strip()
                            ]

                            update_item(
                                data,
                                item_id,
                                {
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "url": (
                                        edit_url.strip()
                                    ),
                                    "content_type": (
                                        edit_type
                                    ),
                                    "priority": (
                                        edit_priority
                                    ),
                                    "status": (
                                        edit_status
                                    ),
                                    "saved_date": str(
                                        edit_date
                                    ),
                                    "saved_reason": (
                                        edit_reason.strip()
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                    "tags": list(
                                        dict.fromkeys(
                                            final_tags
                                        )
                                    ),
                                },
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 削除"
                ):
                    confirm_delete = st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_"
                            f"{item_id}"
                        ),
                    )

                    if st.button(
                        "この項目を削除",
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
# 読後メモ
# =========================================================

with review_tab:
    st.header(
        "📝 読後・視聴後メモ"
    )

    if not items:
        st.info(
            "保存した項目がありません。"
        )

    else:
        review_options = {
            (
                f"{item.get('title', '')}"
                f"｜{item.get('status', '')}"
            ): item["id"]
            for item in items
        }

        selected_review_label = (
            st.selectbox(
                "振り返る項目",
                list(
                    review_options.keys()
                ),
            )
        )

        review_item = get_item_by_id(
            data,
            review_options[
                selected_review_label
            ],
        )

        review_item_id = (
            review_item["id"]
        )

        with st.container(
            border=True,
        ):
            st.subheader(
                review_item.get(
                    "title",
                    "",
                )
            )

            if review_item.get(
                "saved_reason",
                "",
            ):
                st.info(
                    "保存した理由\n\n"
                    + review_item.get(
                        "saved_reason",
                        "",
                    )
                )

        with st.form(
            f"review_form_{review_item_id}",
        ):
            summary = st.text_area(
                "内容の要約",
                value=review_item.get(
                    "summary",
                    "",
                ),
                placeholder=(
                    "何についての記事・動画だったか"
                ),
                height=120,
            )

            learning = st.text_area(
                "学んだこと",
                value=review_item.get(
                    "learning",
                    "",
                ),
                placeholder=(
                    "一番大事だったことを残します。"
                ),
                height=120,
            )

            action = st.text_area(
                "実践したいこと",
                value=review_item.get(
                    "action",
                    "",
                ),
                placeholder=(
                    "学んだ内容を何に使うか"
                ),
                height=100,
            )

            rating = st.slider(
                "おすすめ度",
                min_value=1,
                max_value=5,
                value=(
                    int(
                        review_item.get(
                            "rating",
                            0,
                        )
                    )
                    or 3
                ),
            )

            mark_as_completed = st.checkbox(
                "保存と同時に完了にする",
                value=(
                    review_item.get(
                        "status",
                    )
                    == "完了"
                ),
            )

            review_submit = (
                st.form_submit_button(
                    "📝 読後メモを保存",
                    use_container_width=True,
                )
            )

            if review_submit:
                next_status = (
                    "完了"
                    if mark_as_completed
                    else review_item.get(
                        "status",
                        "未読",
                    )
                )

                update_item(
                    data,
                    review_item_id,
                    {
                        "summary": (
                            summary.strip()
                        ),
                        "learning": (
                            learning.strip()
                        ),
                        "action": (
                            action.strip()
                        ),
                        "rating": rating,
                        "status": (
                            next_status
                        ),
                    },
                )

                st.success(
                    "読後メモを保存しました！"
                )

                st.rerun()


# =========================================================
# お気に入り
# =========================================================

with favorite_tab:
    st.header(
        "⭐ お気に入り"
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
                item.get(
                    "saved_date",
                    "",
                )
            ),
            reverse=True,
        )

        for item in favorites:
            with st.container(
                border=True,
            ):
                st.markdown(
                    f"### ⭐ "
                    f"{item.get('title', '')}"
                )

                st.caption(
                    f"{item.get('content_type', '')} ／ "
                    f"{format_date(item.get('saved_date', ''))}"
                )

                if item.get(
                    "learning",
                    "",
                ):
                    st.success(
                        item.get(
                            "learning",
                            "",
                        )
                    )

                elif item.get(
                    "saved_reason",
                    "",
                ):
                    st.info(
                        item.get(
                            "saved_reason",
                            "",
                        )
                    )


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 あとで読む分析"
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
                    "タイトル": item.get(
                        "title",
                        "",
                    ),
                    "種類": item.get(
                        "content_type",
                        "",
                    ),
                    "状態": item.get(
                        "status",
                        "",
                    ),
                    "優先度": item.get(
                        "priority",
                        "",
                    ),
                    "保存月": item.get(
                        "saved_date",
                        "",
                    )[:7],
                    "完了月": item.get(
                        "completed_date",
                        "",
                    )[:7],
                    "保存から完了": (
                        days_to_complete(
                            item
                        )
                    ),
                    "評価": int(
                        item.get(
                            "rating",
                            0,
                        )
                    ),
                    "お気に入り": (
                        1
                        if item.get(
                            "favorite",
                            False,
                        )
                        else 0
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows,
        )

        summary_columns = st.columns(
            4
        )

        summary_columns[0].metric(
            "消化率",
            f"{completion_rate(items):.1f}%",
        )

        summary_columns[1].metric(
            "お気に入り率",
            f"{favorite_rate(items):.1f}%",
        )

        summary_columns[2].metric(
            "平均消化日数",
            (
                f"{average_completion_days(items):.1f}日"
                if average_completion_days(
                    items
                )
                > 0
                else "未計算"
            ),
        )

        summary_columns[3].metric(
            "未読残数",
            f"{len(unread_items)}件",
        )

        st.divider()

        st.subheader(
            "種類別保存数"
        )

        type_summary = (
            analysis_df.groupby(
                "種類",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "保存数"
                }
            )
            .sort_values(
                "保存数",
                ascending=False,
            )
        )

        st.bar_chart(
            type_summary.set_index(
                "種類"
            )[["保存数"]]
        )

        st.dataframe(
            type_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "状態別"
        )

        status_summary = (
            analysis_df.groupby(
                "状態",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False,
            )
        )

        st.bar_chart(
            status_summary.set_index(
                "状態"
            )[["件数"]]
        )

        st.dataframe(
            status_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "月別追加数"
        )

        monthly_saved = (
            analysis_df.groupby(
                "保存月",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "追加数"
                }
            )
            .sort_values(
                "保存月",
            )
        )

        st.line_chart(
            monthly_saved.set_index(
                "保存月"
            )[["追加数"]]
        )

        st.dataframe(
            monthly_saved,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "月別消化数"
        )

        completed_df = analysis_df[
            analysis_df[
                "完了月"
            ]
            != ""
        ]

        if completed_df.empty:
            st.info(
                "完了記録はまだありません。"
            )

        else:
            monthly_completed_df = (
                completed_df.groupby(
                    "完了月",
                    as_index=False,
                )
                .size()
                .rename(
                    columns={
                        "size": "完了数"
                    }
                )
                .sort_values(
                    "完了月",
                )
            )

            st.line_chart(
                monthly_completed_df.set_index(
                    "完了月"
                )[["完了数"]]
            )

            st.dataframe(
                monthly_completed_df,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "タグ別保存数"
        )

        tag_counter = Counter()

        for item in items:
            for tag in item.get(
                "tags",
                [],
            ):
                tag_counter[
                    tag
                ] += 1

        if not tag_counter:
            st.info(
                "タグはまだ登録されていません。"
            )

        else:
            tag_df = pd.DataFrame(
                [
                    {
                        "タグ": tag,
                        "保存数": count,
                    }
                    for tag, count
                    in tag_counter.most_common()
                ]
            )

            st.bar_chart(
                tag_df.set_index(
                    "タグ"
                )[["保存数"]]
            )

            st.dataframe(
                tag_df,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "保存から完了までの日数"
        )

        completion_days_df = (
            analysis_df.dropna(
                subset=[
                    "保存から完了"
                ]
            )
            .sort_values(
                "保存から完了"
            )
        )

        if completion_days_df.empty:
            st.info(
                "消化日数を計算できる項目がありません。"
            )

        else:
            st.dataframe(
                completion_days_df[
                    [
                        "タイトル",
                        "種類",
                        "保存から完了",
                        "評価",
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
            f"read_later_backup_"
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
                or "items"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "items"
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
        "保存した記事・動画・読後メモがすべて削除されます。"
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
    "保存するだけで終わらせず、ひとつずつ自分の知識に変えていこう。📚"
)
