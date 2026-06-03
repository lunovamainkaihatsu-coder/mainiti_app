import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day159：学びアクション変換"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day159_learning_action.json")

CATEGORIES = [
    "本",
    "動画",
    "名言",
    "AI",
    "仕事",
    "お金",
    "健康",
    "人生",
    "その他",
]

STATUS = [
    "未実行",
    "実行中",
    "達成",
]

ACTION_LEVELS = [
    "超小さく",
    "普通",
    "しっかり",
]

LUNA_COMMENTS = {
    "未実行": "まずは小さく触れるだけでOK。学びは行動にした時に力になるよ。",
    "実行中": "いい感じ、ご主人。途中でもちゃんと前に進んでるよ。",
    "達成": "すごい！学びを行動に変えられたのは本当に強いよ。",
}


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"actions": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return date.today().isoformat()


def to_df(data):
    rows = []

    for x in data["actions"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "category": x["category"],
            "learning": x["learning"],
            "action": x["action"],
            "level": x["level"],
            "reason": x.get("reason", ""),
            "status": x["status"],
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


def find_action(data, action_id):
    for x in data["actions"]:
        if x["id"] == action_id:
            return x
    return None


def status_score(status):
    if status == "達成":
        return 100
    if status == "実行中":
        return 50
    return 0


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Day159：学びアクション変換")
st.caption("本・動画・名言・気づきを、今日できる小さな行動に変えるアプリ。")

data = load_data()

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("学びを行動に変える")

    learning = st.text_area(
        "学び・気づき",
        height=140,
        placeholder="例：成功者は小さな行動を続ける"
    )

    category = st.selectbox(
        "カテゴリ",
        CATEGORIES
    )

    action = st.text_input(
        "今日できる一歩",
        placeholder="例：5分だけ開発する"
    )

    level = st.radio(
        "行動の大きさ",
        ACTION_LEVELS,
        horizontal=True
    )

    reason = st.text_area(
        "なぜやる？",
        height=90,
        placeholder="例：行動に変えないと忘れてしまうから"
    )

    status = st.selectbox(
        "状態",
        STATUS
    )

    memo = st.text_area(
        "メモ",
        height=80,
        placeholder="出典、補足、やってみた感想など"
    )

    favorite = st.checkbox("⭐ 大事な学び")

    if st.button("🎯 保存する", type="primary"):
        if not learning.strip():
            st.warning("学びを入力してね。")
        elif not action.strip():
            st.warning("今日できる一歩を入力してね。")
        else:
            item = {
                "id": f"act_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "learning": learning.strip(),
                "category": category,
                "action": action.strip(),
                "level": level,
                "reason": reason.strip(),
                "status": status,
                "memo": memo.strip(),
                "favorite": favorite,
            }

            data["actions"].append(item)
            save_data(data)

            st.success("学びを行動に変換して保存したよ。")
            st.rerun()

with right:
    st.subheader("アクション状況")

    df = to_df(data)

    total = len(df) if not df.empty else 0
    done = len(df[df["status"] == "達成"]) if not df.empty else 0
    doing = len(df[df["status"] == "実行中"]) if not df.empty else 0
    todo = len(df[df["status"] == "未実行"]) if not df.empty else 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("登録数", total)
        st.metric("達成", done)

    with col2:
        st.metric("実行中", doing)
        st.metric("未実行", todo)

    if total > 0:
        rate = int(done / total * 100)
        st.progress(rate / 100)
        st.info(f"達成率：{rate}%")

    st.divider()

    if not df.empty:
        st.subheader("カテゴリ別")
        cat_count = df["category"].value_counts().reset_index()
        cat_count.columns = ["カテゴリ", "数"]
        st.dataframe(cat_count, use_container_width=True, height=220)
    else:
        st.info("まだアクションがないよ。")

st.divider()
st.subheader("アクション一覧")

df = to_df(data)

if df.empty:
    st.write("まだ記録がないよ。")
else:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        keyword = st.text_input("🔎 検索", placeholder="学び・行動・理由")

    with col_b:
        category_filter = st.selectbox("カテゴリ", ["すべて"] + CATEGORIES)

    with col_c:
        status_filter = st.selectbox("状態", ["すべて"] + STATUS)

    fav_only = st.checkbox("⭐ 大事な学びだけ表示")

    view = df.copy()

    if keyword.strip():
        q = keyword.strip()
        view = view[
            view["learning"].fillna("").str.contains(q, case=False, na=False)
            | view["action"].fillna("").str.contains(q, case=False, na=False)
            | view["reason"].fillna("").str.contains(q, case=False, na=False)
            | view["memo"].fillna("").str.contains(q, case=False, na=False)
        ]

    if category_filter != "すべて":
        view = view[view["category"] == category_filter]

    if status_filter != "すべて":
        view = view[view["status"] == status_filter]

    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(
        view[["date", "category", "learning", "action", "level", "status", "favorite"]],
        use_container_width=True,
        height=320
    )

    st.divider()
    st.subheader("詳細・更新")

    if view.empty:
        st.write("条件に合うアクションがないよ。")
    else:
        options = view["id"].tolist()
        labels = {
            row["id"]: f"{row['category']} / {row['action']} / {row['status']}"
            for _, row in view.iterrows()
        }

        selected_id = st.selectbox(
            "アクションを選ぶ",
            options,
            format_func=lambda x: labels.get(x, x)
        )

        item = find_action(data, selected_id)

        if item:
            st.markdown("### 学び")
            st.info(item["learning"])

            st.markdown("### 今日できる一歩")
            st.success(item["action"])

            st.write(f"カテゴリ：{item['category']}")
            st.write(f"行動の大きさ：{item['level']}")
            st.write(f"状態：{item['status']}")

            if item.get("reason"):
                st.markdown("### なぜやる？")
                st.write(item["reason"])

            if item.get("memo"):
                st.markdown("### メモ")
                st.write(item["memo"])

            st.markdown("### ルナのひとこと")
            st.info(LUNA_COMMENTS.get(item["status"], "小さく進めばOKだよ。"))

            col1, col2, col3 = st.columns(3)

            with col1:
                new_status = st.selectbox(
                    "状態変更",
                    STATUS,
                    index=STATUS.index(item.get("status", "未実行")),
                    key=f"status_{item['id']}"
                )

            with col2:
                new_level = st.selectbox(
                    "行動の大きさ変更",
                    ACTION_LEVELS,
                    index=ACTION_LEVELS.index(item.get("level", "超小さく")),
                    key=f"level_{item['id']}"
                )

            with col3:
                new_fav = st.checkbox(
                    "⭐ 大事",
                    value=bool(item.get("favorite", False)),
                    key=f"fav_{item['id']}"
                )

            new_action = st.text_input(
                "一歩を更新",
                value=item.get("action", ""),
                key=f"action_{item['id']}"
            )

            if st.button("📝 更新する"):
                item["status"] = new_status
                item["level"] = new_level
                item["favorite"] = new_fav
                item["action"] = new_action.strip()
                item["updated_at"] = now_str()

                save_data(data)
                st.success("更新したよ。")
                st.rerun()

            if st.button("🗑️ この記録を削除", type="secondary"):
                data["actions"] = [x for x in data["actions"] if x["id"] != selected_id]
                save_data(data)
                st.warning("削除したよ。")
                st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day159_learning_action.csv",
        mime="text/csv"
    )
