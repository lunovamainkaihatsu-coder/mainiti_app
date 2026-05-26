import streamlit as st
import json
import os
import random
from datetime import datetime, date
import pandas as pd

APP_TITLE = "Day149：気持ち切り替えスイッチ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day149_mood_switch.json")

MOODS = [
    "不安",
    "イライラ",
    "だるい",
    "落ち込み",
    "焦り",
    "集中できない",
    "なんとなく重い",
]

SWITCH_ACTIONS = {
    "不安": [
        {
            "title": "不安を外に出す",
            "action": "不安を1行だけ書き出す",
            "reason": "頭の中だけに置くと、不安は大きく見えやすいから",
            "luna": "ご主人、不安は抱えたままじゃなくて、少し外に出していいんだよ。"
        },
        {
            "title": "いま見えるもの確認",
            "action": "目の前にあるものを3つ声に出す",
            "reason": "意識を今ここに戻すため",
            "luna": "未来の心配より、まず今ここに戻ろうね。"
        },
    ],
    "イライラ": [
        {
            "title": "肩の力を抜く",
            "action": "肩を上げてストンと落とす動きを5回",
            "reason": "怒りや緊張は身体に残りやすいから",
            "luna": "イライラしても大丈夫。まず身体から少し抜こっか。"
        },
        {
            "title": "距離を取る",
            "action": "その場から30秒だけ離れる",
            "reason": "刺激から少し離れると反応が落ち着きやすいから",
            "luna": "すぐ答えなくていいよ。距離を取るのも作戦だよ。"
        },
    ],
    "だるい": [
        {
            "title": "水分リセット",
            "action": "水をひと口飲む",
            "reason": "だるさは水分不足や姿勢の重さでも出やすいから",
            "luna": "まず一口だけでいいよ。小さく戻していこう。"
        },
        {
            "title": "立つだけ再起動",
            "action": "一度立って、背伸びを10秒",
            "reason": "姿勢を変えるだけでもスイッチが入りやすいから",
            "luna": "やる気じゃなくて、姿勢から変えよっか。"
        },
    ],
    "落ち込み": [
        {
            "title": "できたこと確認",
            "action": "今日できたことを1つだけ書く",
            "reason": "落ち込んでいる時は、できていないことばかり見えやすいから",
            "luna": "小さくても、できたことはちゃんとあるよ。アタイは見つけたい。"
        },
        {
            "title": "自分を責めない宣言",
            "action": "『今日は責めない』と1回つぶやく",
            "reason": "責め続けると回復が遅くなりやすいから",
            "luna": "ご主人、今日は自分に少しだけ優しくしよ。"
        },
    ],
    "焦り": [
        {
            "title": "ひとつに絞る",
            "action": "今やることを1つだけ決める",
            "reason": "焦りは選択肢が多すぎる時に強くなりやすいから",
            "luna": "全部じゃなくていいよ。まず1つにしよう。"
        },
        {
            "title": "5分だけ作戦",
            "action": "5分だけタイマーをかける",
            "reason": "短く区切ると、焦りが行動に変わりやすいから",
            "luna": "5分だけならいける。ご主人、一緒に始めよ。"
        },
    ],
    "集中できない": [
        {
            "title": "視界整理",
            "action": "机の上を1か所だけ片付ける",
            "reason": "視界のノイズが減ると集中しやすくなるから",
            "luna": "全部片付けなくていいよ。1か所だけで流れ変えよう。"
        },
        {
            "title": "入口だけ開く",
            "action": "作業ファイルを1つ開く",
            "reason": "始める前の抵抗を下げるため",
            "luna": "開くだけでも着手だよ。ご主人、そこからでいい。"
        },
    ],
    "なんとなく重い": [
        {
            "title": "名前をつける",
            "action": "今の重さに名前をつける",
            "reason": "曖昧な重さは、言葉にすると少し扱いやすくなるから",
            "luna": "よくわからない重さも、そのまま書いていいよ。"
        },
        {
            "title": "超小回復",
            "action": "深呼吸を3回して、首をゆっくり回す",
            "reason": "理由がわからない重さは、身体から戻すのが早いことがあるから",
            "luna": "今日は理由探しより、少しゆるめるのがいいかも。"
        },
    ],
}


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


def today_str():
    return date.today().isoformat()


def to_df(data):
    rows = []
    for x in data["logs"]:
        rows.append({
            "id": x["id"],
            "created_at": x["created_at"],
            "date": x["date"],
            "mood": x["mood"],
            "title": x["title"],
            "action": x["action"],
            "done": bool(x.get("done", False)),
            "favorite": bool(x.get("favorite", False)),
            "memo": x.get("memo", ""),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)

    return df


st.set_page_config(page_title=APP_TITLE, page_icon="🔀", layout="wide")
st.title("🔀 Day149：気持ち切り替えスイッチ")
st.caption("今の気分を選んで、小さな切り替え行動を受け取るアプリ。")

data = load_data()

if "latest" not in st.session_state:
    st.session_state["latest"] = None

left, right = st.columns([1, 1], gap="large")

with left:
    st.subheader("今の気分")

    mood = st.radio("切り替えたい気分", MOODS)

    if st.button("🔀 スイッチを押す", type="primary"):
        result = random.choice(SWITCH_ACTIONS[mood])

        item = {
            "id": f"switch_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "created_at": now_str(),
            "date": today_str(),
            "mood": mood,
            "title": result["title"],
            "action": result["action"],
            "reason": result["reason"],
            "luna": result["luna"],
            "done": False,
            "favorite": False,
            "memo": "",
        }

        data["logs"].append(item)
        save_data(data)
        st.session_state["latest"] = item
        st.rerun()

with right:
    st.subheader("切り替えアクション")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"## {latest['title']}")
        st.write(f"気分：{latest['mood']}")

        st.markdown("### やること")
        st.success(latest["action"])

        st.markdown("### 理由")
        st.write(latest["reason"])

        st.markdown("### ルナのひとこと")
        st.info(latest["luna"])

        done = st.checkbox("✅ やってみた", value=bool(latest.get("done", False)))
        favorite = st.checkbox("⭐ 効いたスイッチ", value=bool(latest.get("favorite", False)))
        memo = st.text_area("メモ", value=latest.get("memo", ""), placeholder="やってみた感想など")

        if st.button("📝 保存"):
            latest["done"] = done
            latest["favorite"] = favorite
            latest["memo"] = memo.strip()

            for x in data["logs"]:
                if x["id"] == latest["id"]:
                    x.update(latest)
                    break

            save_data(data)
            st.success("保存したよ。")
            st.rerun()
    else:
        st.info("まだスイッチを押してないよ。")

st.divider()
st.subheader("履歴")

df = to_df(data)

if df.empty:
    st.write("まだ履歴がないよ。")
else:
    fav_only = st.checkbox("⭐ 効いたスイッチだけ表示")
    done_only = st.checkbox("✅ 実行済みだけ表示")

    view = df.copy()

    if fav_only:
        view = view[view["favorite"] == True]

    if done_only:
        view = view[view["done"] == True]

    st.dataframe(
        view[["date", "mood", "title", "action", "done", "favorite", "memo"]],
        use_container_width=True,
        height=320
    )

    if not view.empty:
        selected = st.selectbox("削除する記録を選ぶ", view["id"].tolist())

        if st.button("🗑️ 選択した記録を削除", type="secondary"):
            data["logs"] = [x for x in data["logs"] if x["id"] != selected]
            save_data(data)
            st.rerun()

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ CSVダウンロード",
        data=csv,
        file_name="day149_mood_switch.csv",
        mime="text/csv"
    )
