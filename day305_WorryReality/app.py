import json
import os
import random
import uuid
from collections import defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="あの日の心配、どうなった？",
    page_icon="🌤️",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "worries.json")

STATUS_WAITING = "📦 結果待ち"
STATUS_RESOLVED = "🌤️ 答え合わせ済み"

CATEGORIES = [
    "💼 仕事",
    "💰 お金",
    "🏠 生活",
    "👨‍👩‍👧 家族",
    "🤝 人間関係",
    "📚 勉強",
    "🚗 移動",
    "💻 開発",
    "🌱 将来",
    "📦 その他",
]

WORST_RESULTS = [
    "○ 起きた",
    "△ 一部起きた",
    "× 起きなかった",
]


# =========================================================
# HELPERS
# =========================================================

def new_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(timespec="seconds")


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


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def format_date(value):
    d = parse_date(value)

    if not d:
        return "未定"

    return d.strftime("%Y/%m/%d")


def worry_bar(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        value = 0

    value = max(0, min(value, 100))

    filled = round(value / 10)
    empty = 10 - filled

    return "█" * filled + "░" * empty


def difference_text(worry_level, actual_severity):
    if actual_severity is None:
        return "-"

    diff = int(actual_severity) - int(worry_level)

    if diff > 0:
        return f"+{diff}"

    return str(diff)


def worry_label(worry):
    return (
        f"{worry.get('title', '')}"
        f" [{worry.get('id', '')[:6]}]"
    )


def days_until_check(worry):
    check_date = parse_date(
        worry.get("check_date")
    )

    if not check_date:
        return None

    return (check_date - date.today()).days


def days_held(worry):
    created = parse_datetime(
        worry.get("created_at")
    )

    if not created:
        return None

    resolved = parse_datetime(
        worry.get("resolved_at")
    )

    end_date = (
        resolved.date()
        if resolved
        else date.today()
    )

    return max(
        0,
        (end_date - created.date()).days,
    )


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "worries": []
    }


def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)

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
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
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

        if not isinstance(data, dict):
            data = default_data()

        data.setdefault("worries", [])

        for worry in data["worries"]:
            worry.setdefault("id", new_id())
            worry.setdefault("title", "")
            worry.setdefault(
                "category",
                "📦 その他",
            )
            worry.setdefault(
                "worry_level",
                50,
            )
            worry.setdefault(
                "prediction",
                "",
            )
            worry.setdefault(
                "worst_case",
                "",
            )
            worry.setdefault(
                "worst_probability",
                50,
            )
            worry.setdefault(
                "check_date",
                None,
            )
            worry.setdefault(
                "status",
                STATUS_WAITING,
            )
            worry.setdefault(
                "actual_result",
                "",
            )
            worry.setdefault(
                "actual_severity",
                None,
            )
            worry.setdefault(
                "worst_result",
                None,
            )
            worry.setdefault(
                "reflection",
                "",
            )
            worry.setdefault(
                "created_at",
                now_text(),
            )
            worry.setdefault(
                "resolved_at",
                None,
            )
            worry.setdefault(
                "updated_at",
                worry.get(
                    "created_at",
                    now_text(),
                ),
            )

        return data

    except (OSError, ValueError):
        data = default_data()
        save_data(data)
        return data


# =========================================================
# GETTERS
# =========================================================

def get_worry(data, worry_id):
    return next(
        (
            worry
            for worry in data["worries"]
            if worry.get("id") == worry_id
        ),
        None,
    )


def waiting_worries(data):
    return [
        worry
        for worry in data["worries"]
        if worry.get("status")
        == STATUS_WAITING
    ]


def resolved_worries(data):
    return [
        worry
        for worry in data["worries"]
        if worry.get("status")
        == STATUS_RESOLVED
    ]


# =========================================================
# CRUD
# =========================================================

