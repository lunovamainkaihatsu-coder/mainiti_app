import json
import os
import uuid
from datetime import date, datetime

import streamlit as st


st.set_page_config(
    page_title="プレゼント管理",
    page_icon="🎁",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "gift_data.json"
)

DEFAULT_DATA = {
    "people": [],
    "gifts": [],
    "wishlists": []
}


# =====================================
# データ保存・読み込み
# =====================================

def save_data(data):
    """データをJSONへ保存する"""
    os.makedirs(DATA_DIR, exist_ok=True)

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
    """JSONからデータを読み込む"""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return {
            "people": [],
            "gifts": [],
            "wishlists": []
        }

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError

        data.setdefault("people", [])
        data.setdefault("gifts", [])
        data.setdefault("wishlists", [])

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        save_data(DEFAULT_DATA)

        return {
            "people": [],
            "gifts": [],
            "wishlists": []
        }


# =====================================
# 人物管理
# =====================================

def add_person(
    data,
    name,
    relationship,
    birthday,
    budget,
    favorite_things,
    memo
):
    """相手を登録する"""

    new_person = {
        "id": str(uuid.uuid4()),
        "name": name,
        "relationship": relationship,
        "birthday": str(birthday),
        "budget": budget,
        "favorite_things": favorite_things,
        "memo": memo,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["people"].append(new_person)
    save_data(data)


def delete_person(data, person_id):
    """相手と関連データを削除する"""

    data["people"] = [
        person
        for person in data["people"]
        if person.get("id") != person_id
    ]

    data["gifts"] = [
        gift
        for gift in data["gifts"]
        if gift.get("person_id") != person_id
    ]

    data["wishlists"] = [
        item
        for item in data["wishlists"]
        if item.get("person_id") != person_id
    ]

    save_data(data)


# =====================================
# プレゼント履歴
# =====================================

def add_gift(
    data,
    person_id,
    gift_name,
    gift_date,
    event_name,
    price,
    reaction,
    memo
):
    """プレゼント履歴を追加する"""

    new_gift = {
        "id": str(uuid.uuid4()),
        "person_id": person_id,
        "gift_name": gift_name,
        "gift_date": str(gift_date),
        "event_name": event_name,
        "price": price,
        "reaction": reaction,
        "memo": memo,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["gifts"].append(new_gift)
    save_data(data)


def delete_gift(data, gift_id):
    """プレゼント履歴を削除する"""

    data["gifts"] = [
        gift
        for gift in data["gifts"]
        if gift.get("id") != gift_id
    ]

    save_data(data)


# =====================================
# 欲しいもの管理
# =====================================

def add_wishlist_item(
    data,
    person_id,
    item_name,
    priority,
    expected_price,
    memo
):
    """欲しいものを登録する"""

    new_item = {
        "id": str(uuid.uuid4()),
        "person_id": person_id,
        "item_name": item_name,
        "priority": priority,
        "expected_price": expected_price,
        "memo": memo,
        "purchased": False,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    data["wishlists"].append(new_item)
    save_data(data)


def update_wishlist_status(
    data,
    item_id,
    purchased
):
    """購入済み状態を変更する"""

    for item in data["wishlists"]:
        if item.get("id") == item_id:
            item["purchased"] = purchased
            break

    save_data(data)


def delete_wishlist_item(data, item_id):
    """欲しいものを削除する"""

    data["wishlists"] = [
        item
        for item in data["wishlists"]
        if item.get("id") != item_id
    ]

    save_data(data)


# =====================================
# 日付計算
# =====================================

def parse_date(date_text):
    """文字列をdate型へ変換する"""

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


def get_next_birthday(birthday):
    """次回の誕生日を返す"""

    today = date.today()

    try:
        next_birthday = date(
            today.year,
            birthday.month,
            birthday.day
        )

    except ValueError:
        next_birthday = date(
            today.year,
            2,
            28
        )

    if next_birthday < today:
        try:
            next_birthday = date(
                today.year + 1,
                birthday.month,
                birthday.day
            )

        except ValueError:
            next_birthday = date(
                today.year + 1,
                2,
                28
            )

    return next_birthday


def get_days_until_birthday(person):
    """次の誕生日までの日数を返す"""

    birthday = parse_date(
        person.get("birthday", "")
    )

    if birthday is None:
        return 99999

    next_birthday = get_next_birthday(
        birthday
    )

    return (
        next_birthday - date.today()
    ).days


def format_price(price):
    """金額を日本円形式で表示する"""

    return f"¥{int(price):,}"


def get_person_name(data, person_id):
    """人物IDから名前を取得する"""

    for person in data["people"]:
        if person.get("id") == person_id:
            return person.get(
                "name",
                "不明"
            )

    return "不明"


# =====================================
# データ読み込み
# =====================================

data = load_data()

people = sorted(
    data["people"],
    key=get_days_until_birthday
)


# =====================================
# タイトル
# =====================================

st.title("🎁 プレゼント管理")

st.caption(
    "大切な人への贈り物と、"
    "思い出をまとめて管理します。"
)


# =====================================
# 集計
# =====================================

total_people = len(
    data["people"]
)

total_gifts = len(
    data["gifts"]
)

total_spent = sum(
    int(gift.get("price", 0))
    for gift in data["gifts"]
)

unpurchased_items = sum(
    1
    for item in data["wishlists"]
    if not item.get(
        "purchased",
        False
    )
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 登録人数",
        f"{total_people}人"
    )

with col2:
    st.metric(
        "🎁 プレゼント数",
        f"{total_gifts}個"
    )

with col3:
    st.metric(
        "💰 合計金額",
        format_price(total_spent)
    )

with col4:
    st.metric(
        "💡 欲しいもの候補",
        f"{unpurchased_items}件"
    )


st.divider()


# =====================================
# 次の誕生日
# =====================================

st.header("🎂 次の誕生日")

if not people:
    st.info(
        "まだ相手が登録されていません。"
    )

else:
    nearest_person = people[0]

    nearest_days = get_days_until_birthday(
        nearest_person
    )

    birthday = parse_date(
        nearest_person.get(
            "birthday",
            ""
        )
    )

    next_birthday = get_next_birthday(
        birthday
    )

    with st.container(border=True):
        birthday_col1, birthday_col2 = (
            st.columns([3, 1])
        )

        with birthday_col1:
            st.subheader(
                f"🎂 "
                f"{nearest_person.get('name', '')}"
            )

            st.write(
                nearest_person.get(
                    "relationship",
                    ""
                )
            )

            st.caption(
                next_birthday.strftime(
                    "%Y年%m月%d日"
                )
            )

        with birthday_col2:
            if nearest_days == 0:
                st.metric(
                    "誕生日",
                    "今日！"
                )

            else:
                st.metric(
                    "誕生日まで",
                    f"あと{nearest_days}日"
                )

        if nearest_days <= 7:
            st.warning(
                "もうすぐ誕生日です！"
                "プレゼントを確認しよう。"
            )

        elif nearest_days <= 30:
            st.info(
                "そろそろプレゼントを"
                "考え始める時期です。"
            )


st.divider()


# =====================================
# タブ
# =====================================

person_tab, gift_tab, wishlist_tab, history_tab = (
    st.tabs(
        [
            "👥 相手",
            "🎁 プレゼント登録",
            "💡 欲しいもの",
            "📚 履歴"
        ]
    )
)


# =====================================
# 相手タブ
# =====================================

with person_tab:
    st.header("➕ 相手を登録")

    with st.form(
        "person_form",
        clear_on_submit=True
    ):
        person_col1, person_col2 = (
            st.columns(2)
        )

        with person_col1:
            person_name = st.text_input(
                "名前",
                placeholder="例：妻"
            )

            relationship = st.selectbox(
                "関係",
                [
                    "家族",
                    "友達",
                    "恋人",
                    "親戚",
                    "会社",
                    "その他"
                ]
            )

            birthday = st.date_input(
                "誕生日",
                value=date.today()
            )

        with person_col2:
            budget = st.number_input(
                "プレゼント予算",
                min_value=0,
                value=5000,
                step=500
            )

            favorite_things = st.text_area(
                "好きなもの",
                placeholder=(
                    "例：青色、コーヒー、"
                    "ディズニー"
                )
            )

            person_memo = st.text_area(
                "メモ",
                placeholder=(
                    "サイズや苦手なものなど"
                )
            )

        person_submit = st.form_submit_button(
            "👥 相手を登録",
            use_container_width=True
        )

        if person_submit:
            cleaned_name = person_name.strip()

            duplicate_exists = any(
                person.get(
                    "name",
                    ""
                ).lower() == cleaned_name.lower()
                for person in data["people"]
            )

            if not cleaned_name:
                st.error(
                    "名前を入力してください。"
                )

            elif duplicate_exists:
                st.warning(
                    "同じ名前の相手が"
                    "すでに登録されています。"
                )

            else:
                add_person(
                    data=data,
                    name=cleaned_name,
                    relationship=relationship,
                    birthday=birthday,
                    budget=int(budget),
                    favorite_things=(
                        favorite_things.strip()
                    ),
                    memo=person_memo.strip()
                )

                st.success(
                    f"「{cleaned_name}」を"
                    "登録しました！"
                )

                st.rerun()

    st.divider()

    st.header("👥 登録済み")

    if not people:
        st.info(
            "相手を登録すると"
            "ここに表示されます。"
        )

    for person in people:
        person_id = person.get(
            "id",
            ""
        )

        person_name = person.get(
            "name",
            "名前未設定"
        )

        days_until = get_days_until_birthday(
            person
        )

        person_gifts = [
            gift
            for gift in data["gifts"]
            if gift.get(
                "person_id"
            ) == person_id
        ]

        spent_amount = sum(
            int(gift.get("price", 0))
            for gift in person_gifts
        )

        with st.container(border=True):
            info_col, birthday_col = (
                st.columns([3, 1])
            )

            with info_col:
                st.subheader(
                    f"👤 {person_name}"
                )

                st.caption(
                    person.get(
                        "relationship",
                        ""
                    )
                )

            with birthday_col:
                if days_until == 0:
                    st.metric(
                        "誕生日",
                        "今日！"
                    )

                else:
                    st.metric(
                        "誕生日まで",
                        f"{days_until}日"
                    )

            detail_col1, detail_col2 = (
                st.columns(2)
            )

            with detail_col1:
                st.write(
                    "**予算**"
                )

                st.write(
                    format_price(
                        person.get(
                            "budget",
                            0
                        )
                    )
                )

            with detail_col2:
                st.write(
                    "**これまでの金額**"
                )

                st.write(
                    format_price(
                        spent_amount
                    )
                )

            favorite_things = person.get(
                "favorite_things",
                ""
            )

            if favorite_things:
                st.markdown(
                    "#### ❤️ 好きなもの"
                )
                st.write(
                    favorite_things
                )

            memo = person.get(
                "memo",
                ""
            )

            if memo:
                st.markdown(
                    "#### 📝 メモ"
                )
                st.write(memo)

            with st.expander(
                "🗑️ この相手を削除"
            ):
                st.warning(
                    "関連するプレゼント履歴と"
                    "欲しいものも削除されます。"
                )

                confirm_delete = st.checkbox(
                    "削除を確認しました",
                    key=(
                        f"confirm_person_"
                        f"{person_id}"
                    )
                )

                if st.button(
                    "相手を削除",
                    key=(
                        f"delete_person_"
                        f"{person_id}"
                    ),
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True
                ):
                    delete_person(
                        data,
                        person_id
                    )

                    st.rerun()


# =====================================
# プレゼント登録タブ
# =====================================

with gift_tab:
    st.header("🎁 プレゼントを記録")

    if not data["people"]:
        st.info(
            "先に「相手」タブから"
            "相手を登録してください。"
        )

    else:
        person_options = {
            person.get("name", ""):
            person.get("id", "")
            for person in data["people"]
        }

        with st.form(
            "gift_form",
            clear_on_submit=True
        ):
            gift_col1, gift_col2 = (
                st.columns(2)
            )

            with gift_col1:
                selected_person_name = (
                    st.selectbox(
                        "贈った相手",
                        list(
                            person_options.keys()
                        )
                    )
                )

                gift_name = st.text_input(
                    "プレゼント名",
                    placeholder="例：絵本"
                )

                gift_date = st.date_input(
                    "贈った日",
                    value=date.today()
                )

                event_name = st.selectbox(
                    "イベント",
                    [
                        "誕生日",
                        "クリスマス",
                        "記念日",
                        "母の日",
                        "父の日",
                        "お祝い",
                        "その他"
                    ]
                )

            with gift_col2:
                price = st.number_input(
                    "金額",
                    min_value=0,
                    value=3000,
                    step=100
                )

                reaction = st.selectbox(
                    "喜び度",
                    [
                        "⭐",
                        "⭐⭐",
                        "⭐⭐⭐",
                        "⭐⭐⭐⭐",
                        "⭐⭐⭐⭐⭐"
                    ],
                    index=3
                )

                gift_memo = st.text_area(
                    "感想・メモ",
                    placeholder=(
                        "とても喜んでくれた"
                    )
                )

            gift_submit = (
                st.form_submit_button(
                    "🎁 プレゼントを記録",
                    use_container_width=True
                )
            )

            if gift_submit:
                cleaned_gift_name = (
                    gift_name.strip()
                )

                if not cleaned_gift_name:
                    st.error(
                        "プレゼント名を"
                        "入力してください。"
                    )

                else:
                    add_gift(
                        data=data,
                        person_id=person_options[
                            selected_person_name
                        ],
                        gift_name=(
                            cleaned_gift_name
                        ),
                        gift_date=gift_date,
                        event_name=event_name,
                        price=int(price),
                        reaction=reaction,
                        memo=gift_memo.strip()
                    )

                    st.success(
                        "プレゼントを"
                        "記録しました！"
                    )

                    st.rerun()


# =====================================
# 欲しいものタブ
# =====================================

with wishlist_tab:
    st.header("💡 欲しいもの候補")

    if not data["people"]:
        st.info(
            "先に相手を登録してください。"
        )

    else:
        person_options = {
            person.get("name", ""):
            person.get("id", "")
            for person in data["people"]
        }

        with st.form(
            "wishlist_form",
            clear_on_submit=True
        ):
            wish_col1, wish_col2 = (
                st.columns(2)
            )

            with wish_col1:
                selected_person_name = (
                    st.selectbox(
                        "相手",
                        list(
                            person_options.keys()
                        ),
                        key="wishlist_person"
                    )
                )

                item_name = st.text_input(
                    "欲しいもの・候補",
                    placeholder=(
                        "例：新しい財布"
                    )
                )

                priority = st.selectbox(
                    "優先度",
                    [
                        "高",
                        "中",
                        "低"
                    ]
                )

            with wish_col2:
                expected_price = (
                    st.number_input(
                        "予想金額",
                        min_value=0,
                        value=3000,
                        step=500
                    )
                )

                wishlist_memo = (
                    st.text_area(
                        "メモ",
                        placeholder=(
                            "好きな色やブランド"
                        )
                    )
                )

            wishlist_submit = (
                st.form_submit_button(
                    "💡 候補を登録",
                    use_container_width=True
                )
            )

            if wishlist_submit:
                cleaned_item_name = (
                    item_name.strip()
                )

                if not cleaned_item_name:
                    st.error(
                        "欲しいものを"
                        "入力してください。"
                    )

                else:
                    add_wishlist_item(
                        data=data,
                        person_id=person_options[
                            selected_person_name
                        ],
                        item_name=(
                            cleaned_item_name
                        ),
                        priority=priority,
                        expected_price=int(
                            expected_price
                        ),
                        memo=(
                            wishlist_memo.strip()
                        )
                    )

                    st.success(
                        "欲しいもの候補を"
                        "登録しました！"
                    )

                    st.rerun()

        st.divider()

        if not data["wishlists"]:
            st.info(
                "まだ候補がありません。"
            )

        else:
            for item in data["wishlists"]:
                item_id = item.get(
                    "id",
                    ""
                )

                person_name = get_person_name(
                    data,
                    item.get(
                        "person_id",
                        ""
                    )
                )

                purchased = item.get(
                    "purchased",
                    False
                )

                with st.container(
                    border=True
                ):
                    item_col1, item_col2 = (
                        st.columns([3, 1])
                    )

                    with item_col1:
                        mark = (
                            "✅"
                            if purchased
                            else "💡"
                        )

                        st.subheader(
                            f"{mark} "
                            f"{item.get('item_name', '')}"
                        )

                        st.caption(
                            f"{person_name} "
                            f"／ 優先度："
                            f"{item.get('priority', '')}"
                        )

                    with item_col2:
                        st.metric(
                            "予想金額",
                            format_price(
                                item.get(
                                    "expected_price",
                                    0
                                )
                            )
                        )

                    memo = item.get(
                        "memo",
                        ""
                    )

                    if memo:
                        st.write(memo)

                    new_status = st.checkbox(
                        "購入済み",
                        value=purchased,
                        key=(
                            f"purchased_"
                            f"{item_id}"
                        )
                    )

                    if new_status != purchased:
                        update_wishlist_status(
                            data,
                            item_id,
                            new_status
                        )

                        st.rerun()

                    if st.button(
                        "🗑️ 候補を削除",
                        key=(
                            f"delete_wish_"
                            f"{item_id}"
                        )
                    ):
                        delete_wishlist_item(
                            data,
                            item_id
                        )

                        st.rerun()


# =====================================
# 履歴タブ
# =====================================

with history_tab:
    st.header("📚 プレゼント履歴")

    if not data["gifts"]:
        st.info(
            "まだプレゼント履歴が"
            "ありません。"
        )

    else:
        person_names = [
            person.get("name", "")
            for person in data["people"]
        ]

        history_filter = st.selectbox(
            "相手で絞り込み",
            ["すべて"] + person_names
        )

        filtered_gifts = data["gifts"]

        if history_filter != "すべて":
            selected_person_id = next(
                (
                    person.get("id")
                    for person in data["people"]
                    if person.get("name")
                    == history_filter
                ),
                None
            )

            filtered_gifts = [
                gift
                for gift in data["gifts"]
                if gift.get(
                    "person_id"
                ) == selected_person_id
            ]

        filtered_gifts = sorted(
            filtered_gifts,
            key=lambda gift: gift.get(
                "gift_date",
                ""
            ),
            reverse=True
        )

        for gift in filtered_gifts:
            gift_id = gift.get(
                "id",
                ""
            )

            person_name = get_person_name(
                data,
                gift.get(
                    "person_id",
                    ""
                )
            )

            with st.container(
                border=True
            ):
                gift_col1, gift_col2 = (
                    st.columns([3, 1])
                )

                with gift_col1:
                    st.subheader(
                        f"🎁 "
                        f"{gift.get('gift_name', '')}"
                    )

                    st.caption(
                        f"{person_name} "
                        f"／ "
                        f"{gift.get('event_name', '')} "
                        f"／ "
                        f"{gift.get('gift_date', '')}"
                    )

                with gift_col2:
                    st.metric(
                        "金額",
                        format_price(
                            gift.get(
                                "price",
                                0
                            )
                        )
                    )

                st.write(
                    f"喜び度："
                    f"{gift.get('reaction', '')}"
                )

                gift_memo = gift.get(
                    "memo",
                    ""
                )

                if gift_memo:
                    st.write(gift_memo)

                with st.expander(
                    "🗑️ この履歴を削除"
                ):
                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_gift_"
                                f"{gift_id}"
                            )
                        )
                    )

                    if st.button(
                        "履歴を削除",
                        key=(
                            f"delete_gift_"
                            f"{gift_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_gift(
                            data,
                            gift_id
                        )

                        st.rerun()


st.divider()

st.success(
    "贈ったものだけでなく、"
    "相手を想った時間も大切な思い出です。🎁"
)
