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
    page_title="失敗・改善ノート",
    page_icon="🛠️",
    layout="wide"
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "failure_data.json"
)

CATEGORIES = [
    "仕事",
    "アプリ開発",
    "勉強",
    "健康",
    "運動",
    "食事",
    "お金",
    "人間関係",
    "家族",
    "生活習慣",
    "メンタル",
    "その他",
]

STATUSES = [
    "未整理",
    "原因分析中",
    "改善策決定",
    "再挑戦中",
    "解決",
    "保留",
]

STATUS_ICONS = {
    "未整理": "⚪",
    "原因分析中": "🔍",
    "改善策決定": "💡",
    "再挑戦中": "🔄",
    "解決": "✅",
    "保留": "⏸️",
}

IMPACT_LEVELS = [
    "軽微",
    "小",
    "中",
    "大",
    "重大",
]

IMPACT_VALUES = {
    "軽微": 1,
    "小": 2,
    "中": 3,
    "大": 4,
    "重大": 5,
}

IMPACT_ICONS = {
    "軽微": "🟢",
    "小": "🔵",
    "中": "🟡",
    "大": "🟠",
    "重大": "🔴",
}

CAUSE_TYPES = [
    "自分の行動",
    "環境",
    "知識不足",
    "準備不足",
    "時間不足",
    "確認不足",
    "コミュニケーション不足",
    "体調",
    "外部要因",
    "その他",
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

RESULT_TYPES = [
    "未評価",
    "失敗",
    "一部改善",
    "成功",
    "完全解決",
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    """一意のIDを作成する。"""

    return str(uuid.uuid4())


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    """空のデータを作成する。"""

    return {
        "failures": []
    }


def save_data(data):
    """JSONファイルへ保存する。"""

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


def normalize_data(data):
    """古いデータにも不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "failures",
        []
    )

    for failure in data["failures"]:
        failure.setdefault(
            "id",
            create_id()
        )

        failure.setdefault(
            "title",
            ""
        )

        failure.setdefault(
            "occurred_date",
            str(date.today())
        )

        failure.setdefault(
            "category",
            "その他"
        )

        failure.setdefault(
            "status",
            "未整理"
        )

        failure.setdefault(
            "impact",
            "中"
        )

        failure.setdefault(
            "priority",
            "中"
        )

        failure.setdefault(
            "what_happened",
            ""
        )

        failure.setdefault(
            "why_problem",
            ""
        )

        failure.setdefault(
            "cause_types",
            []
        )

        failure.setdefault(
            "root_cause",
            ""
        )

        failure.setdefault(
            "improvement_plan",
            ""
        )

        failure.setdefault(
            "prevention_rule",
            ""
        )

        failure.setdefault(
            "learning",
            ""
        )

        failure.setdefault(
            "retry_date",
            ""
        )

        failure.setdefault(
            "resolved_date",
            ""
        )

        failure.setdefault(
            "recurrence_count",
            0
        )

        failure.setdefault(
            "memo",
            ""
        )

        failure.setdefault(
            "retry_logs",
            []
        )

        failure.setdefault(
            "created_at",
            ""
        )

        failure.setdefault(
            "updated_at",
            ""
        )

        for log in failure["retry_logs"]:
            log.setdefault(
                "id",
                create_id()
            )

            log.setdefault(
                "retry_date",
                str(date.today())
            )

            log.setdefault(
                "improvement_tried",
                ""
            )

            log.setdefault(
                "result",
                ""
            )

            log.setdefault(
                "result_type",
                "未評価"
            )

            log.setdefault(
                "next_improvement",
                ""
            )

            log.setdefault(
                "effect_score",
                3
            )

            log.setdefault(
                "created_at",
                ""
            )

    return data


def load_data():
    """JSONファイルから読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
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
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        data = normalize_data(data)
        save_data(data)

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        broken_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(
                DATA_FILE
            ):
                os.replace(
                    DATA_FILE,
                    broken_file
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
            "%Y-%m-%d"
        ).date()

    except (
        TypeError,
        ValueError
    ):
        return None


def format_date(date_text):
    """日付を日本語表示する。"""

    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "未設定"

    return parsed.strftime(
        "%Y年%m月%d日"
    )


def get_failure_by_id(
    data,
    failure_id
):
    """IDから失敗データを取得する。"""

    for failure in data["failures"]:
        if (
            failure.get("id")
            == failure_id
        ):
            return failure

    return None


def retry_count(failure):
    """再挑戦回数を返す。"""

    return len(
        failure.get(
            "retry_logs",
            []
        )
    )


def average_effect_score(failure):
    """再挑戦ログの平均効果を返す。"""

    logs = failure.get(
        "retry_logs",
        []
    )

    if not logs:
        return 0

    scores = [
        int(
            log.get(
                "effect_score",
                0
            )
        )
        for log in logs
        if int(
            log.get(
                "effect_score",
                0
            )
        ) > 0
    ]

    if not scores:
        return 0

    return (
        sum(scores)
        / len(scores)
    )


def days_to_resolve(failure):
    """発生から解決までの日数を計算する。"""

    occurred = parse_date(
        failure.get(
            "occurred_date",
            ""
        )
    )

    resolved = parse_date(
        failure.get(
            "resolved_date",
            ""
        )
    )

    if not occurred or not resolved:
        return None

    return (
        resolved
        - occurred
    ).days


def days_until_retry(failure):
    """再挑戦予定日までの日数を返す。"""

    retry_date = parse_date(
        failure.get(
            "retry_date",
            ""
        )
    )

    if not retry_date:
        return None

    return (
        retry_date
        - date.today()
    ).days


def update_status_automatically(
    failure
):
    """内容に応じて状態を補助的に更新する。"""

    current_status = failure.get(
        "status",
        "未整理"
    )

    if current_status in [
        "解決",
        "保留",
    ]:
        return

    if failure.get(
        "retry_logs",
        []
    ):
        failure["status"] = (
            "再挑戦中"
        )

    elif failure.get(
        "improvement_plan",
        ""
    ).strip():
        failure["status"] = (
            "改善策決定"
        )

    elif failure.get(
        "root_cause",
        ""
    ).strip():
        failure["status"] = (
            "原因分析中"
        )


# =========================================================
# データ操作
# =========================================================

def add_failure(
    data,
    values
):
    """失敗データを登録する。"""

    failure = {
        "id": create_id(),
        "title": values["title"],
        "occurred_date": (
            values["occurred_date"]
        ),
        "category": values["category"],
        "status": values["status"],
        "impact": values["impact"],
        "priority": values["priority"],
        "what_happened": (
            values["what_happened"]
        ),
        "why_problem": (
            values["why_problem"]
        ),
        "cause_types": (
            values["cause_types"]
        ),
        "root_cause": (
            values["root_cause"]
        ),
        "improvement_plan": (
            values["improvement_plan"]
        ),
        "prevention_rule": (
            values["prevention_rule"]
        ),
        "learning": values["learning"],
        "retry_date": (
            values["retry_date"]
        ),
        "resolved_date": "",
        "recurrence_count": int(
            values["recurrence_count"]
        ),
        "memo": values["memo"],
        "retry_logs": [],
        "created_at": now_text(),
        "updated_at": "",
    }

    update_status_automatically(
        failure
    )

    data["failures"].append(
        failure
    )

    save_data(data)


def update_failure(
    data,
    failure_id,
    values
):
    """失敗データを更新する。"""

    failure = get_failure_by_id(
        data,
        failure_id
    )

    if not failure:
        return

    for key, value in values.items():
        failure[key] = value

    update_status_automatically(
        failure
    )

    failure["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_failure(
    data,
    failure_id
):
    """失敗データを削除する。"""

    data["failures"] = [
        failure
        for failure
        in data["failures"]
        if failure.get("id")
        != failure_id
    ]

    save_data(data)


def add_retry_log(
    data,
    failure_id,
    values
):
    """再挑戦ログを追加する。"""

    failure = get_failure_by_id(
        data,
        failure_id
    )

    if not failure:
        return

    retry_log = {
        "id": create_id(),
        "retry_date": (
            values["retry_date"]
        ),
        "improvement_tried": (
            values["improvement_tried"]
        ),
        "result": values["result"],
        "result_type": (
            values["result_type"]
        ),
        "next_improvement": (
            values["next_improvement"]
        ),
        "effect_score": int(
            values["effect_score"]
        ),
        "created_at": now_text(),
    }

    failure["retry_logs"].append(
        retry_log
    )

    if values["result_type"] == (
        "完全解決"
    ):
        failure["status"] = "解決"
        failure["resolved_date"] = (
            values["retry_date"]
        )

    elif values["result_type"] in [
        "成功",
        "一部改善",
    ]:
        failure["status"] = (
            "再挑戦中"
        )

    else:
        failure["status"] = (
            "再挑戦中"
        )

    failure["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_retry_log(
    data,
    failure_id,
    log_id
):
    """再挑戦ログを削除する。"""

    failure = get_failure_by_id(
        data,
        failure_id
    )

    if not failure:
        return

    failure["retry_logs"] = [
        log
        for log
        in failure.get(
            "retry_logs",
            []
        )
        if log.get("id")
        != log_id
    ]

    failure["updated_at"] = (
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
        background: rgba(255, 140, 60, 0.08);
        border: 1px solid rgba(255, 140, 60, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(255, 140, 60, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(255, 140, 60, 0.18),
                rgba(255, 210, 90, 0.12)
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
    unsafe_allow_html=True
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

failures = data[
    "failures"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🛠️ 失敗・改善ノート</h1>
        <p>
            失敗を責めるのではなく、
            原因・改善・再挑戦・学びへ変えるアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ダッシュボード
# =========================================================

total_count = len(
    failures
)

unresolved_count = len(
    [
        failure
        for failure in failures
        if failure.get("status")
        not in [
            "解決",
            "保留",
        ]
    ]
)

analyzing_count = len(
    [
        failure
        for failure in failures
        if failure.get("status")
        == "原因分析中"
    ]
)

retrying_count = len(
    [
        failure
        for failure in failures
        if failure.get("status")
        == "再挑戦中"
    ]
)

resolved_count = len(
    [
        failure
        for failure in failures
        if failure.get("status")
        == "解決"
    ]
)

total_retry_count = sum(
    retry_count(failure)
    for failure in failures
)

this_month_retry_count = 0

for failure in failures:
    for log in failure.get(
        "retry_logs",
        []
    ):
        log_date = parse_date(
            log.get(
                "retry_date",
                ""
            )
        )

        if (
            log_date
            and log_date.year
            == date.today().year
            and log_date.month
            == date.today().month
        ):
            this_month_retry_count += 1

resolution_rate = (
    resolved_count
    / total_count
    * 100
    if total_count > 0
    else 0
)

total_recurrence_count = sum(
    int(
        failure.get(
            "recurrence_count",
            0
        )
    )
    for failure in failures
)

metric_row1 = st.columns(4)

metric_row1[0].metric(
    "登録した失敗",
    f"{total_count}件"
)

metric_row1[1].metric(
    "未解決",
    f"{unresolved_count}件"
)

metric_row1[2].metric(
    "原因分析中",
    f"{analyzing_count}件"
)

metric_row1[3].metric(
    "再挑戦中",
    f"{retrying_count}件"
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "解決済み",
    f"{resolved_count}件"
)

metric_row2[1].metric(
    "今月の再挑戦",
    f"{this_month_retry_count}回"
)

metric_row2[2].metric(
    "解決率",
    f"{resolution_rate:.1f}%"
)

metric_row2[3].metric(
    "再発回数",
    f"{total_recurrence_count}回"
)


# =========================================================
# 今日の改善候補
# =========================================================

active_failures = [
    failure
    for failure in failures
    if failure.get("status")
    not in [
        "解決",
        "保留",
    ]
]

if active_failures:
    st.divider()

    candidate_column, schedule_column = (
        st.columns(2)
    )

    with candidate_column:
        st.subheader(
            "🎯 今日向き合う失敗"
        )

        sorted_failures = sorted(
            active_failures,
            key=lambda failure: (
                PRIORITY_ORDER.get(
                    failure.get(
                        "priority",
                        "中"
                    ),
                    99
                ),
                -IMPACT_VALUES.get(
                    failure.get(
                        "impact",
                        "中"
                    ),
                    3
                ),
            )
        )

        candidate = sorted_failures[0]

        with st.container(
            border=True
        ):
            st.markdown(
                f"### "
                f"{PRIORITY_ICONS.get(candidate.get('priority', ''), '')} "
                f"{candidate.get('title', '無題')}"
            )

            st.caption(
                f"{candidate.get('category', '')} ／ "
                f"{STATUS_ICONS.get(candidate.get('status', ''), '')} "
                f"{candidate.get('status', '')}"
            )

            st.write(
                candidate.get(
                    "what_happened",
                    ""
                )
            )

            if candidate.get(
                "improvement_plan",
                ""
            ):
                st.success(
                    "改善案\n\n"
                    + candidate.get(
                        "improvement_plan",
                        ""
                    )
                )

            else:
                st.warning(
                    "改善案がまだ登録されていません。"
                )

    with schedule_column:
        st.subheader(
            "📅 再挑戦予定"
        )

        scheduled_failures = [
            failure
            for failure in active_failures
            if failure.get(
                "retry_date",
                ""
            )
        ]

        if not scheduled_failures:
            st.info(
                "再挑戦予定はありません。"
            )

        else:
            scheduled_failures = sorted(
                scheduled_failures,
                key=lambda failure: (
                    parse_date(
                        failure.get(
                            "retry_date",
                            ""
                        )
                    )
                    or date.max
                )
            )

            for failure in scheduled_failures[
                :5
            ]:
                remaining_days = (
                    days_until_retry(
                        failure
                    )
                )

                if remaining_days is None:
                    continue

                if remaining_days < 0:
                    st.error(
                        f"{failure.get('title', '')}："
                        f"{-remaining_days}日超過"
                    )

                elif remaining_days == 0:
                    st.warning(
                        f"{failure.get('title', '')}：本日"
                    )

                else:
                    st.info(
                        f"{failure.get('title', '')}："
                        f"あと{remaining_days}日"
                    )


# =========================================================
# ランダムな学び
# =========================================================

learned_failures = [
    failure
    for failure in failures
    if failure.get(
        "learning",
        ""
    ).strip()
]

if learned_failures:
    st.divider()

    st.subheader(
        "💡 過去の失敗から得た学び"
    )

    if (
        "random_failure_id"
        not in st.session_state
    ):
        st.session_state[
            "random_failure_id"
        ] = random.choice(
            learned_failures
        )["id"]

    random_failure = (
        get_failure_by_id(
            data,
            st.session_state[
                "random_failure_id"
            ]
        )
    )

    if random_failure:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### "
                f"{random_failure.get('title', '無題')}"
            )

            st.info(
                random_failure.get(
                    "learning",
                    ""
                )
            )

            if random_failure.get(
                "prevention_rule",
                ""
            ):
                st.success(
                    "今後のルール\n\n"
                    + random_failure.get(
                        "prevention_rule",
                        ""
                    )
                )

    if st.button(
        "🔄 別の学びを表示"
    ):
        st.session_state[
            "random_failure_id"
        ] = random.choice(
            learned_failures
        )["id"]

        st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    retry_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 失敗を登録",
        "📋 失敗一覧",
        "🔄 再挑戦ログ",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 失敗登録
# =========================================================

with add_tab:
    st.header(
        "➕ 失敗・問題を登録"
    )

    with st.form(
        "add_failure_form",
        clear_on_submit=True
    ):
        column1, column2 = (
            st.columns(2)
        )

        with column1:
            title = st.text_input(
                "タイトル",
                placeholder=(
                    "例：保存前にデータが消えた"
                )
            )

            occurred_date = (
                st.date_input(
                    "発生日",
                    value=date.today()
                )
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES
            )

            impact = st.select_slider(
                "影響度",
                options=IMPACT_LEVELS,
                value="中"
            )

        with column2:
            priority = st.selectbox(
                "改善の優先度",
                PRIORITIES,
                index=2
            )

            status = st.selectbox(
                "状態",
                STATUSES,
                index=0
            )

            recurrence_count = (
                st.number_input(
                    "過去の再発回数",
                    min_value=0,
                    max_value=1000,
                    value=0,
                    step=1
                )
            )

            set_retry_date = (
                st.checkbox(
                    "再挑戦予定日を設定する"
                )
            )

            retry_date = ""

            if set_retry_date:
                retry_date = str(
                    st.date_input(
                        "再挑戦予定日",
                        value=date.today()
                    )
                )

        what_happened = st.text_area(
            "何が起きたか",
            placeholder=(
                "事実をできるだけ具体的に書きます。"
            ),
            height=120
        )

        why_problem = st.text_area(
            "なぜ問題だったか",
            placeholder=(
                "どのような損失や影響があったか"
            ),
            height=100
        )

        cause_types = st.multiselect(
            "原因の種類",
            CAUSE_TYPES
        )

        root_cause = st.text_area(
            "根本原因",
            placeholder=(
                "表面的な原因ではなく、"
                "なぜ起きたかを深掘りします。"
            ),
            height=120
        )

        improvement_plan = st.text_area(
            "改善案",
            placeholder=(
                "次回はどのように変えるか"
            ),
            height=120
        )

        prevention_rule = st.text_area(
            "今後のルール",
            placeholder=(
                "例：10分ごとに保存する"
            ),
            height=100
        )

        learning = st.text_area(
            "この失敗から得た学び",
            placeholder=(
                "失敗を一文の学びに変換します。"
            ),
            height=100
        )

        memo = st.text_area(
            "補足メモ",
            placeholder=(
                "参考情報や背景など"
            ),
            height=80
        )

        submitted = (
            st.form_submit_button(
                "🛠️ 失敗を登録",
                use_container_width=True
            )
        )

        if submitted:
            if not title.strip():
                st.error(
                    "タイトルを入力してください。"
                )

            elif not what_happened.strip():
                st.error(
                    "何が起きたかを入力してください。"
                )

            else:
                add_failure(
                    data,
                    {
                        "title": title.strip(),
                        "occurred_date": str(
                            occurred_date
                        ),
                        "category": category,
                        "status": status,
                        "impact": impact,
                        "priority": priority,
                        "what_happened": (
                            what_happened.strip()
                        ),
                        "why_problem": (
                            why_problem.strip()
                        ),
                        "cause_types": cause_types,
                        "root_cause": (
                            root_cause.strip()
                        ),
                        "improvement_plan": (
                            improvement_plan.strip()
                        ),
                        "prevention_rule": (
                            prevention_rule.strip()
                        ),
                        "learning": (
                            learning.strip()
                        ),
                        "retry_date": retry_date,
                        "recurrence_count": (
                            recurrence_count
                        ),
                        "memo": memo.strip(),
                    }
                )

                st.success(
                    "失敗を登録しました！"
                )

                st.rerun()


# =========================================================
# 失敗一覧
# =========================================================

with list_tab:
    st.header(
        "📋 失敗・改善一覧"
    )

    if not failures:
        st.info(
            "失敗データはまだありません。"
        )

    else:
        filter1, filter2, filter3 = (
            st.columns(3)
        )

        with filter1:
            keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "タイトル・原因・改善案"
                )
            )

        with filter2:
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて"
                    ]
                    + STATUSES
                )
            )

        with filter3:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES
                )
            )

        impact_filter = st.multiselect(
            "影響度",
            IMPACT_LEVELS,
            default=IMPACT_LEVELS
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "登録が新しい順",
                "発生日が新しい順",
                "優先度順",
                "影響度が高い順",
                "再発回数が多い順",
                "再挑戦回数が多い順",
            ]
        )

        filtered_failures = list(
            failures
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_failures = [
                failure
                for failure
                in filtered_failures
                if (
                    search_word
                    in failure.get(
                        "title",
                        ""
                    ).lower()
                    or search_word
                    in failure.get(
                        "what_happened",
                        ""
                    ).lower()
                    or search_word
                    in failure.get(
                        "root_cause",
                        ""
                    ).lower()
                    or search_word
                    in failure.get(
                        "improvement_plan",
                        ""
                    ).lower()
                    or search_word
                    in failure.get(
                        "learning",
                        ""
                    ).lower()
                )
            ]

        if status_filter != "すべて":
            filtered_failures = [
                failure
                for failure
                in filtered_failures
                if failure.get(
                    "status"
                )
                == status_filter
            ]

        if category_filter != "すべて":
            filtered_failures = [
                failure
                for failure
                in filtered_failures
                if failure.get(
                    "category"
                )
                == category_filter
            ]

        filtered_failures = [
            failure
            for failure
            in filtered_failures
            if failure.get(
                "impact",
                "中"
            )
            in impact_filter
        ]

        if sort_option == (
            "登録が新しい順"
        ):
            filtered_failures.sort(
                key=lambda failure: (
                    failure.get(
                        "created_at",
                        ""
                    )
                ),
                reverse=True
            )

        elif sort_option == (
            "発生日が新しい順"
        ):
            filtered_failures.sort(
                key=lambda failure: (
                    parse_date(
                        failure.get(
                            "occurred_date",
                            ""
                        )
                    )
                    or date.min
                ),
                reverse=True
            )

        elif sort_option == (
            "優先度順"
        ):
            filtered_failures.sort(
                key=lambda failure: (
                    PRIORITY_ORDER.get(
                        failure.get(
                            "priority",
                            "中"
                        ),
                        99
                    )
                )
            )

        elif sort_option == (
            "影響度が高い順"
        ):
            filtered_failures.sort(
                key=lambda failure: (
                    IMPACT_VALUES.get(
                        failure.get(
                            "impact",
                            "中"
                        ),
                        3
                    )
                ),
                reverse=True
            )

        elif sort_option == (
            "再発回数が多い順"
        ):
            filtered_failures.sort(
                key=lambda failure: int(
                    failure.get(
                        "recurrence_count",
                        0
                    )
                ),
                reverse=True
            )

        elif sort_option == (
            "再挑戦回数が多い順"
        ):
            filtered_failures.sort(
                key=retry_count,
                reverse=True
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_failures)}件**"
        )

        for failure in filtered_failures:
            failure_id = failure["id"]

            with st.container(
                border=True
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
                        f"{PRIORITY_ICONS.get(failure.get('priority', ''), '')} "
                        f"{failure.get('title', '無題')}"
                    )

                    st.caption(
                        f"{failure.get('category', '')} ／ "
                        f"発生日："
                        f"{format_date(failure.get('occurred_date', ''))}"
                    )

                with status_column:
                    current_status = (
                        failure.get(
                            "status",
                            "未整理"
                        )
                    )

                    st.metric(
                        "状態",
                        f"{STATUS_ICONS.get(current_status, '')} "
                        f"{current_status}"
                    )

                detail_columns = (
                    st.columns(4)
                )

                detail_columns[0].metric(
                    "影響度",
                    f"{IMPACT_ICONS.get(failure.get('impact', ''), '')} "
                    f"{failure.get('impact', '')}"
                )

                detail_columns[1].metric(
                    "再挑戦",
                    f"{retry_count(failure)}回"
                )

                detail_columns[2].metric(
                    "再発",
                    f"{failure.get('recurrence_count', 0)}回"
                )

                average_score = (
                    average_effect_score(
                        failure
                    )
                )

                detail_columns[3].metric(
                    "改善効果",
                    (
                        f"{average_score:.1f}/5"
                        if average_score > 0
                        else "未評価"
                    )
                )

                st.write(
                    "**何が起きたか**"
                )

                st.write(
                    failure.get(
                        "what_happened",
                        ""
                    )
                )

                if failure.get(
                    "why_problem",
                    ""
                ):
                    st.write(
                        "**なぜ問題だったか**"
                    )

                    st.write(
                        failure.get(
                            "why_problem",
                            ""
                        )
                    )

                if failure.get(
                    "cause_types",
                    []
                ):
                    st.write(
                        "**原因の種類**"
                    )

                    st.write(
                        "・".join(
                            failure.get(
                                "cause_types",
                                []
                            )
                        )
                    )

                if failure.get(
                    "root_cause",
                    ""
                ):
                    st.warning(
                        "🔍 根本原因\n\n"
                        + failure.get(
                            "root_cause",
                            ""
                        )
                    )

                if failure.get(
                    "improvement_plan",
                    ""
                ):
                    st.success(
                        "🛠️ 改善案\n\n"
                        + failure.get(
                            "improvement_plan",
                            ""
                        )
                    )

                if failure.get(
                    "prevention_rule",
                    ""
                ):
                    st.info(
                        "📌 今後のルール\n\n"
                        + failure.get(
                            "prevention_rule",
                            ""
                        )
                    )

                if failure.get(
                    "learning",
                    ""
                ):
                    st.info(
                        "💡 学び\n\n"
                        + failure.get(
                            "learning",
                            ""
                        )
                    )

                resolution_days = (
                    days_to_resolve(
                        failure
                    )
                )

                if resolution_days is not None:
                    st.caption(
                        f"解決までの日数："
                        f"{resolution_days}日"
                    )

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = (
                        st.text_input(
                            "タイトル",
                            value=failure.get(
                                "title",
                                ""
                            ),
                            key=(
                                f"edit_title_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_occurred_date = (
                        st.date_input(
                            "発生日",
                            value=(
                                parse_date(
                                    failure.get(
                                        "occurred_date",
                                        ""
                                    )
                                )
                                or date.today()
                            ),
                            key=(
                                f"edit_occurred_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_column1, edit_column2 = (
                        st.columns(2)
                    )

                    with edit_column1:
                        current_category = (
                            failure.get(
                                "category",
                                "その他"
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
                                    f"{failure_id}"
                                )
                            )
                        )

                        current_impact = (
                            failure.get(
                                "impact",
                                "中"
                            )
                        )

                        edit_impact = (
                            st.selectbox(
                                "影響度",
                                IMPACT_LEVELS,
                                index=(
                                    IMPACT_LEVELS.index(
                                        current_impact
                                    )
                                    if current_impact
                                    in IMPACT_LEVELS
                                    else 2
                                ),
                                key=(
                                    f"edit_impact_"
                                    f"{failure_id}"
                                )
                            )
                        )

                        current_priority = (
                            failure.get(
                                "priority",
                                "中"
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
                                    f"{failure_id}"
                                )
                            )
                        )

                    with edit_column2:
                        current_status = (
                            failure.get(
                                "status",
                                "未整理"
                            )
                        )

                        edit_status = (
                            st.selectbox(
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
                                    f"{failure_id}"
                                )
                            )
                        )

                        edit_recurrence = (
                            st.number_input(
                                "再発回数",
                                min_value=0,
                                max_value=1000,
                                value=int(
                                    failure.get(
                                        "recurrence_count",
                                        0
                                    )
                                ),
                                key=(
                                    f"edit_recurrence_"
                                    f"{failure_id}"
                                )
                            )
                        )

                    edit_what_happened = (
                        st.text_area(
                            "何が起きたか",
                            value=failure.get(
                                "what_happened",
                                ""
                            ),
                            key=(
                                f"edit_happened_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_why_problem = (
                        st.text_area(
                            "なぜ問題だったか",
                            value=failure.get(
                                "why_problem",
                                ""
                            ),
                            key=(
                                f"edit_problem_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_cause_types = (
                        st.multiselect(
                            "原因の種類",
                            CAUSE_TYPES,
                            default=[
                                cause
                                for cause
                                in failure.get(
                                    "cause_types",
                                    []
                                )
                                if cause
                                in CAUSE_TYPES
                            ],
                            key=(
                                f"edit_causes_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_root_cause = (
                        st.text_area(
                            "根本原因",
                            value=failure.get(
                                "root_cause",
                                ""
                            ),
                            key=(
                                f"edit_root_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_improvement = (
                        st.text_area(
                            "改善案",
                            value=failure.get(
                                "improvement_plan",
                                ""
                            ),
                            key=(
                                f"edit_improvement_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_rule = (
                        st.text_area(
                            "今後のルール",
                            value=failure.get(
                                "prevention_rule",
                                ""
                            ),
                            key=(
                                f"edit_rule_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_learning = (
                        st.text_area(
                            "学び",
                            value=failure.get(
                                "learning",
                                ""
                            ),
                            key=(
                                f"edit_learning_"
                                f"{failure_id}"
                            )
                        )
                    )

                    has_retry_date = (
                        st.checkbox(
                            "再挑戦予定日を設定",
                            value=bool(
                                parse_date(
                                    failure.get(
                                        "retry_date",
                                        ""
                                    )
                                )
                            ),
                            key=(
                                f"edit_has_retry_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_retry_date = ""

                    if has_retry_date:
                        edit_retry_date = str(
                            st.date_input(
                                "再挑戦予定日",
                                value=(
                                    parse_date(
                                        failure.get(
                                            "retry_date",
                                            ""
                                        )
                                    )
                                    or date.today()
                                ),
                                key=(
                                    f"edit_retry_date_"
                                    f"{failure_id}"
                                )
                            )
                        )

                    has_resolved_date = (
                        st.checkbox(
                            "解決日を設定",
                            value=bool(
                                parse_date(
                                    failure.get(
                                        "resolved_date",
                                        ""
                                    )
                                )
                            ),
                            key=(
                                f"edit_has_resolved_"
                                f"{failure_id}"
                            )
                        )
                    )

                    edit_resolved_date = ""

                    if has_resolved_date:
                        edit_resolved_date = str(
                            st.date_input(
                                "解決日",
                                value=(
                                    parse_date(
                                        failure.get(
                                            "resolved_date",
                                            ""
                                        )
                                    )
                                    or date.today()
                                ),
                                key=(
                                    f"edit_resolved_date_"
                                    f"{failure_id}"
                                )
                            )
                        )

                    edit_memo = st.text_area(
                        "補足メモ",
                        value=failure.get(
                            "memo",
                            ""
                        ),
                        key=(
                            f"edit_memo_"
                            f"{failure_id}"
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_failure_"
                            f"{failure_id}"
                        ),
                        use_container_width=True
                    ):
                        if not edit_title.strip():
                            st.error(
                                "タイトルを入力してください。"
                            )

                        elif not edit_what_happened.strip():
                            st.error(
                                "何が起きたかを入力してください。"
                            )

                        else:
                            update_failure(
                                data,
                                failure_id,
                                {
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "occurred_date": str(
                                        edit_occurred_date
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "impact": (
                                        edit_impact
                                    ),
                                    "priority": (
                                        edit_priority
                                    ),
                                    "status": (
                                        edit_status
                                    ),
                                    "recurrence_count": int(
                                        edit_recurrence
                                    ),
                                    "what_happened": (
                                        edit_what_happened.strip()
                                    ),
                                    "why_problem": (
                                        edit_why_problem.strip()
                                    ),
                                    "cause_types": (
                                        edit_cause_types
                                    ),
                                    "root_cause": (
                                        edit_root_cause.strip()
                                    ),
                                    "improvement_plan": (
                                        edit_improvement.strip()
                                    ),
                                    "prevention_rule": (
                                        edit_rule.strip()
                                    ),
                                    "learning": (
                                        edit_learning.strip()
                                    ),
                                    "retry_date": (
                                        edit_retry_date
                                    ),
                                    "resolved_date": (
                                        edit_resolved_date
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                }
                            )

                            st.success(
                                "更新しました！"
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
                                f"{failure_id}"
                            )
                        )
                    )

                    if st.button(
                        "この記録を削除",
                        key=(
                            f"delete_failure_"
                            f"{failure_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_failure(
                            data,
                            failure_id
                        )

                        st.rerun()


# =========================================================
# 再挑戦ログ
# =========================================================

with retry_tab:
    st.header(
        "🔄 再挑戦ログ"
    )

    if not failures:
        st.info(
            "失敗を登録すると再挑戦ログを追加できます。"
        )

    else:
        failure_options = {
            (
                f"{failure.get('title', '無題')}"
                f"｜{failure.get('status', '')}"
            ): failure["id"]
            for failure in failures
        }

        selected_name = st.selectbox(
            "記録する失敗を選択",
            list(
                failure_options.keys()
            )
        )

        selected_failure = (
            get_failure_by_id(
                data,
                failure_options[
                    selected_name
                ]
            )
        )

        selected_failure_id = (
            selected_failure["id"]
        )

        with st.container(
            border=True
        ):
            st.subheader(
                selected_failure.get(
                    "title",
                    "無題"
                )
            )

            st.write(
                selected_failure.get(
                    "what_happened",
                    ""
                )
            )

            if selected_failure.get(
                "improvement_plan",
                ""
            ):
                st.success(
                    "改善案\n\n"
                    + selected_failure.get(
                        "improvement_plan",
                        ""
                    )
                )

        with st.form(
            (
                f"retry_form_"
                f"{selected_failure_id}"
            ),
            clear_on_submit=True
        ):
            retry_log_date = (
                st.date_input(
                    "再挑戦日",
                    value=date.today()
                )
            )

            improvement_tried = (
                st.text_area(
                    "今回試した改善",
                    placeholder=(
                        "実際にどの改善策を試したか"
                    ),
                    height=110
                )
            )

            result = st.text_area(
                "結果",
                placeholder=(
                    "改善したか、再発したか、"
                    "何が起きたか"
                ),
                height=110
            )

            result_type = st.selectbox(
                "結果の判定",
                RESULT_TYPES
            )

            next_improvement = (
                st.text_area(
                    "次の改善",
                    placeholder=(
                        "次回さらに変えること"
                    ),
                    height=100
                )
            )

            effect_score = st.slider(
                "改善策の効果",
                min_value=1,
                max_value=5,
                value=3
            )

            retry_submitted = (
                st.form_submit_button(
                    "🔄 再挑戦ログを追加",
                    use_container_width=True
                )
            )

            if retry_submitted:
                if not improvement_tried.strip():
                    st.error(
                        "試した改善を入力してください。"
                    )

                else:
                    add_retry_log(
                        data,
                        selected_failure_id,
                        {
                            "retry_date": str(
                                retry_log_date
                            ),
                            "improvement_tried": (
                                improvement_tried.strip()
                            ),
                            "result": (
                                result.strip()
                            ),
                            "result_type": (
                                result_type
                            ),
                            "next_improvement": (
                                next_improvement.strip()
                            ),
                            "effect_score": (
                                effect_score
                            ),
                        }
                    )

                    st.success(
                        "再挑戦ログを追加しました！"
                    )

                    st.rerun()

        st.divider()

        st.subheader(
            "過去の再挑戦ログ"
        )

        retry_logs = sorted(
            selected_failure.get(
                "retry_logs",
                []
            ),
            key=lambda log: (
                log.get(
                    "retry_date",
                    ""
                ),
                log.get(
                    "created_at",
                    ""
                )
            ),
            reverse=True
        )

        if not retry_logs:
            st.info(
                "再挑戦ログはまだありません。"
            )

        for log in retry_logs:
            log_id = log["id"]

            with st.container(
                border=True
            ):
                log_column1, log_column2 = (
                    st.columns(
                        [
                            4,
                            1,
                        ]
                    )
                )

                log_column1.markdown(
                    f"### "
                    f"{format_date(log.get('retry_date', ''))}"
                )

                log_column2.metric(
                    "効果",
                    f"{log.get('effect_score', 3)}/5"
                )

                st.write(
                    "**試した改善**"
                )

                st.write(
                    log.get(
                        "improvement_tried",
                        ""
                    )
                )

                if log.get(
                    "result",
                    ""
                ):
                    st.write(
                        "**結果**"
                    )

                    st.write(
                        log.get(
                            "result",
                            ""
                        )
                    )

                st.info(
                    f"判定："
                    f"{log.get('result_type', '未評価')}"
                )

                if log.get(
                    "next_improvement",
                    ""
                ):
                    st.warning(
                        "次の改善\n\n"
                        + log.get(
                            "next_improvement",
                            ""
                        )
                    )

                with st.expander(
                    "ログを削除"
                ):
                    confirm_log_delete = (
                        st.checkbox(
                            "削除を確認しました",
                            key=(
                                f"confirm_log_"
                                f"{log_id}"
                            )
                        )
                    )

                    if st.button(
                        "このログを削除",
                        key=(
                            f"delete_log_"
                            f"{log_id}"
                        ),
                        disabled=(
                            not confirm_log_delete
                        )
                    ):
                        delete_retry_log(
                            data,
                            selected_failure_id,
                            log_id
                        )

                        st.rerun()


# =========================================================
# 分析
# =========================================================

with analysis_tab:
    st.header(
        "📈 失敗と改善の分析"
    )

    if not failures:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for failure in failures:
            resolve_days = (
                days_to_resolve(
                    failure
                )
            )

            analysis_rows.append(
                {
                    "タイトル": (
                        failure.get(
                            "title",
                            ""
                        )
                    ),
                    "カテゴリー": (
                        failure.get(
                            "category",
                            ""
                        )
                    ),
                    "状態": (
                        failure.get(
                            "status",
                            ""
                        )
                    ),
                    "影響度": (
                        failure.get(
                            "impact",
                            ""
                        )
                    ),
                    "影響度数値": (
                        IMPACT_VALUES.get(
                            failure.get(
                                "impact",
                                "中"
                            ),
                            3
                        )
                    ),
                    "再発回数": int(
                        failure.get(
                            "recurrence_count",
                            0
                        )
                    ),
                    "再挑戦回数": (
                        retry_count(
                            failure
                        )
                    ),
                    "平均改善効果": round(
                        average_effect_score(
                            failure
                        ),
                        2
                    ),
                    "解決日数": (
                        resolve_days
                        if resolve_days
                        is not None
                        else None
                    ),
                }
            )

        analysis_df = pd.DataFrame(
            analysis_rows
        )

        st.subheader(
            "状態別"
        )

        status_summary = (
            analysis_df.groupby(
                "状態",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
            .sort_values(
                "件数",
                ascending=False
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
            hide_index=True
        )

        st.divider()

        st.subheader(
            "カテゴリー別"
        )

        category_summary = (
            analysis_df.groupby(
                "カテゴリー",
                as_index=False
            )
            .agg(
                失敗件数=(
                    "タイトル",
                    "count"
                ),
                再発回数=(
                    "再発回数",
                    "sum"
                ),
                再挑戦回数=(
                    "再挑戦回数",
                    "sum"
                ),
            )
            .sort_values(
                "失敗件数",
                ascending=False
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["失敗件数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "原因別ランキング"
        )

        cause_counter = {}

        for failure in failures:
            for cause in failure.get(
                "cause_types",
                []
            ):
                cause_counter[cause] = (
                    cause_counter.get(
                        cause,
                        0
                    )
                    + 1
                )

        if cause_counter:
            cause_df = pd.DataFrame(
                [
                    {
                        "原因": cause,
                        "件数": count,
                    }
                    for cause, count
                    in cause_counter.items()
                ]
            ).sort_values(
                "件数",
                ascending=False
            )

            st.bar_chart(
                cause_df.set_index(
                    "原因"
                )[["件数"]]
            )

            st.dataframe(
                cause_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "原因の種類がまだ登録されていません。"
            )

        st.divider()

        st.subheader(
            "再発しやすい失敗"
        )

        recurrence_ranking = (
            analysis_df.sort_values(
                "再発回数",
                ascending=False
            )[
                [
                    "タイトル",
                    "カテゴリー",
                    "再発回数",
                    "状態",
                ]
            ]
        )

        st.dataframe(
            recurrence_ranking,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "再挑戦回数ランキング"
        )

        retry_ranking = (
            analysis_df.sort_values(
                "再挑戦回数",
                ascending=False
            )[
                [
                    "タイトル",
                    "再挑戦回数",
                    "平均改善効果",
                    "状態",
                ]
            ]
        )

        st.dataframe(
            retry_ranking,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "効果の高い改善"
        )

        effective_df = analysis_df[
            analysis_df[
                "平均改善効果"
            ]
            > 0
        ].sort_values(
            "平均改善効果",
            ascending=False
        )

        if effective_df.empty:
            st.info(
                "改善効果がまだ評価されていません。"
            )

        else:
            st.dataframe(
                effective_df[
                    [
                        "タイトル",
                        "平均改善効果",
                        "再挑戦回数",
                        "状態",
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "解決までの日数"
        )

        resolved_df = analysis_df.dropna(
            subset=[
                "解決日数"
            ]
        ).sort_values(
            "解決日数"
        )

        if resolved_df.empty:
            st.info(
                "解決日が登録されたデータはありません。"
            )

        else:
            average_days = (
                resolved_df[
                    "解決日数"
                ].mean()
            )

            st.metric(
                "平均解決日数",
                f"{average_days:.1f}日"
            )

            st.dataframe(
                resolved_df[
                    [
                        "タイトル",
                        "カテゴリー",
                        "解決日数",
                    ]
                ],
                use_container_width=True,
                hide_index=True
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
        indent=2
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=json_text,
        file_name=(
            f"failure_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True
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
            ]
        )
    )

    if uploaded_file is not None:
        try:
            imported_data = json.load(
                uploaded_file
            )

            if (
                not isinstance(
                    imported_data,
                    dict
                )
                or "failures"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "failures"
                    ],
                    list
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
                    use_container_width=True
                ):
                    save_data(
                        imported_data
                    )

                    st.success(
                        "データを復元しました！"
                    )

                    st.rerun()

        except (
            json.JSONDecodeError,
            UnicodeDecodeError
        ):
            st.error(
                "JSONファイルを読み込めませんでした。"
            )

    st.divider()

    st.subheader(
        "すべてのデータを削除"
    )

    st.error(
        "失敗記録と再挑戦ログがすべて削除されます。"
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
        use_container_width=True
    ):
        save_data(
            create_empty_data()
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
    "失敗は終わりではなく、改善を始めるための記録です。🛠️"
)
