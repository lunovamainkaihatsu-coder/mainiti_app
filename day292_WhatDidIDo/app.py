import json
import os
import random
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="あの時どうした？",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "troubles.json",
)

CATEGORIES = [
    "💻 開発",
    "💼 仕事",
    "🏠 生活",
    "💰 お金",
    "🚗 車・移動",
    "📱 機械・モノ",
    "👥 人間関係",
    "📄 手続き",
    "✨ その他",
]

CAUSE_SOURCES = [
    "❓ まだ分からない",
    "🤖 AIに聞いた",
    "🌐 Webで調べた",
    "🧪 自分で試した",
    "💬 人に聞いた",
    "📚 本・資料",
    "✨ その他",
]

ATTEMPT_RESULTS = [
    "🎉 解決した！",
    "🌱 少し改善",
    "😐 変わらない",
    "💥 悪化した",
]

STATUSES = [
    "🚧 未解決",
    "🎉 解決済み",
    "🍃 終了",
]

REUSE_RESULTS = [
    "🎉 助かった！",
    "😐 今回はダメだった",
]


# =========================================================
# 共通関数
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


def days_between(start, end):
    start_date = parse_date(start)
    end_date = parse_date(end)

    if not start_date or not end_date:
        return None

    return max(
        (end_date - start_date).days,
        0,
    )


def resolution_text(start, end):
    days = days_between(
        start,
        end,
    )

    if days is None:
        return "-"

    if days == 0:
        return "当日解決"

    return f"{days}日"


# =========================================================
# データ
# =========================================================

