import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="300日できたこと図鑑",
    page_icon="🏆",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "achievements.json",
)

CATEGORIES = [
    "💻 アプリ開発",
    "📚 学習",
    "💡 アイデア",
    "🎨 創作",
    "🚀 公開・挑戦",
    "🌱 生活・習慣",
    "💼 仕事",
    "👨‍👩‍👧 家族",
    "✨ その他",
]

SIZES = [
    "🌱 小さな一歩",
    "🔥 頑張った",
    "🏆 大きな達成",
]

ERAS = [
    (1, 50, "🌱 はじまり"),
    (51, 100, "🛠️ 試行錯誤"),
    (101, 150, "🔥 継続"),
    (151, 200, "🚀 進化"),
    (201, 250, "🌌 積み重ね"),
    (251, 300, "🏆 300への道"),
]

MILESTONES = {
    1: "🌱 最初の一歩",
    50: "🎉 50本",
    100: "🔥 100本",
    150: "🚀 150本",
    200: "🌌 200本",
    250: "📚 250本",
    300: "🏆 300本",
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


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return None


def format_date(value):
    parsed = parse_date(value)

    if not parsed:
        return "-"

    return parsed.strftime(
        "%Y/%m/%d"
    )


def short_text(
    text,
    length=35,
):
    text = text or ""

    if len(text) <= length:
        return text

    return text[:length] + "…"


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "achievements": [],
        "day300_message": {
            "thoughts": "",
            "next_creation": "",
            "future_message": "",
            "updated_at": "",
        },
        "next_chapter": {
            "want_to_make": "",
            "want_to_grow": "",
            "next_goal": "",
            "updated_at": "",
        },
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


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = empty_data()
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
            data = empty_data()

        data.setdefault(
            "achievements",
            [],
        )

        data.setdefault(
            "day300_message",
            {},
        )

        data.setdefault(
            "next_chapter",
            {},
        )

        for key in [
            "thoughts",
            "next_creation",
            "future_message",
            "updated_at",
        ]:
            data[
                "day300_message"
            ].setdefault(
                key,
                "",
            )

        for key in [
            "want_to_make",
            "want_to_grow",
            "next_goal",
            "updated_at",
        ]:
            data[
                "next_chapter"
            ].setdefault(
                key,
                "",
            )

        for item in data[
            "achievements"
        ]:
            if not item.get("id"):
                item["id"] = create_id()

            item.setdefault(
                "day",
                1,
            )
            item.setdefault(
                "date",
                str(date.today()),
            )
            item.setdefault(
                "title",
                "",
            )
            item.setdefault(
                "category",
                "✨ その他",
            )
            item.setdefault(
                "size",
                "🌱 小さな一歩",
            )
            item.setdefault(
                "memo",
                "",
            )
            item.setdefault(
                "favorite",
                False,
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
        data = empty_data()
        save_data(data)
        return data


# =========================================================
# 取得
# =========================================================

def get_achievement(
    data,
    achievement_id,
):
    return next(
        (
            item
            for item
            in data["achievements"]
            if item.get("id")
            == achievement_id
        ),
        None,
    )


def achievements_for_day(
    items,
    day_number,
):
    return [
        item
        for item in items
        if int(
            item.get(
                "day",
                0,
            )
        ) == day_number
    ]


def sorted_achievements(
    items,
    reverse=False,
):
    return sorted(
        items,
        key=lambda item: (
            int(
                item.get(
                    "day",
                    0,
                )
            ),
            item.get(
                "date",
                "",
            ),
            item.get(
                "created_at",
                "",
            ),
        ),
        reverse=reverse,
    )


def achievements_for_era(
    items,
    start_day,
    end_day,
):
    return [
        item
        for item in items
        if start_day
        <= int(
            item.get(
                "day",
                0,
            )
        )
        <= end_day
    ]


# =========================================================
# CRUD
# =========================================================

def add_achievement(
    data,
    day_number,
    achievement_date,
    title,
    category,
    size,
    memo,
    favorite,
):
    item = {
        "id": create_id(),
        "day": int(
            day_number
        ),
        "date": str(
            achievement_date
        ),
        "title": title,
        "category": category,
        "size": size,
        "memo": memo,
        "favorite": favorite,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["achievements"].append(
        item
    )

    save_data(data)

    return item


def update_achievement(
    data,
    achievement_id,
    day_number,
    achievement_date,
    title,
    category,
    size,
    memo,
):
    item = get_achievement(
        data,
        achievement_id,
    )

    if not item:
        return False

    item["day"] = int(
        day_number
    )
    item["date"] = str(
        achievement_date
    )
    item["title"] = title
    item["category"] = category
    item["size"] = size
    item["memo"] = memo
    item["updated_at"] = now_text()

    save_data(data)

    return True


def toggle_favorite(
    data,
    achievement_id,
):
    item = get_achievement(
        data,
        achievement_id,
    )

    if not item:
        return

    item["favorite"] = not item.get(
        "favorite",
        False,
    )

    item["updated_at"] = now_text()

    save_data(data)


def delete_achievement(
    data,
    achievement_id,
):
    data["achievements"] = [
        item
        for item in data["achievements"]
        if item.get("id")
        != achievement_id
    ]

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 1250px;
    }

    [data-testid="stMetric"] {
        padding: 16px;
        border-radius: 18px;
        background: rgba(215, 170, 60, 0.07);
        border: 1px solid rgba(215, 170, 60, 0.18);
    }

    .day300-hero {
        text-align: center;
        padding: 55px 25px;
        border-radius: 30px;
        margin-bottom: 30px;
        background:
            linear-gradient(
                135deg,
                rgba(245, 190, 60, 0.20),
                rgba(120, 90, 220, 0.13)
            );
        border:
            1px solid
            rgba(220, 175, 70, 0.22);
    }

    .day300-hero h1 {
        font-size: 3rem;
        margin-bottom: 8px;
    }

    .day300-hero h2 {
        margin-top: 0;
        opacity: 0.90;
    }

    .day300-hero p {
        font-size: 1.08rem;
        opacity: 0.82;
    }

    .milestone {
        padding: 18px;
        border-radius: 18px;
        background:
            rgba(220, 175, 70, 0.06);
        border:
            1px solid
            rgba(220, 175, 70, 0.15);
        margin-bottom: 10px;
    }

    .final-card {
        text-align: center;
        padding: 45px 30px;
        margin-top: 30px;
        border-radius: 28px;
        background:
            linear-gradient(
                135deg,
                rgba(245, 190, 60, 0.16),
                rgba(90, 120, 230, 0.10)
            );
        border:
            1px solid
            rgba(220, 175, 70, 0.20);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 準備
# =========================================================

data = load_data()
items = data["achievements"]
today = date.today()

unique_days = {
    int(
        item.get(
            "day",
            0,
        )
    )
    for item in items
    if 1
    <= int(
        item.get(
            "day",
            0,
        )
    )
    <= 300
}

registered_days = len(
    unique_days
)

progress = min(
    registered_days / 300,
    1.0,
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="day300-hero">
        <div style="font-size:1.2rem;">
            🏆 DAY 300 🏆
        </div>
        <h1>300日できたこと図鑑</h1>
        <h2>300 APP JOURNEY</h2>
        <p>
            300回の「できた」を、
            一つの景色にする。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"### 🏆 {registered_days} / 300 Days"
)

st.progress(
    progress
)

if registered_days >= 300:
    st.success(
        "🎉 300 / 300 COMPLETE！"
    )

else:
    st.caption(
        f"図鑑には現在 "
        f"{registered_days} / 300 Day "
        "が登録されています。"
    )


# =========================================================
# ダッシュボード
# =========================================================

st.divider()

st.subheader(
    "🏆 300 APP JOURNEY"
)

favorites = [
    item
    for item in items
    if item.get(
        "favorite",
        False,
    )
]

big_achievements = [
    item
    for item in items
    if item.get(
        "size"
    ) == "🏆 大きな達成"
]

used_categories = {
    item.get(
        "category"
    )
    for item in items
    if item.get(
        "category"
    )
}

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "📚 できたこと",
    f"{len(items)}個",
)

c2.metric(
    "📅 登録Day",
    f"{registered_days}/300",
)

c3.metric(
    "⭐ 大切な記録",
    f"{len(favorites)}個",
)

c4.metric(
    "🏆 大きな達成",
    f"{len(big_achievements)}個",
)

if items:
    sorted_items = (
        sorted_achievements(
            items
        )
    )

    first_item = sorted_items[0]
    latest_item = sorted_items[-1]

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "🌱 最初の記録\n\n"
            f"**DAY {int(first_item.get('day')):03d}**\n\n"
            f"{first_item.get('title')}"
        )

    with col2:
        st.success(
            "🏆 最新の記録\n\n"
            f"**DAY {int(latest_item.get('day')):03d}**\n\n"
            f"{latest_item.get('title')}"
        )


# =========================================================
# 新しい「できた」
# =========================================================

st.divider()

st.subheader(
    "✨ できたことを残す"
)

with st.form(
    "new_achievement",
    clear_on_submit=True,
):
    col1, col2 = st.columns(2)

    with col1:
        day_number = st.number_input(
            "DAY",
            min_value=1,
            max_value=300,
            value=300,
            step=1,
        )

    with col2:
        achievement_date = (
            st.date_input(
                "日付",
                value=today,
                max_value=today,
            )
        )

    title = st.text_input(
        "できたこと",
        placeholder=(
            "例：300本目の"
            "アプリを完成させた"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

    with col2:
        size = st.selectbox(
            "大きさ",
            SIZES,
            index=2,
        )

    memo = st.text_area(
        "ひとこと",
        placeholder=(
            "例：ついに300本。"
        ),
    )

    favorite = st.checkbox(
        "⭐ 忘れたくない記録にする"
    )

    submitted = (
        st.form_submit_button(
            "🏆 できたを残す",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        clean_title = title.strip()

        if not clean_title:
            st.warning(
                "できたことを入力してね。"
            )

        else:
            new_item = add_achievement(
                data=data,
                day_number=day_number,
                achievement_date=(
                    achievement_date
                ),
                title=clean_title,
                category=category,
                size=size,
                memo=memo.strip(),
                favorite=favorite,
            )

            st.session_state[
                "just_added"
            ] = new_item.get(
                "id"
            )

            st.rerun()


# =========================================================
# 保存直後
# =========================================================

if st.session_state.get(
    "just_added"
):
    added_item = get_achievement(
        data,
        st.session_state[
            "just_added"
        ],
    )

    if added_item:
        st.success(
            "🎉 記録しました！\n\n"
            f"**DAY "
            f"{int(added_item.get('day')):03d}**\n\n"
            f"{added_item.get('size')} "
            f"{added_item.get('title')}"
        )

    del st.session_state[
        "just_added"
    ]


# =========================================================
# 300日のロードマップ
# =========================================================

st.divider()

st.subheader(
    "🗺️ 300日のロードマップ"
)

era_rows = []

for start_day, end_day, era_name in ERAS:
    era_items = achievements_for_era(
        items,
        start_day,
        end_day,
    )

    era_days = {
        int(
            item.get(
                "day",
                0,
            )
        )
        for item in era_items
    }

    category_counts = Counter(
        item.get(
            "category"
        )
        for item in era_items
    )

    top_category = (
        category_counts.most_common(
            1
        )[0][0]
        if category_counts
        else "-"
    )

    era_big = sum(
        1
        for item in era_items
        if item.get(
            "size"
        ) == "🏆 大きな達成"
    )

    era_favorites = sum(
        1
        for item in era_items
        if item.get(
            "favorite",
            False,
        )
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### {era_name}"
        )

        st.caption(
            f"DAY {start_day:03d}"
            f" ━━━ "
            f"DAY {end_day:03d}"
        )

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "登録Day",
            f"{len(era_days)}/50",
        )

        c2.metric(
            "できた",
            len(era_items),
        )

        c3.metric(
            "🏆",
            era_big,
        )

        c4.metric(
            "⭐",
            era_favorites,
        )

        st.caption(
            f"最も多いカテゴリー："
            f"{top_category}"
        )

    era_rows.append(
        {
            "時代": era_name,
            "登録Day": len(
                era_days
            ),
            "できた": len(
                era_items
            ),
            "🏆": era_big,
            "⭐": era_favorites,
        }
    )


# =========================================================
# 50本ごとの比較
# =========================================================

st.markdown(
    "#### 📈 50Dayごとの景色"
)

era_df = pd.DataFrame(
    era_rows
)

st.dataframe(
    era_df,
    hide_index=True,
    use_container_width=True,
)


# =========================================================
# マイルストーン
# =========================================================

st.divider()

st.subheader(
    "🏅 マイルストーン"
)

for milestone_day, milestone_name in (
    MILESTONES.items()
):
    milestone_items = (
        achievements_for_day(
            items,
            milestone_day,
        )
    )

    with st.container(
        border=True
    ):
        st.markdown(
            f"### {milestone_name}"
        )

        st.caption(
            f"DAY {milestone_day:03d}"
        )

        if not milestone_items:
            st.write(
                "まだ記録されていません。"
            )

        else:
            for item in milestone_items:
                star = (
                    " ⭐"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else ""
                )

                st.write(
                    f"{item.get('size')} "
                    f"**{item.get('title')}**"
                    f"{star}"
                )

                if item.get(
                    "memo"
                ):
                    st.caption(
                        item.get(
                            "memo"
                        )
                    )


# =========================================================
# THEN → NOW
# =========================================================

if items:
    st.divider()

    st.subheader(
        "🕰️ 最初と今"
    )

    sorted_items = (
        sorted_achievements(
            items
        )
    )

    first_day_number = min(
        int(
            item.get(
                "day",
                1,
            )
        )
        for item in items
    )

    last_day_number = max(
        int(
            item.get(
                "day",
                1,
            )
        )
        for item in items
    )

    first_day_items = (
        achievements_for_day(
            items,
            first_day_number,
        )
    )

    last_day_items = (
        achievements_for_day(
            items,
            last_day_number,
        )
    )

    col1, col2, col3 = (
        st.columns(
            [4, 1, 4]
        )
    )

    with col1:
        st.markdown(
            "### 🌱 THEN"
        )

        st.markdown(
            f"## DAY "
            f"{first_day_number:03d}"
        )

        for item in first_day_items:
            st.write(
                f"「{item.get('title')}」"
            )

    with col2:
        st.markdown(
            "<h1 style='text-align:center;"
            "padding-top:45px;'>→</h1>",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            "### 🏆 NOW"
        )

        st.markdown(
            f"## DAY "
            f"{last_day_number:03d}"
        )

        for item in last_day_items:
            st.write(
                f"「{item.get('title')}」"
            )


# =========================================================
# カテゴリー分析
# =========================================================

if items:
    st.divider()

    st.subheader(
        "🧩 自分は何を積み上げてきた？"
    )

    category_counts = Counter(
        item.get(
            "category"
        )
        for item in items
    )

    category_df = pd.DataFrame(
        [
            {
                "カテゴリー": category,
                "記録数": (
                    category_counts.get(
                        category,
                        0,
                    )
                ),
            }
            for category in CATEGORIES
            if category_counts.get(
                category,
                0,
            ) > 0
        ]
    )

    if not category_df.empty:
        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )

        top_category = (
            category_counts.most_common(
                1
            )[0]
        )

        st.info(
            "この図鑑で最も多いのは "
            f"**{top_category[0]}** "
            f"（{top_category[1]}個）です。"
        )


# =========================================================
# 大きな達成
# =========================================================

if big_achievements:
    st.divider()

    st.subheader(
        "🏆 これは大きかった"
    )

    for item in sorted_achievements(
        big_achievements,
        reverse=True,
    ):
        with st.container(
            border=True
        ):
            st.markdown(
                f"### DAY "
                f"{int(item.get('day')):03d}"
            )

            st.write(
                f"🏆 **{item.get('title')}**"
            )

            st.caption(
                f"{format_date(item.get('date'))}"
                f" ｜ "
                f"{item.get('category')}"
            )

            if item.get(
                "memo"
            ):
                st.write(
                    f"💭 {item.get('memo')}"
                )


# =========================================================
# お気に入り
# =========================================================

if favorites:
    st.divider()

    st.subheader(
        "⭐ 忘れたくない瞬間"
    )

    for item in sorted_achievements(
        favorites,
        reverse=True,
    ):
        st.write(
            f"**DAY "
            f"{int(item.get('day')):03d}** "
            f"— {item.get('title')}"
        )


# =========================================================
# あの日の自分
# =========================================================

if items:
    st.divider()

    st.subheader(
        "🎲 あの日の自分"
    )

    item_ids = [
        item.get("id")
        for item in items
    ]

    random_id = (
        st.session_state.get(
            "random_achievement"
        )
    )

    if random_id not in item_ids:
        random_id = random.choice(
            item_ids
        )

        st.session_state[
            "random_achievement"
        ] = random_id

    random_item = get_achievement(
        data,
        random_id,
    )

    if random_item:
        with st.container(
            border=True
        ):
            st.markdown(
                f"## 🎲 DAY "
                f"{int(random_item.get('day')):03d}"
            )

            st.write(
                f"{random_item.get('size')} "
                f"**{random_item.get('title')}**"
            )

            st.caption(
                f"{format_date(random_item.get('date'))}"
                f" ｜ "
                f"{random_item.get('category')}"
            )

            if random_item.get(
                "memo"
            ):
                st.write(
                    random_item.get(
                        "memo"
                    )
                )

            distance = (
                300
                - int(
                    random_item.get(
                        "day",
                        300,
                    )
                )
            )

            if distance > 0:
                st.success(
                    f"この記録からDAY300まで、"
                    f"あと{distance}Day。"
                    "\n\n"
                    "この日の自分も、"
                    "今日につながっている。"
                )

    if st.button(
        "🎲 別の日を見る",
        use_container_width=True,
    ):
        alternatives = [
            item_id
            for item_id in item_ids
            if item_id
            != random_id
        ]

        if alternatives:
            st.session_state[
                "random_achievement"
            ] = random.choice(
                alternatives
            )

        st.rerun()


# =========================================================
# DAYガチャ
# =========================================================

if items:
    st.divider()

    st.subheader(
        "🔢 DAYを開く"
    )

    selected_day = st.number_input(
        "何日目を見る？",
        min_value=1,
        max_value=300,
        value=300,
        step=1,
        key="day_lookup",
    )

    selected_day_items = (
        achievements_for_day(
            items,
            int(selected_day),
        )
    )

    if selected_day_items:
        for item in selected_day_items:
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### DAY "
                    f"{int(selected_day):03d}"
                )

                st.write(
                    f"{item.get('size')} "
                    f"**{item.get('title')}**"
                )

                st.caption(
                    f"{format_date(item.get('date'))}"
                    f" ｜ "
                    f"{item.get('category')}"
                )

                if item.get(
                    "memo"
                ):
                    st.write(
                        item.get(
                            "memo"
                        )
                    )

    else:
        st.caption(
            "このDAYはまだ"
            "図鑑に登録されていません。"
        )


# =========================================================
# Day300メッセージ
# =========================================================

st.divider()

st.subheader(
    "💌 Day300の自分から"
)

message = data[
    "day300_message"
]

with st.form(
    "day300_message_form"
):
    thoughts = st.text_area(
        "300本まで来た今、何を思っていますか？",
        value=message.get(
            "thoughts",
            "",
        ),
        height=130,
    )

    next_creation = st.text_area(
        "これから何を作りたい？",
        value=message.get(
            "next_creation",
            "",
        ),
        height=100,
    )

    future_message = st.text_area(
        "未来の自分へ",
        value=message.get(
            "future_message",
            "",
        ),
        height=130,
    )

    if st.form_submit_button(
        "💌 Day300の言葉を保存",
        type="primary",
        use_container_width=True,
    ):
        data[
            "day300_message"
        ] = {
            "thoughts": (
                thoughts.strip()
            ),
            "next_creation": (
                next_creation.strip()
            ),
            "future_message": (
                future_message.strip()
            ),
            "updated_at": now_text(),
        }

        save_data(data)

        st.success(
            "💌 Day300の言葉を"
            "保存しました。"
        )


# =========================================================
# 次の章
# =========================================================

st.divider()

st.subheader(
    "🌅 300の、その先へ"
)

st.caption(
    "301本目を作らなくてもいい。"
    "新しく作ることも、"
    "今あるものを育てることも、"
    "次の一歩です。"
)

next_chapter = data[
    "next_chapter"
]

with st.form(
    "next_chapter_form"
):
    want_to_make = st.text_input(
        "🚀 次に作りたいもの",
        value=next_chapter.get(
            "want_to_make",
            "",
        ),
    )

    want_to_grow = st.text_input(
        "🌱 次に育てたいもの",
        value=next_chapter.get(
            "want_to_grow",
            "",
        ),
    )

    next_goal = st.text_area(
        "🎯 次の目標",
        value=next_chapter.get(
            "next_goal",
            "",
        ),
        height=100,
    )

    if st.form_submit_button(
        "🚀 次の章を保存",
        use_container_width=True,
    ):
        data[
            "next_chapter"
        ] = {
            "want_to_make": (
                want_to_make.strip()
            ),
            "want_to_grow": (
                want_to_grow.strip()
            ),
            "next_goal": (
                next_goal.strip()
            ),
            "updated_at": now_text(),
        }

        save_data(data)

        st.success(
            "🌅 次の章を保存しました。"
        )


# =========================================================
# 300日図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 300日図鑑"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "アプリ、Python、公開……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="library_category",
        )
    )

