import json
import os
import random
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="AI決断メモ",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "decisions.json",
)

CATEGORIES = [
    "仕事",
    "転職",
    "アプリ開発",
    "起業",
    "お金",
    "買い物",
    "健康",
    "家族",
    "人間関係",
    "引っ越し",
    "学習",
    "趣味",
    "生活",
    "その他",
]

STATUSES = [
    "検討前",
    "検討中",
    "決断済み",
    "実行中",
    "完了",
    "保留",
    "撤回",
]

STATUS_ICONS = {
    "検討前": "⚪",
    "検討中": "🤔",
    "決断済み": "✅",
    "実行中": "🚀",
    "完了": "🏁",
    "保留": "⏸️",
    "撤回": "↩️",
}

WEIGHTS = [
    "軽い",
    "普通",
    "重要",
    "人生に関わる",
]

WEIGHT_VALUES = {
    "軽い": 1,
    "普通": 2,
    "重要": 3,
    "人生に関わる": 4,
}

WEIGHT_ICONS = {
    "軽い": "🌱",
    "普通": "🟡",
    "重要": "🔴",
    "人生に関わる": "🔥",
}

REVIEW_RESULTS = [
    "未評価",
    "良い決断だった",
    "結果は悪かったが判断は妥当だった",
    "情報不足だった",
    "感情で決めすぎた",
    "先延ばしにしてしまった",
    "別の選択肢がよかった",
    "判断を撤回した",
]

PRIORITIES = [
    "最優先",
    "高",
    "中",
    "低",
]

PRIORITY_ORDER = {
    "最優先": 0,
    "高": 1,
    "中": 2,
    "低": 3,
}

PRIORITY_ICONS = {
    "最優先": "🔥",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵",
}


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作る。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds",
    )


def create_empty_data():
    """空の初期データを作る。"""

    return {
        "decisions": [],
    }


def save_data(data):
    """JSONファイルへ保存する。"""

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


def normalize_option(option):
    """選択肢データに不足項目を追加する。"""

    option.setdefault(
        "id",
        create_id(),
    )

    option.setdefault(
        "name",
        "",
    )

    option.setdefault(
        "description",
        "",
    )

    option.setdefault(
        "pros",
        "",
    )

    option.setdefault(
        "cons",
        "",
    )

    option.setdefault(
        "score",
        3,
    )

    option.setdefault(
        "cost",
        "",
    )

    option.setdefault(
        "risk",
        "",
    )

    option.setdefault(
        "created_at",
        "",
    )


def normalize_data(data):
    """古い保存データへ不足項目を追加する。"""

    if not isinstance(
        data,
        dict,
    ):
        data = create_empty_data()

    data.setdefault(
        "decisions",
        [],
    )

    for decision in data["decisions"]:
        decision.setdefault(
            "id",
            create_id(),
        )

        decision.setdefault(
            "title",
            "",
        )

        decision.setdefault(
            "category",
            "その他",
        )

        decision.setdefault(
            "status",
            "検討前",
        )

        decision.setdefault(
            "weight",
            "普通",
        )

        decision.setdefault(
            "priority",
            "中",
        )

        decision.setdefault(
            "registered_date",
            str(date.today()),
        )

        decision.setdefault(
            "deadline",
            "",
        )

        decision.setdefault(
            "review_date",
            "",
        )

        decision.setdefault(
            "background",
            "",
        )

        decision.setdefault(
            "important_conditions",
            "",
        )

        decision.setdefault(
            "worries",
            "",
        )

        decision.setdefault(
            "ideal_result",
            "",
        )

        decision.setdefault(
            "facts",
            "",
        )

        decision.setdefault(
            "feelings",
            "",
        )

        decision.setdefault(
            "ai_advice",
            "",
        )

        decision.setdefault(
            "ai_questions",
            "",
        )

        decision.setdefault(
            "options",
            [],
        )

        decision.setdefault(
            "selected_option_id",
            "",
        )

        decision.setdefault(
            "final_decision",
            "",
        )

        decision.setdefault(
            "decision_reason",
            "",
        )

        decision.setdefault(
            "first_step",
            "",
        )

        decision.setdefault(
            "decided_date",
            "",
        )

        decision.setdefault(
            "execution_progress",
            0,
        )

        decision.setdefault(
            "execution_memo",
            "",
        )

        decision.setdefault(
            "review_result",
            "未評価",
        )

        decision.setdefault(
            "satisfaction",
            0,
        )

        decision.setdefault(
            "result_detail",
            "",
        )

        decision.setdefault(
            "unexpected_result",
            "",
        )

        decision.setdefault(
            "next_learning",
            "",
        )

        decision.setdefault(
            "created_at",
            "",
        )

        decision.setdefault(
            "updated_at",
            "",
        )

        for option in decision["options"]:
            normalize_option(
                option,
            )

    return data


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE,
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

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE,
            ):
                os.replace(
                    DATA_FILE,
                    broken_file,
                )

        except OSError:
            pass

        data = create_empty_data()
        save_data(data)

        return data


# =========================================================
# 補助関数
# =========================================================

def parse_date(date_text):
    """日付文字列をdate型へ変換する。"""

    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

    except (
        TypeError,
        ValueError,
    ):
        return None


def format_date(date_text):
    """日付を日本語表示にする。"""

    parsed = parse_date(
        date_text,
    )

    if not parsed:
        return "未設定"

    weekdays = [
        "月",
        "火",
        "水",
        "木",
        "金",
        "土",
        "日",
    ]

    weekday = weekdays[
        parsed.weekday()
    ]

    return parsed.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_decision_by_id(
    data,
    decision_id,
):
    """IDから決断を取得する。"""

    for decision in data[
        "decisions"
    ]:
        if decision.get(
            "id",
        ) == decision_id:
            return decision

    return None


def get_option_by_id(
    decision,
    option_id,
):
    """IDから選択肢を取得する。"""

    for option in decision.get(
        "options",
        [],
    ):
        if option.get(
            "id",
        ) == option_id:
            return option

    return None


def deadline_days(
    decision,
):
    """期限までの日数を返す。"""

    deadline = parse_date(
        decision.get(
            "deadline",
            "",
        )
    )

    if not deadline:
        return None

    return (
        deadline
        - date.today()
    ).days


def is_overdue(
    decision,
):
    """決断期限を過ぎているか判定する。"""

    days = deadline_days(
        decision,
    )

    return bool(
        days is not None
        and days < 0
        and decision.get(
            "status",
        )
        in [
            "検討前",
            "検討中",
        ]
    )


def option_average_score(
    decision,
):
    """選択肢の平均点を返す。"""

    scores = [
        int(
            option.get(
                "score",
                0,
            )
        )
        for option in decision.get(
            "options",
            [],
        )
        if int(
            option.get(
                "score",
                0,
            )
        )
        > 0
    ]

    if not scores:
        return 0

    return (
        sum(scores)
        / len(scores)
    )


