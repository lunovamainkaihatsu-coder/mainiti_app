import copy
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
    page_title="おでかけ持ち物リスト",
    page_icon="🎒",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "packing_data.json"
)


CATEGORIES = [
    "子どもとの外出",
    "公園",
    "買い物",
    "病院",
    "保育園・学校",
    "日帰り旅行",
    "宿泊旅行",
    "帰省",
    "温泉",
    "仕事",
    "その他"
]


PRIORITIES = [
    "必須",
    "あると便利",
    "予備"
]


PRIORITY_ICONS = {
    "必須": "🔴",
    "あると便利": "🟡",
    "予備": "🔵"
}


# =====================================
# データ保存・読み込み
# =====================================

def create_empty_data():
    """初期データを作成する。"""

    return {
        "templates": [],
        "forgotten_records": []
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
                "保存データの形式が正しくありません。"
            )

        data.setdefault(
            "templates",
            []
        )

        data.setdefault(
            "forgotten_records",
            []
        )

        for template in data["templates"]:
            template.setdefault(
                "items",
                []
            )

            template.setdefault(
                "last_used",
                ""
            )

            for item in template["items"]:
                item.setdefault(
                    "checked",
                    False
                )

                item.setdefault(
                    "priority",
                    "必須"
                )

                item.setdefault(
                    "quantity",
                    1
                )

                item.setdefault(
                    "memo",
                    ""
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
# 補助関数
# =====================================

def create_id():
    """一意のIDを作成する。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def get_template_by_id(
    data,
    template_id
):
    """IDからテンプレートを取得する。"""

    for template in data["templates"]:
        if template.get("id") == template_id:
            return template

    return None


def get_item_by_id(
    template,
    item_id
):
    """IDから持ち物を取得する。"""

    for item in template.get(
        "items",
        []
    ):
        if item.get("id") == item_id:
            return item

    return None


def count_checked_items(
    template
):
    """チェック済み持ち物数を取得する。"""

    return len(
        [
            item
            for item in template.get(
                "items",
                []
            )
            if item.get(
                "checked",
                False
            )
        ]
    )


def count_unchecked_items(
    template
):
    """未チェック持ち物数を取得する。"""

    return len(
        [
            item
            for item in template.get(
                "items",
                []
            )
            if not item.get(
                "checked",
                False
            )
        ]
    )


def count_unchecked_required_items(
    template
):
    """未チェックの必須品数を取得する。"""

    return len(
        [
            item
            for item in template.get(
                "items",
                []
            )
            if (
                item.get(
                    "priority"
                ) == "必須"
                and not item.get(
                    "checked",
                    False
                )
            )
        ]
    )


def get_progress_rate(
    template
):
    """チェックの進捗率を取得する。"""

    items = template.get(
        "items",
        []
    )

    if not items:
        return 0.0

    checked_count = count_checked_items(
        template
    )

    return checked_count / len(
        items
    )


def parse_date_text(
    value
):
    """文字列をdate型に変換する。"""

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except (
        ValueError,
        TypeError
    ):
        return date.today()


# =====================================
# テンプレート管理
# =====================================

def add_template(
    data,
    name,
    category,
    destination,
    memo
):
    """テンプレートを登録する。"""

    template = {
        "id": create_id(),
        "name": name,
        "category": category,
        "destination": destination,
        "memo": memo,
        "items": [],
        "last_used": "",
        "created_at": now_text()
    }

    data["templates"].append(
        template
    )

    save_data(data)


def update_template(
    data,
    template_id,
    name,
    category,
    destination,
    memo
):
    """テンプレート情報を更新する。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    template["name"] = name
    template["category"] = category
    template["destination"] = destination
    template["memo"] = memo
    template["updated_at"] = now_text()

    save_data(data)


def delete_template(
    data,
    template_id
):
    """テンプレートと関連履歴を削除する。"""

    data["templates"] = [
        template
        for template in data["templates"]
        if template.get(
            "id"
        ) != template_id
    ]

    data["forgotten_records"] = [
        record
        for record in data["forgotten_records"]
        if record.get(
            "template_id"
        ) != template_id
    ]

    save_data(data)


def duplicate_template(
    data,
    template_id,
    new_name
):
    """テンプレートを複製する。"""

    original = get_template_by_id(
        data,
        template_id
    )

    if not original:
        return

    copied_template = copy.deepcopy(
        original
    )

    copied_template["id"] = create_id()
    copied_template["name"] = new_name
    copied_template["created_at"] = now_text()
    copied_template["updated_at"] = ""
    copied_template["last_used"] = ""

    for item in copied_template.get(
        "items",
        []
    ):
        item["id"] = create_id()
        item["checked"] = False
        item["created_at"] = now_text()

    data["templates"].append(
        copied_template
    )

    save_data(data)


# =====================================
# 持ち物管理
# =====================================

def add_item(
    data,
    template_id,
    name,
    priority,
    quantity,
    person,
    memo
):
    """テンプレートに持ち物を追加する。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    item = {
        "id": create_id(),
        "name": name,
        "priority": priority,
        "quantity": int(quantity),
        "person": person,
        "memo": memo,
        "checked": False,
        "created_at": now_text()
    }

    template["items"].append(
        item
    )

    save_data(data)


def update_item(
    data,
    template_id,
    item_id,
    name,
    priority,
    quantity,
    person,
    memo
):
    """持ち物を更新する。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    item = get_item_by_id(
        template,
        item_id
    )

    if not item:
        return

    item["name"] = name
    item["priority"] = priority
    item["quantity"] = int(quantity)
    item["person"] = person
    item["memo"] = memo
    item["updated_at"] = now_text()

    save_data(data)


def delete_item(
    data,
    template_id,
    item_id
):
    """持ち物を削除する。"""

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

    save_data(data)


def update_item_check(
    data,
    template_id,
    item_id,
    checked
):
    """持ち物のチェック状態を更新する。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    item = get_item_by_id(
        template,
        item_id
    )

    if not item:
        return

    item["checked"] = bool(
        checked
    )

    template["last_used"] = str(
        date.today()
    )

    save_data(data)


def reset_all_checks(
    data,
    template_id
):
    """すべてのチェックを外す。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    for item in template.get(
        "items",
        []
    ):
        item["checked"] = False

    save_data(data)


def check_all_items(
    data,
    template_id
):
    """すべての持ち物をチェック済みにする。"""

    template = get_template_by_id(
        data,
        template_id
    )

    if not template:
        return

    for item in template.get(
        "items",
        []
    ):
        item["checked"] = True

    template["last_used"] = str(
        date.today()
    )

    save_data(data)


# =====================================
# 忘れ物管理
# =====================================

def add_forgotten_record(
    data,
    template_id,
    item_name,
    forgotten_date,
    memo
):
    """忘れ物記録を追加する。"""

    template = get_template_by_id(
        data,
        template_id
    )

    record = {
        "id": create_id(),
        "template_id": template_id,
        "template_name": (
            template.get(
                "name",
                "不明なテンプレート"
            )
            if template
            else "不明なテンプレート"
        ),
        "item_name": item_name,
        "forgotten_date": str(
            forgotten_date
        ),
        "memo": memo,
        "created_at": now_text()
    }

    data["forgotten_records"].append(
        record
    )

    save_data(data)


def delete_forgotten_record(
    data,
    record_id
):
    """忘れ物記録を削除する。"""

    data["forgotten_records"] = [
        record
        for record in data[
            "forgotten_records"
        ]
        if record.get(
            "id"
        ) != record_id
    ]

    save_data(data)


def get_forgotten_count(
    data,
    item_name
):
    """持ち物名ごとの忘れた回数を取得する。"""

    normalized_name = item_name.strip().lower()

    return len(
        [
            record
            for record in data[
                "forgotten_records"
            ]
            if record.get(
                "item_name",
                ""
            ).strip().lower()
            == normalized_name
        ]
    )


# =====================================
# データ読み込み
# =====================================

data = load_data()

templates = data["templates"]
forgotten_records = data[
    "forgotten_records"
]


# =====================================
# タイトル
# =====================================

st.title(
    "🎒 おでかけ持ち物リスト"
)

st.caption(
    "行き先ごとの持ち物を登録して、"
    "出発前の忘れ物を防ぎます。"
)


# =====================================
# テンプレート選択
# =====================================

if templates:
    template_options = {
        template.get(
            "name",
            "名称未設定"
        ): template.get(
            "id",
            ""
        )
        for template in templates
    }

    selected_template_name = (
        st.selectbox(
            "🧳 使用するおでかけリスト",
            list(
                template_options.keys()
            )
        )
    )

    selected_template_id = (
        template_options[
            selected_template_name
        ]
    )

    selected_template = (
        get_template_by_id(
            data,
            selected_template_id
        )
    )

else:
    selected_template_name = ""
    selected_template_id = ""
    selected_template = None


# =====================================
# ダッシュボード
# =====================================

st.divider()

st.header(
    "📊 ダッシュボード"
)

total_templates = len(
    templates
)

total_items = sum(
    len(
        template.get(
            "items",
            []
        )
    )
    for template in templates
)

total_forgotten = len(
    forgotten_records
)

metric_col1, metric_col2, metric_col3, metric_col4 = (
    st.columns(4)
)

with metric_col1:
    st.metric(
        "テンプレート",
        f"{total_templates}件"
    )

with metric_col2:
    st.metric(
        "登録持ち物",
        f"{total_items}個"
    )

with metric_col3:
    if selected_template:
        unchecked_count = (
            count_unchecked_items(
                selected_template
            )
        )
    else:
        unchecked_count = 0

    st.metric(
        "現在の未チェック",
        f"{unchecked_count}個"
    )

with metric_col4:
    st.metric(
        "忘れ物記録",
        f"{total_forgotten}件"
    )


if not selected_template:
    st.info(
        "「テンプレート管理」から"
        "最初のおでかけリストを作成してください。"
    )

else:
    items = selected_template.get(
        "items",
        []
    )

    checked_count = count_checked_items(
        selected_template
    )

    unchecked_required = (
        count_unchecked_required_items(
            selected_template
        )
    )

    progress_rate = get_progress_rate(
        selected_template
    )

    with st.container(
        border=True
    ):
        title_col, progress_col = (
            st.columns([3, 1])
        )

        with title_col:
            st.subheader(
                f"🧳 {selected_template.get('name', '')}"
            )

            st.caption(
                f"{selected_template.get('category', '')}"
            )

            destination = (
                selected_template.get(
                    "destination",
                    ""
                )
            )

            if destination:
                st.write(
                    f"📍 行き先："
                    f"**{destination}**"
                )

            template_memo = (
                selected_template.get(
                    "memo",
                    ""
                )
            )

            if template_memo:
                st.write(
                    f"📝 {template_memo}"
                )

        with progress_col:
            st.metric(
                "準備状況",
                f"{checked_count}/{len(items)}"
            )

        st.progress(
            progress_rate
        )

        if not items:
            st.info(
                "持ち物がまだ登録されていません。"
            )

        elif unchecked_required > 0:
            st.error(
                f"必須品があと"
                f"{unchecked_required}個残っています！"
            )

        elif count_unchecked_items(
            selected_template
        ) > 0:
            st.warning(
                "必須品は準備できています。"
                "便利品・予備品を確認しましょう。"
            )

        else:
            st.success(
                "すべて準備できました！"
                "気をつけていってらっしゃい！🎉"
            )


# =====================================
# タブ
# =====================================

st.divider()

check_tab, item_tab, template_tab, forgotten_tab, analysis_tab = (
    st.tabs(
        [
            "✅ 出発前チェック",
            "➕ 持ち物管理",
            "🧳 テンプレート管理",
            "⚠️ 忘れ物履歴",
            "📈 集計"
        ]
    )
)


# =====================================
# 出発前チェック
# =====================================

with check_tab:
    st.header(
        "✅ 出発前チェック"
    )

    if not selected_template:
        st.info(
            "テンプレートを作成してください。"
        )

    elif not selected_template.get(
        "items",
        []
    ):
        st.info(
            "持ち物を登録してください。"
        )

    else:
        button_col1, button_col2 = (
            st.columns(2)
        )

        with button_col1:
            if st.button(
                "✅ すべてチェック",
                use_container_width=True
            ):
                check_all_items(
                    data,
                    selected_template_id
                )

                st.rerun()

        with button_col2:
            if st.button(
                "🔄 チェックをリセット",
                use_container_width=True
            ):
                reset_all_checks(
                    data,
                    selected_template_id
                )

                st.rerun()

        st.divider()

        priority_filter = (
            st.multiselect(
                "重要度で絞り込み",
                PRIORITIES,
                default=PRIORITIES
            )
        )

        show_unchecked_only = (
            st.checkbox(
                "未チェックのみ表示"
            )
        )

        sorted_items = sorted(
            selected_template.get(
                "items",
                []
            ),
            key=lambda item: (
                PRIORITIES.index(
                    item.get(
                        "priority",
                        "予備"
                    )
                ),
                item.get(
                    "name",
                    ""
                )
            )
        )

        display_items = [
            item
            for item in sorted_items
            if item.get(
                "priority",
                "必須"
            ) in priority_filter
        ]

        if show_unchecked_only:
            display_items = [
                item
                for item in display_items
                if not item.get(
                    "checked",
                    False
                )
            ]

        for item in display_items:
            item_id = item.get(
                "id",
                ""
            )

            item_name = item.get(
                "name",
                "名称未設定"
            )

            priority = item.get(
                "priority",
                "必須"
            )

            quantity = item.get(
                "quantity",
                1
            )

            forgotten_count = (
                get_forgotten_count(
                    data,
                    item_name
                )
            )

            with st.container(
                border=True
            ):
                check_col, info_col, count_col = (
                    st.columns(
                        [1, 5, 1]
                    )
                )

                with check_col:
                    new_checked = (
                        st.checkbox(
                            "準備済み",
                            value=item.get(
                                "checked",
                                False
                            ),
                            key=(
                                f"check_item_"
                                f"{item_id}"
                            ),
                            label_visibility=(
                                "collapsed"
                            )
                        )
                    )

                    if (
                        new_checked
                        != item.get(
                            "checked",
                            False
                        )
                    ):
                        update_item_check(
                            data,
                            selected_template_id,
                            item_id,
                            new_checked
                        )

                        st.rerun()

                with info_col:
                    display_name = (
                        f"{PRIORITY_ICONS.get(priority, '')} "
                        f"{item_name}"
                    )

                    if quantity > 1:
                        display_name += (
                            f" × {quantity}"
                        )

                    if item.get(
                        "checked",
                        False
                    ):
                        st.markdown(
                            f"~~**{display_name}**~~"
                        )
                    else:
                        st.markdown(
                            f"**{display_name}**"
                        )

                    item_person = item.get(
                        "person",
                        ""
                    )

                    if item_person:
                        st.caption(
                            f"担当：{item_person}"
                        )

                    item_memo = item.get(
                        "memo",
                        ""
                    )

                    if item_memo:
                        st.caption(
                            f"メモ：{item_memo}"
                        )

                    if forgotten_count > 0:
                        st.warning(
                            f"過去に"
                            f"{forgotten_count}回"
                            "忘れています。"
                        )

                with count_col:
                    st.caption(
                        priority
                    )

        if not display_items:
            st.success(
                "条件に該当する"
                "未チェック品はありません！"
            )


# =====================================
# 持ち物管理
# =====================================

with item_tab:
    st.header(
        "➕ 持ち物を登録"
    )

    if not selected_template:
        st.info(
            "先にテンプレートを作成してください。"
        )

    else:
        with st.form(
            "add_item_form",
            clear_on_submit=True
        ):
            item_col1, item_col2 = (
                st.columns(2)
            )

            with item_col1:
                new_item_name = (
                    st.text_input(
                        "持ち物名",
                        placeholder=(
                            "例：水筒"
                        )
                    )
                )

                new_item_priority = (
                    st.selectbox(
                        "重要度",
                        PRIORITIES
                    )
                )

                new_item_quantity = (
                    st.number_input(
                        "数量",
                        min_value=1,
                        value=1,
                        step=1
                    )
                )

            with item_col2:
                new_item_person = (
                    st.text_input(
                        "担当者",
                        placeholder=(
                            "例：自分、妻、娘"
                        )
                    )
                )

                new_item_memo = (
                    st.text_area(
                        "メモ",
                        placeholder=(
                            "例：冷たい飲み物を入れる"
                        )
                    )
                )

            item_submit = (
                st.form_submit_button(
                    "➕ 持ち物を追加",
                    use_container_width=True
                )
            )

            if item_submit:
                cleaned_item_name = (
                    new_item_name.strip()
                )

                duplicate_exists = any(
                    item.get(
                        "name",
                        ""
                    ).strip().lower()
                    == cleaned_item_name.lower()
                    for item in selected_template.get(
                        "items",
                        []
                    )
                )

                if not cleaned_item_name:
                    st.error(
                        "持ち物名を入力してください。"
                    )

                elif duplicate_exists:
                    st.warning(
                        "同じ持ち物が"
                        "すでに登録されています。"
                    )

                else:
                    add_item(
                        data=data,
                        template_id=(
                            selected_template_id
                        ),
                        name=cleaned_item_name,
                        priority=(
                            new_item_priority
                        ),
                        quantity=(
                            new_item_quantity
                        ),
                        person=(
                            new_item_person.strip()
                        ),
                        memo=(
                            new_item_memo.strip()
                        )
                    )

                    st.success(
                        f"「{cleaned_item_name}」を"
                        "追加しました！"
                    )

                    st.rerun()

        st.divider()

        st.header(
            "📋 登録済みの持ち物"
        )

        item_search = st.text_input(
            "🔍 持ち物を検索",
            placeholder=(
                "名前・担当者・メモ"
            )
        )

        managed_items = list(
            selected_template.get(
                "items",
                []
            )
        )

        if item_search:
            keyword = (
                item_search.strip().lower()
            )

            managed_items = [
                item
                for item in managed_items
                if (
                    keyword
                    in item.get(
                        "name",
                        ""
                    ).lower()
                    or keyword
                    in item.get(
                        "person",
                        ""
                    ).lower()
                    or keyword
                    in item.get(
                        "memo",
                        ""
                    ).lower()
                )
            ]

        if not managed_items:
            st.info(
                "登録された持ち物はありません。"
            )

        for item in managed_items:
            item_id = item.get(
                "id",
                ""
            )

            with st.container(
                border=True
            ):
                info_col, priority_col = (
                    st.columns([4, 1])
                )

                with info_col:
                    st.subheader(
                        f"{PRIORITY_ICONS.get(item.get('priority', ''), '')} "
                        f"{item.get('name', '')}"
                    )

                    st.caption(
                        f"数量："
                        f"{item.get('quantity', 1)}"
                    )

                    if item.get(
                        "person",
                        ""
                    ):
                        st.write(
                            f"👤 担当："
                            f"{item.get('person', '')}"
                        )

                    if item.get(
                        "memo",
                        ""
                    ):
                        st.write(
                            f"📝 {item.get('memo', '')}"
                        )

                with priority_col:
                    st.metric(
                        "重要度",
                        item.get(
                            "priority",
                            ""
                        )
                    )

                with st.expander(
                    "✏️ 持ち物を編集"
                ):
                    edit_item_name = (
                        st.text_input(
                            "持ち物名",
                            value=item.get(
                                "name",
                                ""
                            ),
                            key=(
                                f"edit_item_name_"
                                f"{item_id}"
                            )
                        )
                    )

                    current_priority = (
                        item.get(
                            "priority",
                            "必須"
                        )
                    )

                    priority_index = (
                        PRIORITIES.index(
                            current_priority
                        )
                        if current_priority
                        in PRIORITIES
                        else 0
                    )

                    edit_priority = (
                        st.selectbox(
                            "重要度",
                            PRIORITIES,
                            index=(
                                priority_index
                            ),
                            key=(
                                f"edit_priority_"
                                f"{item_id}"
                            )
                        )
                    )

                    edit_quantity = (
                        st.number_input(
                            "数量",
                            min_value=1,
                            value=int(
                                item.get(
                                    "quantity",
                                    1
                                )
                            ),
                            step=1,
                            key=(
                                f"edit_quantity_"
                                f"{item_id}"
                            )
                        )
                    )

                    edit_person = (
                        st.text_input(
                            "担当者",
                            value=item.get(
                                "person",
                                ""
                            ),
                            key=(
                                f"edit_person_"
                                f"{item_id}"
                            )
                        )
                    )

                    edit_item_memo = (
                        st.text_area(
                            "メモ",
                            value=item.get(
                                "memo",
                                ""
                            ),
                            key=(
                                f"edit_item_memo_"
                                f"{item_id}"
                            )
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_item_"
                            f"{item_id}"
                        ),
                        use_container_width=True
                    ):
                        cleaned_edit_name = (
                            edit_item_name.strip()
                        )

                        if not cleaned_edit_name:
                            st.error(
                                "持ち物名を入力してください。"
                            )

                        else:
                            update_item(
                                data=data,
                                template_id=(
                                    selected_template_id
                                ),
                                item_id=item_id,
                                name=(
                                    cleaned_edit_name
                                ),
                                priority=(
                                    edit_priority
                                ),
                                quantity=(
                                    edit_quantity
                                ),
                                person=(
                                    edit_person.strip()
                                ),
                                memo=(
                                    edit_item_memo.strip()
                                )
                            )

                            st.success(
                                "持ち物を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 持ち物を削除"
                ):
                    confirm_item_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_item_"
                                f"{item_id}"
                            )
                        )
                    )

                    if st.button(
                        "持ち物を削除",
                        key=(
                            f"delete_item_"
                            f"{item_id}"
                        ),
                        disabled=(
                            not confirm_item_delete
                        ),
                        use_container_width=True
                    ):
                        delete_item(
                            data,
                            selected_template_id,
                            item_id
                        )

                        st.rerun()