with col2:
    size_filter = st.selectbox(
        "大きさ",
        ["すべて"]
        + SIZES,
        key="library_size",
    )

col1, col2 = st.columns(2)

with col1:
    min_day = st.number_input(
        "DAY From",
        min_value=1,
        max_value=300,
        value=1,
        step=1,
    )

with col2:
    max_day = st.number_input(
        "DAY To",
        min_value=1,
        max_value=300,
        value=300,
        step=1,
    )

favorite_only = st.checkbox(
    "⭐ 大切な記録だけ",
    key="library_favorite",
)

filtered_items = []

for item in items:
    day_value = int(
        item.get(
            "day",
            0,
        )
    )

    if not (
        int(min_day)
        <= day_value
        <= int(max_day)
    ):
        continue

    if (
        category_filter
        != "すべて"
        and item.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        size_filter
        != "すべて"
        and item.get(
            "size"
        ) != size_filter
    ):
        continue

    if (
        favorite_only
        and not item.get(
            "favorite",
            False,
        )
    ):
        continue

    searchable = " ".join(
        [
            item.get(
                "title",
                "",
            ),
            item.get(
                "memo",
                "",
            ),
            item.get(
                "category",
                "",
            ),
        ]
    ).lower()

    if (
        search_text.strip()
        and search_text
        .strip()
        .lower()
        not in searchable
    ):
        continue

    filtered_items.append(
        item
    )

