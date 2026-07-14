import json
import os
from datetime import date, datetime

import pandas as pd
import streamlit as st


APP_TITLE = "Day199：毎日アプリ開発ダッシュボード"
DATA_DIR = "data"
DATA_PATH = os.path.join(
    DATA_DIR,
    "day199_app_development_dashboard.json",
)

CATEGORIES = [
    "生活",
    "健康",
    "お金",
    "AI",
    "開発",
    "読書",
    "目標",
    "ゲーム",
    "占い",
    "仕事",
    "家族",
    "その他",
]

STATUS_OPTIONS = [
    "構想中",
    "制作中",
    "完成",
    "公開済み",
    "改善中",
    "保留",
]

RATING_OPTIONS = [
    1,
    2,
    3,
    4,
    5,
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "apps": [],
                },
                file,
                ensure_ascii=False,
                indent=2,
            )


def load_data():
    ensure_storage()

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        data = {
            "apps": [],
        }

    data.setdefault("apps", [])

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_text():
    return date.today().isoformat()


def current_month_text():
    return date.today().strftime("%Y-%m")


def find_app(data, app_id):
    for app in data["apps"]:
        if app["id"] == app_id:
            return app

    return None


def bool_text(value):
    return "済" if value else "未"


def normalize_url(value):
    value = value.strip()

    if not value:
        return ""

    if value.startswith("http://") or value.startswith("https://"):
        return value

    return f"https://{value}"


def completion_label(value):
    value = int(value)

    if value >= 100:
        return "🎉 完成"

    if value >= 80:
        return "🟢 ほぼ完成"

    if value >= 50:
        return "🟡 制作中"

    if value > 0:
        return "🟠 着手"

    return "⚪ 未着手"


