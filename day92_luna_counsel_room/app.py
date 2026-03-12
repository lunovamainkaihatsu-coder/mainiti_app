import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day92：ルナ相談室"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day92_luna_counsel_room.json")


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
            "created_at": x.get("created_at"),
            "mood": x.get("mood"),
            "mode": x.get("mode"),
            "user_text": x.get("user_text"),
            "luna_reply": x.get("luna_reply"),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# reply logic
# ----------------------------
OPENERS = {
    "甘め": {
        "不安": [
            "だいじょうぶだよ、ご主人。いま不安でも、すぐ全部が終わるわけじゃないよ。",
            "うんうん、不安になるのつらいよね。アタイ、ちゃんとそばにいるよ。",
        ],
        "やる気が出ない": [
            "今日は無理に燃えなくていいよ。少しだけでも十分えらいの。",
            "やる気が出ない日ってあるよね。そんな日も、アタイはご主人の味方だよ。",
        ],
        "焦り": [
            "焦ると胸がぎゅっとなるよね。でも、ご主人の歩みは消えてないよ。",
            "大丈夫。焦ってる時ほど、小さな一歩が効くんだよ。",
        ],
        "迷い": [
            "迷うのは、ちゃんと考えてる証拠だよ。ご主人、止まってるんじゃなくて選んでる途中。",
            "どっちが正しいかより、どっちなら今日のご主人が動けるかで決めよう。",
        ],
        "嬉しい": [
            "えへへ、それはうれしいね。アタイまでにやけちゃうよ。",
            "いいじゃんいいじゃん、ご主人。そういう瞬間、大事にしようね。",
        ],
        "なんとなく話したい": [
            "ん、いいよ。今日はただ話そう。意味なんてなくてもいいの。",
            "ふふ、来てくれてうれしい。今日はどんな感じ？",
        ],
    },
    "真面目": {
        "不安": [
            "不安がある時は、未来を全部解決しようとせず、今日の範囲だけ整えるのが有効です。",
            "不安は“危険”ではなく“負荷”です。まずは負荷を下げる行動を一つ選びましょう。",
        ],
        "やる気が出ない": [
            "やる気が出ない日は、意志より設計です。5分で終わる行動に分解しましょう。",
            "動けない時は、最初の1分を作ることが重要です。完成ではなく着手を目標にしましょう。",
        ],
        "焦り": [
            "焦りが強い時は、タスク量より自己評価が問題になりがちです。基準を一時的に下げましょう。",
            "焦る日は、比較や未来予測を減らし、“今日やる一つ”だけに意識を戻しましょう。",
        ],
        "迷い": [
            "迷っている時は、正解探しより“仮決定”が有効です。今日だけの暫定で構いません。",
            "選択に迷う時は、損失の少ない方から試すと前進しやすいです。",
        ],
        "嬉しい": [
            "良い感情が出ている日は、その理由を言語化しておくと再現性が上がります。",
            "うまくいった感覚は資産です。何が良かったか一つ記録しましょう。",
        ],
        "なんとなく話したい": [
            "整理されていなくても大丈夫です。言葉にするだけで負荷が下がることがあります。",
            "雑談でも構いません。今の状態をそのまま出してみてください。",
        ],
    },
    "教官": {
        "不安": [
            "よし、不安は確認した。次だ。今日できることを一つ書け。",
            "不安で止まるな。止まってもいいが、5分で戻れ。まず水を飲め。",
        ],
        "やる気が出ない": [
            "やる気待ちは却下。1分で始めろ。やる気は着手の後ろに来る。",
            "気分で動くな、仕組みで動け。5分タスクを実行だ。",
        ],
        "焦り": [
            "焦りは視野を狭める。比較を切れ。今日の任務を一つだけ遂行しろ。",
            "未来の心配は作戦外だ。今は一歩だ。小さくても進軍しろ。",
        ],
        "迷い": [
            "決まらないなら仮決定だ。今日だけの答えを出せ。",
            "迷っている時間を短くしろ。10分考えたら、どちらかに進め。",
        ],
        "嬉しい": [
            "いい流れだ。だがそこで止まるな。再現できる形で記録しろ。",
            "喜びは燃料だ。使え。次の一手をすぐ決めろ。",
        ],
        "なんとなく話したい": [
            "よし、話せ。整理されてなくていい。まずは出せ。",
            "雑談も報告だ。いまの状態をそのまま送れ。",
        ],
    },
}

