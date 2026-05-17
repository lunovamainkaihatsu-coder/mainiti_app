import streamlit as st
import datetime
import random
import hashlib
import os

# -------------------------
# 基本設定
# -------------------------
st.set_page_config(page_title="にゃんこ運勢＆相性＆図鑑", page_icon="🐾")
st.title("🐾 にゃんこ運勢 & 相性占い & 図鑑")


# -------------------------
# 画像パス
# -------------------------
IMAGE_PATHS = {
    "あかちゃんねこ": "images/あかちゃんねこ.png",
    "おじいちゃんねこ": "images/おじいちゃんねこ.png",
    "すやすやねこ": "images/すやすやねこ.png",
    "とけるねこ": "images/とけるねこ.png",
    "ねこしょうじょ": "images/ねこしょうじょ.png",
    "ねことじょせい": "images/ねことじょせい.png",
    "ねこまた": "images/ねこまた.png",
    "ねこみみしょうじょ": "images/ねこみみしょうじょ.png",
    "ぴじんねこ": "images/びじんねこ.png",
    "ほごされねこ": "images/ほごされねるこ.png",
    "もふもふねこ": "images/もふもふねこ.png",
    "ゆるきゃらふうねこ": "images/ゆるきゃらふうねこ.png",
}


# -------------------------
# 属性（相性判定用）
# -------------------------
CAT_ELEMENTS = {
    "あかちゃんねこ": "SUN",
    "おじいちゃんねこ": "CHILL",
    "すやすやねこ": "CHILL",
    "とけるねこ": "CHILL",
    "ねこしょうじょ": "STYLE",
    "ねことじょせい": "HEART",
    "ねこまた": "MYSTIC",
    "ねこみみしょうじょ": "ART",
    "びじんねこ": "SUN",
    "ほごされるねこ": "HEART",
    "もふもふねこ": "SUN",
    "ゆるきゃらふうねこ": "MYSTIC",
}

CAT_TYPES = list(CAT_ELEMENTS.keys())


# -------------------------
# 図鑑説明文
# -------------------------
NEKO_INFO = {
    "あかちゃんねこ": "はじめての世界にきょろきょろ。新しいことにわくわくしちゃう純粋さMAXのにゃんこ。",
    "おじいちゃんねこ": "ゆっくりのんびり。長生きの知恵と落ち着きを持つにゃんこ。",
    "すやすやねこ": "どこでもすやすや。寝て回復する睡眠マスター。",
    "とけるねこ": "ソファの上でぐにゃ〜。今日は休む日だよと全身で語るにゃんこ。",
    "ねこしょうじょ": "猫耳の付いた少女。かわいさと軽いミステリアスさを併せ持つタイプ。",
    "ねことじょせい": "猫を抱いている女性。優しさと穏やかさがにじむ存在。",
    "ねこまた": "尻尾が二つに分かれた、不思議パワーのにゃんこ。直感に強い。",
    "ねこみみしょうじょ": "甘え上手で元気いっぱいの猫耳少女タイプ。推し活と相性◎。",
    "びじんねこ": "街に紛れ込んだビジネスにゃんこ。都会でも意外とマイペースにやっている。",
    "ほごされるねこ": "いろいろあったけど、今は守られているにゃんこ。優しさがテーマ。",
    "もふもふねこ": "見た目からして癒しの塊。触りたくなるもふもふ。",
    "ゆるきゃらふうねこ": "ゆるキャラのような見た目と動きのにゃんこ。ほのぼの系。",
}


