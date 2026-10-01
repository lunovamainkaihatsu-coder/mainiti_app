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
    page_title="一旦ここまで！",
    page_icon="💾",
    layout="wide",
)


# =========================================================
# 定数
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "saves.json")

CATEGORIES = [
    "💻 開発",
    "📚 勉強",
    "🎨 制作",
    "✍️ 執筆",
    "💼 仕事",
    "🏠 生活",
    "✨ その他",
]

STATES = [
    "🟢 キリがいい",
    "🟡 途中",
    "🔴 詰まっている",
    "💡 アイデアが浮かんだ",
]

HELPFUL_LEVELS = [
    "😊 かなり役立った",
    "😐 普通",
    "😣 あまり役立たなかった",
]


# =========================================================
# 基本関数
# =========================================================

def create_id():
    return str(uuid.uuid4())


def now():
    return datetime.now()


def now_text():
    return now().isoformat(timespec="seconds")


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def create_empty_data():
    return {
        "projects": [],
        "saves": [],
        "resumes": [],
    }


def days_since(value):
    dt = parse_datetime(value)

    if not dt:
        return 0

    return max(
        (date.today() - dt.date()).days,
        0,
    )


def duration_text(start_value, end_value=None):
    start = parse_datetime(start_value)

    if not start:
        return "-"

    if end_value:
        end = parse_datetime(end_value)
    else:
        end = now()

    if not end:
        end = now()

    seconds = max(
        int((end - start).total_seconds()),
        0,
    )

    minutes = seconds // 60

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours < 24:
        if remaining_minutes:
            return f"{hours}時間{remaining_minutes}分"

        return f"{hours}時間"

    days = hours // 24
    remaining_hours = hours % 24

    if remaining_hours:
        return f"{days}日{remaining_hours}時間"

    return f"{days}日"


def format_datetime(value):
    dt = parse_datetime(value)

    if not dt:
        return "-"

    return dt.strftime("%Y/%m/%d %H:%M")


# =========================================================
# 保存・読み込み
# =========================================================

def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)

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
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
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

        if not isinstance(data, dict):
            data = create_empty_data()

        data.setdefault("projects", [])
        data.setdefault("saves", [])
        data.setdefault("resumes", [])

        # -------------------------
        # プロジェクト補完
        # -------------------------

        for project in data["projects"]:
            project.setdefault("id", create_id())
            project.setdefault("name", "")
            project.setdefault(
                "category",
                "✨ その他",
            )
            project.setdefault("memo", "")
            project.setdefault("archived", False)
            project.setdefault("created_at", now_text())
            project.setdefault(
                "updated_at",
                project.get("created_at", now_text()),
            )

        # -------------------------
        # セーブ補完
        # -------------------------

        for save in data["saves"]:
            save.setdefault("id", create_id())
            save.setdefault("project_id", "")
            save.setdefault("save_number", 1)
            save.setdefault("done", "")
            save.setdefault("state", STATES[1])
            save.setdefault("next_action", "")
            save.setdefault("first_step", "")
            save.setdefault("concern", "")
            save.setdefault("memo", "")
            save.setdefault("favorite", False)
            save.setdefault("resumed", False)
            save.setdefault("resumed_at", None)
            save.setdefault("created_at", now_text())
            save.setdefault(
                "updated_at",
                save.get("created_at", now_text()),
            )

        # -------------------------
        # 再開履歴補完
        # -------------------------

        for resume in data["resumes"]:
            resume.setdefault("id", create_id())
            resume.setdefault("project_id", "")
            resume.setdefault("save_id", "")
            resume.setdefault("resumed_at", now_text())
            resume.setdefault("helpful", "")
            resume.setdefault("resume_minutes", None)
            resume.setdefault("memo", "")

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
# データ取得
# =========================================================

def get_project(data, project_id):
    return next(
        (
            project
            for project in data["projects"]
            if project.get("id") == project_id
        ),
        None,
    )


def get_save(data, save_id):
    return next(
        (
            save
            for save in data["saves"]
            if save.get("id") == save_id
        ),
        None,
    )


def project_saves(data, project_id):
    return [
        save
        for save in data["saves"]
        if save.get("project_id") == project_id
    ]


def latest_save(data, project_id):
    saves = project_saves(data, project_id)

    if not saves:
        return None

    return max(
        saves,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
    )


