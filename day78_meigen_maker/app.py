import random
import streamlit as st

st.set_page_config(page_title="名言メーカー", layout="centered")

st.title("🗣️ 名言メーカー")
st.caption("ボタンを押すだけ。ヒーローっぽい名言が降ってくる。")

# -----------------------------
# パーツ（好きに増やしてOK）
# -----------------------------
subject = [
    "正義", "覚悟", "勇気", "信念", "友情",
    "努力", "挑戦", "希望", "未来", "闇",
    "勝利", "自分", "仲間", "心", "運命"
]

verb = [
    "切り開く", "照らす", "守り抜く", "貫く", "乗り越える",
    "燃やす", "変える", "導く", "打ち破る", "超えていく"
]

ending = [
    "それがヒーローだ。",
    "迷うな、進め。",
    "立ち止まるな。",
    "最後に笑うのは、覚悟を決めたやつだ。",
    "負けたって、終わりじゃない。",
    "怖いなら、なおさら前へ。",
    "信じた道を、疑うな。",
    "闇が深いほど、光は強い。",
    "守るべきものがあるなら、強くなれる。",
    "今日の一歩が、未来になる。"
]

spice = [
    "", "", "",  # 空を多めにして“たまに付く”感じ
    "――",
    "今ここで。",
    "そして、",
    "だからこそ。",
    "忘れるな、"
]


def make_quote():
    s = random.choice(subject)
    v = random.choice(verb)
    e = random.choice(ending)
    p = random.choice(spice)
    # たまに二段構えにする
    if random.random() < 0.25:
        s2 = random.choice(subject)
        v2 = random.choice(verb)
        return f"{p}{s}は{s2}を{v2}。\n{s}は{v}。{e}"
    return f"{p}{s}は{v}。{e}"


# -----------------------------
# UI
# -----------------------------
if "quote" not in st.session_state:
    st.session_state.quote = make_quote()

st.divider()

st.markdown("## 🌟 今日の名言")
st.markdown(f"### {st.session_state.quote}")

st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🎲 生成！", use_container_width=True):
        st.session_state.quote = make_quote()
        st.rerun()
with c2:
    if st.button("📋 コピー用", use_container_width=True):
        st.code(st.session_state.quote)
with c3:
    if st.button("🔥 必殺技も生成", use_container_width=True):
        # Day77風の簡易必殺技（ついで機能）
        pre = ["天翔", "紅蓮", "漆黒", "雷鳴", "蒼炎", "銀河", "閃光", "覇王", "神速", "終焉"]
        mid = ["爆裂", "斬撃", "衝撃", "旋風", "流星", "龍撃", "烈火", "轟雷", "零式", "究極"]
        suf = ["ブレイカー", "インパクト", "クラッシュ", "スラッシュ", "ストライク", "バースト", "フィニッシュ"]
        st.session_state.quote = f"必殺技：{random.choice(pre)}{random.choice(mid)}{random.choice(suf)}！！"
        st.rerun()

st.divider()
st.caption("🌙 いい名言は、心のOSを強化する。ご主人、今日も前へ。")
