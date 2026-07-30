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
    page_title="学び実践トラッカー",
    page_icon="🧠",
    layout="wide"
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "learning_data.json")

SOURCE_TYPES = [
    "本",
    "動画",
    "講座",
    "記事",
    "SNS",
    "会話",
    "仕事",
    "体験",
    "その他",
]

STATUSES = [
    "未着手",
    "準備中",
    "実践中",
    "達成",
    "改善中",
    "中止",
]

STATUS_ICONS = {
    "未着手": "⚪",
    "準備中": "🟡",
    "実践中": "🔵",
    "達成": "✅",
    "改善中": "🛠️",
    "中止": "⛔",
}

PRIORITIES = [
    "最優先",
    "高",
    "中",
    "低",
]

PRIORITY_ICONS = {
    "最優先": "🔥",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵",
}

PRIORITY_ORDER = {
    "最優先": 0,
    "高": 1,
    "中": 2,
    "低": 3,
}

CATEGORIES = [
    "仕事・キャリア",
    "アプリ開発",
    "AI・テクノロジー",
    "起業・経営",
    "お金",
    "健康",
    "運動",
    "食事",
    "人間関係",
    "家族",
    "メンタル",
    "習慣",
    "自己成長",
    "その他",
]

DECISIONS = [
    "未決定",
    "このまま続ける",
    "少し改善して続ける",
    "別の方法を試す",
    "今回は中止する",
    "習慣として定着した",
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
    """初期データを作成する。"""

    return {
        "learnings": []
    }


def save_data(data):
    """JSONファイルへデータを保存する。"""

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
    """古い保存データにも不足項目を追加する。"""

    if not isinstance(data, dict):
        data = create_empty_data()

    data.setdefault(
        "learnings",
        []
    )

    for learning in data["learnings"]:
        learning.setdefault(
            "id",
            create_id()
        )

        learning.setdefault(
            "title",
            ""
        )

        learning.setdefault(
            "learning",
            ""
        )

        learning.setdefault(
            "source_type",
            "本"
        )

        learning.setdefault(
            "source_name",
            ""
        )

        learning.setdefault(
            "category",
            "その他"
        )

        learning.setdefault(
            "practice_action",
            ""
        )

        learning.setdefault(
            "status",
            "未着手"
        )

        learning.setdefault(
            "priority",
            "中"
        )

        learning.setdefault(
            "target_count",
            1
        )

        learning.setdefault(
            "practice_count",
            0
        )

        learning.setdefault(
            "start_date",
            ""
        )

        learning.setdefault(
            "deadline",
            ""
        )

        learning.setdefault(
            "memo",
            ""
        )

        learning.setdefault(
            "decision",
            "未決定"
        )

        learning.setdefault(
            "final_reflection",
            ""
        )

        learning.setdefault(
            "scores",
            {
                "effect": 0,
                "ease": 0,
                "fit": 0,
                "repeatability": 0,
                "satisfaction": 0,
            }
        )

        learning.setdefault(
            "logs",
            []
        )

        learning.setdefault(
            "created_at",
            ""
        )

        learning.setdefault(
            "updated_at",
            ""
        )

        for log in learning["logs"]:
            log.setdefault(
                "id",
                create_id()
            )

            log.setdefault(
                "log_date",
                str(date.today())
            )

            log.setdefault(
                "action",
                ""
            )

            log.setdefault(
                "result",
                ""
            )

            log.setdefault(
                "insight",
                ""
            )

            log.setdefault(
                "next_improvement",
                ""
            )

            log.setdefault(
                "success_level",
                3
            )

            log.setdefault(
                "created_at",
                ""
            )

    return data


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):
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
        backup_file = (
            DATA_FILE
            + ".broken"
        )

        try:
            if os.path.exists(DATA_FILE):
                os.replace(
                    DATA_FILE,
                    backup_file
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
        ValueError,
        TypeError
    ):
        return None


def format_date(date_text):
    """日付を日本語表示にする。"""

    parsed = parse_date(
        date_text
    )

    if not parsed:
        return "未設定"

    return parsed.strftime(
        "%Y年%m月%d日"
    )


def get_learning_by_id(
    data,
    learning_id
):
    """IDから学びを取得する。"""

    for learning in data["learnings"]:
        if (
            learning.get("id")
            == learning_id
        ):
            return learning

    return None


def display_name(learning):
    """学びの表示名を返す。"""

    title = learning.get(
        "title",
        ""
    ).strip()

    if title:
        return title

    learning_text = learning.get(
        "learning",
        "無題"
    )

    return learning_text[:30]


def calculate_progress(learning):
    """目標回数に対する進捗率を計算する。"""

    target_count = max(
        int(
            learning.get(
                "target_count",
                1
            )
        ),
        1
    )

    practice_count = max(
        int(
            learning.get(
                "practice_count",
                0
            )
        ),
        0
    )

    progress = (
        practice_count
        / target_count
        * 100
    )

    return min(
        progress,
        100
    )


def calculate_average_score(learning):
    """5項目の平均評価を計算する。"""

    scores = learning.get(
        "scores",
        {}
    )

    values = [
        int(
            scores.get(
                "effect",
                0
            )
        ),
        int(
            scores.get(
                "ease",
                0
            )
        ),
        int(
            scores.get(
                "fit",
                0
            )
        ),
        int(
            scores.get(
                "repeatability",
                0
            )
        ),
        int(
            scores.get(
                "satisfaction",
                0
            )
        ),
    ]

    valid_values = [
        value
        for value in values
        if value > 0
    ]

    if not valid_values:
        return 0

    return (
        sum(valid_values)
        / len(valid_values)
    )


