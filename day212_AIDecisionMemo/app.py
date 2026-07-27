import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =====================================
# ページ設定
# =====================================

st.set_page_config(
    page_title="AI決断メモ",
    page_icon="⚖️",
    layout="wide"
)


DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "decision_data.json"
)


STATUSES = [
    "検討中",
    "情報収集中",
    "決断済み",
    "保留",
    "振り返り済み"
]


STATUS_ICONS = {
    "検討中": "🤔",
    "情報収集中": "🔍",
    "決断済み": "✅",
    "保留": "⏸️",
    "振り返り済み": "📘"
}


CATEGORIES = [
    "仕事",
    "転職",
    "引っ越し",
    "家族",
    "お金",
    "買い物",
    "健康",
    "学び",
    "人間関係",
    "旅行",
    "起業",
    "アプリ開発",
    "その他"
]


PRIORITIES = [
    "最重要",
    "高",
    "中",
    "低"
]


PRIORITY_ICONS = {
    "最重要": "🔥",
    "高": "🔴",
    "中": "🟡",
    "低": "🔵"
}


PRIORITY_ORDER = {
    "最重要": 0,
    "高": 1,
    "中": 2,
    "低": 3
}


DEFAULT_CRITERIA = [
    "費用",
    "将来性",
    "安心感",
    "実現しやすさ",
    "家族との相性",
    "自分の気持ち"
]


SCORE_LABELS = {
    1: "かなり低い",
    2: "低い",
    3: "普通",
    4: "高い",
    5: "とても高い"
}


# =====================================
# データ管理
# =====================================

def create_empty_data():
    """初期データを作成する。"""

    return {
        "decisions": []
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


def load_data():
    """JSONファイルからデータを読み込む。"""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "保存データの形式が正しくありません。"
            )

        data.setdefault(
            "decisions",
            []
        )

        for decision in data["decisions"]:
            decision.setdefault(
                "title",
                ""
            )

            decision.setdefault(
                "category",
                "その他"
            )

            decision.setdefault(
                "priority",
                "中"
            )

            decision.setdefault(
                "status",
                "検討中"
            )

            decision.setdefault(
                "deadline",
                ""
            )

            decision.setdefault(
                "background",
                ""
            )

            decision.setdefault(
                "important_values",
                ""
            )

            decision.setdefault(
                "expectation",
                ""
            )

            decision.setdefault(
                "anxiety",
                ""
            )

            decision.setdefault(
                "intuition",
                ""
            )

            decision.setdefault(
                "criteria",
                list(
                    DEFAULT_CRITERIA
                )
            )

            decision.setdefault(
                "options",
                []
            )

            decision.setdefault(
                "final_choice",
                ""
            )

            decision.setdefault(
                "decision_reason",
                ""
            )

            decision.setdefault(
                "decided_date",
                ""
            )

            decision.setdefault(
                "result",
                ""
            )

            decision.setdefault(
                "learning",
                ""
            )

            decision.setdefault(
                "review_date",
                ""
            )

            decision.setdefault(
                "created_at",
                ""
            )

            decision.setdefault(
                "updated_at",
                ""
            )

            for option in decision["options"]:
                option.setdefault(
                    "id",
                    create_id()
                )

                option.setdefault(
                    "name",
                    ""
                )

                option.setdefault(
                    "merits",
                    ""
                )

                option.setdefault(
                    "demerits",
                    ""
                )

                option.setdefault(
                    "memo",
                    ""
                )

                option.setdefault(
                    "scores",
                    {}
                )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError
    ):
        empty_data = create_empty_data()
        save_data(empty_data)
        return empty_data


# =====================================
# 補助関数
# =====================================

def create_id():
    """一意のIDを生成する。"""

    return str(
        uuid.uuid4()
    )


def now_text():
    """現在日時を文字列で返す。"""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def parse_date_text(
    date_text
):
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


def format_date(
    date_text
):
    """日付を日本語形式にする。"""

    parsed_date = parse_date_text(
        date_text
    )

    if not parsed_date:
        return "未設定"

    return parsed_date.strftime(
        "%Y年%m月%d日"
    )


def get_decision_by_id(
    data,
    decision_id
):
    """IDから決断メモを取得する。"""

    for decision in data["decisions"]:
        if decision.get(
            "id"
        ) == decision_id:
            return decision

    return None


def get_days_until_deadline(
    decision
):
    """決断期限までの日数を取得する。"""

    deadline = parse_date_text(
        decision.get(
            "deadline",
            ""
        )
    )

    if not deadline:
        return None

    return (
        deadline - date.today()
    ).days


def get_deadline_message(
    decision
):
    """期限の状態を表示する。"""

    if decision.get(
        "status"
    ) in [
        "決断済み",
        "振り返り済み"
    ]:
        return "決断済み"

    days_left = get_days_until_deadline(
        decision
    )

    if days_left is None:
        return "期限なし"

    if days_left < 0:
        return (
            f"{abs(days_left)}日超過"
        )

    if days_left == 0:
        return "今日が期限"

    return f"あと{days_left}日"


def calculate_option_score(
    option,
    criteria
):
    """選択肢の合計点と平均点を計算する。"""

    scores = option.get(
        "scores",
        {}
    )

    valid_scores = [
        int(
            scores.get(
                criterion,
                3
            )
        )
        for criterion in criteria
    ]

    if not valid_scores:
        return 0, 0.0

    total_score = sum(
        valid_scores
    )

    average_score = (
        total_score
        / len(valid_scores)
    )

    return (
        total_score,
        average_score
    )