def next_save_number(data, project_id):
    saves = project_saves(data, project_id)

    if not saves:
        return 1

    return max(
        int(save.get("save_number", 1))
        for save in saves
    ) + 1


# =========================================================
# CRUD
# =========================================================

def create_project(
    data,
    name,
    category,
    memo="",
):
    project_id = create_id()

    data["projects"].append(
        {
            "id": project_id,
            "name": name,
            "category": category,
            "memo": memo,
            "archived": False,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
    )

    save_data(data)

    return project_id


def create_save(
    data,
    project_id,
    done,
    state,
    next_action,
    first_step,
    concern,
    memo,
):
    save_record = {
        "id": create_id(),
        "project_id": project_id,
        "save_number": next_save_number(
            data,
            project_id,
        ),
        "done": done,
        "state": state,
        "next_action": next_action,
        "first_step": first_step,
        "concern": concern,
        "memo": memo,
        "favorite": False,
        "resumed": False,
        "resumed_at": None,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["saves"].append(save_record)

    project = get_project(
        data,
        project_id,
    )

    if project:
        project["updated_at"] = now_text()

    save_data(data)

    return save_record["id"]


def resume_save(
    data,
    save_id,
):
    save = get_save(
        data,
        save_id,
    )

    if not save:
        return

    resume_time = now_text()

    save["resumed"] = True
    save["resumed_at"] = resume_time
    save["updated_at"] = resume_time

    created = parse_datetime(
        save.get("created_at")
    )

    resumed = parse_datetime(
        resume_time
    )

    resume_minutes = None

    if created and resumed:
        resume_minutes = max(
            int(
                (
                    resumed - created
                ).total_seconds()
                // 60
            ),
            0,
        )

    data["resumes"].append(
        {
            "id": create_id(),
            "project_id": save.get(
                "project_id",
                "",
            ),
            "save_id": save_id,
            "resumed_at": resume_time,
            "helpful": "",
            "resume_minutes": resume_minutes,
            "memo": "",
        }
    )

    project = get_project(
        data,
        save.get("project_id"),
    )

    if project:
        project["updated_at"] = resume_time

    save_data(data)


def update_resume_feedback(
    data,
    save_id,
    helpful,
    memo,
):
    matches = [
        resume
        for resume in data["resumes"]
        if resume.get("save_id") == save_id
    ]

    if not matches:
        return

    latest = max(
        matches,
        key=lambda item: item.get(
            "resumed_at",
            "",
        ),
    )

    latest["helpful"] = helpful
    latest["memo"] = memo

    save_data(data)


def toggle_favorite(
    data,
    save_id,
):
    save = get_save(
        data,
        save_id,
    )

    if not save:
        return

    save["favorite"] = not save.get(
        "favorite",
        False,
    )
    save["updated_at"] = now_text()

    save_data(data)


def update_save(
    data,
    save_id,
    done,
    state,
    next_action,
    first_step,
    concern,
    memo,
):
    save = get_save(
        data,
        save_id,
    )

    if not save:
        return

    save["done"] = done
    save["state"] = state
    save["next_action"] = next_action
    save["first_step"] = first_step
    save["concern"] = concern
    save["memo"] = memo
    save["updated_at"] = now_text()

    save_data(data)


def update_project(
    data,
    project_id,
    name,
    category,
    memo,
):
    project = get_project(
        data,
        project_id,
    )

    if not project:
        return

    project["name"] = name
    project["category"] = category
    project["memo"] = memo
    project["updated_at"] = now_text()

    save_data(data)


def delete_save(
    data,
    save_id,
):
    data["saves"] = [
        save
        for save in data["saves"]
        if save.get("id") != save_id
    ]

    data["resumes"] = [
        resume
        for resume in data["resumes"]
        if resume.get("save_id") != save_id
    ]

    save_data(data)


def delete_project(
    data,
    project_id,
):
    save_ids = {
        save.get("id")
        for save in data["saves"]
        if save.get("project_id") == project_id
    }

    data["projects"] = [
        project
        for project in data["projects"]
        if project.get("id") != project_id
    ]

    data["saves"] = [
        save
        for save in data["saves"]
        if save.get("project_id") != project_id
    ]

    data["resumes"] = [
        resume
        for resume in data["resumes"]
        if (
            resume.get("project_id") != project_id
            and resume.get("save_id") not in save_ids
        )
    ]

    save_data(data)


# =========================================================
# 分析
# =========================================================

def average(values):
    values = [
        value
        for value in values
        if value is not None
    ]

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        1,
    )


def resume_duration_label(minutes):
    if minutes is None:
        return "-"

    minutes = int(minutes)

    if minutes < 60:
        return f"{minutes}分"

    hours = minutes // 60
    remaining = minutes % 60

    if hours < 24:
        if remaining:
            return f"{hours}時間{remaining}分"

        return f"{hours}時間"

    days = hours // 24
    remaining_hours = hours % 24

    if remaining_hours:
        return f"{days}日{remaining_hours}時間"

    return f"{days}日"


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 16px;
        background: rgba(120, 120, 230, 0.07);
        border: 1px solid rgba(120, 120, 230, 0.15);
    }

    .hero {
        padding: 32px;
        border-radius: 26px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(105, 95, 220, 0.20),
                rgba(100, 180, 230, 0.08)
            );
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 10px;
        margin-bottom: 0;
        opacity: 0.82;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# データ
