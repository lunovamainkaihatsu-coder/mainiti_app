import streamlit as st
import json
import os
import random
from datetime import datetime
import pandas as pd

APP_TITLE = "Day102：今日の小さな魔法"
DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "day102_small_magic.json")

MAGIC_POOL = [
    {
        "category": "心",
        "title": "深呼吸の魔法",
        "message": "今日は、深呼吸を3回するだけで少し流れが変わるかも。",
        "action": "4秒吸って、6秒吐く呼吸を3回やる",
    },
    {
        "category": "行動",
        "title": "5分着手の魔法",
        "message": "大きくやるんじゃなくて、“5分だけ”始めると道が開く日かも。",
        "action": "5分だけ何かを始める",
    },
    {
        "category": "ことば",
        "title": "やさしい言葉の魔法",
        "message": "今日は、自分に少しやさしい言葉をかけると空気が変わるかも。",
        "action": "『今日はこれでいい』を1回つぶやく",
    },
    {
        "category": "整え",
        "title": "ひと区画整理の魔法",
        "message": "机の上でも、心の中でも、1か所整えるだけで軽くなるかも。",
        "action": "目に入る場所を1か所だけ整える",
    },
    {
        "category": "ひらめき",
        "title": "1行メモの魔法",
        "message": "思いつきを1行残すだけで、未来の種になるかも。",
        "action": "メモを1行だけ書く",
    },
    {
        "category": "心",
        "title": "月の休息魔法",
        "message": "今日は“頑張る”より“休ませる”ほうが効くかもしれないよ。",
        "action": "30秒だけ目を閉じる",
    },
    {
        "category": "行動",
        "title": "最初の1操作の魔法",
        "message": "完成じゃなくて、最初の1操作だけで十分な日もあるよ。",
        "action": "アプリやメモ帳を1つ開く",
    },
    {
        "category": "ことば",
        "title": "未来へのひとこと魔法",
        "message": "明日の自分に一言だけ送ると、ちょっと安心できるかも。",
        "action": "明日の自分へ短く1文書く",
    },
]

RARE_MAGIC = [
    {
        "category": "奇跡",
        "title": "流れ反転の魔法",
        "message": "今日は小さな行動が思った以上に未来を動かす当たり日かも。",
        "action": "後回しを1つだけ触る",
    },
    {
        "category": "奇跡",
        "title": "火種覚醒の魔法",
        "message": "ほんの少しのやる気でも、今日はちゃんと火になるかもしれない。",
        "action": "いちばん気になることを3分だけやる",
    },
]

LUNA_LINES = [
    "ご主人、魔法ってね、大きいことじゃなくて“小さく効くこと”だったりするんだよ。",
    "今日はこれくらいでいい、っていう軽さも大事な魔法だよ。",
    "少しだけでもやれたら、それってちゃんと流れが動いてるってこと。",
    "ご主人に合う魔法、今日はこれかもね。",
    "ふふ、こういう小さなきっかけが未来を変えたりするんだよ。",
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
            "title": x["title"],
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
def draw_magic():
    # 10%でレア
    if random.random() < 0.10:
        item = random.choice(RARE_MAGIC)
        rarity = "SR"
    else:
        item = random.choice(MAGIC_POOL)
        rarity = "N"

    return {
        "id": f"log_{random.randint(10000,99999)}",
        "created_at": now_str(),
        "category": item["category"],
        "title": item["title"],
        "message": item["message"],
        "action": item["action"],
        "rarity": rarity,
        "luna": random.choice(LUNA_LINES),
        "favorite": False,
    }


# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🪄", layout="wide")
st.title("🪄 Day102：今日の小さな魔法")
st.caption("今日はどんな小さな魔法が効くか、1つ引いてみるアプリ。")

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
            file_name="day102_small_magic.csv",
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

left, right = st.columns([0.95, 1.05], gap="large")

with left:
    st.subheader("魔法を引く")

    if st.button("🪄 今日の小さな魔法を引く", type="primary"):
        result = draw_magic()
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
            st.success("✨ レア魔法 ✨")
        else:
            st.info("通常魔法")

        st.markdown(f"### {latest['title']}")
        st.write(f"カテゴリ：{latest['category']}")

        st.markdown("**今日のメッセージ**")
        st.write(latest["message"])

        st.markdown("**小さな行動**")
        st.success(latest["action"])

        st.markdown("**ルナのひとこと**")
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
            st.markdown(f"### {chosen['title']}")
            st.write(f"日時：{chosen['created_at']}")
            st.write(f"カテゴリ：{chosen['category']}")
            st.write(f"レア度：{chosen['rarity']}")
            st.write("**今日のメッセージ**")
            st.write(chosen["message"])
            st.write("**小さな行動**")
            st.success(chosen["action"])
            st.write("**ルナのひとこと**")
            st.info(chosen["luna"])
            st.write(f"お気に入り：{'⭐' if chosen.get('favorite') else '—'}")