def get_best_option(
    decision
):
    """評価点が最も高い選択肢を取得する。"""

    options = decision.get(
        "options",
        []
    )

    criteria = decision.get(
        "criteria",
        []
    )

    if not options or not criteria:
        return None

    scored_options = []

    for option in options:
        total_score, average_score = (
            calculate_option_score(
                option,
                criteria
            )
        )

        scored_options.append(
            {
                "option": option,
                "total": total_score,
                "average": average_score
            }
        )

    scored_options.sort(
        key=lambda item: item[
            "total"
        ],
        reverse=True
    )

    return scored_options[0]


def count_this_month_decisions(
    decisions
):
    """今月決断した件数を数える。"""

    today = date.today()
    count = 0

    for decision in decisions:
        decided_date = parse_date_text(
            decision.get(
                "decided_date",
                ""
            )
        )

        if (
            decided_date
            and decided_date.year
            == today.year
            and decided_date.month
            == today.month
        ):
            count += 1

    return count


def count_pending_reviews(
    decisions
):
    """振り返りが未完了の決断数を取得する。"""

    return len(
        [
            decision
            for decision in decisions
            if (
                decision.get(
                    "status"
                ) == "決断済み"
                and not decision.get(
                    "result",
                    ""
                ).strip()
            )
        ]
    )


def split_lines(
    text
):
    """複数行テキストをリストへ変換する。"""

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


# =====================================
# データ操作
# =====================================

def add_decision(
    data,
    title,
    category,
    priority,
    deadline,
    background,
    important_values,
    expectation,
    anxiety,
    intuition,
    criteria,
    option_names
):
    """新しい決断メモを登録する。"""

    options = []

    for option_name in option_names:
        scores = {
            criterion: 3
            for criterion in criteria
        }

        options.append(
            {
                "id": create_id(),
                "name": option_name,
                "merits": "",
                "demerits": "",
                "memo": "",
                "scores": scores
            }
        )

    decision = {
        "id": create_id(),
        "title": title,
        "category": category,
        "priority": priority,
        "status": "検討中",
        "deadline": (
            str(deadline)
            if deadline
            else ""
        ),
        "background": background,
        "important_values": (
            important_values
        ),
        "expectation": expectation,
        "anxiety": anxiety,
        "intuition": intuition,
        "criteria": criteria,
        "options": options,
        "final_choice": "",
        "decision_reason": "",
        "decided_date": "",
        "result": "",
        "learning": "",
        "review_date": "",
        "created_at": now_text(),
        "updated_at": ""
    }

    data["decisions"].append(
        decision
    )

    save_data(data)


def update_basic_info(
    data,
    decision_id,
    title,
    category,
    priority,
    status,
    deadline,
    background,
    important_values,
    expectation,
    anxiety,
    intuition
):
    """基本情報を更新する。"""

    decision = get_decision_by_id(
        data,
        decision_id
    )

    if not decision:
        return

    decision["title"] = title
    decision["category"] = category
    decision["priority"] = priority
    decision["status"] = status
    decision["deadline"] = (
        str(deadline)
        if deadline
        else ""
    )
    decision["background"] = background
    decision["important_values"] = (
        important_values
    )
    decision["expectation"] = expectation
    decision["anxiety"] = anxiety
    decision["intuition"] = intuition
    decision["updated_at"] = now_text()

    save_data(data)


def update_criteria(
    data,
    decision_id,
    criteria
):
    """判断基準を更新する。"""

    decision = get_decision_by_id(
        data,
        decision_id
    )

    if not decision:
        return

    old_criteria = decision.get(
        "criteria",
        []
    )

    decision["criteria"] = criteria

    for option in decision.get(
        "options",
        []
    ):
        old_scores = option.get(
            "scores",
            {}
        )

        option["scores"] = {
            criterion: old_scores.get(
                criterion,
                3
            )
            for criterion in criteria
        }

    decision["updated_at"] = now_text()

    save_data(data)


def add_option(
    data,
    decision_id,
    option_name
):
    """選択肢を追加する。"""

    decision = get_decision_by_id(
        data,
        decision_id
    )

    if not decision:
        return

    scores = {
        criterion: 3
        for criterion in decision.get(
            "criteria",
            []
        )
    }

    decision["options"].append(
        {
            "id": create_id(),
            "name": option_name,
            "merits": "",
            "demerits": "",
            "memo": "",
            "scores": scores
        }
    )

    decision["updated_at"] = now_text()

    save_data(data)


def update_option(
    data,
    decision_id,
    option_id,
    name,
    merits,
    demerits,
    memo,
    scores
):
    """選択肢を更新する。"""

    decision = get_decision_by_id(
        data,
        decision_id
    )

    if not decision:
        return

    for option in decision.get(
        "options",
        []
    ):
        if option.get(
            "id"
        ) == option_id:
            option["name"] = name
            option["merits"] = merits
            option["demerits"] = demerits
            option["memo"] = memo
            option["scores"] = scores
            break

    decision["updated_at"] = now_text()

    save_data(data)


def delete_option(
    data,
    decision_id,
    option_id
):
    """選択肢を削除する。"""

    decision = get_decision_by_id(
        data,
        decision_id
    )

    if not decision:
        return

    decision["options"] = [
        option
        for option in decision.get(
            "options",
            []
        )
        if option.get(
            "id"
        ) != option_id
    ]

    decision["updated_at"] = now_text()

    save_data(data)


def save_final_decision(
    data,
    decision_id,
    final_choice,
    decision_reason,
    decided_date
):
    """最終決定を保存する。"""

    decision = get_decision_by_id(
        data,
        decision_id
    )

    if not decision:
        return

    decision["final_choice"] = (
        final_choice
    )
    decision["decision_reason"] = (
        decision_reason
    )
    decision["decided_date"] = str(
        decided_date
    )
    decision["status"] = "決断済み"
    decision["updated_at"] = now_text()

    save_data(data)


