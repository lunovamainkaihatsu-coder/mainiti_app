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
    page_title="あれ、どこ置いた？",
    page_icon="🔍",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "items.json",
)

CATEGORIES = [
    "🔑 鍵",
    "📄 書類・カード",
    "🔌 電子機器・ケーブル",
    "🛠️ 工具",
    "💊 薬・衛生用品",
    "👕 衣類",
    "🧸 子ども用品",
    "🍳 キッチン",
    "🎮 趣味",
    "📚 本・文房具",
    "💰 お金・貴重品",
    "📦 その他",
]

IMPORTANCE = {
    1: "⭐ 普通",
    2: "⭐⭐ 大事",
    3: "⭐⭐⭐ 超重要",
}

CHECK_DAYS = {
    1: 365,
    2: 180,
    3: 90,
}


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def today_text():
    return str(date.today())


def parse_date(value):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return date.today()


def days_since(value):
    target = parse_date(value)

    return max(
        (
            date.today()
            - target
        ).days,
        0,
    )


def location_text(item):
    parts = [
        item.get("room", "").strip(),
        item.get("place", "").strip(),
        item.get("position", "").strip(),
        item.get("container", "").strip(),
    ]

    parts = [
        part
        for part in parts
        if part
    ]

    if not parts:
        return "場所未登録"

    return " ＞ ".join(parts)


def create_empty_data():
    return {
        "items": [],
        "move_history": [],
    }


# =========================================================
# 保存・読み込み
# =========================================================

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


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
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

        if not isinstance(
            data,
            dict,
        ):
            data = create_empty_data()

        data.setdefault(
            "items",
            [],
        )

        data.setdefault(
            "move_history",
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
                "category",
                "📦 その他",
            )

            item.setdefault(
                "room",
                "",
            )

            item.setdefault(
                "place",
                "",
            )

            item.setdefault(
                "position",
                "",
            )

            item.setdefault(
                "container",
                "",
            )

            item.setdefault(
                "tags",
                "",
            )

            item.setdefault(
                "memo",
                "",
            )

            item.setdefault(
                "importance",
                1,
            )

            item.setdefault(
                "favorite",
                False,
            )

            item.setdefault(
                "created_date",
                today_text(),
            )

            item.setdefault(
                "last_checked_date",
                item.get(
                    "created_date",
                    today_text(),
                ),
            )

            item.setdefault(
                "created_at",
                now_text(),
            )

            item.setdefault(
                "updated_at",
                item.get(
                    "created_at",
                    now_text(),
                ),
            )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = create_empty_data()

        save_data(data)

        return data


# =========================================================
# CRUD
# =========================================================

def get_item(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data["items"]
            if item.get(
                "id"
            ) == item_id
        ),
        None,
    )


