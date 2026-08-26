import json
import os
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="やる？やらない？",
    page_icon="🤔",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "decision_data.json",
)

DECISIONS = [
    "🔥 やる！",
    "🙅 やらない",
]

RESULTS = [
    "未評価",
    "😄 よかった",
    "😐 普通",
    "😣 微妙だった",
]


# =========================================================
# データ管理
# =========================================================

def create_empty_data():
    return {
        "decisions": []
    }


def create_id():
    return str(
        uuid.uuid4()
    )


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


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
        data = create_empty_data()

        save_data(
            data
        )

        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

        if not isinstance(
            data,
            dict,
        ):
            data = create_empty_data()

        data.setdefault(
            "decisions",
            [],
        )

        for decision in data[
            "decisions"
        ]:
            decision.setdefault(
                "id",
                create_id(),
            )

            decision.setdefault(
                "date",
                str(
                    date.today()
                ),
            )

            decision.setdefault(
                "question",
                "",
            )

            decision.setdefault(
                "decision",
                "🔥 やる！",
            )

            decision.setdefault(
                "reason",
                "",
            )

            decision.setdefault(
                "result",
                "未評価",
            )

            decision.setdefault(
                "result_memo",
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

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = create_empty_data()

        save_data(
            data
        )

        return data


# =========================================================
# 補助関数
# =========================================================

def get_decision_by_id(
    data,
    decision_id,
):
    for decision in data[
        "decisions"
    ]:
        if decision.get(
            "id"
        ) == decision_id:
            return decision

    return None


def format_datetime(
    text,
):
    if not text:
        return ""

    try:
        target = datetime.fromisoformat(
            text
        )

        return target.strftime(
            "%Y/%m/%d %H:%M"
        )

    except ValueError:
        return text


def result_score(
    result,
):
    scores = {
        "😄 よかった": 3,
        "😐 普通": 2,
        "😣 微妙だった": 1,
        "未評価": 0,
    }

    return scores.get(
        result,
        0,
    )


# =========================================================
# データ操作
# =========================================================

def add_decision(
    data,
    question,
    decision,
    reason,
):
    record = {
        "id": create_id(),
        "date": str(
            date.today()
        ),
        "question": question,
        "decision": decision,
        "reason": reason,
        "result": "未評価",
        "result_memo": "",
        "created_at": now_text(),
        "updated_at": "",
    }

    data[
        "decisions"
    ].append(
        record
    )

    save_data(
        data
    )


def update_result(
    data,
    decision_id,
    result,
    result_memo,
):
    record = get_decision_by_id(
        data,
        decision_id,
    )

    if not record:
        return

    record[
        "result"
    ] = result

    record[
        "result_memo"
    ] = result_memo

    record[
        "updated_at"
    ] = now_text()

    save_data(
        data
    )


def update_decision(
    data,
    decision_id,
    question,
    decision,
    reason,
):
    record = get_decision_by_id(
        data,
        decision_id,
    )

    if not record:
        return

    record[
        "question"
    ] = question

    record[
        "decision"
    ] = decision

    record[
        "reason"
    ] = reason

    record[
        "updated_at"
    ] = now_text()

    save_data(
        data
    )


def delete_decision(
    data,
    decision_id,
):
    data[
        "decisions"
    ] = [
        decision
        for decision
        in data[
            "decisions"
        ]
        if decision.get(
            "id"
        ) != decision_id
    ]

    save_data(
        data
    )


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
        background: rgba(120, 150, 255, 0.08);
        border: 1px solid rgba(120, 150, 255, 0.18);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 22px;
        border-radius: 20px;
        margin-bottom: 20px;
        background:
            linear-gradient(
                135deg,
                rgba(120, 150, 255, 0.18),
                rgba(200, 120, 255, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.75;
    }

    .decision-box {
        text-align: center;
        padding: 24px;
        border-radius: 18px;
        background: rgba(120, 150, 255, 0.06);
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .decision-question {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .decision-answer {
        font-size: 2rem;
        font-weight: 800;
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

today_text = str(
    date.today()
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🤔 やる？やらない？</h1>
        <p>
            迷ったら決める。
            決めたら理由をひとこと残す。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

today_decisions = [
    decision
    for decision in decisions
    if decision.get(
        "date"
    ) == today_text
]

today_do = [
    decision
    for decision in today_decisions
    if decision.get(
        "decision"
    ) == "🔥 やる！"
]

today_not = [
    decision
    for decision in today_decisions
    if decision.get(
        "decision"
    ) == "🙅 やらない"
]


columns = st.columns(
    4
)

columns[0].metric(
    "今日の決断",
    f"{len(today_decisions)}件",
)

columns[1].metric(
    "やる",
    f"{len(today_do)}件",
)

columns[2].metric(
    "やらない",
    f"{len(today_not)}件",
)

columns[3].metric(
    "累計",
    f"{len(decisions)}件",
)


# =========================================================
# 新しい決断
# =========================================================

st.divider()

st.subheader(
    "⚡ 今ここで決める"
)

with st.form(
    "decision_form",
    clear_on_submit=True,
):
    question = st.text_input(
        "何を迷ってる？",
        placeholder=(
            "例：今日はジムに行く？"
        ),
    )

    decision = st.radio(
        "決断",
        DECISIONS,
        horizontal=True,
    )

    reason = st.text_input(
        "理由をひとこと",
        placeholder=(
            "例：30分だけでも行ってみる"
        ),
    )

    submitted = (
        st.form_submit_button(
            "⚡ 決める！",
            use_container_width=True,
        )
    )

    if submitted:
        if not question.strip():
            st.error(
                "迷っていることを入力してください。"
            )

        else:
            add_decision(
                data,
                question.strip(),
                decision,
                reason.strip(),
            )

            st.success(
                "決断しました！"
            )

            st.rerun()


# =========================================================
# 今日の決断
# =========================================================

st.divider()

st.subheader(
    "📌 今日の決断"
)

if not today_decisions:
    st.info(
        "今日はまだ決断を記録していません。"
    )

else:
    today_decisions = sorted(
        today_decisions,
        key=lambda decision: (
            decision.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )

    for record in today_decisions:
        decision_id = record[
            "id"
        ]

        st.markdown(
            f"""
            <div class="decision-box">
                <div class="decision-question">
                    {record.get('question', '')}
                </div>

                <div class="decision-answer">
                    {record.get('decision', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if record.get(
            "reason",
            "",
        ):
            st.write(
                f"理由："
                f"「{record.get('reason', '')}」"
            )

        st.caption(
            format_datetime(
                record.get(
                    "created_at",
                    "",
                )
            )
        )

        # -------------------------------------------------
        # 結果振り返り
        # -------------------------------------------------

        with st.expander(
            "🔍 結果を振り返る"
        ):
            current_result = record.get(
                "result",
                "未評価",
            )

            result = st.selectbox(
                "結果はどうだった？",
                RESULTS,
                index=(
                    RESULTS.index(
                        current_result
                    )
                    if current_result
                    in RESULTS
                    else 0
                ),
                key=(
                    f"result_"
                    f"{decision_id}"
                ),
            )

            result_memo = st.text_input(
                "結果メモ",
                value=record.get(
                    "result_memo",
                    "",
                ),
                placeholder=(
                    "例：行ってみたら気分転換になった"
                ),
                key=(
                    f"result_memo_"
                    f"{decision_id}"
                ),
            )

            if st.button(
                "結果を保存",
                key=(
                    f"save_result_"
                    f"{decision_id}"
                ),
                use_container_width=True,
            ):
                update_result(
                    data,
                    decision_id,
                    result,
                    result_memo.strip(),
                )

                st.rerun()

        # -------------------------------------------------
        # 編集
        # -------------------------------------------------

        with st.expander(
            "✏️ 編集"
        ):
            edit_question = st.text_input(
                "内容",
                value=record.get(
                    "question",
                    "",
                ),
                key=(
                    f"edit_question_"
                    f"{decision_id}"
                ),
            )

            current_decision = record.get(
                "decision",
                "🔥 やる！",
            )

            edit_decision = st.radio(
                "決断",
                DECISIONS,
                index=(
                    DECISIONS.index(
                        current_decision
                    )
                    if current_decision
                    in DECISIONS
                    else 0
                ),
                horizontal=True,
                key=(
                    f"edit_decision_"
                    f"{decision_id}"
                ),
            )

            edit_reason = st.text_input(
                "理由",
                value=record.get(
                    "reason",
                    "",
                ),
                key=(
                    f"edit_reason_"
                    f"{decision_id}"
                ),
            )

            if st.button(
                "変更を保存",
                key=(
                    f"save_edit_"
                    f"{decision_id}"
                ),
                use_container_width=True,
            ):
                if not edit_question.strip():
                    st.error(
                        "内容を入力してください。"
                    )

                else:
                    update_decision(
                        data,
                        decision_id,
                        edit_question.strip(),
                        edit_decision,
                        edit_reason.strip(),
                    )

                    st.rerun()

        # -------------------------------------------------
        # 削除
        # -------------------------------------------------

        with st.expander(
            "🗑️ 削除"
        ):
            if st.button(
                "この決断を削除",
                key=(
                    f"delete_"
                    f"{decision_id}"
                ),
                use_container_width=True,
            ):
                delete_decision(
                    data,
                    decision_id,
                )

                st.rerun()


# =========================================================
# 結果分析
# =========================================================

st.divider()

st.subheader(
    "📊 決断の結果"
)

evaluated = [
    decision
    for decision in decisions
    if decision.get(
        "result",
        "未評価",
    )
    != "未評価"
]

if not evaluated:
    st.info(
        "結果を振り返ると、ここに傾向が表示されます。"
    )

else:
    good_results = [
        decision
        for decision in evaluated
        if decision.get(
            "result"
        ) == "😄 よかった"
    ]

    neutral_results = [
        decision
        for decision in evaluated
        if decision.get(
            "result"
        ) == "😐 普通"
    ]

    bad_results = [
        decision
        for decision in evaluated
        if decision.get(
            "result"
        ) == "😣 微妙だった"
    ]

    result_columns = st.columns(
        3
    )

    result_columns[0].metric(
        "😄 よかった",
        f"{len(good_results)}件",
    )

    result_columns[1].metric(
        "😐 普通",
        f"{len(neutral_results)}件",
    )

    result_columns[2].metric(
        "😣 微妙",
        f"{len(bad_results)}件",
    )


# =========================================================
# 「やる」の結果
# =========================================================

do_evaluated = [
    decision
    for decision in evaluated
    if decision.get(
        "decision"
    ) == "🔥 やる！"
]

if do_evaluated:
    do_good = len(
        [
            decision
            for decision in do_evaluated
            if decision.get(
                "result"
            ) == "😄 よかった"
        ]
    )

    do_good_rate = (
        do_good
        / len(do_evaluated)
        * 100
    )

    st.success(
        f"🔥 「やる」を選んだ決断のうち、"
        f"**{do_good_rate:.1f}%** が「よかった」でした。"
    )


# =========================================================
# 「やらない」の結果
# =========================================================

not_evaluated = [
    decision
    for decision in evaluated
    if decision.get(
        "decision"
    ) == "🙅 やらない"
]

if not_evaluated:
    not_good = len(
        [
            decision
            for decision in not_evaluated
            if decision.get(
                "result"
            ) == "😄 よかった"
        ]
    )

    not_good_rate = (
        not_good
        / len(not_evaluated)
        * 100
    )

    st.info(
        f"🙅 「やらない」を選んだ決断のうち、"
        f"**{not_good_rate:.1f}%** が「よかった」でした。"
    )


# =========================================================
# 決断比率
# =========================================================

st.divider()

st.subheader(
    "⚖️ やる？やらない？"
)

if decisions:
    summary_rows = [
        {
            "決断": "🔥 やる！",
            "件数": len(
                [
                    decision
                    for decision in decisions
                    if decision.get(
                        "decision"
                    ) == "🔥 やる！"
                ]
            ),
        },
        {
            "決断": "🙅 やらない",
            "件数": len(
                [
                    decision
                    for decision in decisions
                    if decision.get(
                        "decision"
                    ) == "🙅 やらない"
                ]
            ),
        },
    ]

    summary_df = pd.DataFrame(
        summary_rows
    )

    st.bar_chart(
        summary_df.set_index(
            "決断"
        )
    )


# =========================================================
# 過去履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の決断を見る"
):
    if not decisions:
        st.info(
            "まだ履歴がありません。"
        )

    else:
        sorted_decisions = sorted(
            decisions,
            key=lambda decision: (
                decision.get(
                    "created_at",
                    "",
                )
            ),
            reverse=True,
        )

        history_rows = []

        for decision in sorted_decisions:
            history_rows.append(
                {
                    "日時": (
                        format_datetime(
                            decision.get(
                                "created_at",
                                "",
                            )
                        )
                    ),
                    "迷ったこと": (
                        decision.get(
                            "question",
                            "",
                        )
                    ),
                    "決断": (
                        decision.get(
                            "decision",
                            "",
                        )
                    ),
                    "理由": (
                        decision.get(
                            "reason",
                            "",
                        )
                    ),
                    "結果": (
                        decision.get(
                            "result",
                            "未評価",
                        )
                    ),
                    "結果メモ": (
                        decision.get(
                            "result_memo",
                            "",
                        )
                    ),
                }
            )

        history_df = pd.DataFrame(
            history_rows
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )


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
        "⬇️ JSONバックアップ",
        data=json_text,
        file_name=(
            f"decision_backup_"
            f"{date.today()}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# フッター
# =========================================================

st.divider()

st.caption(
    "迷い続けるより、決めてから考える。🤔⚡"
)