def days_until_deadline(learning):
    """期限までの日数を計算する。"""

    deadline = parse_date(
        learning.get(
            "deadline",
            ""
        )
    )

    if not deadline:
        return None

    return (
        deadline
        - date.today()
    ).days


def is_overdue(learning):
    """期限切れか判定する。"""

    remaining_days = (
        days_until_deadline(
            learning
        )
    )

    return bool(
        remaining_days is not None
        and remaining_days < 0
        and learning.get(
            "status"
        )
        not in [
            "達成",
            "中止",
        ]
    )


def update_status_automatically(
    learning
):
    """実践回数に応じて状態を自動更新する。"""

    target_count = max(
        int(
            learning.get(
                "target_count",
                1
            )
        ),
        1
    )

    practice_count = int(
        learning.get(
            "practice_count",
            0
        )
    )

    current_status = learning.get(
        "status",
        "未着手"
    )

    if (
        practice_count
        >= target_count
        and current_status
        not in [
            "中止",
            "改善中",
        ]
    ):
        learning["status"] = "達成"

    elif (
        practice_count > 0
        and current_status
        in [
            "未着手",
            "準備中",
        ]
    ):
        learning["status"] = "実践中"


# =========================================================
# データ操作
# =========================================================

def add_learning(
    data,
    values
):
    """新しい学びを追加する。"""

    learning = {
        "id": create_id(),
        "title": values["title"],
        "learning": values["learning"],
        "source_type": values["source_type"],
        "source_name": values["source_name"],
        "category": values["category"],
        "practice_action": values["practice_action"],
        "status": values["status"],
        "priority": values["priority"],
        "target_count": int(
            values["target_count"]
        ),
        "practice_count": 0,
        "start_date": values["start_date"],
        "deadline": values["deadline"],
        "memo": values["memo"],
        "decision": "未決定",
        "final_reflection": "",
        "scores": {
            "effect": 0,
            "ease": 0,
            "fit": 0,
            "repeatability": 0,
            "satisfaction": 0,
        },
        "logs": [],
        "created_at": now_text(),
        "updated_at": "",
    }

    data["learnings"].append(
        learning
    )

    save_data(data)


def update_learning(
    data,
    learning_id,
    values
):
    """学びを更新する。"""

    learning = get_learning_by_id(
        data,
        learning_id
    )

    if not learning:
        return

    for key, value in values.items():
        learning[key] = value

    update_status_automatically(
        learning
    )

    learning["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_learning(
    data,
    learning_id
):
    """学びを削除する。"""

    data["learnings"] = [
        learning
        for learning in data["learnings"]
        if learning.get("id")
        != learning_id
    ]

    save_data(data)


def add_practice_log(
    data,
    learning_id,
    values
):
    """実践ログを追加する。"""

    learning = get_learning_by_id(
        data,
        learning_id
    )

    if not learning:
        return

    log = {
        "id": create_id(),
        "log_date": values["log_date"],
        "action": values["action"],
        "result": values["result"],
        "insight": values["insight"],
        "next_improvement": (
            values["next_improvement"]
        ),
        "success_level": int(
            values["success_level"]
        ),
        "created_at": now_text(),
    }

    learning["logs"].append(
        log
    )

    learning["practice_count"] = (
        int(
            learning.get(
                "practice_count",
                0
            )
        )
        + 1
    )

    update_status_automatically(
        learning
    )

    learning["updated_at"] = (
        now_text()
    )

    save_data(data)