def add_item(
    data,
    name,
    category,
    room,
    place,
    position,
    container_name,
    tags,
    memo,
    importance,
):
    item_id = create_id()

    item = {
        "id": item_id,
        "name": name,
        "category": category,
        "room": room,
        "place": place,
        "position": position,
        "container": container_name,
        "tags": tags,
        "memo": memo,
        "importance": int(
            importance
        ),
        "favorite": False,
        "created_date": today_text(),
        "last_checked_date": today_text(),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["items"].append(
        item
    )

    add_move_history(
        data,
        item,
        old_location="",
        new_location=location_text(
            item
        ),
        reason="登録",
        save=False,
    )

    save_data(data)


def add_move_history(
    data,
    item,
    old_location,
    new_location,
    reason="移動",
    save=True,
):
    data[
        "move_history"
    ].append(
        {
            "id": create_id(),
            "item_id": item.get(
                "id",
                "",
            ),
            "item_name": item.get(
                "name",
                "",
            ),
            "old_location": (
                old_location
            ),
            "new_location": (
                new_location
            ),
            "reason": reason,
            "move_date": today_text(),
            "created_at": now_text(),
        }
    )

    if save:
        save_data(data)


def update_item(
    data,
    item_id,
    name,
    category,
    room,
    place,
    position,
    container_name,
    tags,
    memo,
    importance,
    favorite,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    old_location = location_text(
        item
    )

    item["name"] = name
    item["category"] = category
    item["room"] = room
    item["place"] = place
    item["position"] = position
    item["container"] = (
        container_name
    )
    item["tags"] = tags
    item["memo"] = memo
    item["importance"] = int(
        importance
    )
    item["favorite"] = favorite
    item["updated_at"] = now_text()

    new_location = location_text(
        item
    )

    if (
        old_location
        != new_location
    ):
        item[
            "last_checked_date"
        ] = today_text()

        add_move_history(
            data,
            item,
            old_location,
            new_location,
            reason="場所変更",
            save=False,
        )

    save_data(data)


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item in data["items"]
        if item.get(
            "id"
        ) != item_id
    ]

    save_data(data)


def toggle_favorite(
    data,
    item_id,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["favorite"] = not (
        item.get(
            "favorite",
            False,
        )
    )

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def confirm_location(
    data,
    item_id,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item[
        "last_checked_date"
    ] = today_text()

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


# =========================================================
# 集計
# =========================================================

def needs_check(item):
    importance = int(
        item.get(
            "importance",
            1,
        )
    )

    threshold = CHECK_DAYS.get(
        importance,
        365,
    )

    elapsed = days_since(
        item.get(
            "last_checked_date"
        )
    )

    return elapsed >= threshold


def unique_rooms(items):
    return sorted(
        {
            item.get(
                "room",
                "",
            ).strip()
            for item in items
            if item.get(
                "room",
                "",
            ).strip()
        }
    )


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 16px;

        background:
            rgba(80, 130, 220, 0.07);

        border:
            1px solid
            rgba(80, 130, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(70, 130, 230, 0.18),
                rgba(80, 200, 170, 0.08)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.82;
    }

    .location-card {
        padding: 25px;
        border-radius: 22px;
        margin-top: 12px;
        margin-bottom: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(70, 140, 230, 0.11),
                rgba(80, 190, 150, 0.06)
            );
    }

    .location-name {
        font-size: 1.55rem;
        font-weight: 800;
    }

    .location-path {
        font-size: 1.1rem;
        margin-top: 10px;
        font-weight: 600;
    }

    .warning-card {
        padding: 22px;
        border-radius: 20px;

        background:
            rgba(240, 170, 60, 0.09);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ
# =========================================================

data = load_data()

items = data["items"]

rooms = unique_rooms(
    items
)

check_items = [
    item
    for item in items
    if needs_check(
        item
    )
]

important_items = [
    item
    for item in items
    if int(
        item.get(
            "importance",
            1,
        )
    ) >= 2
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            🔍 あれ、どこ置いた？
        </h1>

        <p>
            探す時間を、なくそう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "📦 登録",
    f"{len(items)}個",
)

col2.metric(
    "⭐⭐ 大事以上",
    f"{len(important_items)}個",
)

col3.metric(
    "👀 要確認",
    f"{len(check_items)}個",
)

col4.metric(
    "🏠 登録場所",
    f"{len(rooms)}か所",
)


# =========================================================
# メイン検索
# =========================================================

st.divider()

st.subheader(
    "🔍 何を探してる？"
)

search_text = st.text_input(
    "モノを検索",
    placeholder=(
        "印鑑、ケーブル、保証書……"
    ),
    label_visibility="collapsed",
)

search_results = []

if search_text.strip():
    keyword = (
        search_text
        .strip()
        .lower()
    )

    for item in items:
        target = " ".join(
            [
                item.get(
                    "name",
                    "",
                ),
                item.get(
                    "category",
                    "",
                ),
                item.get(
                    "room",
                    "",
                ),
                item.get(
                    "place",
                    "",
                ),
                item.get(
                    "position",
                    "",
                ),
                item.get(
                    "container",
                    "",
                ),
                item.get(
                    "tags",
                    "",
                ),
                item.get(
                    "memo",
                    "",
                ),
            ]
        ).lower()

        if keyword in target:
            search_results.append(
                item
            )

    if not search_results:
        st.warning(
            "見つかりませんでした。"
        )

    else:
        st.success(
            f"{len(search_results)}件"
            "見つかりました！"
        )

        for item in search_results:
            item_id = item.get(
                "id",
                "",
            )

            with st.container(
                border=True
            ):
                col1, col2 = (
                    st.columns(
                        [6, 1]
                    )
                )

                with col1:
                    st.markdown(
                        "### "
                        + item.get(
                            "category",
                            "📦"
                        )
                        + " "
                        + item.get(
                            "name",
                            "",
                        )
                    )

                with col2:
                    icon = (
                        "⭐"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    )

                    if st.button(
                        icon,
                        key=(
                            "search_fav_"
                            + item_id
                        ),
                    ):
                        toggle_favorite(
                            data,
                            item_id,
                        )

                        st.rerun()

                st.markdown(
                    f"""
                    <div class="location-card">

                        <div>
                            📍 登録場所
                        </div>

                        <div class="location-path">
                            {
                                location_text(
                                    item
                                )
                            }
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if item.get(
                    "memo"
                ):
                    st.write(
                        "📝 "
                        + item.get(
                            "memo",
                            "",
                        )
                    )

                st.caption(
                    "👀 最終確認："
                    + item.get(
                        "last_checked_date",
                        "",
                    )
                    + "（"
                    + str(
                        days_since(
                            item.get(
                                "last_checked_date"
                            )
                        )
                    )
                    + "日前）"
                )

                if st.button(
                    "👀 ここにあった！",
                    key=(
                        "found_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    confirm_location(
                        data,
                        item_id,
                    )

                    st.toast(
                        "場所を確認しました！"
                    )

                    st.rerun()


# =========================================================
# 最近登録したもの
# =========================================================

if not search_text.strip():
    st.caption(
        "最近登録したもの"
    )

    recent_items = sorted(
        items,
        key=lambda item: (
            item.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )[:5]

    if not recent_items:
        st.info(
            "まだモノが登録されていません。"
        )

    else:
        for item in recent_items:
            st.write(
                f"{item.get('category', '📦')} "
                f"**{item.get('name', '')}**"
                f"　→　📍 "
                f"{location_text(item)}"
            )


# =========================================================
# モノを登録
# =========================================================

st.divider()

st.subheader(
    "📦 モノを登録"
)

with st.form(
    "add_item_form",
    clear_on_submit=True,
):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "名前",
            placeholder=(
                "例：実印"
            ),
        )

    with col2:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

    st.markdown(
        "#### 📍 どこに置いた？"
    )

    col1, col2 = st.columns(2)

    with col1:
        room = st.text_input(
            "🏠 部屋",
            placeholder=(
                "例：リビング"
            ),
        )

        position = st.text_input(
            "↕️ 位置",
            placeholder=(
                "例：上から2段目"
            ),
        )

    with col2:
        place = st.text_input(
            "📦 場所",
            placeholder=(
                "例：テレビ横の棚"
            ),
        )

        container_name = (
            st.text_input(
                "🗃️ 入れ物",
                placeholder=(
                    "例：白いケース"
                ),
            )
        )

    importance = st.select_slider(
        "⭐ 重要度",
        options=[
            1,
            2,
            3,
        ],
        value=1,
        format_func=lambda value: (
            IMPORTANCE[
                value
            ]
        ),
    )

    tags = st.text_input(
        "🏷️ 検索用タグ",
        placeholder=(
            "重要 役所 身分証"
        ),
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "家族分まとめて保管、"
            "青いファイルの中など"
        ),
    )

    submitted = (
        st.form_submit_button(
            "📦 登録する",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not name.strip():
            st.warning(
                "モノの名前を入力してね。"
            )

        elif not any(
            [
                room.strip(),
                place.strip(),
                position.strip(),
                container_name.strip(),
            ]
        ):
            st.warning(
                "場所を1つ以上"
                "入力してね。"
            )

        else:
            add_item(
                data,
                name.strip(),
                category,
                room.strip(),
                place.strip(),
                position.strip(),
                container_name.strip(),
                tags.strip(),
                memo.strip(),
                importance,
            )

            st.rerun()


# =========================================================
# 場所から探す
# =========================================================

st.divider()

st.subheader(
    "🏠 場所から探す"
)

if not rooms:
    st.info(
        "部屋を登録すると、"
        "ここから場所別に探せます。"
    )

else:
    selected_room = st.selectbox(
        "部屋を選ぶ",
        rooms,
    )

    room_items = [
        item
        for item in items
        if item.get(
            "room",
            "",
        ).strip()
        == selected_room
    ]

    st.caption(
        f"{selected_room}には"
        f"{len(room_items)}個"
        "登録されています。"
    )

    places = sorted(
        {
            item.get(
                "place",
                "",
            ).strip()
            or "場所未設定"
            for item in room_items
        }
    )

    for place_name in places:
        target_items = [
            item
            for item in room_items
            if (
                item.get(
                    "place",
                    "",
                ).strip()
                or "場所未設定"
            )
            == place_name
        ]

        with st.expander(
            f"📦 {place_name}"
            f"　{len(target_items)}個"
        ):
            for item in target_items:
                st.markdown(
                    f"**{item.get('category', '📦')} "
                    f"{item.get('name', '')}**"
                )

                st.caption(
                    "📍 "
                    + location_text(
                        item
                    )
                )


# =========================================================
# 要確認
# =========================================================

if check_items:
    st.divider()

    st.subheader(
        "👀 まだここにある？"
    )

    st.caption(
        "しばらく場所を確認していない"
        "モノがあります。"
    )

    sorted_check_items = sorted(
        check_items,
        key=lambda item: (
            int(
                item.get(
                    "importance",
                    1,
                )
            ),
            days_since(
                item.get(
                    "last_checked_date"
                )
            ),
        ),
        reverse=True,
    )

    for item in sorted_check_items:
        item_id = item.get(
            "id",
            "",
        )

        elapsed = days_since(
            item.get(
                "last_checked_date"
            )
        )

        importance = int(
            item.get(
                "importance",
                1,
            )
        )

        st.markdown(
            f"""
            <div class="warning-card">

                <strong>
                    {
                        item.get(
                            "category",
                            "📦"
                        )
                    }
                    {
                        item.get(
                            "name",
                            ""
                        )
                    }
                </strong>

                <br><br>

                {
                    IMPORTANCE.get(
                        importance,
                        "⭐ 普通"
                    )
                }

                <br>

                最後に場所を確認したのは
                <strong>
                    {elapsed}日前
                </strong>

                <br><br>

                📍
                {
                    location_text(
                        item
                    )
                }

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "👍 まだここにある",
            key=(
                "check_"
                + item_id
            ),
            use_container_width=True,
        ):
            confirm_location(
                data,
                item_id,
            )

            st.rerun()


# =========================================================
# カテゴリー分析
# =========================================================

if items:
    st.divider()

    st.subheader(
        "📊 登録しているモノ"
    )

    category_rows = []

    for category in CATEGORIES:
        count = len(
            [
                item
                for item in items
                if item.get(
                    "category"
                ) == category
            ]
        )

        if count:
            category_rows.append(
                {
                    "カテゴリー": category,
                    "個数": count,
                }
            )

    if category_rows:
        category_df = (
            pd.DataFrame(
                category_rows
            )
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# お気に入り・重要品
# =========================================================

special_items = [
    item
    for item in items
    if item.get(
        "favorite",
        False,
    )
    or int(
        item.get(
            "importance",
            1,
        )
    ) == 3
]

if special_items:
    st.divider()

    st.subheader(
        "⭐ 大切なモノ"
    )

    for item in sorted(
        special_items,
        key=lambda value: (
            int(
                value.get(
                    "importance",
                    1,
                )
            )
        ),
        reverse=True,
    ):
        st.write(
            f"{IMPORTANCE.get(item.get('importance', 1))}"
            f"　**{item.get('name', '')}**"
        )

        st.caption(
            "📍 "
            + location_text(
                item
            )
        )


# =========================================================
# 移動履歴
# =========================================================

st.divider()

st.subheader(
    "🕰️ 場所の履歴"
)

history = data[
    "move_history"
]

if not history:
    st.info(
        "まだ移動履歴はありません。"
    )

else:
    history_rows = []

    for entry in sorted(
        history,
        key=lambda value: (
            value.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    ):
        history_rows.append(
            {
                "日付": entry.get(
                    "move_date",
                    "",
                ),
                "モノ": entry.get(
                    "item_name",
                    "",
                ),
                "変更前": (
                    entry.get(
                        "old_location",
                        "",
                    )
                    or "-"
                ),
                "変更後": (
                    entry.get(
                        "new_location",
                        "",
                    )
                ),
                "種類": entry.get(
                    "reason",
                    "",
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            history_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 全データ管理
# =========================================================

st.divider()

st.subheader(
    "📚 登録一覧"
)

filter_category = st.selectbox(
    "カテゴリーで絞る",
    ["すべて"] + CATEGORIES,
    key="list_category",
)

filter_room_options = (
    ["すべて"]
    + rooms
)

filter_room = st.selectbox(
    "部屋で絞る",
    filter_room_options,
)

filtered_items = []

for item in items:
    if (
        filter_category
        != "すべて"
        and item.get(
            "category"
        )
        != filter_category
    ):
        continue

    if (
        filter_room
        != "すべて"
        and item.get(
            "room"
        )
        != filter_room
    ):
        continue

    filtered_items.append(
        item
    )

for item in sorted(
    filtered_items,
    key=lambda value: (
        value.get(
            "name",
            "",
        )
    ),
):
    item_id = item.get(
        "id",
        "",
    )

    with st.container(
        border=True
    ):
        col1, col2 = st.columns(
            [6, 1]
        )

        with col1:
            st.markdown(
                f"### "
                f"{item.get('category', '📦')} "
                f"{item.get('name', '')}"
            )

        with col2:
            favorite_icon = (
                "⭐"
                if item.get(
                    "favorite",
                    False,
                )
                else "☆"
            )

            if st.button(
                favorite_icon,
                key=(
                    "list_favorite_"
                    + item_id
                ),
            ):
                toggle_favorite(
                    data,
                    item_id,
                )

                st.rerun()

        st.write(
            "📍 **"
            + location_text(
                item
            )
            + "**"
        )

        st.caption(
            IMPORTANCE.get(
                int(
                    item.get(
                        "importance",
                        1,
                    )
                ),
                "⭐ 普通",
            )
            + " ｜ 最終確認："
            + item.get(
                "last_checked_date",
                "",
            )
        )

        if item.get(
            "tags"
        ):
            st.caption(
                "🏷️ "
                + item.get(
                    "tags",
                    "",
                )
            )

        if item.get(
            "memo"
        ):
            st.write(
                "📝 "
                + item.get(
                    "memo",
                    "",
                )
            )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ モノを編集・移動・削除"
):
    if not items:
        st.caption(
            "まだ登録されていません。"
        )

    for item in sorted(
        items,
        key=lambda value: (
            value.get(
                "name",
                "",
            )
        ),
    ):
        item_id = item.get(
            "id",
            "",
        )

        with st.expander(
            item.get(
                "category",
                "📦",
            )
            + " "
            + item.get(
                "name",
                "",
            )
        ):
            edit_name = st.text_input(
                "名前",
                value=item.get(
                    "name",
                    "",
                ),
                key=(
                    "edit_name_"
                    + item_id
                ),
            )

            current_category = (
                item.get(
                    "category",
                    "📦 その他",
                )
            )

            category_index = (
                CATEGORIES.index(
                    current_category
                )
                if current_category
                in CATEGORIES
                else len(
                    CATEGORIES
                ) - 1
            )

            edit_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=category_index,
                    key=(
                        "edit_category_"
                        + item_id
                    ),
                )
            )

            col1, col2 = st.columns(2)

            with col1:
                edit_room = (
                    st.text_input(
                        "部屋",
                        value=item.get(
                            "room",
                            "",
                        ),
                        key=(
                            "edit_room_"
                            + item_id
                        ),
                    )
                )

                edit_position = (
                    st.text_input(
                        "位置",
                        value=item.get(
                            "position",
                            "",
                        ),
                        key=(
                            "edit_position_"
                            + item_id
                        ),
                    )
                )

            with col2:
                edit_place = (
                    st.text_input(
                        "場所",
                        value=item.get(
                            "place",
                            "",
                        ),
                        key=(
                            "edit_place_"
                            + item_id
                        ),
                    )
                )

                edit_container = (
                    st.text_input(
                        "入れ物",
                        value=item.get(
                            "container",
                            "",
                        ),
                        key=(
                            "edit_container_"
                            + item_id
                        ),
                    )
                )

            current_importance = int(
                item.get(
                    "importance",
                    1,
                )
            )

            edit_importance = (
                st.select_slider(
                    "重要度",
                    options=[
                        1,
                        2,
                        3,
                    ],
                    value=current_importance,
                    format_func=lambda value: (
                        IMPORTANCE[
                            value
                        ]
                    ),
                    key=(
                        "edit_importance_"
                        + item_id
                    ),
                )
            )

            edit_tags = st.text_input(
                "検索タグ",
                value=item.get(
                    "tags",
                    "",
                ),
                key=(
                    "edit_tags_"
                    + item_id
                ),
            )

            edit_memo = st.text_area(
                "メモ",
                value=item.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + item_id
                ),
            )

            edit_favorite = (
                st.checkbox(
                    "⭐ お気に入り",
                    value=item.get(
                        "favorite",
                        False,
                    ),
                    key=(
                        "edit_favorite_"
                        + item_id
                    ),
                )
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_name.strip()
                    ):
                        st.warning(
                            "名前を入力してね。"
                        )

                    else:
                        update_item(
                            data,
                            item_id,
                            edit_name.strip(),
                            edit_category,
                            edit_room.strip(),
                            edit_place.strip(),
                            edit_position.strip(),
                            edit_container.strip(),
                            edit_tags.strip(),
                            edit_memo.strip(),
                            edit_importance,
                            edit_favorite,
                        )

                        st.rerun()

            with col2:
                if st.button(
                    "🗑️ 完全削除",
                    key=(
                        "delete_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    delete_item(
                        data,
                        item_id,
                    )

                    st.rerun()


# =========================================================
# JSONバックアップ
# =========================================================

st.divider()

with st.expander(
    "💾 データ管理"
):
    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            "where_did_i_put_it_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "「どこだっけ？」を、"
    "検索できるように。🔍📦"
)