def save_review(
    data,
    decision_id,
    result,
    learning,
    review_date
):
    """決断後の振り返りを保存する。"""

    decision = get_decision_by_id(
        data,
        decision_id
    )

    if not decision:
        return

    decision["result"] = result
    decision["learning"] = learning
    decision["review_date"] = str(
        review_date
    )
    decision["status"] = "振り返り済み"
    decision["updated_at"] = now_text()

    save_data(data)


def delete_decision(
    data,
    decision_id
):
    """決断メモを削除する。"""

    data["decisions"] = [
        decision
        for decision in data["decisions"]
        if decision.get(
            "id"
        ) != decision_id
    ]

    save_data(data)


# =====================================
# データ読み込み
# =====================================

data = load_data()

decisions = data["decisions"]


# =====================================
# タイトル
# =====================================

st.title(
    "⚖️ AI決断メモ"
)

st.caption(
    "迷いを言葉と数字で整理して、"
    "自分らしい決断を支えるアプリです。"
)

st.info(
    "このアプリの点数は、答えを決めるものではありません。"
    "気持ちや大切にしたい価値観を整理する補助として使いましょう。"
)


# =====================================
# ダッシュボード
# =====================================

st.divider()

st.header(
    "📊 ダッシュボード"
)

thinking_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status"
        ) == "検討中"
    ]
)

collecting_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status"
        ) == "情報収集中"
    ]
)

decided_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status"
        ) in [
            "決断済み",
            "振り返り済み"
        ]
    ]
)

holding_count = len(
    [
        decision
        for decision in decisions
        if decision.get(
            "status"
        ) == "保留"
    ]
)

monthly_decision_count = (
    count_this_month_decisions(
        decisions
    )
)

pending_review_count = (
    count_pending_reviews(
        decisions
    )
)


metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6 = (
    st.columns(6)
)

with metric_col1:
    st.metric(
        "総メモ数",
        f"{len(decisions)}件"
    )

with metric_col2:
    st.metric(
        "検討中",
        f"{thinking_count}件"
    )

with metric_col3:
    st.metric(
        "情報収集中",
        f"{collecting_count}件"
    )

with metric_col4:
    st.metric(
        "決断済み",
        f"{decided_count}件"
    )

with metric_col5:
    st.metric(
        "今月の決断",
        f"{monthly_decision_count}件"
    )

with metric_col6:
    st.metric(
        "未振り返り",
        f"{pending_review_count}件"
    )


# =====================================
# 期限が近い決断
# =====================================

urgent_decisions = []

for decision in decisions:
    if decision.get(
        "status"
    ) in [
        "決断済み",
        "振り返り済み",
        "保留"
    ]:
        continue

    days_left = get_days_until_deadline(
        decision
    )

    if (
        days_left is not None
        and days_left <= 7
    ):
        urgent_decisions.append(
            decision
        )


if urgent_decisions:
    st.divider()

    st.header(
        "⏰ 期限が近い決断"
    )

    urgent_decisions = sorted(
        urgent_decisions,
        key=lambda decision: (
            get_days_until_deadline(
                decision
            )
        )
    )

    for decision in urgent_decisions:
        days_left = get_days_until_deadline(
            decision
        )

        with st.container(
            border=True
        ):
            st.subheader(
                f"{PRIORITY_ICONS.get(decision.get('priority', ''), '')} "
                f"{decision.get('title', '')}"
            )

            if days_left is not None:
                if days_left < 0:
                    st.error(
                        f"期限を"
                        f"{abs(days_left)}日過ぎています。"
                    )

                elif days_left == 0:
                    st.warning(
                        "今日が決断期限です。"
                    )

                else:
                    st.warning(
                        f"期限まであと"
                        f"{days_left}日です。"
                    )


# =====================================
# タブ
# =====================================

st.divider()

add_tab, list_tab, compare_tab, result_tab, analysis_tab = (
    st.tabs(
        [
            "➕ 新しい決断",
            "📋 決断メモ一覧",
            "⚖️ 選択肢比較",
            "📘 決断と振り返り",
            "📈 集計"
        ]
    )
)


# =====================================
# 新規登録
# =====================================

