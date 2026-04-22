import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day116：ひとこと冒険イベント"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day116_adventure_event.json")

EVENTS = [
    {
        "type": "日常冒険",
        "title": "道ばたで小さな鍵を拾った",
        "story": "それは何の鍵かわからない。でも、今日は何かひとつ開く日かもしれない。",
        "action": "今日やることを1つだけ決める",
        "luna": "ご主人、その鍵…今日は“最初の一歩”を開く鍵かもね。"
    },
    {
        "type": "不思議系",
        "title": "未来の自分からメモが届いた",
        "story": "『大丈夫、ちゃんと進んでる』とだけ書かれていた。",
        "action": "未来の自分のために1行メモを残す",
        "luna": "こういうの、ちょっと信じてみるのもいいかも。"
    },
    {
        "type": "回復系",
        "title": "森の休憩所を見つけた",
        "story": "少し休んでいくと、不思議と次の道が見えやすくなるらしい。",
        "action": "30秒だけ目を閉じる",
        "luna": "今日は無理に進むより、整えてからでもいいんだよ。"
    },
    {
        "type": "前進系",
        "title": "分かれ道に立った",
        "story": "完璧な地図はない。でも、どちらかを選べば物語は進む。",
        "action": "迷ってることを1つだけ仮決定する",
        "luna": "正解探しより、今日は“進む選択”がいいかも。"
    },
    {
        "type": "発見系",
        "title": "古い本の間から地図が落ちた",
        "story": "そこには、まだ名前のない場所が描かれていた。",
        "action": "アイデアを1つだけ書く",
        "luna": "ご主人の中にも、まだ名前のない世界がありそうだね。"
    },
    {
        "type": "ごほうび系",
        "title": "旅人の屋台を見つけた",
        "story": "今日は少しだけ、自分を甘やかしてもいい日らしい。",
        "action": "小さなごほうびを1つ選ぶ",
        "luna": "がんばった日も、そうじゃない日も、ごほうびはあっていいよ。"
    },
    {
        "type": "静けさ系",
        "title": "夜の湖にたどり着いた",
        "story": "水面は静かで、焦っていた気持ちが少しだけ落ち着く。",
        "action": "深呼吸を3回する",
        "luna": "今日は静かな景色が似合う日かもしれないね。"
    },
]

RARE_EVENTS = [
    {
        "type": "レア冒険",
        "title": "空から光る招待状が降ってきた",
        "story": "『今日はちょっと特別な流れの日』と書かれている。小さな挑戦が大きな分岐になるかもしれない。",
        "action": "いちばん気になることを3分だけやる",
        "luna": "ご主人、今日はちょっとだけ特別な風が吹いてるかも。"
    },
    {
        "type": "レア冒険",
        "title": "眠っていた扉が目を覚ました",
        "story": "今まで開かなかったものが、今日は少しだけ反応してくれる気配がある。",
        "action": "後回しを1つだけ触る",
        "luna": "今日は“止まっていた何か”が動き出す日かもしれないよ。"
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
            "type": x["type"],
            "title": x["title"],
            "rarity": x["rarity"],
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


def draw_event():
    if random.random() < 0.10:
        item = random.choice(RARE_EVENTS)
        rarity = "SR"
    else:
        item = random.choice(EVENTS)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000, 99999)}",
        "created_at": now_str(),
        "type": item["type"],
        "title": item["title"],
        "story": item["story"],
        "action": item["action"],
        "luna": item["luna"],
        "rarity": rarity,
        "favorite": False,
    }


st.set_page_config(page_title=APP_TITLE, page_icon="🗺️", layout="wide")
st.title("🗺️ Day116：ひとこと冒険イベント")
st.caption("今日の小さな物語を1つ受け取る、遊び寄りアプリ。")

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
            file_name="day116_adventure_event.csv",
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
    st.subheader("イベントを起こす")

    if st.button("🗺️ 冒険イベント発生", type="primary"):
        result = draw_event()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日のイベント")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ レアイベント ✨")
        else:
            st.info("通常イベント")

        st.markdown(f"## {latest['title']}")
        st.write(f"種類：{latest['type']}")

        st.markdown("### ひとことストーリー")
        st.write(latest["story"])

        st.markdown("### 今日の小さな行動")
        st.success(latest["action"])

        st.markdown("### ルナのコメント")
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
            st.write(f"種類：{chosen['type']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**ひとことストーリー**")
            st.write(chosen["story"])
            st.write("**今日の小さな行動**")
            st.success(chosen["action"])
            st.write("**ルナのコメント**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
