import random
import textwrap
import streamlit as st


# ===== マスターデータ（ベース） =====

THEMES_BASE = [
    "学園もの", "現代日常", "和風ファンタジー", "中世ファンタジー",
    "サイバーパンク", "近未来SF", "ポストアポカリプス",
    "アイドルもの", "魔法少女／魔法少年", "バトルアクション",
    "スチームパンク", "都市伝説・オカルト", "ゆる日常コメディ",
]

SITUATIONS_BASE = [
    "放課後の屋上で夕焼けを眺めている",
    "雨上がりの路地裏で一人立ち尽くしている",
    "夏祭りの屋台の灯りに照らされている",
    "深夜のコンビニ前で友達を待っている",
    "図書館の窓際で本を読みふけっている",
    "星空の見える草原に寝転んでいる",
    "廃墟となった遊園地を探索している",
    "SF都市の高層ビル屋上で風に吹かれている",
    "神社の境内でお願い事をしている",
    "電車の車内でうつらうつら居眠りしている",
    "戦いの直後、傷だらけで立ち尽くしている",
    "ライブステージで観客に手を振っている",
]

GENDERS = ["女の子", "男の子", "中性的な子"]
AGE_IMPRESSIONS = [
    "10代前半くらい", "10代後半くらい", "20代前半くらい",
    "年齢不詳の雰囲気", "見た目は幼いが中身は大人っぽい",
]

HAIR_STYLES = [
    "ロングヘア", "セミロング", "ボブカット", "ショートヘア",
    "ツインテール", "ポニーテール", "お団子ヘア",
    "外ハネ気味", "ストレート", "ゆるふわウェーブ",
]
HAIR_COLORS = [
    "黒髪", "ダークブラウン", "明るいブラウン", "金髪",
    "銀髪", "赤みのあるブラウン", "ピンク系", "青系",
    "紫系", "ミントグリーン", "グラデーションカラー",
]
EYE_COLORS = [
    "黒い瞳", "茶色の瞳", "琥珀色の瞳", "エメラルドグリーンの瞳",
    "サファイアブルーの瞳", "紫がかった瞳", "金色の瞳",
]

SKIN_TONES = [
    "色白の肌", "健康的に日焼けした肌", "小麦色の肌",
    "やや褐色寄りの肌", "透けるように白い肌",
]

HEIGHTS = [
    "かなり低めの身長", "やや低めの身長", "平均的な身長",
    "やや高めの身長", "長身でモデル体型の身長",
]

BODY_TYPES = [
    "華奢な体型", "標準的な体型", "柔らかそうな体型",
    "スポーティーで引き締まった体型", "全体的にふわっとしたシルエット",
]

FACE_TYPES = [
    "つり目気味でクールな印象", "たれ目で優しい印象",
    "ぱっちりとした大きな瞳", "眠たそうな半目",
    "キリッとした目元", "ほんのり泣きぼくろがある顔立ち",
]

CLOTHES_SFW_BASE = [
    "制服スタイル（ブレザー）",
    "制服スタイル（セーラー服）",
    "私服のパーカーとジーンズ",
    "ふんわりしたワンピース",
    "ジャージ姿",
    "ゴシックロリータ風の服",
    "ストリート系ファッション",
    "和服／浴衣スタイル",
    "シンプルなシャツとスカート",
    "スーツスタイル",
]

CLOTHES_R18_EXTRA = [
    "露出多めのドレス",
    "体のラインが強調されるタイトな服",
    "少し攻めたデザインのランジェリー風衣装",
    "大胆なスリットの入ったチャイナドレス風衣装",
]

PERSONALITIES_BASE = [
    "明るくて人懐っこい性格",
    "クールで不器用なツンデレ気質",
    "おっとりマイペースな性格",
    "生真面目で融通がきかない性格",
    "感情表現が豊かな性格",
    "ミステリアスで何を考えているかわからない性格",
    "毒舌だが根は優しい性格",
]

FEATURES_SFW_BASE = [
    "右目だけ色の違うオッドアイ",
    "片方の耳にだけピアスをしている",
    "首元に小さなペンダントをつけている",
    "髪にリボンやヘアピンをつけている",
    "頬に小さな絆創膏を貼っている",
    "尻尾や獣耳のような特徴がある",
    "腕や足に包帯が巻かれている",
    "ヘッドホンを首にかけている",
]