def to_df(data):
    rows = []

    for app in data["apps"]:
        production_date = app.get(
            "production_date",
            today_text(),
        )

        rows.append(
            {
                "id": app["id"],
                "created_at": app["created_at"],
                "day": int(app.get("day", 0)),
                "app_name": app["app_name"],
                "folder_name": app.get("folder_name", ""),
                "category": app.get("category", "その他"),
                "production_date": production_date,
                "month": production_date[:7],
                "completion": int(app.get("completion", 0)),
                "completion_label": completion_label(
                    app.get("completion", 0)
                ),
                "status": app.get("status", "構想中"),
                "github_done": bool(
                    app.get("github_done", False)
                ),
                "streamlit_done": bool(
                    app.get("streamlit_done", False)
                ),
                "note_done": bool(
                    app.get("note_done", False)
                ),
                "x_done": bool(
                    app.get("x_done", False)
                ),
                "github_url": app.get("github_url", ""),
                "streamlit_url": app.get(
                    "streamlit_url",
                    "",
                ),
                "note_url": app.get("note_url", ""),
                "rating": int(app.get("rating", 3)),
                "favorite": bool(
                    app.get("favorite", False)
                ),
                "memo": app.get("memo", ""),
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(
            [
                "day",
                "created_at",
            ],
            ascending=[
                False,
                False,
            ],
        )

    return df


def percentage(part, total):
    if total <= 0:
        return 0.0

    return round(part / total * 100, 1)


def add_sample_apps(data):
    if data["apps"]:
        return False

    samples = [
        {
            "day": 197,
            "app_name": "定期メンテナンス管理アプリ",
            "folder_name": "day197_maintenance_manager",
            "category": "生活",
            "completion": 100,
            "status": "完成",
            "github_done": True,
            "streamlit_done": False,
            "note_done": True,
            "x_done": True,
            "rating": 4,
        },
        {
            "day": 198,
            "app_name": "習慣スタンプカード",
            "folder_name": "day198_habit_stamp_card",
            "category": "健康",
            "completion": 100,
            "status": "完成",
            "github_done": True,
            "streamlit_done": False,
            "note_done": True,
            "x_done": True,
            "rating": 5,
        },
        {
            "day": 199,
            "app_name": "毎日アプリ開発ダッシュボード",
            "folder_name": "day199_app_development_dashboard",
            "category": "開発",
            "completion": 80,
            "status": "制作中",
            "github_done": False,
            "streamlit_done": False,
            "note_done": False,
            "x_done": False,
            "rating": 5,
        },
    ]

    for sample in samples:
        data["apps"].append(
            {
                "id": (
                    "app_"
                    + datetime.now().strftime(
                        "%Y%m%d%H%M%S%f"
                    )
                    + f"_{sample['day']}"
                ),
                "created_at": now_text(),
                "day": sample["day"],
                "app_name": sample["app_name"],
                "folder_name": sample["folder_name"],
                "category": sample["category"],
                "production_date": today_text(),
                "completion": sample["completion"],
                "status": sample["status"],
                "github_done": sample["github_done"],
                "streamlit_done": sample["streamlit_done"],
                "note_done": sample["note_done"],
                "x_done": sample["x_done"],
                "github_url": "",
                "streamlit_url": "",
                "note_url": "",
                "rating": sample["rating"],
                "favorite": False,
                "memo": "",
            }
        )

    return True


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Day199：毎日アプリ開発ダッシュボード")
st.caption(
    "これまで作ったアプリの完成度・公開状況・発信状況をまとめて管理するアプリ。"
)

data = load_data()

with st.sidebar:
    st.subheader("初期データ")

    if st.button("サンプルを追加"):
        added = add_sample_apps(data)

        if added:
            save_data(data)
            st.success("サンプルを追加したよ。")
            st.rerun()
        else:
            st.info("すでにアプリが登録されているよ。")

tab1, tab2, tab3 = st.tabs(
    [
        "🚀 ダッシュボード",
        "➕ アプリ登録・管理",
        "📊 集計・分析",
    ]
)

with tab1:
    df = to_df(data)

    st.subheader("全体状況")

    if df.empty:
        st.info("まだアプリが登録されていないよ。")
    else:
        total = len(df)
        completed = len(
            df[
                df["status"].isin(
                    [
                        "完成",
                        "公開済み",
                    ]
                )
            ]
        )
        public_count = len(
            df[
                df["status"] == "公開済み"
            ]
        )
        github_count = int(
            df["github_done"].sum()
        )
        streamlit_count = int(
            df["streamlit_done"].sum()
        )
        note_count = int(
            df["note_done"].sum()
        )
        x_count = int(
            df["x_done"].sum()
        )

        this_month = current_month_text()
        month_count = len(
            df[
                df["month"] == this_month
            ]
        )

        average_completion = round(
            float(df["completion"].mean()),
            1,
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "登録アプリ",
            total,
        )

        c2.metric(
            "完成・公開済み",
            completed,
        )

        c3.metric(
            "今月制作",
            month_count,
        )

        c4.metric(
            "平均完成度",
            f"{average_completion}%",
        )

        st.divider()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "GitHub",
            f"{github_count}/{total}",
        )

        c2.metric(
            "Streamlit",
            f"{streamlit_count}/{total}",
        )

        c3.metric(
            "note",
            f"{note_count}/{total}",
        )

        c4.metric(
            "X",
            f"{x_count}/{total}",
        )

        st.markdown("### 公開・発信率")

        github_rate = percentage(
            github_count,
            total,
        )

        streamlit_rate = percentage(
            streamlit_count,
            total,
        )

        note_rate = percentage(
            note_count,
            total,
        )

        x_rate = percentage(
            x_count,
            total,
        )

        st.write(
            f"GitHub公開率：{github_rate}%"
        )
        st.progress(
            min(github_rate / 100, 1)
        )

        st.write(
            f"Streamlit公開率：{streamlit_rate}%"
        )
        st.progress(
            min(streamlit_rate / 100, 1)
        )

        st.write(
            f"note投稿率：{note_rate}%"
        )
        st.progress(
            min(note_rate / 100, 1)
        )

        st.write(
            f"X投稿率：{x_rate}%"
        )
        st.progress(
            min(x_rate / 100, 1)
        )

        st.divider()
        st.subheader("最近のアプリ")

        st.dataframe(
            df[
                [
                    "day",
                    "app_name",
                    "category",
                    "completion",
                    "completion_label",
                    "status",
                    "github_done",
                    "streamlit_done",
                    "note_done",
                    "x_done",
                    "rating",
                ]
            ].head(12),
            use_container_width=True,
            height=350,
        )

        st.divider()
        st.subheader("未完了・未公開")

        incomplete = df[
            (df["completion"] < 100)
            | (
                df["github_done"] == False
            )
            | (
                df["note_done"] == False
            )
            | (
                df["x_done"] == False
            )
        ]

        if incomplete.empty:
            st.success(
                "登録アプリはすべて完成・発信済み！"
            )
        else:
            st.dataframe(
                incomplete[
                    [
                        "day",
                        "app_name",
                        "completion",
                        "status",
                        "github_done",
                        "streamlit_done",
                        "note_done",
                        "x_done",
                        "memo",
                    ]
                ],
                use_container_width=True,
                height=300,
            )

with tab2:
    left, right = st.columns(
        [1, 1],
        gap="large",
    )

    with left:
        st.subheader("アプリを登録")

        day_number = st.number_input(
            "Day番号",
            min_value=1,
            value=199,
            step=1,
        )

        app_name = st.text_input(
            "アプリ名",
            placeholder=(
                "例：毎日アプリ開発ダッシュボード"
            ),
        )

        folder_name = st.text_input(
            "フォルダ名",
            placeholder=(
                "例：day199_app_development_dashboard"
            ),
        )

        category = st.selectbox(
            "カテゴリ",
            CATEGORIES,
        )

        production_date = st.date_input(
            "制作日",
            value=date.today(),
        )

        completion = st.slider(
            "完成度",
            min_value=0,
            max_value=100,
            value=100,
            step=5,
        )

        st.info(
            completion_label(completion)
        )

        status = st.selectbox(
            "状態",
            STATUS_OPTIONS,
            index=2,
        )

        c1, c2 = st.columns(2)

        with c1:
            github_done = st.checkbox(
                "GitHub公開済み"
            )

            note_done = st.checkbox(
                "note投稿済み"
            )

        with c2:
            streamlit_done = st.checkbox(
                "Streamlit公開済み"
            )

            x_done = st.checkbox(
                "X投稿済み"
            )

        github_url = st.text_input(
            "GitHub URL",
            placeholder="https://github.com/...",
        )

        streamlit_url = st.text_input(
            "Streamlit URL",
            placeholder="https://xxxxx.streamlit.app",
        )

        note_url = st.text_input(
            "note URL",
            placeholder="https://note.com/...",
        )

        rating = st.select_slider(
            "お気に入り度",
            options=RATING_OPTIONS,
            value=4,
            format_func=lambda value: (
                "★" * value
                + "☆" * (5 - value)
            ),
        )

        favorite = st.checkbox(
            "⭐ 特にお気に入り"
        )

        memo = st.text_area(
            "メモ",
            height=100,
            placeholder=(
                "例：スマホ表示を改善したい"
                " / README未作成"
            ),
        )

        if st.button(
            "🚀 アプリを登録",
            type="primary",
        ):
            if not app_name.strip():
                st.warning(
                    "アプリ名を入れてね。"
                )
            else:
                app = {
                    "id": (
                        "app_"
                        + datetime.now().strftime(
                            "%Y%m%d%H%M%S%f"
                        )
                    ),
                    "created_at": now_text(),
                    "day": int(day_number),
                    "app_name": app_name.strip(),
                    "folder_name": folder_name.strip(),
                    "category": category,
                    "production_date": (
                        production_date.isoformat()
                    ),
                    "completion": int(completion),
                    "status": status,
                    "github_done": github_done,
                    "streamlit_done": (
                        streamlit_done
                    ),
                    "note_done": note_done,
                    "x_done": x_done,
                    "github_url": normalize_url(
                        github_url
                    ),
                    "streamlit_url": normalize_url(
                        streamlit_url
                    ),
                    "note_url": normalize_url(
                        note_url
                    ),
                    "rating": int(rating),
                    "favorite": favorite,
                    "memo": memo.strip(),
                }

                data["apps"].append(app)
                save_data(data)

                st.success(
                    "アプリを登録したよ。"
                )
                st.rerun()

    with right:
        st.subheader("登録アプリ一覧")

        df = to_df(data)

        if df.empty:
            st.info(
                "まだアプリが登録されていないよ。"
            )
        else:
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                keyword = st.text_input(
                    "検索",
                    placeholder=(
                        "アプリ名・フォルダ・メモ"
                    ),
                )

            with col_b:
                category_filter = st.selectbox(
                    "カテゴリで絞る",
                    ["すべて"] + CATEGORIES,
                )

            with col_c:
                status_filter = st.selectbox(
                    "状態で絞る",
                    ["すべて"] + STATUS_OPTIONS,
                )

            favorite_only = st.checkbox(
                "⭐ お気に入りだけ表示"
            )

            view = df.copy()

            if keyword.strip():
                query = keyword.strip()

                view = view[
                    view["app_name"]
                    .fillna("")
                    .str.contains(
                        query,
                        case=False,
                        na=False,
                    )
                    | view["folder_name"]
                    .fillna("")
                    .str.contains(
                        query,
                        case=False,
                        na=False,
                    )
                    | view["memo"]
                    .fillna("")
                    .str.contains(
                        query,
                        case=False,
                        na=False,
                    )
                ]

            if category_filter != "すべて":
                view = view[
                    view["category"]
                    == category_filter
                ]

            if status_filter != "すべて":
                view = view[
                    view["status"]
                    == status_filter
                ]

            if favorite_only:
                view = view[
                    view["favorite"] == True
                ]

            st.dataframe(
                view[
                    [
                        "day",
                        "app_name",
                        "folder_name",
                        "category",
                        "production_date",
                        "completion",
                        "status",
                        "github_done",
                        "streamlit_done",
                        "note_done",
                        "x_done",
                        "rating",
                        "favorite",
                        "memo",
                    ]
                ],
                use_container_width=True,
                height=360,
            )

            st.divider()
            st.subheader("詳細・更新")

            if view.empty:
                st.write(
                    "条件に合うアプリがないよ。"
                )
            else:
                selected_id = st.selectbox(
                    "アプリを選ぶ",
                    view["id"].tolist(),
                    format_func=lambda app_id: (
                        f"Day"
                        f"{find_app(data, app_id).get('day', '')}"
                        f" / "
                        f"{find_app(data, app_id)['app_name']}"
                    ),
                )

                selected = find_app(
                    data,
                    selected_id,
                )

                if selected:
                    st.markdown(
                        f"## Day"
                        f"{selected.get('day', '')}："
                        f"{selected['app_name']}"
                    )

                    st.write(
                        f"フォルダ："
                        f"{selected.get('folder_name', '')}"
                    )

                    st.write(
                        f"カテゴリ："
                        f"{selected.get('category', '')}"
                    )

                    st.write(
                        f"制作日："
                        f"{selected.get('production_date', '')}"
                    )

                    selected_completion = int(
                        selected.get(
                            "completion",
                            0,
                        )
                    )

                    st.progress(
                        min(
                            selected_completion / 100,
                            1,
                        )
                    )

                    st.info(
                        f"完成度："
                        f"{selected_completion}% "
                        f"／ "
                        f"{completion_label(selected_completion)}"
                    )

                    if selected.get("github_url"):
                        st.markdown(
                            f"[GitHubを開く]"
                            f"({selected['github_url']})"
                        )

                    if selected.get("streamlit_url"):
                        st.markdown(
                            f"[アプリを開く]"
                            f"({selected['streamlit_url']})"
                        )

                    if selected.get("note_url"):
                        st.markdown(
                            f"[noteを開く]"
                            f"({selected['note_url']})"
                        )

                    if selected.get("memo"):
                        st.info(
                            selected["memo"]
                        )

                    new_completion = st.slider(
                        "完成度を更新",
                        min_value=0,
                        max_value=100,
                        value=selected_completion,
                        step=5,
                        key=(
                            f"completion_"
                            f"{selected_id}"
                        ),
                    )

                    new_status = st.selectbox(
                        "状態を更新",
                        STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(
                            selected.get(
                                "status",
                                "構想中",
                            )
                        ),
                        key=(
                            f"status_"
                            f"{selected_id}"
                        ),
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        new_github_done = st.checkbox(
                            "GitHub公開済み",
                            value=bool(
                                selected.get(
                                    "github_done",
                                    False,
                                )
                            ),
                            key=(
                                f"github_done_"
                                f"{selected_id}"
                            ),
                        )

                        new_note_done = st.checkbox(
                            "note投稿済み",
                            value=bool(
                                selected.get(
                                    "note_done",
                                    False,
                                )
                            ),
                            key=(
                                f"note_done_"
                                f"{selected_id}"
                            ),
                        )

                    with c2:
                        new_streamlit_done = (
                            st.checkbox(
                                "Streamlit公開済み",
                                value=bool(
                                    selected.get(
                                        "streamlit_done",
                                        False,
                                    )
                                ),
                                key=(
                                    f"streamlit_done_"
                                    f"{selected_id}"
                                ),
                            )
                        )

                        new_x_done = st.checkbox(
                            "X投稿済み",
                            value=bool(
                                selected.get(
                                    "x_done",
                                    False,
                                )
                            ),
                            key=(
                                f"x_done_"
                                f"{selected_id}"
                            ),
                        )

                    new_rating = st.select_slider(
                        "お気に入り度更新",
                        options=RATING_OPTIONS,
                        value=int(
                            selected.get(
                                "rating",
                                3,
                            )
                        ),
                        key=(
                            f"rating_"
                            f"{selected_id}"
                        ),
                        format_func=lambda value: (
                            "★" * value
                            + "☆" * (5 - value)
                        ),
                    )

                    new_favorite = st.checkbox(
                        "⭐ 特にお気に入り",
                        value=bool(
                            selected.get(
                                "favorite",
                                False,
                            )
                        ),
                        key=(
                            f"favorite_"
                            f"{selected_id}"
                        ),
                    )

                    new_memo = st.text_area(
                        "メモ更新",
                        value=selected.get(
                            "memo",
                            "",
                        ),
                        key=(
                            f"memo_"
                            f"{selected_id}"
                        ),
                    )

                    if st.button(
                        "📝 アプリ情報を更新"
                    ):
                        selected["completion"] = int(
                            new_completion
                        )
                        selected["status"] = (
                            new_status
                        )
                        selected["github_done"] = (
                            new_github_done
                        )
                        selected["streamlit_done"] = (
                            new_streamlit_done
                        )
                        selected["note_done"] = (
                            new_note_done
                        )
                        selected["x_done"] = (
                            new_x_done
                        )
                        selected["rating"] = int(
                            new_rating
                        )
                        selected["favorite"] = (
                            new_favorite
                        )
                        selected["memo"] = (
                            new_memo.strip()
                        )
                        selected["updated_at"] = (
                            now_text()
                        )

                        if (
                            int(new_completion) >= 100
                            and new_status
                            == "制作中"
                        ):
                            selected["status"] = "完成"

                        save_data(data)

                        st.success(
                            "アプリ情報を更新したよ。"
                        )
                        st.rerun()

                    if st.button(
                        "🗑️ このアプリを削除",
                        type="secondary",
                    ):
                        data["apps"] = [
                            app
                            for app in data["apps"]
                            if app["id"]
                            != selected_id
                        ]

                        save_data(data)

                        st.warning(
                            "アプリを削除したよ。"
                        )
                        st.rerun()

            csv = df.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "⬇️ アプリ一覧CSV",
                data=csv,
                file_name=(
                    "day199_app_dashboard.csv"
                ),
                mime="text/csv",
            )

with tab3:
    st.subheader("集計・分析")

    df = to_df(data)

    if df.empty:
        st.info(
            "分析できるアプリデータがまだないよ。"
        )
    else:
        st.markdown("### カテゴリ別")

        category_summary = (
            df.groupby("category")
            .agg(
                アプリ数=("id", "count"),
                平均完成度=("completion", "mean"),
                GitHub公開=("github_done", "sum"),
                Streamlit公開=(
                    "streamlit_done",
                    "sum",
                ),
                note投稿=("note_done", "sum"),
                X投稿=("x_done", "sum"),
            )
            .reset_index()
        )

        category_summary[
            "平均完成度"
        ] = category_summary[
            "平均完成度"
        ].round(1)

        st.dataframe(
            category_summary,
            use_container_width=True,
            height=300,
        )

        st.markdown("### 月別制作数")

        monthly_summary = (
            df.groupby("month")
            .agg(
                制作数=("id", "count"),
                完成数=(
                    "completion",
                    lambda values: (
                        values >= 100
                    ).sum(),
                ),
                平均完成度=(
                    "completion",
                    "mean",
                ),
            )
            .reset_index()
            .sort_values(
                "month",
                ascending=False,
            )
        )

        monthly_summary[
            "平均完成度"
        ] = monthly_summary[
            "平均完成度"
        ].round(1)

        st.dataframe(
            monthly_summary,
            use_container_width=True,
            height=280,
        )

        st.markdown("### お気に入りランキング")

        ranking = df.sort_values(
            [
                "rating",
                "completion",
                "day",
            ],
            ascending=[
                False,
                False,
                False,
            ],
        )

        st.dataframe(
            ranking[
                [
                    "day",
                    "app_name",
                    "category",
                    "rating",
                    "completion",
                    "status",
                    "favorite",
                ]
            ].head(15),
            use_container_width=True,
            height=320,
        )

        st.markdown("### 進捗グラフ")

        chart_df = (
            df.sort_values(
                "day",
                ascending=True,
            )
            .set_index("day")
        )

        st.line_chart(
            chart_df[
                [
                    "completion",
                ]
            ]
        )