# -------------------------
# 運勢データ
# -------------------------
FORTUNES = {
    "あかちゃんねこ": [
        {
            "title": "はじまりキラキラ運",
            "message": "今日は“はじめて”にツキがある日。小さな一歩で世界が広がるよ。",
            "advice": "気になっていたものを一つだけ試してみて。",
            "lucky": "新しいノート",
        }
    ],
    "おじいちゃんねこ": [
        {
            "title": "ゆっくり味わい運",
            "message": "急がなくて大丈夫。ゆっくりが正解の日。",
            "advice": "5分早めに切り上げて休む時間を作ってみて。",
            "lucky": "温かいお茶",
        }
    ],
    "すやすやねこ": [
        {
            "title": "回復スリープ運",
            "message": "眠気は本物。しっかり休むと明日がラクに。",
            "advice": "スマホを10分だけ置いて、その分横になろう。",
            "lucky": "ふかふかの枕",
        }
    ],
    "とけるねこ": [
        {
            "title": "ぐにゃ〜っとリセット運",
            "message": "やる気が出ないのはメンテ時間の証。今日はゆるゆるでOK。",
            "advice": "ToDoは1つだけ。あとは日向ぼっこ気分で。",
            "lucky": "ぬるいお風呂",
        }
    ],
    "ねこしょうじょ": [
        {
            "title": "事情も含めてOK運",
            "message": "『ほんとは色々あるけど…』を笑いに変えられる日。",
            "advice": "もやもやを1行書いて『まぁしゃーない』を添えて。",
            "lucky": "かわいいスタンプ",
        }
    ],
    "ねことじょせい": [
        {
            "title": "現実と仲直り運",
            "message": "全部やらなくてOK。優先順位を決めれば十分えらい日。",
            "advice": "今日のTOP3だけ頑張って、残りは明日に任せよう。",
            "lucky": "ToDoリスト",
        }
    ],
    "ねこまた": [
        {
            "title": "スピアンテナびんびん運",
            "message": "直感が冴える日。ふとした気づきを逃さないで。",
            "advice": "印象に残った出来事を3つメモするだけでOK。",
            "lucky": "お守り",
        }
    ],
    "ねこみみしょうじょ": [
        {
            "title": "かわいい全開運",
            "message": "“かわいい”を出すほど運が味方する日。",
            "advice": "自分のかわいいポイントを一つ甘やかそう。",
            "lucky": "推しカラー小物",
        }
    ],
    "びじんねこ": [
        {
            "title": "街中サバイバル運",
            "message": "都会でも意外となんとかなる日。",
            "advice": "移動中に耳コンテンツを一つ入れておくと吉。",
            "lucky": "イヤホン",
        }
    ],
    "ほごされるねこ": [
        {
            "title": "安心ベース運",
            "message": "『頼っていい』を感じる日。安心がテーマ。",
            "advice": "弱音を一言だけ吐いてみよう。受け止めてもらえる。",
            "lucky": "やさしい飲み物",
        }
    ],
    "もふもふねこ": [
        {
            "title": "ぎゅっとハッピー運",
            "message": "もふ感で幸せが上がる日。触れるものが吉。",
            "advice": "クッションや毛布を抱きしめてみて。",
            "lucky": "もふもふ素材",
        }
    ],
    "ゆるきゃらふうねこ": [
        {
            "title": "しんしん集中運",
            "message": "静かに集中が続く日。派手さよりじわじわ前進。",
            "advice": "作業タイマーを1回だけセットしよう。",
            "lucky": "温かい飲み物",
        }
    ],
}


# -------------------------
# 相性テーブル
# -------------------------
ELEMENT_COMPAT = {
    ("SUN", "SUN"): {"rate": "◎", "comment": "ひなたぼっこ最強コンビ。明るい相性。"},
    ("SUN", "ART"): {"rate": "○", "comment": "元気×創造のにぎやかペア。"},
    ("SUN", "CHILL"): {"rate": "○", "comment": "動く側と休む側でバランス◎。"},
    ("SUN", "STYLE"): {"rate": "○", "comment": "華やかで相乗効果あり。"},
    ("SUN", "MYSTIC"): {"rate": "△", "comment": "ノリは違うが刺激的。"},
    ("SUN", "HEART"): {"rate": "◎", "comment": "優しさ×元気の安心コンビ。"},

    ("ART", "ART"): {"rate": "◎", "comment": "語り出したら止まらない創作沼ペア。"},
    ("ART", "CHILL"): {"rate": "○", "comment": "ゆる×創作の最強落書きタイム。"},
    ("ART", "STYLE"): {"rate": "◎", "comment": "おしゃれで絵になる組み合わせ。"},
    ("ART", "MYSTIC"): {"rate": "○", "comment": "世界観が合えば爆発しそう。"},
    ("ART", "HEART"): {"rate": "○", "comment": "ほっこり癒される創作空間。"},

    ("CHILL", "CHILL"): {"rate": "○", "comment": "だらだら注意。でも幸福度高い。"},
    ("CHILL", "STYLE"): {"rate": "○", "comment": "おしゃれ×癒しのバランス良い関係。"},
    ("CHILL", "MYSTIC"): {"rate": "○", "comment": "静かに深い話が始まりがち。"},
    ("CHILL", "HEART"): {"rate": "◎", "comment": "癒しと優しさで最強安心空間。"},

    ("STYLE", "STYLE"): {"rate": "◎", "comment": "美意識が共鳴するペア。"},
    ("STYLE", "MYSTIC"): {"rate": "○", "comment": "ミステリアスな雰囲気に。"},
    ("STYLE", "HEART"): {"rate": "○", "comment": "お互いを引き立てる関係。"},

    ("MYSTIC", "MYSTIC"): {"rate": "◎", "comment": "不思議な次元で通じ合う2匹。"},
    ("MYSTIC", "HEART"): {"rate": "○", "comment": "スピを優しく受け止めてくれる。"},

    ("HEART", "HEART"): {"rate": "◎", "comment": "優しさで満たされた空間ができる。"},
}


