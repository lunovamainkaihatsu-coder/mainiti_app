import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day119：名言・メモ保管庫"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day119_quote_memo.json")


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"items": []}, f, ensure_ascii=False, indent=2)


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


def to_df(data):
    rows = []
    for x in data["items"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "content": x["content"],
            "source": x.get("source", ""),
            "tags": ", ".join(x.get("tags", [])),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def find_item(data, item_id):
    for x in data["items"]:
        if x["id"] == item_id:
            return x
    return None


st.set_page_config(page_title=APP_TITLE, page_icon="📖", layout="wide")
st.title("📖 Day119：名言・メモ保管庫")
st.caption("あとで見返したい言葉・気づきを貯めるアプリ。")

data = load_data()

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSV", data=csv)

    st.divider()
    keyword = st.text_input("🔎 検索")
    tag_filter = st.text_input("🏷️ タグで絞る（1つ）")
    fav_only = st.checkbox("⭐ お気に入りだけ")

left, right = st.columns([1,1])

# 入力
with left:
    st.subheader("メモを追加")

    with st.form("memo_form"):
        content = st.text_area("内容（名言・気づき）", height=120)
        source = st.text_input("出典（本・人・自分など）")
        tags = st.text_input("タグ（カンマ区切り）")
        note = st.text_area("補足メモ", height=80)
        favorite = st.checkbox("⭐ お気に入り")

        submitted = st.form_submit_button("保存", type="primary")

        if submitted:
            if not content.strip():
                st.warning("内容は必須だよ")
            else:
                item = {
                    "id": f"memo_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "created_at": now_str(),
                    "content": content.strip(),
                    "source": source.strip(),
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "note": note.strip(),
                    "favorite": favorite,
                }
                data["items"].append(item)
                save_data(data)
                st.success("保存したよ")
                st.rerun()

# 表示
with right:
    st.subheader("メモ一覧")

    df = to_df(data)

    if not df.empty:
        view = df.copy()

        if keyword:
            view = view[view["content"].str.contains(keyword, na=False)]

        if tag_filter:
            view = view[view["tags"].str.contains(tag_filter, na=False)]

        if fav_only:
            view = view[view["favorite"] == True]

        st.dataframe(view, use_container_width=True)

        st.divider()
        st.subheader("詳細")

        options = view["id"].tolist()
        selected = st.selectbox("選択", options)

        item = find_item(data, selected)

        if item:
            st.markdown(f"## {item['content']}")
            st.write(f"出典：{item.get('source','')}")
            st.write(f"タグ：{', '.join(item.get('tags', []))}")

            st.markdown("### 補足メモ")
            st.write(item.get("note",""))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("⭐ 切替"):
                    item["favorite"] = not item["favorite"]
                    save_data(data)
                    st.rerun()

            with col2:
                if st.button("🗑️ 削除"):
                    data["items"] = [x for x in data["items"] if x["id"] != selected]
                    save_data(data)
                    st.rerun()
    else:
        st.info("まだメモがないよ")