with add_tab:
    st.header(
        "➕ 新しい決断を整理する"
    )

    with st.form(
        "add_decision_form",
        clear_on_submit=True
    ):
        form_col1, form_col2 = (
            st.columns(2)
        )

        with form_col1:
            title = st.text_input(
                "悩んでいること",
                placeholder=(
                    "例：次の引っ越し先をどこにするか"
                )
            )

            category = st.selectbox(
                "カテゴリー",
                CATEGORIES
            )

            priority = st.selectbox(
                "重要度",
                PRIORITIES,
                index=2
            )

            has_deadline = st.checkbox(
                "決断期限を設定する"
            )

            deadline = None

            if has_deadline:
                deadline = st.date_input(
                    "決断期限",
                    value=(
                        date.today()
                        + timedelta(
                            days=14
                        )
                    ),
                    min_value=date.today()
                )

            background = st.text_area(
                "背景・現在の状況",
                placeholder=(
                    "なぜこの決断が必要なのか、"
                    "現在どんな状況なのか"
                ),
                height=120
            )

        with form_col2:
            important_values = st.text_area(
                "大切にしたいこと",
                placeholder=(
                    "例：家族の暮らしやすさ、"
                    "費用、将来性、安心感"
                ),
                height=100
            )

            expectation = st.text_area(
                "期待していること",
                placeholder=(
                    "この決断で実現したいこと"
                ),
                height=80
            )

            anxiety = st.text_area(
                "不安に感じていること",
                placeholder=(
                    "失敗した場合に心配なこと"
                ),
                height=80
            )

            intuition = st.text_area(
                "今の直感",
                placeholder=(
                    "点数とは別に、"
                    "本心ではどう感じているか"
                ),
                height=80
            )

        st.subheader(
            "⚖️ 選択肢"
        )

        option_text = st.text_area(
            "選択肢を1行ずつ入力",
            placeholder=(
                "茅ヶ崎\n"
                "平塚\n"
                "秦野\n"
                "その他"
            ),
            height=130
        )

        st.subheader(
            "📏 判断基準"
        )

        default_criteria_text = "\n".join(
            DEFAULT_CRITERIA
        )

        criteria_text = st.text_area(
            "判断基準を1行ずつ入力",
            value=default_criteria_text,
            height=160
        )

        submit = st.form_submit_button(
            "✨ 決断メモを作成",
            use_container_width=True
        )

        if submit:
            cleaned_title = title.strip()
            option_names = split_lines(
                option_text
            )
            criteria = split_lines(
                criteria_text
            )

            duplicate_title = any(
                decision.get(
                    "title",
                    ""
                ).strip().lower()
                == cleaned_title.lower()
                for decision in decisions
            )

            if not cleaned_title:
                st.error(
                    "悩んでいることを入力してください。"
                )

            elif duplicate_title:
                st.warning(
                    "同じタイトルの決断メモが存在します。"
                )

            elif len(option_names) < 2:
                st.error(
                    "選択肢を2つ以上入力してください。"
                )

            elif not criteria:
                st.error(
                    "判断基準を1つ以上入力してください。"
                )

            else:
                add_decision(
                    data=data,
                    title=cleaned_title,
                    category=category,
                    priority=priority,
                    deadline=deadline,
                    background=background.strip(),
                    important_values=(
                        important_values.strip()
                    ),
                    expectation=expectation.strip(),
                    anxiety=anxiety.strip(),
                    intuition=intuition.strip(),
                    criteria=criteria,
                    option_names=option_names
                )

                st.success(
                    "決断メモを作成しました！"
                )

                st.rerun()


# =====================================
# 一覧
# =====================================

