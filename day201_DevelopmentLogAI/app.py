import json
import os
import uuid
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="開発ログAI",
    page_icon="📝",
    layout="wide"
)


DATA_DIR = "data"
LOG_FILE = os.path.join(
    DATA_DIR,
    "development_logs.json"
)


# =====================================
# データ保存・読み込み
# =====================================

def save_logs(logs):
    """開発ログをJSONへ保存する"""
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            logs,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_logs():
    """開発ログをJSONから読み込む"""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(LOG_FILE):
        save_logs([])
        return []

    try:
        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    save_logs([])
    return []


def add_log(
    logs,
    log_date,
    project_name,
    development_minutes,
    completed_tasks,
    learning,
    next_tasks,
    mood,
    tags
):
    """新しい開発ログを追加する"""

    new_log = {
        "id": str(uuid.uuid4()),
        "date": str(log_date),
        "project_name": project_name,
        "development_minutes": development_minutes,
        "completed_tasks": completed_tasks,
        "learning": learning,
        "next_tasks": next_tasks,
        "mood": mood,
        "tags": tags,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    logs.append(new_log)
    save_logs(logs)


def delete_log(logs, log_id):
    """指定したログを削除する"""

    updated_logs = [
        log
        for log in logs
        if log.get("id") != log_id
    ]

    save_logs(updated_logs)


# =====================================
# 集計処理
# =====================================

def calculate_total_minutes(logs):
    """総開発時間を分単位で返す"""

    return sum(
        int(log.get(
            "development_minutes",
            0
        ))
        for log in logs
    )


def calculate_month_minutes(logs):
    """今月の開発時間を分単位で返す"""

    today = date.today()

    total = 0

    for log in logs:
        try:
            log_date = datetime.strptime(
                log.get("date", ""),
                "%Y-%m-%d"
            ).date()

            if (
                log_date.year == today.year
                and log_date.month == today.month
            ):
                total += int(
                    log.get(
                        "development_minutes",
                        0
                    )
                )

        except ValueError:
            continue

    return total


def calculate_streak(logs):
    """今日または昨日から続く連続記録日数"""

    recorded_dates = set()

    for log in logs:
        try:
            recorded_dates.add(
                datetime.strptime(
                    log.get("date", ""),
                    "%Y-%m-%d"
                ).date()
            )
        except ValueError:
            continue

    if not recorded_dates:
        return 0

    today = date.today()

    if today in recorded_dates:
        current_date = today

    elif today - timedelta(days=1) in recorded_dates:
        current_date = (
            today - timedelta(days=1)
        )

    else:
        return 0

    streak = 0

    while current_date in recorded_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def format_minutes(minutes):
    """分を○時間○分形式に変換する"""

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours == 0:
        return f"{remaining_minutes}分"

    if remaining_minutes == 0:
        return f"{hours}時間"

    return (
        f"{hours}時間"
        f"{remaining_minutes}分"
    )


# =====================================
# 振り返りコメント
# =====================================

def create_review_comment(
    project_name,
    development_minutes,
    completed_tasks,
    learning,
    next_tasks,
    mood
):
    """
    APIを使用しない簡易的な
    AI風振り返りコメント
    """

    comments = []

    if development_minutes >= 180:
        comments.append(
            "今日はかなり集中して"
            "開発に取り組めました。"
        )

    elif development_minutes >= 60:
        comments.append(
            "今日も着実に"
            "開発を進められました。"
        )

    elif development_minutes > 0:
        comments.append(
            "短い時間でも開発を続けたことが"
            "大きな積み重ねになります。"
        )

    else:
        comments.append(
            "今日は作業時間よりも、"
            "考えを整理できた一日ですね。"
        )

    if project_name:
        comments.append(
            f"「{project_name}」の記録が"
            "また一つ増えました。"
        )

    if completed_tasks:
        comments.append(
            "今日できたことを記録したことで、"
            "成果がはっきり見えるようになりました。"
        )

    if learning:
        comments.append(
            "今日の気づきは、"
            "次の開発にも活かせそうです。"
        )

    if next_tasks:
        comments.append(
            "明日やることも決まっているので、"
            "次回は迷わず始められます。"
        )

    mood_comments = {
        "😁 最高": (
            "良い勢いが出ています。"
            "この流れを大切にしましょう！"
        ),
        "😊 良い": (
            "前向きな気持ちで"
            "取り組めた一日でした。"
        ),
        "😐 普通": (
            "大きな波がなくても、"
            "続けることが力になります。"
        ),
        "😴 眠い": (
            "疲れている中でも記録できました。"
            "今日はしっかり休みましょう。"
        ),
        "😫 大変": (
            "大変な中でも前へ進んだことが"
            "何よりの成果です。"
        )
    }

    if mood in mood_comments:
        comments.append(
            mood_comments[mood]
        )

    return "\n\n".join(comments)


# =====================================
# データ読み込み
# =====================================

logs = load_logs()

logs = sorted(
    logs,
    key=lambda log: (
        log.get("date", ""),
        log.get("created_at", "")
    ),
    reverse=True
)


# =====================================
# タイトル
# =====================================

st.title("📝 開発ログAI")
st.caption(
    "毎日の開発を記録し、"
    "成長の積み重ねを見える化します。"
)


# =====================================
# 集計カード
# =====================================

total_minutes = calculate_total_minutes(
    logs
)

month_minutes = calculate_month_minutes(
    logs
)

streak = calculate_streak(logs)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📚 総ログ数",
        f"{len(logs)}件"
    )

