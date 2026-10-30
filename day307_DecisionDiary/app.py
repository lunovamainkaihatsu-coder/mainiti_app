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
    page_title="今日、何に迷った？",
    page_icon="🤔",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "decisions.json")

STATUS_THINKING = "🤔 迷い中"
STATUS_DECIDED = "✅ 決断済み"
STATUS_REVIEWED = "🔎 振り返り済み"

CATEGORIES = [
    "💼 仕事",
    "💰 お金",
    "📚 勉強",
    "🛒 買い物",
    "🏠 生活",
    "🤝 人間関係",
    "💻 開発",
    "🎮 趣味",
    "🌱 将来",
    "📦 その他",
]

REASONS = [
    "🤔 どちらも良さそう",
    "😨 失敗したくない",
    "💰 お金が気になる",
    "⏰ 時間が気になる",
    "😴 疲れている",
    "🧠 情報が足りない",
    "👀 周りが気になる",
    "💭 気持ちが決まらない",
    "📦 その他",
]

DECISION_METHODS = [
    "⚡ 直感",
    "🧠 よく考えた",
    "💬 誰かに相談",
    "🔎 調べて決めた",
    "🎲 勢い",
    "📦 その他",
]

CHOICES = [
    "A",
    "B",
    "NONE",
    "OTHER",
]

REVIEW_RESULTS = [
    "😊 よかった",
    "😐 どちらともいえない",
    "😕 違ったかも",
]


# =========================================================
# HELPERS
# =========================================================

def new_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


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
        return "未定"

    return d.strftime("%Y/%m/%d")


def star_text(value):
    if value is None:
        return "-"

    value = int(value)
    value = max(0, min(value, 5))

    return "★" * value + "☆" * (5 - value)


def decision_label(item):
    return (
        f"{item.get('question', '')} "
        f"[{item.get('id', '')[:6]}]"
    )


def get_choice_label(item):
    choice = item.get("choice")

    if choice == "A":
        return f"A：{item.get('option_a', '')}"

    if choice == "B":
        return f"B：{item.get('option_b', '')}"

    if choice == "NONE":
        return "どちらも選ばなかった"

    if choice == "OTHER":
        text = item.get(
            "choice_text",
            "",
        )

        return (
            f"別の選択肢：{text}"
            if text
            else "別の選択肢"
        )

    return "-"


def initial_leader(item):
    a = int(
        item.get(
            "a_percent",
            50,
        )
    )

    if a > 50:
        return "A"

    if a < 50:
        return "B"

    return "TIE"


def changed_mind(item):
    leader = initial_leader(item)
    choice = item.get("choice")

    if choice not in ["A", "B"]:
        return False

    if leader == "TIE":
        return False

    return leader != choice


def decision_days(item):
    created = parse_datetime(
        item.get("created_at")
    )

    decided = parse_datetime(
        item.get("decided_at")
    )

    if not created or not decided:
        return None

    return max(
        0,
        (decided.date() - created.date()).days,
    )


def days_since_created(item):
    created = parse_datetime(
        item.get("created_at")
    )

    if not created:
        return None

    return max(
        0,
        (date.today() - created.date()).days,
    )


def deadline_days(item):
    deadline = parse_date(
        item.get("deadline")
    )

    if not deadline:
        return None

    return (
        deadline - date.today()
    ).days


def percent_bar(value):
    value = int(value)
    value = max(0, min(value, 100))

    filled = round(value / 10)
    empty = 10 - filled

    return "█" * filled + "░" * empty


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "decisions": []
    }


