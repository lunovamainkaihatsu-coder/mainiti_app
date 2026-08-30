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
    page_title="今どれくらい？",
    page_icon="📈",
    layout="centered",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"

DATA_FILE = os.path.join(
    DATA_DIR,
    "progress_data.json",
)

CATEGORIES = [
    "勉強",
    "仕事",
    "制作",
    "イラスト",
    "アプリ開発",
    "読書",
    "片付け",
    "運動",
    "趣味",
    "その他",
]

CATEGORY_ICONS = {
    "勉強": "📚",
    "仕事": "💼",
    "制作": "🛠️",
    "イラスト": "🎨",
    "アプリ開発": "💻",
    "読書": "📖",
    "片付け": "🧹",
    "運動": "🏃",
    "趣味": "🎮",
    "その他": "✨",
}


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
        "projects": []
    }


# =========================================================
# 保存
# =========================================================

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


# =========================================================
# 読み込み
# =========================================================

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
            "projects",
            [],
        )

        for project in data[
            "projects"
        ]:
            project.setdefault(
                "id",
                create_id(),
            )

            project.setdefault(
                "title",
                "",
            )

            project.setdefault(
                "category",
                "その他",
            )

            project.setdefault(
                "progress",
                0,
            )

            project.setdefault(
                "memo",
                "",
            )

            project.setdefault(
                "created_at",
                now_text(),
            )

            project.setdefault(
                "updated_at",
                "",
            )

            project.setdefault(
                "history",
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
# プロジェクト取得
# =========================================================

def get_project(
    data,
    project_id,
):
    for project in data[
        "projects"
    ]:
        if project.get(
            "id"
        ) == project_id:
            return project

    return None


# =========================================================
# 新規作成
# =========================================================

def add_project(
    data,
    title,
    category,
    progress,
    memo,
):
    timestamp = now_text()

    project = {
        "id": create_id(),
        "title": title,
        "category": category,
        "progress": progress,
        "memo": memo,
        "created_at": timestamp,
        "updated_at": timestamp,
        "history": [
            {
                "date": str(
                    date.today()
                ),
                "progress": progress,
                "memo": memo,
                "created_at": timestamp,
            }
        ],
    }

    data[
        "projects"
    ].append(
        project
    )

    save_data(data)


# =========================================================
# 進捗更新
# =========================================================

def update_progress(
    data,
    project_id,
    new_progress,
    memo,
):
    project = get_project(
        data,
        project_id,
    )

    if not project:
        return

    timestamp = now_text()

    project[
        "progress"
    ] = new_progress

    project[
        "memo"
    ] = memo

    project[
        "updated_at"
    ] = timestamp

    project[
        "history"
    ].append(
        {
            "date": str(
                date.today()
            ),
            "progress": new_progress,
            "memo": memo,
            "created_at": timestamp,
        }
    )

    save_data(data)


# =========================================================
# 基本情報編集
# =========================================================

def edit_project(
    data,
    project_id,
    title,
    category,
):
    project = get_project(
        data,
        project_id,
    )

    if not project:
        return

    project[
        "title"
    ] = title

    project[
        "category"
    ] = category

    project[
        "updated_at"
    ] = now_text()

    save_data(data)


# =========================================================
# 削除
# =========================================================

def delete_project(
    data,
    project_id,
):
    data[
        "projects"
    ] = [
        project
        for project in data[
            "projects"
        ]
        if project.get(
            "id"
        ) != project_id
    ]

    save_data(data)


# =========================================================
# 前回進捗
# =========================================================

def get_previous_progress(
    project,
):
    history = project.get(
        "history",
        [],
    )

    if len(history) < 2:
        return None

    return history[
        -2
    ].get(
        "progress",
        0,
    )


# =========================================================
# 日時表示
# =========================================================

def format_datetime(
    value,
):
    if not value:
        return ""

    try:
        target = datetime.fromisoformat(
            value
        )

        return target.strftime(
            "%Y/%m/%d %H:%M"
        )

    except ValueError:
        return value


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
        background: rgba(100, 150, 255, 0.07);
        border: 1px solid rgba(100, 150, 255, 0.15);
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
                rgba(90, 150, 255, 0.18),
                rgba(170, 100, 255, 0.12)
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

    .progress-card {
        padding: 20px;
        border-radius: 18px;
        border: 1px solid rgba(150, 150, 150, 0.15);
        margin-bottom: 12px;
    }

    .progress-title {
        font-size: 1.3rem;
        font-weight: 700;
    }

    .progress-number {
        font-size: 2.2rem;
        font-weight: 800;
    }

    .complete-box {
        padding: 20px;
        text-align: center;
        border-radius: 18px;
        background: rgba(255, 190, 50, 0.10);
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ読み込み
# =========================================================

data = load_data()

projects = data[
    "projects"
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>📈 今どれくらい？</h1>

        <p>
            完璧じゃなくていい。
            今どこまで進んだかだけ記録しよう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

active_projects = [
    project
    for project in projects
    if project.get(
        "progress",
        0,
    ) < 100
]

completed_projects = [
    project
    for project in projects
    if project.get(
        "progress",
        0,
    ) >= 100
]


if projects:
    average_progress = sum(
        project.get(
            "progress",
            0,
        )
        for project in projects
    ) / len(projects)

else:
    average_progress = 0


current_month = date.today().strftime(
    "%Y-%m"
)

monthly_updates = 0

for project in projects:
    for history in project.get(
        "history",
        [],
    ):
        if history.get(
            "date",
            "",
        ).startswith(
            current_month
        ):
            monthly_updates += 1


columns = st.columns(
    4
)

columns[0].metric(
    "進行中",
    f"{len(active_projects)}個",
)

columns[1].metric(
    "達成",
    f"{len(completed_projects)}個",
)

columns[2].metric(
    "平均進捗",
    f"{average_progress:.0f}%",
)

columns[3].metric(
    "今月の更新",
    f"{monthly_updates}回",
)


# =========================================================
# 新規プロジェクト
# =========================================================

st.divider()

st.subheader(
    "➕ 新しい進捗を追加"
)

with st.form(
    "new_project_form",
    clear_on_submit=True,
):
    title = st.text_input(
        "何の進捗？",
        placeholder=(
            "例：イラスト練習"
        ),
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    progress = st.slider(
        "現在どれくらい？",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        format="%d%%",
    )

    memo = st.text_input(
        "ひとこと",
        placeholder=(
            "例：今日は手の練習まで進んだ"
        ),
    )

    submitted = (
        st.form_submit_button(
            "📈 登録する",
            use_container_width=True,
        )
    )

    if submitted:
        if not title.strip():
            st.error(
                "タイトルを入力してください。"
            )

        else:
            add_project(
                data,
                title.strip(),
                category,
                progress,
                memo.strip(),
            )

            st.success(
                "進捗を登録しました！"
            )

            st.rerun()


# =========================================================
# 進行中
# =========================================================

st.divider()

st.subheader(
    "🚀 進行中"
)

if not active_projects:
    st.info(
        "現在進行中のものはありません。"
    )

else:
    active_projects = sorted(
        active_projects,
        key=lambda project: (
            project.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    )

    for project in active_projects:
        project_id = project[
            "id"
        ]

        progress_value = int(
            project.get(
                "progress",
                0,
            )
        )

        category_name = project.get(
            "category",
            "その他",
        )

        icon = CATEGORY_ICONS.get(
            category_name,
            "✨",
        )

        previous_progress = (
            get_previous_progress(
                project
            )
        )

        # -------------------------------------------------
        # カード
        # -------------------------------------------------

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### {icon} "
                f"{project.get('title', '')}"
            )

            col1, col2 = st.columns(
                [3, 1]
            )

            with col1:
                st.progress(
                    progress_value
                )

            with col2:
                st.markdown(
                    f"## {progress_value}%"
                )

            # ---------------------------------------------
            # 差分
            # ---------------------------------------------

            if previous_progress is not None:
                difference = (
                    progress_value
                    - previous_progress
                )

                if difference > 0:
                    st.success(
                        f"前回 {previous_progress}% → "
                        f"今回 {progress_value}% "
                        f"（+{difference}%）"
                    )

                elif difference < 0:
                    st.warning(
                        f"前回 {previous_progress}% → "
                        f"今回 {progress_value}% "
                        f"（{difference}%）"
                    )

                else:
                    st.caption(
                        f"前回から変化なし："
                        f"{progress_value}%"
                    )

            if project.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{project.get('memo', '')}"
                )

            st.caption(
                f"{category_name} ／ "
                f"最終更新："
                f"{format_datetime(project.get('updated_at', ''))}"
            )

            # ---------------------------------------------
            # 更新
            # ---------------------------------------------

            with st.expander(
                "📈 進捗を更新"
            ):
                new_progress = st.slider(
                    "現在の進捗",
                    min_value=0,
                    max_value=100,
                    value=progress_value,
                    step=1,
                    format="%d%%",
                    key=(
                        f"progress_"
                        f"{project_id}"
                    ),
                )

                new_memo = st.text_input(
                    "今回のひとこと",
                    placeholder=(
                        "例：今日はここまで進んだ！"
                    ),
                    key=(
                        f"memo_"
                        f"{project_id}"
                    ),
                )

                if st.button(
                    "更新する",
                    key=(
                        f"update_"
                        f"{project_id}"
                    ),
                    use_container_width=True,
                ):
                    update_progress(
                        data,
                        project_id,
                        new_progress,
                        new_memo.strip(),
                    )

                    st.rerun()

            # ---------------------------------------------
            # 履歴
            # ---------------------------------------------

            with st.expander(
                "📚 進捗履歴"
            ):
                history = project.get(
                    "history",
                    [],
                )

                if not history:
                    st.info(
                        "履歴はありません。"
                    )

                else:
                    history_rows = []

                    for item in reversed(
                        history
                    ):
                        history_rows.append(
                            {
                                "日時": (
                                    format_datetime(
                                        item.get(
                                            "created_at",
                                            "",
                                        )
                                    )
                                ),
                                "進捗": (
                                    f"{item.get('progress', 0)}%"
                                ),
                                "メモ": (
                                    item.get(
                                        "memo",
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

            # ---------------------------------------------
            # 編集
            # ---------------------------------------------

            with st.expander(
                "✏️ 基本情報を編集"
            ):
                edit_title = st.text_input(
                    "タイトル",
                    value=project.get(
                        "title",
                        "",
                    ),
                    key=(
                        f"title_"
                        f"{project_id}"
                    ),
                )

                current_category = (
                    project.get(
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
                            f"category_"
                            f"{project_id}"
                        ),
                    )
                )

                if st.button(
                    "変更を保存",
                    key=(
                        f"edit_"
                        f"{project_id}"
                    ),
                    use_container_width=True,
                ):
                    if not edit_title.strip():
                        st.error(
                            "タイトルを入力してください。"
                        )

                    else:
                        edit_project(
                            data,
                            project_id,
                            edit_title.strip(),
                            edit_category,
                        )

                        st.rerun()

            # ---------------------------------------------
            # 削除
            # ---------------------------------------------

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この進捗を削除",
                    key=(
                        f"delete_"
                        f"{project_id}"
                    ),
                    use_container_width=True,
                ):
                    delete_project(
                        data,
                        project_id,
                    )

                    st.rerun()


# =========================================================
# 100%達成
# =========================================================

st.divider()

st.subheader(
    "🏆 100%達成"
)

if not completed_projects:
    st.caption(
        "100%まで到達したものがここに並びます。"
    )

else:
    completed_projects = sorted(
        completed_projects,
        key=lambda project: (
            project.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    )

    for project in completed_projects:
        project_id = project[
            "id"
        ]

        category_name = project.get(
            "category",
            "その他",
        )

        icon = CATEGORY_ICONS.get(
            category_name,
            "✨",
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"## 🎉 {icon} "
                f"{project.get('title', '')}"
            )

            st.progress(
                100
            )

            st.success(
                "🎊 100%！目標達成！"
            )

            if project.get(
                "memo",
                "",
            ):
                st.write(
                    f"💬 "
                    f"{project.get('memo', '')}"
                )

            st.caption(
                f"{category_name} ／ "
                f"{format_datetime(project.get('updated_at', ''))}"
            )

            # ---------------------------------------------
            # 履歴
            # ---------------------------------------------

            with st.expander(
                "📚 達成までの履歴"
            ):
                history_rows = []

                for item in reversed(
                    project.get(
                        "history",
                        [],
                    )
                ):
                    history_rows.append(
                        {
                            "日時": (
                                format_datetime(
                                    item.get(
                                        "created_at",
                                        "",
                                    )
                                )
                            ),
                            "進捗": (
                                f"{item.get('progress', 0)}%"
                            ),
                            "メモ": (
                                item.get(
                                    "memo",
                                    "",
                                )
                            ),
                        }
                    )

                if history_rows:
                    history_df = pd.DataFrame(
                        history_rows
                    )

                    st.dataframe(
                        history_df,
                        use_container_width=True,
                        hide_index=True,
                    )

            # ---------------------------------------------
            # 再開
            # ---------------------------------------------

            with st.expander(
                "🔄 進捗を変更"
            ):
                reopened_progress = st.slider(
                    "進捗",
                    min_value=0,
                    max_value=100,
                    value=100,
                    step=1,
                    format="%d%%",
                    key=(
                        f"reopen_progress_"
                        f"{project_id}"
                    ),
                )

                reopened_memo = st.text_input(
                    "ひとこと",
                    key=(
                        f"reopen_memo_"
                        f"{project_id}"
                    ),
                )

                if st.button(
                    "進捗を更新",
                    key=(
                        f"reopen_"
                        f"{project_id}"
                    ),
                    use_container_width=True,
                ):
                    update_progress(
                        data,
                        project_id,
                        reopened_progress,
                        reopened_memo.strip(),
                    )

                    st.rerun()

            # ---------------------------------------------
            # 削除
            # ---------------------------------------------

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "この記録を削除",
                    key=(
                        f"complete_delete_"
                        f"{project_id}"
                    ),
                    use_container_width=True,
                ):
                    delete_project(
                        data,
                        project_id,
                    )

                    st.rerun()


# =========================================================
# 全体一覧
# =========================================================

st.divider()

st.subheader(
    "📊 全体の進み具合"
)

if not projects:
    st.info(
        "進捗を登録するとここに一覧が表示されます。"
    )

else:
    overview_rows = []

    for project in sorted(
        projects,
        key=lambda item: (
            item.get(
                "progress",
                0,
            )
        ),
        reverse=True,
    ):
        overview_rows.append(
            {
                "カテゴリー": (
                    project.get(
                        "category",
                        "",
                    )
                ),
                "タイトル": (
                    project.get(
                        "title",
                        "",
                    )
                ),
                "進捗": (
                    project.get(
                        "progress",
                        0,
                    )
                ),
            }
        )

    overview_df = pd.DataFrame(
        overview_rows
    )

    chart_df = (
        overview_df[
            [
                "タイトル",
                "進捗",
            ]
        ]
        .set_index(
            "タイトル"
        )
    )

    st.bar_chart(
        chart_df
    )

    display_df = (
        overview_df.copy()
    )

    display_df[
        "進捗"
    ] = display_df[
        "進捗"
    ].astype(
        str
    ) + "%"

    st.dataframe(
        display_df,
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
            f"progress_backup_"
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
    "1%でも進めば、昨日より前にいる。📈"
)
