import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

APP_TITLE = "Day186：パスワード管理帳"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day186_password_manager.json")

CATEGORIES = [
    "SNS",
    "開発",
    "AI",
    "ショッピング",
    "銀行",
    "メール",
    "サブスク",
    "仕事",
    "その他",
]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"accounts": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "accounts" not in data:
        data["accounts"] = []

    return data


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def mask_password(password):
    if not password:
        return ""

    return "●" * min(len(password), 12)


def strength_label(password):
    score = 0

    if len(password) >= 8:
        score += 1

    if len(password) >= 12:
        score += 1

    if any(c.isupper() for c in password):
        score += 1

    if any(c.islower() for c in password):
        score += 1

    if any(c.isdigit() for c in password):
        score += 1

    if any(not c.isalnum() for c in password):
        score += 1

    if score >= 5:
        return "強い"

    if score >= 3:
        return "普通"

    return "弱い"


def to_df(data, show_password=False):
    rows = []

    for x in data["accounts"]:
        password = x.get("password", "")

        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "service": x["service"],
            "category": x["category"],
            "login_id": x.get("login_id", ""),
            "password": password if show_password else mask_password(password),
            "strength": strength_label(password),
            "url": x.get("url", ""),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(["favorite", "created_at"], ascending=[False, False])

    return df


def find_account(data, account_id):
    for x in data["accounts"]:
        if x["id"] == account_id:
            return x

    return None


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Day186：パスワード管理帳")
st.caption("サービス名・ID・パスワード・URLをローカルで管理するシンプルなパスワード帳。")

st.warning("注意：この版は暗号化していません。本当に重要なパスワードの保存は、暗号化版を作ってからがおすすめです。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("アカウント登録")

    service = st.text_input(
        "サービス名",
        placeholder="例：GitHub / ChatGPT / Amazon"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    login_id = st.text_input(
        "ログインID・メールアドレス",
        placeholder="例：example@email.com"
    )

    password = st.text_input(
        "パスワード",
        type="password"
    )

    url = st.text_input(
        "URL",
        placeholder="https://..."
    )

    memo = st.text_area(
        "メモ",
        height=90,
        placeholder="例：2段階認証あり / 仕事用 / サブスク"
    )

    favorite = st.checkbox("⭐ よく使う")

    if password:
        st.info(f"パスワード強度：{strength_label(password)}")

    if st.button("🔐 保存する", type="primary"):
        if not service.strip():
            st.warning("サービス名を入れてね。")
        elif not login_id.strip():
            st.warning("ログインIDを入れてね。")
        elif not password.strip():
            st.warning("パスワードを入れてね。")
        else:
            item = {
                "id": f"account_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "service": service.strip(),
                "category": category,
                "login_id": login_id.strip(),
                "password": password.strip(),
                "url": url.strip(),
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["accounts"].append(item)
            save_data(data)

            st.success("アカウント情報を保存したよ。")
            st.rerun()

with right:
    st.subheader("登録状況")

    df = to_df(data)

    if df.empty:
        st.info("まだ登録がないよ。")
    else:
        total = len(df)
        fav_count = len(df[df["favorite"] == True])
        weak_count = len(df[df["strength"] == "弱い"])

        c1, c2 = st.columns(2)

        with c1:
            st.metric("登録数", total)
            st.metric("お気に入り", fav_count)

        with c2:
            st.metric("弱いパスワード", weak_count)
            st.metric("カテゴリ数", df["category"].nunique())

        st.divider()

        st.subheader("カテゴリ別")

        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "件数"]

        st.dataframe(
            cat_count,
            use_container_width=True,
            height=220
        )

st.divider()
st.subheader("アカウント一覧")

if "show_passwords" not in st.session_state:
    st.session_state["show_passwords"] = False

show_passwords = st.checkbox(
    "👁 パスワードを表示する",
    value=st.session_state["show_passwords"]
)

st.session_state["show_passwords"] = show_passwords

df = to_df(data, show_password=show_passwords)

if df.empty:
    st.write("まだ一覧に表示するデータがないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input(
            "検索",
            placeholder="サービス名・ID・URL・メモ"
        )

    with col_b:
        category_filter = st.selectbox(
            "カテゴリで絞る",
            ["すべて"] + CATEGORIES
        )

    with col_c:
        strength_filter = st.selectbox(
            "強度で絞る",
            ["すべて", "弱い", "普通", "強い"]
        )

    fav_only = st.checkbox("⭐ よく使うものだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["service"].fillna("").str.contains(q, case=False, na=False)
            | view["login_id"].fillna("").str.contains(q, case=False, na=False)
            | view["url"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if strength_filter != "すべて":
        view = view[view["strength"] == strength_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[[
            "service",
            "category",
            "login_id",
            "password",
            "strength",
            "url",
            "favorite",
            "memo",
        ]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合うアカウントがないよ。")
    else:
        selected_id = st.selectbox(
            "アカウントを選ぶ",
            view["id"].tolist(),
            format_func=lambda x: f"{find_account(data, x)['service']} / {find_account(data, x).get('login_id', '')}"
        )

        account = find_account(data, selected_id)

        if account:
            st.markdown(f"## {account['service']}")
            st.write(f"カテゴリ：{account['category']}")
            st.write(f"ログインID：{account.get('login_id', '')}")
            st.write(f"URL：{account.get('url', '')}")
            st.write(f"強度：{strength_label(account.get('password', ''))}")

            st.markdown("### パスワード")
            if show_passwords:
                st.code(account.get("password", ""), language="text")
            else:
                st.code(mask_password(account.get("password", "")), language="text")

            if account.get("memo"):
                st.info(account["memo"])

            c1, c2 = st.columns(2)

            with c1:
                new_category = st.selectbox(
                    "カテゴリ更新",
                    CATEGORIES,
                    index=CATEGORIES.index(account.get("category", "その他")),
                    key=f"category_{account['id']}"
                )

            with c2:
                new_favorite = st.checkbox(
                    "⭐ よく使う",
                    value=bool(account.get("favorite", False)),
                    key=f"fav_{account['id']}"
                )

            new_password = st.text_input(
                "パスワード更新",
                value=account.get("password", ""),
                type="password",
                key=f"password_{account['id']}"
            )

            if st.button("📝 更新する"):
                account["category"] = new_category
                account["favorite"] = new_favorite
                account["password"] = new_password.strip()
                account["updated_at"] = now_str()

                save_data(data)

                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ このアカウントを削除", type="secondary"):
                data["accounts"] = [
                    x for x in data["accounts"]
                    if x["id"] != selected_id
                ]

                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    safe_df = to_df(data, show_password=False)
    csv = safe_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ CSVダウンロード（パスワード非表示版）",
        data=csv,
        file_name="day186_password_manager_safe.csv",
        mime="text/csv"
    )
