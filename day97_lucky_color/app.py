import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day97：今日のラッキーカラー"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day97_lucky_color.json")

COLOR_POOL = {
    "元気を出したい": [
        {
            "name": "サンライズオレンジ",
            "hex": "#FFA94D",
            "meaning": "行動力・前向きさ・再起動",
            "action": "5分だけでも前に進む行動をしてみる",
            "luna": "今日はこの色で、心のエンジンをやさしくかけていこうね。"
        },
        {
            "name": "ライトレッド",
            "hex": "#FF6B6B",
            "meaning": "情熱・決断・突破力",
            "action": "後回しにしていたことを1つだけ触る",
            "luna": "ご主人の中の火、今日は少しだけ信じてみよ？"
        },
    ],
    "落ち着きたい": [
        {
            "name": "ムーンブルー",
            "hex": "#74C0FC",
            "meaning": "冷静さ・安心・呼吸",
            "action": "深呼吸してから、ゆっくり1つ片付ける",
            "luna": "焦らなくて大丈夫。この色は、心を静かに整えてくれるよ。"
        },
        {
            "name": "ミストグレー",
            "hex": "#CED4DA",
            "meaning": "中立・静けさ・余白",
            "action": "今日は予定を詰めすぎず、1つだけやる",
            "luna": "余白ってね、怠けじゃなくて回復のための大事な場所なんだよ。"
        },
    ],
    "癒されたい": [
        {
            "name": "リーフグリーン",
            "hex": "#8CE99A",
            "meaning": "癒し・回復・自然体",
            "action": "水分をとって、身体をゆるめる時間をつくる",
            "luna": "今日はがんばるより、ほどけることを大事にしようね。"
        },
        {
            "name": "ミルキーピンク",
            "hex": "#FAA2C1",
            "meaning": "やさしさ・愛情・安心感",
            "action": "自分を責める言葉を1つやめてみる",
            "luna": "ご主人には、やさしくされる価値がちゃんとあるんだよ。"
        },
    ],
    "集中したい": [
        {
            "name": "ディープネイビー",
            "hex": "#364FC7",
            "meaning": "集中・知性・深さ",
            "action": "25分だけ集中タイムを作る",
            "luna": "今日は静かに潜る日。深く入れたら、それだけで勝ちだよ。"
        },
        {
            "name": "クリアホワイト",
            "hex": "#F8F9FA",
            "meaning": "整理・明瞭さ・リセット",
            "action": "机の上か頭の中を、少しだけ整える",
            "luna": "まっさらな感覚って、それだけで力になるんだよ。"
        },
    ],
    "わくわくしたい": [
        {
            "name": "スターイエロー",
            "hex": "#FFD43B",
            "meaning": "希望・遊び心・発見",
            "action": "新しいことを1つだけ試してみる",
            "luna": "今日は“ちょっと楽しそう”を選ぶと流れが変わるかもっ。"
        },
        {
            "name": "コズミックパープル",
            "hex": "#B197FC",
            "meaning": "直感・ひらめき・魔法感",
            "action": "浮かんだアイデアを1つメモして残す",
            "luna": "ひらめきって、ちゃんと受け取ると未来の鍵になるんだよ。"
        },
    ],
}

RARITY = [
    ("N", 0.65),
    ("R", 0.25),
    ("SR", 0.10),
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
            "id": x.get("id"),
            "created_at": x.get("created_at"),
            "mood": x.get("mood"),
            "rarity": x.get("rarity"),
            "color_name": x.get("color_name"),
            "meaning": x.get("meaning"),
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


def roll_color(mood: str):
    rarity = pick_rarity()
    item = random.choice(COLOR_POOL[mood])

    # レア度で一言盛る
    luna = item["luna"]
    if rarity == "R":
        luna += " 今日はちょっといい流れ、来てるかも。"
    elif rarity == "SR":
        luna += " しかも今日は“当たり日”っぽいよ。直感も信じてみて。"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "mood": mood,
        "rarity": rarity,
        "color_name": item["name"],
        "hex": item["hex"],
        "meaning": item["meaning"],
        "action": item["action"],
        "luna": luna,
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🎨", layout="wide")
st.title("🎨 Day97：今日のラッキーカラー")
st.caption("今の気分から、今日の色と小さなヒントを受け取る軽めアプリ。")

data = load_data()

if "latest_color" not in st.session_state:
    st.session_state["latest_color"] = None

with st.sidebar:
    st.subheader("💾 データ")
    st.code(DATA_PATH)

    df_all = to_df(data)
    if not df_all.empty:
        csv = df_all.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ CSVダウンロード",
            data=csv,
            file_name="day97_lucky_color.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("🧹 リセット")
    if st.button("履歴を全部消す", type="secondary"):
        data["logs"] = []
        save_data(data)
        st.session_state["latest_color"] = None
        st.warning("履歴を全部消したよ。")
        st.rerun()

left, right = st.columns([0.95, 1.05], gap="large")

with left:
    st.subheader("色を引く")

    mood = st.radio(
        "今の気分",
        ["元気を出したい", "落ち着きたい", "癒されたい", "集中したい", "わくわくしたい"]
    )

    if st.button("🎨 ラッキーカラーを引く", type="primary"):
        result = roll_color(mood)
        data["logs"].append(result)
        save_data(data)
        st.session_state["latest_color"] = result
        st.rerun()

with right:
    st.subheader("今日の結果")

    latest = st.session_state.get("latest_color")
    if latest is None and data["logs"]:
        latest = data["logs"][-1]

    if latest:
        st.markdown(f"### {latest['color_name']} 〔{latest['rarity']}〕")

        st.markdown(
            f"""
            <div style="
                width: 100%;
                height: 120px;
                border-radius: 16px;
                background-color: {latest['hex']};
                border: 1px solid #ddd;
                margin-bottom: 16px;
            "></div>
            """,
            unsafe_allow_html=True
        )

        st.write(f"**カラーコード**：{latest['hex']}")
        st.write(f"**意味**：{latest['meaning']}")
        st.write("**今日のおすすめ行動**")
        st.success(latest["action"])
        st.write("**ルナのひとこと**")
        st.info(latest["luna"])

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
            st.markdown(f"### {chosen['color_name']} 〔{chosen['rarity']}〕")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"気分：{chosen['mood']}")
            st.write(f"カラーコード：{chosen['hex']}")
            st.write(f"意味：{chosen['meaning']}")
            st.write("**今日のおすすめ行動**")
            st.success(chosen["action"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
