import streamlit as st
import random

st.title("🌀 変な文書メーカー・強化版")

st.write("5つの単語を入れてボタンを押すと、支離滅裂な文章が量産されます。")

# 5つの単語を入力
word1 = st.text_input("単語①")
word2 = st.text_input("単語②")
word3 = st.text_input("単語③")
word4 = st.text_input("単語④")
word5 = st.text_input("単語⑤")

words = [word1, word2, word3, word4, word5]

# 文体選択
style = st.selectbox(
    "文体を選んでね",
    ["おまかせ（ごちゃ混ぜ）", "昔話風", "SF風", "バトル風", "恋愛風"]
)

# 生成数
num_sentences = st.slider("生成する文章の数", 1, 5, 1)

# 文体ごとのテンプレ
templates_fairy = [
    "昔々、【{0}】の国に【{1}】という不思議なものがあった。そこへ【{2}】が現れ、世界を【{3}】するために【{4}】したという。",
    "その昔、【{0}】は人々を救うため、【{1}】と【{2}】を連れて、【{3}】を倒しに行きながら【{4}】した。",
    "とても古い時代、【{0}】の森で【{1}】が生まれた。だが【{2}】に奪われ、世界は【{3}】し、最後に【{4}】だけが残った。"
]

templates_sf = [
    "西暦2999年、【{0}】は【{1}】システムとして起動した。しかし【{2}】の暴走により、宇宙は【{3}】され、緊急プロトコルとして【{4}】が実行された。",
    "量子実験の失敗により、【{0}】と【{1}】が融合した。その結果、【{2}】は【{3}】空間に飛ばされ、そこで【{4}】ことになった。",
    "未知の惑星で発見された【{0}】は、【{1}】文明の遺産だった。解析を進めた【{2}】は、世界がすでに【{3}】されている事実を知り、最後に【{4}】と向き合う。"
]

templates_battle = [
    "突如現れた【{0}】は、【{1}】軍を率いて【{2}】と激突した。戦場は【{3}】と化し、その混乱の中で【{4}】が放たれた。",
    "最強と呼ばれた【{0}】は、【{1}】を武器に【{2}】へ挑んだ。しかし【{3}】の一撃で形勢は逆転し、最後に【{4}】が勝敗を分けた。",
    "世界を賭けた決戦で、【{0}】と【{1}】がぶつかり合う。観客として現れた【{2}】は、【{3}】の瞬間を見届け、そっと【{4}】した。"
]

templates_love = [
    "はじめて【{0}】に出会ったのは、【{1}】が降る日だった。隣に座っていた【{2}】が笑った瞬間、世界が【{3}】して、心の中で【{4}】と呟いた。",
    "ずっと秘密にしていた【{0}】への想いを、【{1}】の帰り道で打ち明けた。【{2}】は少し黙ってから、【{3}】目線で笑い、そっと【{4}】を返してくれた。",
    "失恋の痛みを抱えた【{0}】は、【{1}】カフェで【{2}】と出会う。会話を重ねるうちに、崩れた心は【{3}】し、最後に【{4}】が始まった。"
]

templates_chaos = [
    "気がつくと世界は【{0}】で埋め尽くされていた。人々は【{1}】を崇め、【{2}】を投げ捨て、最終的に全てが【{3}】して【{4}】になった。",
    "朝起きたら、枕元に【{0}】が落ちていた。それを拾った瞬間、【{1}】が鳴り響き、部屋の中で【{2}】が踊り出し、外では【{3}】が爆発し、最終的に【{4}】になった。",
    "昨日まで普通だった【{0}】が、突然【{1}】し始めた。誰も止められず、【{2}】は【{3}】となり、歴史には【{4}】として刻まれることになる。"
]

# まとめて扱う用
all_templates = (
    templates_fairy + templates_sf +
    templates_battle + templates_love +
    templates_chaos
)

def choose_templates(style_name):
    if style_name == "昔話風":
        return templates_fairy
    elif style_name == "SF風":
        return templates_sf
    elif style_name == "バトル風":
        return templates_battle
    elif style_name == "恋愛風":
        return templates_love
    else:
        # おまかせ（ごちゃ混ぜ）
        return all_templates

if st.button("変な文書を生成！"):
    if all(words):
        templates = choose_templates(style)
        st.subheader("生成結果")
        for i in range(num_sentences):
            shuffled = random.sample(words, len(words))
            temp = random.choice(templates)
            sentence = temp.format(*shuffled)
            st.markdown(f"{i+1}. {sentence}")
    else:
        st.warning("5つ全部ちゃんと入れてから押してね、ご主人。")
