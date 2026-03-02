import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

APP_TITLE = "Day85：Idea Vault（アイデア金庫）"

DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "idea_vault.json")


# ---------- storage ----------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"ideas": []}, f, ensure_ascii=False, indent=2)


def load_data():
    ensure_storage()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    ensure_storage()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------- logic ----------
def add_idea(data, text, tags, priority):
    idea = {
        "text": text,
        "tags": tags,
        "priority": priority,
        "created": now(),
        "done": False
    }
    data["ideas"].append(idea)
    save_data(data)


def to_df(data):
    if not data["ideas"]:
        return pd.DataFrame()
    return pd.DataFrame(data["ideas"]).sort_values(
        ["done", "priority"],
        ascending=[True, False]
    )


def next_candidates(df):
    if df.empty:
        return df
    return df[(df["done"] == False)].head(5)


# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="💡", layout="wide")
st.title("💡 Idea Vault（アイデア金庫）")
st.caption("ひらめきを資産に変える場所")

data = load_data()

col1, col2 = st.columns([1,1])

# ---------- add ----------
with col1:
    st.subheader("新しいアイデア")

    text = st.text_input("アイデア")

    tags = st.multiselect(
        "タグ",
        ["アプリ", "Note", "ルナ", "収益", "世界観", "ゲーム", "ツール"]
    )

    priority = st.slider("重要度", 1, 5, 3)

    if st.button("保存"):
        if text:
            add_idea(data, text, tags, priority)
            st.success("保存した！")
            st.rerun()


# ---------- list ----------
df = to_df(data)

with col2:
    st.subheader("次に作る候補（おすすめ）")

    candidates = next_candidates(df)

    if candidates.empty:
        st.info("まだアイデアがないよ")
    else:
        for _, row in candidates.iterrows():
            st.write(f"★{row['priority']} | {row['text']}")


# ---------- all ----------
st.subheader("すべてのアイデア")

if df.empty:
    st.info("まだ空です")
else:

    search = st.text_input("検索")

    if search:
        df = df[df["text"].str.contains(search)]

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "CSVエクスポート",
        csv,
        "idea_vault.csv",
        "text/csv"
    )
