from __future__ import annotations

import json
import random
import datetime as dt
from pathlib import Path

import streamlit as st


APP_TITLE = "👻 1分怪談ジェネレーター（Day55）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"


# -------------------------
# 保存/読込
# -------------------------
def load_history():
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(rows):
    HISTORY_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


# -------------------------
# 怪談生成（テンプレ合成）
# -------------------------
OPENINGS = [
    "それに気づいたのは、{time}のことだった。",
    "最初は気のせいだと思った。けれど、{time}に起きた出来事は違った。",
    "{time}。{place}にいた私は、妙な違和感を覚えた。",
]

SENSES = [
    "空気がひやりと沈み、音だけが遠くにあるみたいだった。",
    "生ぬるい風が首筋をなぞって、背中がぞわっとした。",
    "なぜか、そこだけ音が吸い込まれるように静かだった。",
]

SIGNS = [
    "視界の端で、白いものが揺れた。",
    "床が、きし…きし…と、誰かの重さで鳴った。",
    "スマホの画面が一瞬だけ真っ黒になり、知らない番号から通知が来た。",
    "背後のガラスに、私以外の影が映った。",
]

ESCALATE_1 = [
    "振り返っても、何もない。",
    "確かめようとしても、理由が見つからない。",
    "見間違いだと自分に言い聞かせた。",
]

ESCALATE_2 = [
    "でも、同じことがもう一度起きた。",
    "次は、もっとはっきり見えた。",
    "そして、耳元で小さく『…{keyword}…』と囁く声がした。",
]

CLIMAX_SOFT = [
    "気づいた瞬間、胸の奥が冷たくなった。——それは最初から、そこにいた。",
    "逃げるように帰ったのに、玄関の鍵が内側から回った気がした。",
    "その夜、鏡に映った私の後ろに、もう一人の“私”が立っていた。",
]

CLIMAX_HARD = [
    "帰ろうとしても足が動かない。床に、黒い指の跡が増えていく。",
    "目を閉じた瞬間、頬に触れる指の感触があった。冷たくて、湿っていた。",
    "ライトが消えた。暗闇の中で、呼吸だけが二つ分聞こえた。",
]

ENDING = [
    "翌朝、{place}の写真を見返したら、写ってはいけないものが写っていた。",
    "思い出したくないのに、{time}になると同じ匂いがする。",
    "今も、{place}の近くを通ると、背後で足音が増える。",
]

DISCLAIMER = "※これは創作（フィクション）です。怖さを楽しむための短編です。"


def choose_climax(level: int) -> str:
    if level <= 2:
        return random.choice(CLIMAX_SOFT)
    if level == 3:
        return random.choice(CLIMAX_SOFT + CLIMAX_HARD)
    return random.choice(CLIMAX_HARD)


def generate_kaidan(place: str, time_str: str, level: int, keyword: str) -> str:
    keyword = keyword.strip() or "ねえ"
    parts = [
        random.choice(OPENINGS).format(place=place, time=time_str),
        random.choice(SENSES),
        random.choice(SIGNS),
        random.choice(ESCALATE_1),
        random.choice(ESCALATE_2).format(keyword=keyword),
        choose_climax(level).format(place=place, time=time_str, keyword=keyword),
        random.choice(ENDING).format(place=place, time=time_str),
    ]

    # 怖さレベルで少しだけ文量調整
    if level >= 4:
        insert = random.choice([
            "それなのに、私の足元だけが妙に温かかった。",
            "誰かが私の名前を、正しい発音で呼んだ。",
            "影が一瞬だけ“笑った”気がした。",
        ])
        parts.insert(3, insert)

    return "\n".join(parts)


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("👻 1分怪談ジェネレーター")
st.caption("入力をもとに“それっぽい怪談”を即生成。投稿用にもどうぞ。")
st.info(DISCLAIMER)

history = load_history()

st.divider()

col1, col2 = st.columns(2)
with col1:
    place = st.text_input("場所", value="夜の廊下", placeholder="例：実家の階段、学校のトイレ、夜道")
with col2:
    time_str = st.selectbox("時間帯", ["深夜", "夜", "夕方", "明け方", "昼"], index=0)

level = st.slider("怖さレベル", 1, 5, 3)
keyword = st.text_input("キーワード（任意）", placeholder="例：名前／合言葉／口癖／地名…")

st.divider()

if st.button("生成する", use_container_width=True):
    story = generate_kaidan(place.strip() or "どこか", time_str, level, keyword)
    st.session_state["story"] = story

if "story" in st.session_state:
    st.subheader("📖 生成された怪談")
    st.text_area("コピペ用", st.session_state["story"], height=260)

    cA, cB = st.columns(2)
    with cA:
        if st.button("💾 履歴に保存", use_container_width=True):
            history.append({
                "saved_at": dt.datetime.now().isoformat(timespec="seconds"),
                "place": place,
                "time": time_str,
                "level": level,
                "keyword": keyword,
                "story": st.session_state["story"],
            })
            save_history(history)
            st.success("保存したよ。")
    with cB:
        if st.button("🧹 クリア", use_container_width=True):
            st.session_state.pop("story", None)
            st.rerun()

st.divider()

with st.expander("🗂 過去の怪談（最新10件）"):
    if not history:
        st.write("まだ保存がないよ。")
    else:
        for row in reversed(history[-10:]):
            st.markdown(f"**{row['saved_at']}｜{row['place']}｜{row['time']}｜Lv{row['level']}**")
            st.write(row["story"])
            st.write("---")
