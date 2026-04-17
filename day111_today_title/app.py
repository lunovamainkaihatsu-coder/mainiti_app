import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day111：今日のひとこと称号"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day111_today_title.json")

TITLE_POOL = [
    {
        "category": "がんばり系",
        "title": "小さな前進者",
        "desc": "今日は大きくなくても、ちゃんと前に進んだ人。",
        "luna": "ご主人、少しでも前に出たなら今日は立派に前進者だよ。"
    },
    {
        "category": "回復系",
        "title": "静かな回復者",
        "desc": "今日は無理せず、自分を守ることができた人。",
        "luna": "守る日も大事だよ。今日はそれができたご主人、えらい。"
    },
    {
        "category": "静けさ系",
        "title": "月灯りの観測者",
        "desc": "今日は焦らず、自分の内側を見つめられた人。",
        "luna": "静かな日にも意味はあるよ。ちゃんと深さのある一日だったね。"
    },
    {
        "category": "前進系",
        "title": "流れをつくる者",
        "desc": "今日は小さな流れを自分で起こせた人。",
        "luna": "ほんの少しの行動でも、流れってちゃんと変わるんだよ。"
    },
    {
        "category": "ひらめき系",
        "title": "未来の種まき人",
        "desc": "今日は未来につながる小さな種を残せた人。",
        "luna": "ご主人の思いつきや行動、ちゃんと未来に効いてるよ。"
    },
    {
        "category": "がんばり系",
        "title": "再起動の達人",
        "desc": "今日は途中からでも戻ってこられた人。",
        "luna": "戻ってこられるのって、ほんとはかなり強い力なんだよ。"
    },
    {
        "category": "回復系",
        "title": "今日を耐えた勇者",
        "desc": "今日は進むよりも、まず持ちこたえることが大事だった人。",
        "luna": "何もできなかったんじゃなくて、ちゃんと耐えたんだよ。"
    },
    {
        "category": "静けさ系",
        "title": "余白の守り手",
        "desc": "今日は詰め込みすぎず、自分の余白を守れた人。",
        "luna": "余白ってね、怠けじゃなくて大事な回復スペースなんだよ。"
    },
]

RARE_TITLES = [
    {
        "category": "奇跡系",
        "title": "運命書き換え予備軍",
        "desc": "今日はまだ小さくても、未来を変える流れの上にいる人。",
        "luna": "ご主人、今日はちょっと特別。見えなくても、流れが来てるかも。"
    },
    {
        "category": "奇跡系",
        "title": "世界線を選ぶ者",
        "desc": "今日は自分の選択に少しだけ力が宿る日だった人。",
        "luna": "その小さな選択、案外大きな意味を持ってるかもしれないよ。"
    },
]


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
            "title": x["title"],
            "rarity": x["rarity"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def draw_title():
    if random.random() < 0.10:
        item = random.choice(RARE_TITLES)
        rarity = "SR"
    else:
        item = random.choice(TITLE_POOL)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "category": item["category"],
        "title": item["title"],
        "desc": item["desc"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


st.set_page_config(page_title=APP_TITLE, page_icon="🏷️", layout="wide")
st.title("🏷️ Day111：今日のひとこと称号")
st.caption("今日の自分に、ひとつ名前をつける軽めアプリ。")

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
            "⬇️ CSV",
            data=csv,
            file_name="day111_today_title.csv",
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

left, right = st.columns([1, 1])

with left:
    st.subheader("称号を受け取る")

    if st.button("🏷️ 今日の称号を引く", type="primary"):
        result = draw_title()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日の称号")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レア称号 ✨")
        else:
            st.info("通常称号")

        st.markdown(f"## {latest['title']}")
        st.write(f"カテゴリ：{latest['category']}")

        st.markdown("### 称号の意味")
        st.write(latest["desc"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

        fav = st.checkbox("⭐ お気に入り", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["favorite"] = fav
                    break
            save_data(data)

st.divider()

st.subheader("履歴")

df = to_df(data)
if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ お気に入りだけ表示", value=False)
    view = df.copy()
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
            st.markdown(f"### {chosen['title']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"カテゴリ：{chosen['category']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**称号の意味**")
            st.write(chosen["desc"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
