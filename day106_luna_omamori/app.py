import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day106：ルナのひとことお守り"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day106_luna_omamori.json")

OMAMORI_POOL = [
    {
        "category": "安心",
        "word": "今日は全部できなくても大丈夫",
        "luna": "ご主人、今日は“ちゃんと全部”じゃなくていいんだよ。"
    },
    {
        "category": "前進",
        "word": "小さな一歩も、ちゃんと未来を動かす",
        "luna": "ほんの少しでも進めたら、それって本物の前進だよ。"
    },
    {
        "category": "回復",
        "word": "休むことは、止まることじゃない",
        "luna": "今日は守る日でもいいの。守った分だけ、また進めるから。"
    },
    {
        "category": "やさしさ",
        "word": "自分に向ける言葉を、ひとつだけ優しくする",
        "luna": "ご主人には、やさしい言葉を受け取る価値があるよ。"
    },
    {
        "category": "ひらめき",
        "word": "思いつきは、未来から届いた小さな種",
        "luna": "浮かんだこと、今日はちょっと信じてみよっか。"
    },
    {
        "category": "安心",
        "word": "焦らなくても、流れはまた戻ってくる",
        "luna": "いま少し曇ってても、大丈夫。ちゃんと晴れる時はくるよ。"
    },
    {
        "category": "前進",
        "word": "始める前の重さは、始めた後に軽くなる",
        "luna": "最初の一歩って重いけど、そこを越えると変わるんだよね。"
    },
    {
        "category": "回復",
        "word": "今日は“これでよし”を置いて眠っていい",
        "luna": "ご主人、今日は十分やったよ。ちゃんと休んでね。"
    },
]

RARE_OMAMORI = [
    {
        "category": "奇跡",
        "word": "今日は小さな選択が、大きな流れを呼ぶ日",
        "luna": "ご主人、今日はね…ちょっと特別な風が吹いてるかも。"
    },
    {
        "category": "奇跡",
        "word": "あなたの未来は、まだいくらでも優しく変えられる",
        "luna": "まだ遅くないし、まだ終わってないよ。ご主人の未来、ちゃんと動くから。"
    },
]


# ----------------------------
# storage
# ----------------------------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"logs": []}, f, ensure_ascii=False, indent=2)


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
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "category": x["category"],
            "word": x["word"],
            "rarity": x["rarity"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# logic
# ----------------------------
def draw_omamori():
    if random.random() < 0.10:
        item = random.choice(RARE_OMAMORI)
        rarity = "SR"
    else:
        item = random.choice(OMAMORI_POOL)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "category": item["category"],
        "word": item["word"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🧿", layout="wide")
st.title("🧿 Day106：ルナのひとことお守り")
st.caption("その日ずっと持っていたい、小さな言葉を受け取るアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day106_luna_omamori.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest"] = None
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([0.9, 1.1], gap="large")

with left:
    st.subheader("お守りを受け取る")

    if st.button("🧿 お守りを引く", type="primary"):
        result = draw_omamori()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日のお守り")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レアお守り ✨")
        else:
            st.info("通常お守り")

        st.markdown(f"### {latest['word']}")
        st.write(f"カテゴリ：{latest['category']}")

        st.markdown("**ルナの添え言葉**")
        st.info(latest["luna"])

        fav = st.checkbox("⭐ お気に入り", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
                    break
            save_data(data)
            st.toast("お気に入り更新！")
    else:
        st.write("まだ引いてないよ。左のボタンからどうぞ。")

st.divider()
st.subheader("履歴")

df_all = to_df(data)
if df_all.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ お気に入りだけ表示", value=False)
    view = df_all.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        pick_id = st.selectbox("結果を選んでね", options=view["id"].tolist())
        chosen = None
        for row in data["logs"]:
            if row["id"] == pick_id:
                chosen = row
                break

        if chosen:
            st.markdown(f"### {chosen['word']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"カテゴリ：{chosen['category']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**ルナの添え言葉**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