def selected_option_name(
    decision,
):
    """選ばれた選択肢名を返す。"""

    selected_id = decision.get(
        "selected_option_id",
        "",
    )

    option = get_option_by_id(
        decision,
        selected_id,
    )

    if option:
        return option.get(
            "name",
            "",
        )

    return ""


def execution_rate(
    decisions,
):
    """決断済みのうち実行へ移せた割合を返す。"""

    decided = [
        decision
        for decision in decisions
        if decision.get(
            "status",
        )
        in [
            "決断済み",
            "実行中",
            "完了",
        ]
    ]

    if not decided:
        return 0

    executed = [
        decision
        for decision in decided
        if decision.get(
            "status",
        )
        in [
            "実行中",
            "完了",
        ]
        or int(
            decision.get(
                "execution_progress",
                0,
            )
        )
        > 0
    ]

    return (
        len(executed)
        / len(decided)
        * 100
    )


def decision_days(
    decision,
):
    """登録から決断までの日数を返す。"""

    registered = parse_date(
        decision.get(
            "registered_date",
            "",
        )
    )

    decided = parse_date(
        decision.get(
            "decided_date",
            "",
        )
    )

    if not registered or not decided:
        return None

    return (
        decided
        - registered
    ).days


def update_status_automatically(
    decision,
):
    """内容から状態を補助的に更新する。"""

    current_status = decision.get(
        "status",
        "検討前",
    )

    if current_status in [
        "完了",
        "保留",
        "撤回",
    ]:
        return

    progress = int(
        decision.get(
            "execution_progress",
            0,
        )
    )

    if progress >= 100:
        decision["status"] = "完了"

    elif progress > 0:
        decision["status"] = "実行中"

    elif decision.get(
        "final_decision",
        "",
    ).strip():
        decision["status"] = "決断済み"

    elif (
        decision.get(
            "options",
            [],
        )
        or decision.get(
            "ai_advice",
            "",
        ).strip()
    ):
        decision["status"] = "検討中"


# =========================================================
# データ操作
# =========================================================

def add_decision(
    data,
    values,
):
    """決断テーマを登録する。"""

    decision = {
        "id": create_id(),
        "title": values["title"],
        "category": values["category"],
        "status": values["status"],
        "weight": values["weight"],
        "priority": values["priority"],
        "registered_date": (
            values["registered_date"]
        ),
        "deadline": values["deadline"],
        "review_date": (
            values["review_date"]
        ),
        "background": values["background"],
        "important_conditions": (
            values[
                "important_conditions"
            ]
        ),
        "worries": values["worries"],
        "ideal_result": (
            values["ideal_result"]
        ),
        "facts": values["facts"],
        "feelings": values["feelings"],
        "ai_advice": values["ai_advice"],
        "ai_questions": (
            values["ai_questions"]
        ),
        "options": [],
        "selected_option_id": "",
        "final_decision": "",
        "decision_reason": "",
        "first_step": "",
        "decided_date": "",
        "execution_progress": 0,
        "execution_memo": "",
        "review_result": "未評価",
        "satisfaction": 0,
        "result_detail": "",
        "unexpected_result": "",
        "next_learning": "",
        "created_at": now_text(),
        "updated_at": "",
    }

    update_status_automatically(
        decision,
    )

    data["decisions"].append(
        decision,
    )

    save_data(data)


def update_decision(
    data,
    decision_id,
    values,
):
    """決断テーマを更新する。"""

    decision = get_decision_by_id(
        data,
        decision_id,
    )

    if not decision:
        return

    previous_final = decision.get(
        "final_decision",
        "",
    )

    for key, value in values.items():
        decision[key] = value

    if (
        decision.get(
            "final_decision",
            "",
        ).strip()
        and not previous_final.strip()
        and not decision.get(
            "decided_date",
            "",
        )
    ):
        decision["decided_date"] = str(
            date.today()
        )

    update_status_automatically(
        decision,
    )

    decision["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_decision(
    data,
    decision_id,
):
    """決断テーマを削除する。"""

    data["decisions"] = [
        decision
        for decision in data[
            "decisions"
        ]
        if decision.get(
            "id",
        )
        != decision_id
    ]

    save_data(data)


def add_option(
    data,
    decision_id,
    values,
):
    """選択肢を追加する。"""

    decision = get_decision_by_id(
        data,
        decision_id,
    )

    if not decision:
        return

    option = {
        "id": create_id(),
        "name": values["name"],
        "description": (
            values["description"]
        ),
        "pros": values["pros"],
        "cons": values["cons"],
        "score": int(
            values["score"]
        ),
        "cost": values["cost"],
        "risk": values["risk"],
        "created_at": now_text(),
    }

    decision["options"].append(
        option,
    )

    update_status_automatically(
        decision,
    )

    decision["updated_at"] = (
        now_text()
    )

    save_data(data)


def update_option(
    data,
    decision_id,
    option_id,
    values,
):
    """選択肢を更新する。"""

    decision = get_decision_by_id(
        data,
        decision_id,
    )

    if not decision:
        return

    option = get_option_by_id(
        decision,
        option_id,
    )

    if not option:
        return

    for key, value in values.items():
        option[key] = value

    option["score"] = int(
        option.get(
            "score",
            3,
        )
    )

    decision["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_option(
    data,
    decision_id,
    option_id,
):
    """選択肢を削除する。"""

    decision = get_decision_by_id(
        data,
        decision_id,
    )

    if not decision:
        return

    decision["options"] = [
        option
        for option in decision.get(
            "options",
            [],
        )
        if option.get(
            "id",
        )
        != option_id
    ]

    if (
        decision.get(
            "selected_option_id",
        )
        == option_id
    ):
        decision[
            "selected_option_id"
        ] = ""

    decision["updated_at"] = (
        now_text()
    )

    save_data(data)


# =========================================================
# デザイン
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(105, 95, 255, 0.07);
        border: 1px solid rgba(105, 95, 255, 0.16);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(105, 95, 255, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(105, 95, 255, 0.18),
                rgba(60, 200, 180, 0.12)
            );
    }

    .hero h1 {
        margin: 0 0 8px 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.78;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

decisions = data[
    "decisions"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧠 AI決断メモ</h1>
        <p>
            AIの意見を参考にしながら、
            最後は自分で納得して決断するための記録アプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

total_count = len(
    decisions,
)

considering_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status",
        )
        in [
            "検討前",
            "検討中",
        ]
    ]
)

decided_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status",
        )
        == "決断済み"
    ]
)

executing_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status",
        )
        == "実行中"
    ]
)

completed_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status",
        )
        == "完了"
    ]
)

overdue_count = len(
    [
        decision
        for decision in decisions
        if is_overdue(
            decision,
        )
    ]
)

current_month = (
    date.today().strftime(
        "%Y-%m",
    )
)

monthly_decision_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "decided_date",
            "",
        ).startswith(
            current_month,
        )
    ]
)

execution_percentage = (
    execution_rate(
        decisions,
    )
)

metric_row1 = st.columns(4)

