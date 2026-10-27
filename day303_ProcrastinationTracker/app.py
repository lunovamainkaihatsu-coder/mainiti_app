import json
import os
import random
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="今日、何を先延ばしした？",
    page_icon="🐢",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "procrastination.json",
)

REASONS = [
    "😩 面倒だった",
    "😰 難しそうだった",
    "⏰ 時間がなかった",
    "😴 疲れていた",
    "🤔 やり方が分からなかった",
    "😨 失敗したくなかった",
    "🎮 他のことをしたかった",
    "📦 その他",
]

STATUSES = [
    "📦 保留",
    "✅ 完了",
    "🗑️ やらない",
]

WEEKDAYS = [
    "月",
    "火",
    "水",
    "木",
    "金",
    "土",
    "日",
]


# =========================================================
# HELPERS
# =========================================================

def new_id():
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
            str(value),
            "%Y-%m-%d",
        ).date()

    except (ValueError, TypeError):
        return None


def format_date(value):
    d = parse_date(value)

    if not d:
        return "-"

    return d.strftime("%Y/%m/%d")


def format_minutes(minutes):
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        return "-"

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    remain = minutes % 60

    if remain == 0:
        return f"{hours}時間"

    return f"{hours}時間{remain}分"


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def days_waiting(item):
    first_date = parse_date(
        item.get("first_date")
    )

    if not first_date:
        return 0

    end_date = date.today()

    if (
        item.get("status")
        == "✅ 完了"
    ):
        completed = parse_date(
            item.get("completed_date")
        )

        if completed:
            end_date = completed

    elif (
        item.get("status")
        == "🗑️ やらない"
    ):
        decided = parse_date(
            item.get("decided_date")
        )

        if decided:
            end_date = decided

    return max(
        0,
        (end_date - first_date).days,
    )


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "items": [],
        "postponements": [],
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
    ) as f:
        json.dump(
            data,
            f,
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
        data = default_data()
        save_data(data)
        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(
            data,
            dict,
        ):
            data = default_data()

        data.setdefault(
            "items",
            [],
        )

        data.setdefault(
            "postponements",
            [],
        )

        for item in data["items"]:
            item.setdefault(
                "id",
                new_id(),
            )
            item.setdefault(
                "title",
                "",
            )
            item.setdefault(
                "first_date",
                str(date.today()),
            )
            item.setdefault(
                "planned_date",
                str(date.today()),
            )
            item.setdefault(
                "estimated_minutes",
                30,
            )
            item.setdefault(
                "reasons",
                [],
            )
            item.setdefault(
                "barrier",
                3,
            )
            item.setdefault(
                "status",
                "📦 保留",
            )
            item.setdefault(
                "completed_date",
                None,
            )
            item.setdefault(
                "actual_minutes",
                None,
            )
            item.setdefault(
                "after_note",
                "",
            )
            item.setdefault(
                "decided_date",
                None,
            )
            item.setdefault(
                "memo",
                "",
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

        for row in data[
            "postponements"
        ]:
            row.setdefault(
                "id",
                new_id(),
            )
            row.setdefault(
                "item_id",
                "",
            )
            row.setdefault(
                "date",
                str(date.today()),
            )
            row.setdefault(
                "next_date",
                str(date.today()),
            )
            row.setdefault(
                "memo",
                "",
            )
            row.setdefault(
                "created_at",
                now_text(),
            )

        return data

    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        data = default_data()
        save_data(data)
        return data


# =========================================================
# GETTERS
# =========================================================

def get_item(data, item_id):
    return next(
        (
            item
            for item in data["items"]
            if item.get("id")
            == item_id
        ),
        None,
    )


def postponements_for(
    data,
    item_id,
):
    return sorted(
        [
            row
            for row
            in data["postponements"]
            if row.get("item_id")
            == item_id
        ],
        key=lambda row: (
            row.get("date", ""),
            row.get(
                "created_at",
                "",
            ),
        ),
    )


def postponement_count(
    data,
    item_id,
):
    return len(
        postponements_for(
            data,
            item_id,
        )
    )


def item_label(item):
    return (
        f"{item.get('title', '')}"
        f" [{item.get('id', '')[:6]}]"
    )


# =========================================================
# CRUD
# =========================================================

def add_item(
    data,
    title,
    first_date,
    planned_date,
    estimated_minutes,
    reasons,
    barrier,
    memo,
):
    item = {
        "id": new_id(),
        "title": title,
        "first_date": str(
            first_date
        ),
        "planned_date": str(
            planned_date
        ),
        "estimated_minutes": int(
            estimated_minutes
        ),
        "reasons": reasons,
        "barrier": int(barrier),
        "status": "📦 保留",
        "completed_date": None,
        "actual_minutes": None,
        "after_note": "",
        "decided_date": None,
        "memo": memo,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["items"].append(
        item
    )

    save_data(data)


def postpone_item(
    data,
    item_id,
    next_date,
    memo,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    row = {
        "id": new_id(),
        "item_id": item_id,
        "date": str(
            date.today()
        ),
        "next_date": str(
            next_date
        ),
        "memo": memo,
        "created_at": now_text(),
    }

    data[
        "postponements"
    ].append(row)

    item[
        "planned_date"
    ] = str(next_date)

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def complete_item(
    data,
    item_id,
    completed_date,
    actual_minutes,
    after_note,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = (
        "✅ 完了"
    )

    item[
        "completed_date"
    ] = str(
        completed_date
    )

    item[
        "actual_minutes"
    ] = int(
        actual_minutes
    )

    item[
        "after_note"
    ] = after_note

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def abandon_item(
    data,
    item_id,
):
    item = get_item(
        data,
        item_id,
    )

    if not item:
        return

    item["status"] = (
        "🗑️ やらない"
    )

    item[
        "decided_date"
    ] = str(
        date.today()
    )

    item[
        "updated_at"
    ] = now_text()

    save_data(data)


def delete_item(
    data,
    item_id,
):
    data["items"] = [
        item
        for item in data["items"]
        if item.get("id")
        != item_id
    ]

    data[
        "postponements"
    ] = [
        row
        for row
        in data["postponements"]
        if row.get("item_id")
        != item_id
    ]

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .hero {
        text-align: center;
        padding: 38px 20px;
        margin-bottom: 24px;
        border-radius: 28px;
        background:
            linear-gradient(
                135deg,
                rgba(100, 180, 130, .13),
                rgba(220, 180, 80, .10)
            );
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        border:
            1px solid
            rgba(100, 160, 120, .15);
        background:
            rgba(100, 180, 130, .05);
    }

    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 30px;
        border-radius: 25px;
        background:
            rgba(100, 160, 120, .05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()

items = data["items"]

today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>🐢 DAY 303 / 365</div>
        <h1>今日、何を先延ばしした？</h1>
        <p>
            先延ばしを責めるのではなく、
            「なぜ止まった？」を観察する。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

(
    tab_home,
    tab_box,
    tab_analysis,
    tab_done,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🏠 今日",
        "📦 先延ばしBOX",
        "🧠 分析",
        "🌱 結局やった",
        "📚 図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    st.subheader(
        "🐢 今日、何を先延ばしした？"
    )

    with st.form(
        "new_item",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "先延ばししたこと",
            placeholder=(
                "例：部屋の片付け"
            ),
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            first_date = (
                st.date_input(
                    "先延ばしした日",
                    value=today,
                    max_value=today,
                )
            )

        with col2:
            planned_date = (
                st.date_input(
                    "本当はいつやる予定だった？",
                    value=today,
                )
            )

        estimated = (
            st.number_input(
                "どれくらいかかると思う？（分）",
                min_value=1,
                value=30,
                step=5,
            )
        )

        reasons = st.multiselect(
            "なぜ先延ばしした？",
            REASONS,
        )

        barrier = st.slider(
            "始めるハードル",
            1,
            5,
            3,
            help=(
                "1 = すぐ始められそう"
                " / 5 = かなり重い"
            ),
        )

        memo = st.text_area(
            "メモ（任意）",
            placeholder=(
                "今日は仕事で疲れていた"
            ),
        )

        if st.form_submit_button(
            "📦 先延ばしBOXへ",
            type="primary",
            use_container_width=True,
        ):
            if not title.strip():
                st.warning(
                    "内容を入力してね。"
                )

            else:
                add_item(
                    data=data,
                    title=title.strip(),
                    first_date=first_date,
                    planned_date=(
                        planned_date
                    ),
                    estimated_minutes=(
                        estimated
                    ),
                    reasons=reasons,
                    barrier=barrier,
                    memo=memo.strip(),
                )

                st.rerun()

    # -----------------------------------------------------
    # DASHBOARD
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "📊 今の先延ばし"
    )

    pending = [
        item
        for item in items
        if item.get(
            "status"
        ) == "📦 保留"
    ]

    completed = [
        item
        for item in items
        if item.get(
            "status"
        ) == "✅ 完了"
    ]

    abandoned = [
        item
        for item in items
        if item.get(
            "status"
        ) == "🗑️ やらない"
    ]

    total_count = len(items)

    completion_rate = (
        len(completed)
        / total_count
        * 100
        if total_count
        else 0
    )

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "📦 保留",
        f"{len(pending)}件",
    )

    c2.metric(
        "🌱 結局やった",
        f"{len(completed)}件",
    )

    c3.metric(
        "🗑️ やらない",
        f"{len(abandoned)}件",
    )

    c4.metric(
        "✅ 完了率",
        (
            f"{completion_rate:.1f}%"
            if total_count
            else "-"
        ),
    )

    # -----------------------------------------------------
    # TODAY
    # -----------------------------------------------------

    today_items = [
        item
        for item in items
        if item.get(
            "first_date"
        ) == str(today)
    ]

    if today_items:
        st.divider()

        st.subheader(
            "🐢 今日の記録"
        )

        for item in reversed(
            today_items
        ):
            with st.container(
                border=True
            ):
                st.write(
                    f"**{item.get('title')}**"
                )

                st.caption(
                    f"予想 "
                    f"{format_minutes(item.get('estimated_minutes'))}"
                    f" ｜ "
                    f"ハードル {item.get('barrier')}/5"
                    f" ｜ "
                    f"{item.get('status')}"
                )

                if item.get(
                    "reasons"
                ):
                    st.write(
                        " / ".join(
                            item.get(
                                "reasons"
                            )
                        )
                    )


# =========================================================
# BOX
# =========================================================

with tab_box:

    st.subheader(
        "📦 先延ばしBOX"
    )

    pending = sorted(
        [
            item
            for item in items
            if item.get(
                "status"
            ) == "📦 保留"
        ],
        key=lambda item: (
            item.get(
                "first_date",
                ""
            )
        ),
    )

    if not pending:
        st.success(
            "📦 BOXは空っぽです！"
        )

    else:
        box_options = {
            item_label(item):
            item.get("id")
            for item in pending
        }

        selected_label = (
            st.selectbox(
                "取り出す",
                list(
                    box_options.keys()
                ),
                key="box_item",
            )
        )

        selected_id = (
            box_options[
                selected_label
            ]
        )

        item = get_item(
            data,
            selected_id,
        )

        postpone_count = (
            postponement_count(
                data,
                selected_id,
            )
        )

        st.markdown(
            f"### 🐢 "
            f"{item.get('title')}"
        )

        c1, c2, c3 = (
            st.columns(3)
        )

        c1.metric(
            "寝かせた日数",
            f"{days_waiting(item)}日",
        )

        c2.metric(
            "予想時間",
            format_minutes(
                item.get(
                    "estimated_minutes"
                )
            ),
        )

        c3.metric(
            "延期回数",
            f"{postpone_count}回",
        )

        if item.get(
            "reasons"
        ):
            st.write(
                "**止まった理由**"
            )

            st.write(
                " / ".join(
                    item.get(
                        "reasons"
                    )
                )
            )

        st.write(
            f"**始めるハードル：** "
            f"{'★' * safe_int(item.get('barrier'))}"
            f"{'☆' * (5 - safe_int(item.get('barrier')))}"
        )

        if item.get(
            "memo"
        ):
            st.info(
                item.get("memo")
            )

        # -------------------------------------------------
        # COMPLETE
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "#### ▶ やってみた！"
        )

        with st.form(
            "complete_item"
        ):
            completed_date = (
                st.date_input(
                    "完了日",
                    value=today,
                    min_value=(
                        parse_date(
                            item.get(
                                "first_date"
                            )
                        )
                    ),
                    max_value=today,
                )
            )

            actual_minutes = (
                st.number_input(
                    "実際にかかった時間（分）",
                    min_value=1,
                    value=30,
                    step=5,
                )
            )

            after_note = (
                st.text_area(
                    "やってみてどうだった？",
                    placeholder=(
                        "始めれば意外とすぐだった"
                    ),
                )
            )

            if st.form_submit_button(
                "🌱 完了！",
                type="primary",
                use_container_width=True,
            ):
                complete_item(
                    data=data,
                    item_id=selected_id,
                    completed_date=(
                        completed_date
                    ),
                    actual_minutes=(
                        actual_minutes
                    ),
                    after_note=(
                        after_note.strip()
                    ),
                )

                st.rerun()

        # -------------------------------------------------
        # POSTPONE
        # -------------------------------------------------

        st.markdown(
            "#### 📅 もう少し延期"
        )

        with st.form(
            "postpone_item"
        ):
            next_date = (
                st.date_input(
                    "次にやる予定",
                    value=max(
                        today,
                        parse_date(
                            item.get(
                                "planned_date"
                            )
                        ) or today,
                    ),
                    key="next_date",
                )
            )

            postpone_memo = (
                st.text_input(
                    "理由・メモ（任意）",
                    placeholder=(
                        "週末にやる"
                    ),
                )
            )

            if st.form_submit_button(
                "📅 延期する",
                use_container_width=True,
            ):
                postpone_item(
                    data=data,
                    item_id=selected_id,
                    next_date=next_date,
                    memo=(
                        postpone_memo
                        .strip()
                    ),
                )

                st.rerun()

        # -------------------------------------------------
        # ABANDON
        # -------------------------------------------------

        st.markdown(
            "#### 🗑️ やらないと決める"
        )

        st.caption(
            "やらないと決めることも、"
            "ひとつの整理です。"
        )

        abandon_confirm = (
            st.checkbox(
                "この項目はやらない",
                key=(
                    "abandon_confirm_"
                    + selected_id
                ),
            )
        )

        if st.button(
            "🗑️ やらないと決める",
            disabled=(
                not abandon_confirm
            ),
            use_container_width=True,
        ):
            abandon_item(
                data,
                selected_id,
            )

            st.rerun()

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        history = postponements_for(
            data,
            selected_id,
        )

        if history:
            st.divider()

            st.markdown(
                "#### 🔁 延期履歴"
            )

            for index, row in enumerate(
                history,
                start=1,
            ):
                st.write(
                    f"**{index}回目** "
                    f"{format_date(row.get('date'))}"
                    f" → "
                    f"{format_date(row.get('next_date'))}"
                )

                if row.get(
                    "memo"
                ):
                    st.caption(
                        row.get(
                            "memo"
                        )
                    )

    # -----------------------------------------------------
    # RANDOM OLD
    # -----------------------------------------------------

    old_pending = [
        item
        for item in pending
        if days_waiting(item)
        >= 14
    ]

    if old_pending:
        st.divider()

        st.subheader(
            "🎲 これ、まだやる？"
        )

        old_ids = [
            item.get("id")
            for item in old_pending
        ]

        random_id = (
            st.session_state.get(
                "random_old"
            )
        )

        if random_id not in old_ids:
            random_id = random.choice(
                old_ids
            )

            st.session_state[
                "random_old"
            ] = random_id

        old_item = get_item(
            data,
            random_id,
        )

        with st.container(
            border=True
        ):
            st.caption(
                f"🎲 "
                f"{days_waiting(old_item)}日前から"
                "ここにあります"
            )

            st.markdown(
                f"### "
                f"{old_item.get('title')}"
            )

            st.write(
                f"予想："
                f"{format_minutes(old_item.get('estimated_minutes'))}"
            )

            st.write(
                f"延期："
                f"{postponement_count(data, random_id)}回"
            )

        if st.button(
            "🎲 別の項目を見る",
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
                    "random_old"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "🧠 なぜ先延ばしする？"
    )

    if not items:
        st.info(
            "記録が増えると、"
            "ここに傾向が見えてきます。"
        )

    else:
        # -------------------------------------------------
        # REASON COUNTS
        # -------------------------------------------------

        reason_counter = Counter()

        for item in items:
            for reason in item.get(
                "reasons",
                [],
            ):
                reason_counter[
                    reason
                ] += 1

        if reason_counter:
            reason_df = pd.DataFrame(
                [
                    {
                        "理由": reason,
                        "記録数": count,
                    }
                    for reason, count
                    in reason_counter
                    .most_common()
                ]
            ).set_index(
                "理由"
            )

            st.bar_chart(
                reason_df
            )

            top_reason = (
                reason_counter
                .most_common(1)[0][0]
            )

            st.info(
                f"🔍 最近の記録では、"
                f"**「{top_reason}」**"
                "が最も多く記録されています。"
            )

        # -------------------------------------------------
        # REASON x RESULT
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "🔍 理由 × 結果"
        )

        reason_stats = {}

        for reason in REASONS:
            matching = [
                item
                for item in items
                if reason
                in item.get(
                    "reasons",
                    [],
                )
            ]

            if not matching:
                continue

            done = [
                item
                for item in matching
                if item.get(
                    "status"
                ) == "✅ 完了"
            ]

            estimated_values = [
                safe_int(
                    item.get(
                        "estimated_minutes"
                    )
                )
                for item in done
            ]

            actual_values = [
                safe_int(
                    item.get(
                        "actual_minutes"
                    )
                )
                for item in done
            ]

            reason_stats[
                reason
            ] = {
                "total": len(
                    matching
                ),
                "done": len(done),
                "estimated_avg": (
                    sum(
                        estimated_values
                    )
                    / len(
                        estimated_values
                    )
                    if estimated_values
                    else 0
                ),
                "actual_avg": (
                    sum(
                        actual_values
                    )
                    / len(
                        actual_values
                    )
                    if actual_values
                    else 0
                ),
            }

        for reason, stats in (
            reason_stats.items()
        ):
            with st.expander(
                f"{reason} "
                f"— {stats['total']}件"
            ):
                c1, c2 = (
                    st.columns(2)
                )

                c1.metric(
                    "その後やった",
                    f"{stats['done']}件",
                )

                done_rate = (
                    stats["done"]
                    / stats["total"]
                    * 100
                    if stats["total"]
                    else 0
                )

                c2.metric(
                    "完了率",
                    f"{done_rate:.1f}%",
                )

                if stats[
                    "done"
                ]:
                    st.write(
                        "平均予想："
                        f"**{format_minutes(stats['estimated_avg'])}**"
                    )

                    st.write(
                        "平均実際："
                        f"**{format_minutes(stats['actual_avg'])}**"
                    )

                    diff = (
                        stats[
                            "estimated_avg"
                        ]
                        - stats[
                            "actual_avg"
                        ]
                    )

                    if diff > 0:
                        st.success(
                            "💡 完了した記録では、"
                            f"予想より平均"
                            f"**{format_minutes(diff)}**"
                            "早く終わっています。"
                        )

        # -------------------------------------------------
        # PREDICTED VS ACTUAL
        # -------------------------------------------------

        completed_items = [
            item
            for item in items
            if (
                item.get("status")
                == "✅ 完了"
                and item.get(
                    "actual_minutes"
                )
                is not None
            )
        ]

        st.divider()

        st.subheader(
            "😲 思ったよりすぐ終わった"
        )

        faster_items = []

        for item in (
            completed_items
        ):
            estimated = safe_int(
                item.get(
                    "estimated_minutes"
                )
            )

            actual = safe_int(
                item.get(
                    "actual_minutes"
                )
            )

            saved = (
                estimated
                - actual
            )

            if saved > 0:
                faster_items.append(
                    (
                        saved,
                        item,
                    )
                )

        faster_items.sort(
            key=lambda row: row[0],
            reverse=True,
        )

        if not faster_items:
            st.caption(
                "予想より早く終わった記録は"
                "まだありません。"
            )

        else:
            for index, (
                saved,
                item,
            ) in enumerate(
                faster_items[:10],
                start=1,
            ):
                st.write(
                    f"**{index}. "
                    f"{item.get('title')}**"
                )

                st.caption(
                    f"予想 "
                    f"{format_minutes(item.get('estimated_minutes'))}"
                    f" → 実際 "
                    f"{format_minutes(item.get('actual_minutes'))}"
                    f" ｜ "
                    f"−{format_minutes(saved)}"
                )

        # -------------------------------------------------
        # POSTPONE RANKING
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "🔁 最も延期しているもの"
        )

        postpone_ranking = [
            (
                postponement_count(
                    data,
                    item.get("id"),
                ),
                item,
            )
            for item in items
        ]

        postpone_ranking = [
            row
            for row
            in postpone_ranking
            if row[0] > 0
        ]

        postpone_ranking.sort(
            key=lambda row: row[0],
            reverse=True,
        )

        if not postpone_ranking:
            st.caption(
                "延期履歴はまだありません。"
            )

        else:
            for index, (
                count,
                item,
            ) in enumerate(
                postpone_ranking[:10],
                start=1,
            ):
                st.write(
                    f"**{index}. "
                    f"{item.get('title')}** "
                    f"— {count}回"
                )

        # -------------------------------------------------
        # WEEKDAY
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "📅 曜日別"
        )

        weekday_counter = Counter()

        for item in items:
            d = parse_date(
                item.get(
                    "first_date"
                )
            )

            if d:
                weekday_counter[
                    WEEKDAYS[
                        d.weekday()
                    ]
                ] += 1

        weekday_df = pd.DataFrame(
            {
                "曜日": WEEKDAYS,
                "件数": [
                    weekday_counter.get(
                        weekday,
                        0,
                    )
                    for weekday
                    in WEEKDAYS
                ],
            }
        ).set_index(
            "曜日"
        )

        st.bar_chart(
            weekday_df
        )

        # -------------------------------------------------
        # MONTHLY
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "📊 月間レポート"
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:
            report_year = (
                st.number_input(
                    "年",
                    min_value=2000,
                    max_value=2100,
                    value=today.year,
                    step=1,
                    key="report_year",
                )
            )

        with col2:
            report_month = (
                st.selectbox(
                    "月",
                    list(
                        range(1, 13)
                    ),
                    index=(
                        today.month - 1
                    ),
                    format_func=lambda x: (
                        f"{x}月"
                    ),
                    key="report_month",
                )
            )

        monthly_items = []

        for item in items:
            d = parse_date(
                item.get(
                    "first_date"
                )
            )

            if (
                d
                and d.year
                == int(
                    report_year
                )
                and d.month
                == int(
                    report_month
                )
            ):
                monthly_items.append(
                    item
                )

        monthly_done = [
            item
            for item in monthly_items
            if item.get(
                "status"
            ) == "✅ 完了"
        ]

        monthly_pending = [
            item
            for item in monthly_items
            if item.get(
                "status"
            ) == "📦 保留"
        ]

        monthly_abandoned = [
            item
            for item in monthly_items
            if item.get(
                "status"
            ) == "🗑️ やらない"
        ]

        monthly_rate = (
            len(monthly_done)
            / len(monthly_items)
            * 100
            if monthly_items
            else 0
        )

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "🐢 記録",
            f"{len(monthly_items)}件",
        )

        c2.metric(
            "✅ 後からやった",
            f"{len(monthly_done)}件",
        )

        c3.metric(
            "📦 保留",
            f"{len(monthly_pending)}件",
        )

        c4.metric(
            "完了率",
            (
                f"{monthly_rate:.1f}%"
                if monthly_items
                else "-"
            ),
        )

        if monthly_abandoned:
            st.caption(
                "🗑️ やらないと決めた："
                f"{len(monthly_abandoned)}件"
            )

        monthly_reason_counter = (
            Counter()
        )

        for item in monthly_items:
            monthly_reason_counter.update(
                item.get(
                    "reasons",
                    [],
                )
            )

        if monthly_reason_counter:
            top_reason = (
                monthly_reason_counter
                .most_common(1)[0]
            )

            st.info(
                "この月に最も多かった理由："
                f"**{top_reason[0]}** "
                f"（{top_reason[1]}件）"
            )


