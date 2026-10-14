import json
import os
import random
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="今日の発見",
    page_icon="🔎",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "discoveries.json")

CATEGORIES = [
    "🧠 自分",
    "💻 開発",
    "📚 知識",
    "👥 人",
    "🏠 生活",
    "🌏 世界",
    "🎮 趣味",
    "💼 仕事",
    "✨ その他",
]

DISCOVERY_TYPES = [
    "💡 知識",
    "🧠 自分について",
    "🛠️ やり方",
    "👀 気づき",
    "🌱 経験",
    "✨ その他",
]

SOURCES = [
    "📚 本",
    "🌐 Web",
    "🤖 AI",
    "💬 人との会話",
    "🧪 実際にやってみた",
    "🎬 動画",
    "🎧 音声・Podcast",
    "✨ その他",
]

MEMORY_RESULTS = [
    "😎 覚えてる！",
    "🤔 なんとなく",
    "😳 忘れてた！",
]


# =========================================================
# 共通関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def today_text():
    return str(date.today())


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

    return parsed.strftime("%Y/%m/%d")


def stars(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = 3

    value = max(1, min(value, 5))

    return (
        "★" * value
        + "☆" * (5 - value)
    )


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "discoveries": [],
        "memory_checks": [],
    }


def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)

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
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
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

        if not isinstance(data, dict):
            data = empty_data()

        data.setdefault("discoveries", [])
        data.setdefault("memory_checks", [])

        for item in data["discoveries"]:
            item.setdefault("id", create_id())
            item.setdefault("title", "")
            item.setdefault("category", "✨ その他")
            item.setdefault("discovery_type", "👀 気づき")
            item.setdefault("source", "✨ その他")
            item.setdefault("rating", 3)
            item.setdefault("why", "")
            item.setdefault("use", "")
            item.setdefault("memo", "")
            item.setdefault("favorite", False)
            item.setdefault("discovery_date", today_text())
            item.setdefault("created_at", now_text())
            item.setdefault(
                "updated_at",
                item.get("created_at", now_text()),
            )

        for check in data["memory_checks"]:
            check.setdefault("id", create_id())
            check.setdefault("discovery_id", "")
            check.setdefault("check_date", today_text())
            check.setdefault("result", "🤔 なんとなく")
            check.setdefault("created_at", now_text())

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
# データ取得
# =========================================================

def get_discovery(data, discovery_id):
    return next(
        (
            item
            for item in data["discoveries"]
            if item.get("id") == discovery_id
        ),
        None,
    )


def get_memory_checks(data, discovery_id):
    return sorted(
        [
            check
            for check in data["memory_checks"]
            if check.get("discovery_id") == discovery_id
        ],
        key=lambda row: row.get("check_date", ""),
        reverse=True,
    )


def get_latest_memory_check(data, discovery_id):
    checks = get_memory_checks(
        data,
        discovery_id,
    )

    if not checks:
        return None

    return checks[0]


# =========================================================
# CRUD
# =========================================================

def add_discovery(
    data,
    title,
    category,
    discovery_type,
    source,
    rating,
    why,
    use,
    memo,
    discovery_date,
):
    discovery = {
        "id": create_id(),
        "title": title,
        "category": category,
        "discovery_type": discovery_type,
        "source": source,
        "rating": int(rating),
        "why": why,
        "use": use,
        "memo": memo,
        "favorite": False,
        "discovery_date": str(discovery_date),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["discoveries"].append(discovery)
    save_data(data)


def update_discovery(
    data,
    discovery_id,
    title,
    category,
    discovery_type,
    source,
    rating,
    why,
    use,
    memo,
    discovery_date,
):
    item = get_discovery(
        data,
        discovery_id,
    )

    if not item:
        return

    item["title"] = title
    item["category"] = category
    item["discovery_type"] = discovery_type
    item["source"] = source
    item["rating"] = int(rating)
    item["why"] = why
    item["use"] = use
    item["memo"] = memo
    item["discovery_date"] = str(discovery_date)
    item["updated_at"] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    discovery_id,
):
    item = get_discovery(
        data,
        discovery_id,
    )

    if not item:
        return

    item["favorite"] = not item.get(
        "favorite",
        False,
    )

    item["updated_at"] = now_text()

    save_data(data)