FETISH_TAGS_R18 = [
    "メガネフェチっぽさがある",
    "絶対領域が強調されている",
    "首筋フェチ向けの雰囲気",
    "手フェチに刺さる指先の表現",
    "声フェチ向けの囁きそうな雰囲気",
    "年上好き／年下好きがにじむ態度",
    "S気質・M気質が感じられる仕草",
]

# ===== カラーパレット =====

COLOR_PALETTES = [
    {
        "name": "桜色ポップ",
        "colors": [
            ("背景", "#fff5f7"),
            ("メイン", "#f7a8c4"),
            ("サブ", "#ffcdd7"),
            ("アクセント", "#ff6b9c"),
        ],
    },
    {
        "name": "夜空ネオン",
        "colors": [
            ("背景", "#050816"),
            ("メイン", "#1f51ff"),
            ("サブ", "#7b2cff"),
            ("アクセント", "#00ffd1"),
        ],
    },
    {
        "name": "和風レトロ",
        "colors": [
            ("背景", "#fdf3e7"),
            ("メイン", "#c94c4c"),
            ("サブ", "#e0a96d"),
            ("アクセント", "#355c7d"),
        ],
    },
    {
        "name": "ダークファンタジー",
        "colors": [
            ("背景", "#16161a"),
            ("メイン", "#3f2b96"),
            ("サブ", "#a100f2"),
            ("アクセント", "#ff6b6b"),
        ],
    },
    {
        "name": "森のヒーリング",
        "colors": [
            ("背景", "#f0f7f4"),
            ("メイン", "#3f784c"),
            ("サブ", "#8fb996"),
            ("アクセント", "#f2c14f"),
        ],
    },
]


# ===== カスタムお題の管理 =====

# セッションで持つキー名
CUSTOM_DEFAULT = {
    "themes": [],
    "situations": [],
    "clothes_sfw": [],
    "personalities": [],
    "features_sfw": [],
}


def init_custom_state():
    if "custom_topics" not in st.session_state:
        st.session_state.custom_topics = CUSTOM_DEFAULT.copy()


def get_merged_lists():
    c = st.session_state.custom_topics

    themes = THEMES_BASE + c["themes"]
    situations = SITUATIONS_BASE + c["situations"]
    clothes_sfw = CLOTHES_SFW_BASE + c["clothes_sfw"]
    personalities = PERSONALITIES_BASE + c["personalities"]
    features_sfw = FEATURES_SFW_BASE + c["features_sfw"]

    return {
        "themes": themes,
        "situations": situations,
        "clothes_sfw": clothes_sfw,
        "personalities": personalities,
        "features_sfw": features_sfw,
    }


# ===== 生成ロジック =====

def generate_prompt(r18: bool, lists: dict) -> dict:
    theme = random.choice(lists["themes"])
    situation = random.choice(lists["situations"])
    gender = random.choice(GENDERS)
    age = random.choice(AGE_IMPRESSIONS)

    hair_style = random.choice(HAIR_STYLES)
    hair_color = random.choice(HAIR_COLORS)
    eye_color = random.choice(EYE_COLORS)
    skin = random.choice(SKIN_TONES)
    height = random.choice(HEIGHTS)
    body = random.choice(BODY_TYPES)
    face = random.choice(FACE_TYPES)

    clothes_list = lists["clothes_sfw"].copy()
    features_list = lists["features_sfw"].copy()
    extra_tags = []

    if r18:
        clothes_list = clothes_list + CLOTHES_R18_EXTRA
        features_list = features_list + FETISH_TAGS_R18
        extra_tags.append("大人向け・セクシー寄りのデザイン")

    clothes = random.choice(clothes_list)
    feature = random.choice(features_list)
    personality = random.choice(lists["personalities"])

    palette = random.choice(COLOR_PALETTES)

    return {
        "theme": theme,
        "situation": situation,
        "gender": gender,
        "age": age,
        "hair_style": hair_style,
        "hair_color": hair_color,
        "eye_color": eye_color,
        "skin": skin,
        "height": height,
        "body": body,
        "face": face,
        "clothes": clothes,
        "personality": personality,
        "feature": feature,
        "extra_tags": extra_tags,
        "palette": palette,
    }


