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
    page_title="今どこまでやった？",
    page_icon="🔖",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(
    DATA_DIR,
    "projects.json",
)

CATEGORIES = [
    "🤖 AI・プログラミング",
    "📱 アプリ開発",
    "🎨 イラスト",
    "📚 勉強",
    "💼 仕事",
    "✍️ ブログ・文章",
    "🏠 生活",
    "🔥 挑戦",
    "✨ その他",
]

STATUSES = [
    "▶️ 作業中",
    "⏸️ 一時停止",
    "✅ 完了",
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
        "projects": []
    }


# =========================================================
# 保存・読み込み
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

        for project in data["projects"]:
            project.setdefault(
                "id",
                create_id(),
            )

            project.setdefault(
                "name",
                "",
            )

            project.setdefault(
                "category",
                "✨ その他",
            )

            project.setdefault(
                "last_done",
                "",
            )

            project.setdefault(
                "next_action",
                "",
            )

            project.setdefault(
                "resume_memo",
                "",
            )

            project.setdefault(
                "progress",
                0,
            )

            project.setdefault(
                "status",
                "▶️ 作業中",
            )

            project.setdefault(
                "favorite",
                False,
            )

            project.setdefault(
                "created_at",
                now_text(),
            )

            project.setdefault(
                "updated_at",
                now_text(),
            )

            project.setdefault(
                "completed_at",
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
# 日時関数
# =========================================================

def parse_datetime(
    text,
):
    try:
        return datetime.fromisoformat(
            text
        )

    except (
        ValueError,
        TypeError,
    ):
        return datetime.now()


def format_datetime(
    text,
):
    try:
        target = datetime.fromisoformat(
            text
        )

        return target.strftime(
            "%Y/%m/%d %H:%M"
        )

    except (
        ValueError,
        TypeError,
    ):
        return "不明"


def days_since_update(
    project,
):
    updated = parse_datetime(
        project.get(
            "updated_at",
            "",
        )
    )

    return (
        date.today()
        - updated.date()
    ).days


def update_status_text(
    project,
):
    days = days_since_update(
        project
    )

    if days <= 0:
        return "🟢 今日更新"

    if days == 1:
        return "🟢 昨日更新"

    if days <= 3:
        return f"🟡 {days}日前"

    if days <= 7:
        return f"🟠 {days}日前"

    if days < 30:
        return f"🔴 {days}日前"

    return f"🚨 {days}日以上触っていない"


# =========================================================
# データ取得
# =========================================================

def get_project_by_id(
    data,
    project_id,
):
    return next(
        (
            project
            for project in data[
                "projects"
            ]
            if project.get(
                "id"
            )
            == project_id
        ),
        None,
    )


# =========================================================
# CRUD
# =========================================================

def add_project(
    data,
    name,
    category,
    last_done,
    next_action,
    resume_memo,
    progress,
    favorite,
):
    data[
        "projects"
    ].append(
        {
            "id": create_id(),
            "name": name,
            "category": category,
            "last_done": last_done,
            "next_action": next_action,
            "resume_memo": resume_memo,
            "progress": int(
                progress
            ),
            "status": "▶️ 作業中",
            "favorite": favorite,
            "created_at": now_text(),
            "updated_at": now_text(),
            "completed_at": "",
            "history": [],
        }
    )

    save_data(data)


def save_history_snapshot(
    project,
):
    history = project.setdefault(
        "history",
        [],
    )

    history.append(
        {
            "id": create_id(),
            "saved_at": now_text(),
            "last_done": project.get(
                "last_done",
                "",
            ),
            "next_action": project.get(
                "next_action",
                "",
            ),
            "resume_memo": project.get(
                "resume_memo",
                "",
            ),
            "progress": project.get(
                "progress",
                0,
            ),
            "status": project.get(
                "status",
                "▶️ 作業中",
            ),
        }
    )


def update_project(
    data,
    project_id,
    name,
    category,
    last_done,
    next_action,
    resume_memo,
    progress,
    status,
    favorite,
):
    project = get_project_by_id(
        data,
        project_id,
    )

    if not project:
        return

    # 更新前の状態を履歴へ保存
    save_history_snapshot(
        project
    )

    old_status = project.get(
        "status",
        "▶️ 作業中",
    )

    project[
        "name"
    ] = name

    project[
        "category"
    ] = category

    project[
        "last_done"
    ] = last_done

    project[
        "next_action"
    ] = next_action

    project[
        "resume_memo"
    ] = resume_memo

    project[
        "progress"
    ] = int(
        progress
    )

    project[
        "status"
    ] = status

    project[
        "favorite"
    ] = favorite

    project[
        "updated_at"
    ] = now_text()

    if (
        status == "✅ 完了"
        and old_status != "✅ 完了"
    ):
        project[
            "completed_at"
        ] = now_text()

        project[
            "progress"
        ] = 100

    elif status != "✅ 完了":
        project[
            "completed_at"
        ] = ""

    save_data(data)


def toggle_favorite(
    data,
    project_id,
):
    project = get_project_by_id(
        data,
        project_id,
    )

    if not project:
        return

    project[
        "favorite"
    ] = not project.get(
        "favorite",
        False,
    )

    save_data(data)


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
        )
        != project_id
    ]

    save_data(data)


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
        background: rgba(100, 130, 255, 0.07);
        border: 1px solid rgba(100, 130, 255, 0.15);
        border-radius: 16px;
        padding: 15px;
    }

    .hero {
        padding: 28px;
        border-radius: 24px;
        margin-bottom: 22px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 130, 255, 0.18),
                rgba(120, 220, 190, 0.10)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 8px;
        margin-bottom: 0;
        opacity: 0.78;
    }

    .project-title {
        font-size: 1.35rem;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .resume-box {
        padding: 28px;
        border-radius: 22px;
        margin-top: 10px;
        margin-bottom: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(100, 130, 255, 0.12),
                rgba(120, 220, 190, 0.07)
            );
    }

    .resume-name {
        font-size: 1.55rem;
        font-weight: 900;
        margin-bottom: 16px;
    }

    .resume-label {
        font-size: 0.85rem;
        opacity: 0.65;
        font-weight: 700;
        margin-top: 12px;
    }

    .resume-text {
        font-size: 1.1rem;
        font-weight: 650;
        margin-top: 4px;
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

active_projects = [
    project
    for project in projects
    if project.get(
        "status"
    )
    != "✅ 完了"
]

completed_projects = [
    project
    for project in projects
    if project.get(
        "status"
    )
    == "✅ 完了"
]

today_updated = [
    project
    for project in projects
    if parse_datetime(
        project.get(
            "updated_at",
            "",
        )
    ).date()
    == date.today()
]

stale_projects = [
    project
    for project in active_projects
    if days_since_update(
        project
    ) >= 7
]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>🔖 今どこまでやった？</h1>

        <p>
            作業の続きを未来の自分へ。
            次に開いた瞬間、すぐ続きから始めよう。
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

col1.metric(
    "▶️ 作業中",
    f"{len(active_projects)}件",
)

col2.metric(
    "🟢 今日更新",
    f"{len(today_updated)}件",
)

col3.metric(
    "🚨 7日以上",
    f"{len(stale_projects)}件",
)

col4.metric(
    "✅ 完了",
    f"{len(completed_projects)}件",
)


# =========================================================
# 再開中プロジェクト
# =========================================================

resume_id = st.session_state.get(
    "resume_project_id"
)

if resume_id:
    resume_project = get_project_by_id(
        data,
        resume_id,
    )

    if (
        resume_project
        and resume_project.get(
            "status"
        )
        != "✅ 完了"
    ):
        st.divider()

        st.subheader(
            "🚀 今これを再開"
        )

        st.markdown(
            f"""
            <div class="resume-box">

                <div class="resume-name">
                    {resume_project.get('name', '')}
                </div>

                <div class="resume-label">
                    次にやること
                </div>

                <div class="resume-text">
                    {resume_project.get('next_action', '') or '未登録'}
                </div>

                <div class="resume-label">
                    再開地点・メモ
                </div>

                <div class="resume-text">
                    {resume_project.get('resume_memo', '') or '未登録'}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(
            int(
                resume_project.get(
                    "progress",
                    0,
                )
            ) / 100
        )

        st.caption(
            f"現在の進捗："
            f"{resume_project.get('progress', 0)}%"
        )

        if st.button(
            "✖ 再開表示を閉じる",
            use_container_width=True,
        ):
            st.session_state.pop(
                "resume_project_id",
                None,
            )

            st.rerun()


# =========================================================
# 新規プロジェクト
# =========================================================

st.divider()

st.subheader(
    "➕ 続きを残す"
)

with st.form(
    "add_project_form"
):
    name = st.text_input(
        "プロジェクト・作業名",
        placeholder=(
            "例：AI Router"
        ),
    )

    category = st.selectbox(
        "カテゴリー",
        CATEGORIES,
    )

    last_done = st.text_area(
        "✅ 最後にやったこと",
        placeholder=(
            "例：検索結果カードの"
            "レイアウト調整まで完了"
        ),
        height=90,
    )

    next_action = st.text_area(
        "➡️ 次にやること",
        placeholder=(
            "例：画像表示部分を追加する"
        ),
        height=90,
    )

    resume_memo = st.text_input(
        "📍 再開地点・メモ",
        placeholder=(
            "例：app/page.tsx の下あたり"
        ),
    )

    progress = st.slider(
        "進捗率",
        min_value=0,
        max_value=100,
        value=10,
        step=5,
    )

    favorite = st.checkbox(
        "⭐ お気に入りにする"
    )

    submitted = st.form_submit_button(
        "🔖 続きを保存",
        use_container_width=True,
    )

    if submitted:
        if not name.strip():
            st.error(
                "プロジェクト名を入力してください。"
            )

        elif not next_action.strip():
            st.error(
                "「次にやること」を入力してください。"
            )

        else:
            add_project(
                data,
                name.strip(),
                category,
                last_done.strip(),
                next_action.strip(),
                resume_memo.strip(),
                progress,
                favorite,
            )

            st.rerun()


# =========================================================
# 作業中一覧
# =========================================================

st.divider()

st.subheader(
    "🗂️ 作業中のプロジェクト"
)

filter_col1, filter_col2 = st.columns(
    2
)

with filter_col1:
    category_filter = st.selectbox(
        "カテゴリー",
        [
            "すべて",
            *CATEGORIES,
        ],
        key="category_filter",
    )

with filter_col2:
    sort_mode = st.selectbox(
        "並び順",
        [
            "最近更新した順",
            "しばらく触っていない順",
            "進捗が高い順",
            "進捗が低い順",
        ],
    )


filtered_projects = (
    active_projects.copy()
)

if category_filter != "すべて":
    filtered_projects = [
        project
        for project in filtered_projects
        if project.get(
            "category"
        )
        == category_filter
    ]

if sort_mode == "最近更新した順":
    filtered_projects = sorted(
        filtered_projects,
        key=lambda project: parse_datetime(
            project.get(
                "updated_at",
                "",
            )
        ),
        reverse=True,
    )

elif sort_mode == "しばらく触っていない順":
    filtered_projects = sorted(
        filtered_projects,
        key=lambda project: days_since_update(
            project
        ),
        reverse=True,
    )

elif sort_mode == "進捗が高い順":
    filtered_projects = sorted(
        filtered_projects,
        key=lambda project: int(
            project.get(
                "progress",
                0,
            )
        ),
        reverse=True,
    )

else:
    filtered_projects = sorted(
        filtered_projects,
        key=lambda project: int(
            project.get(
                "progress",
                0,
            )
        ),
    )


if not filtered_projects:
    st.info(
        "作業中のプロジェクトはありません。"
    )

else:
    for project in filtered_projects:
        project_id = project.get(
            "id",
            "",
        )

        favorite_mark = (
            "⭐ "
            if project.get(
                "favorite",
                False,
            )
            else ""
        )

        with st.container(
            border=True,
        ):
            st.markdown(
                f"### {favorite_mark}"
                f"{project.get('name', '')}"
            )

            st.caption(
                f"{project.get('category', '')}"
                f" ｜ "
                f"{project.get('status', '')}"
                f" ｜ "
                f"{update_status_text(project)}"
            )

            st.progress(
                int(
                    project.get(
                        "progress",
                        0,
                    )
                ) / 100
            )

            st.caption(
                f"進捗 "
                f"{project.get('progress', 0)}%"
            )

            st.markdown(
                "**✅ 最後にやったこと**"
            )

            st.write(
                project.get(
                    "last_done",
                    "",
                )
                or "まだ記録なし"
            )

            st.markdown(
                "**➡️ 次にやること**"
            )

            st.write(
                project.get(
                    "next_action",
                    "",
                )
                or "まだ記録なし"
            )

            if project.get(
                "resume_memo",
                "",
            ):
                st.markdown(
                    "**📍 再開地点**"
                )

                st.write(
                    project.get(
                        "resume_memo",
                        "",
                    )
                )

            st.caption(
                "最終更新："
                + format_datetime(
                    project.get(
                        "updated_at",
                        "",
                    )
                )
            )

            col1, col2 = st.columns(
                2
            )

            with col1:
                if st.button(
                    "▶ 今これを再開",
                    key=(
                        "resume_"
                        + project_id
                    ),
                    use_container_width=True,
                ):
                    st.session_state[
                        "resume_project_id"
                    ] = project_id

                    st.rerun()

            with col2:
                favorite_text = (
                    "⭐ お気に入り解除"
                    if project.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                )

                if st.button(
                    favorite_text,
                    key=(
                        "favorite_"
                        + project_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        project_id,
                    )

                    st.rerun()


# =========================================================
# 放置プロジェクト
# =========================================================

if stale_projects:
    st.divider()

    st.subheader(
        "🚨 そろそろ続きを思い出す？"
    )

    for project in sorted(
        stale_projects,
        key=lambda item: days_since_update(
            item
        ),
        reverse=True,
    ):
        with st.container(
            border=True,
        ):
            st.markdown(
                f"**{update_status_text(project)} "
                f"｜ {project.get('name', '')}**"
            )

            st.write(
                "➡️ "
                + (
                    project.get(
                        "next_action",
                        "",
                    )
                    or "次の作業は未登録"
                )
            )


# =========================================================
# 進捗一覧
# =========================================================

if active_projects:
    st.divider()

    st.subheader(
        "📊 プロジェクト進捗"
    )

    rows = []

    for project in active_projects:
        rows.append(
            {
                "プロジェクト": project.get(
                    "name",
                    "",
                ),
                "カテゴリー": project.get(
                    "category",
                    "",
                ),
                "進捗": int(
                    project.get(
                        "progress",
                        0,
                    )
                ),
                "最終更新": update_status_text(
                    project
                ),
            }
        )

    df = pd.DataFrame(
        rows
    ).sort_values(
        "進捗",
        ascending=False,
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "進捗": st.column_config.ProgressColumn(
                "進捗",
                min_value=0,
                max_value=100,
                format="%d%%",
            )
        },
    )


# =========================================================
# 編集・更新
# =========================================================

st.divider()

with st.expander(
    "✏️ プロジェクトを更新・編集"
):
    if not projects:
        st.caption(
            "まだプロジェクトがありません。"
        )

    else:
        sorted_projects = sorted(
            projects,
            key=lambda project: parse_datetime(
                project.get(
                    "updated_at",
                    "",
                )
            ),
            reverse=True,
        )

        for project in sorted_projects:
            project_id = project.get(
                "id",
                "",
            )

            st.markdown(
                f"### {project.get('name', '')}"
            )

            st.caption(
                f"{project.get('status', '')}"
                f" ｜ "
                f"{format_datetime(project.get('updated_at', ''))}"
            )

            with st.expander(
                "📝 内容を更新"
            ):
                edit_name = st.text_input(
                    "プロジェクト名",
                    value=project.get(
                        "name",
                        "",
                    ),
                    key=(
                        "edit_name_"
                        + project_id
                    ),
                )

                current_category = project.get(
                    "category",
                    "✨ その他",
                )

                edit_category = st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=(
                        CATEGORIES.index(
                            current_category
                        )
                        if current_category
                        in CATEGORIES
                        else len(
                            CATEGORIES
                        ) - 1
                    ),
                    key=(
                        "edit_category_"
                        + project_id
                    ),
                )

                edit_last_done = st.text_area(
                    "✅ 最後にやったこと",
                    value=project.get(
                        "last_done",
                        "",
                    ),
                    key=(
                        "edit_last_"
                        + project_id
                    ),
                )

                edit_next_action = st.text_area(
                    "➡️ 次にやること",
                    value=project.get(
                        "next_action",
                        "",
                    ),
                    key=(
                        "edit_next_"
                        + project_id
                    ),
                )

                edit_resume_memo = st.text_input(
                    "📍 再開地点・メモ",
                    value=project.get(
                        "resume_memo",
                        "",
                    ),
                    key=(
                        "edit_resume_"
                        + project_id
                    ),
                )

                edit_progress = st.slider(
                    "進捗率",
                    0,
                    100,
                    int(
                        project.get(
                            "progress",
                            0,
                        )
                    ),
                    5,
                    key=(
                        "edit_progress_"
                        + project_id
                    ),
                )

                current_status = project.get(
                    "status",
                    "▶️ 作業中",
                )

                edit_status = st.selectbox(
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
                        "edit_status_"
                        + project_id
                    ),
                )

                edit_favorite = st.checkbox(
                    "⭐ お気に入り",
                    value=project.get(
                        "favorite",
                        False,
                    ),
                    key=(
                        "edit_favorite_"
                        + project_id
                    ),
                )

                if st.button(
                    "💾 今の地点を保存",
                    key=(
                        "save_edit_"
                        + project_id
                    ),
                    use_container_width=True,
                ):
                    if not edit_name.strip():
                        st.error(
                            "プロジェクト名を入力してください。"
                        )

                    elif (
                        edit_status
                        != "✅ 完了"
                        and not edit_next_action.strip()
                    ):
                        st.error(
                            "次にやることを入力してください。"
                        )

                    else:
                        update_project(
                            data,
                            project_id,
                            edit_name.strip(),
                            edit_category,
                            edit_last_done.strip(),
                            edit_next_action.strip(),
                            edit_resume_memo.strip(),
                            edit_progress,
                            edit_status,
                            edit_favorite,
                        )

                        st.rerun()

            # ---------------------------------------------
            # 履歴
            # ---------------------------------------------

            history = project.get(
                "history",
                [],
            )

            if history:
                with st.expander(
                    f"🕰️ 更新履歴 "
                    f"({len(history)}件)"
                ):
                    for history_item in reversed(
                        history
                    ):
                        st.markdown(
                            "**"
                            + format_datetime(
                                history_item.get(
                                    "saved_at",
                                    "",
                                )
                            )
                            + "**"
                        )

                        st.caption(
                            f"進捗："
                            f"{history_item.get('progress', 0)}%"
                            f" ｜ "
                            f"{history_item.get('status', '')}"
                        )

                        if history_item.get(
                            "last_done",
                            "",
                        ):
                            st.write(
                                "✅ "
                                + history_item.get(
                                    "last_done",
                                    "",
                                )
                            )

                        if history_item.get(
                            "next_action",
                            "",
                        ):
                            st.write(
                                "➡️ "
                                + history_item.get(
                                    "next_action",
                                    "",
                                )
                            )

                        if history_item.get(
                            "resume_memo",
                            "",
                        ):
                            st.caption(
                                "📍 "
                                + history_item.get(
                                    "resume_memo",
                                    "",
                                )
                            )

                        st.divider()

            # ---------------------------------------------
            # 削除
            # ---------------------------------------------

            with st.expander(
                "🗑️ 削除"
            ):
                if st.button(
                    "このプロジェクトを削除",
                    key=(
                        "delete_"
                        + project_id
                    ),
                    use_container_width=True,
                ):
                    delete_project(
                        data,
                        project_id,
                    )

                    if (
                        st.session_state.get(
                            "resume_project_id"
                        )
                        == project_id
                    ):
                        st.session_state.pop(
                            "resume_project_id",
                            None,
                        )

                    st.rerun()

            st.divider()


# =========================================================
# 完了プロジェクト
# =========================================================

if completed_projects:
    st.divider()

    with st.expander(
        "🏆 完了したプロジェクト"
    ):
        for project in sorted(
            completed_projects,
            key=lambda item: parse_datetime(
                item.get(
                    "completed_at",
                    "",
                )
            ),
            reverse=True,
        ):
            st.markdown(
                f"### ✅ {project.get('name', '')}"
            )

            st.caption(
                project.get(
                    "category",
                    "",
                )
            )

            if project.get(
                "completed_at",
                "",
            ):
                st.write(
                    "🏁 完了："
                    + format_datetime(
                        project.get(
                            "completed_at",
                            "",
                        )
                    )
                )

            if project.get(
                "last_done",
                "",
            ):
                st.write(
                    "**最後にやったこと**"
                )

                st.write(
                    project.get(
                        "last_done",
                        "",
                    )
                )

            st.divider()


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
            "where_was_i_"
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
    "未来の自分が迷わないように、続きをここに置いておこう。🔖✨"
)