def delete_practice_log(
    data,
    learning_id,
    log_id
):
    """実践ログを削除する。"""

    learning = get_learning_by_id(
        data,
        learning_id
    )

    if not learning:
        return

    old_log_count = len(
        learning.get(
            "logs",
            []
        )
    )

    learning["logs"] = [
        log
        for log in learning.get(
            "logs",
            []
        )
        if log.get("id")
        != log_id
    ]

    new_log_count = len(
        learning["logs"]
    )

    if new_log_count < old_log_count:
        learning["practice_count"] = max(
            int(
                learning.get(
                    "practice_count",
                    0
                )
            )
            - 1,
            0
        )

    learning["updated_at"] = (
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
        background: rgba(120, 100, 255, 0.07);
        border: 1px solid rgba(120, 100, 255, 0.15);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px 28px;
        margin-bottom: 20px;
        border-radius: 22px;
        border: 1px solid rgba(117, 93, 255, 0.20);
        background:
            linear-gradient(
                135deg,
                rgba(117, 93, 255, 0.18),
                rgba(60, 190, 255, 0.12)
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

learnings = data[
    "learnings"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧠 学び実践トラッカー</h1>
        <p>
            学んだことを小さな行動へ変え、
            実践・改善・習慣化まで記録するアプリ
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ダッシュボード
# =========================================================

total_count = len(
    learnings
)

not_started_count = len(
    [
        learning
        for learning in learnings
        if learning.get("status")
        == "未着手"
    ]
)

practicing_count = len(
    [
        learning
        for learning in learnings
        if learning.get("status")
        == "実践中"
    ]
)

completed_count = len(
    [
        learning
        for learning in learnings
        if learning.get("status")
        == "達成"
    ]
)

improving_count = len(
    [
        learning
        for learning in learnings
        if learning.get("status")
        == "改善中"
    ]
)

overdue_count = len(
    [
        learning
        for learning in learnings
        if is_overdue(learning)
    ]
)

today = date.today()

monthly_log_count = 0

for learning in learnings:
    for log in learning.get(
        "logs",
        []
    ):
        log_date = parse_date(
            log.get(
                "log_date",
                ""
            )
        )

        if (
            log_date
            and log_date.year
            == today.year
            and log_date.month
            == today.month
        ):
            monthly_log_count += 1

completion_rate = (
    completed_count
    / total_count
    * 100
    if total_count > 0
    else 0
)

metric_row1 = st.columns(4)

metric_row1[0].metric(
    "登録した学び",
    f"{total_count}件"
)

metric_row1[1].metric(
    "未着手",
    f"{not_started_count}件"
)

metric_row1[2].metric(
    "実践中",
    f"{practicing_count}件"
)

metric_row1[3].metric(
    "達成",
    f"{completed_count}件"
)

metric_row2 = st.columns(4)

metric_row2[0].metric(
    "今月の実践",
    f"{monthly_log_count}回"
)

metric_row2[1].metric(
    "達成率",
    f"{completion_rate:.1f}%"
)

metric_row2[2].metric(
    "期限切れ",
    f"{overdue_count}件"
)

metric_row2[3].metric(
    "改善中",
    f"{improving_count}件"
)


# =========================================================
# 今日の候補・期限アラート
# =========================================================

active_learnings = [
    learning
    for learning in learnings
    if learning.get("status")
    not in [
        "達成",
        "中止",
    ]
]

if active_learnings:
    st.divider()

    candidate_column, alert_column = (
        st.columns(2)
    )

    with candidate_column:
        st.subheader(
            "🎯 今日の実践候補"
        )

        sorted_candidates = sorted(
            active_learnings,
            key=lambda learning: (
                PRIORITY_ORDER.get(
                    learning.get(
                        "priority",
                        "中"
                    ),
                    99
                ),
                (
                    days_until_deadline(
                        learning
                    )
                    if days_until_deadline(
                        learning
                    )
                    is not None
                    else 999999
                )
            )
        )

        candidate = (
            sorted_candidates[0]
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### "
                f"{PRIORITY_ICONS.get(candidate.get('priority', ''), '')} "
                f"{display_name(candidate)}"
            )

            st.success(
                candidate.get(
                    "practice_action",
                    ""
                )
            )

            candidate_progress = (
                calculate_progress(
                    candidate
                )
            )

            st.progress(
                candidate_progress
                / 100
            )

            st.caption(
                f"実践回数："
                f"{candidate.get('practice_count', 0)}"
                f"／"
                f"{candidate.get('target_count', 1)}回"
            )

    with alert_column:
        st.subheader(
            "⏰ 期限アラート"
        )

        alert_learnings = [
            learning
            for learning
            in active_learnings
            if (
                days_until_deadline(
                    learning
                )
                is not None
                and days_until_deadline(
                    learning
                )
                <= 7
            )
        ]

        if not alert_learnings:
            st.success(
                "7日以内に期限を迎える学びはありません。"
            )

        else:
            alert_learnings = sorted(
                alert_learnings,
                key=lambda learning: (
                    days_until_deadline(
                        learning
                    )
                )
            )

            for learning in alert_learnings:
                remaining_days = (
                    days_until_deadline(
                        learning
                    )
                )

                if remaining_days < 0:
                    st.error(
                        f"期限切れ："
                        f"{display_name(learning)} "
                        f"（{-remaining_days}日超過）"
                    )

                elif remaining_days == 0:
                    st.warning(
                        f"本日期限："
                        f"{display_name(learning)}"
                    )

                else:
                    st.info(
                        f"あと{remaining_days}日："
                        f"{display_name(learning)}"
                    )


# =========================================================
# ランダム学び
# =========================================================

random_candidates = [
    learning
    for learning in learnings
    if learning.get(
        "learning",
        ""
    ).strip()
]

if random_candidates:
    st.divider()

    st.subheader(
        "💡 学びを思い出す"
    )

    if (
        "random_learning_id"
        not in st.session_state
    ):
        st.session_state[
            "random_learning_id"
        ] = random.choice(
            random_candidates
        )["id"]

    random_learning = (
        get_learning_by_id(
            data,
            st.session_state[
                "random_learning_id"
            ]
        )
    )

    if random_learning:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### "
                f"{display_name(random_learning)}"
            )

            st.info(
                random_learning.get(
                    "learning",
                    ""
                )
            )

            st.success(
                "実践すること\n\n"
                + random_learning.get(
                    "practice_action",
                    ""
                )
            )

    if st.button(
        "🔄 別の学びを表示"
    ):
        st.session_state[
            "random_learning_id"
        ] = random.choice(
            random_candidates
        )["id"]

        st.rerun()


# =========================================================
# タブ
# =========================================================

st.divider()

(
    add_tab,
    list_tab,
    log_tab,
    review_tab,
    analysis_tab,
    data_tab,
) = st.tabs(
    [
        "➕ 学びを登録",
        "📋 学び一覧",
        "📝 実践ログ",
        "🔍 振り返り",
        "📈 分析",
        "💾 データ管理",
    ]
)


# =========================================================
# 学び登録
# =========================================================

with add_tab:
    st.header(
        "➕ 新しい学びを登録"
    )

    with st.form(
        "add_learning_form",
        clear_on_submit=True
    ):
        input_column1, input_column2 = (
            st.columns(2)
        )

        with input_column1:
            title = st.text_input(
                "学びのタイトル",
                placeholder=(
                    "例：学んだ方法を自分用に変える"
                )
            )

            source_type = st.selectbox(
                "学び元の種類",
                SOURCE_TYPES
            )

            source_name = st.text_input(
                "学び元の名前",
                placeholder=(
                    "例：フリーランスの教科書"
                )
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES
            )

            priority = st.selectbox(
                "優先度",
                PRIORITIES,
                index=2
            )

        with input_column2:
            status = st.selectbox(
                "実践状態",
                STATUSES,
                index=0
            )

            target_count = (
                st.number_input(
                    "目標実践回数",
                    min_value=1,
                    max_value=10000,
                    value=5,
                    step=1
                )
            )

            set_start_date = (
                st.checkbox(
                    "開始日を設定する"
                )
            )

            start_date_value = ""

            if set_start_date:
                start_date_value = str(
                    st.date_input(
                        "開始日",
                        value=date.today()
                    )
                )

            set_deadline = st.checkbox(
                "期限を設定する"
            )

            deadline_value = ""

            if set_deadline:
                deadline_value = str(
                    st.date_input(
                        "実践期限",
                        value=(
                            date.today()
                            + timedelta(
                                days=14
                            )
                        )
                    )
                )

        learning_text = st.text_area(
            "学んだ内容",
            placeholder=(
                "何を学んだのか、具体的に書きます。"
            ),
            height=120
        )

        practice_action = st.text_area(
            "実践すること",
            placeholder=(
                "今日から行う小さな行動を書きます。"
            ),
            height=120
        )

        memo = st.text_area(
            "補足メモ",
            placeholder=(
                "背景、注意点、参考情報など"
            ),
            height=90
        )

        add_submitted = (
            st.form_submit_button(
                "🧠 学びを登録",
                use_container_width=True
            )
        )

        if add_submitted:
            if not title.strip():
                st.error(
                    "学びのタイトルを入力してください。"
                )

            elif not learning_text.strip():
                st.error(
                    "学んだ内容を入力してください。"
                )

            elif not practice_action.strip():
                st.error(
                    "実践することを入力してください。"
                )

            else:
                add_learning(
                    data,
                    {
                        "title": title.strip(),
                        "learning": (
                            learning_text.strip()
                        ),
                        "source_type": (
                            source_type
                        ),
                        "source_name": (
                            source_name.strip()
                        ),
                        "category": category,
                        "practice_action": (
                            practice_action.strip()
                        ),
                        "status": status,
                        "priority": priority,
                        "target_count": (
                            target_count
                        ),
                        "start_date": (
                            start_date_value
                        ),
                        "deadline": (
                            deadline_value
                        ),
                        "memo": memo.strip(),
                    }
                )

                st.success(
                    "学びを登録しました！"
                )

                st.rerun()


# =========================================================
# 学び一覧
# =========================================================

with list_tab:
    st.header(
        "📋 学び一覧"
    )

    if not learnings:
        st.info(
            "学びはまだ登録されていません。"
        )

    else:
        filter_column1, filter_column2, filter_column3 = (
            st.columns(3)
        )

        with filter_column1:
            keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "タイトル・学び・学び元"
                )
            )

        with filter_column2:
            status_filter = (
                st.selectbox(
                    "状態",
                    [
                        "すべて"
                    ]
                    + STATUSES
                )
            )

        with filter_column3:
            category_filter = (
                st.selectbox(
                    "カテゴリー",
                    [
                        "すべて"
                    ]
                    + CATEGORIES
                )
            )

        priority_filter = (
            st.multiselect(
                "優先度",
                PRIORITIES,
                default=PRIORITIES
            )
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "登録が新しい順",
                "優先度順",
                "期限が近い順",
                "進捗が高い順",
                "評価が高い順",
            ]
        )

        filtered_learnings = list(
            learnings
        )

        if keyword.strip():
            search_word = (
                keyword.strip().lower()
            )

            filtered_learnings = [
                learning
                for learning
                in filtered_learnings
                if (
                    search_word
                    in learning.get(
                        "title",
                        ""
                    ).lower()
                    or search_word
                    in learning.get(
                        "learning",
                        ""
                    ).lower()
                    or search_word
                    in learning.get(
                        "source_name",
                        ""
                    ).lower()
                    or search_word
                    in learning.get(
                        "practice_action",
                        ""
                    ).lower()
                    or search_word
                    in learning.get(
                        "memo",
                        ""
                    ).lower()
                )
            ]

        if status_filter != "すべて":
            filtered_learnings = [
                learning
                for learning
                in filtered_learnings
                if learning.get(
                    "status"
                )
                == status_filter
            ]

        if category_filter != "すべて":
            filtered_learnings = [
                learning
                for learning
                in filtered_learnings
                if learning.get(
                    "category"
                )
                == category_filter
            ]

        filtered_learnings = [
            learning
            for learning
            in filtered_learnings
            if learning.get(
                "priority",
                "中"
            )
            in priority_filter
        ]

        if (
            sort_option
            == "登録が新しい順"
        ):
            filtered_learnings.sort(
                key=lambda learning: (
                    learning.get(
                        "created_at",
                        ""
                    )
                ),
                reverse=True
            )

        elif (
            sort_option
            == "優先度順"
        ):
            filtered_learnings.sort(
                key=lambda learning: (
                    PRIORITY_ORDER.get(
                        learning.get(
                            "priority",
                            "中"
                        ),
                        99
                    ),
                    learning.get(
                        "created_at",
                        ""
                    )
                )
            )

        elif (
            sort_option
            == "期限が近い順"
        ):
            filtered_learnings.sort(
                key=lambda learning: (
                    parse_date(
                        learning.get(
                            "deadline",
                            ""
                        )
                    )
                    or date.max
                )
            )

        elif (
            sort_option
            == "進捗が高い順"
        ):
            filtered_learnings.sort(
                key=calculate_progress,
                reverse=True
            )

        elif (
            sort_option
            == "評価が高い順"
        ):
            filtered_learnings.sort(
                key=calculate_average_score,
                reverse=True
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_learnings)}件**"
        )

        for learning in filtered_learnings:
            learning_id = learning[
                "id"
            ]

            progress = (
                calculate_progress(
                    learning
                )
            )

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
                        f"{PRIORITY_ICONS.get(learning.get('priority', ''), '')} "
                        f"{display_name(learning)}"
                    )

                    source_text = (
                        learning.get(
                            "source_type",
                            ""
                        )
                    )

                    if learning.get(
                        "source_name",
                        ""
                    ):
                        source_text += (
                            "："
                            + learning.get(
                                "source_name",
                                ""
                            )
                        )

                    st.caption(
                        f"{source_text} ／ "
                        f"{learning.get('category', '')}"
                    )

                with status_column:
                    current_status = (
                        learning.get(
                            "status",
                            "未着手"
                        )
                    )

                    st.metric(
                        "状態",
                        f"{STATUS_ICONS.get(current_status, '')} "
                        f"{current_status}"
                    )

                st.write(
                    "**学んだ内容**"
                )

                st.write(
                    learning.get(
                        "learning",
                        ""
                    )
                )

                st.write(
                    "**実践すること**"
                )

                st.success(
                    learning.get(
                        "practice_action",
                        ""
                    )
                )

                st.progress(
                    progress / 100
                )

                st.caption(
                    f"実践進捗："
                    f"{learning.get('practice_count', 0)}"
                    f"／"
                    f"{learning.get('target_count', 1)}回 "
                    f"（{progress:.0f}%）"
                )

                detail_columns = (
                    st.columns(3)
                )

                detail_columns[0].write(
                    f"**開始日**\n\n"
                    f"{format_date(learning.get('start_date', ''))}"
                )

                detail_columns[1].write(
                    f"**期限**\n\n"
                    f"{format_date(learning.get('deadline', ''))}"
                )

                average_score = (
                    calculate_average_score(
                        learning
                    )
                )

                if average_score > 0:
                    detail_columns[2].write(
                        f"**平均評価**\n\n"
                        f"{average_score:.1f} / 5"
                    )

                else:
                    detail_columns[2].write(
                        "**平均評価**\n\n"
                        "未評価"
                    )

                if is_overdue(learning):
                    st.error(
                        "この学びは期限を過ぎています。"
                    )

                with st.expander(
                    "✏️ 編集"
                ):
                    edit_title = (
                        st.text_input(
                            "タイトル",
                            value=learning.get(
                                "title",
                                ""
                            ),
                            key=(
                                f"edit_title_"
                                f"{learning_id}"
                            )
                        )
                    )

                    edit_learning_text = (
                        st.text_area(
                            "学んだ内容",
                            value=learning.get(
                                "learning",
                                ""
                            ),
                            key=(
                                f"edit_learning_"
                                f"{learning_id}"
                            )
                        )
                    )

                    edit_action = (
                        st.text_area(
                            "実践すること",
                            value=learning.get(
                                "practice_action",
                                ""
                            ),
                            key=(
                                f"edit_action_"
                                f"{learning_id}"
                            )
                        )
                    )

                    edit_column1, edit_column2 = (
                        st.columns(2)
                    )

                    with edit_column1:
                        current_source = (
                            learning.get(
                                "source_type",
                                "本"
                            )
                        )

                        edit_source_type = (
                            st.selectbox(
                                "学び元の種類",
                                SOURCE_TYPES,
                                index=(
                                    SOURCE_TYPES.index(
                                        current_source
                                    )
                                    if current_source
                                    in SOURCE_TYPES
                                    else 0
                                ),
                                key=(
                                    f"edit_source_type_"
                                    f"{learning_id}"
                                )
                            )
                        )

                        edit_source_name = (
                            st.text_input(
                                "学び元の名前",
                                value=learning.get(
                                    "source_name",
                                    ""
                                ),
                                key=(
                                    f"edit_source_name_"
                                    f"{learning_id}"
                                )
                            )
                        )

                        current_category = (
                            learning.get(
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
                                        len(
                                            CATEGORIES
                                        )
                                        - 1
                                    )
                                ),
                                key=(
                                    f"edit_category_"
                                    f"{learning_id}"
                                )
                            )
                        )

                        current_priority = (
                            learning.get(
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
                                    f"{learning_id}"
                                )
                            )
                        )

                    with edit_column2:
                        current_status = (
                            learning.get(
                                "status",
                                "未着手"
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
                                    f"{learning_id}"
                                )
                            )
                        )

                        edit_target_count = (
                            st.number_input(
                                "目標回数",
                                min_value=1,
                                max_value=10000,
                                value=int(
                                    learning.get(
                                        "target_count",
                                        1
                                    )
                                ),
                                key=(
                                    f"edit_target_"
                                    f"{learning_id}"
                                )
                            )
                        )

                        edit_practice_count = (
                            st.number_input(
                                "現在の実践回数",
                                min_value=0,
                                max_value=10000,
                                value=int(
                                    learning.get(
                                        "practice_count",
                                        0
                                    )
                                ),
                                key=(
                                    f"edit_count_"
                                    f"{learning_id}"
                                )
                            )
                        )

                    start_date_parsed = (
                        parse_date(
                            learning.get(
                                "start_date",
                                ""
                            )
                        )
                    )

                    edit_has_start_date = (
                        st.checkbox(
                            "開始日を設定",
                            value=bool(
                                start_date_parsed
                            ),
                            key=(
                                f"edit_has_start_"
                                f"{learning_id}"
                            )
                        )
                    )

                    edit_start_date = ""

                    if edit_has_start_date:
                        edit_start_date = str(
                            st.date_input(
                                "開始日",
                                value=(
                                    start_date_parsed
                                    or date.today()
                                ),
                                key=(
                                    f"edit_start_date_"
                                    f"{learning_id}"
                                )
                            )
                        )

                    deadline_parsed = (
                        parse_date(
                            learning.get(
                                "deadline",
                                ""
                            )
                        )
                    )

                    edit_has_deadline = (
                        st.checkbox(
                            "期限を設定",
                            value=bool(
                                deadline_parsed
                            ),
                            key=(
                                f"edit_has_deadline_"
                                f"{learning_id}"
                            )
                        )
                    )

                    edit_deadline = ""

                    if edit_has_deadline:
                        edit_deadline = str(
                            st.date_input(
                                "期限",
                                value=(
                                    deadline_parsed
                                    or date.today()
                                ),
                                key=(
                                    f"edit_deadline_"
                                    f"{learning_id}"
                                )
                            )
                        )

                    edit_memo = (
                        st.text_area(
                            "補足メモ",
                            value=learning.get(
                                "memo",
                                ""
                            ),
                            key=(
                                f"edit_memo_"
                                f"{learning_id}"
                            )
                        )
                    )

                    if st.button(
                        "変更を保存",
                        key=(
                            f"save_learning_"
                            f"{learning_id}"
                        ),
                        use_container_width=True
                    ):
                        if not edit_title.strip():
                            st.error(
                                "タイトルを入力してください。"
                            )

                        elif not edit_learning_text.strip():
                            st.error(
                                "学んだ内容を入力してください。"
                            )

                        elif not edit_action.strip():
                            st.error(
                                "実践することを入力してください。"
                            )

                        else:
                            update_learning(
                                data,
                                learning_id,
                                {
                                    "title": (
                                        edit_title.strip()
                                    ),
                                    "learning": (
                                        edit_learning_text.strip()
                                    ),
                                    "practice_action": (
                                        edit_action.strip()
                                    ),
                                    "source_type": (
                                        edit_source_type
                                    ),
                                    "source_name": (
                                        edit_source_name.strip()
                                    ),
                                    "category": (
                                        edit_category
                                    ),
                                    "priority": (
                                        edit_priority
                                    ),
                                    "status": (
                                        edit_status
                                    ),
                                    "target_count": int(
                                        edit_target_count
                                    ),
                                    "practice_count": int(
                                        edit_practice_count
                                    ),
                                    "start_date": (
                                        edit_start_date
                                    ),
                                    "deadline": (
                                        edit_deadline
                                    ),
                                    "memo": (
                                        edit_memo.strip()
                                    ),
                                }
                            )

                            st.success(
                                "学びを更新しました！"
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
                                f"{learning_id}"
                            )
                        )
                    )

                    if st.button(
                        "この学びを削除",
                        key=(
                            f"delete_learning_"
                            f"{learning_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_learning(
                            data,
                            learning_id
                        )

                        st.rerun()


# =========================================================
# 実践ログ
# =========================================================

with log_tab:
    st.header(
        "📝 実践ログ"
    )

    if not learnings:
        st.info(
            "学びを登録すると実践ログを追加できます。"
        )

    else:
        learning_options = {
            (
                f"{display_name(learning)}"
                f"｜"
                f"{learning.get('status', '')}"
            ): learning["id"]
            for learning in learnings
        }

        selected_learning_name = (
            st.selectbox(
                "学びを選択",
                list(
                    learning_options.keys()
                )
            )
        )

        selected_learning = (
            get_learning_by_id(
                data,
                learning_options[
                    selected_learning_name
                ]
            )
        )

        if selected_learning:
            selected_learning_id = (
                selected_learning["id"]
            )

            with st.container(
                border=True
            ):
                st.subheader(
                    display_name(
                        selected_learning
                    )
                )

                st.info(
                    selected_learning.get(
                        "learning",
                        ""
                    )
                )

                st.success(
                    selected_learning.get(
                        "practice_action",
                        ""
                    )
                )

                selected_progress = (
                    calculate_progress(
                        selected_learning
                    )
                )

                st.progress(
                    selected_progress
                    / 100
                )

                st.caption(
                    f"実践回数："
                    f"{selected_learning.get('practice_count', 0)}"
                    f"／"
                    f"{selected_learning.get('target_count', 1)}回"
                )

            with st.form(
                (
                    f"add_log_form_"
                    f"{selected_learning_id}"
                ),
                clear_on_submit=True
            ):
                log_date = st.date_input(
                    "実践日",
                    value=date.today()
                )

                log_action = st.text_area(
                    "実際に行ったこと",
                    placeholder=(
                        "何を、どのように実践したか"
                    ),
                    height=100
                )

                log_result = st.text_area(
                    "結果",
                    placeholder=(
                        "実践して何が起きたか"
                    ),
                    height=100
                )

                log_insight = st.text_area(
                    "気づき",
                    placeholder=(
                        "実践から新しく分かったこと"
                    ),
                    height=100
                )

                log_improvement = (
                    st.text_area(
                        "次回の改善",
                        placeholder=(
                            "次は何を変えるか"
                        ),
                        height=90
                    )
                )

                success_level = st.slider(
                    "今回の手応え",
                    min_value=1,
                    max_value=5,
                    value=3
                )

                add_log_submitted = (
                    st.form_submit_button(
                        "📝 実践ログを追加",
                        use_container_width=True
                    )
                )

                if add_log_submitted:
                    if not log_action.strip():
                        st.error(
                            "実際に行ったことを入力してください。"
                        )

                    else:
                        add_practice_log(
                            data,
                            selected_learning_id,
                            {
                                "log_date": str(
                                    log_date
                                ),
                                "action": (
                                    log_action.strip()
                                ),
                                "result": (
                                    log_result.strip()
                                ),
                                "insight": (
                                    log_insight.strip()
                                ),
                                "next_improvement": (
                                    log_improvement.strip()
                                ),
                                "success_level": (
                                    success_level
                                ),
                            }
                        )

                        st.success(
                            "実践ログを追加しました！"
                        )

                        st.rerun()

            st.divider()

            st.subheader(
                "過去の実践ログ"
            )

            practice_logs = sorted(
                selected_learning.get(
                    "logs",
                    []
                ),
                key=lambda log: (
                    log.get(
                        "log_date",
                        ""
                    ),
                    log.get(
                        "created_at",
                        ""
                    )
                ),
                reverse=True
            )

            if not practice_logs:
                st.info(
                    "実践ログはまだありません。"
                )

            for log in practice_logs:
                log_id = log["id"]

                with st.container(
                    border=True
                ):
                    log_title_column, log_score_column = (
                        st.columns(
                            [
                                4,
                                1,
                            ]
                        )
                    )

                    log_title_column.markdown(
                        f"### "
                        f"{format_date(log.get('log_date', ''))}"
                    )

                    log_score_column.metric(
                        "手応え",
                        f"{log.get('success_level', 3)} / 5"
                    )

                    st.write(
                        "**行ったこと**"
                    )

                    st.write(
                        log.get(
                            "action",
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

                    if log.get(
                        "insight",
                        ""
                    ):
                        st.info(
                            "💡 気づき\n\n"
                            + log.get(
                                "insight",
                                ""
                            )
                        )

                    if log.get(
                        "next_improvement",
                        ""
                    ):
                        st.warning(
                            "🛠️ 次回の改善\n\n"
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
                                    f"confirm_log_delete_"
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
                            delete_practice_log(
                                data,
                                selected_learning_id,
                                log_id
                            )

                            st.rerun()


# =========================================================
# 振り返り
# =========================================================

with review_tab:
    st.header(
        "🔍 実践の振り返り"
    )

    reviewable_learnings = [
        learning
        for learning in learnings
        if int(
            learning.get(
                "practice_count",
                0
            )
        )
        > 0
    ]

    if not reviewable_learnings:
        st.info(
            "実践ログを追加すると振り返りできます。"
        )

    else:
        review_options = {
            display_name(
                learning
            ): learning["id"]
            for learning
            in reviewable_learnings
        }

        selected_review_name = (
            st.selectbox(
                "振り返る学び",
                list(
                    review_options.keys()
                ),
                key="review_learning_select"
            )
        )

        review_learning = (
            get_learning_by_id(
                data,
                review_options[
                    selected_review_name
                ]
            )
        )

        review_learning_id = (
            review_learning["id"]
        )

        st.info(
            review_learning.get(
                "learning",
                ""
            )
        )

        st.success(
            review_learning.get(
                "practice_action",
                ""
            )
        )

        scores = review_learning.get(
            "scores",
            {}
        )

        with st.form(
            f"review_form_{review_learning_id}"
        ):
            st.subheader(
                "5段階評価"
            )

            score_columns = (
                st.columns(5)
            )

            effect_score = (
                score_columns[0].slider(
                    "効果",
                    min_value=1,
                    max_value=5,
                    value=(
                        int(
                            scores.get(
                                "effect",
                                0
                            )
                        )
                        or 3
                    )
                )
            )

            ease_score = (
                score_columns[1].slider(
                    "続けやすさ",
                    min_value=1,
                    max_value=5,
                    value=(
                        int(
                            scores.get(
                                "ease",
                                0
                            )
                        )
                        or 3
                    )
                )
            )

            fit_score = (
                score_columns[2].slider(
                    "自分との相性",
                    min_value=1,
                    max_value=5,
                    value=(
                        int(
                            scores.get(
                                "fit",
                                0
                            )
                        )
                        or 3
                    )
                )
            )

            repeatability_score = (
                score_columns[3].slider(
                    "再現性",
                    min_value=1,
                    max_value=5,
                    value=(
                        int(
                            scores.get(
                                "repeatability",
                                0
                            )
                        )
                        or 3
                    )
                )
            )

            satisfaction_score = (
                score_columns[4].slider(
                    "満足度",
                    min_value=1,
                    max_value=5,
                    value=(
                        int(
                            scores.get(
                                "satisfaction",
                                0
                            )
                        )
                        or 3
                    )
                )
            )

            current_decision = (
                review_learning.get(
                    "decision",
                    "未決定"
                )
            )

            decision = st.selectbox(
                "今後の判断",
                DECISIONS,
                index=(
                    DECISIONS.index(
                        current_decision
                    )
                    if current_decision
                    in DECISIONS
                    else 0
                )
            )

            final_reflection = (
                st.text_area(
                    "総合振り返り",
                    value=(
                        review_learning.get(
                            "final_reflection",
                            ""
                        )
                    ),
                    placeholder=(
                        "良かった点、改善点、"
                        "今後どうするか"
                    ),
                    height=160
                )
            )

            review_submitted = (
                st.form_submit_button(
                    "振り返りを保存",
                    use_container_width=True
                )
            )

            if review_submitted:
                next_status = (
                    review_learning.get(
                        "status",
                        "実践中"
                    )
                )

                if (
                    decision
                    == "今回は中止する"
                ):
                    next_status = "中止"

                elif (
                    decision
                    == "少し改善して続ける"
                ):
                    next_status = "改善中"

                elif (
                    decision
                    == "習慣として定着した"
                ):
                    next_status = "達成"

                update_learning(
                    data,
                    review_learning_id,
                    {
                        "scores": {
                            "effect": (
                                effect_score
                            ),
                            "ease": (
                                ease_score
                            ),
                            "fit": (
                                fit_score
                            ),
                            "repeatability": (
                                repeatability_score
                            ),
                            "satisfaction": (
                                satisfaction_score
                            ),
                        },
                        "decision": decision,
                        "final_reflection": (
                            final_reflection.strip()
                        ),
                        "status": next_status,
                    }
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
        "📈 学びと実践の分析"
    )

    if not learnings:
        st.info(
            "分析できるデータがありません。"
        )

    else:
        analysis_rows = []

        for learning in learnings:
            analysis_rows.append(
                {
                    "タイトル": (
                        display_name(
                            learning
                        )
                    ),
                    "カテゴリー": (
                        learning.get(
                            "category",
                            ""
                        )
                    ),
                    "学び元": (
                        learning.get(
                            "source_type",
                            ""
                        )
                    ),
                    "状態": (
                        learning.get(
                            "status",
                            ""
                        )
                    ),
                    "優先度": (
                        learning.get(
                            "priority",
                            ""
                        )
                    ),
                    "実践回数": int(
                        learning.get(
                            "practice_count",
                            0
                        )
                    ),
                    "目標回数": int(
                        learning.get(
                            "target_count",
                            1
                        )
                    ),
                    "進捗率": round(
                        calculate_progress(
                            learning
                        ),
                        1
                    ),
                    "平均評価": round(
                        calculate_average_score(
                            learning
                        ),
                        2
                    ),
                    "期限切れ": (
                        "はい"
                        if is_overdue(
                            learning
                        )
                        else "いいえ"
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
                登録件数=(
                    "タイトル",
                    "count"
                ),
                実践回数=(
                    "実践回数",
                    "sum"
                ),
            )
            .sort_values(
                "実践回数",
                ascending=False
            )
        )

        st.bar_chart(
            category_summary.set_index(
                "カテゴリー"
            )[["実践回数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "学び元別"
        )

        source_summary = (
            analysis_df.groupby(
                "学び元",
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
            source_summary.set_index(
                "学び元"
            )[["件数"]]
        )

        st.dataframe(
            source_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "実践回数ランキング"
        )

        practice_ranking = (
            analysis_df.sort_values(
                "実践回数",
                ascending=False
            )[
                [
                    "タイトル",
                    "実践回数",
                    "目標回数",
                    "進捗率",
                    "状態",
                ]
            ]
        )

        st.dataframe(
            practice_ranking,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "効果の高い学び"
        )

        rated_learnings = (
            analysis_df[
                analysis_df[
                    "平均評価"
                ]
                > 0
            ]
            .sort_values(
                "平均評価",
                ascending=False
            )
        )

        if rated_learnings.empty:
            st.info(
                "評価済みの学びはありません。"
            )

        else:
            st.dataframe(
                rated_learnings[
                    [
                        "タイトル",
                        "平均評価",
                        "実践回数",
                        "状態",
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.subheader(
            "月別実践回数"
        )

        monthly_log_rows = []

        for learning in learnings:
            for log in learning.get(
                "logs",
                []
            ):
                log_date = parse_date(
                    log.get(
                        "log_date",
                        ""
                    )
                )

                if log_date:
                    monthly_log_rows.append(
                        {
                            "月": (
                                log_date.strftime(
                                    "%Y-%m"
                                )
                            ),
                            "実践回数": 1,
                        }
                    )

        if monthly_log_rows:
            monthly_log_df = (
                pd.DataFrame(
                    monthly_log_rows
                )
            )

            monthly_summary = (
                monthly_log_df.groupby(
                    "月",
                    as_index=False
                )["実践回数"]
                .sum()
                .sort_values(
                    "月"
                )
            )

            st.bar_chart(
                monthly_summary.set_index(
                    "月"
                )[["実践回数"]]
            )

            st.dataframe(
                monthly_summary,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "実践ログがまだありません。"
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
            f"learning_backup_"
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
                or "learnings"
                not in imported_data
                or not isinstance(
                    imported_data[
                        "learnings"
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
        "登録した学びと実践ログがすべて削除されます。"
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
    "学びは、実践して振り返ることで自分の力になります。🧠"
)