with list_tab:
    st.header(
        "📋 決断メモ一覧"
    )

    if not decisions:
        st.info(
            "決断メモはまだありません。"
        )

    else:
        filter_col1, filter_col2, filter_col3 = (
            st.columns(3)
        )

        with filter_col1:
            search_keyword = st.text_input(
                "🔍 キーワード検索",
                placeholder=(
                    "タイトル・背景・価値観"
                ),
                key="decision_search"
            )

        with filter_col2:
            status_filter = st.selectbox(
                "状態",
                [
                    "すべて"
                ] + STATUSES,
                key="decision_status_filter"
            )

        with filter_col3:
            category_filter = st.selectbox(
                "カテゴリー",
                [
                    "すべて"
                ] + CATEGORIES,
                key="decision_category_filter"
            )

        priority_filter = st.multiselect(
            "重要度",
            PRIORITIES,
            default=PRIORITIES
        )

        sort_option = st.selectbox(
            "並び順",
            [
                "重要度順",
                "登録が新しい順",
                "期限が近い順",
                "状態順"
            ]
        )

        filtered_decisions = list(
            decisions
        )

        if search_keyword:
            keyword = (
                search_keyword.strip().lower()
            )

            filtered_decisions = [
                decision
                for decision in filtered_decisions
                if (
                    keyword
                    in decision.get(
                        "title",
                        ""
                    ).lower()
                    or keyword
                    in decision.get(
                        "background",
                        ""
                    ).lower()
                    or keyword
                    in decision.get(
                        "important_values",
                        ""
                    ).lower()
                    or keyword
                    in decision.get(
                        "expectation",
                        ""
                    ).lower()
                    or keyword
                    in decision.get(
                        "anxiety",
                        ""
                    ).lower()
                )
            ]

        if status_filter != "すべて":
            filtered_decisions = [
                decision
                for decision in filtered_decisions
                if decision.get(
                    "status"
                ) == status_filter
            ]

        if category_filter != "すべて":
            filtered_decisions = [
                decision
                for decision in filtered_decisions
                if decision.get(
                    "category"
                ) == category_filter
            ]

        filtered_decisions = [
            decision
            for decision in filtered_decisions
            if decision.get(
                "priority",
                "中"
            ) in priority_filter
        ]

        if sort_option == "重要度順":
            filtered_decisions = sorted(
                filtered_decisions,
                key=lambda decision: (
                    PRIORITY_ORDER.get(
                        decision.get(
                            "priority",
                            "中"
                        ),
                        99
                    ),
                    decision.get(
                        "created_at",
                        ""
                    )
                )
            )

        elif sort_option == "登録が新しい順":
            filtered_decisions = sorted(
                filtered_decisions,
                key=lambda decision: decision.get(
                    "created_at",
                    ""
                ),
                reverse=True
            )

        elif sort_option == "期限が近い順":
            filtered_decisions = sorted(
                filtered_decisions,
                key=lambda decision: (
                    get_days_until_deadline(
                        decision
                    )
                    if get_days_until_deadline(
                        decision
                    ) is not None
                    else 999999
                )
            )

        else:
            filtered_decisions = sorted(
                filtered_decisions,
                key=lambda decision: (
                    STATUSES.index(
                        decision.get(
                            "status",
                            "検討中"
                        )
                    )
                    if decision.get(
                        "status"
                    ) in STATUSES
                    else 99
                )
            )

        st.write(
            f"表示件数："
            f"**{len(filtered_decisions)}件**"
        )

        for decision in filtered_decisions:
            decision_id = decision.get(
                "id",
                ""
            )

            best_option = get_best_option(
                decision
            )

            with st.container(
                border=True
            ):
                title_col, status_col = (
                    st.columns([4, 1])
                )

                with title_col:
                    st.subheader(
                        f"{PRIORITY_ICONS.get(decision.get('priority', ''), '')} "
                        f"{decision.get('title', '')}"
                    )

                    st.caption(
                        f"{decision.get('category', '')} "
                        f"／ {decision.get('priority', '')} "
                        f"／ {STATUS_ICONS.get(decision.get('status', ''), '')} "
                        f"{decision.get('status', '')}"
                    )

                with status_col:
                    st.metric(
                        "期限",
                        get_deadline_message(
                            decision
                        )
                    )

                if decision.get(
                    "background",
                    ""
                ):
                    st.write(
                        f"📝 **背景：**"
                        f"{decision.get('background', '')}"
                    )

                if decision.get(
                    "important_values",
                    ""
                ):
                    st.info(
                        f"💎 大切にしたいこと\n\n"
                        f"{decision.get('important_values', '')}"
                    )

                st.write(
                    f"⚖️ 選択肢："
                    f"**{len(decision.get('options', []))}個**"
                )

                if best_option:
                    st.success(
                        f"現在の評価1位："
                        f"**{best_option['option'].get('name', '')}** "
                        f"（平均 {best_option['average']:.2f}点）"
                    )

                if decision.get(
                    "final_choice",
                    ""
                ):
                    st.success(
                        f"✅ 最終決定："
                        f"**{decision.get('final_choice', '')}**"
                    )

                with st.expander(
                    "✏️ 基本情報を編集"
                ):
                    edit_title = st.text_input(
                        "悩んでいること",
                        value=decision.get(
                            "title",
                            ""
                        ),
                        key=(
                            f"edit_title_{decision_id}"
                        )
                    )

                    current_category = decision.get(
                        "category",
                        "その他"
                    )

                    category_index = (
                        CATEGORIES.index(
                            current_category
                        )
                        if current_category
                        in CATEGORIES
                        else 0
                    )

                    edit_category = st.selectbox(
                        "カテゴリー",
                        CATEGORIES,
                        index=category_index,
                        key=(
                            f"edit_category_{decision_id}"
                        )
                    )

                    current_priority = decision.get(
                        "priority",
                        "中"
                    )

                    priority_index = (
                        PRIORITIES.index(
                            current_priority
                        )
                        if current_priority
                        in PRIORITIES
                        else 2
                    )

                    edit_priority = st.selectbox(
                        "重要度",
                        PRIORITIES,
                        index=priority_index,
                        key=(
                            f"edit_priority_{decision_id}"
                        )
                    )

                    current_status = decision.get(
                        "status",
                        "検討中"
                    )

                    status_index = (
                        STATUSES.index(
                            current_status
                        )
                        if current_status
                        in STATUSES
                        else 0
                    )

                    edit_status = st.selectbox(
                        "状態",
                        STATUSES,
                        index=status_index,
                        key=(
                            f"edit_status_{decision_id}"
                        )
                    )

                    current_deadline = parse_date_text(
                        decision.get(
                            "deadline",
                            ""
                        )
                    )

                    edit_has_deadline = st.checkbox(
                        "決断期限を設定する",
                        value=bool(
                            current_deadline
                        ),
                        key=(
                            f"edit_has_deadline_{decision_id}"
                        )
                    )

                    edit_deadline = None

                    if edit_has_deadline:
                        edit_deadline = st.date_input(
                            "決断期限",
                            value=(
                                current_deadline
                                or date.today()
                            ),
                            key=(
                                f"edit_deadline_{decision_id}"
                            )
                        )

                    edit_background = st.text_area(
                        "背景・現在の状況",
                        value=decision.get(
                            "background",
                            ""
                        ),
                        key=(
                            f"edit_background_{decision_id}"
                        )
                    )

                    edit_values = st.text_area(
                        "大切にしたいこと",
                        value=decision.get(
                            "important_values",
                            ""
                        ),
                        key=(
                            f"edit_values_{decision_id}"
                        )
                    )

                    edit_expectation = st.text_area(
                        "期待していること",
                        value=decision.get(
                            "expectation",
                            ""
                        ),
                        key=(
                            f"edit_expectation_{decision_id}"
                        )
                    )

                    edit_anxiety = st.text_area(
                        "不安に感じていること",
                        value=decision.get(
                            "anxiety",
                            ""
                        ),
                        key=(
                            f"edit_anxiety_{decision_id}"
                        )
                    )

                    edit_intuition = st.text_area(
                        "今の直感",
                        value=decision.get(
                            "intuition",
                            ""
                        ),
                        key=(
                            f"edit_intuition_{decision_id}"
                        )
                    )

                    if st.button(
                        "基本情報を保存",
                        key=(
                            f"save_basic_{decision_id}"
                        ),
                        use_container_width=True
                    ):
                        if not edit_title.strip():
                            st.error(
                                "タイトルを入力してください。"
                            )

                        else:
                            update_basic_info(
                                data=data,
                                decision_id=decision_id,
                                title=edit_title.strip(),
                                category=edit_category,
                                priority=edit_priority,
                                status=edit_status,
                                deadline=edit_deadline,
                                background=(
                                    edit_background.strip()
                                ),
                                important_values=(
                                    edit_values.strip()
                                ),
                                expectation=(
                                    edit_expectation.strip()
                                ),
                                anxiety=(
                                    edit_anxiety.strip()
                                ),
                                intuition=(
                                    edit_intuition.strip()
                                )
                            )

                            st.success(
                                "基本情報を更新しました！"
                            )

                            st.rerun()

                with st.expander(
                    "🗑️ 決断メモを削除"
                ):
                    st.warning(
                        "削除したデータは元に戻せません。"
                    )

                    confirm_delete = st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_delete_{decision_id}"
                        )
                    )

                    if st.button(
                        "この決断メモを削除",
                        key=(
                            f"delete_decision_{decision_id}"
                        ),
                        disabled=(
                            not confirm_delete
                        ),
                        use_container_width=True
                    ):
                        delete_decision(
                            data,
                            decision_id
                        )

                        st.rerun()