with col2:
    st.metric(
        "⏱️ 総開発時間",
        format_minutes(total_minutes)
    )

with col3:
    st.metric(
        "📅 今月の開発時間",
        format_minutes(month_minutes)
    )

with col4:
    st.metric(
        "🔥 連続記録",
        f"{streak}日"
    )


st.divider()


# =====================================
# 開発ログ登録フォーム
# =====================================

st.header("✍️ 今日の開発を記録")

with st.form(
    "development_log_form",
    clear_on_submit=True
):
    form_col1, form_col2 = st.columns(2)

    with form_col1:
        log_date = st.date_input(
            "記録日",
            value=date.today()
        )

        project_name = st.text_input(
            "プロジェクト名",
            placeholder=(
                "例：LuNova Developer OS"
            )
        )

        hour = st.number_input(
            "開発時間",
            min_value=0,
            max_value=24,
            value=1,
            step=1
        )

        minute = st.selectbox(
            "追加の分数",
            [
                0,
                10,
                15,
                20,
                30,
                45
            ]
        )

        mood = st.selectbox(
            "今日の気分",
            [
                "😁 最高",
                "😊 良い",
                "😐 普通",
                "😴 眠い",
                "😫 大変"
            ],
            index=1
        )

    with form_col2:
        completed_tasks = st.text_area(
            "今日やったこと",
            placeholder=(
                "・ホーム画面を作成\n"
                "・JSON保存機能を追加\n"
                "・バグを修正"
            ),
            height=120
        )

        learning = st.text_area(
            "今日の気づき・学び",
            placeholder=(
                "JSONを使うと"
                "データ管理がしやすかった。"
            ),
            height=100
        )

        next_tasks = st.text_area(
            "明日やること",
            placeholder=(
                "・グラフ機能を追加\n"
                "・GitHubを更新"
            ),
            height=100
        )

        tags_text = st.text_input(
            "タグ",
            placeholder=(
                "Luna, Streamlit, AI"
            )
        )

    submitted = st.form_submit_button(
        "💾 開発ログを保存",
        use_container_width=True
    )

    if submitted:
        cleaned_project_name = (
            project_name.strip()
        )

        development_minutes = (
            int(hour) * 60
            + int(minute)
        )

        tags = [
            tag.strip()
            for tag in tags_text.split(",")
            if tag.strip()
        ]

        if not cleaned_project_name:
            st.error(
                "プロジェクト名を"
                "入力してください。"
            )

        elif not completed_tasks.strip():
            st.error(
                "今日やったことを"
                "入力してください。"
            )

        else:
            add_log(
                logs=logs,
                log_date=log_date,
                project_name=cleaned_project_name,
                development_minutes=(
                    development_minutes
                ),
                completed_tasks=(
                    completed_tasks.strip()
                ),
                learning=learning.strip(),
                next_tasks=next_tasks.strip(),
                mood=mood,
                tags=tags
            )

            review_comment = (
                create_review_comment(
                    project_name=(
                        cleaned_project_name
                    ),
                    development_minutes=(
                        development_minutes
                    ),
                    completed_tasks=(
                        completed_tasks.strip()
                    ),
                    learning=learning.strip(),
                    next_tasks=(
                        next_tasks.strip()
                    ),
                    mood=mood
                )
            )

            st.session_state[
                "latest_review"
            ] = review_comment

            st.success(
                "開発ログを保存しました！"
            )

            st.rerun()


# =====================================
# 最新の振り返り
# =====================================

if "latest_review" in st.session_state:
    st.subheader("🤖 今日の振り返り")

    st.info(
        st.session_state[
            "latest_review"
        ]
    )

    if st.button(
        "振り返りを閉じる"
    ):
        del st.session_state[
            "latest_review"
        ]
        st.rerun()


st.divider()


# =====================================
# 開発時間グラフ
# =====================================

st.header("📊 開発時間の推移")

