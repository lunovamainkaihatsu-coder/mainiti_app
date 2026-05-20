import streamlit as st
import json
import os
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day144：忘れ物チェックアプリ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day144_belongings_check.json")

DEFAULT_ITEMS = {
    "日常": ["財布", "スマホ", "鍵", "イヤホン", "ハンカチ", "ティッシュ"],
    "仕事": ["社員証", "名刺", "手帳", "筆記用具", "充電器", "書類"],
    "外出": ["飲み物", "モバイルバッテリー", "折りたたみ傘", "マスク"],
    "子ども連れ": ["おむつ", "おしりふき", "着替え", "飲み物", "おやつ"],
    "運動": ["タオル", "水分", "着替え", "プロテイン", "シューズ"],
}

SCENES = list(DEFAULT_ITEMS.keys()) + ["カスタム"]


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": [], "custom_items": []}, f, ensure_ascii=False, indent=2)


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
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "scene": x["scene"],
            "checked_count": x["checked_count"],
            "total_count": x["total_count"],
            "complete": x["complete"],
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🎒", layout="wide")
st.title("🎒 Day144：忘れ物チェックアプリ")
st.caption("出かける前に、持ち物をチェックして安心するアプリ。")

data = load_data()

if "check_items" not in st.session_state:
    st.session_state["check_items"] = []

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("持ち物リストを作る")

    scene = st.selectbox("シーン", SCENES)

    base_items = []
    if scene != "カスタム":
        base_items = DEFAULT_ITEMS.get(scene, [])

    custom_text = st.text_area(
        "追加したい持ち物（1行に1つ）",
        height=120,
        placeholder="例：薬\n本\nノートPC"
    )

    custom_items = [
        x.strip()
        for x in custom_text.splitlines()
        if x.strip()
    ]

    items = base_items + custom_items

    if st.button("🎒 チェックリスト作成", type="primary"):
        if not items:
            st.warning("持ち物を1つ以上入れてね。")
        else:
            st.session_state["check_items"] = items
            st.success("チェックリストを作ったよ。")

with right:
    st.subheader("出発前チェック")

    items = st.session_state.get("check_items", [])

    if not items:
        st.info("左でチェックリストを作ってね。")
    else:
        checked = []

        for item in items:
            if st.checkbox(item, key=f"check_{item}"):
                checked.append(item)

        total = len(items)
        checked_count = len(checked)
        complete = checked_count == total

        st.metric("チェック済み", f"{checked_count} / {total}")

        progress = checked_count / total if total else 0
        st.progress(progress)

        if complete:
            st.success("忘れ物なし！いってらっしゃい、ご主人！")
        else:
            remain = [x for x in items if x not in checked]
            st.warning("まだ未チェックがあるよ。")
            st.write("未チェック：")
            for r in remain:
                st.write(f"- {r}")

        memo = st.text_area("メモ", placeholder="例：今日は雨だから傘も確認")

        if st.button("✅ チェック結果を保存"):
            item = {
                "id": f"check_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                "created_at": now_str(),
                "date": today_str(),
                "scene": scene,
                "items": items,
                "checked": checked,
                "unchecked": [x for x in items if x not in checked],
                "checked_count": checked_count,
                "total_count": total,
                "complete": complete,
                "memo": memo.strip(),
            }

            data["logs"].append(item)
            save_data(data)
            st.success("チェック結果を保存したよ。")
            st.rerun()

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(
        df[["date", "scene", "checked_count", "total_count", "complete", "memo"]],
        use_container_width=True,
        height=300
    )

    selected = st.selectbox("詳細を見る / 削除する記録", df["id"].tolist())
    chosen = next((x for x in data["logs"] if x["id"] == selected), None)

    if chosen:
        st.markdown(f"### {chosen['date']} / {chosen['scene']}")
        st.write(f"チェック：{chosen['checked_count']} / {chosen['total_count']}")

        st.markdown("**チェック済み**")
        st.write("、".join(chosen.get("checked", [])) or "なし")

        st.markdown("**未チェック**")
        st.write("、".join(chosen.get("unchecked", [])) or "なし")

        if chosen.get("memo"):
            st.write(f"メモ：{chosen['memo']}")

        if st.button("🗑️ この記録を削除", type="secondary"):
            data["logs"] = [x for x in data["logs"] if x["id"] != selected]
            save_data(data)
            st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day144_belongings_check.csv",
        mime="text/csv"
    )