# =========================================================

data = load_data()

projects = [
    project
    for project in data["projects"]
    if not project.get(
        "archived",
        False,
    )
]

saves = data["saves"]
resumes = data["resumes"]


# =========================================================
# ヘッダー
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🛑 一旦ここまで！</h1>
        <p>
            今日の自分から、次に作業する自分へ。
            「続きから始められる場所」を残そう。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ダッシュボード
# =========================================================

current_month = date.today().strftime(
    "%Y-%m"
)

month_saves = [
    save
    for save in saves
    if (
        save.get(
            "created_at",
            "",
        )
        or ""
    ).startswith(current_month)
]

month_resumes = [
    resume
    for resume in resumes
    if (
        resume.get(
            "resumed_at",
            "",
        )
        or ""
    ).startswith(current_month)
]

resume_minutes = [
    resume.get("resume_minutes")
    for resume in month_resumes
    if resume.get("resume_minutes")
    is not None
]

avg_resume_minutes = average(
    resume_minutes
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💾 今月のセーブ",
    f"{len(month_saves)}回",
)

col2.metric(
    "▶️ 今月の再開",
    f"{len(month_resumes)}回",
)

col3.metric(
    "📂 プロジェクト",
    f"{len(projects)}個",
)

col4.metric(
    "⏱️ 平均再開間隔",
    (
        resume_duration_label(
            avg_resume_minutes
        )
        if resume_minutes
        else "-"
    ),
)


# =========================================================
# 続きから
# =========================================================

st.divider()

st.subheader("▶️ 続きから")

latest_unresumed = []

for project in projects:
    latest = latest_save(
        data,
        project.get("id"),
    )

    if (
        latest
        and not latest.get(
            "resumed",
            False,
        )
    ):
        latest_unresumed.append(
            (project, latest)
        )


if not latest_unresumed:
    st.info(
        "今、再開待ちのセーブデータはありません。"
    )