def add_memory_check(
    data,
    discovery_id,
    result,
):
    check = {
        "id": create_id(),
        "discovery_id": discovery_id,
        "check_date": today_text(),
        "result": result,
        "created_at": now_text(),
    }

    data["memory_checks"].append(check)
    save_data(data)


def delete_discovery(
    data,
    discovery_id,
):
    data["discoveries"] = [
        item
        for item in data["discoveries"]
        if item.get("id") != discovery_id
    ]

    data["memory_checks"] = [
        check
        for check in data["memory_checks"]
        if check.get("discovery_id")
        != discovery_id
    ]

    save_data(data)


# =========================================================
# ストリーク
# =========================================================

def calculate_streak(discoveries):
    recorded_dates = {
        parse_date(
            item.get("discovery_date")
        )
        for item in discoveries
        if parse_date(
            item.get("discovery_date")
        )
    }

    if not recorded_dates:
        return 0

    current = date.today()

    # 今日まだ記録していなければ昨日から数える
    if current not in recorded_dates:
        current -= timedelta(days=1)

    streak = 0

    while current in recorded_dates:
        streak += 1
        current -= timedelta(days=1)

    return streak


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
        background: rgba(100, 160, 255, 0.07);
        border: 1px solid rgba(100, 160, 255, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(100, 160, 255, 0.18),
                rgba(160, 100, 255, 0.10)
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ準備
# =========================================================

data = load_data()

discoveries = data["discoveries"]

today = date.today()
today_string = today_text()
month_prefix = today.strftime("%Y-%m")

today_discoveries = [
    item
    for item in discoveries
    if item.get("discovery_date")
    == today_string
]

month_discoveries = [
    item
    for item in discoveries
    if (
        item.get("discovery_date", "")
        or ""
    ).startswith(month_prefix)
]

recorded_days = {
    item.get("discovery_date")
    for item in month_discoveries
    if item.get("discovery_date")
}

streak = calculate_streak(
    discoveries
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🔎 今日の発見</h1>
        <p>
            小さな「知らなかった」を残して、
            自分だけの発見図鑑を育てよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🔎 今日の発見",
    f"{len(today_discoveries)}個",
)

col2.metric(
    f"📅 {today.month}月の発見",
    f"{len(month_discoveries)}個",
)

col3.metric(
    "🔥 発見ストリーク",
    f"{streak}日",
)

col4.metric(
    "📚 累計発見",
    f"{len(discoveries)}個",
)

if recorded_days:
    st.caption(
        f"🌱 今月は {len(recorded_days)}日、"
        "何かを発見しています。"
    )

if streak >= 2:
    st.success(
        f"🔥 {streak}日連続で、"
        "新しい気づきを残しています！"
    )

elif discoveries:
    st.caption(
        "記録がない日にも、"
        "発見はあったかもしれません。"
    )


# =========================================================
# 新しい発見
# =========================================================

st.divider()

st.subheader(
    "✨ 今日、何を発見した？"
)

with st.form(
    "new_discovery_form",
    clear_on_submit=True,
):
    title = st.text_area(
        "🔎 発見",
        placeholder=(
            "例：Pythonのreturnは、"
            "値を返した時点で関数を終了する"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

        discovery_type = st.selectbox(
            "💡 どんな発見？",
            DISCOVERY_TYPES,
        )

        rating = st.slider(
            "😲 発見度",
            1,
            5,
            3,
        )

    with col2:
        source = st.selectbox(
            "📍 どこで発見した？",
            SOURCES,
        )

        discovery_date = st.date_input(
            "📅 発見日",
            value=today,
            max_value=today,
        )

    why = st.text_area(
        "💭 なぜ印象に残った？",
        placeholder=(
            "例：returnは結果を返すだけだと"
            "思っていたから"
        ),
    )

    use = st.text_area(
        "🚀 どう使えそう？",
        placeholder=(
            "例：関数を書くときの"
            "終了条件として使えそう"
        ),
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "関連する言葉、URL、"
            "あとで調べたいことなど"
        ),
    )

    submitted = st.form_submit_button(
        "🔎 発見を記録する",
        type="primary",
        use_container_width=True,
    )

    if submitted:
        if not title.strip():
            st.warning(
                "発見したことを入力してね。"
            )

        else:
            add_discovery(
                data=data,
                title=title.strip(),
                category=category,
                discovery_type=discovery_type,
                source=source,
                rating=rating,
                why=why.strip(),
                use=use.strip(),
                memo=memo.strip(),
                discovery_date=discovery_date,
            )

            st.rerun()


# =========================================================
# 今日の発見
# =========================================================

st.divider()

st.subheader(
    "🌞 今日の発見"
)

if not today_discoveries:
    st.info(
        "今日はまだ発見を記録していません。"
    )

else:
    for item in reversed(
        today_discoveries
    ):
        item_id = item.get("id", "")

        with st.container(border=True):
            col1, col2 = st.columns(
                [8, 1]
            )

            with col1:
                st.markdown(
                    "### "
                    + item.get(
                        "title",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if item.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "today_fav_"
                        + item_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )
                    st.rerun()

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ "
                f"{item.get('discovery_type', '')}"
                f" ｜ "
                f"{item.get('source', '')}"
            )

            st.write(
                "😲 発見度："
                + stars(
                    item.get(
                        "rating",
                        3,
                    )
                )
            )

            if item.get("why"):
                st.write(
                    "**💭 なぜ印象に残った？**"
                )
                st.write(
                    item.get(
                        "why",
                        "",
                    )
                )

            if item.get("use"):
                st.write(
                    "**🚀 どう使えそう？**"
                )
                st.write(
                    item.get(
                        "use",
                        "",
                    )
                )


# =========================================================
# 今月の大発見
# =========================================================

big_discoveries = [
    item
    for item in month_discoveries
    if int(
        item.get("rating", 0)
    ) == 5
]

if big_discoveries:
    st.divider()

    st.subheader(
        "🏆 今月の大発見"
    )

    for item in reversed(
        big_discoveries
    ):
        with st.container(border=True):
            st.caption(
                format_date(
                    item.get(
                        "discovery_date"
                    )
                )
            )

            st.write(
                "⭐⭐⭐⭐⭐"
            )

            st.markdown(
                "### "
                + item.get(
                    "title",
                    "",
                )
            )

            st.caption(
                f"{item.get('category', '')}"
                f" ｜ "
                f"{item.get('source', '')}"
            )


# =========================================================
# カテゴリー分析
# =========================================================

st.divider()

st.subheader(
    f"🧭 {today.month}月は何を発見してる？"
)

if not month_discoveries:
    st.info(
        "今月のデータがまだありません。"
    )

else:
    category_counts = {}

    for item in month_discoveries:
        category = item.get(
            "category",
            "✨ その他",
        )

        category_counts[category] = (
            category_counts.get(
                category,
                0,
            )
            + 1
        )

    category_df = (
        pd.DataFrame(
            [
                {
                    "カテゴリー": key,
                    "発見数": value,
                }
                for key, value
                in category_counts.items()
            ]
        )
        .sort_values(
            "発見数",
            ascending=False,
        )
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )

    top_category = (
        category_df.iloc[0][
            "カテゴリー"
        ]
    )

    st.info(
        "🔎 今月もっとも多いのは "
        f"**{top_category}** の発見です。"
    )


# =========================================================
# 発見元分析
# =========================================================

if month_discoveries:
    st.markdown(
        "### 📍 発見のきっかけ"
    )

    source_counts = {}

    for item in month_discoveries:
        source = item.get(
            "source",
            "✨ その他",
        )

        source_counts[source] = (
            source_counts.get(
                source,
                0,
            )
            + 1
        )

    source_df = (
        pd.DataFrame(
            [
                {
                    "発見元": key,
                    "発見数": value,
                }
                for key, value
                in source_counts.items()
            ]
        )
        .sort_values(
            "発見数",
            ascending=False,
        )
    )

    st.bar_chart(
        source_df.set_index(
            "発見元"
        )
    )

    top_source = (
        source_df.iloc[0][
            "発見元"
        ]
    )

    st.caption(
        "今月は "
        f"{top_source} からの発見が"
        "もっとも多くなっています。"
    )


# =========================================================
# 発見タイプ分析
# =========================================================

if month_discoveries:
    st.markdown(
        "### 💡 どんな発見だった？"
    )

    type_counts = {}

    for item in month_discoveries:
        discovery_type = item.get(
            "discovery_type",
            "✨ その他",
        )

        type_counts[
            discovery_type
        ] = (
            type_counts.get(
                discovery_type,
                0,
            )
            + 1
        )

    type_df = (
        pd.DataFrame(
            [
                {
                    "発見タイプ": key,
                    "発見数": value,
                }
                for key, value
                in type_counts.items()
            ]
        )
        .sort_values(
            "発見数",
            ascending=False,
        )
    )

    st.bar_chart(
        type_df.set_index(
            "発見タイプ"
        )
    )


# =========================================================
# 月別推移
# =========================================================

if discoveries:
    st.divider()

    st.subheader(
        "📈 発見の推移"
    )

    monthly_counts = {}

    for item in discoveries:
        item_date = parse_date(
            item.get(
                "discovery_date"
            )
        )

        if not item_date:
            continue

        key = item_date.strftime(
            "%Y-%m"
        )

        monthly_counts[key] = (
            monthly_counts.get(
                key,
                0,
            )
            + 1
        )

    if monthly_counts:
        monthly_df = (
            pd.DataFrame(
                [
                    {
                        "月": key,
                        "発見数": value,
                    }
                    for key, value
                    in sorted(
                        monthly_counts.items()
                    )
                ]
            )
        )

        st.line_chart(
            monthly_df.set_index(
                "月"
            )
        )

        st.caption(
            "※ 発見数の多さが、"
            "そのまま成長の大きさを"
            "意味するものではありません。"
        )


# =========================================================
# 発見ガチャ
# =========================================================

old_discoveries = [
    item
    for item in discoveries
    if (
        parse_date(
            item.get(
                "discovery_date"
            )
        )
        and (
            today
            - parse_date(
                item.get(
                    "discovery_date"
                )
            )
        ).days >= 14
    )
]

if old_discoveries:
    st.divider()

    st.subheader(
        "🎲 発見ガチャ"
    )

    st.caption(
        "昔の「知らなかった」を、"
        "もう一度見てみよう。"
    )

    old_ids = [
        item.get("id")
        for item in old_discoveries
    ]

    random_id = st.session_state.get(
        "random_discovery_id"
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_discovery_id"
        ] = random_id

    random_item = get_discovery(
        data,
        random_id,
    )

    if random_item:
        with st.container(border=True):
            st.caption(
                format_date(
                    random_item.get(
                        "discovery_date"
                    )
                )
            )

            st.markdown(
                "### 🔎 "
                + random_item.get(
                    "title",
                    "",
                )
            )

            st.caption(
                f"{random_item.get('category', '')}"
                f" ｜ "
                f"{random_item.get('source', '')}"
            )

            st.write(
                "当時の発見度："
                + stars(
                    random_item.get(
                        "rating",
                        3,
                    )
                )
            )

            if random_item.get("why"):
                st.write(
                    "**💭 当時の気づき**"
                )
                st.write(
                    random_item.get(
                        "why",
                        "",
                    )
                )

            if random_item.get("use"):
                st.write(
                    "**🚀 どう使えそうと思った？**"
                )
                st.write(
                    random_item.get(
                        "use",
                        "",
                    )
                )

            latest_check = (
                get_latest_memory_check(
                    data,
                    random_id,
                )
            )

            if latest_check:
                st.caption(
                    "前回の記憶チェック："
                    f"{latest_check.get('result', '')}"
                    " / "
                    f"{format_date(latest_check.get('check_date'))}"
                )

        st.markdown(
            "#### 🔁 この発見、覚えてる？"
        )

        col1, col2, col3 = st.columns(3)

        results = [
            "😎 覚えてる！",
            "🤔 なんとなく",
            "😳 忘れてた！",
        ]

        for column, result in zip(
            [col1, col2, col3],
            results,
        ):
            with column:
                if st.button(
                    result,
                    key=(
                        "memory_"
                        + result
                        + random_id
                    ),
                    use_container_width=True,
                ):
                    add_memory_check(
                        data,
                        random_id,
                        result,
                    )

                    if result == "😳 忘れてた！":
                        st.session_state[
                            "memory_message"
                        ] = (
                            "🔎 今日、もう一度"
                            "発見しました。"
                        )
                    else:
                        st.session_state[
                            "memory_message"
                        ] = (
                            "📚 記憶チェックを"
                            "記録しました。"
                        )

                    st.rerun()

        if st.session_state.get(
            "memory_message"
        ):
            st.success(
                st.session_state.pop(
                    "memory_message"
                )
            )

        if st.button(
            "🎲 もう一回！",
            use_container_width=True,
        ):
            alternatives = [
                discovery_id
                for discovery_id
                in old_ids
                if discovery_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_discovery_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 記憶チェック分析
# =========================================================

memory_checks = data[
    "memory_checks"
]

if memory_checks:
    st.divider()

    st.subheader(
        "🧠 発見はどれくらい残ってる？"
    )

    memory_counts = {
        result: 0
        for result in MEMORY_RESULTS
    }

    for check in memory_checks:
        result = check.get(
            "result",
            "🤔 なんとなく",
        )

        memory_counts[result] = (
            memory_counts.get(
                result,
                0,
            )
            + 1
        )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "😎 覚えてた",
        memory_counts.get(
            "😎 覚えてる！",
            0,
        ),
    )

    col2.metric(
        "🤔 なんとなく",
        memory_counts.get(
            "🤔 なんとなく",
            0,
        ),
    )

    col3.metric(
        "😳 再発見",
        memory_counts.get(
            "😳 忘れてた！",
            0,
        ),
    )


# =========================================================
# お気に入り
# =========================================================

favorites = [
    item
    for item in discoveries
    if item.get(
        "favorite",
        False,
    )
]

if favorites:
    st.divider()

    st.subheader(
        "⭐ お気に入りの発見"
    )

    for item in sorted(
        favorites,
        key=lambda row: row.get(
            "discovery_date",
            "",
        ),
        reverse=True,
    )[:10]:
        st.write(
            f"⭐ **{item.get('title', '')}**"
            f" — "
            f"{format_date(item.get('discovery_date'))}"
        )


# =========================================================
# 発見図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 発見図鑑"
)

search_text = st.text_input(
    "🔎 発見を検索",
    placeholder=(
        "Python、仕事、自分……"
    ),
)

col1, col2 = st.columns(2)

with col1:
    category_filter = st.selectbox(
        "カテゴリー",
        ["すべて"] + CATEGORIES,
        key="discovery_category_filter",
    )

    type_filter = st.selectbox(
        "発見タイプ",
        ["すべて"] + DISCOVERY_TYPES,
        key="discovery_type_filter",
    )

with col2:
    source_filter = st.selectbox(
        "発見元",
        ["すべて"] + SOURCES,
        key="discovery_source_filter",
    )

    rating_filter = st.selectbox(
        "発見度",
        [
            "すべて",
            "★★★★★",
            "★★★★以上",
            "★★★以上",
        ],
        key="discovery_rating_filter",
    )

minimum_rating = 0

if rating_filter == "★★★★★":
    minimum_rating = 5

elif rating_filter == "★★★★以上":
    minimum_rating = 4

elif rating_filter == "★★★以上":
    minimum_rating = 3


filtered = []

for item in discoveries:
    if (
        category_filter != "すべて"
        and item.get("category")
        != category_filter
    ):
        continue

    if (
        type_filter != "すべて"
        and item.get("discovery_type")
        != type_filter
    ):
        continue

    if (
        source_filter != "すべて"
        and item.get("source")
        != source_filter
    ):
        continue

    if (
        int(item.get("rating", 0))
        < minimum_rating
    ):
        continue

    searchable = " ".join(
        [
            item.get("title", ""),
            item.get("why", ""),
            item.get("use", ""),
            item.get("memo", ""),
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

    filtered.append(item)


if not filtered:
    st.info(
        "条件に合う発見はありません。"
    )

else:
    rows = []

    for item in sorted(
        filtered,
        key=lambda row: row.get(
            "discovery_date",
            "",
        ),
        reverse=True,
    ):
        latest_check = (
            get_latest_memory_check(
                data,
                item.get("id"),
            )
        )

        rows.append(
            {
                "日付": format_date(
                    item.get(
                        "discovery_date"
                    )
                ),
                "発見": item.get(
                    "title",
                    "",
                ),
                "カテゴリー": item.get(
                    "category",
                    "",
                ),
                "タイプ": item.get(
                    "discovery_type",
                    "",
                ),
                "発見元": item.get(
                    "source",
                    "",
                ),
                "発見度": stars(
                    item.get(
                        "rating",
                        3,
                    )
                ),
                "記憶": (
                    latest_check.get(
                        "result",
                        "",
                    )
                    if latest_check
                    else "-"
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
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


# =========================================================
# 編集・履歴・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・記憶履歴・削除"
):
    if not discoveries:
        st.caption(
            "まだ発見がありません。"
        )

    for item in sorted(
        discoveries,
        key=lambda row: row.get(
            "discovery_date",
            "",
        ),
        reverse=True,
    ):
        item_id = item.get("id", "")

        short_title = item.get(
            "title",
            "",
        )

        if len(short_title) > 40:
            short_title = (
                short_title[:40]
                + "..."
            )

        with st.expander(
            f"{format_date(item.get('discovery_date'))}"
            f" ｜ {short_title}"
        ):
            edit_title = st.text_area(
                "発見",
                value=item.get(
                    "title",
                    "",
                ),
                key=(
                    "edit_title_"
                    + item_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                old_category = item.get(
                    "category",
                    "✨ その他",
                )

                category_index = (
                    CATEGORIES.index(
                        old_category
                    )
                    if old_category
                    in CATEGORIES
                    else len(CATEGORIES) - 1
                )

                edit_category = st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=category_index,
                    key=(
                        "edit_category_"
                        + item_id
                    ),
                )

                old_type = item.get(
                    "discovery_type",
                    "✨ その他",
                )

                type_index = (
                    DISCOVERY_TYPES.index(
                        old_type
                    )
                    if old_type
                    in DISCOVERY_TYPES
                    else len(
                        DISCOVERY_TYPES
                    ) - 1
                )

                edit_type = st.selectbox(
                    "発見タイプ",
                    DISCOVERY_TYPES,
                    index=type_index,
                    key=(
                        "edit_type_"
                        + item_id
                    ),
                )

                edit_rating = st.slider(
                    "発見度",
                    1,
                    5,
                    int(
                        item.get(
                            "rating",
                            3,
                        )
                    ),
                    key=(
                        "edit_rating_"
                        + item_id
                    ),
                )

            with col2:
                old_source = item.get(
                    "source",
                    "✨ その他",
                )

                source_index = (
                    SOURCES.index(
                        old_source
                    )
                    if old_source
                    in SOURCES
                    else len(SOURCES) - 1
                )

                edit_source = st.selectbox(
                    "発見元",
                    SOURCES,
                    index=source_index,
                    key=(
                        "edit_source_"
                        + item_id
                    ),
                )

                edit_date = st.date_input(
                    "発見日",
                    value=(
                        parse_date(
                            item.get(
                                "discovery_date"
                            )
                        )
                        or today
                    ),
                    max_value=today,
                    key=(
                        "edit_date_"
                        + item_id
                    ),
                )

            edit_why = st.text_area(
                "なぜ印象に残った？",
                value=item.get(
                    "why",
                    "",
                ),
                key=(
                    "edit_why_"
                    + item_id
                ),
            )

            edit_use = st.text_area(
                "どう使えそう？",
                value=item.get(
                    "use",
                    "",
                ),
                key=(
                    "edit_use_"
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

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 変更を保存",
                    key=(
                        "save_edit_"
                        + item_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.warning(
                            "発見を入力してね。"
                        )

                    else:
                        update_discovery(
                            data=data,
                            discovery_id=item_id,
                            title=edit_title.strip(),
                            category=edit_category,
                            discovery_type=edit_type,
                            source=edit_source,
                            rating=edit_rating,
                            why=edit_why.strip(),
                            use=edit_use.strip(),
                            memo=edit_memo.strip(),
                            discovery_date=edit_date,
                        )

                        st.rerun()

            with col2:
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
                        "edit_fav_"
                        + item_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        item_id,
                    )
                    st.rerun()

            checks = get_memory_checks(
                data,
                item_id,
            )

            if checks:
                st.markdown(
                    "#### 🧠 記憶チェック履歴"
                )

                for check in checks:
                    st.write(
                        f"{format_date(check.get('check_date'))}"
                        f" — "
                        f"{check.get('result', '')}"
                    )

            st.markdown(
                "#### 🗑️ 削除"
            )

            confirm_delete = st.checkbox(
                "この発見と記憶履歴を削除する",
                key=(
                    "confirm_delete_"
                    + item_id
                ),
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + item_id
                ),
                disabled=not confirm_delete,
                use_container_width=True,
            ):
                delete_discovery(
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
            "today_discovery_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "🔎 小さな「知らなかった」を残すと、"
    "昨日まで知らなかった自分が見えてくる。"
)

st.caption(
    "大発見じゃなくていい。"
    "「あ、そうなんだ」も、"
    "ちゃんと今日の発見。"
)