if not filtered_items:
    st.info(
        "条件に合う記録は"
        "ありません。"
    )

else:
    rows = []

    for item in sorted_achievements(
        filtered_items
    ):
        rows.append(
            {
                "DAY": (
                    f"{int(item.get('day')):03d}"
                ),
                "日付": format_date(
                    item.get(
                        "date"
                    )
                ),
                "できたこと": (
                    item.get(
                        "title",
                        "",
                    )
                ),
                "カテゴリー": (
                    item.get(
                        "category",
                        "",
                    )
                ),
                "大きさ": (
                    item.get(
                        "size",
                        "",
                    )
                ),
                "⭐": (
                    "⭐"
                    if item.get(
                        "favorite",
                        False,
                    )
                    else ""
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            rows
        ),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 記録を編集・削除"
):
    if not items:
        st.caption(
            "まだ記録がありません。"
        )

    else:
        edit_options = {}

        for item in sorted_achievements(
            items,
            reverse=True,
        ):
            label = (
                f"DAY "
                f"{int(item.get('day')):03d}"
                f" ｜ "
                f"{short_text(item.get('title'))}"
            )

            # 同じタイトルでも選べるようにIDを付与
            unique_label = (
                f"{label} "
                f"[{item.get('id')[:6]}]"
            )

            edit_options[
                unique_label
            ] = item.get(
                "id"
            )

        selected_label = (
            st.selectbox(
                "編集する記録",
                list(
                    edit_options.keys()
                ),
            )
        )

        selected_id = (
            edit_options[
                selected_label
            ]
        )

        selected = get_achievement(
            data,
            selected_id,
        )

        if selected:
            edit_day = st.number_input(
                "DAY",
                min_value=1,
                max_value=300,
                value=int(
                    selected.get(
                        "day",
                        1,
                    )
                ),
                step=1,
                key=(
                    "edit_day_"
                    + selected_id
                ),
            )

            selected_date = (
                parse_date(
                    selected.get(
                        "date"
                    )
                )
                or today
            )

            edit_date = st.date_input(
                "日付",
                value=selected_date,
                max_value=today,
                key=(
                    "edit_date_"
                    + selected_id
                ),
            )

            edit_title = st.text_input(
                "できたこと",
                value=selected.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + selected_id
                ),
            )

            old_category = (
                selected.get(
                    "category",
                    "✨ その他",
                )
            )

            category_index = (
                CATEGORIES.index(
                    old_category
                )
                if old_category
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
                        + selected_id
                    ),
                )
            )

            old_size = selected.get(
                "size",
                "🌱 小さな一歩",
            )

            size_index = (
                SIZES.index(
                    old_size
                )
                if old_size
                in SIZES
                else 0
            )

            edit_size = st.selectbox(
                "大きさ",
                SIZES,
                index=size_index,
                key=(
                    "edit_size_"
                    + selected_id
                ),
            )

            edit_memo = st.text_area(
                "ひとこと",
                value=selected.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_memo_"
                    + selected_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + selected_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "できたことを"
                            "入力してね。"
                        )

                    else:
                        update_achievement(
                            data=data,
                            achievement_id=(
                                selected_id
                            ),
                            day_number=(
                                edit_day
                            ),
                            achievement_date=(
                                edit_date
                            ),
                            title=(
                                edit_title.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            size=edit_size,
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if selected.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "edit_favorite_"
                        + selected_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        selected_id,
                    )

                    st.rerun()

            st.divider()

            st.warning(
                "削除すると元には戻せません。"
            )

            delete_confirm = (
                st.checkbox(
                    "この記録を削除する",
                    key=(
                        "delete_confirm_"
                        + selected_id
                    ),
                )
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + selected_id
                ),
                disabled=(
                    not delete_confirm
                ),
                use_container_width=True,
            ):
                delete_achievement(
                    data,
                    selected_id,
                )

                st.rerun()


# =========================================================
# バックアップ
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
        "⬇️ 300日図鑑をバックアップ",
        data=json_text,
        file_name=(
            "300_day_achievement_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# FINAL
# =========================================================

st.markdown(
    """
    <div class="final-card">
        <div style="font-size:3rem;">
            🏆
        </div>

        <h1>300本、作った。</h1>

        <p>
            最初から300本作れる人だったわけじゃない。
            <br>
            1本作って、次の1本を作って、
            また次を作った。
        </p>

        <p>
            うまくいった日も、
            何もしたくない日も、
            分からないまま進んだ日もあった。
        </p>

        <p>
            それでも、
            小さな「できた」が300まで続いた。
        </p>

        <hr style="
            border:none;
            border-top:1px solid rgba(150,150,150,.25);
            margin:30px 0;
        ">

        <h3>
            これは300本作った記録ではなく、
            <br>
            300回「次もやってみよう」と思った記録だ。
        </h3>

        <br>

        <h2>DAY 300 — COMPLETE 🏆</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
