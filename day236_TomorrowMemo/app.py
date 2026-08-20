import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="明日の自分へ",
    page_icon="📩",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "tomorrow_memo.json",
)

MESSAGE_TYPES = [
    "🔥 応援",
    "🌱 アドバイス",
    "📌 忘れないで",
    "🌙 労わる",
    "💡 アイデア",
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
        "messages": []
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
            "messages",
            [],
        )

        for message in data[
            "messages"
        ]:
            message.setdefault(
                "id",
                create_id(),
            )

            message.setdefault(
                "created_date",
                str(
                    date.today()
                ),
            )

            message.setdefault(
                "show_date",
                str(
                    date.today()
                    + timedelta(
                        days=1
                    )
                ),
            )

            message.setdefault(
                "message_type",
                "🔥 応援",
            )

            message.setdefault(
                "text",
                "",
            )

            message.setdefault(
                "checked",
                False,
            )

            message.setdefault(
                "checked_at",
                "",
            )

            message.setdefault(
                "created_at",
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

def format_date(
    date_text,
):
    try:
        target = datetime.strptime(
            date_text,
            "%Y-%m-%d",
        ).date()

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

    except ValueError:
        return date_text


def get_message_by_id(
    data,
    message_id,
):
    for message in data[
        "messages"
    ]:
        if message.get(
            "id"
        ) == message_id:
            return message

    return None


# =========================================================
# データ操作
# =========================================================

def add_message(
    data,
    message_type,
    text,
):
    created_date = date.today()

    show_date = (
        created_date
        + timedelta(
            days=1
        )
    )

    message = {
        "id": create_id(),
        "created_date": str(
            created_date
        ),
        "show_date": str(
            show_date
        ),
        "message_type": (
            message_type
        ),
        "text": text,
        "checked": False,
        "checked_at": "",
        "created_at": (
            now_text()
        ),
    }

    data[
        "messages"
    ].append(
        message
    )

    save_data(
        data
    )


def mark_checked(
    data,
    message_id,
):
    message = (
        get_message_by_id(
            data,
            message_id,
        )
    )

    if not message:
        return

    message[
        "checked"
    ] = True

    message[
        "checked_at"
    ] = now_text()

    save_data(
        data
    )


def update_message(
    data,
    message_id,
    message_type,
    text,
):
    message = (
        get_message_by_id(
            data,
            message_id,
        )
    )

    if not message:
        return

    message[
        "message_type"
    ] = message_type

    message[
        "text"
    ] = text

    save_data(
        data
    )


def delete_message(
    data,
    message_id,
):
    data[
        "messages"
    ] = [
        message
        for message
        in data[
            "messages"
        ]
        if message.get(
            "id"
        )
        != message_id
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
        background: rgba(110, 150, 255, 0.08);
        border: 1px solid rgba(110, 150, 255, 0.18);
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
                rgba(110, 150, 255, 0.18),
                rgba(180, 120, 255, 0.10)
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

    .letter {
        padding: 20px;
        border-radius: 18px;
        background: rgba(110, 150, 255, 0.06);
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

messages = data[
    "messages"
]

today = date.today()

today_text = str(
    today
)

tomorrow_text = str(
    today
    + timedelta(
        days=1
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📩 明日の自分へ</h1>
        <p>
            今日の自分から、
            明日の自分へ一言だけ残すメモ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 今日届いたメッセージ
# =========================================================

today_messages = [
    message
    for message in messages
    if (
        message.get(
            "show_date"
        )
        <= today_text
        and not message.get(
            "checked",
            False,
        )
    )
]


checked_messages = [
    message
    for message in messages
    if message.get(
        "checked",
        False,
    )
]


tomorrow_messages = [
    message
    for message in messages
    if (
        message.get(
            "show_date"
        )
        == tomorrow_text
        and not message.get(
            "checked",
            False,
        )
    )
]


columns = st.columns(
    3
)

columns[0].metric(
    "今日届いた",
    f"{len(today_messages)}件",
)

columns[1].metric(
    "確認済み",
    f"{len(checked_messages)}件",
)

columns[2].metric(
    "明日へのメモ",
    f"{len(tomorrow_messages)}件",
)


# =========================================================
# 今日のメッセージ
# =========================================================

st.divider()

st.subheader(
    "📬 今日の自分へ届いたメッセージ"
)

if not today_messages:
    st.info(
        "今日はまだメッセージが届いていません。"
    )

else:
    today_messages = sorted(
        today_messages,
        key=lambda message: (
            message.get(
                "show_date",
                "",
            ),
            message.get(
                "created_at",
                "",
            ),
        ),
    )

    for message in today_messages:
        message_id = message[
            "id"
        ]

        st.markdown(
            f"""
            <div class="letter">
                <h3>
                    {message.get('message_type', '')}
                </h3>
                <p style="font-size:1.15rem;">
                    {message.get('text', '')}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "書いた日："
            + format_date(
                message.get(
                    "created_date",
                    "",
                )
            )
        )

        if st.button(
            "✅ 読んだ",
            key=(
                f"checked_"
                f"{message_id}"
            ),
            use_container_width=True,
        ):
            mark_checked(
                data,
                message_id,
            )

            st.success(
                "確認済みにしました！"
            )

            st.rerun()


# =========================================================
# 明日の自分へ書く
# =========================================================

st.divider()

st.subheader(
    "✍️ 明日の自分へ"
)

with st.form(
    "tomorrow_message_form",
    clear_on_submit=True,
):
    message_type = (
        st.selectbox(
            "どんなメッセージ？",
            MESSAGE_TYPES,
        )
    )

    text = st.text_area(
        "明日の自分へ一言",
        placeholder=(
            "例：朝起きたら、5分だけ勉強しよう"
        ),
        height=120,
    )

    submitted = (
        st.form_submit_button(
            "📩 明日の自分へ送る",
            use_container_width=True,
        )
    )

    if submitted:
        if not text.strip():
            st.error(
                "メッセージを入力してください。"
            )

        else:
            add_message(
                data,
                message_type,
                text.strip(),
            )

            st.success(
                "明日の自分へメッセージを残しました！"
            )

            st.rerun()


# =========================================================
# 明日届く予定
# =========================================================

st.divider()

st.subheader(
    "🌅 明日届くメッセージ"
)

if not tomorrow_messages:
    st.info(
        "明日へのメッセージはまだありません。"
    )

else:
    for message in tomorrow_messages:
        message_id = message[
            "id"
        ]

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### "
                f"{message.get('message_type', '')}"
            )

            st.write(
                message.get(
                    "text",
                    "",
                )
            )

            st.caption(
                "明日になると「今日届いたメッセージ」に表示されます。"
            )

            with st.expander(
                "✏️ 編集"
            ):
                current_type = (
                    message.get(
                        "message_type",
                        "🔥 応援",
                    )
                )

                edit_type = (
                    st.selectbox(
                        "種類",
                        MESSAGE_TYPES,
                        index=(
                            MESSAGE_TYPES.index(
                                current_type
                            )
                            if current_type
                            in MESSAGE_TYPES
                            else 0
                        ),
                        key=(
                            f"type_"
                            f"{message_id}"
                        ),
                    )
                )

                edit_text = (
                    st.text_area(
                        "メッセージ",
                        value=message.get(
                            "text",
                            "",
                        ),
                        key=(
                            f"text_"
                            f"{message_id}"
                        ),
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"save_"
                        f"{message_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_text.strip():
                        st.error(
                            "メッセージを入力してください。"
                        )

                    else:
                        update_message(
                            data,
                            message_id,
                            edit_type,
                            edit_text.strip(),
                        )

                        st.rerun()

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "このメッセージを削除",
                    key=(
                        f"delete_"
                        f"{message_id}"
                    ),
                    use_container_width=True,
                ):
                    delete_message(
                        data,
                        message_id,
                    )

                    st.rerun()


# =========================================================
# 過去のメッセージ
# =========================================================

st.divider()

st.subheader(
    "📚 過去の自分から"
)

if not checked_messages:
    st.info(
        "確認済みのメッセージはまだありません。"
    )

else:
    checked_messages = sorted(
        checked_messages,
        key=lambda message: (
            message.get(
                "show_date",
                "",
            )
        ),
        reverse=True,
    )

    for message in checked_messages[
        :10
    ]:
        with st.container(
            border=True,
        ):
            st.markdown(
                f"### "
                f"{message.get('message_type', '')}"
            )

            st.write(
                f"「"
                f"{message.get('text', '')}"
                f"」"
            )

            st.caption(
                "届いた日："
                + format_date(
                    message.get(
                        "show_date",
                        "",
                    )
                )
            )


# =========================================================
# 簡単な振り返り
# =========================================================

st.divider()

st.subheader(
    "📊 メッセージの種類"
)

if not messages:
    st.info(
        "まだメッセージがありません。"
    )

else:
    type_rows = []

    for message_type in MESSAGE_TYPES:
        count = len(
            [
                message
                for message in messages
                if message.get(
                    "message_type"
                )
                == message_type
            ]
        )

        if count > 0:
            type_rows.append(
                {
                    "種類": (
                        message_type
                    ),
                    "回数": (
                        count
                    ),
                }
            )

    type_df = pd.DataFrame(
        type_rows
    )

    st.bar_chart(
        type_df.set_index(
            "種類"
        )
    )

    st.dataframe(
        type_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 全履歴
# =========================================================

st.divider()

with st.expander(
    "📜 全メッセージ履歴"
):
    if not messages:
        st.info(
            "メッセージ履歴はありません。"
        )

    else:
        history_rows = []

        sorted_messages = sorted(
            messages,
            key=lambda message: (
                message.get(
                    "created_date",
                    "",
                ),
                message.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        for message in sorted_messages:
            history_rows.append(
                {
                    "書いた日": (
                        message.get(
                            "created_date",
                            "",
                        )
                    ),
                    "届く日": (
                        message.get(
                            "show_date",
                            "",
                        )
                    ),
                    "種類": (
                        message.get(
                            "message_type",
                            "",
                        )
                    ),
                    "メッセージ": (
                        message.get(
                            "text",
                            "",
                        )
                    ),
                    "確認": (
                        "確認済み"
                        if message.get(
                            "checked",
                            False,
                        )
                        else "未確認"
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
            f"tomorrow_memo_backup_"
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
    "今日の自分が、明日の自分を少しだけ助ける。📩"
)
