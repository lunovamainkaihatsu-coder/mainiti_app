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
    page_title="今いくら使った？",
    page_icon="💸",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "expense_data.json",
)

CATEGORIES = [
    "食費",
    "外食",
    "コンビニ",
    "日用品",
    "交通",
    "趣味",
    "子ども",
    "医療",
    "買い物",
    "その他",
]


# =========================================================
# データ管理
# =========================================================

def create_id():
    return str(
        uuid.uuid4()
    )


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "expenses": []
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


def normalize_data(data):
    if not isinstance(
        data,
        dict,
    ):
        data = create_empty_data()

    data.setdefault(
        "expenses",
        [],
    )

    for expense in data[
        "expenses"
    ]:
        expense.setdefault(
            "id",
            create_id(),
        )

        expense.setdefault(
            "date",
            str(
                date.today()
            ),
        )

        expense.setdefault(
            "amount",
            0,
        )

        expense.setdefault(
            "category",
            "その他",
        )

        expense.setdefault(
            "memo",
            "",
        )

        expense.setdefault(
            "created_at",
            "",
        )

    return data


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(
        DATA_FILE
    ):
        data = (
            create_empty_data()
        )

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

        data = normalize_data(
            data
        )

        save_data(
            data
        )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        data = (
            create_empty_data()
        )

        save_data(
            data
        )

        return data


# =========================================================
# 補助関数
# =========================================================

def get_expense_by_id(
    data,
    expense_id,
):
    for expense in data[
        "expenses"
    ]:
        if expense.get(
            "id"
        ) == expense_id:
            return expense

    return None


def format_date(
    date_text,
):
    try:
        target = datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

        return target.strftime(
            "%Y/%m/%d"
        )

    except ValueError:
        return date_text


# =========================================================
# データ操作
# =========================================================

def add_expense(
    data,
    amount,
    category,
    memo,
):
    expense = {
        "id": create_id(),
        "date": str(
            date.today()
        ),
        "amount": int(
            amount
        ),
        "category": category,
        "memo": memo,
        "created_at": (
            now_text()
        ),
    }

    data[
        "expenses"
    ].append(
        expense
    )

    save_data(
        data
    )


def update_expense(
    data,
    expense_id,
    amount,
    category,
    memo,
):
    expense = (
        get_expense_by_id(
            data,
            expense_id,
        )
    )

    if not expense:
        return

    expense[
        "amount"
    ] = int(
        amount
    )

    expense[
        "category"
    ] = category

    expense[
        "memo"
    ] = memo

    save_data(
        data
    )


