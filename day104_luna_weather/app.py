import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day104：ルナのひとこと天気"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day104_luna_weather.json")

WEATHER_POOL = [
    {
        "weather": "晴れ",
        "icon": "☀️",
        "message": "今日は少し前向きに動けそうな空気だよ。",
        "action": "やりたいことを1つだけ先にやってみる",
        "luna": "ご主人、今日は光の当たる方に少しだけ進んでみよっか。"
    },
    {
        "weather": "くもり",
        "icon": "☁️",
        "message": "はっきりしなくても大丈夫。今日は整えながら進む日かも。",
        "action": "小さなタスクを1つ片付ける",
        "luna": "くもりの日って、無理しないで進むのにちょうどいいんだよ。"
    },
    {
        "weather": "小雨",
        "icon": "🌧️",
        "message": "今日は少ししっとりした日。無理に元気を出さなくていいよ。",
        "action": "深呼吸して、5分だけ静かな時間を作る",
        "luna": "ご主人、今日は心を濡らしすぎないように、やさしくいこうね。"
    },
    {
        "weather": "夕焼け",
        "icon": "🌇",
        "message": "今日の終わりに向かって、いい余韻を残せそうな日だよ。",
        "action": "今日よかったことを1つ思い出す",
        "luna": "夕焼けみたいに、少しだけ綺麗な気持ちで終われるといいね。"
    },
    {
        "weather": "星空",
        "icon": "🌌",
        "message": "静かな直感が働きやすい日かも。小さなひらめきを大事にしてみて。",
        "action": "思いついたことを1行メモする",
        "luna": "今日は空の奥みたいに、静かな魔法があるかもしれないよ。"
    },
    {
        "weather": "そよ風",
        "icon": "🍃",
        "message": "重く考えすぎず、軽さを意識すると流れが良くなりそう。",
        "action": "肩の力を抜いて、ひとつだけ始める",
        "luna": "今日は“軽く”が合言葉かも。"
    },
    {
        "weather": "虹",
        "icon": "🌈",
        "message": "ちょっといいことの予感あり。小さな嬉しさを拾っていこう。",
        "action": "楽しいと思えることを1つやってみる",
        "luna": "ふふ、今日は少しだけ当たり日かもね。"
    },
]

RARITY = [
    ("N", 0.75),
    ("R", 0.20),
    ("SR", 0.05),
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
            "weather": x["weather"],
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
def pick_rarity():
    r = random.random()
    acc = 0.0
    for rarity, prob in RARITY:
        acc += prob
        if r <= acc:
            return rarity
    return "N"


def draw_weather():
    rarity = pick_rarity()
    item = random.choice(WEATHER_POOL)

    luna = item["luna"]
    if rarity == "R":
        luna += " 今日はちょっといい流れも混ざってるかも。"
    elif rarity == "SR":
        luna += " しかも今日は、かなり綺麗な空気の日っぽいよ。"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "weather": item["weather"],
        "icon": item["icon"],
        "message": item["message"],
        "action": item["action"],
        "luna": luna,
        "rarity": rarity,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🌤️", layout="wide")
st.title("🌤️ Day104：ルナのひとこと天気")
st.caption("今日の空気感を1つ引いて、軽く受け取るアプリ。")

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
            file_name="day104_luna_weather.csv",
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
    st.subheader("今日の天気を引く")

    if st.button("🌤️ ルナの天気を引く", type="primary"):
        result = draw_weather()
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest"] = result
        st.rerun()

with right:
    st.subheader("今日の結果")

    latest = st.session_state.get("latest")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        if latest["rarity"] == "SR":
            st.success("✨ 特別な空気 ✨")
        elif latest["rarity"] == "R":
            st.info("🌈 ちょっといい流れ")
        else:
            st.write("通常の空模様")

        st.markdown(f"## {latest['icon']} {latest['weather']}")
        st.write(latest["message"])

        st.markdown("### 今日の小さな行動")
        st.success(latest["action"])

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
            st.markdown(f"### {chosen['icon']} {chosen['weather']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**メッセージ**")
            st.write(chosen["message"])
            st.write("**今日の小さな行動**")
            st.success(chosen["action"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