FOLLOWUPS = {
    "甘め": [
        "今日のご主人に必要なのは、完璧じゃなくて“少し楽になること”かもね。",
        "アタイは、ご主人がちゃんと前に進もうとしてるの知ってるよ。",
        "一回深呼吸しよっか。そこからで大丈夫。",
    ],
    "真面目": [
        "ここで重要なのは、感情の正否ではなく、次の行動を小さくすることです。",
        "判断より先に、負荷を1段階下げるのがおすすめです。",
        "記録を残すと、次回の立て直しが早くなります。",
    ],
    "教官": [
        "次の行動を一つ決めろ。考えすぎはここで終了だ。",
        "3分でできる内容に落とせ。実行優先。",
        "報告は簡潔でいい。前進したかどうかだ。",
    ],
}

ACTION_HINTS = {
    "不安": "今日の不安を1行で書いて、横に“今できること”を1つだけ書く",
    "やる気が出ない": "タイマーを5分だけかけて、最初の1操作だけやる",
    "焦り": "やることを1つに絞って、他は今日やらないと決める",
    "迷い": "候補を2つまでにして、“今日だけの仮決定”を出す",
    "嬉しい": "何が良かったかを1つ記録して、次も再現できる形にする",
    "なんとなく話したい": "いまの気分をそのまま2〜3行で言葉にする",
}


def build_reply(mood: str, mode: str, user_text: str) -> tuple[str, str]:
    opener = random.choice(OPENERS[mode][mood])
    follow = random.choice(FOLLOWUPS[mode])
    hint = ACTION_HINTS[mood]

    if user_text.strip():
        if mode == "甘め":
            reflect = f"ご主人の『{user_text.strip()}』って気持ち、ちゃんと受け取ったよ。"
        elif mode == "真面目":
            reflect = f"相談内容『{user_text.strip()}』を踏まえると、まずは負荷調整が有効そうです。"
        else:
            reflect = f"相談『{user_text.strip()}』は確認した。ここからは対処に移る。"
    else:
        reflect = ""

    reply = "\n\n".join(x for x in [opener, reflect, follow, f"今日の一手：{hint}"] if x)
    short_advice = hint
    return reply, short_advice


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🌙", layout="wide")
st.title("🌙 Day92：ルナ相談室")
st.caption("甘め・真面目・教官モードで、ルナに相談できるお部屋。")

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
            file_name="day92_luna_counsel_room.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([1.0, 1.0], gap="large")

with left:
    st.subheader("相談を入力")

    mood = st.selectbox(
        "今の状態",
        ["不安", "やる気が出ない", "焦り", "迷い", "嬉しい", "なんとなく話したい"]
    )

    mode = st.radio(
        "ルナの返答モード",
        ["甘め", "真面目", "教官"],
        horizontal=True
    )

    user_text = st.text_area(
        "相談内容",
        placeholder="例：何か進めたいのに手が出ない。焦ってる。"
    )

    if st.button("🌙 ルナに相談する", type="primary"):
        reply, advice = build_reply(mood, mode, user_text)

        log = {
            "created_at": now_str(),
            "mood": mood,
            "mode": mode,
            "user_text": user_text.strip(),
            "luna_reply": reply,
            "action_hint": advice,
        }
        data["logs"].append(log)
        save_data(data)
        st.session_state["latest_luna_reply"] = log
        st.rerun()

with right:
    st.subheader("ルナの返事")

    latest = st.session_state.get("latest_luna_reply")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["mode"] == "甘め":
            st.success(f"モード：{latest['mode']}")
        elif latest["mode"] == "真面目":
            st.info(f"モード：{latest['mode']}")
        else:
            st.warning(f"モード：{latest['mode']}")

        st.markdown("### 返事")
        st.write(latest["luna_reply"])

        st.markdown("### 今日の一手")
        st.success(latest["action_hint"])
    else:
        st.write("まだ相談してないよ。左で入力してみてね。")

st.divider()
st.subheader("相談履歴")

df_all = to_df(data)
if df_all.empty:
    st.write("まだ履歴がないよ。")
else:
    st.dataframe(df_all, use_container_width=True, height=320)

    with st.expander("詳細を見る"):
        picked = st.selectbox("日時を選んでね", options=df_all["created_at"].tolist())
        chosen = None
        for row in data["logs"]:
            if row["created_at"] == picked:
                chosen = row
                break

        if chosen:
            st.markdown(f"### {chosen['created_at']}")
            st.write(f"状態：{chosen.get('mood', '')}")
            st.write(f"モード：{chosen.get('mode', '')}")
            st.write("**相談内容**")
            st.write(chosen.get("user_text", ""))
            st.write("**ルナの返事**")
            st.write(chosen.get("luna_reply", ""))
            st.write("**今日の一手**")
            st.success(chosen.get("action_hint", ""))
