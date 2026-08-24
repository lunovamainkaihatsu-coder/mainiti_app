import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# ページ設定
# =========================================================

st.set_page_config(
    page_title="5分だけやる！",
    page_icon="⏱️",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "focus_data.json",
)

FOCUS_MINUTES = 5


# =========================================================
# データ管理
# =========================================================

def create_empty_data():
    return {
        "records": []
    }


def create_id():
    return str(uuid.uuid4())


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
            "records",
            [],
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
# 記録
# =========================================================

def add_record(
    data,
    task,
):
    data[
        "records"
    ].append(
        {
            "id": create_id(),
            "date": str(
                date.today()
            ),
            "task": task,
            "minutes": (
                FOCUS_MINUTES
            ),
            "completed_at": (
                now_text()
            ),
        }
    )

    save_data(data)


def delete_record(
    data,
    record_id,
):
    data[
        "records"
    ] = [
        record
        for record
        in data[
            "records"
        ]
        if record.get(
            "id"
        ) != record_id
    ]

    save_data(data)


# =========================================================
# Session State
# =========================================================

if "task" not in st.session_state:
    st.session_state.task = ""

if "timer_started" not in st.session_state:
    st.session_state.timer_started = False


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stMetric"] {
        background: rgba(100, 150, 255, 0.08);
        border: 1px solid rgba(100, 150, 255, 0.18);
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
                rgba(100, 150, 255, 0.18),
                rgba(160, 100, 255, 0.10)
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

    .task-box {
        text-align: center;
        padding: 20px;
        border-radius: 18px;
        background: rgba(100, 150, 255, 0.06);
        margin-bottom: 15px;
    }

    .task-text {
        font-size: 1.5rem;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

records = data[
    "records"
]

today = date.today()

today_text = str(
    today
)

week_start = (
    today
    - timedelta(
        days=6
    )
)


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>⏱️ 5分だけやる！</h1>
        <p>
            やる気がなくても大丈夫。
            とりあえず5分だけ始めよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 集計
# =========================================================

today_records = [
    record
    for record in records
    if record.get(
        "date"
    ) == today_text
]


weekly_records = []

for record in records:
    try:
        record_date = (
            datetime.strptime(
                record.get(
                    "date",
                    "",
                ),
                "%Y-%m-%d",
            ).date()
        )

        if (
            week_start
            <= record_date
            <= today
        ):
            weekly_records.append(
                record
            )

    except ValueError:
        pass


today_minutes = sum(
    int(
        record.get(
            "minutes",
            0,
        )
    )
    for record
    in today_records
)


# =========================================================
# ダッシュボード
# =========================================================

columns = st.columns(
    4
)

columns[0].metric(
    "今日",
    f"{len(today_records)}回",
)

columns[1].metric(
    "今日の時間",
    f"{today_minutes}分",
)

columns[2].metric(
    "今週",
    f"{len(weekly_records)}回",
)

columns[3].metric(
    "累計",
    f"{len(records)}回",
)


# =========================================================
# タスク入力
# =========================================================

st.divider()

st.subheader(
    "🎯 5分だけ何をやる？"
)

if not st.session_state.timer_started:

    task_input = st.text_input(
        "やること",
        value=st.session_state.task,
        placeholder=(
            "例：NumPyの本を読む"
        ),
    )

    if st.button(
        "▶️ 5分スタート！",
        type="primary",
        use_container_width=True,
    ):
        if not task_input.strip():
            st.error(
                "やることを入力してください。"
            )

        else:
            st.session_state.task = (
                task_input.strip()
            )

            st.session_state.timer_started = (
                True
            )

            st.rerun()


# =========================================================
# タイマー
# =========================================================

else:

    st.markdown(
        f"""
        <div class="task-box">
            <div>
                今やること
            </div>

            <div class="task-text">
                {st.session_state.task}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    timer_html = """
    <div
        style="
            text-align:center;
            padding:25px;
            font-family:sans-serif;
        "
    >

        <div
            id="timer"
            style="
                font-size:64px;
                font-weight:700;
                margin-bottom:10px;
            "
        >
            05:00
        </div>

        <div
            id="message"
            style="
                font-size:18px;
                opacity:0.75;
            "
        >
            5分だけ集中しよう！
        </div>

    </div>

    <script>

    let seconds = 300;

    const timer =
        document.getElementById("timer");

    const message =
        document.getElementById("message");

    function updateTimer() {

        const minutes =
            Math.floor(seconds / 60);

        const remainingSeconds =
            seconds % 60;

        timer.innerText =
            String(minutes).padStart(2, "0")
            + ":"
            + String(remainingSeconds)
                .padStart(2, "0");

        if (seconds <= 60) {
            message.innerText =
                "🔥 あと少し！";
        }

        if (seconds <= 0) {

            timer.innerText =
                "00:00";

            message.innerText =
                "🎉 5分終了！";

            clearInterval(interval);

            try {
                const audio =
                    new Audio(
                        "data:audio/wav;base64,"
                        + "UklGRigAAABXQVZFZm10IBAAAAABAAEA"
                    );

                audio.play();

            } catch (error) {
                console.log(error);
            }

            return;
        }

        seconds--;

    }

    updateTimer();

    const interval =
        setInterval(
            updateTimer,
            1000
        );

    </script>
    """

    components.html(
        timer_html,
        height=180,
    )


    # =====================================================
    # 完了
    # =====================================================

    st.info(
        "タイマーが終わったら「できた！」を押そう。"
    )

    if st.button(
        "✅ できた！",
        type="primary",
        use_container_width=True,
    ):
        add_record(
            data,
            st.session_state.task,
        )

        st.session_state.timer_started = (
            False
        )

        st.session_state.task = ""

        st.success(
            "🎉 5分達成！"
        )

        st.balloons()

        st.rerun()


    # =====================================================
    # もう5分
    # =====================================================

    if st.button(
        "🔁 もう5分やる",
        use_container_width=True,
    ):
        add_record(
            data,
            st.session_state.task,
        )

        # timer_startedはTrueのまま
        # rerunするとタイマーが再び5:00から始まる

        st.rerun()


    # =====================================================
    # 中止
    # =====================================================

    with st.expander(
        "今日はやめる"
    ):
        if st.button(
            "⏹️ 中止する",
            use_container_width=True,
        ):
            st.session_state.timer_started = (
                False
            )

            st.session_state.task = ""

            st.rerun()


# =========================================================
# 今日の記録
# =========================================================

st.divider()

st.subheader(
    "✨ 今日やった5分"
)

if not today_records:

    st.info(
        "今日はまだ5分チャレンジを達成していません。"
    )

else:

    sorted_today = sorted(
        today_records,
        key=lambda record: (
            record.get(
                "completed_at",
                "",
            )
        ),
        reverse=True,
    )

    for record in sorted_today:

        record_id = record.get(
            "id",
            "",
        )

        with st.container(
            border=True,
        ):

            st.markdown(
                f"### ✅ "
                f"{record.get('task', '')}"
            )

            st.write(
                f"⏱️ "
                f"{record.get('minutes', 5)}分"
            )

            completed_at = record.get(
                "completed_at",
                "",
            )

            if completed_at:

                try:

                    completed_time = (
                        datetime.fromisoformat(
                            completed_at
                        )
                    )

                    st.caption(
                        "完了："
                        + completed_time.strftime(
                            "%H:%M"
                        )
                    )

                except ValueError:
                    pass

            with st.expander(
                "🗑️ 削除"
            ):

                if st.button(
                    "この記録を削除",
                    key=(
                        f"delete_"
                        f"{record_id}"
                    ),
                    use_container_width=True,
                ):

                    delete_record(
                        data,
                        record_id,
                    )

                    st.rerun()


# =========================================================
# 最近7日
# =========================================================

st.divider()

st.subheader(
    "📊 最近7日間"
)

daily_rows = []

for i in range(
    7
):

    target_date = (
        week_start
        + timedelta(
            days=i
        )
    )

    target_records = [
        record
        for record in records
        if record.get(
            "date"
        )
        == str(
            target_date
        )
    ]

    daily_rows.append(
        {
            "日付": (
                target_date.strftime(
                    "%m/%d"
                )
            ),
            "集中回数": len(
                target_records
            ),
        }
    )


daily_df = pd.DataFrame(
    daily_rows
).set_index(
    "日付"
)

st.bar_chart(
    daily_df
)


# =========================================================
# 履歴
# =========================================================

st.divider()

with st.expander(
    "📚 過去の5分を見る"
):

    if not records:

        st.info(
            "まだ履歴がありません。"
        )

    else:

        sorted_records = sorted(
            records,
            key=lambda record: (
                record.get(
                    "completed_at",
                    "",
                )
            ),
            reverse=True,
        )

        history_rows = []

        for record in sorted_records:

            history_rows.append(
                {
                    "日付": (
                        record.get(
                            "date",
                            "",
                        )
                    ),
                    "やったこと": (
                        record.get(
                            "task",
                            "",
                        )
                    ),
                    "時間": (
                        f"{record.get('minutes', 5)}分"
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
            f"focus_backup_"
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
    "やる気を待たない。まず5分だけ始めよう。⏱️"
)
