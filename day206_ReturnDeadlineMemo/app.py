import json
import os
import uuid
from datetime import date, datetime, timedelta

import streamlit as st


# =====================================
# ページ設定
# =====================================

st.set_page_config(
    page_title="返却期限メモ",
    page_icon="📚",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "borrowed_items.json"
)


CATEGORIES = [
    "本",
    "DVD・ゲーム",
    "レンタル品",
    "友人・家族",
    "会社・学校",
    "その他"
]


# =====================================
# データ保存・読み込み
# =====================================

def save_items(items):
    """借りたもののデータをJSONへ保存する。"""

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
            items,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_items():
    """JSONから借りたもののデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):
        save_items([])
        return []

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    save_items([])
    return []


# =====================================
# 登録・更新・削除
# =====================================

def add_item(
    items,
    item_name,
    lender,
    category,
    borrowed_date,
    return_deadline,
    memo
):
    """借りたものを新しく登録する。"""

    new_item = {
        "id": str(uuid.uuid4()),
        "item_name": item_name,
        "lender": lender,
        "category": category,
        "borrowed_date": str(borrowed_date),
        "return_deadline": str(return_deadline),
        "memo": memo,
        "returned": False,
        "returned_date": "",
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    items.append(new_item)
    save_items(items)


def update_return_status(
    items,
    item_id,
    returned
):
    """返却済み状態を更新する。"""

    for item in items:
        if item.get("id") == item_id:
            item["returned"] = returned

            if returned:
                item["returned_date"] = str(
                    date.today()
                )

            else:
                item["returned_date"] = ""

            break

    save_items(items)


def delete_item(
    items,
    item_id
):
    """指定したデータを削除する。"""

    updated_items = [
        item
        for item in items
        if item.get("id") != item_id
    ]

    save_items(updated_items)


# =====================================
# 日付処理
# =====================================

def parse_date(date_text):
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
        return None


def get_remaining_days(item):
    """返却期限までの残り日数を返す。"""

    deadline = parse_date(
        item.get(
            "return_deadline",
            ""
        )
    )

    if deadline is None:
        return 99999

    return (
        deadline - date.today()
    ).days


def format_japanese_date(date_value):
    """日付を日本語形式に変換する。"""

    if date_value is None:
        return "日付不明"

    return date_value.strftime(
        "%Y年%m月%d日"
    )


def get_deadline_text(remaining_days):
    """残り日数に応じた表示文を返す。"""

    if remaining_days > 7:
        return f"あと{remaining_days}日"

    if remaining_days > 1:
        return f"あと{remaining_days}日"

    if remaining_days == 1:
        return "明日まで"

    if remaining_days == 0:
        return "今日が期限"

    return f"{abs(remaining_days)}日超過"


def get_category_icon(category):
    """カテゴリーに合ったアイコンを返す。"""

    icons = {
        "本": "📚",
        "DVD・ゲーム": "🎮",
        "レンタル品": "📦",
        "友人・家族": "👥",
        "会社・学校": "🏢",
        "その他": "📝"
    }

    return icons.get(
        category,
        "📝"
    )


# =====================================
# データ読み込み
# =====================================

items = load_items()


# =====================================
# タイトル
# =====================================

st.title("📚 返却期限メモ")

st.caption(
    "借りたものと返却期限をまとめて管理し、"
    "返し忘れを防ぎます。"
)


# =====================================
# 集計
# =====================================

unreturned_items = [
    item
    for item in items
    if not item.get(
        "returned",
        False
    )
]

returned_items = [
    item
    for item in items
    if item.get(
        "returned",
        False
    )
]

near_deadline_items = [
    item
    for item in unreturned_items
    if 0 <= get_remaining_days(item) <= 3
]

overdue_items = [
    item
    for item in unreturned_items
    if get_remaining_days(item) < 0
]


metric_col1, metric_col2, metric_col3, metric_col4 = (
    st.columns(4)
)

with metric_col1:
    st.metric(
        "📦 未返却",
        f"{len(unreturned_items)}件"
    )

with metric_col2:
    st.metric(
        "⚠️ 3日以内",
        f"{len(near_deadline_items)}件"
    )

with metric_col3:
    st.metric(
        "🚨 期限超過",
        f"{len(overdue_items)}件"
    )

with metric_col4:
    st.metric(
        "✅ 返却済み",
        f"{len(returned_items)}件"
    )


st.divider()


# =====================================
# 最も期限が近いもの
# =====================================

st.header("⏰ 次の返却期限")

sorted_unreturned_items = sorted(
    unreturned_items,
    key=lambda item: get_remaining_days(
        item
    )
)

if not sorted_unreturned_items:
    st.success(
        "現在、未返却のものはありません！"
    )

else:
    nearest_item = sorted_unreturned_items[0]

    nearest_days = get_remaining_days(
        nearest_item
    )

    nearest_deadline = parse_date(
        nearest_item.get(
            "return_deadline",
            ""
        )
    )

    nearest_category = nearest_item.get(
        "category",
        "その他"
    )

    nearest_icon = get_category_icon(
        nearest_category
    )

    with st.container(border=True):
        nearest_col1, nearest_col2 = (
            st.columns([3, 1])
        )

        with nearest_col1:
            st.subheader(
                f"{nearest_icon} "
                f"{nearest_item.get('item_name', '')}"
            )

            st.write(
                f"借りた相手・場所："
                f"**{nearest_item.get('lender', '')}**"
            )

            st.caption(
                f"返却期限："
                f"{format_japanese_date(nearest_deadline)}"
            )

        with nearest_col2:
            st.metric(
                "返却まで",
                get_deadline_text(
                    nearest_days
                )
            )

        if nearest_days < 0:
            st.error(
                "返却期限を過ぎています。"
                "できるだけ早く返却しましょう。"
            )

        elif nearest_days == 0:
            st.error(
                "今日が返却期限です！"
            )

        elif nearest_days <= 3:
            st.warning(
                "返却期限が近づいています。"
            )

        elif nearest_days <= 7:
            st.info(
                "一週間以内に返却期限です。"
            )

        memo = nearest_item.get(
            "memo",
            ""
        )

        if memo:
            st.write(
                f"📝 {memo}"
            )


st.divider()


# =====================================
# タブ
# =====================================

register_tab, list_tab, history_tab = st.tabs(
    [
        "➕ 登録",
        "📋 未返却一覧",
        "✅ 返却履歴"
    ]
)


# =====================================
# 登録タブ
# =====================================

with register_tab:
    st.header("➕ 借りたものを登録")

    with st.form(
        "borrowed_item_form",
        clear_on_submit=True
    ):
        form_col1, form_col2 = (
            st.columns(2)
        )

        with form_col1:
            item_name = st.text_input(
                "借りたもの",
                placeholder=(
                    "例：図書館の本"
                )
            )

            lender = st.text_input(
                "借りた相手・場所",
                placeholder=(
                    "例：静岡市立図書館"
                )
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES
            )

        with form_col2:
            borrowed_date = st.date_input(
                "借りた日",
                value=date.today()
            )

            return_deadline = st.date_input(
                "返却期限",
                value=(
                    date.today()
                    + timedelta(days=14)
                )
            )

            memo = st.text_area(
                "メモ",
                placeholder=(
                    "例：延長は1回まで"
                )
            )

        submitted = st.form_submit_button(
            "📚 登録する",
            use_container_width=True
        )

        if submitted:
            cleaned_item_name = (
                item_name.strip()
            )

            cleaned_lender = lender.strip()

            if not cleaned_item_name:
                st.error(
                    "借りたものを入力してください。"
                )

            elif not cleaned_lender:
                st.error(
                    "借りた相手や場所を"
                    "入力してください。"
                )

            elif return_deadline < borrowed_date:
                st.error(
                    "返却期限は借りた日以降に"
                    "設定してください。"
                )

            else:
                add_item(
                    items=items,
                    item_name=cleaned_item_name,
                    lender=cleaned_lender,
                    category=category,
                    borrowed_date=borrowed_date,
                    return_deadline=return_deadline,
                    memo=memo.strip()
                )

                st.success(
                    f"「{cleaned_item_name}」を"
                    "登録しました！"
                )

                st.rerun()


# =====================================
# 未返却一覧タブ
# =====================================

with list_tab:
    st.header("📋 未返却一覧")

    if not unreturned_items:
        st.success(
            "未返却のものはありません！"
        )

    else:
        filter_col1, filter_col2 = (
            st.columns(2)
        )

        with filter_col1:
            search_word = st.text_input(
                "🔍 検索",
                placeholder=(
                    "名前、相手、場所、メモ"
                )
            )

        with filter_col2:
            category_filter = st.selectbox(
                "カテゴリー",
                [
                    "すべて"
                ] + CATEGORIES,
                key="unreturned_category"
            )

        deadline_filter = st.radio(
            "期限で絞り込み",
            [
                "すべて",
                "3日以内",
                "7日以内",
                "期限超過"
            ],
            horizontal=True
        )

        sort_order = st.selectbox(
            "並び順",
            [
                "返却期限が近い順",
                "返却期限が遠い順",
                "登録が新しい順"
            ]
        )

        filtered_items = list(
            unreturned_items
        )

        if search_word:
            keyword = (
                search_word.strip().lower()
            )

            filtered_items = [
                item
                for item in filtered_items
                if keyword
                in item.get(
                    "item_name",
                    ""
                ).lower()
                or keyword
                in item.get(
                    "lender",
                    ""
                ).lower()
                or keyword
                in item.get(
                    "memo",
                    ""
                ).lower()
            ]

        if category_filter != "すべて":
            filtered_items = [
                item
                for item in filtered_items
                if item.get(
                    "category"
                ) == category_filter
            ]

        if deadline_filter == "3日以内":
            filtered_items = [
                item
                for item in filtered_items
                if 0
                <= get_remaining_days(item)
                <= 3
            ]

        elif deadline_filter == "7日以内":
            filtered_items = [
                item
                for item in filtered_items
                if 0
                <= get_remaining_days(item)
                <= 7
            ]

        elif deadline_filter == "期限超過":
            filtered_items = [
                item
                for item in filtered_items
                if get_remaining_days(item) < 0
            ]

        if sort_order == "返却期限が近い順":
            filtered_items = sorted(
                filtered_items,
                key=get_remaining_days
            )

        elif sort_order == "返却期限が遠い順":
            filtered_items = sorted(
                filtered_items,
                key=get_remaining_days,
                reverse=True
            )

        else:
            filtered_items = sorted(
                filtered_items,
                key=lambda item: item.get(
                    "created_at",
                    ""
                ),
                reverse=True
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_items)}件**"
        )

        if not filtered_items:
            st.info(
                "条件に一致するものは"
                "ありません。"
            )

        for item in filtered_items:
            item_id = item.get(
                "id",
                ""
            )

            item_name = item.get(
                "item_name",
                "名称未設定"
            )

            lender = item.get(
                "lender",
                "不明"
            )

            category = item.get(
                "category",
                "その他"
            )

            icon = get_category_icon(
                category
            )

            deadline = parse_date(
                item.get(
                    "return_deadline",
                    ""
                )
            )

            borrowed_date = parse_date(
                item.get(
                    "borrowed_date",
                    ""
                )
            )

            remaining_days = get_remaining_days(
                item
            )

            with st.container(border=True):
                item_col1, item_col2 = (
                    st.columns([3, 1])
                )

                with item_col1:
                    st.subheader(
                        f"{icon} {item_name}"
                    )

                    st.caption(
                        f"{category} ／ "
                        f"{lender}"
                    )

                with item_col2:
                    st.metric(
                        "返却まで",
                        get_deadline_text(
                            remaining_days
                        )
                    )

                detail_col1, detail_col2 = (
                    st.columns(2)
                )

                with detail_col1:
                    st.write(
                        "**借りた日**"
                    )

                    st.write(
                        format_japanese_date(
                            borrowed_date
                        )
                    )

                with detail_col2:
                    st.write(
                        "**返却期限**"
                    )

                    st.write(
                        format_japanese_date(
                            deadline
                        )
                    )

                if remaining_days < 0:
                    st.error(
                        f"返却期限を"
                        f"{abs(remaining_days)}日"
                        "過ぎています。"
                    )

                elif remaining_days == 0:
                    st.error(
                        "今日が返却期限です！"
                    )

                elif remaining_days <= 3:
                    st.warning(
                        "返却期限が迫っています。"
                    )

                elif remaining_days <= 7:
                    st.info(
                        "一週間以内に返却期限です。"
                    )

                memo = item.get(
                    "memo",
                    ""
                )

                if memo:
                    st.write(
                        f"📝 {memo}"
                    )

                returned = st.checkbox(
                    "✅ 返却済みにする",
                    value=False,
                    key=(
                        f"returned_"
                        f"{item_id}"
                    )
                )

                if returned:
                    update_return_status(
                        items,
                        item_id,
                        True
                    )

                    st.success(
                        f"「{item_name}」を"
                        "返却済みにしました！"
                    )

                    st.rerun()

                with st.expander(
                    "🗑️ このデータを削除"
                ):
                    st.warning(
                        "削除したデータは"
                        "元に戻せません。"
                    )

                    confirm_delete = st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_"
                            f"{item_id}"
                        )
                    )

                    if st.button(
                        "削除する",
                        key=(
                            f"delete_item_"
                            f"{item_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_item(
                            items,
                            item_id
                        )

                        st.rerun()


# =====================================
# 返却履歴タブ
# =====================================

with history_tab:
    st.header("✅ 返却履歴")

    if not returned_items:
        st.info(
            "返却済みの履歴は"
            "まだありません。"
        )

    else:
        history_search = st.text_input(
            "🔍 履歴を検索",
            placeholder=(
                "名前、相手、場所"
            )
        )

        history_category = st.selectbox(
            "カテゴリーで絞り込み",
            [
                "すべて"
            ] + CATEGORIES,
            key="history_category"
        )

        filtered_history = list(
            returned_items
        )

        if history_search:
            keyword = (
                history_search.strip().lower()
            )

            filtered_history = [
                item
                for item in filtered_history
                if keyword
                in item.get(
                    "item_name",
                    ""
                ).lower()
                or keyword
                in item.get(
                    "lender",
                    ""
                ).lower()
            ]

        if history_category != "すべて":
            filtered_history = [
                item
                for item in filtered_history
                if item.get(
                    "category"
                ) == history_category
            ]

        filtered_history = sorted(
            filtered_history,
            key=lambda item: item.get(
                "returned_date",
                ""
            ),
            reverse=True
        )

        st.write(
            f"表示件数："
            f"**{len(filtered_history)}件**"
        )

        for item in filtered_history:
            item_id = item.get(
                "id",
                ""
            )

            category = item.get(
                "category",
                "その他"
            )

            icon = get_category_icon(
                category
            )

            with st.container(border=True):
                history_col1, history_col2 = (
                    st.columns([3, 1])
                )

                with history_col1:
                    st.subheader(
                        f"{icon} "
                        f"{item.get('item_name', '')}"
                    )

                    st.caption(
                        f"{item.get('lender', '')} "
                        f"／ {category}"
                    )

                with history_col2:
                    st.metric(
                        "状態",
                        "返却済み"
                    )

                st.write(
                    f"返却期限："
                    f"{item.get('return_deadline', '')}"
                )

                st.write(
                    f"返却日："
                    f"{item.get('returned_date', '')}"
                )

                memo = item.get(
                    "memo",
                    ""
                )

                if memo:
                    st.write(
                        f"📝 {memo}"
                    )

                restore_col, delete_col = (
                    st.columns(2)
                )

                with restore_col:
                    if st.button(
                        "↩️ 未返却に戻す",
                        key=(
                            f"restore_"
                            f"{item_id}"
                        ),
                        use_container_width=True
                    ):
                        update_return_status(
                            items,
                            item_id,
                            False
                        )

                        st.rerun()

                with delete_col:
                    if st.button(
                        "🗑️ 履歴を削除",
                        key=(
                            f"delete_history_"
                            f"{item_id}"
                        ),
                        use_container_width=True
                    ):
                        delete_item(
                            items,
                            item_id
                        )

                        st.rerun()


st.divider()

st.success(
    "返却期限を見える化して、"
    "忘れ物や延滞を防ごう！📚"
)
