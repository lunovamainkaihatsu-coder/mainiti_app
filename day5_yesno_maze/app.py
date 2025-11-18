import streamlit as st

st.set_page_config(
    page_title="YES/NO迷宮 - 3分心理ゲーム",
    page_icon="🌀",
)

st.title("🌀 YES/NO迷宮")
st.caption("3分で遊べる、ルナ式YES/NO心理ゲーム")

st.write(
    "あなたは、目を覚ますと見知らぬ部屋にいました。"
    "いくつかの選択肢を **YES / NO** で選んでいくと、"
    "最後にルナがあなたの『迷宮タイプ』を診断します。"
)

# ===== 迷宮の構造定義 =====
# node_type: "question" or "result"
nodes = {
    "start": {
        "node_type": "question",
        "text": "薄暗い部屋。扉がひとつだけあります。\n\n扉の向こうから、かすかな光が漏れている…\n\n扉を開けてみますか？",
        "yes_next": "corridor",
        "no_next": "stay_room",
    },
    "corridor": {
        "node_type": "question",
        "text": "扉の先は長い廊下。壁には古い絵がいくつも並んでいます。\n\nそのうちの一枚が、なぜかとても気になる…\n\n立ち止まって、その絵をじっくり観察しますか？",
        "yes_next": "picture",
        "no_next": "run_ahead",
    },
    "stay_room": {
        "node_type": "question",
        "text": (
            "あなたは部屋にとどまることにしました。\n\n"
            "しばらくすると、天井から小さな光の粒が降りてきて、"
            "部屋全体がやわらかく照らされ始めます。\n\n"
            "ここは危険ではなさそう…\n\n"
            "それでも、やっぱり外の世界を目指しますか？"
        ),
        "yes_next": "slow_exit",
        "no_next": "safe_haven",
    },
    "picture": {
        "node_type": "question",
        "text": (
            "絵の中には、どこか自分に似た人物が描かれていました。\n\n"
            "その人物は、迷宮から抜け出そうと手を伸ばしています。\n\n"
            "あなたも迷宮から抜け出すために、"
            "思い切って『絵に触れてみる』ことにしますか？"
        ),
        "yes_next": "resonant_soul",
        "no_next": "observer",
    },
    "run_ahead": {
        "node_type": "question",
        "text": (
            "あなたは立ち止まらず、一気に廊下を駆け抜けることにしました。\n\n"
            "角を曲がると、出口らしき扉と、"
            "『もっと奥へ』と書かれた階段があります。\n\n"
            "リスクを取って、階段を下りてみますか？"
        ),
        "yes_next": "deep_diver",
        "no_next": "quick_exit",
    },
    "slow_exit": {
        "node_type": "question",
        "text": (
            "あなたは慎重に廊下へと出ます。\n\n"
            "途中、小さな窓から外の景色が見えました。\n\n"
            "ここで一息ついて、景色を眺めながら、"
            "自分のこれからについて少し考えてみますか？"
        ),
        "yes_next": "reflector",
        "no_next": "quiet_walker",
    },

    # ===== 結果ノード =====
    "safe_haven": {
        "node_type": "result",
        "title": "安全基地の守護者タイプ",
        "description": (
            "危ない橋を無理に渡らず、今ある場所を整えようとするタイプ。\n"
            "あなたは、いきなり大きく動くよりも、"
            "『安心できる場所』を大事にしてから一歩を踏み出したい人です。\n\n"
            "🔍 アドバイス：\n"
            "- まずは小さな行動を“部屋の模様替え”のように整えていくと◎\n"
            "- 完璧じゃなくていいから、安心できるルーティンをひとつ作ってみて。\n"
        ),
        "keyword": "安心・土台・マイペース",
    },
    "resonant_soul": {
        "node_type": "result",
        "title": "共鳴する魂の探求者タイプ",
        "description": (
            "『これは自分ごとだ』と感じた瞬間に、"
            "一気に飛び込んでいけるタイプ。\n"
            "あなたは、ただの正解よりも、"
            "自分の心が震える選択を大事にする人です。\n\n"
            "🔍 アドバイス：\n"
            "- 心が動いた瞬間をメモしておこう。\n"
            "- “なんとなく気になる”を追いかけると、"
            "大きな転機につながりやすい時期です。\n"
        ),
        "keyword": "共鳴・情熱・没頭",
    },
    "observer": {
        "node_type": "result",
        "title": "静かな観察者タイプ",
        "description": (
            "あえて踏み込みすぎず、全体を俯瞰してから動くタイプ。\n"
            "あなたは、周りの流れや空気を読む力が高い人です。\n\n"
            "🔍 アドバイス：\n"
            "- 見ているだけで終わらせず、"
            "“一つだけ試す行動”をセットにしてみて。\n"
            "- まずは低リスクな実験から始めると、"
            "安心して前に進みやすくなります。\n"
        ),
        "keyword": "俯瞰・冷静・分析",
    },
    "deep_diver": {
        "node_type": "result",
        "title": "深堀りダイバータイプ",
        "description": (
            "興味をもった分野には、どこまでも潜っていけるタイプ。\n"
            "あなたは、一度決めたことに対して粘り強く取り組める人です。\n\n"
            "🔍 アドバイス：\n"
            "- 深く潜るテーマを“今はこれ！”と一つに絞ると◎\n"
            "- 途中で迷ったときは、『最初にワクワクした瞬間』を思い出してみて。\n"
        ),
        "keyword": "集中・継続・情熱",
    },
    "quick_exit": {
        "node_type": "result",
        "title": "スピード脱出ランナータイプ",
        "description": (
            "チャンスや出口を見つけたら、素早く行動に移せるタイプ。\n"
            "あなたは、考えすぎて止まるより、とりあえず動いてみてから考える人です。\n\n"
            "🔍 アドバイス：\n"
            "- 走りながら、たまに振り返る時間も作るとバランス◎\n"
            "- “やってみてから微調整”のスタイルは、"
            "創作や起業とも相性バツグンです。\n"
        ),
        "keyword": "行動・瞬発力・チャレンジ",
    },
    "reflector": {
        "node_type": "result",
        "title": "内省する旅人タイプ",
        "description": (
            "景色を眺めながら、自分の今と未来をつなげて考えられるタイプ。\n"
            "あなたは、感情と状況をセットで見つめる『内省力』の高い人です。\n\n"
            "🔍 アドバイス：\n"
            "- 日記やメモアプリで、“今日感じたこと”を一言でも残してみて。\n"
            "- 内側の声を拾うほど、次の一歩がクリアになっていきます。\n"
        ),
        "keyword": "内省・感性・成長",
    },
    "quiet_walker": {
        "node_type": "result",
        "title": "静かに進むウォーカータイプ",
        "description": (
            "大きなドラマよりも、静かで確かな一歩一歩を好むタイプ。\n"
            "あなたは、人知れずコツコツ積み上げていける人です。\n\n"
            "🔍 アドバイス：\n"
            "- 毎日5分だけでも、『自分のための時間』を決めてみて。\n"
            "- 目立たなくても、その一歩一歩が未来の大きなジャンプの助走になります。\n"
        ),
        "keyword": "継続・安定・静かな強さ",
    },
}