# =====================================
# 選択肢比較
# =====================================

with compare_tab:
    st.header(
        "⚖️ 選択肢を比較する"
    )

    if not decisions:
        st.info(
            "比較する決断メモがありません。"
        )

    else:
        decision_options = {
            decision.get(
                "title",
                "名称なし"
            ): decision.get(
                "id"
            )
            for decision in decisions
        }

        selected_title = st.selectbox(
            "比較する決断メモ",
            list(
                decision_options.keys()
            ),
            key="compare_decision"
        )

        selected_decision = (
            get_decision_by_id(
                data,
                decision_options[
                    selected_title
                ]
            )
        )

        if selected_decision:
            decision_id = selected_decision.get(
                "id",
                ""
            )

            st.subheader(
                selected_decision.get(
                    "title",
                    ""
                )
            )

            if selected_decision.get(
                "important_values",
                ""
            ):
                st.info(
                    f"💎 大切にしたいこと\n\n"
                    f"{selected_decision.get('important_values', '')}"
                )

            if selected_decision.get(
                "intuition",
                ""
            ):
                st.warning(
                    f"💭 現在の直感\n\n"
                    f"{selected_decision.get('intuition', '')}"
                )

            st.divider()

            st.subheader(
                "📏 判断基準"
            )

            criteria_text = st.text_area(
                "判断基準を1行ずつ入力",
                value="\n".join(
                    selected_decision.get(
                        "criteria",
                        []
                    )
                ),
                key=(
                    f"criteria_text_{decision_id}"
                )
            )

            if st.button(
                "判断基準を更新",
                key=(
                    f"save_criteria_{decision_id}"
                )
            ):
                new_criteria = split_lines(
                    criteria_text
                )

                if not new_criteria:
                    st.error(
                        "判断基準を1つ以上入力してください。"
                    )

                else:
                    update_criteria(
                        data,
                        decision_id,
                        new_criteria
                    )

                    st.success(
                        "判断基準を更新しました！"
                    )

                    st.rerun()

            st.divider()

            st.subheader(
                "➕ 選択肢を追加"
            )

            new_option_name = st.text_input(
                "新しい選択肢",
                placeholder=(
                    "例：藤沢"
                ),
                key=(
                    f"new_option_{decision_id}"
                )
            )

            if st.button(
                "選択肢を追加",
                key=(
                    f"add_option_{decision_id}"
                )
            ):
                if not new_option_name.strip():
                    st.error(
                        "選択肢名を入力してください。"
                    )

                else:
                    duplicate_option = any(
                        option.get(
                            "name",
                            ""
                        ).strip().lower()
                        == new_option_name.strip().lower()
                        for option
                        in selected_decision.get(
                            "options",
                            []
                        )
                    )

                    if duplicate_option:
                        st.warning(
                            "同じ選択肢が存在します。"
                        )

                    else:
                        add_option(
                            data,
                            decision_id,
                            new_option_name.strip()
                        )

                        st.rerun()

            st.divider()

            options = selected_decision.get(
                "options",
                []
            )

            criteria = selected_decision.get(
                "criteria",
                []
            )

            if not options:
                st.warning(
                    "選択肢がありません。"
                )

            else:
                score_rows = []

                for option in options:
                    total_score, average_score = (
                        calculate_option_score(
                            option,
                            criteria
                        )
                    )

                    row = {
                        "選択肢": option.get(
                            "name",
                            ""
                        ),
                        "合計点": total_score,
                        "平均点": round(
                            average_score,
                            2
                        )
                    }

                    for criterion in criteria:
                        row[criterion] = (
                            option.get(
                                "scores",
                                {}
                            ).get(
                                criterion,
                                3
                            )
                        )

                    score_rows.append(
                        row
                    )

                score_df = pd.DataFrame(
                    score_rows
                )

                score_df = score_df.sort_values(
                    "合計点",
                    ascending=False
                )

                st.subheader(
                    "🏆 現在の比較結果"
                )

                st.dataframe(
                    score_df,
                    use_container_width=True,
                    hide_index=True
                )

                chart_df = (
                    score_df[
                        [
                            "選択肢",
                            "合計点"
                        ]
                    ]
                    .set_index(
                        "選択肢"
                    )
                )

                st.bar_chart(
                    chart_df
                )

                best_option = get_best_option(
                    selected_decision
                )

                if best_option:
                    st.success(
                        f"現在の評価1位は "
                        f"**{best_option['option'].get('name', '')}** "
                        f"です。平均点は"
                        f" **{best_option['average']:.2f}点** です。"
                    )

                st.caption(
                    "点数が高い選択肢が、必ず正しいとは限りません。"
                    "直感や家族との話し合いも大切にしてください。"
                )

                st.divider()

                st.subheader(
                    "✏️ 選択肢の詳細・評価"
                )

                for option in options:
                    option_id = option.get(
                        "id",
                        ""
                    )

                    with st.expander(
                        f"⚖️ {option.get('name', '')}",
                        expanded=False
                    ):
                        option_name = st.text_input(
                            "選択肢名",
                            value=option.get(
                                "name",
                                ""
                            ),
                            key=(
                                f"option_name_{option_id}"
                            )
                        )

                        merits = st.text_area(
                            "⭕ メリット",
                            value=option.get(
                                "merits",
                                ""
                            ),
                            placeholder=(
                                "良い点を1行ずつ整理"
                            ),
                            key=(
                                f"merits_{option_id}"
                            )
                        )

                        demerits = st.text_area(
                            "❌ デメリット",
                            value=option.get(
                                "demerits",
                                ""
                            ),
                            placeholder=(
                                "不安な点や弱点を整理"
                            ),
                            key=(
                                f"demerits_{option_id}"
                            )
                        )

                        option_memo = st.text_area(
                            "📝 補足メモ",
                            value=option.get(
                                "memo",
                                ""
                            ),
                            key=(
                                f"option_memo_{option_id}"
                            )
                        )

                        st.markdown(
                            "#### 5段階評価"
                        )

                        updated_scores = {}

                        for criterion in criteria:
                            current_score = int(
                                option.get(
                                    "scores",
                                    {}
                                ).get(
                                    criterion,
                                    3
                                )
                            )

                            score = st.slider(
                                criterion,
                                min_value=1,
                                max_value=5,
                                value=current_score,
                                help=(
                                    "1＝かなり低い、"
                                    "5＝とても高い"
                                ),
                                key=(
                                    f"score_{option_id}_{criterion}"
                                )
                            )

                            updated_scores[
                                criterion
                            ] = score

                            st.caption(
                                SCORE_LABELS.get(
                                    score,
                                    ""
                                )
                            )

                        total_score = sum(
                            updated_scores.values()
                        )

                        average_score = (
                            total_score
                            / len(updated_scores)
                            if updated_scores
                            else 0
                        )

                        score_col1, score_col2 = (
                            st.columns(2)
                        )

                        with score_col1:
                            st.metric(
                                "合計点",
                                total_score
                            )

                        with score_col2:
                            st.metric(
                                "平均点",
                                f"{average_score:.2f}"
                            )

                        if st.button(
                            "選択肢を保存",
                            key=(
                                f"save_option_{option_id}"
                            ),
                            use_container_width=True
                        ):
                            if not option_name.strip():
                                st.error(
                                    "選択肢名を入力してください。"
                                )

                            else:
                                update_option(
                                    data=data,
                                    decision_id=decision_id,
                                    option_id=option_id,
                                    name=option_name.strip(),
                                    merits=merits.strip(),
                                    demerits=demerits.strip(),
                                    memo=option_memo.strip(),
                                    scores=updated_scores
                                )

                                st.success(
                                    "選択肢を更新しました！"
                                )

                                st.rerun()

                        if len(options) > 2:
                            confirm_option_delete = (
                                st.checkbox(
                                    "この選択肢を削除する",
                                    key=(
                                        f"confirm_option_delete_{option_id}"
                                    )
                                )
                            )

                            if st.button(
                                "選択肢を削除",
                                key=(
                                    f"delete_option_{option_id}"
                                ),
                                disabled=(
                                    not confirm_option_delete
                                ),
                                use_container_width=True
                            ):
                                delete_option(
                                    data,
                                    decision_id,
                                    option_id
                                )

                                st.rerun()


