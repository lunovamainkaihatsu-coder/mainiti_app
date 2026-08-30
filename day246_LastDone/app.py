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
    page_title="最後にやったのいつ？",
    page_icon="🕐",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "last_done_data.json",
)

CATEGORIES = [
    "掃除",
    "メンテナンス",
    "交換",
    "健康・身だしなみ",
    "車",
    "デジタル",
    "家事",
    "整理整頓",
    "その他",
]


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def create_empty_data():
    return {
        "items": []
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

        if not isinstance(
            data,
            dict,
        ):
            data = create_empty_data()

        data.setdefault(
            "items",
            [],
        )

        for item in data["items"]:
            item.setdefault(
                "id",
                create_id(),
            )

            item.setdefault(
                "name",
                "",
            )

            item.setdefault(
                "category",
                "その他",
            )

            item.setdefault(
                "last_done",
                str(date.today()),
            )

            item.setdefault(
                "target_days",
                30,
            )

            item.setdefault(
                "memo",
                "",
            )

            item.setdefault(
                "history",
                [],
            )

            item.setdefault(
                "created_at",
                "",
            )

            item.setdefault(
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
        save_data(data)

        return data


# =========================================================
# 補助関数
# =========================================================

def get_item_by_id(
    data,
    item_id,
):
    return next(
        (
            item
            for item in data["items"]
            if item.get("id") == item_id
        ),
        None,
    )


def parse_date(
    date_text,
):
    try:
        return datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

    except (
        ValueError,
        TypeError,
    ):
        return date.today()


def days_since(
    date_text,
):
    target = parse_date(
        date_text
    )

    return (
        date.today()
        - target
    ).days


def format_date(
    date_text,
):
    target = parse_date(
        date_text
    )

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
        target.weekday()
    ]

    return target.strftime(
        f"%Y年%m月%d日（{weekday}）"
    )


def get_status(
    item,
):
    elapsed = days_since(
        item.get(
            "last_done",
            str(date.today()),
        )
    )

    target_days = max(
        1,
        int(
            item.get(
                "target_days",
                30,
            )
        ),
    )

    ratio = (
        elapsed
        / target_days
    )

    if elapsed >= target_days:
        return (
            "🔴 超過",
            f"目安から{elapsed - target_days}日経過",
        )

    if ratio >= 0.7:
        return (
            "🟡 そろそろ",
            f"あと{target_days - elapsed}日",
        )

    return (
        "🟢 まだ大丈夫",
        f"あと{target_days - elapsed}日",
    )


# =========================================================
# データ操作
# =========================================================

def add_item(
    data,
    name,
    category,
    last_done,
    target_days,
    memo,
):
    data["items"].append(
        {
            "id": create_id(),
            "name": name,
            "category": category,
            "last_done": str(last_done),
            "target_days": int(
                target_days
            ),
            "memo": memo,
            "history": [
                {
                    "date": str(last_done),
                    "created_at": now_text(),
                }
            ],
            "created_at": now_text(),
            "updated_at": "",
        }
    )

    save_data(data)


def mark_done_today(
    data,
    item_id,
):
    item = get_item_by_id(
        data,
        item_id,
    )

    if not item:
        return

    today_text = str(
        date.today()
    )

    item["last_done"] = (
        today_text
    )

    history = item.setdefault(
        "history",
        [],
    )

    if not any(
        record.get("date")
        == today_text
        for record in history
    ):
        history.append(
            {
                "date": today_text,
                "created_at": now_text(),
            }
        )

    item["updated_at"] = (
        now_text()
    )

    save_data(data)


def update_item(
    data,
    item_id,
    name,
    category,
    last_done,
    target_days,
    memo,
):
    item = get_item_by_id(
        data,
        item_id,
    )

    if not item:
        return

    item["name"] = name
    item["category"] = category
    item["last_done"] = str(
        last_done
    )
    item["target_days"] = int(
        target_days
    )
    item["memo"] = memo
    item["updated_at"] = (
        now_text()
    )

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
        background: rgba(80, 150, 255, 0.07);
        border: 1px solid rgba(80, 150, 255, 0.15);
        border-radius: 15px;
        padding: 15px;
    }

    .hero {
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(80, 150, 255, 0.16),
                rgba(120, 210, 180, 0.10)
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

    .days-box {
        padding: 15px;
        border-radius: 16px;
        text-align: center;
        background: rgba(80, 150, 255, 0.06);
        margin-bottom: 10px;
    }

    .days-number {
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

items = data["items"]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🕐 最後にやったのいつ？</h1>

        <p>
            定期的にやることを、
            「最後にいつやったか」で管理しよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

overdue_count = 0
soon_count = 0

for item in items:
    status, _ = get_status(
        item
    )

    if status == "🔴 超過":
        overdue_count += 1

    elif status == "🟡 そろそろ":
        soon_count += 1


today_done_count = 0

for item in items:
    history = item.get(
        "history",
        [],
    )

    if any(
        record.get("date")
        == str(date.today())
        for record in history
    ):
        today_done_count += 1


columns = st.columns(
    4
)

columns[0].metric(
    "登録",
    f"{len(items)}個",
)

columns[1].metric(
    "🔴 超過",
    f"{overdue_count}個",
)

columns[2].metric(
    "🟡 そろそろ",
    f"{soon_count}個",
)

columns[3].metric(
    "今日やった",
    f"{today_done_count}個",
)


# =========================================================
# 新規追加
# =========================================================

st.divider()

st.subheader(
    "➕ 新しい項目"
)

with st.form(
    "add_item_form"
):
    name = st.text_input(
        "何を管理する？",
        placeholder=(
            "例：洗車"
        ),
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    last_done = st.date_input(
        "最後にやった日",
        value=date.today(),
        max_value=date.today(),
    )

    target_days = st.number_input(
        "何日くらいでまたやりたい？",
        min_value=1,
        max_value=3650,
        value=30,
        step=1,
    )

    memo = st.text_input(
        "メモ",
        placeholder=(
            "例：月1回くらいが目安"
        ),
    )

    submitted = (
        st.form_submit_button(
            "🕐 登録する",
            use_container_width=True,
        )
    )

    if submitted:
        if not name.strip():
            st.error(
                "項目名を入力してください。"
            )

        else:
            add_item(
                data,
                name.strip(),
                category,
                last_done,
                target_days,
                memo.strip(),
            )

            st.success(
                "登録しました！"
            )

            st.rerun()


# =========================================================
# 一覧
# =========================================================

st.divider()

st.subheader(
    "📋 一覧"
)

if not items:
    st.info(
        "まだ項目がありません。"
    )

else:
    sorted_items = sorted(
        items,
        key=lambda item: (
            days_since(
                item.get(
                    "last_done",
                    str(
                        date.today()
                    ),
                )
            )
            / max(
                1,
                item.get(
                    "target_days",
                    30,
                ),
            )
        ),
        reverse=True,
    )

    for item in sorted_items:
        item_id = item.get(
            "id",
            "",
        )

        elapsed = days_since(
            item.get(
                "last_done",
                "",
            )
        )

        target_days = int(
            item.get(
                "target_days",
                30,
            )
        )

        status, status_message = (
            get_status(
                item
            )
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### {status} "
                f"{item.get('name', '')}"
            )

            st.caption(
                f"{item.get('category', '')}"
            )

            st.markdown(
                f"""
                <div class="days-box">
                    <div class="days-number">
                        {elapsed}日前
                    </div>

                    <div>
                        最後：
                        {format_date(item.get('last_done', ''))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write(
                f"🎯 目安："
                f"{target_days}日ごと"
            )

            if status == "🔴 超過":
                st.error(
                    status_message
                )

            elif status == "🟡 そろそろ":
                st.warning(
                    status_message
                )

            else:
                st.success(
                    status_message
                )

            if item.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{item.get('memo', '')}"
                )

            if st.button(
                "✅ 今日やった！",
                key=(
                    f"done_"
                    f"{item_id}"
                ),
                use_container_width=True,
            ):
                mark_done_today(
                    data,
                    item_id,
                )

                st.rerun()

            # -----------------------------------------
            # 編集
            # -----------------------------------------

            with st.expander(
                "✏️ 編集"
            ):
                edit_name = st.text_input(
                    "項目名",
                    value=item.get(
                        "name",
                        "",
                    ),
                    key=(
                        f"edit_name_"
                        f"{item_id}"
                    ),
                )

                current_category = (
                    item.get(
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
                            else 0
                        ),
                        key=(
                            f"edit_category_"
                            f"{item_id}"
                        ),
                    )
                )

                edit_last_done = (
                    st.date_input(
                        "最後にやった日",
                        value=parse_date(
                            item.get(
                                "last_done",
                                str(date.today()),
                            )
                        ),
                        max_value=date.today(),
                        key=(
                            f"edit_last_done_"
                            f"{item_id}"
                        ),
                    )
                )

                edit_target_days = (
                    st.number_input(
                        "目安日数",
                        min_value=1,
                        max_value=3650,
                        value=int(
                            item.get(
                                "target_days",
                                30,
                            )
                        ),
                        step=1,
                        key=(
                            f"edit_target_"
                            f"{item_id}"
                        ),
                    )
                )

                edit_memo = st.text_input(
                    "メモ",
                    value=item.get(
                        "memo",
                        "",
                    ),
                    key=(
                        f"edit_memo_"
                        f"{item_id}"
                    ),
                )

                if st.button(
                    "💾 変更を保存",
                    key=(
                        f"save_edit_"
                        f"{item_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_name.strip():
                        st.error(
                            "項目名を入力してください。"
                        )

                    else:
                        update_item(
                            data,
                            item_id,
                            edit_name.strip(),
                            edit_category,
                            edit_last_done,
                            edit_target_days,
                            edit_memo.strip(),
                        )

                        st.rerun()

            # -----------------------------------------
            # 履歴
            # -----------------------------------------

            with st.expander(
                "📅 実行履歴"
            ):
                history = sorted(
                    item.get(
                        "history",
                        [],
                    ),
                    key=lambda record: (
                        record.get(
                            "date",
                            "",
                        )
                    ),
                    reverse=True,
                )

                if not history:
                    st.caption(
                        "履歴はまだありません。"
                    )

                else:
                    for record in history:
                        st.write(
                            "✅ "
                            + format_date(
                                record.get(
                                    "date",
                                    "",
                                )
                            )
                        )

            # -----------------------------------------
            # 削除
            # -----------------------------------------

            with st.expander(
                "🗑️ 削除"
            ):
                st.warning(
                    "削除すると実行履歴も消えます。"
                )

                if st.button(
                    "この項目を削除",
                    key=(
                        f"delete_"
                        f"{item_id}"
                    ),
                    use_container_width=True,
                ):
                    delete_item(
                        data,
                        item_id,
                    )

                    st.rerun()


# =========================================================
# カテゴリー集計
# =========================================================

if items:
    st.divider()

    st.subheader(
        "📊 カテゴリー"
    )

    category_rows = []

    for category_name in CATEGORIES:
        count = len(
            [
                item
                for item in items
                if item.get(
                    "category"
                )
                == category_name
            ]
        )

        if count > 0:
            category_rows.append(
                {
                    "カテゴリー": (
                        category_name
                    ),
                    "登録数": count,
                }
            )

    if category_rows:
        category_df = pd.DataFrame(
            category_rows
        ).sort_values(
            "登録数",
            ascending=False,
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 全実行履歴
# =========================================================

st.divider()

with st.expander(
    "🗓️ 最近の実行履歴"
):
    history_rows = []

    for item in items:
        for record in item.get(
            "history",
            [],
        ):
            history_rows.append(
                {
                    "日付": record.get(
                        "date",
                        "",
                    ),
                    "項目": item.get(
                        "name",
                        "",
                    ),
                    "カテゴリー": item.get(
                        "category",
                        "",
                    ),
                }
            )

    if not history_rows:
        st.caption(
            "まだ実行履歴がありません。"
        )

    else:
        history_df = pd.DataFrame(
            history_rows
        ).sort_values(
            "日付",
            ascending=False,
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
            f"last_done_backup_"
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
    "「いつやったっけ？」を、もう覚えておかなくていい。🕐"
)