def format_prompt_text(data: dict, r18: bool = False) -> str:
    lines = [
        f"■テーマ：{data['theme']}",
        f"■シチュエーション：{data['situation']}",
        "",
        f"■キャラクター：{data['gender']}（{data['age']}）",
        f"- 髪型：{data['hair_style']}／髪色：{data['hair_color']}",
        f"- 目：{data['eye_color']}",
        f"- 肌：{data['skin']}",
        f"- 身長イメージ：{data['height']}",
        f"- 体型：{data['body']}",
        f"- 顔立ち：{data['face']}",
        "",
        f"■服装：{data['clothes']}",
        f"■性格：{data['personality']}",
        f"■特徴：{data['feature']}",
    ]

    if data["extra_tags"]:
        lines.append(f"■追加タグ：{ '／'.join(data['extra_tags']) }")

    # カラーパレット情報
    lines.append("")
    lines.append(f"■カラーパレット：{data['palette']['name']}")
    for label, code in data["palette"]["colors"]:
        lines.append(f"- {label}: {code}")

    # 簡易プロンプト例（AIイラスト用テキストを意識）
    prompt_line = (
        f"{data['theme']}の世界観、{data['situation']}シーン。"
        f"{data['gender']}（{data['age']}）、{data['hair_color']}・{data['hair_style']}、"
        f"{data['eye_color']}、{data['skin']}、{data['height']}、{data['body']}。"
        f"{data['clothes']}。{data['personality']}。{data['feature']}。"
        f"カラーパレットは「{data['palette']['name']}」。"
    )
    if r18:
        prompt_line += "少し大人っぽく、セクシー寄りの雰囲気。"

    lines.append("")
    lines.append("■プロンプト例（AIイラスト用メモ）：")
    lines.append(textwrap.fill(prompt_line, width=60))

    return "\n".join(lines)


def show_palette_streamlit(palette: dict):
    """Streamlit上でカラーパレットを色付きボックスで表示"""
    st.markdown(f"**🎨 カラーパレット：{palette['name']}**")
    cols = st.columns(len(palette["colors"]))
    for col, (label, code) in zip(cols, palette["colors"]):
        with col:
            st.markdown(label)
            st.markdown(
                f"<div style='width:100%;height:40px;"
                f"border-radius:6px;border:1px solid #ccc;"
                f"background:{code};'></div>",
                unsafe_allow_html=True,
            )


# ===== Streamlit アプリ本体 =====

def main():
    st.set_page_config(
        page_title="イラストお題ジェネレーター",
        page_icon="🎨",
        layout="centered",
    )
    init_custom_state()

    st.title("🎨 イラストお題ジェネレーター")
    st.caption("今日描く一枚のネタをランダムで決めちゃおう！")

    with st.sidebar:
        st.subheader("設定")
        num = st.slider("生成するお題の数", 1, 5, 1)
        r18_mode = st.checkbox("R18モード（大人向け要素を少し追加）", value=False)

        st.info(
            "R18モードでは、服装や雰囲気・性癖タグなど "
            "『大人っぽい』『フェチ寄り』の要素が少しだけ増えます。\n"
            "※露骨な描写は含みません。"
        )

        # --- カスタムお題エリア ---
        with st.expander("✏ お題カスタム（任意）"):
            category_label = st.selectbox(
                "編集するカテゴリーを選択",
                [
                    "テーマ",
                    "シチュエーション",
                    "服装（SFW）",
                    "性格",
                    "特徴（SFW）",
                ],
            )

            key_map = {
                "テーマ": "themes",
                "シチュエーション": "situations",
                "服装（SFW）": "clothes_sfw",
                "性格": "personalities",
                "特徴（SFW）": "features_sfw",
            }
            key = key_map[category_label]

            current_lines = "\n".join(st.session_state.custom_topics[key])
            text = st.text_area(
                "1行につき1つずつ入力してください",
                value=current_lines,
                height=150,
            )

            if st.button("このカテゴリーを更新"):
                new_items = [
                    line.strip() for line in text.splitlines() if line.strip()
                ]
                st.session_state.custom_topics[key] = new_items
                st.success(f"{category_label} を更新しました！（{len(new_items)} 件）")

        generate = st.button("お題を生成する！")

    if generate:
        merged = get_merged_lists()

        for i in range(num):
            data = generate_prompt(r18=r18_mode, lists=merged)
            text = format_prompt_text(data, r18=r18_mode)

            st.markdown(f"---")
            st.markdown(f"### お題 {i+1}")
            show_palette_streamlit(data["palette"])
            st.code(text, language="markdown")
    else:
        st.write("左のサイドバーで設定して、「お題を生成する！」ボタンを押してね。")


if __name__ == "__main__":
    main()