# =====================================
# 決断と振り返り
# =====================================

with result_tab:
    st.header(
        "📘 最終決定と振り返り"
    )

    if not decisions:
        st.info(
            "対象となる決断メモがありません。"
        )

    else:
        result_options = {
            decision.get(
                "title",
                "名称なし"
            ): decision.get(
                "id"
            )
            for decision in decisions
        }

        selected_result_title = st.selectbox(
            "決断メモを選択",
            list(
                result_options.keys()
            ),
            key="result_decision"
        )

        result_decision = get_decision_by_id(
            data,
            result_options[
                selected_result_title
            ]
        )

        if result_decision:
            decision_id = result_decision.get(
                "id",
                ""
            )

            best_option = get_best_option(
                result_decision
            )

            if best_option:
                st.info(
                    f"点数上の1位："
                    f"**{best_option['option'].get('name', '')}** "
                    f"（平均 {best_option['average']:.2f}点）"
                )

            if result_decision.get(
                "intuition",
                ""
            ):
                st.warning(
                    f"記録した直感：\n\n"
                    f"{result_decision.get('intuition', '')}"
                )

            st.subheader(
                "✅ 最終決定"
            )

            option_names = [
                option.get(
                    "name",
                    ""
                )
                for option in result_decision.get(
                    "options",
                    []
                )
            ]

            current_final_choice = (
                result_decision.get(
                    "final_choice",
                    ""
                )
            )

            final_choice_options = (
                option_names
                + [
                    "その他・複数案"
                ]
            )

            if (
                current_final_choice
                and current_final_choice
                not in final_choice_options
            ):
                final_choice_options.append(
                    current_final_choice
                )

            final_choice_index = (
                final_choice_options.index(
                    current_final_choice
                )
                if current_final_choice
                in final_choice_options
                else 0
            )

            selected_final_choice = st.selectbox(
                "最終的に選んだもの",
                final_choice_options,
                index=final_choice_index,
                key=(
                    f"final_choice_{decision_id}"
                )
            )

            custom_final_choice = ""

            if selected_final_choice == "その他・複数案":
                custom_final_choice = (
                    st.text_input(
                        "決定内容を入力",
                        value=(
                            current_final_choice
                            if current_final_choice
                            not in option_names
                            else ""
                        ),
                        key=(
                            f"custom_final_choice_{decision_id}"
                        )
                    )
                )

            decision_reason = st.text_area(
                "決めた理由",
                value=result_decision.get(
                    "decision_reason",
                    ""
                ),
                placeholder=(
                    "点数、直感、家族との話し合いなど、"
                    "最終的な決め手"
                ),
                height=140,
                key=(
                    f"decision_reason_{decision_id}"
                )
            )

            current_decided_date = (
                parse_date_text(
                    result_decision.get(
                        "decided_date",
                        ""
                    )
                )
                or date.today()
            )

            decided_date = st.date_input(
                "決断日",
                value=current_decided_date,
                max_value=date.today(),
                key=(
                    f"decided_date_{decision_id}"
                )
            )

            if st.button(
                "✅ 最終決定を保存",
                key=(
                    f"save_final_{decision_id}"
                ),
                use_container_width=True
            ):
                final_choice = (
                    custom_final_choice.strip()
                    if selected_final_choice
                    == "その他・複数案"
                    else selected_final_choice
                )

                if not final_choice:
                    st.error(
                        "最終決定を入力してください。"
                    )

                elif not decision_reason.strip():
                    st.error(
                        "決めた理由を入力してください。"
                    )

                else:
                    save_final_decision(
                        data=data,
                        decision_id=decision_id,
                        final_choice=final_choice,
                        decision_reason=(
                            decision_reason.strip()
                        ),
                        decided_date=decided_date
                    )

                    st.success(
                        "最終決定を保存しました！"
                    )

                    st.balloons()
                    st.rerun()

            if result_decision.get(
                "final_choice",
                ""
            ):
                st.divider()

                st.subheader(
                    "🔍 決断後の振り返り"
                )

                st.success(
                    f"最終決定："
                    f"**{result_decision.get('final_choice', '')}**"
                )

                result_text = st.text_area(
                    "実際の結果",
                    value=result_decision.get(
                        "result",
                        ""
                    ),
                    placeholder=(
                        "選んだ結果、何が起きたか。"
                        "満足した点や想定外だった点"
                    ),
                    height=160,
                    key=(
                        f"review_result_{decision_id}"
                    )
                )

                learning_text = st.text_area(
                    "この決断から学んだこと",
                    value=result_decision.get(
                        "learning",
                        ""
                    ),
                    placeholder=(
                        "次の決断に生かせる学びや、"
                        "自分が本当に大切にしていたこと"
                    ),
                    height=160,
                    key=(
                        f"review_learning_{decision_id}"
                    )
                )

                current_review_date = (
                    parse_date_text(
                        result_decision.get(
                            "review_date",
                            ""
                        )
                    )
                    or date.today()
                )

                review_date = st.date_input(
                    "振り返り日",
                    value=current_review_date,
                    max_value=date.today(),
                    key=(
                        f"review_date_{decision_id}"
                    )
                )

                if st.button(
                    "📘 振り返りを保存",
                    key=(
                        f"save_review_{decision_id}"
                    ),
                    use_container_width=True
                ):
                    if not result_text.strip():
                        st.error(
                            "実際の結果を入力してください。"
                        )

                    elif not learning_text.strip():
                        st.error(
                            "学んだことを入力してください。"
                        )

                    else:
                        save_review(
                            data=data,
                            decision_id=decision_id,
                            result=result_text.strip(),
                            learning=learning_text.strip(),
                            review_date=review_date
                        )

                        st.success(
                            "振り返りを保存しました！"
                        )

                        st.rerun()