if logs:
    graph_data = []

    for log in logs:
        graph_data.append(
            {
                "日付": log.get("date", ""),
                "開発時間": round(
                    int(
                        log.get(
                            "development_minutes",
                            0
                        )
                    ) / 60,
                    2
                )
            }
        )

    dataframe = pd.DataFrame(
        graph_data
    )

    dataframe["日付"] = pd.to_datetime(
        dataframe["日付"],
        errors="coerce"
    )

    dataframe = (
        dataframe
        .dropna(
            subset=["日付"]
        )
        .groupby(
            "日付",
            as_index=False
        )["開発時間"]
        .sum()
        .sort_values("日付")
    )

    st.line_chart(
        dataframe,
        x="日付",
        y="開発時間",
        use_container_width=True
    )

else:
    st.info(
        "ログを登録すると、"
        "開発時間のグラフが表示されます。"
    )


st.divider()


# =====================================
# 過去ログ一覧
# =====================================

st.header("📚 開発ログ一覧")

if not logs:
    st.info(
        "まだ開発ログがありません。"
        "今日の記録を残してみよう！"
    )

else:
    filter_col1, filter_col2 = (
        st.columns(2)
    )

    with filter_col1:
        search_word = st.text_input(
            "🔍 キーワード検索",
            placeholder=(
                "プロジェクト名・内容・タグ"
            )
        )

    with filter_col2:
        project_names = sorted(
            {
                log.get(
                    "project_name",
                    ""
                )
                for log in logs
                if log.get(
                    "project_name"
                )
            }
        )

        project_filter = st.selectbox(
            "プロジェクトで絞り込み",
            ["すべて"] + project_names
        )

    filtered_logs = logs

    if search_word:
        keyword = search_word.lower()

        filtered_logs = [
            log
            for log in filtered_logs
            if keyword in log.get(
                "project_name",
                ""
            ).lower()
            or keyword in log.get(
                "completed_tasks",
                ""
            ).lower()
            or keyword in log.get(
                "learning",
                ""
            ).lower()
            or keyword in " ".join(
                log.get(
                    "tags",
                    []
                )
            ).lower()
        ]

    if project_filter != "すべて":
        filtered_logs = [
            log
            for log in filtered_logs
            if log.get(
                "project_name"
            ) == project_filter
        ]

    st.write(
        f"表示件数："
        f"**{len(filtered_logs)}件**"
    )

    if not filtered_logs:
        st.warning(
            "条件に一致する"
            "開発ログがありません。"
        )

    for log in filtered_logs:
        log_id = log.get("id", "")
        log_date = log.get(
            "date",
            "日付不明"
        )
        project_name = log.get(
            "project_name",
            "名称未設定"
        )
        mood = log.get(
            "mood",
            "😐 普通"
        )

        with st.container(
            border=True
        ):
            title_col, time_col = (
                st.columns([3, 1])
            )

            with title_col:
                st.subheader(
                    f"{mood} {project_name}"
                )

                st.caption(
                    f"📅 {log_date}"
                )

            with time_col:
                development_minutes = int(
                    log.get(
                        "development_minutes",
                        0
                    )
                )

                st.metric(
                    "開発時間",
                    format_minutes(
                        development_minutes
                    )
                )

            st.markdown(
                "#### ✅ 今日やったこと"
            )

            st.write(
                log.get(
                    "completed_tasks",
                    ""
                )
            )

            learning = log.get(
                "learning",
                ""
            )

            if learning:
                st.markdown(
                    "#### 💡 気づき・学び"
                )
                st.write(learning)

            next_tasks = log.get(
                "next_tasks",
                ""
            )

            if next_tasks:
                st.markdown(
                    "#### 🚀 次にやること"
                )
                st.write(next_tasks)

            tags = log.get(
                "tags",
                []
            )

            if tags:
                tag_text = " ".join(
                    f"`#{tag}`"
                    for tag in tags
                )

                st.markdown(tag_text)

            with st.expander(
                "🤖 この日の振り返り"
            ):
                st.write(
                    create_review_comment(
                        project_name=(
                            project_name
                        ),
                        development_minutes=(
                            development_minutes
                        ),
                        completed_tasks=(
                            log.get(
                                "completed_tasks",
                                ""
                            )
                        ),
                        learning=learning,
                        next_tasks=next_tasks,
                        mood=mood
                    )
                )

            with st.expander(
                "🗑️ このログを削除"
            ):
                st.warning(
                    "削除したログは"
                    "元に戻せません。"
                )

                confirm_delete = (
                    st.checkbox(
                        "削除を確認しました",
                        key=(
                            f"confirm_"
                            f"{log_id}"
                        )
                    )
                )

                if st.button(
                    "ログを削除",
                    key=f"delete_{log_id}",
                    disabled=(
                        not confirm_delete
                    ),
                    use_container_width=True
                ):
                    delete_log(
                        logs,
                        log_id
                    )

                    st.success(
                        "ログを削除しました。"
                    )

                    st.rerun()


st.divider()

st.success(
    "今日の一歩が、"
    "LuNovaの未来を作っています。🌙"
)