else:
    latest_unresumed.sort(
        key=lambda pair: pair[1].get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    for project, save in latest_unresumed:
        project_id = project.get(
            "id",
            "",
        )
        save_id = save.get(
            "id",
            "",
        )

        with st.container(border=True):
            col1, col2 = st.columns(
                [7, 1]
            )

            with col1:
                st.subheader(
                    "▶️ "
                    + project.get(
                        "name",
                        "",
                    )
                )

            with col2:
                if st.button(
                    (
                        "⭐"
                        if save.get(
                            "favorite",
                            False,
                        )
                        else "☆"
                    ),
                    key=(
                        "latest_fav_"
                        + save_id
                    ),
                ):
                    toggle_favorite(
                        data,
                        save_id,
                    )
                    st.rerun()

            st.caption(
                project.get(
                    "category",
                    "",
                )
                + " ｜ Save #"
                + str(
                    save.get(
                        "save_number",
                        1,
                    )
                )
                + " ｜ "
                + format_datetime(
                    save.get(
                        "created_at"
                    )
                )
            )

            st.write(
                "**状態：** "
                + save.get(
                    "state",
                    "",
                )
            )

            if save.get("done"):
                st.write(
                    "✅ **できたところ**"
                )
                st.write(
                    save.get(
                        "done",
                        "",
                    )
                )

            if save.get(
                "next_action"
            ):
                st.write(
                    "🎯 **次にやること**"
                )
                st.write(
                    save.get(
                        "next_action",
                        "",
                    )
                )

            if save.get(
                "first_step"
            ):
                st.write(
                    "👉 **最初の一手**"
                )
                st.info(
                    save.get(
                        "first_step",
                        "",
                    )
                )

            if save.get("concern"):
                st.write(
                    "⚠️ **気になっていること**"
                )
                st.write(
                    save.get(
                        "concern",
                        "",
                    )
                )

            st.caption(
                "💤 セーブしてから "
                + duration_text(
                    save.get(
                        "created_at"
                    )
                )
            )

            if st.button(
                "▶️ 作業を再開",
                type="primary",
                use_container_width=True,
                key=(
                    "resume_"
                    + save_id
                ),
            ):
                gap_days = days_since(
                    save.get(
                        "created_at"
                    )
                )

                resume_save(
                    data,
                    save_id,
                )

                st.session_state[
                    "last_resumed_save"
                ] = save_id

                st.session_state[
                    "last_resume_gap_days"
                ] = gap_days

                st.rerun()


# =========================================================
# 再開直後
# =========================================================

last_resumed_save_id = (
    st.session_state.get(
        "last_resumed_save"
    )
)

if last_resumed_save_id:
    resumed_save = get_save(
        data,
        last_resumed_save_id,
    )

    if resumed_save:
        resumed_project = get_project(
            data,
            resumed_save.get(
                "project_id"
            ),
        )

        if resumed_project:
            st.divider()

            gap_days = st.session_state.get(
                "last_resume_gap_days",
                0,
            )

            if gap_days >= 7:
                st.success(
                    "🏆 おかえり！ "
                    f"{gap_days}日ぶりに"
                    "このプロジェクトへ戻ってきました。"
                )
            else:
                st.success(
                    "🚀 作業再開！"
                )

            st.subheader(
                resumed_project.get(
                    "name",
                    "",
                )
            )

            if resumed_save.get(
                "first_step"
            ):
                st.write(
                    "👉 **まずはこれから**"
                )
                st.info(
                    resumed_save.get(
                        "first_step",
                        "",
                    )
                )

            with st.form(
                "resume_feedback_"
                + last_resumed_save_id
            ):
                helpful = st.selectbox(
                    "前回決めた「最初の一手」は役立った？",
                    HELPFUL_LEVELS,
                    index=0,
                )

                feedback_memo = (
                    st.text_area(
                        "再開メモ",
                        placeholder=(
                            "実際に再開してみて"
                            "気づいたことなど"
                        ),
                    )
                )

                submitted = (
                    st.form_submit_button(
                        "📝 再開記録を保存",
                        use_container_width=True,
                    )
                )

                if submitted:
                    update_resume_feedback(
                        data,
                        last_resumed_save_id,
                        helpful,
                        feedback_memo.strip(),
                    )

                    st.session_state.pop(
                        "last_resumed_save",
                        None,
                    )

                    st.session_state.pop(
                        "last_resume_gap_days",
                        None,
                    )

                    st.rerun()


# =========================================================
# セーブ
# =========================================================

st.divider()

st.subheader("💾 ここでセーブ")

save_mode = st.radio(
    "どの作業をセーブする？",
    [
        "📂 既存プロジェクト",
        "✨ 新しいプロジェクト",
    ],
    horizontal=True,
)


selected_project_id = None

if save_mode == "📂 既存プロジェクト":
    if not projects:
        st.info(
            "まだプロジェクトがありません。"
            "「新しいプロジェクト」を選んで作成しよう。"
        )
    else:
        project_options = {
            project.get("id"): (
                project.get(
                    "category",
                    "",
                )
                + " "
                + project.get(
                    "name",
                    "",
                )
            )
            for project in projects
        }

        selected_project_id = (
            st.selectbox(
                "📂 プロジェクト",
                list(
                    project_options.keys()
                ),
                format_func=lambda value: (
                    project_options[value]
                ),
            )
        )


with st.form(
    "save_point_form",
    clear_on_submit=True,
):
    if save_mode == "✨ 新しいプロジェクト":
        new_project_name = (
            st.text_input(
                "📂 プロジェクト名",
                placeholder=(
                    "例：AI Router"
                ),
            )
        )

        new_category = st.selectbox(
            "🏷️ カテゴリー",
            CATEGORIES,
        )

        new_project_memo = (
            st.text_input(
                "プロジェクトメモ",
                placeholder=(
                    "任意"
                ),
            )
        )

    done = st.text_area(
        "✅ 今日できたところ",
        placeholder=(
            "例：Geminiの検索処理まで完成"
        ),
    )

    state = st.selectbox(
        "🚦 今の状態",
        STATES,
        index=1,
    )

    next_action = st.text_area(
        "🎯 次にやること",
        placeholder=(
            "例：検索結果の表示を整える"
        ),
    )

    first_step = st.text_input(
        "👉 次回の最初の一手",
        placeholder=(
            "例：route.tsを開く"
        ),
    )

    concern = st.text_area(
        "⚠️ 気になっていること",
        placeholder=(
            "例：エラー時の表示がまだ弱い"
        ),
    )

    save_memo = st.text_area(
        "📝 その他メモ",
        placeholder="任意",
    )

    submitted = (
        st.form_submit_button(
            "💾 ここでセーブ",
            type="primary",
            use_container_width=True,
        )
    )

    if submitted:
        project_id = (
            selected_project_id
        )

        if save_mode == "✨ 新しいプロジェクト":
            if not new_project_name.strip():
                st.warning(
                    "プロジェクト名を入力してね。"
                )
                st.stop()

            project_id = create_project(
                data,
                new_project_name.strip(),
                new_category,
                new_project_memo.strip(),
            )

        if not project_id:
            st.warning(
                "プロジェクトを選択してね。"
            )

        elif not next_action.strip():
            st.warning(
                "次にやることを残しておくと、"
                "次回かなり戻りやすくなるよ。"
            )

        else:
            save_id = create_save(
                data=data,
                project_id=project_id,
                done=done.strip(),
                state=state,
                next_action=(
                    next_action.strip()
                ),
                first_step=(
                    first_step.strip()
                ),
                concern=concern.strip(),
                memo=save_memo.strip(),
            )

            st.session_state[
                "just_saved"
            ] = save_id

            st.rerun()


just_saved_id = st.session_state.pop(
    "just_saved",
    None,
)

if just_saved_id:
    saved = get_save(
        data,
        just_saved_id,
    )

    if saved:
        project = get_project(
            data,
            saved.get(
                "project_id"
            ),
        )

        if project:
            st.success(
                "💾 Save #"
                + str(
                    saved.get(
                        "save_number",
                        1,
                    )
                )
                + " 完了！ "
                + project.get(
                    "name",
                    "",
                )
                + " の続きは、"
                "ここから始められます。"
            )


# =========================================================
# プロジェクト一覧
# =========================================================

st.divider()

st.subheader("📂 セーブデータ")

if not projects:
    st.info(
        "まだプロジェクトがありません。"
    )

else:
    for project in sorted(
        projects,
        key=lambda item: item.get(
            "updated_at",
            "",
        ),
        reverse=True,
    ):
        latest = latest_save(
            data,
            project.get("id"),
        )

        with st.container(border=True):
            st.subheader(
                project.get(
                    "category",
                    "",
                )
                + " "
                + project.get(
                    "name",
                    "",
                )
            )

            if not latest:
                st.caption(
                    "まだセーブデータがありません。"
                )
                continue

            st.caption(
                "Save #"
                + str(
                    latest.get(
                        "save_number",
                        1,
                    )
                )
                + " ｜ "
                + format_datetime(
                    latest.get(
                        "created_at"
                    )
                )
            )

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.write(
                "**状態**"
            )
            col1.write(
                latest.get(
                    "state",
                    "",
                )
            )

            col2.metric(
                "💾 セーブ数",
                len(
                    project_saves(
                        data,
                        project.get(
                            "id"
                        ),
                    )
                ),
            )

            col3.metric(
                "💤 最終セーブから",
                (
                    f"{days_since(latest.get('created_at'))}日"
                ),
            )

            if latest.get(
                "next_action"
            ):
                st.write(
                    "🎯 **次：** "
                    + latest.get(
                        "next_action",
                        "",
                    )
                )

            if latest.get(
                "first_step"
            ):
                st.write(
                    "👉 **最初の一手：** "
                    + latest.get(
                        "first_step",
                        "",
                    )
                )


# =========================================================
# 放置プロジェクト
# =========================================================

st.divider()

st.subheader(
    "😴 しばらく再開していない"
)

stale_projects = []

for project in projects:
    latest = latest_save(
        data,
        project.get("id"),
    )

    if not latest:
        continue

    if latest.get(
        "resumed",
        False,
    ):
        continue

    stale_days = days_since(
        latest.get(
            "created_at"
        )
    )

    if stale_days >= 7:
        stale_projects.append(
            (
                stale_days,
                project,
                latest,
            )
        )


if not stale_projects:
    st.caption(
        "7日以上止まっている"
        "再開待ちプロジェクトはありません。"
    )

else:
    stale_projects.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    for (
        stale_days,
        project,
        save,
    ) in stale_projects:
        with st.container(border=True):
            if stale_days >= 30:
                level = "💤"
            elif stale_days >= 14:
                level = "😴"
            else:
                level = "🌙"

            st.subheader(
                level
                + " "
                + project.get(
                    "name",
                    "",
                )
            )

            st.write(
                f"最後のセーブから **{stale_days}日**"
            )

            if save.get(
                "next_action"
            ):
                st.write(
                    "🎯 **次にやること：** "
                    + save.get(
                        "next_action",
                        "",
                    )
                )

            if save.get(
                "first_step"
            ):
                st.write(
                    "👉 **最初の一手：** "
                    + save.get(
                        "first_step",
                        "",
                    )
                )

            if st.button(
                "▶️ 久しぶりに再開",
                key=(
                    "stale_resume_"
                    + save.get(
                        "id",
                        "",
                    )
                ),
                use_container_width=True,
            ):
                resume_save(
                    data,
                    save.get("id"),
                )

                st.session_state[
                    "last_resumed_save"
                ] = save.get("id")

                st.session_state[
                    "last_resume_gap_days"
                ] = stale_days

                st.rerun()


# =========================================================
# 月間分析
# =========================================================

st.divider()

st.subheader(
    f"📊 {date.today().month}月の再開力"
)

if not month_saves and not month_resumes:
    st.info(
        "今月のデータはまだありません。"
    )

else:
    resumed_save_ids = {
        resume.get("save_id")
        for resume in month_resumes
    }

    resume_rate = (
        round(
            len(resumed_save_ids)
            / len(month_saves)
            * 100
        )
        if month_saves
        else 0
    )

    longest_minutes = max(
        resume_minutes,
        default=None,
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "💾 セーブ",
        f"{len(month_saves)}回",
    )

    col2.metric(
        "▶️ 再開",
        f"{len(month_resumes)}回",
    )

    col3.metric(
        "🔁 再開率",
        f"{resume_rate}%",
    )

    col4.metric(
        "🕰️ 最長再開間隔",
        (
            resume_duration_label(
                longest_minutes
            )
            if longest_minutes
            is not None
            else "-"
        ),
    )

    # -------------------------
    # 状態別
    # -------------------------

    state_rows = []

    for state in STATES:
        count = len(
            [
                save
                for save in month_saves
                if save.get(
                    "state"
                )
                == state
            ]
        )

        state_rows.append(
            {
                "状態": state,
                "回数": count,
            }
        )

    state_df = pd.DataFrame(
        state_rows
    )

    st.markdown(
        "### 🧠 作業を止めた状態"
    )

    st.bar_chart(
        state_df.set_index(
            "状態"
        )
    )

    # -------------------------
    # カテゴリー別
    # -------------------------

    category_counts = {}

    for save in month_saves:
        project = get_project(
            data,
            save.get(
                "project_id"
            ),
        )

        if not project:
            continue

        category = project.get(
            "category",
            "✨ その他",
        )

        category_counts[
            category
        ] = (
            category_counts.get(
                category,
                0,
            )
            + 1
        )

    if category_counts:
        category_df = pd.DataFrame(
            [
                {
                    "カテゴリー": key,
                    "セーブ回数": value,
                }
                for key, value
                in category_counts.items()
            ]
        )

        st.markdown(
            "### 📂 カテゴリー別セーブ"
        )

        st.bar_chart(
            category_df.set_index(
                "カテゴリー"
            )
        )


# =========================================================
# 最初の一手 分析
# =========================================================

feedback_resumes = [
    resume
    for resume in resumes
    if resume.get(
        "helpful"
    )
]

if feedback_resumes:
    st.divider()

    st.subheader(
        "👉 「最初の一手」は役立った？"
    )

    helpful_rows = []

    for level in HELPFUL_LEVELS:
        count = len(
            [
                resume
                for resume
                in feedback_resumes
                if resume.get(
                    "helpful"
                )
                == level
            ]
        )

        helpful_rows.append(
            {
                "評価": level,
                "回数": count,
            }
        )

    helpful_df = pd.DataFrame(
        helpful_rows
    )

    st.bar_chart(
        helpful_df.set_index(
            "評価"
        )
    )


# =========================================================
# お気に入り
# =========================================================

favorite_saves = [
    save
    for save in saves
    if save.get(
        "favorite",
        False,
    )
]

if favorite_saves:
    st.divider()

    st.subheader(
        "⭐ 大事なセーブ"
    )

    for save in sorted(
        favorite_saves,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    ):
        project = get_project(
            data,
            save.get(
                "project_id"
            ),
        )

        if not project:
            continue

        with st.container(border=True):
            st.write(
                "⭐ **"
                + project.get(
                    "name",
                    "",
                )
                + " / Save #"
                + str(
                    save.get(
                        "save_number",
                        1,
                    )
                )
                + "**"
            )

            st.caption(
                format_datetime(
                    save.get(
                        "created_at"
                    )
                )
            )

            if save.get(
                "next_action"
            ):
                st.write(
                    "🎯 "
                    + save.get(
                        "next_action",
                        "",
                    )
                )

            if save.get(
                "first_step"
            ):
                st.write(
                    "👉 "
                    + save.get(
                        "first_step",
                        "",
                    )
                )


# =========================================================
# セーブ履歴
# =========================================================

st.divider()

st.subheader(
    "📜 セーブ履歴"
)

search_text = st.text_input(
    "🔎 検索",
    placeholder=(
        "プロジェクト名、次にやること、メモ……"
    ),
)

category_filter = st.selectbox(
    "カテゴリー",
    ["すべて"] + CATEGORIES,
    key="history_category",
)

history_rows = []

for save in saves:
    project = get_project(
        data,
        save.get(
            "project_id"
        ),
    )

    if not project:
        continue

    if (
        category_filter != "すべて"
        and project.get(
            "category"
        )
        != category_filter
    ):
        continue

    searchable = " ".join(
        [
            project.get(
                "name",
                "",
            ),
            save.get(
                "done",
                "",
            ),
            save.get(
                "next_action",
                "",
            ),
            save.get(
                "first_step",
                "",
            ),
            save.get(
                "concern",
                "",
            ),
            save.get(
                "memo",
                "",
            ),
        ]
    ).lower()

    if (
        search_text.strip()
        and search_text.strip().lower()
        not in searchable
    ):
        continue

    history_rows.append(
        {
            "日時": format_datetime(
                save.get(
                    "created_at"
                )
            ),
            "プロジェクト": (
                project.get(
                    "name",
                    "",
                )
            ),
            "Save": (
                "#"
                + str(
                    save.get(
                        "save_number",
                        1,
                    )
                )
            ),
            "状態": save.get(
                "state",
                "",
            ),
            "次にやること": (
                save.get(
                    "next_action",
                    "",
                )
            ),
            "再開": (
                "▶️"
                if save.get(
                    "resumed",
                    False,
                )
                else "💤"
            ),
            "⭐": (
                "⭐"
                if save.get(
                    "favorite",
                    False,
                )
                else ""
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
else:
    st.info(
        "条件に合うセーブはありません。"
    )


# =========================================================
# 編集・管理
# =========================================================

st.divider()

with st.expander(
    "🛠️ 編集・管理"
):
    # -------------------------
    # プロジェクト管理
    # -------------------------

    st.markdown(
        "### 📂 プロジェクト"
    )

    for project in projects:
        project_id = project.get(
            "id",
            "",
        )

        with st.expander(
            project.get(
                "category",
                "",
            )
            + " "
            + project.get(
                "name",
                "",
            )
        ):
            edit_name = st.text_input(
                "プロジェクト名",
                value=project.get(
                    "name",
                    "",
                ),
                key=(
                    "project_name_"
                    + project_id
                ),
            )

            old_category = project.get(
                "category",
                "✨ その他",
            )

            category_index = (
                CATEGORIES.index(
                    old_category
                )
                if old_category
                in CATEGORIES
                else len(
                    CATEGORIES
                ) - 1
            )

            edit_category = (
                st.selectbox(
                    "カテゴリー",
                    CATEGORIES,
                    index=category_index,
                    key=(
                        "project_category_"
                        + project_id
                    ),
                )
            )

            edit_memo = st.text_area(
                "プロジェクトメモ",
                value=project.get(
                    "memo",
                    "",
                ),
                key=(
                    "project_memo_"
                    + project_id
                ),
            )

            if st.button(
                "💾 プロジェクトを保存",
                key=(
                    "save_project_"
                    + project_id
                ),
                use_container_width=True,
            ):
                if not edit_name.strip():
                    st.warning(
                        "プロジェクト名を入力してね。"
                    )
                else:
                    update_project(
                        data,
                        project_id,
                        edit_name.strip(),
                        edit_category,
                        edit_memo.strip(),
                    )
                    st.rerun()

            confirm_project_delete = (
                st.checkbox(
                    "このプロジェクトと"
                    "全セーブを削除する",
                    key=(
                        "confirm_project_delete_"
                        + project_id
                    ),
                )
            )

            if st.button(
                "🗑️ プロジェクトを完全削除",
                key=(
                    "delete_project_"
                    + project_id
                ),
                disabled=(
                    not confirm_project_delete
                ),
                use_container_width=True,
            ):
                delete_project(
                    data,
                    project_id,
                )
                st.rerun()

    # -------------------------
    # セーブ管理
    # -------------------------

    st.markdown(
        "### 💾 セーブデータ"
    )

    for save in sorted(
        saves,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    ):
        project = get_project(
            data,
            save.get(
                "project_id"
            ),
        )

        if not project:
            continue

        save_id = save.get(
            "id",
            "",
        )

        with st.expander(
            project.get(
                "name",
                "",
            )
            + " ｜ Save #"
            + str(
                save.get(
                    "save_number",
                    1,
                )
            )
        ):
            edit_done = st.text_area(
                "できたところ",
                value=save.get(
                    "done",
                    "",
                ),
                key=(
                    "edit_done_"
                    + save_id
                ),
            )

            old_state = save.get(
                "state",
                STATES[1],
            )

            state_index = (
                STATES.index(
                    old_state
                )
                if old_state
                in STATES
                else 1
            )

            edit_state = st.selectbox(
                "状態",
                STATES,
                index=state_index,
                key=(
                    "edit_state_"
                    + save_id
                ),
            )

            edit_next = st.text_area(
                "次にやること",
                value=save.get(
                    "next_action",
                    "",
                ),
                key=(
                    "edit_next_"
                    + save_id
                ),
            )

            edit_first = st.text_input(
                "最初の一手",
                value=save.get(
                    "first_step",
                    "",
                ),
                key=(
                    "edit_first_"
                    + save_id
                ),
            )

            edit_concern = (
                st.text_area(
                    "気になっていること",
                    value=save.get(
                        "concern",
                        "",
                    ),
                    key=(
                        "edit_concern_"
                        + save_id
                    ),
                )
            )

            edit_memo = st.text_area(
                "メモ",
                value=save.get(
                    "memo",
                    "",
                ),
                key=(
                    "edit_save_memo_"
                    + save_id
                ),
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 保存",
                    key=(
                        "update_save_"
                        + save_id
                    ),
                    use_container_width=True,
                ):
                    update_save(
                        data,
                        save_id,
                        edit_done.strip(),
                        edit_state,
                        edit_next.strip(),
                        edit_first.strip(),
                        edit_concern.strip(),
                        edit_memo.strip(),
                    )
                    st.rerun()

            with col2:
                favorite_label = (
                    "⭐ お気に入り解除"
                    if save.get(
                        "favorite",
                        False,
                    )
                    else "☆ お気に入り"
                )

                if st.button(
                    favorite_label,
                    key=(
                        "manage_fav_"
                        + save_id
                    ),
                    use_container_width=True,
                ):
                    toggle_favorite(
                        data,
                        save_id,
                    )
                    st.rerun()

            confirm_delete = (
                st.checkbox(
                    "削除を確認",
                    key=(
                        "confirm_save_delete_"
                        + save_id
                    ),
                )
            )

            if st.button(
                "🗑️ このセーブを完全削除",
                key=(
                    "delete_save_"
                    + save_id
                ),
                disabled=(
                    not confirm_delete
                ),
                use_container_width=True,
            ):
                delete_save(
                    data,
                    save_id,
                )
                st.rerun()


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
            "stop_here_"
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
    "🛑 今日はここまで。"
    "でも、次の自分が迷わないところまで残しておこう。"
)
