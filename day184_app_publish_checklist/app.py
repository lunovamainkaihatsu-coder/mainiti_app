import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day184：アプリ公開チェックリスト"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day184_app_publish_checklist.json")

DEFAULT_CHECKS = [
    "app.py 完成",
    "requirements.txt 作成",
    "GitHub push",
    "README 作成",
    "スクショ作成",
    "アプリ説明文",
    "Streamlit Cloud確認",
    "X投稿",
    "note記事",
    "改善メモ",
]

STATUS = [
    "制作中",
    "公開準備中",
    "公開済み",
    "改善中",
    "保留",
]

CATEGORIES = [
    "健康",
    "お金",
    "生活",
    "読書",
    "AI",
    "開発",
    "目標",
    "その他",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"apps": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "apps" not in data:
        data["apps"] = []

    for app in data["apps"]:
        if "checks" not in app:
            app["checks"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def progress_rate(app):
    checks = app.get("checks", [])

    if not checks:
        return 0

    done = len([x for x in checks if x.get("done", False)])
    total = len(checks)

    return round(done / total * 100, 1)


def progress_text(app):
    checks = app.get("checks", [])

    if not checks:
        return "0 / 0"

    done = len([x for x in checks if x.get("done", False)])
    total = len(checks)

    return f"{done} / {total}"


def make_default_checks():
    return [
        {
            "id": f"check_{i}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "title": title,
            "done": False,
        }
        for i, title in enumerate(DEFAULT_CHECKS)
    ]


def to_df(data):
    rows = []

    for x in data["apps"]:
        rate = progress_rate(x)

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "day": int(x.get("day", 0)),
            "app_name": x["app_name"],
            "folder_name": x.get("folder_name", ""),
            "category": x.get("category", "その他"),
            "status": x.get("status", "制作中"),
            "progress": rate,
            "checks": progress_text(x),
            "github_url": x.get("github_url", ""),
            "app_url": x.get("app_url", ""),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(["day", "created_at"], ascending=[False, False])

    return df


def find_app(data, app_id):
    for x in data["apps"]:
        if x["id"] == app_id:
            return x

    return None


def find_check(app, check_id):
    for x in app.get("checks", []):
        if x["id"] == check_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Day184：アプリ公開チェックリスト")
st.caption("作ったアプリを公開できる状態まで整えるためのチェックリスト管理アプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("アプリを登録")

    day = st.number_input(
        "Day番号",
        min_value=1,
        value=184,
        step=1
    )

    app_name = st.text_input(
        "アプリ名",
        placeholder="例：Day184：アプリ公開チェックリスト"
    )

    folder_name = st.text_input(
        "フォルダ名",
        placeholder="例：day184_app_publish_checklist"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    github_url = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/..."
    )

    app_url = st.text_input(
        "公開URL",
        placeholder="https://xxxxx.streamlit.app"
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：README未作成 / スクショあとで撮る"
    )

    if st.button("🚀 アプリを登録", type="primary"):
        if not app_name.strip():
            st.warning("アプリ名を入れてね。")
        else:
            item = {
                "id": f"app_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "day": int(day),
                "app_name": app_name.strip(),
                "folder_name": folder_name.strip(),
                "category": category,
                "status": status,
                "github_url": github_url.strip(),
                "app_url": app_url.strip(),
                "memo": memo.strip(),
                "checks": make_default_checks(),
            }

            data["apps"].append(item)
            save_data(data)

            st.success("アプリを登録したよ。")
            st.rerun()

with right:
    st.subheader("公開準備状況")

    df = to_df(data)

    if df.empty:
        st.info("まだアプリが登録されていないよ。")
    else:
        total = len(df)
        published = len(df[df["status"] == "公開済み"])
        preparing = len(df[df["status"] == "公開準備中"])
        avg_progress = round(float(df["progress"].mean()), 1)

        c1, c2 = st.columns(2)

        with c1:
            st.metric("登録アプリ数", total)
            st.metric("公開済み", published)

        with c2:
            st.metric("公開準備中", preparing)
            st.metric("平均準備率", f"{avg_progress}%")

        st.progress(min(avg_progress / 100, 1.0))

        st.divider()

        st.subheader("未公開アプリ")

        not_published = df[df["status"] != "公開済み"]

        if not_published.empty:
            st.success("全部公開済み！すごい！")
        else:
            st.dataframe(
                not_published[["day", "app_name", "status", "progress", "checks"]],
                use_container_width=True,
                height=220
            )

st.divider()
st.subheader("アプリ一覧")

df = to_df(data)

if df.empty:
    st.write("まだチェックリストがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="アプリ名・フォルダ名・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        status_filter = st.selectbox(
            "状態で絞る",
            ["すべて"] + STATUS
        )

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["app_name"].fillna("").str.contains(q, case=False, na=False)
            | view["folder_name"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    st.dataframe(
        view[[
            "day",
            "app_name",
            "folder_name",
            "category",
            "status",
            "progress",
            "checks",
            "github_url",
            "app_url",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・チェックリスト")

    if view.empty:
        st.write("条件に合うアプリがないよ。")
    else:
        selected_app_id = st.selectbox(
            "アプリを選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"Day{find_app(data, x).get('day', '')} / {find_app(data, x)['app_name']}"
        )

        app = find_app(data, selected_app_id)

        if app:
            st.markdown(f"## Day{app.get('day', '')}：{app['app_name']}")
            st.write(f"フォルダ：{app.get('folder_name', '')}")
            st.write(f"カテゴリ：{app.get('category', '')}")
            st.write(f"状態：{app.get('status', '')}")

            if app.get("github_url"):
                st.write(f"GitHub：{app['github_url']}")

            if app.get("app_url"):
                st.write(f"公開URL：{app['app_url']}")

            if app.get("memo"):
                st.info(app["memo"])

            rate = progress_rate(app)

            st.progress(rate / 100)
            st.info(f"公開準備率：{rate}%（{progress_text(app)}）")

            st.divider()
            st.subheader("チェック項目")

            for check in app.get("checks", []):
                done = st.checkbox(
                    check["title"],
                    value=bool(check.get("done", False)),
                    key=f"check_{check['id']}"
                )

                check["done"] = done

            if st.button("📝 チェック状態を保存"):
                app["updated_at"] = now_str()

                if progress_rate(app) >= 100:
                    app["status"] = "公開済み"
                elif progress_rate(app) > 0 and app.get("status") == "制作中":
                    app["status"] = "公開準備中"

                save_data(data)

                st.success("チェック状態を保存したよ。")
                st.rerun()

            st.divider()
            st.subheader("チェック項目追加")

            new_check = st.text_input(
                "追加チェック項目",
                placeholder="例：スマホ表示確認"
            )

            if st.button("➕ チェック項目を追加"):
                if not new_check.strip():
                    st.warning("項目名を入れてね。")
                else:
                    app["checks"].append({
                        "id": f"check_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                        "title": new_check.strip(),
                        "done": False,
                    })

                    app["updated_at"] = now_str()
                    save_data(data)

                    st.success("チェック項目を追加したよ。")
                    st.rerun()

            if app.get("checks"):
                delete_check_id = st.selectbox(
                    "削除するチェック項目",
                    [c["id"] for c in app["checks"]],
                    format_func=lambda x: find_check(app, x)["title"]
                )

                if st.button("🗑️ チェック項目を削除", type="secondary"):
                    app["checks"] = [
                        c for c in app["checks"]
                        if c["id"] != delete_check_id
                    ]

                    app["updated_at"] = now_str()
                    save_data(data)

                    st.warning("チェック項目を削除したよ。")
                    st.rerun()

            st.divider()
            st.subheader("アプリ情報更新")

            c1, c2 = st.columns(2)

            with c1:
                new_status = st.selectbox(
                    "状態を更新",
                    STATUS,
                    index=STATUS.index(app.get("status", "制作中")),
                    key=f"status_{app['id']}"
                )

            with c2:
                new_category = st.selectbox(
                    "カテゴリを更新",
                    CATEGORIES,
                    index=CATEGORIES.index(app.get("category", "その他")),
                    key=f"category_{app['id']}"
                )

            new_github = st.text_input(
                "GitHub URL更新",
                value=app.get("github_url", ""),
                key=f"github_{app['id']}"
            )

            new_app_url = st.text_input(
                "公開URL更新",
                value=app.get("app_url", ""),
                key=f"appurl_{app['id']}"
            )

            if st.button("📝 アプリ情報を更新"):
                app["status"] = new_status
                app["category"] = new_category
                app["github_url"] = new_github.strip()
                app["app_url"] = new_app_url.strip()
                app["updated_at"] = now_str()

                save_data(data)

                st.success("アプリ情報を更新したよ。")
                st.rerun()

            if st.button("🗑️ このアプリを削除", type="secondary"):
                data["apps"] = [
                    x for x in data["apps"]
                    if x["id"] != selected_app_id
                ]

                save_data(data)
                st.warning("アプリを削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day184_app_publish_checklist.csv",
        mime="text/csv"
    )
