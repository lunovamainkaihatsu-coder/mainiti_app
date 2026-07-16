import json
import os
import uuid
from datetime import date

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="アプリ管理 | LuNova Developer OS",
    page_icon="📱",
    layout="wide"
)


APP_FILE = "data/apps.json"


def save_apps(apps):
    """アプリデータをJSONへ保存する"""
    os.makedirs("data", exist_ok=True)

    with open(APP_FILE, "w", encoding="utf-8") as file:
        json.dump(
            apps,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_apps():
    """JSONからアプリデータを読み込む"""
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(APP_FILE):
        save_apps([])
        return []

    try:
        with open(APP_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        save_apps([])
        return []

    except (json.JSONDecodeError, OSError):
        save_apps([])
        return []


def add_app(
    apps,
    name,
    category,
    progress,
    status,
    platform,
    description
):
    """新しいアプリを追加する"""
    new_app = {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "progress": progress,
        "status": status,
        "platform": platform,
        "description": description,
        "created_at": str(date.today())
    }

    apps.append(new_app)
    save_apps(apps)


def delete_app(apps, app_id):
    """指定したアプリを削除する"""
    updated_apps = [
        app
        for app in apps
        if app.get("id") != app_id
    ]

    save_apps(updated_apps)

def update_app(
    apps,
    app_id,
    name,
    category,
    progress,
    status,
    platform,
    description
):
    """登録済みアプリを更新する"""

    for app in apps:
        if app.get("id") == app_id:
            app["name"] = name
            app["category"] = category
            app["progress"] = progress
            app["status"] = status
            app["platform"] = platform
            app["description"] = description
            app["updated_at"] = str(date.today())
            break

    save_apps(apps)

apps = load_apps()


st.title("📱 アプリ管理")
st.caption("LuNovaで開発しているアプリを一元管理します。")

st.divider()


# =====================================
# 集計カード
# =====================================

total_apps = len(apps)

completed_apps = sum(
    1
    for app in apps
    if app.get("status") == "完成"
)

developing_apps = sum(
    1
    for app in apps
    if app.get("status") == "開発中"
)

published_apps = sum(
    1
    for app in apps
    if app.get("status") == "公開中"
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📦 登録アプリ",
        value=total_apps
    )

with col2:
    st.metric(
        label="🛠️ 開発中",
        value=developing_apps
    )

with col3:
    st.metric(
        label="✅ 完成",
        value=completed_apps
    )

with col4:
    st.metric(
        label="🌍 公開中",
        value=published_apps
    )


st.divider()


# =====================================
# アプリ登録フォーム
# =====================================

st.header("➕ 新しいアプリを登録")

with st.form(
    key="add_app_form",
    clear_on_submit=True
):
    form_col1, form_col2 = st.columns(2)

    with form_col1:
        app_name = st.text_input(
            "アプリ名",
            placeholder="例：LunaPocket"
        )

        category = st.selectbox(
            "カテゴリー",
            [
                "AI",
                "生活",
                "健康",
                "学習",
                "仕事",
                "お金",
                "エンタメ",
                "ゲーム",
                "開発支援",
                "その他"
            ]
        )

        platform = st.selectbox(
            "プラットフォーム",
            [
                "Web",
                "Android",
                "iOS",
                "Windows",
                "複数",
                "未定"
            ]
        )

    with form_col2:
        status = st.selectbox(
            "開発状況",
            [
                "アイデア",
                "設計中",
                "開発中",
                "テスト中",
                "完成",
                "公開中",
                "休止中"
            ],
            index=2
        )

        progress = st.slider(
            "完成度",
            min_value=0,
            max_value=100,
            value=10,
            step=5
        )

        description = st.text_area(
            "アプリの説明",
            placeholder="このアプリで実現したいことを書こう。"
        )

    submitted = st.form_submit_button(
        "📱 アプリを登録",
        use_container_width=True
    )

    if submitted:
        cleaned_name = app_name.strip()

        if not cleaned_name:
            st.error("アプリ名を入力してください。")

        elif any(
            app.get("name", "").lower() == cleaned_name.lower()
            for app in apps
        ):
            st.warning("同じ名前のアプリがすでに登録されています。")

        else:
            add_app(
                apps=apps,
                name=cleaned_name,
                category=category,
                progress=progress,
                status=status,
                platform=platform,
                description=description.strip()
            )

            st.success(
                f"「{cleaned_name}」を登録しました！"
            )

            st.rerun()


st.divider()


# =====================================
# アプリ一覧
# =====================================

st.header("📋 登録アプリ一覧")

if not apps:
    st.info(
        "まだアプリが登録されていません。"
        "上のフォームから最初のアプリを登録しよう！"
    )

else:
    search_word = st.text_input(
        "🔍 アプリを検索",
        placeholder="アプリ名やカテゴリーを入力"
    )

    status_filter = st.selectbox(
        "表示する開発状況",
        [
            "すべて",
            "アイデア",
            "設計中",
            "開発中",
            "テスト中",
            "完成",
            "公開中",
            "休止中"
        ]
    )

    filtered_apps = apps

    if search_word:
        keyword = search_word.lower()

        filtered_apps = [
            app
            for app in filtered_apps
            if keyword in app.get("name", "").lower()
            or keyword in app.get("category", "").lower()
            or keyword in app.get("description", "").lower()
        ]

    if status_filter != "すべて":
        filtered_apps = [
            app
            for app in filtered_apps
            if app.get("status") == status_filter
        ]

    st.write(
        f"表示件数：**{len(filtered_apps)}件**"
    )

    if not filtered_apps:
        st.warning("条件に一致するアプリがありません。")

    for app in filtered_apps:
        app_id = app.get("id", "")
        app_name = app.get("name", "名称未設定")
        progress = app.get("progress", 0)

        with st.container(border=True):
            title_col, status_col = st.columns([3, 1])

            with title_col:
                st.subheader(f"📱 {app_name}")

                st.caption(
                    f"{app.get('category', '未設定')} "
                    f"／ {app.get('platform', '未設定')}"
                )

            with status_col:
                st.markdown(
                    f"### {app.get('status', '未設定')}"
                )

            st.write(
                app.get("description", "")
                or "説明はまだ登録されていません。"
            )

            st.progress(progress / 100)
            st.write(f"完成度：**{progress}%**")

            created_at = app.get("created_at", "不明")
            updated_at = app.get("updated_at")

            st.caption(f"登録日：{created_at}")

            if updated_at:
                st.caption(f"最終更新日：{updated_at}")

            edit_tab, delete_tab = st.tabs(
                ["✏️ 編集", "🗑️ 削除"]
            )

            with edit_tab:
                with st.form(
                    key=f"edit_form_{app_id}"
                ):
                    edit_col1, edit_col2 = st.columns(2)

                    with edit_col1:
                        edited_name = st.text_input(
                            "アプリ名",
                            value=app.get("name", ""),
                            key=f"edit_name_{app_id}"
                        )

                        categories = [
                            "AI",
                            "生活",
                            "健康",
                            "学習",
                            "仕事",
                            "お金",
                            "エンタメ",
                            "ゲーム",
                            "開発支援",
                            "その他"
                        ]

                        current_category = app.get(
                            "category",
                            "その他"
                        )

                        if current_category not in categories:
                            current_category = "その他"

                        edited_category = st.selectbox(
                            "カテゴリー",
                            categories,
                            index=categories.index(
                                current_category
                            ),
                            key=f"edit_category_{app_id}"
                        )

                        platforms = [
                            "Web",
                            "Android",
                            "iOS",
                            "Windows",
                            "複数",
                            "未定"
                        ]

                        current_platform = app.get(
                            "platform",
                            "未定"
                        )

                        if current_platform not in platforms:
                            current_platform = "未定"

                        edited_platform = st.selectbox(
                            "プラットフォーム",
                            platforms,
                            index=platforms.index(
                                current_platform
                            ),
                            key=f"edit_platform_{app_id}"
                        )

                    with edit_col2:
                        statuses = [
                            "アイデア",
                            "設計中",
                            "開発中",
                            "テスト中",
                            "完成",
                            "公開中",
                            "休止中"
                        ]

                        current_status = app.get(
                            "status",
                            "アイデア"
                        )

                        if current_status not in statuses:
                            current_status = "アイデア"

                        edited_status = st.selectbox(
                            "開発状況",
                            statuses,
                            index=statuses.index(
                                current_status
                            ),
                            key=f"edit_status_{app_id}"
                        )

                        edited_progress = st.slider(
                            "完成度",
                            min_value=0,
                            max_value=100,
                            value=int(
                                app.get("progress", 0)
                            ),
                            step=5,
                            key=f"edit_progress_{app_id}"
                        )

                        edited_description = st.text_area(
                            "アプリの説明",
                            value=app.get(
                                "description",
                                ""
                            ),
                            key=f"edit_description_{app_id}"
                        )

                    update_button = st.form_submit_button(
                        "💾 変更を保存",
                        use_container_width=True
                    )

                    if update_button:
                        cleaned_name = edited_name.strip()

                        duplicate_exists = any(
                            other_app.get("id") != app_id
                            and other_app.get(
                                "name",
                                ""
                            ).lower() == cleaned_name.lower()
                            for other_app in apps
                        )

                        if not cleaned_name:
                            st.error(
                                "アプリ名を入力してください。"
                            )

                        elif duplicate_exists:
                            st.warning(
                                "同じ名前のアプリが"
                                "すでに登録されています。"
                            )

                        else:
                            update_app(
                                apps=apps,
                                app_id=app_id,
                                name=cleaned_name,
                                category=edited_category,
                                progress=edited_progress,
                                status=edited_status,
                                platform=edited_platform,
                                description=(
                                    edited_description.strip()
                                )
                            )

                            st.success(
                                f"「{cleaned_name}」を"
                                "更新しました！"
                            )

                            st.rerun()

            with delete_tab:
                st.warning(
                    "削除したアプリは元に戻せません。"
                )

                confirm_delete = st.checkbox(
                    "削除することを確認しました",
                    key=f"confirm_delete_{app_id}"
                )

                delete_button = st.button(
                    "🗑️ このアプリを削除",
                    key=f"delete_{app_id}",
                    use_container_width=True,
                    disabled=not confirm_delete
                )

                if delete_button:
                    delete_app(apps, app_id)

                    st.success(
                        f"「{app_name}」を削除しました。"
                    )

                    st.rerun()

st.divider()


# =====================================
# 表形式で確認
# =====================================

if apps:
    with st.expander("📊 表形式で確認"):
        table_data = []

        for app in apps:
            table_data.append(
                {
                    "アプリ名": app.get("name", ""),
                    "カテゴリー": app.get("category", ""),
                    "プラットフォーム": app.get(
                        "platform",
                        ""
                    ),
                    "開発状況": app.get("status", ""),
                    "完成度": app.get("progress", 0),
                    "登録日": app.get("created_at", "")
                }
            )

        dataframe = pd.DataFrame(table_data)

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )
