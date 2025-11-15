import random
from pathlib import Path

import streamlit as st
from PIL import Image

# ===========================
#  基本設定
# ===========================
st.set_page_config(
    page_title="今日だけのルナ占いミニ",
    page_icon="🔮",
    layout="centered"
)

# ===========================
#  カスタムCSS
# ===========================
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #1b1b2f, #162447);
        color: #f5f5f5;
    }
    .main {
        background-color: rgba(0, 0, 0, 0);
    }
    .card-box {
        padding: 18px 20px;
        border-radius: 16px;
        background: rgba(0, 0, 0, 0.32);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .title-text {
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle-text {
        font-size: 14px;
        text-align: center;
        opacity: 0.8;
        margin-top: 4px;
        margin-bottom: 24px;
    }
    .fortune-title {
        font-size: 22px;
        font-weight: 600;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 6px;
    }
    .fortune-tag {
        font-size: 13px;
        text-align: center;
        opacity: 0.8;
        margin-bottom: 12px;
    }
    .fortune-message {
        font-size: 15px;
        line-height: 1.6;
        margin-top: 12px;
    }
    .small-note {
        font-size: 11px;
        opacity: 0.7;
        text-align: center;
        margin-top: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===========================
#  フォルダ設定
# ===========================
TAROT_DIR = Path("assets") / "tarot"

if "card" not in st.session_state:
    st.session_state.card = None
if "rev" not in st.session_state:
    st.session_state.rev = False

# ===========================
#  カード意味辞書（日本語ファイル名対応）
# ===========================
MEANINGS = {
    "愚者": {
        "name": "愚者 / The Fool",
        "upright": "自由・冒険・新しいスタート。ご主人の『やってみたい』を大事にして◎",
        "reversed": "衝動・未熟・無計画。今日は少しだけ慎重さをプラスすると吉。"
    },
    "魔術師": {
        "name": "魔術師 / The Magician",
        "upright": "創造・才能の発揮。新しい挑戦の最適日！",
        "reversed": "準備不足・迷い。情報整理に時間を使ってみて。"
    },
    "女教皇": {
        "name": "女教皇 / The High Priestess",
        "upright": "直感と冷静さが冴える日。勉強運◎",
        "reversed": "考えすぎ・神経質。60点で良いから進めてOK。"
    },
    "女帝": {
        "name": "女帝 / The Empress",
        "upright": "豊かさ・癒し・愛情運アップ。美味しいもの吉。",
        "reversed": "怠惰・過保護。メリハリを意識すると運気回復。"
    },
    "皇帝": {
        "name": "皇帝 / The Emperor",
        "upright": "決断・強さ・主導権。自分で未来を作る日。",
        "reversed": "頑固・支配的。柔軟な視点が運気の鍵。"
    },
    "法王": {
        "name": "法王 / The Hierophant",
        "upright": "助言・伝統・学び。信頼できる人の意見が力になる。",
        "reversed": "形式に縛られる。自分のやり方で進んでOK。"
    },
    "恋人": {
        "name": "恋人 / The Lovers",
        "upright": "選択・情熱・つながり。愛情運・SNS運アップ。",
        "reversed": "優柔不断。小さな選択から決めていくと◎。"
    },
    "戦車": {
        "name": "戦車 / The Chariot",
        "upright": "勝利・行動力。勢いに乗ってGO！",
        "reversed": "暴走・空回り。焦らずペースを整えて。"
    },
    "力": {
        "name": "力 / Strength",
        "upright": "内なる力・優しさ・克服。心が安定して強い日。",
        "reversed": "自信喪失。まずは休息で回復を。"
    },
    "隠者": {
        "name": "隠者 / The Hermit",
        "upright": "内省・探求。静かに答えが見える日。",
        "reversed": "孤立感。人と少し話すだけで気が軽くなるよ。"
    },
    "運命の輪": {
        "name": "運命の輪 / Wheel of Fortune",
        "upright": "好転・タイミング到来。流れが味方する！",
        "reversed": "停滞。無理に動かず、整える日に。"
    },
    "正義": {
        "name": "正義 / Justice",
        "upright": "バランス・判断力。冷静に選べば吉。",
        "reversed": "不公平感。焦って決めないようにね。"
    },
    "吊られた男": {
        "name": "吊られた男 / The Hanged Man",
        "upright": "忍耐・別視点。突破口が見えはじめる。",
        "reversed": "無駄な我慢。手放せるものは手放して。"
    },
    "死神": {
        "name": "死神 / Death",
        "upright": "終わりと再生。不要なものをやめる好機。",
        "reversed": "変化の停滞。小さな行動で流れを動かして。"
    },
    "節制": {
        "name": "節制 / Temperance",
        "upright": "調和・回復。無理しないペースが成功へ。",
        "reversed": "不均衡。休息＋リセットが必要。"
    },
    "悪魔": {
        "name": "悪魔 / The Devil",
        "upright": "誘惑・欲望。ほどほどに楽しむならOK！",
        "reversed": "解放・回復。悪習から抜け出すチャンス。"
    },
    "塔": {
        "name": "塔 / The Tower",
        "upright": "崩壊・衝撃。実は必要な変化の前触れ。",
        "reversed": "回避・小さな修正。壊れる前に整えて◎。"
    },
    "星": {
        "name": "星 / The Star",
        "upright": "希望・癒し。未来への光が見える時。",
        "reversed": "理想疲れ。ハードルを下げてOK。"
    },
    "月": {
        "name": "月 / The Moon",
        "upright": "不安・直感。焦らず様子見が吉。",
        "reversed": "霧が晴れる。誤解や不安が解消へ。"
    },
    "太陽": {
        "name": "太陽 / The Sun",
        "upright": "成功・活力。娘ちゃん・奥さんとの時間吉！",
        "reversed": "空回り。まず休んでリズムを戻そう。"
    },
    "審判": {
        "name": "審判 / Judgement",
        "upright": "再スタート・復活。やり直しが成功する。",
        "reversed": "迷い。過去を手放す勇気を持って。"
    },
    "世界": {
        "name": "世界 / The World",
        "upright": "完成・達成。一区切りの成功が舞い込む！",
        "reversed": "未完了。あと一歩だけ、丁寧に仕上げて。"
    },
}

DEFAULT = {
    "name": "謎のカード",
    "upright": "このカードは、ご主人への静かな励ましかも。",
    "reversed": "今日は焦らず、自分のペースでいいよ。"
}

# ===========================
#  ファイル名 → 意味
# ===========================
def get_card_meaning(stem: str):
    name = stem.replace("tarot_", "").replace(".png", "")
    return MEANINGS.get(name, DEFAULT)


# ===========================
#  UIヘッダー
# ===========================
st.markdown('<p class="title-text">🔮 今日だけのルナ占いミニ 🔮</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">1日1回、ご主人のためにタロットを一枚引くよ。</p>', unsafe_allow_html=True)

# ===========================
#  カード一覧取得
# ===========================
cards = sorted(TAROT_DIR.glob("*.png"))
if not cards:
    st.error("カード画像が見つからないよ！  assets/tarot に .png を入れてね。")
    st.stop()

# ===========================
#  ボタン
# ===========================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🌙 今日の1枚を引く", type="primary", use_container_width=True):
        st.session_state.card = random.choice(cards)
        st.session_state.rev = random.choice([True, False])

# ===========================
#  結果表示
# ===========================
st.markdown("<div class='card-box'>", unsafe_allow_html=True)

if st.session_state.card:
    img = Image.open(st.session_state.card)
    if st.session_state.rev:
        img = img.rotate(180, expand=True)

    st.image(img)

    stem = st.session_state.card.stem
    data = get_card_meaning(stem)

    pos = "逆位置" if st.session_state.rev else "正位置"

    st.markdown(f"<p class='fortune-title'>{data['name']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='fortune-tag'>（{pos}）</p>", unsafe_allow_html=True)

    msg = data["reversed"] if st.session_state.rev else data["upright"]
    st.markdown(f"<div class='fortune-message'>ルナからのひとこと：<br>{msg}</div>", unsafe_allow_html=True)

else:
    st.write("ボタンを押すと、ご主人にぴったりなカードが1枚だけ出てくるよ。")

st.markdown(
    "<p class='small-note'>※エンタメ用だよ。気に入った部分だけ、そっと拾ってね。</p>",
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)