def get_element(cat):
    return CAT_ELEMENTS.get(cat, "HEART")


def get_compat(cat1, cat2):
    e1 = get_element(cat1)
    e2 = get_element(cat2)
    if (e1, e2) in ELEMENT_COMPAT:
        return ELEMENT_COMPAT[(e1, e2)]
    if (e2, e1) in ELEMENT_COMPAT:
        return ELEMENT_COMPAT[(e2, e1)]
    return {"rate": "○", "comment": "未知の関係。ゆっくり距離が縮まるタイプ。"}


# -------------------------
# タブ構成
# -------------------------
tab1, tab2, tab3 = st.tabs(["今日の運勢（ランダム）", "相性ガチャ", "にゃんこ図鑑"])


# -------------------------
# タブ1：今日の運勢（全部ランダム排出）
# -------------------------
with tab1:
    st.subheader("🐱 今日のにゃんこ運勢（ランダム排出）")

    name = st.text_input("にゃんこの名前（省略可）")

    if st.button("今日のにゃんこを引く！", key="fortune"):
        cat_name = name.strip() if name.strip() else "にゃんこ"
        today = datetime.date.today().isoformat()

        # 名前＋日付でシード固定 → 1日1にゃんこ
        seed = int(hashlib.md5(f"{today}-{cat_name}".encode()).hexdigest(), 16)
        random.seed(seed)

        # ねこ種類もランダム
        cat_type = random.choice(CAT_TYPES)
        fortune_list = FORTUNES.get(cat_type)
        image_path = IMAGE_PATHS.get(cat_type)

        if image_path and os.path.exists(image_path):
            st.image(image_path, use_container_width=True)

        st.subheader(f"{cat_name} に今日現れたにゃんこは…「{cat_type}」！")

        if fortune_list:
            f = random.choice(fortune_list)
            st.markdown(f"### 🐾 {f['title']}")
            st.write(f["message"])
            st.markdown("#### 🌸 おすすめの過ごし方")
            st.write(f["advice"])
            st.markdown("#### 🎁 ラッキーアイテム")
            st.write(f["lucky"])
        else:
            st.write("今日はのんびりしてOKの日。ゆっくりしよう。")


# -------------------------
# タブ2：相性ガチャ（2匹ともランダム）
# -------------------------
with tab2:
    st.subheader("💘 にゃんこ相性ガチャ")

    if st.button("2匹のにゃんこを引く！", key="compat"):
        today = datetime.date.today().isoformat()
        seed = int(hashlib.md5(f"compat-{today}".encode()).hexdigest(), 16)
        random.seed(seed)

        c1 = random.choice(CAT_TYPES)
        c2 = random.choice(CAT_TYPES)

        result = get_compat(c1, c2)

        col_a, col_b = st.columns(2)

        with col_a:
            p1 = IMAGE_PATHS.get(c1)
            if p1 and os.path.exists(p1):
                st.image(p1, use_container_width=True)
            st.markdown(f"### 1匹目：{c1}")

        with col_b:
            p2 = IMAGE_PATHS.get(c2)
            if p2 and os.path.exists(p2):
                st.image(p2, use_container_width=True)
            st.markdown(f"### 2匹目：{c2}")

        st.markdown("---")
        st.markdown(f"## 💞 相性：{result['rate']}")
        st.write(result["comment"])


# -------------------------
# タブ3：図鑑
# -------------------------
with tab3:
    st.subheader("📖 にゃんこ図鑑")

    for ct in CAT_TYPES:
        st.markdown("---")
        cols = st.columns([1, 2])

        with cols[0]:
            p = IMAGE_PATHS.get(ct)
            if p and os.path.exists(p):
                st.image(p, use_container_width=True)

        with cols[1]:
            st.markdown(f"### {ct}")
            st.write(NEKO_INFO.get(ct, "このにゃんこの説明は今後追加予定。"))

            elem = get_element(ct)
            elem_label = {
                "SUN": "🌞 明るさ・元気タイプ",
                "CHILL": "💤 ゆるゆる休息タイプ",
                "ART": "🎨 クリエイティブタイプ",
                "STYLE": "👗 おしゃれタイプ",
                "MYSTIC": "🌌 不思議タイプ",
                "HEART": "💗 やさしさタイプ",
            }.get(elem, "🐾 ふしぎタイプ")

            st.caption(f"属性：{elem_label}")