# =====================================
# テンプレート管理
# =====================================

with template_tab:
    st.header(
        "🧳 テンプレートを作成"
    )

    with st.form(
        "template_form",
        clear_on_submit=True
    ):
        template_col1, template_col2 = (
            st.columns(2)
        )

        with template_col1:
            template_name = (
                st.text_input(
                    "テンプレート名",
                    placeholder=(
                        "例：娘と公園"
                    )
                )
            )

            template_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES
                )
            )

        with template_col2:
            template_destination = (
                st.text_input(
                    "主な行き先",
                    placeholder=(
                        "例：近所の公園"
                    )
                )
            )

            template_memo = (
                st.text_area(
                    "メモ",
                    placeholder=(
                        "例：暑い日は帽子と水筒を忘れない"
                    )
                )
            )

        template_submit = (
            st.form_submit_button(
                "🧳 テンプレートを作成",
                use_container_width=True
            )
        )

        if template_submit:
            cleaned_template_name = (
                template_name.strip()
            )

            duplicate_exists = any(
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

            elif duplicate_exists:
                st.warning(
                    "同じ名前のテンプレートが"
                    "すでに存在します。"
                )

            else:
                add_template(
                    data=data,
                    name=(
                        cleaned_template_name
                    ),
                    category=(
                        template_category
                    ),
                    destination=(
                        template_destination.strip()
                    ),
                    memo=(
                        template_memo.strip()
                    )
                )

                st.success(
                    f"「{cleaned_template_name}」を"
                    "作成しました！"
                )

                st.rerun()

    st.divider()

    st.header(
        "📋 登録済みテンプレート"
    )

    if not templates:
        st.info(
            "登録されたテンプレートはありません。"
        )

    for template in templates:
        template_id = template.get(
            "id",
            ""
        )

        template_name_display = (
            template.get(
                "name",
                "名称未設定"
            )
        )

        item_count = len(
            template.get(
                "items",
                []
            )
        )

        with st.container(
            border=True
        ):
            template_info_col, template_metric_col = (
                st.columns([3, 1])
            )

            with template_info_col:
                st.subheader(
                    f"🧳 {template_name_display}"
                )

                st.caption(
                    template.get(
                        "category",
                        ""
                    )
                )

                if template.get(
                    "destination",
                    ""
                ):
                    st.write(
                        f"📍 "
                        f"{template.get('destination', '')}"
                    )

                if template.get(
                    "memo",
                    ""
                ):
                    st.write(
                        f"📝 "
                        f"{template.get('memo', '')}"
                    )

            with template_metric_col:
                st.metric(
                    "持ち物",
                    f"{item_count}個"
                )

            with st.expander(
                "📄 テンプレートを複製"
            ):
                duplicate_name = (
                    st.text_input(
                        "新しいテンプレート名",
                        value=(
                            f"{template_name_display}のコピー"
                        ),
                        key=(
                            f"duplicate_name_"
                            f"{template_id}"
                        )
                    )
                )

                if st.button(
                    "複製する",
                    key=(
                        f"duplicate_template_"
                        f"{template_id}"
                    ),
                    use_container_width=True
                ):
                    cleaned_duplicate_name = (
                        duplicate_name.strip()
                    )

                    if not cleaned_duplicate_name:
                        st.error(
                            "新しい名前を入力してください。"
                        )

                    else:
                        duplicate_template(
                            data,
                            template_id,
                            cleaned_duplicate_name
                        )

                        st.success(
                            "テンプレートを複製しました！"
                        )

                        st.rerun()

            with st.expander(
                "✏️ テンプレート情報を編集"
            ):
                edit_template_name = (
                    st.text_input(
                        "テンプレート名",
                        value=(
                            template_name_display
                        ),
                        key=(
                            f"edit_template_name_"
                            f"{template_id}"
                        )
                    )
                )

                current_category = (
                    template.get(
                        "category",
                        "その他"
                    )
                )

                category_index = (
                    CATEGORIES.index(
                        current_category
                    )
                    if current_category
                    in CATEGORIES
                    else 0
                )

                edit_template_category = (
                    st.selectbox(
                        "カテゴリー",
                        CATEGORIES,
                        index=(
                            category_index
                        ),
                        key=(
                            f"edit_template_category_"
                            f"{template_id}"
                        )
                    )
                )

                edit_destination = (
                    st.text_input(
                        "主な行き先",
                        value=template.get(
                            "destination",
                            ""
                        ),
                        key=(
                            f"edit_destination_"
                            f"{template_id}"
                        )
                    )
                )

                edit_template_memo = (
                    st.text_area(
                        "メモ",
                        value=template.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_template_memo_"
                            f"{template_id}"
                        )
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_template_"
                        f"{template_id}"
                    ),
                    use_container_width=True
                ):
                    cleaned_edit_template_name = (
                        edit_template_name.strip()
                    )

                    if not cleaned_edit_template_name:
                        st.error(
                            "テンプレート名を入力してください。"
                        )

                    else:
                        update_template(
                            data=data,
                            template_id=template_id,
                            name=(
                                cleaned_edit_template_name
                            ),
                            category=(
                                edit_template_category
                            ),
                            destination=(
                                edit_destination.strip()
                            ),
                            memo=(
                                edit_template_memo.strip()
                            )
                        )

                        st.success(
                            "テンプレートを更新しました！"
                        )

                        st.rerun()

            with st.expander(
                "🗑️ テンプレートを削除"
            ):
                st.warning(
                    "登録された持ち物と"
                    "関連する忘れ物履歴も削除されます。"
                )

                confirm_template_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_template_delete_"
                            f"{template_id}"
                        )
                    )
                )

                if st.button(
                    "テンプレートを削除",
                    key=(
                        f"delete_template_"
                        f"{template_id}"
                    ),
                    disabled=(
                        not confirm_template_delete
                    ),
                    use_container_width=True
                ):
                    delete_template(
                        data,
                        template_id
                    )

                    st.rerun()