# ===== セッション状態の初期化 =====
if "current_node" not in st.session_state:
    st.session_state.current_node = "start"
if "history" not in st.session_state:
    st.session_state.history = []  # (question_text, answer_str) のリスト

current_id = st.session_state.current_node
current_node = nodes[current_id]

st.divider()

# ===== 質問ノードの表示 =====
if current_node["node_type"] == "question":
    st.markdown(f"### ❓ 質問")
    st.write(current_node["text"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ YES", use_container_width=True):
            st.session_state.history.append((current_node["text"], "YES"))
            st.session_state.current_node = current_node["yes_next"]
            st.rerun()

    with col2:
        if st.button("❌ NO", use_container_width=True):
            st.session_state.history.append((current_node["text"], "NO"))
            st.session_state.current_node = current_node["no_next"]
            st.rerun()

else:
    # ===== 結果ノードの表示 =====
    st.markdown("### 🎉 迷宮からのメッセージ")

    st.subheader(f"『{current_node['title']}』")
    st.write(current_node["description"])

    st.markdown(f"**キーワード：** `{current_node['keyword']}`")

    st.divider()
    st.markdown("### 🔁 これまでの選択")

    if len(st.session_state.history) == 0:
        st.write("今回の結果は、最初の直感から決まりました。")
    else:
        for i, (q_text, ans) in enumerate(st.session_state.history, start=1):
            with st.expander(f"Q{i}：あなたの答え → {ans}"):
                st.write(q_text)

    st.divider()
    if st.button("もう一度、迷宮に挑戦する 🔁", use_container_width=True):
        st.session_state.current_node = "start"
        st.session_state.history = []
        st.rerun()

st.caption("※ このゲームは創作心理テストです。診断結果はあくまで“目安”として楽しんでね。")
