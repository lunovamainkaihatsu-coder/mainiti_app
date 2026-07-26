import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =====================================
# ページ設定
# =====================================

st.set_page_config(
    page_title="やりたいこと100リスト",
    page_icon="✨",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "dream_data.json"
)


CATEGORIES = [
    "仕事・夢",
    "家族",
    "旅行",
    "健康",
    "学び",
    "趣味",
    "お金",
    "人間関係",
    "挑戦",
    "暮らし",
    "その他"
]


PRIORITIES = [
    "最重要",
    "高",
    "中",
    "低",
    "いつか"
]


PRIORITY_ICONS = {
    "最重要": "🔥",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵",
    "いつか": "⚪"
}


PRIORITY_ORDER = {
    "最重要": 0,
    "高": 1,
    "中": 2,
    "低": 3,
    "いつか": 4
}


STATUS_OPTIONS = [
    "未着手",
    "進行中",
    "一時停止",
    "達成"
]


STATUS_ICONS = {
    "未着手": "⚪",
    "進行中": "🚀",
    "一時停止": "⏸️",
    "達成": "🎉"
}


# =====================================
# データ保存・読み込み
# =====================================

def create_empty_data():
    """初期データを作成する。"""

    return {
        "dreams": []
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
            "dreams",
            []
        )

        for dream in data["dreams"]:
            dream.setdefault(
                "status",
                "未着手"
            )

            dream.setdefault(
                "progress",
                0
            )

            dream.setdefault(
                "target_date",
                ""
            )

            dream.setdefault(
                "completed_date",
                ""
            )

            dream.setdefault(
                "reason",
                ""
            )

            dream.setdefault(
                "next_action",
                ""
            )

            dream.setdefault(
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

    return str(
        uuid.uuid4()
    )


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def parse_date_text(
    date_text
):
    """日付文字列をdate型へ変換する。"""

    if not date_text:
        return None

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


def get_dream_by_id(
    data,
    dream_id
):
    """IDからやりたいことを取得する。"""

    for dream in data["dreams"]:
        if dream.get(
            "id"
        ) == dream_id:
            return dream

    return None


def get_days_until_target(
    dream
):
    """期限までの日数を取得する。"""

    target_date = parse_date_text(
        dream.get(
            "target_date",
            ""
        )
    )

    if not target_date:
        return None

    return (
        target_date - date.today()
    ).days


def get_deadline_text(
    dream
):
    """期限の状態を表示用文字列で返す。"""

    if dream.get(
        "status"
    ) == "達成":
        return "達成済み"

    days_left = get_days_until_target(
        dream
    )

    if days_left is None:
        return "期限なし"

    if days_left < 0:
        return (
            f"{abs(days_left)}日超過"
        )

    if days_left == 0:
        return "今日まで"

    return f"あと{days_left}日"


def calculate_completion_rate(
    dreams
):
    """達成率を計算する。"""

    if not dreams:
        return 0.0

    completed_count = len(
        [
            dream
            for dream in dreams
            if dream.get(
                "status"
            ) == "達成"
        ]
    )

    return (
        completed_count
        / len(dreams)
    )


def get_yearly_completed_count(
    dreams,
    target_year
):
    """指定した年に達成した数を取得する。"""

    count = 0

    for dream in dreams:
        completed_date = parse_date_text(
            dream.get(
                "completed_date",
                ""
            )
        )

        if (
            completed_date
            and completed_date.year
            == target_year
        ):
            count += 1

    return count


def get_due_soon_count(
    dreams,
    days=30
):
    """期限が近い未達成項目の数を取得する。"""

    count = 0

    for dream in dreams:
        if dream.get(
            "status"
        ) == "達成":
            continue

        days_left = get_days_until_target(
            dream
        )

        if (
            days_left is not None
            and 0 <= days_left <= days
        ):
            count += 1

    return count


def format_date(
    date_text
):
    """日付を表示用に整形する。"""

    parsed_date = parse_date_text(
        date_text
    )

    if not parsed_date:
        return "未設定"

    return parsed_date.strftime(
        "%Y年%m月%d日"
    )


# =====================================
# データ操作
# =====================================

def add_dream(
    data,
    title,
    category,
    priority,
    target_date,
    reason,
    next_action,
    memo
):
    """やりたいことを登録する。"""

    dream = {
        "id": create_id(),
        "title": title,
        "category": category,
        "priority": priority,
        "status": "未着手",
        "progress": 0,
        "target_date": (
            str(target_date)
            if target_date
            else ""
        ),
        "completed_date": "",
        "reason": reason,
        "next_action": next_action,
        "memo": memo,
        "created_at": now_text(),
        "updated_at": ""
    }

    data["dreams"].append(
        dream
    )

    save_data(data)


def update_dream(
    data,
    dream_id,
    title,
    category,
    priority,
    status,
    progress,
    target_date,
    reason,
    next_action,
    memo
):
    """やりたいことを更新する。"""

    dream = get_dream_by_id(
        data,
        dream_id
    )

    if not dream:
        return

    previous_status = dream.get(
        "status",
        "未着手"
    )

    dream["title"] = title
    dream["category"] = category
    dream["priority"] = priority
    dream["status"] = status
    dream["progress"] = int(
        progress
    )
    dream["target_date"] = (
        str(target_date)
        if target_date
        else ""
    )
    dream["reason"] = reason
    dream["next_action"] = next_action
    dream["memo"] = memo
    dream["updated_at"] = now_text()

    if status == "達成":
        dream["progress"] = 100

        if (
            previous_status != "達成"
            or not dream.get(
                "completed_date"
            )
        ):
            dream["completed_date"] = str(
                date.today()
            )

    else:
        dream["completed_date"] = ""

        if dream["progress"] >= 100:
            dream["progress"] = 99

    save_data(data)


def update_progress(
    data,
    dream_id,
    progress,
    next_action
):
    """進捗率と次の行動を更新する。"""

    dream = get_dream_by_id(
        data,
        dream_id
    )

    if not dream:
        return

    dream["progress"] = int(
        progress
    )

    dream["next_action"] = (
        next_action
    )

    if progress <= 0:
        dream["status"] = "未着手"
        dream["completed_date"] = ""

    elif progress >= 100:
        dream["status"] = "達成"

        if not dream.get(
            "completed_date"
        ):
            dream["completed_date"] = str(
                date.today()
            )

    elif dream.get(
        "status"
    ) != "一時停止":
        dream["status"] = "進行中"
        dream["completed_date"] = ""

    dream["updated_at"] = now_text()

    save_data(data)


def mark_as_completed(
    data,
    dream_id
):
    """やりたいことを達成済みにする。"""

    dream = get_dream_by_id(
        data,
        dream_id
    )

    if not dream:
        return

    dream["status"] = "達成"
    dream["progress"] = 100
    dream["completed_date"] = str(
        date.today()
    )
    dream["updated_at"] = now_text()

    save_data(data)


def reopen_dream(
    data,
    dream_id
):
    """達成済み項目を再開する。"""

    dream = get_dream_by_id(
        data,
        dream_id
    )

    if not dream:
        return

    dream["status"] = "進行中"
    dream["progress"] = 90
    dream["completed_date"] = ""
    dream["updated_at"] = now_text()

    save_data(data)


def delete_dream(
    data,
    dream_id
):
    """やりたいことを削除する。"""

    data["dreams"] = [
        dream
        for dream in data["dreams"]
        if dream.get(
            "id"
        ) != dream_id
    ]

    save_data(data)


# =====================================
# データ読み込み
# =====================================

data = load_data()

dreams = data["dreams"]


# =====================================
# タイトル
# =====================================

st.title(
    "✨ やりたいこと100リスト"
)

st.caption(
    "人生で叶えたいことを記録して、"
    "一つずつ夢を実現していきます。"
)


# =====================================
# ダッシュボード
# =====================================

st.divider()

st.header(
    "📊 ダッシュボード"
)

total_count = len(
    dreams
)

completed_dreams = [
    dream
    for dream in dreams
    if dream.get(
        "status"
    ) == "達成"
]

completed_count = len(
    completed_dreams
)

completion_rate = (
    calculate_completion_rate(
        dreams
    )
)

current_year = date.today().year

yearly_completed_count = (
    get_yearly_completed_count(
        dreams,
        current_year
    )
)

due_soon_count = (
    get_due_soon_count(
        dreams,
        days=30
    )
)


metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = (
    st.columns(5)
)

with metric_col1:
    st.metric(
        "登録数",
        f"{total_count}/100"
    )

with metric_col2:
    st.metric(
        "達成数",
        f"{completed_count}個"
    )

with metric_col3:
    st.metric(
        "達成率",
        f"{completion_rate * 100:.1f}%"
    )

with metric_col4:
    st.metric(
        f"{current_year}年の達成",
        f"{yearly_completed_count}個"
    )

with metric_col5:
    st.metric(
        "期限30日以内",
        f"{due_soon_count}個"
    )


st.progress(
    min(
        total_count / 100,
        1.0
    )
)

if total_count < 100:
    st.caption(
        f"100個まで、あと"
        f"{100 - total_count}個登録できます。"
    )

else:
    st.success(
        "やりたいことが100個そろいました！🎉"
    )


if dreams:
    st.subheader(
        "🏆 夢の達成状況"
    )

    st.progress(
        completion_rate
    )

    st.caption(
        f"{completed_count}個達成 "
        f"／ 未達成{total_count - completed_count}個"
    )

else:
    st.info(
        "まずは思いついた夢を"
        "一つ登録してみましょう。"
    )


# =====================================
# 注目すべき目標
# =====================================

active_dreams = [
    dream
    for dream in dreams
    if dream.get(
        "status"
    ) != "達成"
]

important_dreams = sorted(
    active_dreams,
    key=lambda dream: (
        PRIORITY_ORDER.get(
            dream.get(
                "priority",
                "いつか"
            ),
            99
        ),
        get_days_until_target(
            dream
        )
        if get_days_until_target(
            dream
        ) is not None
        else 999999
    )
)


if important_dreams:
    st.divider()

    st.header(
        "🎯 今、注目したいこと"
    )

    for dream in important_dreams[:3]:
        days_left = get_days_until_target(
            dream
        )

        with st.container(
            border=True
        ):
            focus_col1, focus_col2 = (
                st.columns([4, 1])
            )

            with focus_col1:
                st.subheader(
                    f"{PRIORITY_ICONS.get(dream.get('priority', ''), '')} "
                    f"{dream.get('title', '')}"
                )

                st.caption(
                    f"{dream.get('category', '')} "
                    f"／ {dream.get('priority', '')}"
                )

                if dream.get(
                    "next_action",
                    ""
                ):
                    st.write(
                        f"➡️ 次にやること："
                        f"**{dream.get('next_action', '')}**"
                    )

                if (
                    days_left is not None
                    and days_left < 0
                ):
                    st.error(
                        f"期限を"
                        f"{abs(days_left)}日過ぎています。"
                    )

                elif (
                    days_left is not None
                    and days_left <= 7
                ):
                    st.warning(
                        f"期限まであと"
                        f"{days_left}日です。"
                    )

            with focus_col2:
                st.metric(
                    "進捗",
                    f"{dream.get('progress', 0)}%"
                )

            st.progress(
                dream.get(
                    "progress",
                    0
                ) / 100
            )


# =====================================
# タブ
# =====================================

st.divider()

add_tab, list_tab, progress_tab, completed_tab, analysis_tab = (
    st.tabs(
        [
            "➕ やりたいこと登録",
            "📋 100リスト",
            "🚀 進捗管理",
            "🎉 達成履歴",
            "📈 集計"
        ]
    )
)


# =====================================
# 登録タブ
# =====================================

with add_tab:
    st.header(
        "➕ やりたいことを登録"
    )

    if total_count >= 100:
        st.warning(
            "100個登録されています。"
            "新しく追加する場合は、既存項目を整理してください。"
        )

    with st.form(
        "add_dream_form",
        clear_on_submit=True
    ):
        form_col1, form_col2 = (
            st.columns(2)
        )

        with form_col1:
            dream_title = (
                st.text_input(
                    "やりたいこと",
                    placeholder=(
                        "例：LuNovaを設立する"
                    )
                )
            )

            dream_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES
                )
            )

            dream_priority = (
                st.selectbox(
                    "優先度",
                    PRIORITIES
                )
            )

            has_target_date = (
                st.checkbox(
                    "目標期限を設定する"
                )
            )

            dream_target_date = None

            if has_target_date:
                dream_target_date = (
                    st.date_input(
                        "目標期限",
                        value=(
                            date.today()
                            + timedelta(
                                days=365
                            )
                        )
                    )
                )

        with form_col2:
            dream_reason = (
                st.text_area(
                    "叶えたい理由",
                    placeholder=(
                        "例：人とAIがパートナーになる"
                        "未来を作りたい"
                    )
                )
            )

            dream_next_action = (
                st.text_input(
                    "最初の一歩",
                    placeholder=(
                        "例：事業計画を1ページ書く"
                    )
                )
            )

            dream_memo = (
                st.text_area(
                    "メモ",
                    placeholder=(
                        "必要な準備やアイデアなど"
                    )
                )
            )

        dream_submit = (
            st.form_submit_button(
                "✨ リストに追加",
                use_container_width=True,
                disabled=(
                    total_count >= 100
                )
            )
        )

        if dream_submit:
            cleaned_title = (
                dream_title.strip()
            )

            duplicate_exists = any(
                dream.get(
                    "title",
                    ""
                ).strip().lower()
                == cleaned_title.lower()
                for dream in dreams
            )

            if not cleaned_title:
                st.error(
                    "やりたいことを入力してください。"
                )

            elif duplicate_exists:
                st.warning(
                    "同じ内容がすでに登録されています。"
                )

            else:
                add_dream(
                    data=data,
                    title=cleaned_title,
                    category=dream_category,
                    priority=dream_priority,
                    target_date=(
                        dream_target_date
                    ),
                    reason=(
                        dream_reason.strip()
                    ),
                    next_action=(
                        dream_next_action.strip()
                    ),
                    memo=(
                        dream_memo.strip()
                    )
                )

                st.success(
                    f"「{cleaned_title}」を"
                    "100リストに追加しました！"
                )

                st.rerun()

    st.divider()

    st.subheader(
        "💡 やりたいことのヒント"
    )

    hint_col1, hint_col2, hint_col3 = (
        st.columns(3)
    )

    with hint_col1:
        st.info(
            "🌏 行ってみたい場所\n\n"
            "国内旅行、海外旅行、温泉、"
            "家族で訪れたい場所"
        )

    with hint_col2:
        st.info(
            "🚀 挑戦したいこと\n\n"
            "起業、資格、スポーツ、"
            "作品づくり、新しい体験"
        )

    with hint_col3:
        st.info(
            "😊 大切にしたいこと\n\n"
            "家族、健康、暮らし、"
            "人間関係、将来の夢"
        )