def add_worry(
    data,
    title,
    category,
    worry_level,
    prediction,
    worst_case,
    worst_probability,
    check_date,
):
    worry = {
        "id": new_id(),
        "title": title,
        "category": category,
        "worry_level": int(worry_level),
        "prediction": prediction,
        "worst_case": worst_case,
        "worst_probability": int(
            worst_probability
        ),
        "check_date": (
            str(check_date)
            if check_date
            else None
        ),
        "status": STATUS_WAITING,
        "actual_result": "",
        "actual_severity": None,
        "worst_result": None,
        "reflection": "",
        "created_at": now_text(),
        "resolved_at": None,
        "updated_at": now_text(),
    }

    data["worries"].append(worry)
    save_data(data)


def resolve_worry(
    data,
    worry_id,
    actual_result,
    actual_severity,
    worst_result,
    reflection,
):
    worry = get_worry(
        data,
        worry_id,
    )

    if not worry:
        return

    worry["status"] = STATUS_RESOLVED
    worry["actual_result"] = actual_result
    worry["actual_severity"] = int(
        actual_severity
    )
    worry["worst_result"] = worst_result
    worry["reflection"] = reflection
    worry["resolved_at"] = now_text()
    worry["updated_at"] = now_text()

    save_data(data)


def delete_worry(
    data,
    worry_id,
):
    data["worries"] = [
        worry
        for worry in data["worries"]
        if worry.get("id") != worry_id
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
                rgba(100, 150, 255, .12),
                rgba(255, 210, 100, .11),
                rgba(255, 255, 255, .02)
            );
    }

    .compare-card {
        padding: 28px;
        text-align: center;
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                rgba(110, 150, 255, .10),
                rgba(255, 220, 120, .10)
            );
        margin: 15px 0;
    }

    .worry-card {
        padding: 18px;
        border-radius: 20px;
        border: 1px solid
            rgba(130, 150, 180, .18);
        margin-bottom: 12px;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background:
            rgba(100, 160, 255, .05);
        border: 1px solid
            rgba(100, 160, 255, .12);
    }

    .footer {
        text-align: center;
        padding: 32px;
        margin-top: 35px;
        border-radius: 25px;
        background:
            rgba(100, 160, 255, .05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()
worries = data["worries"]
today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>😟➡️🌤️ DAY 305 / 365</div>
        <h1>あの日の心配、どうなった？</h1>
        <p>
            あのとき想像した未来と、
            実際にやってきた未来を比べてみる。
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
    tab_answers,
    tab_analysis,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🏠 ホーム",
        "➕ 心配を記録",
        "📦 心配BOX",
        "🌤️ 答え合わせ",
        "📊 分析",
        "📚 心配図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    waiting = waiting_worries(data)
    resolved = resolved_worries(data)

    worry_levels = [
        int(w.get("worry_level", 0))
        for w in resolved
    ]

    actual_levels = [
        int(w.get("actual_severity", 0))
        for w in resolved
        if w.get("actual_severity") is not None
    ]

    avg_worry = (
        sum(worry_levels) / len(worry_levels)
        if worry_levels
        else 0
    )

    avg_actual = (
        sum(actual_levels) / len(actual_levels)
        if actual_levels
        else 0
    )

    st.subheader("📊 今の記録")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📦 結果待ち",
        f"{len(waiting)}件",
    )

    c2.metric(
        "🌤️ 答え合わせ済み",
        f"{len(resolved)}件",
    )

    c3.metric(
        "😟 平均心配度",
        (
            f"{avg_worry:.1f}"
            if resolved
            else "-"
        ),
    )

    c4.metric(
        "🌤️ 平均深刻度",
        (
            f"{avg_actual:.1f}"
            if actual_levels
            else "-"
        ),
    )

    # -----------------------------------------------------
    # DUE
    # -----------------------------------------------------

    due_worries = []

    for worry in waiting:
        check_date = parse_date(
            worry.get("check_date")
        )

        if (
            check_date
            and check_date <= today
        ):
            due_worries.append(worry)

    if due_worries:
        st.divider()

        st.subheader(
            "🌤️ そろそろ答え合わせしてみる？"
        )

        for worry in due_worries[:5]:
            with st.container(border=True):
                st.markdown(
                    f"### {worry.get('category')} "
                    f"{worry.get('title')}"
                )

                st.write(
                    f"😟 当時の心配度："
                    f"**{worry.get('worry_level')} / 100**"
                )

                st.caption(
                    f"確認予定日："
                    f"{format_date(worry.get('check_date'))}"
                )

    # -----------------------------------------------------
    # RECENT
    # -----------------------------------------------------

    if waiting:
        st.divider()

        st.subheader(
            "📦 最近の心配"
        )

        recent_waiting = sorted(
            waiting,
            key=lambda w: w.get(
                "created_at",
                "",
            ),
            reverse=True,
        )

        for worry in recent_waiting[:5]:
            level = int(
                worry.get(
                    "worry_level",
                    0,
                )
            )

            st.markdown(
                f"""
                <div class="worry-card">
                    <b>
                    {worry.get("category")}
                    {worry.get("title")}
                    </b>
                    <br><br>
                    😟 {worry_bar(level)}
                    &nbsp; {level}/100
                    <br>
                    <small>
                    確認予定：
                    {format_date(worry.get("check_date"))}
                    </small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------
    # SAFE MEMORIES
    # -----------------------------------------------------

    safe_memories = [
        w
        for w in resolved
        if (
            w.get("actual_severity")
            is not None
            and int(
                w.get("actual_severity")
            ) <= 30
        )
    ]

    if safe_memories:
        st.divider()

        st.subheader(
            "🌤️ 結局、大丈夫だった"
        )

        safe_sorted = sorted(
            safe_memories,
            key=lambda w: (
                int(w.get("worry_level", 0))
                - int(w.get("actual_severity", 0))
            ),
            reverse=True,
        )

        for worry in safe_sorted[:5]:
            st.write(
                f"**{worry.get('title')}**"
            )

            st.caption(
                f"😟 {worry.get('worry_level')} "
                f"→ 🌤️ {worry.get('actual_severity')} "
                f"｜差 "
                f"{difference_text(worry.get('worry_level'), worry.get('actual_severity'))}"
            )


# =========================================================
# ADD
# =========================================================

with tab_add:

    st.subheader(
        "➕ 今の心配を残す"
    )

    st.caption(
        "心配をなくすためではなく、"
        "今どう感じているかを記録します。"
    )

    with st.form(
        "add_worry",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "😟 今、何が心配？",
            placeholder=(
                "例：明日の仕事で"
                "ミスするかもしれない"
            ),
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        worry_level = st.slider(
            "心配度",
            0,
            100,
            70,
            step=5,
        )

        st.write(
            f"{worry_bar(worry_level)} "
            f"**{worry_level}%**"
        )

        prediction = st.text_area(
            "どうなると思う？",
            placeholder=(
                "例：ミスして"
                "かなり怒られるかもしれない"
            ),
        )

        worst_case = st.text_area(
            "😨 最悪の場合どうなる？",
            placeholder=(
                "例：仕事で"
                "大きな問題になる"
            ),
        )

        worst_probability = st.slider(
            "その最悪のケースが起きると思う確率",
            0,
            100,
            50,
            step=5,
        )

        date_unknown = st.checkbox(
            "📅 結果が分かる日は未定"
        )

        check_date = st.date_input(
            "いつ頃、答え合わせする？",
            value=today,
            min_value=today,
            disabled=date_unknown,
        )

        if st.form_submit_button(
            "📦 心配BOXに入れる",
            type="primary",
            use_container_width=True,
        ):
            if not title.strip():
                st.warning(
                    "心配していることを入力してね。"
                )
            else:
                add_worry(
                    data=data,
                    title=title.strip(),
                    category=category,
                    worry_level=worry_level,
                    prediction=prediction.strip(),
                    worst_case=worst_case.strip(),
                    worst_probability=worst_probability,
                    check_date=(
                        None
                        if date_unknown
                        else check_date
                    ),
                )

                st.rerun()


# =========================================================
# WORRY BOX
# =========================================================

with tab_box:

    st.subheader(
        "📦 心配BOX"
    )

    waiting = waiting_worries(data)

    if not waiting:
        st.success(
            "今、答え待ちの心配はありません。"
        )

    else:
        sort_type = st.selectbox(
            "並び順",
            [
                "確認日が近い順",
                "心配度が高い順",
                "新しい順",
            ],
        )

        if sort_type == "心配度が高い順":
            waiting = sorted(
                waiting,
                key=lambda w: int(
                    w.get("worry_level", 0)
                ),
                reverse=True,
            )

        elif sort_type == "新しい順":
            waiting = sorted(
                waiting,
                key=lambda w: w.get(
                    "created_at",
                    "",
                ),
                reverse=True,
            )

        else:
            waiting = sorted(
                waiting,
                key=lambda w: (
                    parse_date(
                        w.get("check_date")
                    )
                    or date.max
                ),
            )

        for worry in waiting:
            level = int(
                worry.get(
                    "worry_level",
                    0,
                )
            )

            with st.container(border=True):
                st.markdown(
                    f"### {worry.get('category')} "
                    f"{worry.get('title')}"
                )

                st.write(
                    f"😟 {worry_bar(level)} "
                    f"**{level}/100**"
                )

                days = days_until_check(worry)

                if days is None:
                    st.caption(
                        "📅 確認日：未定"
                    )

                elif days > 1:
                    st.caption(
                        f"📅 答え合わせまであと{days}日"
                    )

                elif days == 1:
                    st.caption(
                        "📅 答え合わせは明日"
                    )

                elif days == 0:
                    st.success(
                        "🌤️ 今日は答え合わせ予定日"
                    )

                else:
                    st.warning(
                        f"🌤️ 確認予定日から"
                        f"{abs(days)}日経過"
                    )

                if worry.get("prediction"):
                    st.write(
                        "**予想**"
                    )
                    st.write(
                        worry.get("prediction")
                    )

                if worry.get("worst_case"):
                    st.write(
                        "**最悪の想定**"
                    )
                    st.write(
                        worry.get("worst_case")
                    )

                    st.caption(
                        f"当時は "
                        f"{worry.get('worst_probability')}% "
                        "くらい起こると思っていた"
                    )


# =========================================================
# ANSWERS
# =========================================================

with tab_answers:

    st.subheader(
        "🌤️ 答え合わせ"
    )

    waiting = waiting_worries(data)

    if not waiting:
        st.info(
            "答え合わせを待っている"
            "記録はありません。"
        )

    else:
        options = {
            worry_label(w): w.get("id")
            for w in waiting
        }

        selected_label = st.selectbox(
            "どの心配を振り返る？",
            list(options.keys()),
        )

        selected_id = options[
            selected_label
        ]

        worry = get_worry(
            data,
            selected_id,
        )

        st.markdown(
            f"### 😟 {worry.get('title')}"
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "当時の心配度",
            f"{worry.get('worry_level')} / 100",
        )

        c2.metric(
            "最悪ケースの予想確率",
            f"{worry.get('worst_probability')}%",
        )

        if worry.get("prediction"):
            st.info(
                "当時の予想：\n\n"
                + worry.get("prediction")
            )

        if worry.get("worst_case"):
            st.warning(
                "最悪の想定：\n\n"
                + worry.get("worst_case")
            )

        with st.form(
            "resolve_worry"
        ):
            actual_result = st.text_area(
                "🌤️ 実際どうなった？",
                placeholder=(
                    "例：特に問題なく"
                    "終わった"
                ),
            )

            actual_severity = st.slider(
                "実際の深刻度",
                0,
                100,
                30,
                step=5,
            )

            st.write(
                f"{worry_bar(actual_severity)} "
                f"**{actual_severity}%**"
            )

            worst_result = st.radio(
                "最悪の予想は起きた？",
                WORST_RESULTS,
                index=2,
            )

            reflection = st.text_area(
                "今振り返ってどう思う？",
                placeholder=(
                    "例：かなり考えすぎて"
                    "いたかもしれない"
                ),
            )

            if st.form_submit_button(
                "🌤️ 答え合わせを保存",
                type="primary",
                use_container_width=True,
            ):
                if not actual_result.strip():
                    st.warning(
                        "実際どうなったか"
                        "少しだけ残してみよう。"
                    )

                else:
                    resolve_worry(
                        data=data,
                        worry_id=selected_id,
                        actual_result=(
                            actual_result.strip()
                        ),
                        actual_severity=(
                            actual_severity
                        ),
                        worst_result=(
                            worst_result
                        ),
                        reflection=(
                            reflection.strip()
                        ),
                    )

                    st.rerun()

    # -----------------------------------------------------
    # RECENT ANSWERS
    # -----------------------------------------------------

    resolved = resolved_worries(data)

    if resolved:
        st.divider()

        st.subheader(
            "📝 最近の答え合わせ"
        )

        resolved_sorted = sorted(
            resolved,
            key=lambda w: w.get(
                "resolved_at",
                "",
            ),
            reverse=True,
        )

        for worry in resolved_sorted[:8]:
            before = int(
                worry.get(
                    "worry_level",
                    0,
                )
            )

            actual = int(
                worry.get(
                    "actual_severity",
                    0,
                )
            )

            diff = actual - before

            diff_display = (
                f"+{diff}"
                if diff > 0
                else str(diff)
            )

            st.markdown(
                f"""
                <div class="compare-card">
                    <b>{worry.get("title")}</b>
                    <br><br>
                    <span style="font-size:1.8rem;">
                        😟 {before}
                        &nbsp; → &nbsp;
                        🌤️ {actual}
                    </span>
                    <br>
                    <b>差 {diff_display}ポイント</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(
                "実際の深刻度と、"
                "当時の心配度を比較しています。"
            )

            with st.expander(
                "答え合わせを見る"
            ):
                st.write(
                    "**実際**"
                )
                st.write(
                    worry.get(
                        "actual_result"
                    )
                )

                st.write(
                    "**最悪の予想**"
                )
                st.write(
                    worry.get(
                        "worst_result"
                    )
                )

                if worry.get("reflection"):
                    st.write(
                        "**振り返り**"
                    )
                    st.write(
                        worry.get(
                            "reflection"
                        )
                    )


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 心配と現実"
    )

    resolved = resolved_worries(data)

    if not resolved:
        st.info(
            "答え合わせが増えると、"
            "ここに自分の傾向が見えてきます。"
        )

    else:
        valid = [
            w
            for w in resolved
            if w.get("actual_severity")
            is not None
        ]

        avg_worry = sum(
            int(w.get("worry_level", 0))
            for w in valid
        ) / len(valid)

        avg_actual = sum(
            int(w.get("actual_severity", 0))
            for w in valid
        ) / len(valid)

        avg_diff = (
            avg_actual - avg_worry
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "🌤️ 答え合わせ",
            f"{len(valid)}件",
        )

        c2.metric(
            "😟 平均心配度",
            f"{avg_worry:.1f}",
        )

        c3.metric(
            "🌤️ 平均深刻度",
            f"{avg_actual:.1f}",
        )

        c4.metric(
            "📏 平均差",
            f"{avg_diff:+.1f}",
        )

        st.caption(
            "差 ＝ 実際の深刻度 − 当時の心配度。"
            "マイナスなら、実際の深刻度の方が"
            "低かったことを表します。"
        )

        # -------------------------------------------------
        # WORST CASE
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 😨 最悪の予想はどうなった？"
        )

        result_counts = {
            result: sum(
                1
                for w in valid
                if w.get(
                    "worst_result"
                ) == result
            )
            for result in WORST_RESULTS
        }

        result_df = pd.DataFrame(
            [
                {
                    "結果": result,
                    "件数": count,
                }
                for result, count
                in result_counts.items()
            ]
        ).set_index("結果")

        st.bar_chart(result_df)

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🧠 カテゴリー別"
        )

        category_data = defaultdict(
            lambda: {
                "worry": [],
                "actual": [],
            }
        )

        for w in valid:
            category = w.get(
                "category",
                "📦 その他",
            )

            category_data[
                category
            ]["worry"].append(
                int(w.get("worry_level", 0))
            )

            category_data[
                category
            ]["actual"].append(
                int(w.get("actual_severity", 0))
            )

        category_rows = []

        for category, values in (
            category_data.items()
        ):
            avg_w = (
                sum(values["worry"])
                / len(values["worry"])
            )

            avg_a = (
                sum(values["actual"])
                / len(values["actual"])
            )

            category_rows.append(
                {
                    "カテゴリー": category,
                    "件数": len(
                        values["worry"]
                    ),
                    "平均心配度": round(
                        avg_w,
                        1,
                    ),
                    "平均深刻度": round(
                        avg_a,
                        1,
                    ),
                    "差": round(
                        avg_a - avg_w,
                        1,
                    ),
                }
            )

        category_df = pd.DataFrame(
            category_rows
        ).sort_values(
            "平均心配度",
            ascending=False,
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        chart_df = category_df[
            [
                "カテゴリー",
                "平均心配度",
                "平均深刻度",
            ]
        ].set_index(
            "カテゴリー"
        )

        st.bar_chart(chart_df)

        # -------------------------------------------------
        # PROBABILITY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🎯 予想確率の答え合わせ"
        )

        probability_groups = [
            (0, 19, "0〜19%"),
            (20, 39, "20〜39%"),
            (40, 59, "40〜59%"),
            (60, 79, "60〜79%"),
            (80, 100, "80〜100%"),
        ]

        probability_rows = []

        for low, high, label in (
            probability_groups
        ):
            group = [
                w
                for w in valid
                if (
                    low
                    <= int(
                        w.get(
                            "worst_probability",
                            0,
                        )
                    )
                    <= high
                )
            ]

            if not group:
                continue

            happened = sum(
                1
                for w in group
                if w.get("worst_result")
                == "○ 起きた"
            )

            partial = sum(
                1
                for w in group
                if w.get("worst_result")
                == "△ 一部起きた"
            )

            not_happened = sum(
                1
                for w in group
                if w.get("worst_result")
                == "× 起きなかった"
            )

            probability_rows.append(
                {
                    "当時の予想": label,
                    "記録": len(group),
                    "起きた": happened,
                    "一部": partial,
                    "起きなかった": (
                        not_happened
                    ),
                }
            )

        if probability_rows:
            st.dataframe(
                pd.DataFrame(
                    probability_rows
                ),
                hide_index=True,
                use_container_width=True,
            )

        # -------------------------------------------------
        # LONGEST
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### ⏳ 長く抱えていた心配"
        )

        held_rows = []

        for w in valid:
            days = days_held(w)

            if days is not None:
                held_rows.append(
                    (
                        days,
                        w,
                    )
                )

        held_rows.sort(
            key=lambda row: row[0],
            reverse=True,
        )

        for index, (
            days,
            worry,
        ) in enumerate(
            held_rows[:10],
            start=1,
        ):
            st.write(
                f"**{index}. "
                f"{worry.get('title')}** "
                f"— {days}日"
            )

        # -------------------------------------------------
        # MONTHLY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 📅 月別の心配"
        )

        monthly_rows = []

        for w in worries:
            created = parse_datetime(
                w.get("created_at")
            )

            if not created:
                continue

            monthly_rows.append(
                {
                    "月": (
                        created.strftime(
                            "%Y-%m"
                        )
                    ),
                    "心配度": int(
                        w.get(
                            "worry_level",
                            0,
                        )
                    ),
                    "実際の深刻度": (
                        int(
                            w.get(
                                "actual_severity"
                            )
                        )
                        if w.get(
                            "actual_severity"
                        )
                        is not None
                        else None
                    ),
                }
            )

        if monthly_rows:
            monthly_df = pd.DataFrame(
                monthly_rows
            )

            monthly_summary = (
                monthly_df
                .groupby("月")
                .agg(
                    記録数=(
                        "心配度",
                        "count",
                    ),
                    平均心配度=(
                        "心配度",
                        "mean",
                    ),
                    平均深刻度=(
                        "実際の深刻度",
                        "mean",
                    ),
                )
                .round(1)
            )

            st.dataframe(
                monthly_summary,
                use_container_width=True,
            )

            st.line_chart(
                monthly_summary[
                    [
                        "平均心配度",
                        "平均深刻度",
                    ]
                ]
            )

        # -------------------------------------------------
        # RANDOM
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🎲 あの心配、覚えてる？"
        )

        resolved_ids = [
            w.get("id")
            for w in valid
        ]

        random_id = st.session_state.get(
            "random_worry_id"
        )

        if random_id not in resolved_ids:
            random_id = random.choice(
                resolved_ids
            )

            st.session_state[
                "random_worry_id"
            ] = random_id

        random_worry = get_worry(
            data,
            random_id,
        )

        with st.container(border=True):
            st.markdown(
                f"### 😟 "
                f"{random_worry.get('title')}"
            )

            st.write(
                f"当時："
                f"**{random_worry.get('worry_level')}**"
            )

            st.write(
                f"実際："
                f"**{random_worry.get('actual_severity')}**"
            )

            st.write(
                f"最悪の予想："
                f"**{random_worry.get('worst_result')}**"
            )

            if random_worry.get(
                "reflection"
            ):
                st.info(
                    random_worry.get(
                        "reflection"
                    )
                )

        if st.button(
            "🎲 別の心配を見る",
            use_container_width=True,
        ):
            alternatives = [
                worry_id
                for worry_id
                in resolved_ids
                if worry_id != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_worry_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 心配図鑑"
    )

    search = st.text_input(
        "🔎 検索",
        key="library_search",
    )

    col1, col2 = st.columns(2)

    with col1:
        category_filter = st.selectbox(
            "カテゴリー",
            ["すべて"] + CATEGORIES,
            key="library_category",
        )

    with col2:
        status_filter = st.selectbox(
            "状態",
            [
                "すべて",
                STATUS_WAITING,
                STATUS_RESOLVED,
            ],
            key="library_status",
        )

    min_level = st.slider(
        "最低心配度",
        0,
        100,
        0,
        step=10,
    )

    rows = []

    for worry in worries:
        if (
            category_filter != "すべて"
            and worry.get("category")
            != category_filter
        ):
            continue

        if (
            status_filter != "すべて"
            and worry.get("status")
            != status_filter
        ):
            continue

        if (
            int(worry.get("worry_level", 0))
            < min_level
        ):
            continue

        searchable = " ".join(
            [
                worry.get("title", ""),
                worry.get("prediction", ""),
                worry.get("worst_case", ""),
                worry.get("actual_result", ""),
                worry.get("reflection", ""),
            ]
        ).lower()

        if (
            search.strip()
            and search.strip().lower()
            not in searchable
        ):
            continue

        created = parse_datetime(
            worry.get("created_at")
        )

        rows.append(
            {
                "心配": worry.get("title"),
                "カテゴリー": (
                    worry.get("category")
                ),
                "記録日": (
                    created.strftime(
                        "%Y/%m/%d"
                    )
                    if created
                    else "-"
                ),
                "心配度": (
                    worry.get("worry_level")
                ),
                "実際": (
                    worry.get("actual_severity")
                    if worry.get(
                        "actual_severity"
                    )
                    is not None
                    else "-"
                ),
                "差": (
                    difference_text(
                        worry.get(
                            "worry_level"
                        ),
                        worry.get(
                            "actual_severity"
                        ),
                    )
                ),
                "状態": (
                    worry.get("status")
                ),
            }
        )

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info(
            "条件に合う記録はありません。"
        )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 記録を編集"
    )

    if not worries:
        st.info(
            "まだ記録がありません。"
        )

    else:
        options = {
            worry_label(w): w.get("id")
            for w in worries
        }

        selected_label = st.selectbox(
            "編集する記録",
            list(options.keys()),
            key="manage_select",
        )

        selected_id = options[
            selected_label
        ]

        worry = get_worry(
            data,
            selected_id,
        )

        edit_title = st.text_input(
            "心配",
            value=worry.get(
                "title",
                "",
            ),
        )

        old_category = worry.get(
            "category",
            "📦 その他",
        )

        category_index = (
            CATEGORIES.index(
                old_category
            )
            if old_category in CATEGORIES
            else len(CATEGORIES) - 1
        )

        edit_category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
            index=category_index,
            key="manage_category",
        )

        edit_level = st.slider(
            "当時の心配度",
            0,
            100,
            int(
                worry.get(
                    "worry_level",
                    50,
                )
            ),
            step=5,
        )

        edit_prediction = st.text_area(
            "当時の予想",
            value=worry.get(
                "prediction",
                "",
            ),
        )

        edit_worst = st.text_area(
            "最悪の想定",
            value=worry.get(
                "worst_case",
                "",
            ),
        )

        edit_probability = st.slider(
            "最悪ケースの予想確率",
            0,
            100,
            int(
                worry.get(
                    "worst_probability",
                    50,
                )
            ),
            step=5,
        )

        check_unknown = st.checkbox(
            "確認日は未定",
            value=(
                worry.get("check_date")
                is None
            ),
        )

        current_check = (
            parse_date(
                worry.get("check_date")
            )
            or today
        )

        edit_check_date = st.date_input(
            "確認予定日",
            value=current_check,
            disabled=check_unknown,
            key="manage_check_date",
        )

        if st.button(
            "💾 基本情報を保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_title.strip():
                st.warning(
                    "心配の内容を入力してね。"
                )

            else:
                worry["title"] = (
                    edit_title.strip()
                )
                worry["category"] = (
                    edit_category
                )
                worry["worry_level"] = (
                    int(edit_level)
                )
                worry["prediction"] = (
                    edit_prediction.strip()
                )
                worry["worst_case"] = (
                    edit_worst.strip()
                )
                worry[
                    "worst_probability"
                ] = int(
                    edit_probability
                )
                worry["check_date"] = (
                    None
                    if check_unknown
                    else str(
                        edit_check_date
                    )
                )
                worry["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # -------------------------------------------------
        # RESOLVED EDIT
        # -------------------------------------------------

        if (
            worry.get("status")
            == STATUS_RESOLVED
        ):
            st.divider()

            st.subheader(
                "🌤️ 答え合わせを編集"
            )

            edit_actual_result = (
                st.text_area(
                    "実際どうなった？",
                    value=worry.get(
                        "actual_result",
                        "",
                    ),
                    key="manage_actual_result",
                )
            )

            edit_actual_severity = (
                st.slider(
                    "実際の深刻度",
                    0,
                    100,
                    int(
                        worry.get(
                            "actual_severity",
                            0,
                        )
                    ),
                    step=5,
                    key="manage_actual_severity",
                )
            )

            old_worst_result = (
                worry.get(
                    "worst_result"
                )
            )

            result_index = (
                WORST_RESULTS.index(
                    old_worst_result
                )
                if old_worst_result
                in WORST_RESULTS
                else 2
            )

            edit_worst_result = (
                st.selectbox(
                    "最悪の予想は？",
                    WORST_RESULTS,
                    index=result_index,
                    key="manage_worst_result",
                )
            )

            edit_reflection = (
                st.text_area(
                    "振り返り",
                    value=worry.get(
                        "reflection",
                        "",
                    ),
                    key="manage_reflection",
                )
            )

            if st.button(
                "💾 答え合わせを保存",
                use_container_width=True,
            ):
                worry["actual_result"] = (
                    edit_actual_result.strip()
                )
                worry[
                    "actual_severity"
                ] = int(
                    edit_actual_severity
                )
                worry["worst_result"] = (
                    edit_worst_result
                )
                worry["reflection"] = (
                    edit_reflection.strip()
                )
                worry["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        st.divider()

        delete_confirm = st.checkbox(
            "この記録を完全に削除する",
            key=(
                "delete_confirm_"
                + selected_id
            ),
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=not delete_confirm,
            key=(
                "delete_"
                + selected_id
            ),
            use_container_width=True,
        ):
            delete_worry(
                data,
                selected_id,
            )

            st.rerun()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

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
            f"worry_reality_{today}.json"
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
            あの日の自分は、
            本気で心配していた。
            </b>
        </p>

        <p>
            その気持ちを否定しなくていい。
        </p>

        <p>
            ただ、未来が実際にやってきたとき、
            <b>何が起きたのか</b>も残しておこう。
        </p>

        <p>
            それを積み重ねれば、
            自分が未来をどう見ているのかが、
            少しずつ見えてくる。🌤️
        </p>

        <br>

        <b>DAY 305 / 365 — COMPLETE 🔥</b>
    </div>
    """,
    unsafe_allow_html=True,
)
