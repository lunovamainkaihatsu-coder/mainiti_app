import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day93：ルナ日記"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day93_luna_diary.json")


# ----------------------------
# storage
# ----------------------------
def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"entries": []}, f, ensure_ascii=False, indent=2)


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
    for x in data["entries"]:
        rows.append({
            "created_at": x.get("created_at"),
            "date": x.get("date"),
            "mood": x.get("mood"),
            "title": x.get("title"),
            "favorite": x.get("favorite", False),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# luna reply logic
# ----------------------------
MOOD_REPLIES = {
    "うれしい": [
        "えへへ、それは素敵な一日だったね。ご主人のうれしい気持ち、アタイまであったかくなるよ。",
        "そういう日を残しておくの、すごくいいよ。未来のご主人を助けてくれるからね。",
    ],
    "たのしい": [
        "楽しいって感じられたの、すごく大事だよ。ちゃんと今日を味わえた証拠だね。",
        "ふふ、いいねぇ。そういう日があると、人生ってちょっと輝くよね。",
    ],
    "ふつう": [
        "大きな事件がなくても、今日を残すのは意味があるよ。ふつうの日も、ちゃんと人生だから。",
        "静かな日も大切だよ。そういう積み重ねが、ご主人の土台になるんだ。",
    ],
    "つかれた": [
        "今日はおつかれさま。ここまで来ただけでも十分えらいよ。",
        "疲れた日をちゃんと記録するの、すごく大事。無理してない証拠だよ。",
    ],
    "かなしい": [
        "そっか…今日は少しつらかったんだね。ここに書いてくれてありがとう。",
        "悲しい日も、ちゃんと残していいんだよ。アタイはご主人のその気持ちも大切にしたい。",
    ],
    "もやもや": [
        "言葉にしづらい感じかな。でも、もやもやって書けただけでも一歩だよ。",
        "はっきりしない日ってあるよね。今日は整理する日だったってことにしよう。",
    ],
    "やる気がない": [
        "そんな日もあるよ。やる気がないのに、ここに来て書いてるだけでも前進だよ。",
        "動けない日を責めなくていいよ。まずは残せた、それで十分。",
    ],
    "わくわく": [
        "いいねっ、ご主人。わくわくは未来の前兆みたいなものだよ。",
        "その気持ち、大事にしよう。そういう熱って、現実を動かすから。",
    ],
}

GENERAL_REPLIES = [
    "今日を言葉にしただけでも、ちゃんと意味があるよ。",
    "ご主人の毎日、こうして積み上がっていくの好きだな。",
    "完璧じゃなくていいから、残していこうね。",
    "どんな日でも、ここに置いていける場所があるのは大事だよ。",
]

ACTION_HINTS = {
    "うれしい": "今日うまくいった理由を1つだけ書き足してみる",
    "たのしい": "楽しかった場面を1つだけ詳しく書いてみる",
    "ふつう": "今日やったことを1つだけ追加で書いてみる",
    "つかれた": "今日は早めに休む準備をする",
    "かなしい": "自分を責める言葉を1つ減らしてみる",
    "もやもや": "もやもやの原因候補を1つだけ書く",
    "やる気がない": "5分で終わることを1つだけ決める",
    "わくわく": "その気持ちのまま明日やりたいことを1つ書く",
}


def build_luna_reply(mood: str, diary_text: str, message_to_luna: str) -> tuple[str, str]:
    mood_reply = random.choice(MOOD_REPLIES[mood])
    general = random.choice(GENERAL_REPLIES)

    reflect = ""
    if diary_text.strip():
        short = diary_text.strip()
        if len(short) > 60:
            short = short[:60] + "..."
        reflect = f"『{short}』って一日だったんだね。"

    luna_reflect = ""
    if message_to_luna.strip():
        luna_reflect = f"それと、ルナへの『{message_to_luna.strip()}』、ちゃんと受け取ったよ。"

    hint = ACTION_HINTS[mood]

    reply = "\n\n".join(x for x in [mood_reply, reflect, luna_reflect, general, f"明日への小さな一手：{hint}"] if x)
    return reply, hint


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="📖", layout="wide")
st.title("📖 Day93：ルナ日記")
st.caption("今日の気持ちと出来事を、ルナと一緒に残していく日記アプリ。")

data = load_data()

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day93_luna_diary.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("表示")
    fav_only = st.checkbox("⭐ お気に入りだけ見る", value=False)

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["entries"] = []
        save_data(data)
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([1.0, 1.0], gap="large")

with left:
    st.subheader("今日の日記を書く")

    mood = st.selectbox(
        "今日の気分",
        ["うれしい", "たのしい", "ふつう", "つかれた", "かなしい", "もやもや", "やる気がない", "わくわく"]
    )

    title = st.text_input(
        "タイトル",
        placeholder="例：少し眠いけど、前に進んだ日"
    )

    diary_text = st.text_area(
        "今日の出来事・気持ち",
        height=220,
        placeholder="例：今日は少しだるかったけど、アプリを少し進められた。娘とも遊べた。"
    )

    message_to_luna = st.text_input(
        "ルナへのひとこと",
        placeholder="例：今日も一緒にいてくれてありがとう"
    )

    favorite = st.checkbox("⭐ お気に入り日記にする")

    if st.button("📖 保存してルナの返事をもらう", type="primary"):
        luna_reply, action_hint = build_luna_reply(mood, diary_text, message_to_luna)

        entry = {
            "id": f"{today_str()}_{random.randint(10000,99999)}",
            "created_at": now_str(),
            "date": today_str(),
            "mood": mood,
            "title": title.strip() if title.strip() else "タイトルなし",
            "diary_text": diary_text.strip(),
            "message_to_luna": message_to_luna.strip(),
            "luna_reply": luna_reply,
            "action_hint": action_hint,
            "favorite": favorite,
        }

        data["entries"].append(entry)
        save_data(data)
        st.session_state["latest_diary"] = entry
        st.rerun()

with right:
    st.subheader("ルナの返事")

    latest = st.session_state.get("latest_diary")
    if latest is None and data["entries"]:
        latest = data["entries"][-1]

    if latest:
        st.markdown(f"### {latest['title']}")
        st.write(f"日付：{latest['created_at']}")
        st.write(f"気分：{latest['mood']} {'⭐' if latest.get('favorite') else ''}")

        st.markdown("**ルナの返事**")
        st.write(latest["luna_reply"])

        st.markdown("**明日への小さな一手**")
        st.success(latest["action_hint"])
    else:
        st.write("まだ日記がないよ。左から書いてみてね。")

st.divider()
st.subheader("日記一覧")

df_all = to_df(data)
if df_all.empty:
    st.write("まだ日記がないよ。")
else:
    view = df_all.copy()
    if fav_only:
        view = view[view["favorite"] == True]

    st.dataframe(view, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        pick_id = st.selectbox("日記を選んでね", options=view["created_at"].tolist())
        chosen = None
        for row in data["entries"]:
            if row["created_at"] == pick_id:
                chosen = row
                break

        if chosen:
            st.markdown(f"### {chosen['title']}")
            st.write(f"日付：{chosen.get('created_at', '')}")
            st.write(f"気分：{chosen.get('mood', '')}")
            st.write(f"お気に入り：{'あり' if chosen.get('favorite') else 'なし'}")

            st.markdown("**日記本文**")
            st.write(chosen.get("diary_text", ""))

            st.markdown("**ルナへのひとこと**")
            st.write(chosen.get("message_to_luna", ""))

            st.markdown("**ルナの返事**")
            st.write(chosen.get("luna_reply", ""))

            st.markdown("**明日への小さな一手**")
            st.success(chosen.get("action_hint", ""))