metric_row1[0].metric(
    "登録した悩み",
    f"{total_count}件",
)

metric_row1[1].metric(
    "検討中",
    f"{considering_count}件",
)

metric_row1[2].metric(
    "決断済み",
    f"{decided_count}件",
)

metric_row1[3].metric(
    "実行中",
    f"{executing_count}件",
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "完了",
    f"{completed_count}件",
)

metric_row2[1].metric(
    "期限超過",
    f"{overdue_count}件",
)

metric_row2[2].metric(
    "今月の決断",
    f"{monthly_decision_count}件",
)

metric_row2[3].metric(
    "実行に移せた割合",
    f"{execution_percentage:.1f}%",
)


# =========================================================
# 次に決めること
# =========================================================

active_decisions = [
    decision
    for decision in decisions
    if decision.get(
        "status",
    )
    in [
        "検討前",
        "検討中",
    ]
]

if active_decisions:
    st.divider()

    active_decisions.sort(
        key=lambda decision: (
            PRIORITY_ORDER.get(
                decision.get(
                    "priority",
                    "中",
                ),
                99,
            ),
            deadline_days(
                decision,
            )
            if deadline_days(
                decision,
            )
            is not None
            else 999999,
        )
    )

    next_decision = (
        active_decisions[0]
    )

    st.subheader(
        "🎯 次に決めること"
    )

    with st.container(
        border=True,
    ):
        column1, column2 = (
            st.columns(
                [
                    4,
                    1,
                ]
            )
        )

        with column1:
            st.markdown(
                f"### "
                f"{PRIORITY_ICONS.get(next_decision.get('priority', ''), '')} "
                f"{next_decision.get('title', '')}"
            )

            st.caption(
                f"{next_decision.get('category', '')} ／ "
                f"{WEIGHT_ICONS.get(next_decision.get('weight', ''), '')} "
                f"{next_decision.get('weight', '')}"
            )

            if next_decision.get(
                "background",
                "",
            ):
                st.write(
                    next_decision.get(
                        "background",
                        "",
                    )
                )

        with column2:
            remaining_days = (
                deadline_days(
                    next_decision,
                )
            )

            if remaining_days is None:
                st.metric(
                    "決断期限",
                    "未設定",
                )

            elif remaining_days < 0:
                st.metric(
                    "決断期限",
                    f"{-remaining_days}日超過",
                )

            elif remaining_days == 0:
                st.metric(
                    "決断期限",
                    "今日",
                )

            else:
                st.metric(
                    "決断期限",
                    f"あと{remaining_days}日",
                )


# =========================================================
# 過去の学び
# =========================================================

reviewed_decisions = [
    decision
    for decision in decisions
    if decision.get(
        "next_learning",
        "",
    ).strip()
]

if reviewed_decisions:
    st.divider()

    st.subheader(
        "💡 過去の決断から得た学び"
    )

    if (
        "random_decision_id"
        not in st.session_state
    ):
        st.session_state[
            "random_decision_id"
        ] = random.choice(
            reviewed_decisions
        )["id"]

    random_decision = (
        get_decision_by_id(
            data,
            st.session_state[
                "random_decision_id"
            ],
        )
    )

    if random_decision:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### "
                f"{random_decision.get('title', '')}"
            )

            st.info(
                random_decision.get(
                    "next_learning",
                    "",
                )
            )

            if random_decision.get(
                "final_decision",
                "",
            ):
                st.caption(
                    "当時の決断："
                    + random_decision.get(
                        "final_decision",
                        "",
                    )
                )

    if st.button(
        "🔄 別の学びを表示"
    ):
        st.session_state[
            "random_decision_id"
        ] = random.choice(
            reviewed_decisions
        )["id"]

        st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    options_tab,
    decision_tab,
    list_tab,
    review_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 悩みを登録",
        "⚖️ 選択肢比較",
        "✅ 最終決断",
        "📚 決断一覧",
        "🔍 結果の振り返り",
        "📈 決断分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 悩み登録
# =========================================================