# =====================================
# 忘れ物履歴
# =====================================

with forgotten_tab:
    st.header(
        "⚠️ 忘れ物を記録"
    )

    if not templates:
        st.info(
            "先にテンプレートを作成してください。"
        )

    else:
        forgotten_template_options = {
            template.get(
                "name",
                "名称未設定"
            ): template.get(
                "id",
                ""
            )
            for template in templates
        }

        with st.form(
            "forgotten_form",
            clear_on_submit=True
        ):
            forgotten_col1, forgotten_col2 = (
                st.columns(2)
            )

            with forgotten_col1:
                forgotten_template_name = (
                    st.selectbox(
                        "おでかけリスト",
                        list(
                            forgotten_template_options.keys()
                        )
                    )
                )

                forgotten_template_id = (
                    forgotten_template_options[
                        forgotten_template_name
                    ]
                )

                forgotten_template = (
                    get_template_by_id(
                        data,
                        forgotten_template_id
                    )
                )

                template_item_names = [
                    item.get(
                        "name",
                        ""
                    )
                    for item in forgotten_template.get(
                        "items",
                        []
                    )
                ]

                item_input_method = (
                    st.radio(
                        "持ち物の選び方",
                        [
                            "登録済みから選ぶ",
                            "自由入力"
                        ],
                        horizontal=True
                    )
                )

                if (
                    item_input_method
                    == "登録済みから選ぶ"
                    and template_item_names
                ):
                    forgotten_item_name = (
                        st.selectbox(
                            "忘れた持ち物",
                            template_item_names
                        )
                    )

                else:
                    forgotten_item_name = (
                        st.text_input(
                            "忘れた持ち物",
                            placeholder=(
                                "例：帽子"
                            )
                        )
                    )

            with forgotten_col2:
                forgotten_date = (
                    st.date_input(
                        "忘れた日",
                        value=date.today()
                    )
                )

                forgotten_memo = (
                    st.text_area(
                        "状況・メモ",
                        placeholder=(
                            "例：玄関に置いたまま出発した"
                        )
                    )
                )

            forgotten_submit = (
                st.form_submit_button(
                    "⚠️ 忘れ物を記録",
                    use_container_width=True
                )
            )

            if forgotten_submit:
                cleaned_forgotten_name = (
                    forgotten_item_name.strip()
                )

                if not cleaned_forgotten_name:
                    st.error(
                        "忘れた持ち物を入力してください。"
                    )

                else:
                    add_forgotten_record(
                        data=data,
                        template_id=(
                            forgotten_template_id
                        ),
                        item_name=(
                            cleaned_forgotten_name
                        ),
                        forgotten_date=(
                            forgotten_date
                        ),
                        memo=(
                            forgotten_memo.strip()
                        )
                    )

                    st.success(
                        "忘れ物を記録しました。"
                        "次回は注意表示されます！"
                    )

                    st.rerun()

    st.divider()

    st.header(
        "📋 忘れ物履歴"
    )

    if not forgotten_records:
        st.info(
            "忘れ物の記録はありません。"
        )

    else:
        forgotten_search = (
            st.text_input(
                "🔍 忘れ物履歴を検索",
                placeholder=(
                    "持ち物・テンプレート・メモ"
                )
            )
        )

        filtered_forgotten = list(
            forgotten_records
        )

        if forgotten_search:
            keyword = (
                forgotten_search.strip().lower()
            )

            filtered_forgotten = [
                record
                for record in filtered_forgotten
                if (
                    keyword
                    in record.get(
                        "item_name",
                        ""
                    ).lower()
                    or keyword
                    in record.get(
                        "template_name",
                        ""
                    ).lower()
                    or keyword
                    in record.get(
                        "memo",
                        ""
                    ).lower()
                )
            ]

        filtered_forgotten = sorted(
            filtered_forgotten,
            key=lambda record: (
                record.get(
                    "forgotten_date",
                    ""
                ),
                record.get(
                    "created_at",
                    ""
                )
            ),
            reverse=True
        )

        for record in filtered_forgotten:
            record_id = record.get(
                "id",
                ""
            )

            with st.container(
                border=True
            ):
                forgotten_info_col, forgotten_count_col = (
                    st.columns([4, 1])
                )

                with forgotten_info_col:
                    st.subheader(
                        f"⚠️ "
                        f"{record.get('item_name', '')}"
                    )

                    st.write(
                        f"🧳 "
                        f"{record.get('template_name', '')}"
                    )

                    st.caption(
                        f"忘れた日："
                        f"{record.get('forgotten_date', '')}"
                    )

                    if record.get(
                        "memo",
                        ""
                    ):
                        st.write(
                            f"📝 "
                            f"{record.get('memo', '')}"
                        )

                with forgotten_count_col:
                    st.metric(
                        "忘れた回数",
                        get_forgotten_count(
                            data,
                            record.get(
                                "item_name",
                                ""
                            )
                        )
                    )

                if st.button(
                    "この履歴を削除",
                    key=(
                        f"delete_forgotten_"
                        f"{record_id}"
                    )
                ):
                    delete_forgotten_record(
                        data,
                        record_id
                    )

                    st.rerun()