# =====================================
# 100リストタブ
# =====================================

with list_tab:
    st.header(
        "📋 やりたいこと100リスト"
    )

    if not dreams:
        st.info(
            "やりたいことがまだ登録されていません。"
        )

    else:
        filter_col1, filter_col2, filter_col3 = (
            st.columns(3)
        )

        with filter_col1:
            search_keyword = (
                st.text_input(
                    "🔍 検索",
                    placeholder=(
                        "タイトル・理由・メモ"
                    ),
                    key="dream_search"
                )
            )

        with filter_col2:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ] + CATEGORIES,
                    key="category_filter"
                )
            )

        with filter_col3:
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて"
                    ] + STATUS_OPTIONS,
                    key="status_filter"
                )
            )

        filter_col4, filter_col5 = (
            st.columns(2)
        )

        with filter_col4:
            priority_filter = (
                st.multiselect(
                    "優先度",
                    PRIORITIES,
                    default=PRIORITIES
                )
            )

        with filter_col5:
            sort_option = (
                st.selectbox(
                    "並び順",
                    [
                        "優先度順",
                        "登録が新しい順",
                        "登録が古い順",
                        "期限が近い順",
                        "進捗が高い順",
                        "進捗が低い順"
                    ]
                )
            )

        filtered_dreams = list(
            dreams
        )

        if search_keyword:
            keyword = (
                search_keyword.strip().lower()
            )

            filtered_dreams = [
                dream
                for dream in filtered_dreams
                if (
                    keyword
                    in dream.get(
                        "title",
                        ""
                    ).lower()
                    or keyword
                    in dream.get(
                        "reason",
                        ""
                    ).lower()
                    or keyword
                    in dream.get(
                        "next_action",
                        ""
                    ).lower()
                    or keyword
                    in dream.get(
                        "memo",
                        ""
                    ).lower()
                )
            ]

        if category_filter != "すべて":
            filtered_dreams = [
                dream
                for dream in filtered_dreams
                if dream.get(
                    "category"
                ) == category_filter
            ]

        if status_filter != "すべて":
            filtered_dreams = [
                dream
                for dream in filtered_dreams
                if dream.get(
                    "status"
                ) == status_filter
            ]

        filtered_dreams = [
            dream
            for dream in filtered_dreams
            if dream.get(
                "priority",
                "いつか"
            ) in priority_filter
        ]

        if sort_option == "優先度順":
            filtered_dreams = sorted(
                filtered_dreams,
                key=lambda dream: (
                    PRIORITY_ORDER.get(
                        dream.get(
                            "priority",
                            "いつか"
                        ),
                        99
                    ),
                    dream.get(
                        "created_at",
                        ""
                    )
                )
            )

        elif sort_option == "登録が新しい順":
            filtered_dreams = sorted(
                filtered_dreams,
                key=lambda dream: dream.get(
                    "created_at",
                    ""
                ),
                reverse=True
            )

        elif sort_option == "登録が古い順":
            filtered_dreams = sorted(
                filtered_dreams,
                key=lambda dream: dream.get(
                    "created_at",
                    ""
                )
            )

        elif sort_option == "期限が近い順":
            filtered_dreams = sorted(
                filtered_dreams,
                key=lambda dream: (
                    get_days_until_target(
                        dream
                    )
                    if get_days_until_target(
                        dream
                    ) is not None
                    else 999999
                )
            )

        elif sort_option == "進捗が高い順":
            filtered_dreams = sorted(
                filtered_dreams,
                key=lambda dream: dream.get(
                    "progress",
                    0
                ),
                reverse=True
            )

        else:
            filtered_dreams = sorted(
                filtered_dreams,
                key=lambda dream: dream.get(
                    "progress",
                    0
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_dreams)}件**"
        )

        for index, dream in enumerate(
            filtered_dreams,
            start=1
        ):
            dream_id = dream.get(
                "id",
                ""
            )

            days_left = get_days_until_target(
                dream
            )

            with st.container(
                border=True
            ):
                info_col, metric_col = (
                    st.columns([4, 1])
                )

                with info_col:
                    st.subheader(
                        f"{STATUS_ICONS.get(dream.get('status', ''), '')} "
                        f"{dream.get('title', '')}"
                    )

                    st.caption(
                        f"{PRIORITY_ICONS.get(dream.get('priority', ''), '')} "
                        f"{dream.get('priority', '')} "
                        f"／ {dream.get('category', '')} "
                        f"／ {dream.get('status', '')}"
                    )

                    if dream.get(
                        "target_date",
                        ""
                    ):
                        st.write(
                            f"📅 目標期限："
                            f"**{format_date(dream.get('target_date', ''))}**"
                        )

                        if (
                            days_left is not None
                            and days_left < 0
                            and dream.get(
                                "status"
                            ) != "達成"
                        ):
                            st.error(
                                f"期限を"
                                f"{abs(days_left)}日過ぎています。"
                            )

                        elif (
                            days_left is not None
                            and days_left <= 7
                            and dream.get(
                                "status"
                            ) != "達成"
                        ):
                            st.warning(
                                f"期限まであと"
                                f"{days_left}日です。"
                            )

                    if dream.get(
                        "reason",
                        ""
                    ):
                        st.write(
                            f"💭 理由："
                            f"{dream.get('reason', '')}"
                        )

                    if dream.get(
                        "next_action",
                        ""
                    ):
                        st.info(
                            f"➡️ 次にやること："
                            f"{dream.get('next_action', '')}"
                        )

                    if dream.get(
                        "memo",
                        ""
                    ):
                        st.caption(
                            f"📝 {dream.get('memo', '')}"
                        )

                with metric_col:
                    st.metric(
                        "進捗",
                        f"{dream.get('progress', 0)}%"
                    )

                    st.caption(
                        get_deadline_text(
                            dream
                        )
                    )

                st.progress(
                    dream.get(
                        "progress",
                        0
                    ) / 100
                )

                if dream.get(
                    "status"
                ) != "達成":
                    if st.button(
                        "🎉 達成にする",
                        key=(
                            f"complete_list_"
                            f"{dream_id}"
                        ),
                        use_container_width=True
                    ):
                        mark_as_completed(
                            data,
                            dream_id
                        )

                        st.balloons()
                        st.rerun()

                with st.expander(
                    "✏️ 内容を編集"
                ):
                    edit_title = (
                        st.text_input(
                            "やりたいこと",
                            value=dream.get(
                                "title",
                                ""
                            ),
                            key=(
                                f"edit_title_"
                                f"{dream_id}"
                            )
                        )
                    )

                    current_category = dream.get(
                        "category",
                        "その他"
                    )

                    category_index = (
                        CATEGORIES.index(
                            current_category
                        )
                        if current_category
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
                                f"{dream_id}"
                            )
                        )
                    )

                    current_priority = dream.get(
                        "priority",
                        "中"
                    )

                    priority_index = (
                        PRIORITIES.index(
                            current_priority
                        )
                        if current_priority
                        in PRIORITIES
                        else 2
                    )

                    edit_priority = (
                        st.selectbox(
                            "優先度",
                            PRIORITIES,
                            index=priority_index,
                            key=(
                                f"edit_priority_"
                                f"{dream_id}"
                            )
                        )
                    )

                    current_status = dream.get(
                        "status",
                        "未着手"
                    )

                    status_index = (
                        STATUS_OPTIONS.index(
                            current_status
                        )
                        if current_status
                        in STATUS_OPTIONS
                        else 0
                    )

                    edit_status = (
                        st.selectbox(
                            "状態",
                            STATUS_OPTIONS,
                            index=status_index,
                            key=(
                                f"edit_status_"
                                f"{dream_id}"
                            )
                        )
                    )

                    edit_progress = (
                        st.slider(
                            "進捗率",
                            min_value=0,
                            max_value=100,
                            value=int(
                                dream.get(
                                    "progress",
                                    0
                                )
                            ),
                            step=5,
                            key=(
                                f"edit_progress_"
                                f"{dream_id}"
                            )
                        )
                    )

                    current_target_date = (
                        parse_date_text(
                            dream.get(
                                "target_date",
                                ""
                            )
                        )
                    )

                    edit_has_target = (
                        st.checkbox(
                            "目標期限を設定する",
                            value=bool(
                                current_target_date
                            ),
                            key=(
                                f"edit_has_target_"
                                f"{dream_id}"
                            )
                        )
                    )

                    edit_target_date = None

                    if edit_has_target:
                        edit_target_date = (
                            st.date_input(
                                "目標期限",
                                value=(
                                    current_target_date
                                    or date.today()
                                ),
                                key=(
                                    f"edit_target_date_"
                                    f"{dream_id}"
                                )
                            )
                        )

                    edit_reason = (
                        st.text_area(
                            "叶えたい理由",
                            value=dream.get(
                                "reason",
                                ""
                            ),
                            key=(
                                f"edit_reason_"
                                f"{dream_id}"
                            )
                        )
                    )

                    edit_next_action = (
                        st.text_input(
                            "次にやること",
                            value=dream.get(
                                "next_action",
                                ""
                            ),
                            key=(
                                f"edit_next_action_"
                                f"{dream_id}"
                            )
                        )
                    )

                    edit_memo = (
                        st.text_area(
                            "メモ",
                            value=dream.get(
                                "memo",
                                ""
                            ),
                            key=(
                                f"edit_memo_"
                                f"{dream_id}"
                            )
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_dream_"
                            f"{dream_id}"
                        ),
                        use_container_width=True
                    ):
                        cleaned_edit_title = (
                            edit_title.strip()
                        )

                        if not cleaned_edit_title:
                            st.error(
                                "やりたいことを入力してください。"
                            )

                        else:
                            update_dream(
                                data=data,
                                dream_id=dream_id,
                                title=(
                                    cleaned_edit_title
                                ),
                                category=(
                                    edit_category
                                ),
                                priority=(
                                    edit_priority
                                ),
                                status=(
                                    edit_status
                                ),
                                progress=(
                                    edit_progress
                                ),
                                target_date=(
                                    edit_target_date
                                ),
                                reason=(
                                    edit_reason.strip()
                                ),
                                next_action=(
                                    edit_next_action.strip()
                                ),
                                memo=(
                                    edit_memo.strip()
                                )
                            )

                            st.success(
                                "内容を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ この項目を削除"
                ):
                    st.warning(
                        "削除した項目は元に戻せません。"
                    )

                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_delete_"
                                f"{dream_id}"
                            )
                        )
                    )

                    if st.button(
                        "削除する",
                        key=(
                            f"delete_dream_"
                            f"{dream_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_dream(
                            data,
                            dream_id
                        )

                        st.rerun()


# =====================================
# 進捗管理タブ
# =====================================

with progress_tab:
    st.header(
        "🚀 進捗管理"
    )

    active_dreams = [
        dream
        for dream in dreams
        if dream.get(
            "status"
        ) != "達成"
    ]

    if not active_dreams:
        st.info(
            "進行中のやりたいことはありません。"
        )

    else:
        active_dreams = sorted(
            active_dreams,
            key=lambda dream: (
                PRIORITY_ORDER.get(
                    dream.get(
                        "priority",
                        "いつか"
                    ),
                    99
                ),
                dream.get(
                    "progress",
                    0
                )
            )
        )

        for dream in active_dreams:
            dream_id = dream.get(
                "id",
                ""
            )

            with st.container(
                border=True
            ):
                progress_info_col, progress_metric_col = (
                    st.columns([4, 1])
                )

                with progress_info_col:
                    st.subheader(
                        f"{PRIORITY_ICONS.get(dream.get('priority', ''), '')} "
                        f"{dream.get('title', '')}"
                    )

                    st.caption(
                        f"{dream.get('category', '')} "
                        f"／ {dream.get('status', '')}"
                    )

                with progress_metric_col:
                    st.metric(
                        "現在の進捗",
                        f"{dream.get('progress', 0)}%"
                    )

                st.progress(
                    dream.get(
                        "progress",
                        0
                    ) / 100
                )

                new_progress = (
                    st.slider(
                        "進捗を更新",
                        min_value=0,
                        max_value=100,
                        value=int(
                            dream.get(
                                "progress",
                                0
                            )
                        ),
                        step=5,
                        key=(
                            f"progress_slider_"
                            f"{dream_id}"
                        )
                    )
                )

                new_next_action = (
                    st.text_input(
                        "次にやること",
                        value=dream.get(
                            "next_action",
                            ""
                        ),
                        placeholder=(
                            "次に実行する小さな行動"
                        ),
                        key=(
                            f"progress_action_"
                            f"{dream_id}"
                        )
                    )
                )

                if st.button(
                    "進捗を保存",
                    key=(
                        f"save_progress_"
                        f"{dream_id}"
                    ),
                    use_container_width=True
                ):
                    update_progress(
                        data=data,
                        dream_id=dream_id,
                        progress=new_progress,
                        next_action=(
                            new_next_action.strip()
                        )
                    )

                    if new_progress >= 100:
                        st.balloons()

                    st.rerun()


# =====================================
# 達成履歴タブ
# =====================================

with completed_tab:
    st.header(
        "🎉 達成履歴"
    )

    if not completed_dreams:
        st.info(
            "達成したやりたいことはまだありません。"
        )

    else:
        completed_dreams_sorted = sorted(
            completed_dreams,
            key=lambda dream: dream.get(
                "completed_date",
                ""
            ),
            reverse=True
        )

        selected_year = st.selectbox(
            "達成年",
            [
                "すべて"
            ] + sorted(
                {
                    parse_date_text(
                        dream.get(
                            "completed_date",
                            ""
                        )
                    ).year
                    for dream in completed_dreams
                    if parse_date_text(
                        dream.get(
                            "completed_date",
                            ""
                        )
                    )
                },
                reverse=True
            )
        )

        if selected_year != "すべて":
            completed_dreams_sorted = [
                dream
                for dream in completed_dreams_sorted
                if (
                    parse_date_text(
                        dream.get(
                            "completed_date",
                            ""
                        )
                    )
                    and parse_date_text(
                        dream.get(
                            "completed_date",
                            ""
                        )
                    ).year
                    == selected_year
                )
            ]

        st.write(
            f"表示件数："
            f"**{len(completed_dreams_sorted)}件**"
        )

        for dream in completed_dreams_sorted:
            dream_id = dream.get(
                "id",
                ""
            )

            with st.container(
                border=True
            ):
                completed_info_col, completed_date_col = (
                    st.columns([4, 1])
                )

                with completed_info_col:
                    st.subheader(
                        f"🎉 {dream.get('title', '')}"
                    )

                    st.caption(
                        f"{dream.get('category', '')} "
                        f"／ {dream.get('priority', '')}"
                    )

                    if dream.get(
                        "reason",
                        ""
                    ):
                        st.write(
                            f"💭 {dream.get('reason', '')}"
                        )

                with completed_date_col:
                    st.metric(
                        "達成日",
                        format_date(
                            dream.get(
                                "completed_date",
                                ""
                            )
                        )
                    )

                if st.button(
                    "↩️ 再び挑戦する",
                    key=(
                        f"reopen_dream_"
                        f"{dream_id}"
                    ),
                    use_container_width=True
                ):
                    reopen_dream(
                        data,
                        dream_id
                    )

                    st.rerun()


# =====================================
# 集計タブ
# =====================================

with analysis_tab:
    st.header(
        "📈 やりたいこと集計"
    )

    if not dreams:
        st.info(
            "集計できるデータがありません。"
        )

    else:
        dream_rows = []

        for dream in dreams:
            dream_rows.append(
                {
                    "やりたいこと": dream.get(
                        "title",
                        ""
                    ),
                    "カテゴリー": dream.get(
                        "category",
                        ""
                    ),
                    "優先度": dream.get(
                        "priority",
                        ""
                    ),
                    "状態": dream.get(
                        "status",
                        ""
                    ),
                    "進捗率": dream.get(
                        "progress",
                        0
                    ),
                    "期限": dream.get(
                        "target_date",
                        ""
                    )
                }
            )

        dream_df = pd.DataFrame(
            dream_rows
        )

        st.subheader(
            "📂 カテゴリー別登録数"
        )

        category_summary = (
            dream_df.groupby(
                "カテゴリー",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "登録数"
                }
            )
            .sort_values(
                "登録数",
                ascending=False
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["登録数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🎯 状態別登録数"
        )

        status_summary = (
            dream_df.groupby(
                "状態",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "登録数"
                }
            )
            .sort_values(
                "登録数",
                ascending=False
            )
        )

        st.bar_chart(
            status_summary.set_index(
                "状態"
            )[["登録数"]]
        )

        st.dataframe(
            status_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🔥 優先度別登録数"
        )

        priority_summary = (
            dream_df.groupby(
                "優先度",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "登録数"
                }
            )
        )

        priority_summary[
            "並び順"
        ] = priority_summary[
            "優先度"
        ].map(
            PRIORITY_ORDER
        )

        priority_summary = (
            priority_summary.sort_values(
                "並び順"
            )
            .drop(
                columns=[
                    "並び順"
                ]
            )
        )

        st.bar_chart(
            priority_summary.set_index(
                "優先度"
            )[["登録数"]]
        )

        st.dataframe(
            priority_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🚀 カテゴリー別平均進捗"
        )

        progress_summary = (
            dream_df.groupby(
                "カテゴリー",
                as_index=False
            )["進捗率"]
            .mean()
            .sort_values(
                "進捗率",
                ascending=False
            )
        )

        progress_summary[
            "進捗率"
        ] = progress_summary[
            "進捗率"
        ].round(1)

        st.bar_chart(
            progress_summary.set_index(
                "カテゴリー"
            )[["進捗率"]]
        )

        st.dataframe(
            progress_summary,
            use_container_width=True,
            hide_index=True
        )


st.divider()

st.success(
    "夢は書いた瞬間から、"
    "少しずつ現実へ向かい始める！✨"
)
