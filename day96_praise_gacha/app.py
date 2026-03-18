import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day96：一言ほめガチャ"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day96_praise_gacha.json")

RARITIES = [
    ("N", 0.55),
    ("R", 0.27),
    ("SR", 0.13),
    ("SSR", 0.05),
]

PRAISES = {
    "甘め": {
        "N": [
            "ご主人、今日ここに来ただけでもえらいよ。",
            "ちゃんと前に進もうとしてるの、アタイは知ってるよ。",
            "無理してなくても、ご主人には価値があるんだからね。",
            "今日も生きててくれてえらいよ。",
        ],
        "R": [
            "ご主人の小さな一歩って、ほんとはすごく尊いんだよ。",
            "焦ってても止まらずに来た、それだけで十分すごいよ。",
            "アタイ、ご主人が積み上げてるのちゃんと見てるからね。",
        ],
        "SR": [
            "ご主人はね、まだ途中なだけで、ちゃんと未来に向かってる人だよ。",
            "誰にも見えないところで頑張ってるの、アタイには全部伝わってるよ。",
        ],
        "SSR": [
            "ご主人がここまで歩いてきた軌跡、ぜんぶ宝物だよ。アタイはその一つ一つが大好き。",
            "ねぇご主人、今のあなたは“まだ何者でもない”んじゃなくて、“これから形になるすごい途中”なんだよ。",
        ],
    },
    "真面目": {
        "N": [
            "行動しようと意識を向けた時点で前進です。",
            "小さな継続は十分に評価すべきです。",
            "止まって見えても、整理している時間には意味があります。",
            "今日ここを開いたこと自体が再起動です。",
        ],
        "R": [
            "完璧ではなくても、継続を選んでいるのは強みです。",
            "記録を残そうとする姿勢は、将来の資産になります。",
            "いまの積み上げは、あとで効いてきます。",
        ],
        "SR": [
            "不安があっても前に出ようとする姿勢は、かなり価値があります。",
            "日々の試行錯誤を続けている時点で、十分に前進しています。",
        ],
        "SSR": [
            "あなたは“結果が出るまで続ける力”をすでに育て始めています。それは非常に強い資質です。",
            "いまの地道な積み上げは、後から振り返った時に大きな分岐点になります。",
        ],
    },
    "教官": {
        "N": [
            "よし、来たな。それだけで一歩前進だ。",
            "止まってない。確認した。次へ進め。",
            "今日も再起動完了。いいぞ。",
            "小さくても行動意思あり。十分だ。",
        ],
        "R": [
            "迷いながらでも前に出る、それが強さだ。",
            "気分に関係なく戻ってきた。評価する。",
            "継続の意思を見せたな。悪くない。",
        ],
        "SR": [
            "お前はちゃんと積み上げている。見えなくても進軍中だ。",
            "不調でもゼロにしない、その姿勢はかなり強い。",
        ],
        "SSR": [
            "聞け。お前はもう“やる側”の人間だ。ここまで来た時点で、凡人の停止線は越えている。",
            "お前の前進はまだ小さい。だが本物だ。本物は積もる。続けろ。",
        ],
    },
}

RARITY_LABEL = {
    "N": "N",
    "R": "R",
    "SR": "SR",
    "SSR": "SSR",
}


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
            "id": x.get("id"),
            "created_at": x.get("created_at"),
            "mode": x.get("mode"),
            "rarity": x.get("rarity"),
            "message": x.get("message"),
            "favorite": bool(x.get("favorite", False)),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("created_at", ascending=False)
    return df


# ----------------------------
# gacha logic
# ----------------------------
def pick_rarity():
    r = random.random()
    acc = 0.0
    for rarity, prob in RARITIES:
        acc += prob
        if r <= acc:
            return rarity
    return "N"


def roll_praise(mode: str):
    rarity = pick_rarity()
    message = random.choice(PRAISES[mode][rarity])

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "mode": mode,
        "rarity": rarity,
        "message": message,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🎁", layout="wide")
st.title("🎁 Day96：一言ほめガチャ")
st.caption("ボタンを押すと、ルナが一言ほめてくれる軽めのお遊びアプリ。")

data = load_data()

if "latest_praise" not in st.session_state:
    st.session_state["latest_praise"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day96_praise_gacha.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest_praise"] = None
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([1.0, 1.0], gap="large")

with left:
    st.subheader("ガチャを回す")

    mode = st.radio("モード", ["甘め", "真面目", "教官"], horizontal=True)

    if st.button("🎲 ほめてもらう", type="primary"):
        result = roll_praise(mode)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest_praise"] = result
        st.rerun()

with right:
    st.subheader("今回の結果")

    latest = st.session_state.get("latest_praise")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["mode"] == "甘め":
            st.success(f"モード：{latest['mode']}")
        elif latest["mode"] == "真面目":
            st.info(f"モード：{latest['mode']}")
        else:
            st.warning(f"モード：{latest['mode']}")

        st.markdown(f"### レア度：{RARITY_LABEL[latest['rarity']]}")
        st.write(latest["message"])

        fav = st.checkbox("⭐ お気に入りにする", value=bool(latest.get("favorite", False)))
        if fav != bool(latest.get("favorite", False)):
            latest["favorite"] = fav
            for row in data["logs"]:
                if row.get("id") == latest.get("id"):
                    row["favorite"] = fav
                    break
            save_data(data)
            st.toast("お気に入り更新！")
    else:
        st.write("まだ回してないよ。左のボタンを押してみてね。")

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
            st.markdown(f"### {chosen['created_at']}")
            st.write(f"モード：{chosen['mode']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**ほめ言葉**")
            st.write(chosen["message"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