# =========================================================
# DONE
# =========================================================

with tab_done:

    st.subheader(
        "🌱 結局やった"
    )

    completed_items = sorted(
        [
            item
            for item in items
            if item.get(
                "status"
            ) == "✅ 完了"
        ],
        key=lambda item: (
            item.get(
                "completed_date",
                ""
            )
        ),
        reverse=True,
    )

    if not completed_items:
        st.info(
            "ここには、"
            "先延ばししたけれど"
            "最後にはやった記録が並びます。"
        )

    else:
        total_wait_days = sum(
            days_waiting(item)
            for item
            in completed_items
        )

        average_wait = (
            total_wait_days
            / len(
                completed_items
            )
        )

        c1, c2 = (
            st.columns(2)
        )

        c1.metric(
            "🌱 結局やった",
            f"{len(completed_items)}件",
        )

        c2.metric(
            "平均寝かせ日数",
            f"{average_wait:.1f}日",
        )

        for item in (
            completed_items
        ):
            with st.container(
                border=True
            ):
                st.markdown(
                    f"### 🌱 "
                    f"{item.get('title')}"
                )

                wait_days = (
                    days_waiting(item)
                )

                postpone_count = (
                    postponement_count(
                        data,
                        item.get("id"),
                    )
                )

                if wait_days > 0:
                    st.write(
                        f"**{wait_days}日"
                        "先延ばししたけど、やった。**"
                    )

                else:
                    st.write(
                        "**その日のうちに、やった。**"
                    )

                if postpone_count:
                    st.caption(
                        f"🔁 "
                        f"{postpone_count}回延期"
                    )

                estimated = (
                    safe_int(
                        item.get(
                            "estimated_minutes"
                        )
                    )
                )

                actual = safe_int(
                    item.get(
                        "actual_minutes"
                    )
                )

                st.write(
                    f"予想 "
                    f"{format_minutes(estimated)}"
                    f" → 実際 "
                    f"{format_minutes(actual)}"
                )

                if item.get(
                    "after_note"
                ):
                    st.info(
                        "💭 "
                        + item.get(
                            "after_note"
                        )
                    )


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 先延ばし図鑑"
    )

    search = st.text_input(
        "🔎 検索",
        key="library_search",
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:
        status_filter = (
            st.selectbox(
                "状態",
                ["すべて"]
                + STATUSES,
                key="status_filter",
            )
        )

    with col2:
        reason_filter = (
            st.selectbox(
                "理由",
                ["すべて"]
                + REASONS,
                key="reason_filter",
            )
        )

    barrier_filter = (
        st.select_slider(
            "最大ハードル",
            options=[
                1,
                2,
                3,
                4,
                5,
            ],
            value=5,
        )
    )

    rows = []

    for item in items:

        if (
            status_filter
            != "すべて"
            and item.get(
                "status"
            )
            != status_filter
        ):
            continue

        if (
            reason_filter
            != "すべて"
            and reason_filter
            not in item.get(
                "reasons",
                [],
            )
        ):
            continue

        if (
            safe_int(
                item.get(
                    "barrier"
                )
            )
            > barrier_filter
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
                    "after_note",
                    "",
                ),
            ]
        ).lower()

        if (
            search.strip()
            and search
            .strip()
            .lower()
            not in searchable
        ):
            continue

        rows.append(
            {
                "内容": (
                    item.get("title")
                ),
                "開始": (
                    format_date(
                        item.get(
                            "first_date"
                        )
                    )
                ),
                "日数": (
                    days_waiting(
                        item
                    )
                ),
                "予想": (
                    format_minutes(
                        item.get(
                            "estimated_minutes"
                        )
                    )
                ),
                "延期": (
                    postponement_count(
                        data,
                        item.get("id"),
                    )
                ),
                "ハードル": (
                    item.get(
                        "barrier"
                    )
                ),
                "状態": (
                    item.get(
                        "status"
                    )
                ),
            }
        )

    if rows:
        st.dataframe(
            pd.DataFrame(
                rows
            ),
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "条件に合う記録は"
            "ありません。"
        )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 記録を編集"
    )

    if not items:
        st.info(
            "まだ記録がありません。"
        )

    else:
        manage_options = {
            item_label(item):
            item.get("id")
            for item in items
        }

        manage_label = (
            st.selectbox(
                "編集する記録",
                list(
                    manage_options.keys()
                ),
                key="manage_item",
            )
        )

        manage_id = (
            manage_options[
                manage_label
            ]
        )

        item = get_item(
            data,
            manage_id,
        )

        edit_title = (
            st.text_input(
                "内容",
                value=item.get(
                    "title",
                    "",
                ),
            )
        )

        edit_first_date = (
            st.date_input(
                "最初に先延ばしした日",
                value=(
                    parse_date(
                        item.get(
                            "first_date"
                        )
                    )
                    or today
                ),
                max_value=today,
                key="edit_first_date",
            )
        )

        edit_planned_date = (
            st.date_input(
                "現在の予定日",
                value=(
                    parse_date(
                        item.get(
                            "planned_date"
                        )
                    )
                    or today
                ),
                key="edit_planned_date",
            )
        )

        edit_estimated = (
            st.number_input(
                "予想時間（分）",
                min_value=1,
                value=safe_int(
                    item.get(
                        "estimated_minutes"
                    )
                ),
                step=5,
            )
        )

        edit_reasons = (
            st.multiselect(
                "理由",
                REASONS,
                default=[
                    reason
                    for reason
                    in item.get(
                        "reasons",
                        [],
                    )
                    if reason
                    in REASONS
                ],
            )
        )

        edit_barrier = (
            st.slider(
                "ハードル",
                1,
                5,
                safe_int(
                    item.get(
                        "barrier",
                        3,
                    )
                ),
            )
        )

        edit_memo = (
            st.text_area(
                "メモ",
                value=item.get(
                    "memo",
                    "",
                ),
            )
        )

        if st.button(
            "💾 基本情報を保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_title.strip():
                st.warning(
                    "内容を入力してね。"
                )

            else:
                item[
                    "title"
                ] = edit_title.strip()

                item[
                    "first_date"
                ] = str(
                    edit_first_date
                )

                item[
                    "planned_date"
                ] = str(
                    edit_planned_date
                )

                item[
                    "estimated_minutes"
                ] = int(
                    edit_estimated
                )

                item[
                    "reasons"
                ] = edit_reasons

                item[
                    "barrier"
                ] = int(
                    edit_barrier
                )

                item[
                    "memo"
                ] = edit_memo.strip()

                item[
                    "updated_at"
                ] = now_text()

                save_data(data)

                st.rerun()

        # -------------------------------------------------
        # COMPLETED INFO
        # -------------------------------------------------

        if (
            item.get("status")
            == "✅ 完了"
        ):
            st.divider()

            st.subheader(
                "🌱 完了情報"
            )

            edit_completed_date = (
                st.date_input(
                    "完了日",
                    value=(
                        parse_date(
                            item.get(
                                "completed_date"
                            )
                        )
                        or today
                    ),
                    max_value=today,
                    key=(
                        "manage_completed_date"
                    ),
                )
            )

            edit_actual = (
                st.number_input(
                    "実時間（分）",
                    min_value=1,
                    value=max(
                        1,
                        safe_int(
                            item.get(
                                "actual_minutes"
                            )
                        ),
                    ),
                    step=5,
                    key="manage_actual",
                )
            )

            edit_after_note = (
                st.text_area(
                    "やってみた感想",
                    value=item.get(
                        "after_note",
                        "",
                    ),
                    key=(
                        "manage_after_note"
                    ),
                )
            )

            if st.button(
                "💾 完了情報を保存",
                use_container_width=True,
            ):
                item[
                    "completed_date"
                ] = str(
                    edit_completed_date
                )

                item[
                    "actual_minutes"
                ] = int(
                    edit_actual
                )

                item[
                    "after_note"
                ] = (
                    edit_after_note
                    .strip()
                )

                item[
                    "updated_at"
                ] = now_text()

                save_data(data)

                st.rerun()

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        st.divider()

        st.warning(
            "削除すると、"
            "この項目の延期履歴も"
            "すべて削除されます。"
        )

        delete_confirm = (
            st.checkbox(
                "この記録を削除する",
                key=(
                    "delete_confirm_"
                    + manage_id
                ),
            )
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=(
                not delete_confirm
            ),
            key=(
                "delete_"
                + manage_id
            ),
            use_container_width=True,
        ):
            delete_item(
                data,
                manage_id,
            )

            st.rerun()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            "procrastination_"
            f"{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        <p>
            🐢 <b>
            先延ばしした日があってもいい。
            </b>
        </p>

        <p>
            🔍 大切なのは、
            自分がどこで止まりやすいのかを
            知ること。
        </p>

        <p>
            🌱 そして、あとからやったなら、
            それもちゃんと前進だ。
        </p>

        <br>

        <b>DAY 303 / 365 — COMPLETE 🔥</b>
    </div>
    """,
    unsafe_allow_html=True,
)