with add_tab:
    st.header(
        "➕ 新しい決断テーマを登録"
    )

    with st.form(
        "add_decision_form",
        clear_on_submit=True,
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            title = st.text_input(
                "決断テーマ",
                placeholder=(
                    "例：次にどのアプリを優先して作るか"
                ),
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
            )

            weight = st.selectbox(
                "決断の重み",
                WEIGHTS,
                index=1,
            )

            priority = st.selectbox(
                "優先度",
                PRIORITIES,
                index=2,
            )

        with column2:
            status = st.selectbox(
                "状態",
                STATUSES,
                index=0,
            )

            registered_date = (
                st.date_input(
                    "登録日",
                    value=date.today(),
                    max_value=date.today(),
                )
            )

            set_deadline = (
                st.checkbox(
                    "決断期限を設定する"
                )
            )

            deadline = ""

            if set_deadline:
                deadline = str(
                    st.date_input(
                        "決断期限",
                        value=(
                            date.today()
                            + timedelta(
                                days=7,
                            )
                        ),
                    )
                )

            set_review_date = (
                st.checkbox(
                    "振り返り予定日を設定する"
                )
            )

            review_date = ""

            if set_review_date:
                review_date = str(
                    st.date_input(
                        "振り返り予定日",
                        value=(
                            date.today()
                            + timedelta(
                                days=30,
                            )
                        ),
                    )
                )

        background = st.text_area(
            "背景・何に迷っている？",
            placeholder=(
                "なぜ今この決断が必要なのか"
            ),
            height=110,
        )

        important_conditions = (
            st.text_area(
                "重要な条件",
                placeholder=(
                    "必ず守りたい条件や判断基準"
                ),
                height=100,
            )
        )

        worries = st.text_area(
            "不安なこと",
            placeholder=(
                "失敗した場合に心配なこと"
            ),
            height=90,
        )

        ideal_result = st.text_area(
            "理想の結果",
            placeholder=(
                "どのような状態になれば成功か"
            ),
            height=90,
        )

        fact_column, feeling_column = (
            st.columns(2)
        )

        with fact_column:
            facts = st.text_area(
                "現実・事実",
                placeholder=(
                    "数字、期限、予算、能力など"
                ),
                height=120,
            )

        with feeling_column:
            feelings = st.text_area(
                "自分の気持ち",
                placeholder=(
                    "本当はどうしたいか"
                ),
                height=120,
            )

        ai_advice = st.text_area(
            "AIからの提案",
            placeholder=(
                "ChatGPTなどから受け取った意見を貼り付けます。"
            ),
            height=140,
        )

        ai_questions = st.text_area(
            "AIから聞かれたこと・追加で考えること",
            placeholder=(
                "まだ整理できていない問いを残します。"
            ),
            height=100,
        )

        submitted = (
            st.form_submit_button(
                "🧠 決断テーマを登録",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.error(
                    "決断テーマを入力してください。"
                )

            elif not background.strip():
                st.error(
                    "背景・迷っていることを入力してください。"
                )

            else:
                add_decision(
                    data,
                    {
                        "title": (
                            title.strip()
                        ),
                        "category": category,
                        "status": status,
                        "weight": weight,
                        "priority": priority,
                        "registered_date": str(
                            registered_date
                        ),
                        "deadline": deadline,
                        "review_date": (
                            review_date
                        ),
                        "background": (
                            background.strip()
                        ),
                        "important_conditions": (
                            important_conditions.strip()
                        ),
                        "worries": (
                            worries.strip()
                        ),
                        "ideal_result": (
                            ideal_result.strip()
                        ),
                        "facts": facts.strip(),
                        "feelings": (
                            feelings.strip()
                        ),
                        "ai_advice": (
                            ai_advice.strip()
                        ),
                        "ai_questions": (
                            ai_questions.strip()
                        ),
                    },
                )

                st.success(
                    "決断テーマを登録しました！"
                )

                st.rerun()


# =========================================================
# 選択肢比較
# =========================================================

with options_tab:
    st.header(
        "⚖️ 選択肢を比較"
    )

    if not decisions:
        st.info(
            "先に決断テーマを登録してください。"
        )

    else:
        decision_options = {
            (
                f"{decision.get('title', '')}"
                f"｜{decision.get('status', '')}"
            ): decision["id"]
            for decision in decisions
        }

        selected_label = st.selectbox(
            "決断テーマ",
            list(
                decision_options.keys()
            ),
            key="option_decision_select",
        )

        selected_decision = (
            get_decision_by_id(
                data,
                decision_options[
                    selected_label
                ],
            )
        )

        decision_id = (
            selected_decision["id"]
        )

        with st.container(
            border=True,
        ):
            st.subheader(
                selected_decision.get(
                    "title",
                    "",
                )
            )

            st.write(
                selected_decision.get(
                    "background",
                    "",
                )
            )

            if selected_decision.get(
                "important_conditions",
                "",
            ):
                st.info(
                    "重要な条件\n\n"
                    + selected_decision.get(
                        "important_conditions",
                        "",
                    )
                )

        with st.form(
            f"add_option_{decision_id}",
            clear_on_submit=True,
        ):
            st.subheader(
                "➕ 選択肢を追加"
            )

            option_name = st.text_input(
                "選択肢名",
                placeholder=(
                    "例：AI Router βを進める"
                ),
            )

            option_description = (
                st.text_area(
                    "選択肢の説明",
                    placeholder=(
                        "具体的に何を選ぶのか"
                    ),
                    height=80,
                )
            )

            option_columns = (
                st.columns(2)
            )

            with option_columns[0]:
                pros = st.text_area(
                    "メリット",
                    placeholder=(
                        "良い点を改行して入力"
                    ),
                    height=120,
                )

                cost = st.text_area(
                    "必要なコスト",
                    placeholder=(
                        "お金・時間・労力など"
                    ),
                    height=80,
                )

            with option_columns[1]:
                cons = st.text_area(
                    "デメリット",
                    placeholder=(
                        "悪い点や失うもの"
                    ),
                    height=120,
                )

                risk = st.text_area(
                    "リスク",
                    placeholder=(
                        "起こり得る問題"
                    ),
                    height=80,
                )

            score = st.slider(
                "現時点での総合評価",
                min_value=1,
                max_value=5,
                value=3,
            )

            option_submit = (
                st.form_submit_button(
                    "選択肢を追加",
                    use_container_width=True,
                )
            )

            if option_submit:
                if not option_name.strip():
                    st.error(
                        "選択肢名を入力してください。"
                    )

                else:
                    add_option(
                        data,
                        decision_id,
                        {
                            "name": (
                                option_name.strip()
                            ),
                            "description": (
                                option_description.strip()
                            ),
                            "pros": pros.strip(),
                            "cons": cons.strip(),
                            "score": score,
                            "cost": cost.strip(),
                            "risk": risk.strip(),
                        },
                    )

                    st.rerun()

        st.divider()

        options = sorted(
            selected_decision.get(
                "options",
                [],
            ),
            key=lambda option: int(
                option.get(
                    "score",
                    0,
                )
            ),
            reverse=True,
        )

        if not options:
            st.info(
                "選択肢はまだ登録されていません。"
            )

        else:
            st.write(
                f"選択肢："
                f"**{len(options)}件** ／ "
                f"平均評価："
                f"**{option_average_score(selected_decision):.1f}/5**"
            )

            for option in options:
                option_id = option[
                    "id"
                ]

                with st.container(
                    border=True,
                ):
                    title_column, score_column = (
                        st.columns(
                            [
                                4,
                                1,
                            ]
                        )
                    )

                    with title_column:
                        st.markdown(
                            f"### "
                            f"{option.get('name', '')}"
                        )

                        if option.get(
                            "description",
                            "",
                        ):
                            st.write(
                                option.get(
                                    "description",
                                    "",
                                )
                            )

                    with score_column:
                        st.metric(
                            "総合評価",
                            f"{option.get('score', 3)}/5",
                        )

                    comparison_columns = (
                        st.columns(2)
                    )

                    with comparison_columns[0]:
                        if option.get(
                            "pros",
                            "",
                        ):
                            st.success(
                                "メリット\n\n"
                                + option.get(
                                    "pros",
                                    "",
                                )
                            )

                        if option.get(
                            "cost",
                            "",
                        ):
                            st.info(
                                "必要なコスト\n\n"
                                + option.get(
                                    "cost",
                                    "",
                                )
                            )

                    with comparison_columns[1]:
                        if option.get(
                            "cons",
                            "",
                        ):
                            st.warning(
                                "デメリット\n\n"
                                + option.get(
                                    "cons",
                                    "",
                                )
                            )

                        if option.get(
                            "risk",
                            "",
                        ):
                            st.error(
                                "リスク\n\n"
                                + option.get(
                                    "risk",
                                    "",
                                )
                            )

                    with st.expander(
                        "✏️ 選択肢を編集"
                    ):
                        edit_name = st.text_input(
                            "選択肢名",
                            value=option.get(
                                "name",
                                "",
                            ),
                            key=(
                                f"edit_option_name_"
                                f"{option_id}"
                            ),
                        )

                        edit_description = (
                            st.text_area(
                                "説明",
                                value=option.get(
                                    "description",
                                    "",
                                ),
                                key=(
                                    f"edit_option_description_"
                                    f"{option_id}"
                                ),
                            )
                        )

                        edit_pros = st.text_area(
                            "メリット",
                            value=option.get(
                                "pros",
                                "",
                            ),
                            key=(
                                f"edit_option_pros_"
                                f"{option_id}"
                            ),
                        )

                        edit_cons = st.text_area(
                            "デメリット",
                            value=option.get(
                                "cons",
                                "",
                            ),
                            key=(
                                f"edit_option_cons_"
                                f"{option_id}"
                            ),
                        )

                        edit_cost = st.text_area(
                            "コスト",
                            value=option.get(
                                "cost",
                                "",
                            ),
                            key=(
                                f"edit_option_cost_"
                                f"{option_id}"
                            ),
                        )

                        edit_risk = st.text_area(
                            "リスク",
                            value=option.get(
                                "risk",
                                "",
                            ),
                            key=(
                                f"edit_option_risk_"
                                f"{option_id}"
                            ),
                        )

                        edit_score = st.slider(
                            "評価",
                            min_value=1,
                            max_value=5,
                            value=int(
                                option.get(
                                    "score",
                                    3,
                                )
                            ),
                            key=(
                                f"edit_option_score_"
                                f"{option_id}"
                            ),
                        )

                        if st.button(
                            "選択肢を更新",
                            key=(
                                f"save_option_"
                                f"{option_id}"
                            ),
                            use_container_width=True,
                        ):
                            if not edit_name.strip():
                                st.error(
                                    "選択肢名を入力してください。"
                                )

                            else:
                                update_option(
                                    data,
                                    decision_id,
                                    option_id,
                                    {
                                        "name": (
                                            edit_name.strip()
                                        ),
                                        "description": (
                                            edit_description.strip()
                                        ),
                                        "pros": (
                                            edit_pros.strip()
                                        ),
                                        "cons": (
                                            edit_cons.strip()
                                        ),
                                        "cost": (
                                            edit_cost.strip()
                                        ),
                                        "risk": (
                                            edit_risk.strip()
                                        ),
                                        "score": (
                                            edit_score
                                        ),
                                    },
                                )

                                st.rerun()

                    with st.expander(
                        "🗑️ 選択肢を削除"
                    ):
                        confirm_option_delete = (
                            st.checkbox(
                                "削除を確認しました",
                                key=(
                                    f"confirm_option_delete_"
                                    f"{option_id}"
                                ),
                            )
                        )

                        if st.button(
                            "この選択肢を削除",
                            key=(
                                f"delete_option_"
                                f"{option_id}"
                            ),
                            disabled=(
                                not confirm_option_delete
                            ),
                            use_container_width=True,
                        ):
                            delete_option(
                                data,
                                decision_id,
                                option_id,
                            )

                            st.rerun()


# =========================================================
# 最終決断
# =========================================================

with decision_tab:
    st.header(
        "✅ 自分の最終決断"
    )

    if not decisions:
        st.info(
            "決断テーマはまだありません。"
        )

    else:
        final_options = {
            decision.get(
                "title",
                "",
            ): decision["id"]
            for decision in decisions
        }

        selected_final_label = (
            st.selectbox(
                "決断テーマ",
                list(
                    final_options.keys()
                ),
                key="final_decision_select",
            )
        )

        final_decision_data = (
            get_decision_by_id(
                data,
                final_options[
                    selected_final_label
                ],
            )
        )

        final_decision_id = (
            final_decision_data[
                "id"
            ]
        )

        if final_decision_data.get(
            "ai_advice",
            "",
        ):
            st.info(
                "🤖 AIの提案\n\n"
                + final_decision_data.get(
                    "ai_advice",
                    "",
                )
            )

        comparison_columns = (
            st.columns(2)
        )

        with comparison_columns[0]:
            if final_decision_data.get(
                "facts",
                "",
            ):
                st.write(
                    "**現実・事実**"
                )

                st.write(
                    final_decision_data.get(
                        "facts",
                        "",
                    )
                )

        with comparison_columns[1]:
            if final_decision_data.get(
                "feelings",
                "",
            ):
                st.write(
                    "**自分の気持ち**"
                )

                st.write(
                    final_decision_data.get(
                        "feelings",
                        "",
                    )
                )

        available_options = (
            final_decision_data.get(
                "options",
                [],
            )
        )

        option_names = {
            "選択肢を指定しない": ""
        }

        for option in available_options:
            option_names[
                (
                    f"{option.get('name', '')}"
                    f"｜評価 {option.get('score', 3)}/5"
                )
            ] = option[
                "id"
            ]

        current_option_id = (
            final_decision_data.get(
                "selected_option_id",
                "",
            )
        )

        option_labels = list(
            option_names.keys()
        )

        current_label = next(
            (
                label
                for label, option_id
                in option_names.items()
                if option_id
                == current_option_id
            ),
            "選択肢を指定しない",
        )

        with st.form(
            f"final_decision_form_{final_decision_id}",
        ):
            selected_option_label = (
                st.selectbox(
                    "選んだ選択肢",
                    option_labels,
                    index=(
                        option_labels.index(
                            current_label
                        )
                    ),
                )
            )

            final_decision_text = (
                st.text_area(
                    "自分の最終決断",
                    value=(
                        final_decision_data.get(
                            "final_decision",
                            "",
                        )
                    ),
                    placeholder=(
                        "例：AI Router βを小さく進める"
                    ),
                    height=110,
                )
            )

            decision_reason = (
                st.text_area(
                    "決めた理由",
                    value=(
                        final_decision_data.get(
                            "decision_reason",
                            "",
                        )
                    ),
                    placeholder=(
                        "AIの意見ではなく、自分が納得した理由"
                    ),
                    height=120,
                )
            )

            first_step = st.text_area(
                "最初の一歩",
                value=(
                    final_decision_data.get(
                        "first_step",
                        "",
                    )
                ),
                placeholder=(
                    "決断後、最初に行う具体的な行動"
                ),
                height=100,
            )

            current_decided_date = (
                parse_date(
                    final_decision_data.get(
                        "decided_date",
                        "",
                    )
                )
            )

            decided_date_input = (
                st.date_input(
                    "決断日",
                    value=(
                        current_decided_date
                        or date.today()
                    ),
                    max_value=date.today(),
                )
            )

            final_submit = (
                st.form_submit_button(
                    "✅ 最終決断を保存",
                    use_container_width=True,
                )
            )

            if final_submit:
                if not final_decision_text.strip():
                    st.error(
                        "最終決断を入力してください。"
                    )

                elif not decision_reason.strip():
                    st.error(
                        "決めた理由を入力してください。"
                    )

                else:
                    update_decision(
                        data,
                        final_decision_id,
                        {
                            "selected_option_id": (
                                option_names[
                                    selected_option_label
                                ]
                            ),
                            "final_decision": (
                                final_decision_text.strip()
                            ),
                            "decision_reason": (
                                decision_reason.strip()
                            ),
                            "first_step": (
                                first_step.strip()
                            ),
                            "decided_date": str(
                                decided_date_input
                            ),
                            "status": (
                                "決断済み"
                            ),
                        },
                    )

                    st.success(
                        "自分の決断を保存しました！"
                    )

                    st.balloons()
                    st.rerun()

        st.divider()

        st.subheader(
            "🚀 実行状況"
        )

        execution_progress = (
            st.slider(
                "実行進捗",
                min_value=0,
                max_value=100,
                value=int(
                    final_decision_data.get(
                        "execution_progress",
                        0,
                    )
                ),
                step=5,
            )
        )

        execution_memo = st.text_area(
            "実行メモ",
            value=(
                final_decision_data.get(
                    "execution_memo",
                    "",
                )
            ),
            placeholder=(
                "実際に進めたこと、止まっている理由など"
            ),
            height=110,
        )

        if st.button(
            "実行状況を保存",
            use_container_width=True,
        ):
            next_status = (
                final_decision_data.get(
                    "status",
                    "決断済み",
                )
            )

            if execution_progress >= 100:
                next_status = "完了"

            elif execution_progress > 0:
                next_status = "実行中"

            update_decision(
                data,
                final_decision_id,
                {
                    "execution_progress": (
                        execution_progress
                    ),
                    "execution_memo": (
                        execution_memo.strip()
                    ),
                    "status": next_status,
                },
            )

            st.rerun()


# =========================================================
# 決断一覧
# =========================================================

with list_tab:
    st.header(
        "📚 決断一覧"
    )

    if not decisions:
        st.info(
            "決断テーマはまだありません。"
        )

    else:
        filter_columns = (
            st.columns(3)
        )

        with filter_columns[0]:
            keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "テーマ・背景・決断内容"
                ),
            )

        with filter_columns[1]:
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて"
                    ]
                    + STATUSES,
                )
            )

        with filter_columns[2]:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES,
                )
            )

        weight_filter = st.multiselect(
            "決断の重み",
            WEIGHTS,
            default=WEIGHTS,
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "登録が新しい順",
                "優先度順",
                "期限が近い順",
                "決断の重い順",
                "実行進捗が高い順",
            ],
        )

        filtered_decisions = list(
            decisions,
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_decisions = [
                decision
                for decision
                in filtered_decisions
                if (
                    search_word
                    in decision.get(
                        "title",
                        "",
                    ).lower()
                    or search_word
                    in decision.get(
                        "background",
                        "",
                    ).lower()
                    or search_word
                    in decision.get(
                        "final_decision",
                        "",
                    ).lower()
                    or search_word
                    in decision.get(
                        "ai_advice",
                        "",
                    ).lower()
                )
            ]

        if status_filter != "すべて":
            filtered_decisions = [
                decision
                for decision
                in filtered_decisions
                if decision.get(
                    "status",
                )
                == status_filter
            ]

        if category_filter != "すべて":
            filtered_decisions = [
                decision
                for decision
                in filtered_decisions
                if decision.get(
                    "category",
                )
                == category_filter
            ]

        filtered_decisions = [
            decision
            for decision
            in filtered_decisions
            if decision.get(
                "weight",
                "普通",
            )
            in weight_filter
        ]

        if sort_option == "登録が新しい順":
            filtered_decisions.sort(
                key=lambda decision: (
                    decision.get(
                        "registered_date",
                        "",
                    ),
                    decision.get(
                        "created_at",
                        "",
                    ),
                ),
                reverse=True,
            )

        elif sort_option == "優先度順":
            filtered_decisions.sort(
                key=lambda decision: (
                    PRIORITY_ORDER.get(
                        decision.get(
                            "priority",
                            "中",
                        ),
                        99,
                    )
                )
            )

        elif sort_option == "期限が近い順":
            filtered_decisions.sort(
                key=lambda decision: (
                    parse_date(
                        decision.get(
                            "deadline",
                            "",
                        )
                    )
                    or date.max
                )
            )

        elif sort_option == "決断の重い順":
            filtered_decisions.sort(
                key=lambda decision: (
                    WEIGHT_VALUES.get(
                        decision.get(
                            "weight",
                            "普通",
                        ),
                        2,
                    )
                ),
                reverse=True,
            )

        elif sort_option == "実行進捗が高い順":
            filtered_decisions.sort(
                key=lambda decision: int(
                    decision.get(
                        "execution_progress",
                        0,
                    )
                ),
                reverse=True,
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_decisions)}件**"
        )

        for decision in filtered_decisions:
            decision_id = decision[
                "id"
            ]

            with st.container(
                border=True,
            ):
                title_column, status_column = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                with title_column:
                    st.markdown(
                        f"### "
                        f"{PRIORITY_ICONS.get(decision.get('priority', ''), '')} "
                        f"{decision.get('title', '')}"
                    )

                    st.caption(
                        f"{decision.get('category', '')} ／ "
                        f"{WEIGHT_ICONS.get(decision.get('weight', ''), '')} "
                        f"{decision.get('weight', '')}"
                    )

                with status_column:
                    current_status = (
                        decision.get(
                            "status",
                            "検討前",
                        )
                    )

                    st.metric(
                        "状態",
                        f"{STATUS_ICONS.get(current_status, '')} "
                        f"{current_status}",
                    )

                st.write(
                    decision.get(
                        "background",
                        "",
                    )
                )

                if is_overdue(
                    decision,
                ):
                    st.error(
                        f"決断期限を"
                        f"{-deadline_days(decision)}日"
                        f"過ぎています。"
                    )

                elif deadline_days(
                    decision,
                ) is not None:
                    st.caption(
                        f"決断期限："
                        f"{format_date(decision.get('deadline', ''))}"
                    )

                if decision.get(
                    "ai_advice",
                    "",
                ):
                    st.info(
                        "🤖 AIの提案\n\n"
                        + decision.get(
                            "ai_advice",
                            "",
                        )
                    )

                if decision.get(
                    "final_decision",
                    "",
                ):
                    st.success(
                        "✅ 自分の決断\n\n"
                        + decision.get(
                            "final_decision",
                            "",
                        )
                    )

                    st.write(
                        f"**決めた理由**\n\n"
                        f"{decision.get('decision_reason', '')}"
                    )

                selected_name = (
                    selected_option_name(
                        decision,
                    )
                )

                if selected_name:
                    st.caption(
                        f"選択した案："
                        f"{selected_name}"
                    )

                if int(
                    decision.get(
                        "execution_progress",
                        0,
                    )
                ) > 0:
                    st.progress(
                        int(
                            decision.get(
                                "execution_progress",
                                0,
                            )
                        )
                        / 100
                    )

                    st.caption(
                        f"実行進捗："
                        f"{decision.get('execution_progress', 0)}%"
                    )

                with st.expander(
                    "✏️ 基本情報を編集"
                ):
                    edit_title = st.text_input(
                        "決断テーマ",
                        value=decision.get(
                            "title",
                            "",
                        ),
                        key=(
                            f"edit_title_"
                            f"{decision_id}"
                        ),
                    )

                    edit_columns = (
                        st.columns(2)
                    )

                    with edit_columns[0]:
                        current_category = (
                            decision.get(
                                "category",
                                "その他",
                            )
                        )

                        edit_category = (
                            st.selectbox(
                                "カテゴリー",
                                CATEGORIES,
                                index=(
                                    CATEGORIES.index(
                                        current_category
                                    )
                                    if current_category
                                    in CATEGORIES
                                    else (
                                        len(CATEGORIES)
                                        - 1
                                    )
                                ),
                                key=(
                                    f"edit_category_"
                                    f"{decision_id}"
                                ),
                            )
                        )

                        current_weight = (
                            decision.get(
                                "weight",
                                "普通",
                            )
                        )

                        edit_weight = st.selectbox(
                            "決断の重み",
                            WEIGHTS,
                            index=(
                                WEIGHTS.index(
                                    current_weight
                                )
                                if current_weight
                                in WEIGHTS
                                else 1
                            ),
                            key=(
                                f"edit_weight_"
                                f"{decision_id}"
                            ),
                        )

                        current_priority = (
                            decision.get(
                                "priority",
                                "中",
                            )
                        )

                        edit_priority = (
                            st.selectbox(
                                "優先度",
                                PRIORITIES,
                                index=(
                                    PRIORITIES.index(
                                        current_priority
                                    )
                                    if current_priority
                                    in PRIORITIES
                                    else 2
                                ),
                                key=(
                                    f"edit_priority_"
                                    f"{decision_id}"
                                ),
                            )
                        )

                    with edit_columns[1]:
                        current_status = (
                            decision.get(
                                "status",
                                "検討前",
                            )
                        )

                        edit_status = st.selectbox(
                            "状態",
                            STATUSES,
                            index=(
                                STATUSES.index(
                                    current_status
                                )
                                if current_status
                                in STATUSES
                                else 0
                            ),
                            key=(
                                f"edit_status_"
                                f"{decision_id}"
                            ),
                        )

                        deadline_value = parse_date(
                            decision.get(
                                "deadline",
                                "",
                            )
                        )

                        has_deadline = st.checkbox(
                            "期限を設定",
                            value=bool(
                                deadline_value
                            ),
                            key=(
                                f"edit_has_deadline_"
                                f"{decision_id}"
                            ),
                        )

                        edit_deadline = ""

                        if has_deadline:
                            edit_deadline = str(
                                st.date_input(
                                    "決断期限",
                                    value=(
                                        deadline_value
                                        or date.today()
                                    ),
                                    key=(
                                        f"edit_deadline_"
                                        f"{decision_id}"
                                    ),
                                )
                            )

                    edit_background = (
                        st.text_area(
                            "背景",
                            value=decision.get(
                                "background",
                                "",
                            ),
                            key=(
                                f"edit_background_"
                                f"{decision_id}"
                            ),
                        )
                    )

                    edit_conditions = (
                        st.text_area(
                            "重要条件",
                            value=decision.get(
                                "important_conditions",
                                "",
                            ),
                            key=(
                                f"edit_conditions_"
                                f"{decision_id}"
                            ),
                        )
                    )

                    edit_worries = st.text_area(
                        "不安",
                        value=decision.get(
                            "worries",
                            "",
                        ),
                        key=(
                            f"edit_worries_"
                            f"{decision_id}"
                        ),
                    )

                    edit_facts = st.text_area(
                        "現実・事実",
                        value=decision.get(
                            "facts",
                            "",
                        ),
                        key=(
                            f"edit_facts_"
                            f"{decision_id}"
                        ),
                    )

                    edit_feelings = (
                        st.text_area(
                            "自分の気持ち",
                            value=decision.get(
                                "feelings",
                                "",
                            ),
                            key=(
                                f"edit_feelings_"
                                f"{decision_id}"
                            ),
                        )
                    )

                    edit_ai_advice = (
                        st.text_area(
                            "AIの提案",
                            value=decision.get(
                                "ai_advice",
                                "",
                            ),
                            key=(
                                f"edit_ai_advice_"
                                f"{decision_id}"
                            ),
                        )
                    )

                    if st.button(
                        "基本情報を保存",
                        key=(
                            f"save_decision_"
                            f"{decision_id}"
                        ),
                        use_container_width=True,
                    ):
                        if not edit_title.strip():
                            st.error(
                                "決断テーマを入力してください。"
                            )

                        else:
                            update_decision(
                                data,
                                decision_id,
                                {
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "weight": (
                                        edit_weight
                                    ),
                                    "priority": (
                                        edit_priority
                                    ),
                                    "status": (
                                        edit_status
                                    ),
                                    "deadline": (
                                        edit_deadline
                                    ),
                                    "background": (
                                        edit_background.strip()
                                    ),
                                    "important_conditions": (
                                        edit_conditions.strip()
                                    ),
                                    "worries": (
                                        edit_worries.strip()
                                    ),
                                    "facts": (
                                        edit_facts.strip()
                                    ),
                                    "feelings": (
                                        edit_feelings.strip()
                                    ),
                                    "ai_advice": (
                                        edit_ai_advice.strip()
                                    ),
                                },
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 削除"
                ):
                    confirm_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_delete_"
                                f"{decision_id}"
                            ),
                        )
                    )

                    if st.button(
                        "この決断記録を削除",
                        key=(
                            f"delete_decision_"
                            f"{decision_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True,
                    ):
                        delete_decision(
                            data,
                            decision_id,
                        )

                        st.rerun()


# =========================================================
# 結果の振り返り
# =========================================================

with review_tab:
    st.header(
        "🔍 決断結果の振り返り"
    )

    reviewable_decisions = [
        decision
        for decision in decisions
        if decision.get(
            "final_decision",
            "",
        ).strip()
    ]

    if not reviewable_decisions:
        st.info(
            "最終決断を保存すると振り返りできます。"
        )

    else:
        review_options = {
            decision.get(
                "title",
                "",
            ): decision["id"]
            for decision
            in reviewable_decisions
        }

        selected_review_label = (
            st.selectbox(
                "振り返る決断",
                list(
                    review_options.keys()
                ),
            )
        )

        review_decision = (
            get_decision_by_id(
                data,
                review_options[
                    selected_review_label
                ],
            )
        )

        review_decision_id = (
            review_decision["id"]
        )

        st.success(
            "当時の決断\n\n"
            + review_decision.get(
                "final_decision",
                "",
            )
        )

        st.write(
            f"**決めた理由**\n\n"
            f"{review_decision.get('decision_reason', '')}"
        )

        current_result = (
            review_decision.get(
                "review_result",
                "未評価",
            )
        )

        with st.form(
            f"review_form_{review_decision_id}",
        ):
            review_result = (
                st.selectbox(
                    "決断の評価",
                    REVIEW_RESULTS,
                    index=(
                        REVIEW_RESULTS.index(
                            current_result
                        )
                        if current_result
                        in REVIEW_RESULTS
                        else 0
                    ),
                )
            )

            satisfaction = st.slider(
                "決断への満足度",
                min_value=1,
                max_value=5,
                value=(
                    int(
                        review_decision.get(
                            "satisfaction",
                            0,
                        )
                    )
                    or 3
                ),
            )

            result_detail = st.text_area(
                "実際の結果",
                value=review_decision.get(
                    "result_detail",
                    "",
                ),
                placeholder=(
                    "決断後、何が起きたか"
                ),
                height=120,
            )

            unexpected_result = (
                st.text_area(
                    "予想と違ったこと",
                    value=(
                        review_decision.get(
                            "unexpected_result",
                            "",
                        )
                    ),
                    placeholder=(
                        "事前には分からなかったこと"
                    ),
                    height=100,
                )
            )

            next_learning = st.text_area(
                "次回の決断に生かす学び",
                value=review_decision.get(
                    "next_learning",
                    "",
                ),
                placeholder=(
                    "次はどのような情報や考え方を重視するか"
                ),
                height=120,
            )

            review_submit = (
                st.form_submit_button(
                    "振り返りを保存",
                    use_container_width=True,
                )
            )

            if review_submit:
                update_decision(
                    data,
                    review_decision_id,
                    {
                        "review_result": (
                            review_result
                        ),
                        "satisfaction": (
                            satisfaction
                        ),
                        "result_detail": (
                            result_detail.strip()
                        ),
                        "unexpected_result": (
                            unexpected_result.strip()
                        ),
                        "next_learning": (
                            next_learning.strip()
                        ),
                    },
                )

                st.success(
                    "振り返りを保存しました！"
                )

                st.rerun()


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 決断分析"
    )

    if not decisions:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for decision in decisions:
            analysis_rows.append(
                {
                    "テーマ": decision.get(
                        "title",
                        "",
                    ),
                    "カテゴリー": (
                        decision.get(
                            "category",
                            "",
                        )
                    ),
                    "状態": decision.get(
                        "status",
                        "",
                    ),
                    "重み": decision.get(
                        "weight",
                        "",
                    ),
                    "重み数値": (
                        WEIGHT_VALUES.get(
                            decision.get(
                                "weight",
                                "普通",
                            ),
                            2,
                        )
                    ),
                    "選択肢数": len(
                        decision.get(
                            "options",
                            [],
                        )
                    ),
                    "実行進捗": int(
                        decision.get(
                            "execution_progress",
                            0,
                        )
                    ),
                    "満足度": int(
                        decision.get(
                            "satisfaction",
                            0,
                        )
                    ),
                    "決断日数": (
                        decision_days(
                            decision
                        )
                    ),
                    "振り返り結果": (
                        decision.get(
                            "review_result",
                            "未評価",
                        )
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows,
        )

        st.subheader(
            "状態別"
        )

        status_summary = (
            analysis_df.groupby(
                "状態",
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False,
            )
        )

        st.bar_chart(
            status_summary.set_index(
                "状態"
            )[["件数"]]
        )

        st.dataframe(
            status_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "カテゴリー別"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False,
            )
            .agg(
                決断数=(
                    "テーマ",
                    "count",
                ),
                平均実行進捗=(
                    "実行進捗",
                    "mean",
                ),
            )
            .sort_values(
                "決断数",
                ascending=False,
            )
        )

        category_summary[
            "平均実行進捗"
        ] = category_summary[
            "平均実行進捗"
        ].round(
            1
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["決断数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "決断の重み別"
        )

        weight_summary = (
            analysis_df.groupby(
                [
                    "重み",
                    "重み数値",
                ],
                as_index=False,
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "重み数値"
            )
        )

        st.bar_chart(
            weight_summary.set_index(
                "重み"
            )[["件数"]]
        )

        st.dataframe(
            weight_summary[
                [
                    "重み",
                    "件数",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader(
            "決断までの日数"
        )

        decided_days_df = (
            analysis_df.dropna(
                subset=[
                    "決断日数"
                ]
            )
            .sort_values(
                "決断日数"
            )
        )

        if decided_days_df.empty:
            st.info(
                "決断日数を計算できる記録がありません。"
            )

        else:
            st.metric(
                "平均決断日数",
                f"{decided_days_df['決断日数'].mean():.1f}日",
            )

            st.dataframe(
                decided_days_df[
                    [
                        "テーマ",
                        "カテゴリー",
                        "決断日数",
                        "重み",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "振り返り結果"
        )

        reviewed_df = analysis_df[
            analysis_df[
                "振り返り結果"
            ]
            != "未評価"
        ]

        if reviewed_df.empty:
            st.info(
                "振り返り済みの決断はありません。"
            )

        else:
            result_summary = (
                reviewed_df.groupby(
                    "振り返り結果",
                    as_index=False,
                )
                .size()
                .rename(
                    columns={
                        "size": "件数"
                    }
                )
                .sort_values(
                    "件数",
                    ascending=False,
                )
            )

            st.bar_chart(
                result_summary.set_index(
                    "振り返り結果"
                )[["件数"]]
            )

            st.dataframe(
                result_summary,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "満足度の高い決断"
        )

        satisfaction_df = analysis_df[
            analysis_df[
                "満足度"
            ]
            > 0
        ].sort_values(
            "満足度",
            ascending=False,
        )

        if satisfaction_df.empty:
            st.info(
                "満足度が記録された決断はありません。"
            )

        else:
            st.dataframe(
                satisfaction_df[
                    [
                        "テーマ",
                        "カテゴリー",
                        "満足度",
                        "振り返り結果",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        st.subheader(
            "よく迷うカテゴリー"
        )

        category_counter = Counter(
            decision.get(
                "category",
                "その他",
            )
            for decision in decisions
        )

        if category_counter:
            top_category, top_count = (
                category_counter.most_common(
                    1
                )[0]
            )

            st.metric(
                "最多カテゴリー",
                top_category,
                f"{top_count}件",
            )


# =========================================================
# データ管理
# =========================================================

with data_tab:
    st.header(
        "💾 データ管理"
    )

    st.subheader(
        "JSONバックアップ"
    )

    json_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"decision_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.divider()

    st.subheader(
        "JSONデータの復元"
    )

    uploaded_file = (
        st.file_uploader(
            "バックアップJSONを選択",
            type=[
                "json"
            ],
        )
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file,
            )

            if (
                not isinstance(
                    imported_data,
                    dict,
                )
                or "decisions"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "decisions"
                    ],
                    list,
                )
            ):
                st.error(
                    "対応していないJSON形式です。"
                )

            else:
                imported_data = (
                    normalize_data(
                        imported_data
                    )
                )

                st.warning(
                    "復元すると現在のデータが上書きされます。"
                )

                confirm_restore = (
                    st.checkbox(
                        "上書き復元を確認しました"
                    )
                )

                if st.button(
                    "JSONから復元",
                    disabled=(
                        not confirm_restore
                    ),
                    use_container_width=True,
                ):
                    save_data(
                        imported_data,
                    )

                    st.success(
                        "データを復元しました！"
                    )

                    st.rerun()

        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "決断テーマ・選択肢・振り返りがすべて削除されます。"
    )

    confirm_delete_all = (
        st.checkbox(
            "全データ削除を確認しました"
        )
    )

    if st.button(
        "すべて削除",
        disabled=(
            not confirm_delete_all
        ),
        use_container_width=True,
    ):
        save_data(
            create_empty_data(),
        )

        st.success(
            "すべてのデータを削除しました。"
        )

        st.rerun()


# =========================================================
# フッター
# =========================================================

st.divider()

st.success(
    "AIは答えを押しつける存在ではなく、自分で決めるための相談相手。🧠"
)