def empty_data():
    return {
        "troubles": [],
        "attempts": [],
        "recurrences": [],
        "reuses": [],
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

        for key in [
            "troubles",
            "attempts",
            "recurrences",
            "reuses",
        ]:
            data.setdefault(
                key,
                [],
            )

        for trouble in data[
            "troubles"
        ]:
            trouble.setdefault(
                "id",
                create_id(),
            )
            trouble.setdefault(
                "title",
                "",
            )
            trouble.setdefault(
                "category",
                "✨ その他",
            )
            trouble.setdefault(
                "situation",
                "",
            )
            trouble.setdefault(
                "cause",
                "",
            )
            trouble.setdefault(
                "cause_source",
                "❓ まだ分からない",
            )
            trouble.setdefault(
                "status",
                "🚧 未解決",
            )
            trouble.setdefault(
                "start_date",
                today_text(),
            )
            trouble.setdefault(
                "resolved_date",
                None,
            )
            trouble.setdefault(
                "resolution",
                "",
            )
            trouble.setdefault(
                "memo",
                "",
            )
            trouble.setdefault(
                "favorite",
                False,
            )
            trouble.setdefault(
                "created_at",
                now_text(),
            )
            trouble.setdefault(
                "updated_at",
                trouble.get(
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

def get_trouble(
    data,
    trouble_id,
):
    return next(
        (
            trouble
            for trouble
            in data["troubles"]
            if trouble.get("id")
            == trouble_id
        ),
        None,
    )


def get_attempts(
    data,
    trouble_id,
):
    return sorted(
        [
            attempt
            for attempt
            in data["attempts"]
            if attempt.get(
                "trouble_id"
            ) == trouble_id
        ],
        key=lambda row: (
            row.get(
                "attempt_date",
                ""
            ),
            row.get(
                "created_at",
                "",
            ),
        ),
    )


def get_recurrences(
    data,
    trouble_id,
):
    return sorted(
        [
            row
            for row
            in data["recurrences"]
            if row.get(
                "trouble_id"
            ) == trouble_id
        ],
        key=lambda row: row.get(
            "recurrence_date",
            "",
        ),
    )


def get_reuses(
    data,
    trouble_id,
):
    return [
        row
        for row
        in data["reuses"]
        if row.get(
            "trouble_id"
        ) == trouble_id
    ]


def helpful_count(
    data,
    trouble_id,
):
    return sum(
        1
        for row in get_reuses(
            data,
            trouble_id,
        )
        if row.get(
            "result"
        ) == "🎉 助かった！"
    )


def final_success_attempt(
    data,
    trouble_id,
):
    successes = [
        attempt
        for attempt
        in get_attempts(
            data,
            trouble_id,
        )
        if attempt.get(
            "result"
        ) == "🎉 解決した！"
    ]

    if not successes:
        return None

    return successes[-1]


# =========================================================
# CRUD
# =========================================================

def add_trouble(
    data,
    title,
    category,
    situation,
    cause,
    cause_source,
    start_date,
    memo,
):
    trouble = {
        "id": create_id(),
        "title": title,
        "category": category,
        "situation": situation,
        "cause": cause,
        "cause_source": cause_source,
        "status": "🚧 未解決",
        "start_date": str(start_date),
        "resolved_date": None,
        "resolution": "",
        "memo": memo,
        "favorite": False,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["troubles"].append(
        trouble
    )

    save_data(data)


def add_attempt(
    data,
    trouble_id,
    action,
    result,
    note,
    attempt_date,
):
    attempt = {
        "id": create_id(),
        "trouble_id": trouble_id,
        "action": action,
        "result": result,
        "note": note,
        "attempt_date": str(
            attempt_date
        ),
        "created_at": now_text(),
    }

    data["attempts"].append(
        attempt
    )

    trouble = get_trouble(
        data,
        trouble_id,
    )

    if trouble:
        if result == "🎉 解決した！":
            trouble[
                "status"
            ] = "🎉 解決済み"

            trouble[
                "resolved_date"
            ] = str(
                attempt_date
            )

            trouble[
                "resolution"
            ] = action

        trouble[
            "updated_at"
        ] = now_text()

    save_data(data)


def add_recurrence(
    data,
    trouble_id,
    recurrence_date,
    note,
):
    row = {
        "id": create_id(),
        "trouble_id": trouble_id,
        "recurrence_date": str(
            recurrence_date
        ),
        "note": note,
        "created_at": now_text(),
    }

    data["recurrences"].append(
        row
    )

    trouble = get_trouble(
        data,
        trouble_id,
    )

    if trouble:
        trouble[
            "updated_at"
        ] = now_text()

    save_data(data)


def add_reuse(
    data,
    trouble_id,
    result,
    note,
):
    row = {
        "id": create_id(),
        "trouble_id": trouble_id,
        "reuse_date": today_text(),
        "result": result,
        "note": note,
        "created_at": now_text(),
    }

    data["reuses"].append(
        row
    )

    trouble = get_trouble(
        data,
        trouble_id,
    )

    if trouble:
        trouble[
            "updated_at"
        ] = now_text()

    save_data(data)


def toggle_favorite(
    data,
    trouble_id,
):
    trouble = get_trouble(
        data,
        trouble_id,
    )

    if not trouble:
        return

    trouble[
        "favorite"
    ] = not trouble.get(
        "favorite",
        False,
    )

    trouble[
        "updated_at"
    ] = now_text()

    save_data(data)


def close_trouble(
    data,
    trouble_id,
):
    trouble = get_trouble(
        data,
        trouble_id,
    )

    if not trouble:
        return

    trouble[
        "status"
    ] = "🍃 終了"

    trouble[
        "updated_at"
    ] = now_text()

    save_data(data)


def reopen_trouble(
    data,
    trouble_id,
):
    trouble = get_trouble(
        data,
        trouble_id,
    )

    if not trouble:
        return

    trouble[
        "status"
    ] = "🚧 未解決"

    trouble[
        "resolved_date"
    ] = None

    trouble[
        "resolution"
    ] = ""

    trouble[
        "updated_at"
    ] = now_text()

    save_data(data)


def update_trouble(
    data,
    trouble_id,
    title,
    category,
    situation,
    cause,
    cause_source,
    memo,
):
    trouble = get_trouble(
        data,
        trouble_id,
    )

    if not trouble:
        return

    trouble["title"] = title
    trouble[
        "category"
    ] = category
    trouble[
        "situation"
    ] = situation
    trouble[
        "cause"
    ] = cause
    trouble[
        "cause_source"
    ] = cause_source
    trouble[
        "memo"
    ] = memo
    trouble[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_attempt(
    data,
    attempt_id,
):
    data["attempts"] = [
        row
        for row in data["attempts"]
        if row.get("id")
        != attempt_id
    ]

    save_data(data)


def delete_trouble(
    data,
    trouble_id,
):
    data["troubles"] = [
        row
        for row in data["troubles"]
        if row.get("id")
        != trouble_id
    ]

    for key in [
        "attempts",
        "recurrences",
        "reuses",
    ]:
        data[key] = [
            row
            for row in data[key]
            if row.get(
                "trouble_id"
            ) != trouble_id
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
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 16px;
        background: rgba(90, 150, 220, 0.07);
        border: 1px solid rgba(90, 150, 220, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(70, 150, 220, 0.18),
                rgba(100, 210, 160, 0.10)
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

troubles = data["troubles"]
today = date.today()
month_prefix = today.strftime(
    "%Y-%m"
)

unresolved = [
    row
    for row in troubles
    if row.get(
        "status"
    ) == "🚧 未解決"
]

resolved = [
    row
    for row in troubles
    if row.get(
        "status"
    ) == "🎉 解決済み"
]

closed = [
    row
    for row in troubles
    if row.get(
        "status"
    ) == "🍃 終了"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧠 あの時どうした？</h1>
        <p>
            困った経験を、
            次に困った自分の味方にする。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

total_attempts = len(
    data["attempts"]
)

total_helpful = sum(
    1
    for row in data["reuses"]
    if row.get(
        "result"
    ) == "🎉 助かった！"
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "🧠 困った経験",
    f"{len(troubles)}件",
)

col2.metric(
    "🎉 解決",
    f"{len(resolved)}件",
)

col3.metric(
    "🚧 未解決",
    f"{len(unresolved)}件",
)

col4.metric(
    "♻️ 再利用成功",
    f"{total_helpful}回",
)


# =========================================================
# 検索
# =========================================================

st.divider()

st.subheader(
    "🔎 前にも困ったことない？"
)

search_text = st.text_input(
    "困ったことを検索",
    placeholder=(
        "例：Streamlit 画像"
    ),
    key="main_search",
)

if search_text.strip():
    keywords = (
        search_text
        .strip()
        .lower()
        .split()
    )

    search_results = []

    for trouble in troubles:
        trouble_id = trouble.get(
            "id",
            "",
        )

        attempts = get_attempts(
            data,
            trouble_id,
        )

        searchable_parts = [
            trouble.get(
                "title",
                "",
            ),
            trouble.get(
                "situation",
                "",
            ),
            trouble.get(
                "cause",
                "",
            ),
            trouble.get(
                "resolution",
                "",
            ),
            trouble.get(
                "memo",
                "",
            ),
        ]

        for attempt in attempts:
            searchable_parts.extend(
                [
                    attempt.get(
                        "action",
                        "",
                    ),
                    attempt.get(
                        "note",
                        "",
                    ),
                ]
            )

        searchable = " ".join(
            searchable_parts
        ).lower()

        if all(
            keyword in searchable
            for keyword in keywords
        ):
            search_results.append(
                trouble
            )

    if not search_results:
        st.info(
            "似た経験はまだ見つかりません。"
        )

    else:
        st.success(
            f"💡 {len(search_results)}件の"
            "経験が見つかりました。"
        )

        for trouble in search_results:
            trouble_id = trouble.get(
                "id",
                "",
            )

            success = (
                final_success_attempt(
                    data,
                    trouble_id,
                )
            )

            with st.container(
                border=True
            ):
                st.write(
                    "**"
                    + trouble.get(
                        "title",
                        "",
                    )
                    + "**"
                )

                st.caption(
                    format_date(
                        trouble.get(
                            "start_date"
                        )
                    )
                    + " ｜ "
                    + trouble.get(
                        "category",
                        "",
                    )
                    + " ｜ "
                    + trouble.get(
                        "status",
                        "",
                    )
                )

                if trouble.get(
                    "cause"
                ):
                    st.write(
                        "**🔍 原因**"
                    )
                    st.write(
                        trouble.get(
                            "cause",
                            "",
                        )
                    )

                if success:
                    st.write(
                        "**🛠️ あの時はこうした**"
                    )
                    st.success(
                        success.get(
                            "action",
                            "",
                        )
                    )

                    count = helpful_count(
                        data,
                        trouble_id,
                    )

                    if count:
                        st.caption(
                            f"♻️ この経験は"
                            f"{count}回、"
                            "その後も役に立っています。"
                        )

                    col1, col2 = (
                        st.columns(2)
                    )

                    with col1:
                        if st.button(
                            "🎉 今回も助かった！",
                            key=(
                                "search_help_"
                                + trouble_id
                            ),
                            use_container_width=True,
                        ):
                            add_reuse(
                                data,
                                trouble_id,
                                "🎉 助かった！",
                                "",
                            )
                            st.rerun()

                    with col2:
                        if st.button(
                            "😐 今回はダメだった",
                            key=(
                                "search_nohelp_"
                                + trouble_id
                            ),
                            use_container_width=True,
                        ):
                            add_reuse(
                                data,
                                trouble_id,
                                "😐 今回はダメだった",
                                "",
                            )
                            st.rerun()


# =========================================================
# 新規登録
# =========================================================

st.divider()

st.subheader(
    "😵 新しく困ったこと"
)

with st.form(
    "new_trouble_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "何に困った？",
        placeholder=(
            "例：Streamlitで"
            "画像が表示されない"
        ),
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        start_date = st.date_input(
            "いつ起きた？",
            value=today,
            max_value=today,
        )

    with col2:
        cause_source = (
            st.selectbox(
                "原因はどう分かった？",
                CAUSE_SOURCES,
            )
        )

    situation = st.text_area(
        "😵 どんな状況？",
        placeholder=(
            "エラー内容や、"
            "何をしていたかなど"
        ),
    )

    cause = st.text_area(
        "🔍 原因",
        placeholder=(
            "まだ分からなければ"
            "空欄でOK"
        ),
    )

    memo = st.text_area(
        "📝 メモ",
        placeholder=(
            "URL、エラーコード、"
            "関連情報など"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🧠 困ったことを記録",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.warning(
                "困ったことを入力してね。"
            )
        else:
            add_trouble(
                data=data,
                title=title.strip(),
                category=category,
                situation=(
                    situation.strip()
                ),
                cause=cause.strip(),
                cause_source=(
                    cause_source
                ),
                start_date=start_date,
                memo=memo.strip(),
            )

            st.rerun()


# =========================================================
# 未解決BOX
# =========================================================

st.divider()

st.subheader(
    "🚧 未解決BOX"
)

if not unresolved:
    st.success(
        "現在、未解決の問題はありません！"
    )

else:
    for trouble in sorted(
        unresolved,
        key=lambda row: (
            row.get(
                "start_date",
                "",
            )
        ),
    ):
        trouble_id = trouble.get(
            "id",
            "",
        )

        start = parse_date(
            trouble.get(
                "start_date"
            )
        )

        age = (
            (today - start).days
            if start
            else 0
        )

        attempts = get_attempts(
            data,
            trouble_id,
        )

        with st.container(
            border=True
        ):
            st.subheader(
                trouble.get(
                    "title",
                    "",
                )
            )

            st.caption(
                trouble.get(
                    "category",
                    "",
                )
                + " ｜ "
                + format_date(
                    trouble.get(
                        "start_date"
                    )
                )
                + f" ｜ {age}日前"
            )

            if trouble.get(
                "situation"
            ):
                st.write(
                    trouble.get(
                        "situation",
                        "",
                    )
                )

            if trouble.get(
                "cause"
            ):
                st.write(
                    "**🔍 現在考えている原因**"
                )
                st.write(
                    trouble.get(
                        "cause",
                        "",
                    )
                )

            st.caption(
                f"🧪 試した方法："
                f"{len(attempts)}個"
            )

            with st.expander(
                "🛠️ 方法を試した"
            ):
                action = st.text_area(
                    "何をした？",
                    key=(
                        "attempt_action_"
                        + trouble_id
                    ),
                )

                result = st.selectbox(
                    "結果",
                    ATTEMPT_RESULTS,
                    key=(
                        "attempt_result_"
                        + trouble_id
                    ),
                )

                attempt_note = (
                    st.text_area(
                        "メモ",
                        key=(
                            "attempt_note_"
                            + trouble_id
                        ),
                    )
                )

                attempt_date = (
                    st.date_input(
                        "試した日",
                        value=today,
                        max_value=today,
                        key=(
                            "attempt_date_"
                            + trouble_id
                        ),
                    )
                )

                if st.button(
                    "🧪 試行を記録",
                    key=(
                        "add_attempt_"
                        + trouble_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not action.strip():
                        st.warning(
                            "試したことを入力してね。"
                        )
                    else:
                        add_attempt(
                            data=data,
                            trouble_id=(
                                trouble_id
                            ),
                            action=(
                                action.strip()
                            ),
                            result=result,
                            note=(
                                attempt_note.strip()
                            ),
                            attempt_date=(
                                attempt_date
                            ),
                        )

                        st.rerun()

            if attempts:
                st.markdown(
                    "#### 🧪 これまでの試行"
                )

                for index, attempt in enumerate(
                    attempts,
                    start=1,
                ):
                    st.write(
                        f"**試行{index}** "
                        f"{attempt.get('action', '')}"
                    )

                    st.caption(
                        f"{attempt.get('result', '')}"
                        f" ｜ "
                        f"{format_date(attempt.get('attempt_date'))}"
                    )

            if age >= 30:
                st.warning(
                    "この問題は30日以上"
                    "未解決です。"
                    "まだ困ってる？"
                )

                if st.button(
                    "🍃 もう気にならない",
                    key=(
                        "close_"
                        + trouble_id
                    ),
                    use_container_width=True,
                ):
                    close_trouble(
                        data,
                        trouble_id,
                    )
                    st.rerun()


# =========================================================
# 解決済み
# =========================================================

if resolved:
    st.divider()

    st.subheader(
        "🎉 解決した経験"
    )

    for trouble in sorted(
        resolved,
        key=lambda row: (
            row.get(
                "resolved_date",
                "",
            )
        ),
        reverse=True,
    )[:10]:
        trouble_id = trouble.get(
            "id",
            "",
        )

        attempts = get_attempts(
            data,
            trouble_id,
        )

        success = (
            final_success_attempt(
                data,
                trouble_id,
            )
        )

        recurrence_count = len(
            get_recurrences(
                data,
                trouble_id,
            )
        )

        with st.container(
            border=True
        ):
            col1, col2 = st.columns(
                [8, 1]
            )

            with col1:
                st.write(
                    "**"
                    + trouble.get(
                        "title",
                        "",
                    )
                    + "**"
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if trouble.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "resolved_fav_"
                        + trouble_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        trouble_id,
                    )
                    st.rerun()

            st.caption(
                trouble.get(
                    "category",
                    "",
                )
                + " ｜ "
                + resolution_text(
                    trouble.get(
                        "start_date"
                    ),
                    trouble.get(
                        "resolved_date"
                    ),
                )
            )

            if trouble.get(
                "cause"
            ):
                st.write(
                    "**🔍 原因**"
                )
                st.write(
                    trouble.get(
                        "cause",
                        "",
                    )
                )

            if success:
                st.write(
                    "**🎉 最終的な解決法**"
                )
                st.success(
                    success.get(
                        "action",
                        "",
                    )
                )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "🧪 試行",
                f"{len(attempts)}回",
            )

            col2.metric(
                "🔁 再発",
                f"{recurrence_count}回",
            )

            col3.metric(
                "♻️ 再利用成功",
                f"{helpful_count(data, trouble_id)}回",
            )

            with st.expander(
                "🔁 また起きた"
            ):
                recurrence_date = (
                    st.date_input(
                        "再発日",
                        value=today,
                        max_value=today,
                        key=(
                            "recurrence_date_"
                            + trouble_id
                        ),
                    )
                )

                recurrence_note = (
                    st.text_area(
                        "今回の状況",
                        key=(
                            "recurrence_note_"
                            + trouble_id
                        ),
                    )
                )

                if st.button(
                    "🔁 再発を記録",
                    key=(
                        "recurrence_"
                        + trouble_id
                    ),
                    use_container_width=True,
                ):
                    add_recurrence(
                        data,
                        trouble_id,
                        recurrence_date,
                        recurrence_note.strip(),
                    )
                    st.rerun()

            with st.expander(
                "♻️ 解決法をまた使った"
            ):
                reuse_result = (
                    st.selectbox(
                        "今回どうだった？",
                        REUSE_RESULTS,
                        key=(
                            "reuse_result_"
                            + trouble_id
                        ),
                    )
                )

                reuse_note = (
                    st.text_area(
                        "メモ",
                        key=(
                            "reuse_note_"
                            + trouble_id
                        ),
                    )
                )

                if st.button(
                    "♻️ 結果を記録",
                    key=(
                        "reuse_"
                        + trouble_id
                    ),
                    use_container_width=True,
                ):
                    add_reuse(
                        data,
                        trouble_id,
                        reuse_result,
                        reuse_note.strip(),
                    )
                    st.rerun()


# =========================================================
# よく効く解決法
# =========================================================

helpful_ranking = []

for trouble in resolved:
    count = helpful_count(
        data,
        trouble.get(
            "id",
            "",
        ),
    )

    if count > 0:
        helpful_ranking.append(
            (
                trouble,
                count,
            )
        )

if helpful_ranking:
    st.divider()

    st.subheader(
        "🏆 よく効く解決法"
    )

    helpful_ranking.sort(
        key=lambda pair: pair[1],
        reverse=True,
    )

    for rank, (
        trouble,
        count,
    ) in enumerate(
        helpful_ranking[:10],
        start=1,
    ):
        medal = {
            1: "🥇",
            2: "🥈",
            3: "🥉",
        }.get(
            rank,
            f"{rank}.",
        )

        success = (
            final_success_attempt(
                data,
                trouble.get(
                    "id",
                    "",
                ),
            )
        )

        if success:
            st.write(
                f"{medal} "
                f"**{success.get('action', '')}**"
            )

            st.caption(
                f"元の問題："
                f"{trouble.get('title', '')}"
                f" ｜ ♻️ {count}回助かった"
            )


# =========================================================
# 再発ランキング
# =========================================================

recurrence_ranking = []

for trouble in troubles:
    count = len(
        get_recurrences(
            data,
            trouble.get(
                "id",
                "",
            ),
        )
    )

    if count:
        recurrence_ranking.append(
            (
                trouble,
                count,
            )
        )

if recurrence_ranking:
    st.divider()

    st.subheader(
        "🚨 よく再発する問題"
    )

    recurrence_ranking.sort(
        key=lambda pair: pair[1],
        reverse=True,
    )

    for trouble, count in (
        recurrence_ranking[:10]
    ):
        st.write(
            f"🔁 **{trouble.get('title', '')}**"
            f" — {count}回再発"
        )


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {today.month}月のトラブル"
)

month_troubles = [
    trouble
    for trouble in troubles
    if (
        trouble.get(
            "start_date",
            "",
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_resolved = [
    trouble
    for trouble in troubles
    if (
        trouble.get(
            "resolved_date",
            "",
        )
        or ""
    ).startswith(
        month_prefix
    )
]

month_attempts = [
    row
    for row in data["attempts"]
    if (
        row.get(
            "attempt_date",
            "",
        )
        or ""
    ).startswith(
        month_prefix
    )
]

same_day_resolved = [
    trouble
    for trouble in month_resolved
    if days_between(
        trouble.get(
            "start_date"
        ),
        trouble.get(
            "resolved_date"
        ),
    ) == 0
]

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "😵 発生",
    f"{len(month_troubles)}件",
)

col2.metric(
    "🎉 解決",
    f"{len(month_resolved)}件",
)

col3.metric(
    "🧪 試行",
    f"{len(month_attempts)}回",
)

col4.metric(
    "⚡ 当日解決",
    f"{len(same_day_resolved)}件",
)

if month_resolved:
    attempt_counts = [
        len(
            get_attempts(
                data,
                trouble.get(
                    "id",
                    "",
                ),
            )
        )
        for trouble in month_resolved
    ]

    average_attempts = (
        sum(attempt_counts)
        / len(attempt_counts)
    )

    st.caption(
        "🎯 今月解決した問題は、"
        f"平均 {average_attempts:.1f}回"
        "の試行を記録しています。"
    )

if month_troubles:
    category_counts = {}

    for trouble in (
        month_troubles
    ):
        category = trouble.get(
            "category",
            "✨ その他",
        )

        category_counts[
            category
        ] = (
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
                    "件数": value,
                }
                for key, value
                in category_counts.items()
            ]
        )
        .sort_values(
            "件数",
            ascending=False,
        )
    )

    st.markdown(
        "### 🏷️ カテゴリー"
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )


# =========================================================
# 過去トラブルガチャ
# =========================================================

old_troubles = [
    trouble
    for trouble in troubles
    if (
        parse_date(
            trouble.get(
                "start_date"
            )
        )
        and (
            today
            - parse_date(
                trouble.get(
                    "start_date"
                )
            )
        ).days >= 30
    )
]

if old_troubles:
    st.divider()

    st.subheader(
        "🎲 こんなことに困っていました"
    )

    old_ids = [
        trouble.get("id")
        for trouble in old_troubles
    ]

    random_id = (
        st.session_state.get(
            "random_trouble_id"
        )
    )

    if random_id not in old_ids:
        random_id = random.choice(
            old_ids
        )

        st.session_state[
            "random_trouble_id"
        ] = random_id

    random_trouble = (
        get_trouble(
            data,
            random_id,
        )
    )

    if random_trouble:
        success = (
            final_success_attempt(
                data,
                random_id,
            )
        )

        with st.container(
            border=True
        ):
            st.caption(
                format_date(
                    random_trouble.get(
                        "start_date"
                    )
                )
            )

            st.subheader(
                random_trouble.get(
                    "title",
                    "",
                )
            )

            st.write(
                random_trouble.get(
                    "status",
                    "",
                )
            )

            if random_trouble.get(
                "cause"
            ):
                st.write(
                    "**🔍 原因**"
                )
                st.write(
                    random_trouble.get(
                        "cause",
                        "",
                    )
                )

            if success:
                st.write(
                    "**🛠️ 解決法**"
                )
                st.success(
                    success.get(
                        "action",
                        "",
                    )
                )

            st.caption(
                f"🧪 試行 "
                f"{len(get_attempts(data, random_id))}回"
                f" ｜ 🔁 再発 "
                f"{len(get_recurrences(data, random_id))}回"
                f" ｜ ♻️ 再利用成功 "
                f"{helpful_count(data, random_id)}回"
            )

        if st.button(
            "🎲 別の経験を見る",
            use_container_width=True,
        ):
            alternatives = [
                item_id
                for item_id in old_ids
                if item_id
                != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_trouble_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# 困ったこと図鑑
# =========================================================

st.divider()

st.subheader(
    "📚 困ったこと図鑑"
)

library_search = st.text_input(
    "🔎 図鑑を検索",
    placeholder=(
        "Python、画像、車……"
    ),
    key="library_search",
)

col1, col2 = st.columns(2)

with col1:
    category_filter = (
        st.selectbox(
            "カテゴリー",
            ["すべて"]
            + CATEGORIES,
            key="category_filter",
        )
    )

with col2:
    status_filter = (
        st.selectbox(
            "状態",
            ["すべて"]
            + STATUSES,
            key="status_filter",
        )
    )

filtered = []

for trouble in troubles:
    if (
        category_filter
        != "すべて"
        and trouble.get(
            "category"
        ) != category_filter
    ):
        continue

    if (
        status_filter
        != "すべて"
        and trouble.get(
            "status"
        ) != status_filter
    ):
        continue

    trouble_id = trouble.get(
        "id",
        "",
    )

    searchable_parts = [
        trouble.get(
            "title",
            "",
        ),
        trouble.get(
            "situation",
            "",
        ),
        trouble.get(
            "cause",
            "",
        ),
        trouble.get(
            "resolution",
            "",
        ),
        trouble.get(
            "memo",
            "",
        ),
    ]

    for attempt in get_attempts(
        data,
        trouble_id,
    ):
        searchable_parts.append(
            attempt.get(
                "action",
                "",
            )
        )

    searchable = " ".join(
        searchable_parts
    ).lower()

    if (
        library_search.strip()
        and library_search
        .strip()
        .lower()
        not in searchable
    ):
        continue

    filtered.append(
        trouble
    )

if not filtered:
    st.info(
        "条件に合う経験はありません。"
    )

else:
    rows = []

    for trouble in sorted(
        filtered,
        key=lambda row: (
            row.get(
                "start_date",
                "",
            )
        ),
        reverse=True,
    ):
        trouble_id = trouble.get(
            "id",
            "",
        )

        rows.append(
            {
                "日付": format_date(
                    trouble.get(
                        "start_date"
                    )
                ),
                "問題": trouble.get(
                    "title",
                    "",
                ),
                "カテゴリー": trouble.get(
                    "category",
                    "",
                ),
                "状態": trouble.get(
                    "status",
                    "",
                ),
                "試行": len(
                    get_attempts(
                        data,
                        trouble_id,
                    )
                ),
                "再発": len(
                    get_recurrences(
                        data,
                        trouble_id,
                    )
                ),
                "再利用成功": (
                    helpful_count(
                        data,
                        trouble_id,
                    )
                ),
                "⭐": (
                    "⭐"
                    if trouble.get(
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
# 編集・履歴・削除
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・履歴・削除"
):
    if not troubles:
        st.caption(
            "まだ記録がありません。"
        )

    for trouble in sorted(
        troubles,
        key=lambda row: (
            row.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    ):
        trouble_id = trouble.get(
            "id",
            "",
        )

        with st.expander(
            trouble.get(
                "title",
                "",
            )
        ):
            edit_title = (
                st.text_input(
                    "問題",
                    value=trouble.get(
                        "title",
                        "",
                    ),
                    key=(
                        "edit_title_"
                        + trouble_id
                    ),
                )
            )

            old_category = (
                trouble.get(
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
                        + trouble_id
                    ),
                )
            )

            edit_situation = (
                st.text_area(
                    "状況",
                    value=trouble.get(
                        "situation",
                        "",
                    ),
                    key=(
                        "edit_situation_"
                        + trouble_id
                    ),
                )
            )

            edit_cause = (
                st.text_area(
                    "原因",
                    value=trouble.get(
                        "cause",
                        "",
                    ),
                    key=(
                        "edit_cause_"
                        + trouble_id
                    ),
                )
            )

            old_source = (
                trouble.get(
                    "cause_source",
                    "❓ まだ分からない",
                )
            )

            source_index = (
                CAUSE_SOURCES.index(
                    old_source
                )
                if old_source
                in CAUSE_SOURCES
                else 0
            )

            edit_source = (
                st.selectbox(
                    "原因はどう分かった？",
                    CAUSE_SOURCES,
                    index=source_index,
                    key=(
                        "edit_source_"
                        + trouble_id
                    ),
                )
            )

            edit_memo = (
                st.text_area(
                    "メモ",
                    value=trouble.get(
                        "memo",
                        "",
                    ),
                    key=(
                        "edit_memo_"
                        + trouble_id
                    ),
                )
            )

            col1, col2 = (
                st.columns(2)
            )

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "save_"
                        + trouble_id
                    ),
                    type="primary",
                    use_container_width=True,
                ):
                    if not (
                        edit_title.strip()
                    ):
                        st.warning(
                            "問題を入力してね。"
                        )
                    else:
                        update_trouble(
                            data=data,
                            trouble_id=(
                                trouble_id
                            ),
                            title=(
                                edit_title.strip()
                            ),
                            category=(
                                edit_category
                            ),
                            situation=(
                                edit_situation.strip()
                            ),
                            cause=(
                                edit_cause.strip()
                            ),
                            cause_source=(
                                edit_source
                            ),
                            memo=(
                                edit_memo.strip()
                            ),
                        )

                        st.rerun()

            with col2:
                if st.button(
                    (
                        "⭐ お気に入り解除"
                        if trouble.get(
                            "favorite",
                            False,
                        )
                        else "☆ お気に入り"
                    ),
                    key=(
                        "fav_"
                        + trouble_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        trouble_id,
                    )
                    st.rerun()

            st.markdown(
                "#### 🧪 試行履歴"
            )

            attempts = get_attempts(
                data,
                trouble_id,
            )

            if not attempts:
                st.caption(
                    "まだ試行はありません。"
                )

            for index, attempt in enumerate(
                attempts,
                start=1,
            ):
                with st.container(
                    border=True
                ):
                    st.write(
                        f"**試行{index}："
                        f"{attempt.get('action', '')}**"
                    )

                    st.caption(
                        format_date(
                            attempt.get(
                                "attempt_date"
                            )
                        )
                        + " ｜ "
                        + attempt.get(
                            "result",
                            "",
                        )
                    )

                    if attempt.get(
                        "note"
                    ):
                        st.write(
                            attempt.get(
                                "note",
                                "",
                            )
                        )

                    if st.button(
                        "🗑️ この試行を削除",
                        key=(
                            "delete_attempt_"
                            + attempt.get(
                                "id",
                                "",
                            )
                        ),
                    ):
                        delete_attempt(
                            data,
                            attempt.get(
                                "id",
                                "",
                            ),
                        )
                        st.rerun()

            recurrences = (
                get_recurrences(
                    data,
                    trouble_id,
                )
            )

            if recurrences:
                st.markdown(
                    "#### 🔁 再発履歴"
                )

                for recurrence in (
                    recurrences
                ):
                    st.write(
                        format_date(
                            recurrence.get(
                                "recurrence_date"
                            )
                        )
                        + " — "
                        + (
                            recurrence.get(
                                "note",
                                "",
                            )
                            or "再発"
                        )
                    )

            reuses = get_reuses(
                data,
                trouble_id,
            )

            if reuses:
                st.markdown(
                    "#### ♻️ 再利用履歴"
                )

                for reuse in reuses:
                    st.write(
                        format_date(
                            reuse.get(
                                "reuse_date"
                            )
                        )
                        + " — "
                        + reuse.get(
                            "result",
                            "",
                        )
                    )

            if trouble.get(
                "status"
            ) == "🍃 終了":
                if st.button(
                    "🔄 未解決に戻す",
                    key=(
                        "reopen_"
                        + trouble_id
                    ),
                    use_container_width=True,
                ):
                    reopen_trouble(
                        data,
                        trouble_id,
                    )
                    st.rerun()

            st.markdown(
                "#### 🗑️ 完全削除"
            )

            confirm = st.checkbox(
                "この問題とすべての履歴を削除する",
                key=(
                    "confirm_"
                    + trouble_id
                ),
            )

            if st.button(
                "🗑️ 完全削除",
                key=(
                    "delete_"
                    + trouble_id
                ),
                disabled=not confirm,
                use_container_width=True,
            ):
                delete_trouble(
                    data,
                    trouble_id,
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
            "what_did_i_do_"
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
    "🧠 今日困ったことは、"
    "未来の自分を助ける知識になる。"
)

st.caption(
    "🛠️ うまくいかなかった方法も、"
    "立派な答えのひとつ。"
)