def save_data(data):
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    temp_file = DATA_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    os.replace(
        temp_file,
        DATA_FILE,
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
            "decisions",
            [],
        )

        for item in data["decisions"]:
            item.setdefault(
                "id",
                new_id(),
            )
            item.setdefault(
                "question",
                "",
            )
            item.setdefault(
                "category",
                "📦 その他",
            )
            item.setdefault(
                "option_a",
                "",
            )
            item.setdefault(
                "option_b",
                "",
            )
            item.setdefault(
                "a_percent",
                50,
            )
            item.setdefault(
                "confusion_level",
                50,
            )
            item.setdefault(
                "reasons",
                [],
            )
            item.setdefault(
                "memo",
                "",
            )
            item.setdefault(
                "deadline",
                None,
            )
            item.setdefault(
                "status",
                STATUS_THINKING,
            )

            item.setdefault(
                "choice",
                None,
            )
            item.setdefault(
                "choice_text",
                "",
            )
            item.setdefault(
                "decision_method",
                None,
            )
            item.setdefault(
                "deciding_factor",
                "",
            )
            item.setdefault(
                "decided_at",
                None,
            )

            item.setdefault(
                "review_result",
                None,
            )
            item.setdefault(
                "satisfaction",
                None,
            )
            item.setdefault(
                "review_note",
                "",
            )
            item.setdefault(
                "reviewed_at",
                None,
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
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        data = default_data()
        save_data(data)
        return data


# =========================================================
# GETTERS / CRUD
# =========================================================

def get_decision(
    data,
    decision_id,
):
    return next(
        (
            item
            for item
            in data["decisions"]
            if item.get("id")
            == decision_id
        ),
        None,
    )


def add_decision(
    data,
    question,
    category,
    option_a,
    option_b,
    a_percent,
    confusion_level,
    reasons,
    memo,
    deadline,
):
    item = {
        "id": new_id(),
        "question": question,
        "category": category,
        "option_a": option_a,
        "option_b": option_b,
        "a_percent": int(
            a_percent
        ),
        "confusion_level": int(
            confusion_level
        ),
        "reasons": reasons,
        "memo": memo,
        "deadline": (
            str(deadline)
            if deadline
            else None
        ),

        "status": STATUS_THINKING,

        "choice": None,
        "choice_text": "",
        "decision_method": None,
        "deciding_factor": "",
        "decided_at": None,

        "review_result": None,
        "satisfaction": None,
        "review_note": "",
        "reviewed_at": None,

        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["decisions"].append(
        item
    )

    save_data(data)


def decide_item(
    data,
    decision_id,
    choice,
    choice_text,
    method,
    factor,
):
    item = get_decision(
        data,
        decision_id,
    )

    if not item:
        return

    item["choice"] = choice
    item["choice_text"] = (
        choice_text
    )
    item["decision_method"] = (
        method
    )
    item["deciding_factor"] = (
        factor
    )
    item["decided_at"] = (
        now_text()
    )
    item["status"] = (
        STATUS_DECIDED
    )
    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def review_item(
    data,
    decision_id,
    result,
    satisfaction,
    note,
):
    item = get_decision(
        data,
        decision_id,
    )

    if not item:
        return

    item["review_result"] = (
        result
    )
    item["satisfaction"] = int(
        satisfaction
    )
    item["review_note"] = (
        note
    )
    item["reviewed_at"] = (
        now_text()
    )
    item["status"] = (
        STATUS_REVIEWED
    )
    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_decision(
    data,
    decision_id,
):
    data["decisions"] = [
        item
        for item
        in data["decisions"]
        if item.get("id")
        != decision_id
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
        padding: 42px 25px;
        text-align: center;
        border-radius: 28px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(120, 130, 255, .12),
                rgba(255, 200, 100, .10),
                rgba(255, 255, 255, .02)
            );
    }

    .decision-card {
        padding: 20px;
        border-radius: 20px;
        border:
            1px solid
            rgba(130, 140, 220, .18);
        margin-bottom: 12px;
    }

    .timeline-card {
        padding: 25px;
        border-radius: 22px;
        background:
            linear-gradient(
                135deg,
                rgba(120, 140, 255, .08),
                rgba(255, 210, 110, .08)
            );
        margin: 15px 0;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background:
            rgba(120, 140, 255, .05);
        border:
            1px solid
            rgba(120, 140, 255, .12);
    }

    .footer {
        text-align: center;
        padding: 34px;
        margin-top: 35px;
        border-radius: 25px;
        background:
            rgba(120, 140, 255, .05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()
items = data["decisions"]
today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>🤔↔️ DAY 307 / 365</div>
        <h1>今日、何に迷った？</h1>
        <p>
            正解を探すのではなく、
            自分がどう迷い、
            どう決めたのかを残す。
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
    tab_add,
    tab_box,
    tab_decide,
    tab_review,
    tab_analysis,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🏠 ホーム",
        "➕ 迷いを記録",
        "🤔 迷いBOX",
        "✅ 決めた！",
        "🔎 答え合わせ",
        "📊 意思決定分析",
        "📚 迷い図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    thinking = [
        item
        for item in items
        if item.get("status")
        == STATUS_THINKING
    ]

    decided = [
        item
        for item in items
        if item.get("status")
        in [
            STATUS_DECIDED,
            STATUS_REVIEWED,
        ]
    ]

    reviewed = [
        item
        for item in items
        if item.get("status")
        == STATUS_REVIEWED
    ]

    satisfactions = [
        int(
            item.get(
                "satisfaction",
                0,
            )
        )
        for item in reviewed
        if item.get(
            "satisfaction"
        )
        is not None
    ]

    avg_satisfaction = (
        sum(satisfactions)
        / len(satisfactions)
        if satisfactions
        else None
    )

    st.subheader(
        "🧭 今の意思決定"
    )

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "🤔 迷い中",
        f"{len(thinking)}件",
    )

    c2.metric(
        "✅ 決めた",
        f"{len(decided)}件",
    )

    c3.metric(
        "🔎 振り返った",
        f"{len(reviewed)}件",
    )

    c4.metric(
        "⭐ 平均満足度",
        (
            f"{avg_satisfaction:.1f} / 5"
            if avg_satisfaction
            is not None
            else "-"
        ),
    )

    # DEADLINES
    due_items = []

    for item in thinking:
        days = deadline_days(
            item
        )

        if (
            days is not None
            and days <= 3
        ):
            due_items.append(
                (
                    days,
                    item,
                )
            )

    if due_items:
        st.divider()

        st.subheader(
            "⏰ そろそろ決める？"
        )

        due_items.sort(
            key=lambda x: x[0]
        )

        for days, item in (
            due_items[:5]
        ):
            with st.container(
                border=True
            ):
                st.write(
                    f"**{item.get('category')} "
                    f"{item.get('question')}**"
                )

                if days < 0:
                    st.warning(
                        f"期限から"
                        f"{abs(days)}日経過"
                    )
                elif days == 0:
                    st.warning(
                        "今日が決断期限"
                    )
                else:
                    st.caption(
                        f"あと{days}日"
                    )

    # RECENT
    if items:
        st.divider()

        st.subheader(
            "📝 最近の迷い"
        )

        recent = sorted(
            items,
            key=lambda x: x.get(
                "created_at",
                "",
            ),
            reverse=True,
        )

        for item in recent[:5]:
            a = int(
                item.get(
                    "a_percent",
                    50,
                )
            )

            b = 100 - a

            st.markdown(
                f"""
                <div class="decision-card">
                    <b>
                    {item.get("category")}
                    {item.get("question")}
                    </b>
                    <br><br>
                    A：{item.get("option_a")}
                    &nbsp; {a}%
                    <br>
                    B：{item.get("option_b")}
                    &nbsp; {b}%
                    <br><br>
                    迷い度：
                    {item.get("confusion_level")} / 100
                    <br>
                    {item.get("status")}
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# ADD
# =========================================================

with tab_add:

    st.subheader(
        "➕ 今の迷いを残す"
    )

    st.caption(
        "決める前だからこそ残せる"
        "気持ちがあります。"
    )

    with st.form(
        "add_decision_form",
        clear_on_submit=True,
    ):
        question = st.text_input(
            "🤔 何に迷ってる？",
            placeholder=(
                "例：今日は勉強する？"
                "それとも休む？"
            ),
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        c1, c2 = st.columns(2)

        with c1:
            option_a = (
                st.text_input(
                    "🅰️ 選択肢A",
                    placeholder=(
                        "勉強する"
                    ),
                )
            )

        with c2:
            option_b = (
                st.text_input(
                    "🅱️ 選択肢B",
                    placeholder=(
                        "休む"
                    ),
                )
            )

        a_percent = st.slider(
            "今はどっち寄り？",
            0,
            100,
            50,
            step=5,
            help=(
                "数値はAへの気持ち。"
                "Bは自動で100から"
                "差し引きます。"
            ),
        )

        b_percent = (
            100 - a_percent
        )

        st.write(
            f"**A {a_percent}%** "
            f"{percent_bar(a_percent)} "
            f"**B {b_percent}%**"
        )

        confusion = st.slider(
            "😵 迷い度",
            0,
            100,
            50,
            step=5,
        )

        reasons = st.multiselect(
            "なぜ迷ってる？",
            REASONS,
        )

        memo = st.text_area(
            "今の気持ち・メモ",
            placeholder=(
                "迷っている理由を"
                "自由に残しておこう"
            ),
        )

        unknown_deadline = (
            st.checkbox(
                "決断期限は未定"
            )
        )

        deadline = st.date_input(
            "いつまでに決める？",
            value=today,
            min_value=today,
            disabled=(
                unknown_deadline
            ),
        )

        submitted = (
            st.form_submit_button(
                "🤔 迷いBOXに入れる",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not question.strip():
                st.warning(
                    "何に迷っているか"
                    "入力してね。"
                )

            elif (
                not option_a.strip()
                or not option_b.strip()
            ):
                st.warning(
                    "AとBの両方を"
                    "入力してね。"
                )

            else:
                add_decision(
                    data=data,
                    question=(
                        question.strip()
                    ),
                    category=category,
                    option_a=(
                        option_a.strip()
                    ),
                    option_b=(
                        option_b.strip()
                    ),
                    a_percent=(
                        a_percent
                    ),
                    confusion_level=(
                        confusion
                    ),
                    reasons=reasons,
                    memo=memo.strip(),
                    deadline=(
                        None
                        if unknown_deadline
                        else deadline
                    ),
                )

                st.rerun()


# =========================================================
# THINKING BOX
# =========================================================

with tab_box:

    st.subheader(
        "🤔 迷いBOX"
    )

    thinking = [
        item
        for item in items
        if item.get("status")
        == STATUS_THINKING
    ]

    if not thinking:
        st.success(
            "今、記録されている"
            "迷いはありません。"
        )

    else:
        sort_type = st.selectbox(
            "並び順",
            [
                "迷い度が高い順",
                "期限が近い順",
                "古い順",
                "新しい順",
            ],
        )

        if (
            sort_type
            == "迷い度が高い順"
        ):
            thinking.sort(
                key=lambda x: int(
                    x.get(
                        "confusion_level",
                        0,
                    )
                ),
                reverse=True,
            )

        elif (
            sort_type
            == "期限が近い順"
        ):
            thinking.sort(
                key=lambda x: (
                    parse_date(
                        x.get(
                            "deadline"
                        )
                    )
                    or date.max
                )
            )

        elif sort_type == "古い順":
            thinking.sort(
                key=lambda x: x.get(
                    "created_at",
                    "",
                )
            )

        else:
            thinking.sort(
                key=lambda x: x.get(
                    "created_at",
                    "",
                ),
                reverse=True,
            )

        for item in thinking:
            a = int(
                item.get(
                    "a_percent",
                    50,
                )
            )

            b = 100 - a

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### "
                    f"{item.get('category')} "
                    f"{item.get('question')}"
                )

                c1, c2, c3 = (
                    st.columns(3)
                )

                c1.metric(
                    "A",
                    f"{a}%",
                )

                c2.metric(
                    "B",
                    f"{b}%",
                )

                c3.metric(
                    "迷い度",
                    (
                        f"{item.get('confusion_level')}"
                        " / 100"
                    ),
                )

                st.write(
                    f"🅰️ **{item.get('option_a')}**"
                )

                st.write(
                    f"🅱️ **{item.get('option_b')}**"
                )

                st.caption(
                    f"A {a}% / B {b}%"
                )

                if item.get(
                    "reasons"
                ):
                    st.write(
                        "**迷っている理由**"
                    )

                    st.write(
                        " / ".join(
                            item.get(
                                "reasons",
                                [],
                            )
                        )
                    )

                if item.get("memo"):
                    st.info(
                        item.get("memo")
                    )

                days = deadline_days(
                    item
                )

                if days is None:
                    st.caption(
                        "📅 決断期限：未定"
                    )
                elif days > 0:
                    st.caption(
                        f"📅 あと{days}日"
                    )
                elif days == 0:
                    st.warning(
                        "📅 今日が決断期限"
                    )
                else:
                    st.warning(
                        f"📅 期限から"
                        f"{abs(days)}日経過"
                    )


# =========================================================
# DECIDE
# =========================================================

with tab_decide:

    st.subheader(
        "✅ 決めた！"
    )

    thinking = [
        item
        for item in items
        if item.get("status")
        == STATUS_THINKING
    ]

    if not thinking:
        st.info(
            "決断待ちの迷いは"
            "ありません。"
        )

    else:
        options = {
            decision_label(item):
            item.get("id")
            for item in thinking
        }

        selected_label = (
            st.selectbox(
                "どの迷いを決めた？",
                list(
                    options.keys()
                ),
            )
        )

        selected_id = options[
            selected_label
        ]

        item = get_decision(
            data,
            selected_id,
        )

        a = int(
            item.get(
                "a_percent",
                50,
            )
        )

        b = 100 - a

        st.markdown(
            f"### 🤔 "
            f"{item.get('question')}"
        )

        st.write(
            f"当時："
            f"**A {a}% / B {b}%**"
        )

        st.caption(
            f"A：{item.get('option_a')} "
            f"｜ B：{item.get('option_b')}"
        )

        choice_display = [
            f"A：{item.get('option_a')}",
            f"B：{item.get('option_b')}",
            "どちらも選ばなかった",
            "別の選択肢になった",
        ]

        with st.form(
            "decide_form"
        ):
            choice_ui = st.radio(
                "どれを選んだ？",
                choice_display,
            )

            other_text = (
                st.text_input(
                    "別の選択肢",
                    placeholder=(
                        "別の選択肢を"
                        "選んだ場合だけ入力"
                    ),
                )
            )

            method = st.selectbox(
                "どう決めた？",
                DECISION_METHODS,
            )

            factor = st.text_area(
                "決め手は？",
                placeholder=(
                    "例：30分だけなら"
                    "できそうだったから"
                ),
            )

            submitted = (
                st.form_submit_button(
                    "✅ 決断を保存",
                    type="primary",
                    use_container_width=True,
                )
            )

            if submitted:
                if (
                    choice_ui
                    == choice_display[0]
                ):
                    choice = "A"

                elif (
                    choice_ui
                    == choice_display[1]
                ):
                    choice = "B"

                elif (
                    choice_ui
                    == choice_display[2]
                ):
                    choice = "NONE"

                else:
                    choice = "OTHER"

                if (
                    choice == "OTHER"
                    and not other_text.strip()
                ):
                    st.warning(
                        "別の選択肢を"
                        "入力してね。"
                    )

                else:
                    decide_item(
                        data=data,
                        decision_id=(
                            selected_id
                        ),
                        choice=choice,
                        choice_text=(
                            other_text.strip()
                        ),
                        method=method,
                        factor=(
                            factor.strip()
                        ),
                    )

                    st.rerun()


# =========================================================
# REVIEW
# =========================================================

with tab_review:

    st.subheader(
        "🔎 あの選択、どうだった？"
    )

    reviewable = [
        item
        for item in items
        if item.get("status")
        == STATUS_DECIDED
    ]

    if not reviewable:
        st.info(
            "振り返り待ちの"
            "決断はありません。"
        )

    else:
        options = {
            decision_label(item):
            item.get("id")
            for item in reviewable
        }

        selected_label = (
            st.selectbox(
                "どの決断を振り返る？",
                list(
                    options.keys()
                ),
                key="review_select",
            )
        )

        selected_id = options[
            selected_label
        ]

        item = get_decision(
            data,
            selected_id,
        )

        st.markdown(
            f"### {item.get('question')}"
        )

        st.success(
            "選んだもの："
            + get_choice_label(
                item
            )
        )

        if item.get(
            "deciding_factor"
        ):
            st.caption(
                "決め手："
                + item.get(
                    "deciding_factor"
                )
            )

        with st.form(
            "review_form"
        ):
            result = st.radio(
                "結果はどうだった？",
                REVIEW_RESULTS,
            )

            satisfaction = (
                st.slider(
                    "満足度",
                    1,
                    5,
                    4,
                )
            )

            st.write(
                star_text(
                    satisfaction
                )
            )

            note = st.text_area(
                "今振り返ってどう思う？",
                placeholder=(
                    "例：やってみたら"
                    "意外と集中できた"
                ),
            )

            submitted = (
                st.form_submit_button(
                    "🔎 振り返りを保存",
                    type="primary",
                    use_container_width=True,
                )
            )

            if submitted:
                review_item(
                    data=data,
                    decision_id=(
                        selected_id
                    ),
                    result=result,
                    satisfaction=(
                        satisfaction
                    ),
                    note=note.strip(),
                )

                st.rerun()

    # REVIEWED TIMELINES
    reviewed = [
        item
        for item in items
        if item.get("status")
        == STATUS_REVIEWED
    ]

    if reviewed:
        st.divider()

        st.subheader(
            "🤔 → ✅ → 🔎"
        )

        recent_reviewed = sorted(
            reviewed,
            key=lambda x: x.get(
                "reviewed_at",
                "",
            ),
            reverse=True,
        )

        for item in (
            recent_reviewed[:5]
        ):
            created = parse_datetime(
                item.get(
                    "created_at"
                )
            )

            decided_at = (
                parse_datetime(
                    item.get(
                        "decided_at"
                    )
                )
            )

            reviewed_at = (
                parse_datetime(
                    item.get(
                        "reviewed_at"
                    )
                )
            )

            st.markdown(
                f"""
                <div class="timeline-card">
                    <b>
                    🤔 {created.strftime("%Y/%m/%d") if created else "-"}
                    </b>
                    <br>
                    {item.get("question")}
                    <br>
                    A {item.get("a_percent")}%
                    /
                    B {100 - int(item.get("a_percent", 50))}%
                    <br><br>

                    ↓
                    <br><br>

                    <b>
                    ✅ {decided_at.strftime("%Y/%m/%d") if decided_at else "-"}
                    </b>
                    <br>
                    {get_choice_label(item)}
                    <br>
                    {item.get("decision_method", "")}
                    <br><br>

                    ↓
                    <br><br>

                    <b>
                    🔎 {reviewed_at.strftime("%Y/%m/%d") if reviewed_at else "-"}
                    </b>
                    <br>
                    {item.get("review_result", "")}
                    <br>
                    {star_text(item.get("satisfaction"))}
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 自分はどう迷い、"
        "どう決めている？"
    )

    decided_items = [
        item
        for item in items
        if item.get("status")
        in [
            STATUS_DECIDED,
            STATUS_REVIEWED,
        ]
    ]

    reviewed_items = [
        item
        for item in items
        if item.get("status")
        == STATUS_REVIEWED
    ]

    if not items:
        st.info(
            "記録が増えると、"
            "ここに意思決定の傾向が"
            "見えてきます。"
        )

    else:
        confusion_values = [
            int(
                item.get(
                    "confusion_level",
                    0,
                )
            )
            for item in items
        ]

        decision_day_values = [
            decision_days(item)
            for item in decided_items
        ]

        decision_day_values = [
            d
            for d
            in decision_day_values
            if d is not None
        ]

        satisfaction_values = [
            int(
                item.get(
                    "satisfaction",
                    0,
                )
            )
            for item
            in reviewed_items
            if item.get(
                "satisfaction"
            )
            is not None
        ]

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "🤔 迷い",
            f"{len(items)}件",
        )

        c2.metric(
            "😵 平均迷い度",
            (
                f"{sum(confusion_values) / len(confusion_values):.1f}"
                if confusion_values
                else "-"
            ),
        )

        c3.metric(
            "⏱️ 平均決断日数",
            (
                f"{sum(decision_day_values) / len(decision_day_values):.1f}日"
                if decision_day_values
                else "-"
            ),
        )

        c4.metric(
            "⭐ 平均満足度",
            (
                f"{sum(satisfaction_values) / len(satisfaction_values):.1f}"
                if satisfaction_values
                else "-"
            ),
        )

        # CATEGORY
        st.divider()

        st.markdown(
            "### 🧭 何に迷っている？"
        )

        category_rows = []

        for category in CATEGORIES:
            category_items = [
                item
                for item in items
                if item.get(
                    "category"
                ) == category
            ]

            if not category_items:
                continue

            confusion_list = [
                int(
                    item.get(
                        "confusion_level",
                        0,
                    )
                )
                for item
                in category_items
            ]

            day_list = [
                decision_days(item)
                for item
                in category_items
            ]

            day_list = [
                d
                for d in day_list
                if d is not None
            ]

            sat_list = [
                int(
                    item.get(
                        "satisfaction"
                    )
                )
                for item
                in category_items
                if item.get(
                    "satisfaction"
                )
                is not None
            ]

            category_rows.append(
                {
                    "カテゴリー":
                        category,
                    "件数":
                        len(
                            category_items
                        ),
                    "平均迷い度":
                        round(
                            sum(
                                confusion_list
                            )
                            / len(
                                confusion_list
                            ),
                            1,
                        ),
                    "平均決断日数":
                        (
                            round(
                                sum(day_list)
                                / len(day_list),
                                1,
                            )
                            if day_list
                            else None
                        ),
                    "平均満足度":
                        (
                            round(
                                sum(sat_list)
                                / len(sat_list),
                                1,
                            )
                            if sat_list
                            else None
                        ),
                }
            )

        category_df = pd.DataFrame(
            category_rows
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        if not category_df.empty:
            category_chart = (
                category_df[
                    [
                        "カテゴリー",
                        "件数",
                    ]
                ]
                .set_index(
                    "カテゴリー"
                )
            )

            st.bar_chart(
                category_chart
            )

        # REASONS
        st.divider()

        st.markdown(
            "### 🧠 なぜ迷っている？"
        )

        reason_counter = Counter()

        for item in items:
            reason_counter.update(
                item.get(
                    "reasons",
                    [],
                )
            )

        if reason_counter:
            reason_df = (
                pd.DataFrame(
                    [
                        {
                            "理由": reason,
                            "回数": count,
                        }
                        for reason, count
                        in reason_counter
                        .most_common()
                    ]
                )
                .set_index("理由")
            )

            st.bar_chart(
                reason_df
            )

            st.dataframe(
                reason_df,
                use_container_width=True,
            )

        else:
            st.caption(
                "理由の記録がまだありません。"
            )

        # METHOD SATISFACTION
        st.divider()

        st.markdown(
            "### ⚡ どう決めたとき"
            "満足していた？"
        )

        method_data = defaultdict(
            list
        )

        for item in reviewed_items:
            method = item.get(
                "decision_method"
            )

            satisfaction = (
                item.get(
                    "satisfaction"
                )
            )

            if (
                method
                and satisfaction
                is not None
            ):
                method_data[
                    method
                ].append(
                    int(
                        satisfaction
                    )
                )

        method_rows = []

        for method, values in (
            method_data.items()
        ):
            method_rows.append(
                {
                    "決め方": method,
                    "件数": len(values),
                    "平均満足度":
                        round(
                            sum(values)
                            / len(values),
                            2,
                        ),
                }
            )

        if method_rows:
            method_df = (
                pd.DataFrame(
                    method_rows
                )
                .sort_values(
                    "平均満足度",
                    ascending=False,
                )
            )

            st.dataframe(
                method_df,
                hide_index=True,
                use_container_width=True,
            )

            st.caption(
                "※これまで記録した"
                "選択の結果です。"
                "件数が少ない場合は"
                "傾向とは限りません。"
            )

        else:
            st.caption(
                "振り返りが増えると"
                "表示されます。"
            )

        # INITIAL VS FINAL
        st.divider()

        st.markdown(
            "### 🔄 最初の気持ちと"
            "最終決定"
        )

        ab_decisions = [
            item
            for item in decided_items
            if item.get("choice")
            in ["A", "B"]
        ]

        if ab_decisions:
            leader_decisions = [
                item
                for item
                in ab_decisions
                if initial_leader(item)
                != "TIE"
            ]

            followed = sum(
                1
                for item
                in leader_decisions
                if not changed_mind(
                    item
                )
            )

            changed = sum(
                1
                for item
                in leader_decisions
                if changed_mind(
                    item
                )
            )

            c1, c2 = st.columns(2)

            c1.metric(
                "➡️ 最初に優勢だった方",
                f"{followed}件",
            )

            c2.metric(
                "🔄 途中で変わった",
                f"{changed}件",
            )

            if leader_decisions:
                rate = (
                    followed
                    / len(
                        leader_decisions
                    )
                    * 100
                )

                st.caption(
                    "最初に優勢だった"
                    "選択肢を最終的に"
                    f"選んだ割合："
                    f"{rate:.1f}%"
                )

        # HARD BUT SATISFIED
        st.divider()

        st.markdown(
            "### 😲 かなり迷った。"
            "でも満足した"
        )

        hard_good = [
            item
            for item
            in reviewed_items
            if (
                int(
                    item.get(
                        "confusion_level",
                        0,
                    )
                ) >= 70
                and int(
                    item.get(
                        "satisfaction",
                        0,
                    )
                ) >= 4
            )
        ]

        if not hard_good:
            st.caption(
                "まだ該当する記録は"
                "ありません。"
            )

        for item in hard_good[:10]:
            with st.container(
                border=True
            ):
                st.write(
                    f"**{item.get('question')}**"
                )

                st.write(
                    f"😵 迷い度 "
                    f"{item.get('confusion_level')}"
                    f" → "
                    f"{star_text(item.get('satisfaction'))}"
                )

                st.caption(
                    "選択："
                    + get_choice_label(
                        item
                    )
                )

        # RANDOM
        st.divider()

        st.markdown(
            "### 🎲 あの迷い、覚えてる？"
        )

        if not reviewed_items:
            st.caption(
                "振り返り済みの記録が"
                "ここに現れます。"
            )

        else:
            reviewed_ids = [
                item.get("id")
                for item
                in reviewed_items
            ]

            random_id = (
                st.session_state.get(
                    "random_decision_id"
                )
            )

            if (
                random_id
                not in reviewed_ids
            ):
                random_id = (
                    random.choice(
                        reviewed_ids
                    )
                )

                st.session_state[
                    "random_decision_id"
                ] = random_id

            random_item = (
                get_decision(
                    data,
                    random_id,
                )
            )

            with st.container(
                border=True
            ):
                st.markdown(
                    f"### 🤔 "
                    f"{random_item.get('question')}"
                )

                st.write(
                    f"A "
                    f"{random_item.get('a_percent')}%"
                    f" / B "
                    f"{100 - int(random_item.get('a_percent', 50))}%"
                )

                st.write(
                    "**最終決定**"
                )

                st.write(
                    get_choice_label(
                        random_item
                    )
                )

                st.write(
                    "**結果**"
                )

                st.write(
                    random_item.get(
                        "review_result"
                    )
                )

                st.write(
                    star_text(
                        random_item.get(
                            "satisfaction"
                        )
                    )
                )

                if random_item.get(
                    "review_note"
                ):
                    st.info(
                        random_item.get(
                            "review_note"
                        )
                    )

            if st.button(
                "🎲 別の迷いを見る",
                use_container_width=True,
            ):
                alternatives = [
                    item_id
                    for item_id
                    in reviewed_ids
                    if item_id
                    != random_id
                ]

                if alternatives:
                    st.session_state[
                        "random_decision_id"
                    ] = random.choice(
                        alternatives
                    )

                st.rerun()


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 迷い図鑑"
    )

    search = st.text_input(
        "🔎 検索",
        key="library_search",
    )

    c1, c2 = st.columns(2)

    with c1:
        category_filter = (
            st.selectbox(
                "カテゴリー",
                ["すべて"]
                + CATEGORIES,
                key="library_category",
            )
        )

    with c2:
        status_filter = (
            st.selectbox(
                "状態",
                [
                    "すべて",
                    STATUS_THINKING,
                    STATUS_DECIDED,
                    STATUS_REVIEWED,
                ],
                key="library_status",
            )
        )

    min_confusion = st.slider(
        "最低迷い度",
        0,
        100,
        0,
        step=10,
    )

    rows = []

    for item in items:
        if (
            category_filter
            != "すべて"
            and item.get(
                "category"
            )
            != category_filter
        ):
            continue

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
            int(
                item.get(
                    "confusion_level",
                    0,
                )
            )
            < min_confusion
        ):
            continue

        searchable = " ".join(
            [
                item.get(
                    "question",
                    "",
                ),
                item.get(
                    "option_a",
                    "",
                ),
                item.get(
                    "option_b",
                    "",
                ),
                item.get(
                    "memo",
                    "",
                ),
                item.get(
                    "deciding_factor",
                    "",
                ),
                item.get(
                    "review_note",
                    "",
                ),
            ]
        ).lower()

        if (
            search.strip()
            and search.strip().lower()
            not in searchable
        ):
            continue

        rows.append(
            {
                "迷い":
                    item.get(
                        "question"
                    ),
                "カテゴリー":
                    item.get(
                        "category"
                    ),
                "迷い度":
                    item.get(
                        "confusion_level"
                    ),
                "初期":
                    (
                        f"A {item.get('a_percent')} / "
                        f"B {100 - int(item.get('a_percent', 50))}"
                    ),
                "決断":
                    get_choice_label(
                        item
                    ),
                "満足度":
                    (
                        item.get(
                            "satisfaction"
                        )
                        if item.get(
                            "satisfaction"
                        )
                        is not None
                        else "-"
                    ),
                "状態":
                    item.get(
                        "status"
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
        "🛠️ 記録を管理"
    )

    if not items:
        st.info(
            "まだ記録がありません。"
        )

    else:
        options = {
            decision_label(item):
            item.get("id")
            for item in items
        }

        selected_label = (
            st.selectbox(
                "編集する記録",
                list(
                    options.keys()
                ),
                key="manage_select",
            )
        )

        selected_id = options[
            selected_label
        ]

        item = get_decision(
            data,
            selected_id,
        )

        edit_question = (
            st.text_input(
                "迷い",
                value=item.get(
                    "question",
                    "",
                ),
            )
        )

        old_category = item.get(
            "category",
            "📦 その他",
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
                index=(
                    category_index
                ),
                key=(
                    "manage_category"
                ),
            )
        )

        edit_a = st.text_input(
            "選択肢A",
            value=item.get(
                "option_a",
                "",
            ),
        )

        edit_b = st.text_input(
            "選択肢B",
            value=item.get(
                "option_b",
                "",
            ),
        )

        edit_a_percent = (
            st.slider(
                "最初のAへの気持ち",
                0,
                100,
                int(
                    item.get(
                        "a_percent",
                        50,
                    )
                ),
                step=5,
            )
        )

        edit_confusion = (
            st.slider(
                "迷い度",
                0,
                100,
                int(
                    item.get(
                        "confusion_level",
                        50,
                    )
                ),
                step=5,
            )
        )

        edit_reasons = (
            st.multiselect(
                "迷った理由",
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

        edit_memo = (
            st.text_area(
                "メモ",
                value=item.get(
                    "memo",
                    "",
                ),
            )
        )

        deadline_unknown = (
            st.checkbox(
                "決断期限は未定",
                value=(
                    item.get(
                        "deadline"
                    )
                    is None
                ),
            )
        )

        current_deadline = (
            parse_date(
                item.get(
                    "deadline"
                )
            )
            or today
        )

        edit_deadline = (
            st.date_input(
                "決断期限",
                value=(
                    current_deadline
                ),
                disabled=(
                    deadline_unknown
                ),
                key=(
                    "manage_deadline"
                ),
            )
        )

        if st.button(
            "💾 基本情報を保存",
            type="primary",
            use_container_width=True,
        ):
            if (
                not edit_question.strip()
                or not edit_a.strip()
                or not edit_b.strip()
            ):
                st.warning(
                    "迷い・A・Bを"
                    "入力してね。"
                )

            else:
                item["question"] = (
                    edit_question.strip()
                )
                item["category"] = (
                    edit_category
                )
                item["option_a"] = (
                    edit_a.strip()
                )
                item["option_b"] = (
                    edit_b.strip()
                )
                item[
                    "a_percent"
                ] = int(
                    edit_a_percent
                )
                item[
                    "confusion_level"
                ] = int(
                    edit_confusion
                )
                item["reasons"] = (
                    edit_reasons
                )
                item["memo"] = (
                    edit_memo.strip()
                )
                item["deadline"] = (
                    None
                    if deadline_unknown
                    else str(
                        edit_deadline
                    )
                )
                item["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # DECISION EDIT
        if item.get("status") in [
            STATUS_DECIDED,
            STATUS_REVIEWED,
        ]:
            st.divider()

            st.subheader(
                "✅ 決断内容"
            )

            st.write(
                "**選んだもの：** "
                + get_choice_label(
                    item
                )
            )

            current_method = (
                item.get(
                    "decision_method"
                )
            )

            method_index = (
                DECISION_METHODS.index(
                    current_method
                )
                if current_method
                in DECISION_METHODS
                else 0
            )

            edit_method = (
                st.selectbox(
                    "決め方",
                    DECISION_METHODS,
                    index=(
                        method_index
                    ),
                    key=(
                        "manage_method"
                    ),
                )
            )

            edit_factor = (
                st.text_area(
                    "決め手",
                    value=item.get(
                        "deciding_factor",
                        "",
                    ),
                    key=(
                        "manage_factor"
                    ),
                )
            )

            if st.button(
                "💾 決断情報を保存",
                use_container_width=True,
            ):
                item[
                    "decision_method"
                ] = edit_method

                item[
                    "deciding_factor"
                ] = (
                    edit_factor.strip()
                )

                item["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # REVIEW EDIT
        if (
            item.get("status")
            == STATUS_REVIEWED
        ):
            st.divider()

            st.subheader(
                "🔎 振り返り"
            )

            current_result = (
                item.get(
                    "review_result"
                )
            )

            result_index = (
                REVIEW_RESULTS.index(
                    current_result
                )
                if current_result
                in REVIEW_RESULTS
                else 0
            )

            edit_result = (
                st.selectbox(
                    "結果",
                    REVIEW_RESULTS,
                    index=(
                        result_index
                    ),
                    key=(
                        "manage_result"
                    ),
                )
            )

            edit_satisfaction = (
                st.slider(
                    "満足度",
                    1,
                    5,
                    int(
                        item.get(
                            "satisfaction",
                            3,
                        )
                    ),
                    key=(
                        "manage_sat"
                    ),
                )
            )

            edit_review_note = (
                st.text_area(
                    "振り返り",
                    value=item.get(
                        "review_note",
                        "",
                    ),
                    key=(
                        "manage_review_note"
                    ),
                )
            )

            if st.button(
                "💾 振り返りを保存",
                use_container_width=True,
            ):
                item[
                    "review_result"
                ] = edit_result

                item[
                    "satisfaction"
                ] = int(
                    edit_satisfaction
                )

                item[
                    "review_note"
                ] = (
                    edit_review_note.strip()
                )

                item["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # DELETE
        st.divider()

        delete_confirm = (
            st.checkbox(
                "この記録を"
                "完全に削除する",
                key=(
                    "delete_confirm_"
                    + selected_id
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
                + selected_id
            ),
            use_container_width=True,
        ):
            delete_decision(
                data,
                selected_id,
            )

            st.rerun()

    # BACKUP
    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    backup_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=backup_text,
        file_name=(
            f"decision_diary_{today}.json"
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
            <b>
                迷った時間も、
                決めた理由も、
                選ばなかった道も。
            </b>
        </p>

        <p>
            そのときの自分にとっては、
            全部ちゃんと意味があった。
        </p>

        <p>
            正解だったかを裁くためではなく、
            <br>
            <b>
                自分がどう考え、
                どう選んできたのかを知るために。
            </b>
        </p>

        <p>
            今日の迷いを、
            残しておこう。🤔
        </p>

        <br>

        <b>
            DAY 307 / 365 — COMPLETE 🔥
        </b>
    </div>
    """,
    unsafe_allow_html=True,
)
