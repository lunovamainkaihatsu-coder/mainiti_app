import random
import streamlit as st

st.set_page_config(page_title="ヒーロー生成機", layout="centered")

st.title("🦸 ヒーロー生成機")
st.caption("世界に一人だけのヒーローを生成せよ。")


# -----------------------------
# データ
# -----------------------------

names1 = [
    "シャドウ", "ブレイズ", "サンダー", "ゼロ",
    "ネオ", "ダーク", "ライト", "フェニックス",
    "クロノ", "アーク", "ルミナス"
]

names2 = [
    "ブレイカー", "ナイト", "セイバー", "ストライカー",
    "ファング", "ランサー", "ウォリアー", "ジャッジ",
    "レイ", "ブレード"
]

types = [
    "🔥 熱血型",
    "🧠 クール頭脳型",
    "👑 俺様型",
    "🥺 成長型",
    "😈 ダークヒーロー型"
]

elements = [
    "🔥 炎",
    "⚡ 雷",
    "❄️ 氷",
    "🌑 闇",
    "✨ 光",
    "🌪 風",
    "🌍 大地"
]

prefix = ["天翔", "紅蓮", "漆黒", "雷鳴", "神速", "銀河"]
middle = ["爆裂", "斬撃", "衝撃", "龍撃", "轟雷", "究極"]
suffix = ["ブレイカー", "クラッシュ", "ストライク", "フィニッシュ", "バースト"]

subjects = ["正義", "覚悟", "勇気", "信念", "希望", "運命"]
verbs = ["切り開く", "守り抜く", "貫く", "超える", "変える"]
endings = ["それがヒーローだ。", "迷うな、進め。", "立ち止まるな。", "未来は変えられる。"]

ranks = ["C", "B", "A", "S", "SS", "SSS"]


# -----------------------------
# 生成関数
# -----------------------------

def make_name():
    return random.choice(names1) + random.choice(names2)

def make_skill():
    return random.choice(prefix) + random.choice(middle) + random.choice(suffix)

def make_quote():
    return random.choice(subjects) + "は" + random.choice(verbs) + "。" + random.choice(endings)

def make_hero():
    return {
        "name": make_name(),
        "type": random.choice(types),
        "element": random.choice(elements),
        "skill": make_skill(),
        "quote": make_quote(),
        "rank": random.choice(ranks)
    }


# -----------------------------
# UI
# -----------------------------

if "hero" not in st.session_state:
    st.session_state.hero = make_hero()

hero = st.session_state.hero

st.divider()

st.header(f"🦸 {hero['name']}")

st.write(f"属性：{hero['element']}")
st.write(f"タイプ：{hero['type']}")
st.write(f"ランク：⭐ {hero['rank']}")

st.divider()

st.subheader("💥 必殺技")
st.success(hero["skill"])

st.subheader("🗣 名言")
st.info(hero["quote"])

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🎲 新しいヒーロー生成", use_container_width=True):
        st.session_state.hero = make_hero()
        st.rerun()

with col2:
    if st.button("📋 コピー用表示", use_container_width=True):
        text = f"""
名前：{hero['name']}
属性：{hero['element']}
タイプ：{hero['type']}
ランク：{hero['rank']}
必殺技：{hero['skill']}
名言：{hero['quote']}
"""
        st.code(text)

st.divider()
st.caption("🌙 ヒーローは、いつも心の中にいる。")
