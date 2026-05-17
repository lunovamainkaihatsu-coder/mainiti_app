import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day129：五月病リカバリーモード"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day129_may_blues_recovery.json")

RECOVERY_POOL = {
    "重い": [
        {
            "title": "今日は回復最優先",
            "mission": "水を飲んで、30秒だけ目を閉じる",
            "reason": "気力が低い日は、まず身体から戻すのが一番早いから",
            "luna": "ご主人、今日は頑張る日じゃなくて“戻す日”でいいよ。"
        },
        {
            "title": "ゼロ回避だけで勝ち",
            "mission": "1行だけメモを書く",
            "reason": "大きな行動より、ゼロじゃない記録が回復のきっかけになるから",
            "luna": "1行でも残せたら、今日はちゃんと勝ちだよ。"
        },
    ],
    "普通": [
        {
            "title": "小さく整える日",
            "mission": "机かスマホ画面を1か所だけ整える",
            "reason": "環境を少し整えると、気持ちも少し戻りやすいから",
            "luna": "今日は小さく整えて、流れを戻していこう。"
        },
        {
            "title": "5分だけ再起動",
            "mission": "5分だけ作業か読書をする",
            "reason": "やる気は待つより、軽く動いた後に出やすいから",
            "luna": "ご主人、5分だけでいいよ。一緒に再起動しよ。"
        },
    ],
    "少し元気": [
        {
            "title": "前進の火種を作る日",
            "mission": "今日やりたいことを1つだけ進める",
            "reason": "少し元気がある日は、小さな成果を作ると流れが続くから",
            "luna": "今日はちょっと進めそうだね。無理なく一歩いこっか。"
        },
        {
            "title": "未来の自分を助ける日",
            "mission": "明日の自分が楽になることを1つやる",
            "reason": "今の小さな準備が、明日の負担を減らしてくれるから",
            "luna": "その一手、明日のご主人を助けるやつだよ。"
        },
    ],
}

RARE = [
    {
        "title": "反転のきっかけ",
        "mission": "いちばん気になっていることを3分だけ触る",
        "reason": "止まっていた流れは、短い接触だけで動き出すことがあるから",
        "luna": "ご主人、今日は少しだけ反転の気配があるかも。"
    }
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


def draw_recovery(level):
    if random.random() < 0.1:
        item = random.choice(RARE)
        rarity = "SR"
    else:
        item = random.choice(RECOVERY_POOL[level])
        rarity = "N"

    return {
        "id": f"log_{datetime.now().strftime('%H%M%S%f')}",
        "created_at": now_str(),
        "level": level,
        "rarity": rarity,
        "title": item["title"],
        "mission": item["mission"],
        "reason": item["reason"],
        "luna": item["luna"],
        "done": False,
        "favorite": False,
    }


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "level": x["level"],
            "title": x["title"],
            "mission": x["mission"],
            "rarity": x["rarity"],
            "done": bool(x.get("done", False)),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🌿", layout="wide")
st.title("🌿 Day129：五月病リカバリーモード")
st.caption("無理に上げず、少しだけ戻るための回復ミッションアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今の状態")

    level = st.radio(
        "今日はどのくらい重い？",
        ["重い", "普通", "少し元気"],
        horizontal=True
    )

    if st.button("🌿 リカバリーミッションを受け取る", type="primary"):
        result = draw_recovery(level)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日のリカバリー")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レア回復ミッション ✨")
        else:
            st.info("通常ミッション")

        st.markdown(f"## {latest['title']}")
        st.write(f"状態：{latest['level']}")

        st.markdown("### 今日やること")
        st.success(latest["mission"])

        st.markdown("### 理由")
        st.write(latest["reason"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

        done = st.checkbox("✅ やった", value=bool(latest.get("done", False)))
        fav = st.checkbox("⭐ お気に入り", value=bool(latest.get("favorite", False)))

        if done != bool(latest.get("done", False)) or fav != bool(latest.get("favorite", False)):
            latest["done"] = done
            latest["favorite"] = fav
            for row in data["logs"]:
                if row["id"] == latest["id"]:
                    row["done"] = done
                    row["favorite"] = fav
                    break
            save_data(data)
            st.toast("更新したよ")

st.divider()
st.subheader("履歴")

df = to_df(data)
if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ お気に入りだけ表示")
    view = df.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day129_may_blues_recovery.csv",
        mime="text/csv"
    )