def delete_expense(
    data,
    expense_id,
):
    data[
        "expenses"
    ] = [
        expense
        for expense
        in data[
            "expenses"
        ]
        if expense.get(
            "id"
        )
        != expense_id
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
        background: rgba(80, 170, 120, 0.08);
        border: 1px solid rgba(80, 170, 120, 0.18);
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
                rgba(80, 170, 120, 0.18),
                rgba(90, 150, 255, 0.10)
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

expenses = data[
    "expenses"
]

today_text = str(
    date.today()
)

current_month = (
    date.today().strftime(
        "%Y-%m"
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>💸 今いくら使った？</h1>
        <p>
            使った瞬間にサッと記録する、
            超シンプル家計メモ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

today_expenses = [
    expense
    for expense in expenses
    if expense.get(
        "date"
    )
    == today_text
]

monthly_expenses = [
    expense
    for expense in expenses
    if expense.get(
        "date",
        "",
    ).startswith(
        current_month
    )
]

today_total = sum(
    int(
        expense.get(
            "amount",
            0,
        )
    )
    for expense
    in today_expenses
)

monthly_total = sum(
    int(
        expense.get(
            "amount",
            0,
        )
    )
    for expense
    in monthly_expenses
)


# =========================================================
# ダッシュボード
# =========================================================

columns = st.columns(
    3
)

columns[0].metric(
    "今日",
    f"{today_total:,}円",
)

columns[1].metric(
    "今月",
    f"{monthly_total:,}円",
)

columns[2].metric(
    "今日の記録",
    f"{len(today_expenses)}件",
)


# =========================================================
# 支出入力
# =========================================================

st.divider()

st.subheader(
    "➕ 今使った金額"
)

with st.form(
    "expense_form",
    clear_on_submit=True,
):
    amount = st.number_input(
        "金額",
        min_value=1,
        max_value=10000000,
        value=500,
        step=10,
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    memo = st.text_input(
        "ひとこと",
        placeholder=(
            "例：昼ごはん"
        ),
    )

    submitted = (
        st.form_submit_button(
            "💾 支出を記録",
            use_container_width=True,
        )
    )

    if submitted:
        add_expense(
            data,
            amount,
            category,
            memo.strip(),
        )

        st.success(
            f"{amount:,}円を記録しました！"
        )

        st.rerun()


# =========================================================
# 今日の支出
# =========================================================

st.divider()

st.subheader(
    "🧾 今日の支出"
)

if not today_expenses:
    st.info(
        "今日はまだ支出を記録していません。"
    )

else:
    today_expenses = sorted(
        today_expenses,
        key=lambda expense: (
            expense.get(
                "created_at",
                "",
            )
        ),
        reverse=True,
    )

    for expense in today_expenses:
        expense_id = expense[
            "id"
        ]

        with st.container(
            border=True,
        ):
            column1, column2 = (
                st.columns(
                    [
                        3,
                        1,
                    ]
                )
            )

            with column1:
                if expense.get(
                    "memo",
                    "",
                ):
                    st.markdown(
                        f"### "
                        f"{expense.get('memo', '')}"
                    )

                else:
                    st.markdown(
                        f"### "
                        f"{expense.get('category', '')}"
                    )

                st.caption(
                    expense.get(
                        "category",
                        "",
                    )
                )

            with column2:
                st.metric(
                    "金額",
                    f"{expense.get('amount', 0):,}円",
                )

            with st.expander(
                "✏️ 編集"
            ):
                edit_amount = (
                    st.number_input(
                        "金額",
                        min_value=1,
                        max_value=10000000,
                        value=int(
                            expense.get(
                                "amount",
                                1,
                            )
                        ),
                        key=(
                            f"edit_amount_"
                            f"{expense_id}"
                        ),
                    )
                )

                current_category = (
                    expense.get(
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
                                len(
                                    CATEGORIES
                                )
                                - 1
                            )
                        ),
                        key=(
                            f"edit_category_"
                            f"{expense_id}"
                        ),
                    )
                )

                edit_memo = (
                    st.text_input(
                        "メモ",
                        value=expense.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"edit_memo_"
                            f"{expense_id}"
                        ),
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_"
                        f"{expense_id}"
                    ),
                    use_container_width=True,
                ):
                    update_expense(
                        data,
                        expense_id,
                        edit_amount,
                        edit_category,
                        edit_memo.strip(),
                    )

                    st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この支出を削除",
                    key=(
                        f"delete_"
                        f"{expense_id}"
                    ),
                    use_container_width=True,
                ):
                    delete_expense(
                        data,
                        expense_id,
                    )

                    st.rerun()

    st.metric(
        "今日の合計",
        f"{today_total:,}円",
    )


# =========================================================
# カテゴリー別
# =========================================================

st.divider()

st.subheader(
    "📊 今月のカテゴリー別"
)

if not monthly_expenses:
    st.info(
        "今月の支出データがありません。"
    )

else:
    category_rows = []

    for category_name in CATEGORIES:
        category_total = sum(
            int(
                expense.get(
                    "amount",
                    0,
                )
            )
            for expense
            in monthly_expenses
            if expense.get(
                "category"
            )
            == category_name
        )

        if category_total > 0:
            category_rows.append(
                {
                    "カテゴリー": (
                        category_name
                    ),
                    "金額": (
                        category_total
                    ),
                }
            )

    category_df = pd.DataFrame(
        category_rows
    )

    category_df = (
        category_df.sort_values(
            "金額",
            ascending=False,
        )
    )

    st.bar_chart(
        category_df.set_index(
            "カテゴリー"
        )
    )

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 過去の履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の支出を見る"
):
    if not expenses:
        st.info(
            "支出履歴はありません。"
        )

    else:
        sorted_expenses = sorted(
            expenses,
            key=lambda expense: (
                expense.get(
                    "date",
                    "",
                ),
                expense.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        history_rows = []

        for expense in sorted_expenses:
            history_rows.append(
                {
                    "日付": (
                        format_date(
                            expense.get(
                                "date",
                                "",
                            )
                        )
                    ),
                    "カテゴリー": (
                        expense.get(
                            "category",
                            "",
                        )
                    ),
                    "メモ": (
                        expense.get(
                            "memo",
                            "",
                        )
                    ),
                    "金額": int(
                        expense.get(
                            "amount",
                            0,
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
            f"expense_backup_"
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
    "細かく管理しすぎない。"
    "使ったら、金額だけサッと残そう。💸"
)