# =====================================
# 集計
# =====================================

with analysis_tab:
    st.header(
        "📈 決断データの集計"
    )

    if not decisions:
        st.info(
            "集計できるデータがありません。"
        )

    else:
        decision_rows = []

        for decision in decisions:
            decision_rows.append(
                {
                    "タイトル": decision.get(
                        "title",
                        ""
                    ),
                    "カテゴリー": decision.get(
                        "category",
                        ""
                    ),
                    "重要度": decision.get(
                        "priority",
                        ""
                    ),
                    "状態": decision.get(
                        "status",
                        ""
                    ),
                    "選択肢数": len(
                        decision.get(
                            "options",
                            []
                        )
                    ),
                    "決断日": decision.get(
                        "decided_date",
                        ""
                    )
                }
            )

        decision_df = pd.DataFrame(
            decision_rows
        )

        st.subheader(
            "📋 状態別件数"
        )

        status_summary = (
            decision_df.groupby(
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
            "📂 カテゴリー別件数"
        )

        category_summary = (
            decision_df.groupby(
                "カテゴリー",
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
            category_summary.set_index(
                "カテゴリー"
            )[["件数"]]
        )

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "🔥 重要度別件数"
        )

        priority_summary = (
            decision_df.groupby(
                "重要度",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "件数"
                }
            )
        )

        priority_summary[
            "並び順"
        ] = priority_summary[
            "重要度"
        ].map(
            PRIORITY_ORDER
        )

        priority_summary = (
            priority_summary.sort_values(
                "並び順"
            )
            .drop(
                columns=[
                    "並び順"
                ]
            )
        )

        st.bar_chart(
            priority_summary.set_index(
                "重要度"
            )[["件数"]]
        )

        st.dataframe(
            priority_summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(
            "⚖️ 平均選択肢数"
        )

        average_option_count = (
            decision_df[
                "選択肢数"
            ].mean()
        )

        st.metric(
            "1つの決断あたりの平均選択肢数",
            f"{average_option_count:.1f}個"
        )

        reviewed_decisions = [
            decision
            for decision in decisions
            if decision.get(
                "status"
            ) == "振り返り済み"
        ]

        if reviewed_decisions:
            st.divider()

            st.subheader(
                "📘 過去の決断からの学び"
            )

            for decision in sorted(
                reviewed_decisions,
                key=lambda item: item.get(
                    "review_date",
                    ""
                ),
                reverse=True
            ):
                with st.container(
                    border=True
                ):
                    st.subheader(
                        decision.get(
                            "title",
                            ""
                        )
                    )

                    st.write(
                        f"✅ 決断："
                        f"**{decision.get('final_choice', '')}**"
                    )

                    if decision.get(
                        "learning",
                        ""
                    ):
                        st.info(
                            f"💡 学び\n\n"
                            f"{decision.get('learning', '')}"
                        )


st.divider()

st.success(
    "良い決断とは、迷わないことではなく、"
    "自分が何を大切にしたか理解できる決断です。⚖️"
)
