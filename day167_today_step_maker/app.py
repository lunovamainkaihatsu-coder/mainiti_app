import streamlit as st
import pandas as pd
import random
from datetime import datetime
from pathlib import Path

# =========================
# 基本設定
# =========================

st.set_page_config(
    page_title="今日の一歩メーカー",
    page_icon="👣",
    layout="centered"
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

LOG_FILE = DATA_DIR / "step_log.csv"

# =========================
# データ
# =========================

MISSIONS = {
    "お金": {
        "低い": [
            "財布の中を整理する",
            "不要なサブスクがないか1つ確認する",
            "ココナラの商品説明を5分だけ見直す",
            "Noteの有料記事ネタを1つメモする",
        ],
        "普通": [
            "Noteの記事案を3つ出す",
            "ココナラの出品文を1か所改善する",
            "家計の支出を1項目だけ見直す",
            "収益化できそうなアプリ案を1つ考える",
        ],
        "高い": [
            "Noteを1記事書く",
            "ココナラ出品を1つ改善する",
            "収益化アプリの機能を1つ追加する",
            "販売できそうな商品案を10個出す",
        ],
    },
    "健康": {
        "低い": [
            "水を1杯飲む",
            "首と肩を1分回す",
            "深呼吸を10回する",
            "今日は早めに寝る準備をする",
        ],
        "普通": [
            "散歩を10分する",
            "スクワットを30回する",
            "ストレッチを5分する",
            "プロテインかヨーグルトを摂る",
        ],
        "高い": [
            "筋トレを1セットやる",
            "散歩を20分する",
            "ストレッチと筋トレを両方やる",
            "今日の食事を記録する",
        ],
    },
    "AI・勉強": {
        "低い": [
            "AI記事のタイトルだけ考える",
            "Pythonコードを5分だけ眺める",
            "本を3ページ読む",
            "気になったAI用語を1つ調べる",
        ],
        "普通": [
            "Pythonを15分触る",
            "AIについてNoteの見出しを作る",
            "本を10ページ読む",
            "アプリの改善点を3つ書く",
        ],
        "高い": [
            "アプリに1機能追加する",
            "Noteを1記事書く",
            "Pythonを30分学習する",
            "AIアプリ案を5個出す",
        ],
    },
    "家族": {
        "低い": [
            "娘に一言やさしく声をかける",
            "妻にありがとうを1回言う",
            "家の中を1か所だけ片付ける",
            "イライラしたら一度離れて深呼吸する",
        ],
        "普通": [
            "娘と5分遊ぶ",
            "洗い物か片付けを1つやる",
            "妻の話を途中で遮らずに聞く",
            "家族のために小さな用事を1つ済ませる",
        ],
        "高い": [
            "娘としっかり遊ぶ時間を作る",
            "家事を1つ多めにやる",
            "妻の負担を1つ減らす",
            "家族時間を意識してスマホを置く",
        ],
    },
    "趣味": {
        "低い": [
            "好きな作品を5分だけ見る",
            "イラストの資料を1枚集める",
            "ゲーム案を1つメモする",
            "好きなキャラを1人思い出す",
        ],
        "普通": [
            "イラストを10分模写する",
            "ゲーム案を3つ書く",
            "好きな作品から学べることを1つメモする",
            "創作キャラの設定を1つ足す",
        ],
        "高い": [
            "イラスト練習を30分する",
            "ゲーム企画を1ページ書く",
            "キャラ設定を深掘りする",
            "作品アイデアを10個出す",
        ],
    },
}

LUNA_MESSAGES = [
    "ご主人、今日は一歩だけでも十分です♪",
    "小さな行動も、未来のご主人を助けてくれますよ。",
    "完璧じゃなくて大丈夫。動いた時点で勝ちです♪",
    "今日は今日のペースでいきましょう。",
    "ご主人なら大丈夫。まずは軽く始めましょう♪",
    "積み重ねは、ちゃんと力になりますよ。",
]

# =========================
# 関数
# =========================

def save_log(categories, motivation, missions):
    now = datetime.now()
    row = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "categories": "、".join(categories),
        "motivation": motivation,
        "missions": " / ".join(missions),
    }

    if LOG_FILE.exists():
        df = pd.read_csv(LOG_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")


# =========================
# 画面
# =========================

st.title("👣 今日の一歩メーカー")
st.caption("何をやればいいかわからない日に、今日の小さな一歩を決めるアプリ")

st.divider()

categories = st.multiselect(
    "今日、少し進めたいこと",
    ["お金", "健康", "AI・勉強", "家族", "趣味"],
    default=["AI・勉強"]
)

motivation = st.radio(
    "今日のやる気",
    ["低い", "普通", "高い"],
    horizontal=True,
    index=1
)

mission_count = st.slider(
    "出すミッション数",
    min_value=1,
    max_value=5,
    value=3
)

st.divider()

if st.button("今日の一歩を決める", use_container_width=True):
    if not categories:
        st.warning("まずは進めたいことを1つ選んでね。")
    else:
        all_candidates = []

        for category in categories:
            all_candidates.extend(MISSIONS[category][motivation])

        selected = random.sample(
            all_candidates,
            k=min(mission_count, len(all_candidates))
        )

        luna_message = random.choice(LUNA_MESSAGES)

        st.subheader("🌟 今日のミッション")

        for i, mission in enumerate(selected, start=1):
            st.success(f"{i}. {mission}")

        st.info(f"🌙 ルナのひとこと：{luna_message}")

        save_log(categories, motivation, selected)

st.divider()

st.subheader("📚 これまでの一歩ログ")

if LOG_FILE.exists:
    try:
        log_df = pd.read_csv(LOG_FILE)
        st.dataframe(log_df.tail(10), use_container_width=True)
    except Exception:
        st.write("ログはまだありません。")
else:
    st.write("まだ記録はありません。")
