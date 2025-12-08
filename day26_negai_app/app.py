import streamlit as st
import time
import random

# ==============================
# 基本設定
# ==============================
st.set_page_config(
    page_title="17秒×4 願望フォーカスルーム",
    layout="centered",
)

# カスタムCSS（円形タイマー用）
st.markdown(
    """
    <style>
    .title-center {
        text-align: center;
        font-weight: bold;
        font-size: 28px;
        margin-bottom: 0.5rem;
    }
    .subtitle-center {
        text-align: center;
        font-size: 16px;
        color: #666666;
        margin-bottom: 1.5rem;
    }
    .circle-wrapper {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    .circle {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .circle-inner {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background-color: #ffffff;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        font-weight: bold;
    }
    .step-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 12px;
        background-color: #eee;
        margin-bottom: 0.25rem;
    }
    .step-title {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 0.25rem;
    }
    .small-note {
        font-size: 12px;
        color: #777;
    }
    .footer-note {
        font-size: 11px;
        color: #999;
        text-align: center;
        margin-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
# セッション状態の初期化
# ==============================
if "step" not in st.session_state:
    st.session_state.step = 1  # 1〜4、5で完了状態扱い
if "wish_text" not in st.session_state:
    st.session_state.wish_text = ""
if "theme" not in st.session_state:
    st.session_state.theme = "お金・豊かさ"
if "future_message" not in st.session_state:
    st.session_state.future_message = ""
if "finished" not in st.session_state:
    st.session_state.finished = False

# ==============================
# タイトル
# ==============================
st.markdown('<div class="title-center">17秒×4 願望フォーカスルーム</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-center">68秒だけ、未来の自分に波動を合わせるための小さな儀式。</div>',
    unsafe_allow_html=True,
)

# ==============================
# 願いごと入力エリア
# ==============================
with st.expander("📝 まずは今日フォーカスする願いを決めよう", expanded=True):
    st.session_state.theme = st.selectbox(
        "今日のテーマ",
        [
            "お金・豊かさ",
            "仕事・ライフワーク",
            "恋愛・パートナーシップ",
            "健康・美容",
            "自己成長・学び",
            "家族・人間関係",
            "その他",
        ],
        index=[
            "お金・豊かさ",
            "仕事・ライフワーク",
            "恋愛・パートナーシップ",
            "健康・美容",
            "自己成長・学び",
            "家族・人間関係",
            "その他",
        ].index(st.session_state.theme),
    )

    st.session_state.wish_text = st.text_area(
        "今日、17秒×4でフォーカスする「叶えたい未来」を1つだけ書いてみてね",
        value=st.session_state.wish_text,
        height=80,
        placeholder="例）2026年末までに、LUNAPOCKETで月100万円を安定して稼いでいる",
    )

    st.markdown(
        '<span class="small-note">※ できるだけ「もう叶っている前提」で書くと、波動がそろいやすいよ。</span>',
        unsafe_allow_html=True,
    )

# リセットボタン
cols_reset = st.columns([1, 1, 1])
with cols_reset[2]:
    if st.button("🔁 やり直す（ステップをリセット）"):
        st.session_state.step = 1
        st.session_state.future_message = ""
        st.session_state.finished = False
        st.toast("ステップをリセットしたよ。また最初の17秒から一緒にやろうね。")

st.divider()

# 願いが未入力なら注意
if not st.session_state.wish_text.strip():
    st.info("願いごとがまだ書かれてないみたい。上の欄に、今日フォーカスする願いを1つだけ書いてね。")
    st.stop()

# ==============================
# ステップ説明（4段階）
# ==============================
STEP_TEXT = {
    1: {
        "label": "STEP 1 / イメージを「ぼんやり」流す17秒",
        "guide": "ふわっとでいいから、願いが叶った状態を映画みたいに流してみよう。細かく考えすぎなくてOK。",
        "keyword": "映像に慣れる時間",
    },
    2: {
        "label": "STEP 2 / 感情を「じんわり」感じる17秒",
        "guide": "その未来の自分が感じているであろう嬉しさ・安心・誇らしさを、胸のあたりで味わってみて。",
        "keyword": "感情を強める時間",
    },
    3: {
        "label": "STEP 3 / 感謝を「先取り」する17秒",
        "guide": "その未来がもう起きている前提で、「叶ってくれてありがとう」と心の中で何度か唱えてみよう。",
        "keyword": "感謝を灯す時間",
    },
    4: {
        "label": "STEP 4 / 宇宙に「任せる」17秒",
        "guide": "どう叶うかは一旦手放して、『なるようになる、でもきっとうまくいく』と信頼して、力を抜いてみよう。",
        "keyword": "手放しの時間",
    },
}

# ==============================
# 円形タイマー描画用関数
# ==============================
def render_circle_timer(remaining_sec: float, total_sec: int = 17):
    """円形のカウントダウンタイマーを描画する（CSS＋conic-gradient）"""
    remaining_sec = max(0.0, remaining_sec)
    percent = (total_sec - remaining_sec) / total_sec
    percent = min(max(percent, 0.0), 1.0)
    degree = int(percent * 360)

    circle_html = f"""
    <div class="circle-wrapper">
        <div class="circle" style="background: conic-gradient(#4CAF50 {degree}deg, #E0E0E0 0deg);">
            <div class="circle-inner">
                {int(remaining_sec)}秒
            </div>
        </div>
    </div>
    """
    st.markdown(circle_html, unsafe_allow_html=True)

# ==============================
# 未来ルナのメッセージ生成
# ==============================
def generate_future_message(wish_text: str, theme: str) -> str:
    base_templates = [
        "「{wish}」っていう願い、未来のご主人にとってはもう『当たり前の景色』になってるよ。",
        "焦って動き回るよりも、今日みたいに【波動をそろえる時間】を持つことが、一番の近道なんだよ。",
        "ちゃんと感じきれた68秒は、行動の質をじわじわ変えていくからね。ご主人はもう、スタートを切ってる。",
        "途中で落ち込む日があっても大丈夫。未来のご主人は、その全部込みで『よくここまで来たな』って笑ってるよ。",
        "ご主人が思ってる以上に、宇宙もアタイも、ちゃんと味方だからね。",
    ]

    theme_tail = {
        "お金・豊かさ": "お金は、ご主人の喜びと好奇心についてくる“エネルギーの流れ”みたいなもの。楽しむことを、遠慮しないでね。",
        "仕事・ライフワーク": "仕事は『自分をすり減らす場』じゃなくて、『自分の才能を試して育てるステージ』。少しずつ、そっち側に寄っていくよ。",
        "恋愛・パートナーシップ": "ご主人が自分を大切にするほど、周りとの関係もほどけていくからね。まずは自分の心に、優しくしてあげて。",
        "健康・美容": "体は、魂の“お家”みたいなもの。ちょっとずつでも、ご主人の体が喜ぶ選択を足していこうね。",
        "自己成長・学び": "インプットも休息も、どっちも成長の一部。『止まったように見える日』にも、ちゃんと発酵は進んでるよ。",
        "家族・人間関係": "完璧な家族なんてどこにもないからこそ、ご主人の小さな優しさが、ちゃんと光ってるよ。",
        "その他": "ご主人の“変なこだわり”や“マニアックな夢”こそ、未来の世界を面白くするタネなんだよ。",
    }

    template = random.choice(base_templates)
    wish_short = wish_text.strip()
    if len(wish_short) > 40:
        wish_short = wish_short[:37] + "…"

    first_line = template.format(wish=wish_short)
    second_line = theme_tail.get(theme, "")

    return first_line + "\n\n" + second_line

# ==============================
# メインのステップ表示
# ==============================

if st.session_state.step <= 4:
    step_data = STEP_TEXT[st.session_state.step]

    st.markdown(f"<div class='step-badge'>{step_data['label']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='step-title'>{step_data['keyword']}</div>", unsafe_allow_html=True)
    st.write(step_data["guide"])

    st.markdown(
        "<span class='small-note'>※ 好きなBGMや環境音があれば、別アプリで流しながらやってもOKだよ。</span>",
        unsafe_allow_html=True,
    )

    st.divider()

    # カウントダウンエリア
    timer_placeholder_text = st.empty()
    timer_placeholder_circle = st.empty()

    start_button = st.button(f"▶ この17秒をスタート（STEP {st.session_state.step}）")

    if start_button:
        total_sec = 17
        start_time = time.time()

        for _ in range(total_sec * 10):  # 0.1秒ごとに更新（約17秒）
            elapsed = time.time() - start_time
            remaining = total_sec - elapsed
            if remaining <= 0:
                remaining = 0

            # テキスト表示
            timer_placeholder_text.info("目を閉じて、いまのステップのイメージと感情だけに集中してみよう。")

            # 円形タイマー
            with timer_placeholder_circle:
                render_circle_timer(remaining_sec=remaining, total_sec=total_sec)

            if remaining <= 0:
                break

            time.sleep(0.1)

        st.success(f"STEP {st.session_state.step}：17秒おつかれさま。")

        # 次のステップへ
        st.session_state.step += 1

        # 画面を更新
        st.rerun()

else:
    # ==============================
    # 全ステップ完了後の画面
    # ==============================
    if not st.session_state.finished:
        st.session_state.future_message = generate_future_message(
            st.session_state.wish_text,
            st.session_state.theme,
        )
        st.session_state.finished = True

    st.success("✨ 68秒のフォーカスタイム完了！")

    st.markdown("## 🔮 未来ルナからの一言メッセージ")
    st.write(st.session_state.future_message)

    st.markdown("### 🧭 今日のご主人への小さな宿題")
    st.markdown(
        "- さっきイメージした未来に近づくために、**今日1つだけ具体的な行動** を選んでみてね。\n"
        "  - 例：5分だけリサーチする / 1行だけコードを書く / 1件だけ営業のメモを見直す など\n"
        "- 大きな一歩じゃなくていいから、『いまの自分でもできる一歩』を選ぶことがポイントだよ。"
    )

    if st.button("🔁 もう一度、別の願いでやってみる"):
        st.session_state.step = 1
        st.session_state.finished = False
        st.session_state.future_message = ""
        st.toast("もう一回、最初から一緒にやろうね。")

st.markdown(
    "<div class='footer-note'>※ このアプリは、ご主人の「引き寄せの練習部屋」だよ。うまく集中できない日があっても、それも含めて大丈夫。</div>",
    unsafe_allow_html=True,
)