# =====================================
# 集計
# =====================================

with analysis_tab:
    st.header(
        "📈 持ち物・忘れ物集計"
    )

    if not templates:
        st.info(
            "集計するデータがありません。"
        )

    else:
        template_rows = []

        for template in templates:
            template_rows.append(
                {
                    "テンプレート": template.get(
                        "name",
                        ""
                    ),
                    "カテゴリー": template.get(
                        "category",
                        ""
                    ),
                    "持ち物数": len(
                        template.get(
                            "items",
                            []
                        )
                    ),
                    "必須品数": len(
                        [
                            item
                            for item in template.get(
                                "items",
                                []
                            )
                            if item.get(
                                "priority"
                            ) == "必須"
                        ]
                    ),
                    "最終使用日": template.get(
                        "last_used",
                        ""
                    )
                }
            )

        template_df = pd.DataFrame(
            template_rows
        )

        st.subheader(
            "🧳 テンプレート別持ち物数"
        )

        if not template_df.empty:
            st.bar_chart(
                template_df.set_index(
                    "テンプレート"
                )[["持ち物数"]]
            )

            st.dataframe(
                template_df,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "⚠️ よく忘れる持ち物"
        )

        if not forgotten_records:
            st.info(
                "忘れ物記録がまだありません。"
            )

        else:
            forgotten_df = pd.DataFrame(
                [
                    {
                        "持ち物": record.get(
                            "item_name",
                            ""
                        ),
                        "テンプレート": record.get(
                            "template_name",
                            ""
                        ),
                        "忘れた日": record.get(
                            "forgotten_date",
                            ""
                        )
                    }
                    for record in forgotten_records
                ]
            )

            forgotten_summary = (
                forgotten_df.groupby(
                    "持ち物",
                    as_index=False
                )
                .size()
                .rename(
                    columns={
                        "size": "忘れた回数"
                    }
                )
                .sort_values(
                    "忘れた回数",
                    ascending=False
                )
            )

            st.bar_chart(
                forgotten_summary.set_index(
                    "持ち物"
                )[["忘れた回数"]]
            )

            st.dataframe(
                forgotten_summary,
                use_container_width=True,
                hide_index=True
            )


st.divider()

st.success(
    "出発前にチェックして、"
    "忘れ物のないおでかけにしよう！🎒"
)
