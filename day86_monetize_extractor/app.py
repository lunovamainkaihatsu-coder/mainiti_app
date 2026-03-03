import streamlit as st
import json
import os
import re
from datetime import datetime
import pandas as pd

APP_TITLE = "Day86：Monetize Extractor（収益化アイデア抽出）"

# 既定：Day85 Idea Vault が保存しているJSON（相対パス想定）
DEFAULT_VAULT_PATH = os.path.join("data", "idea_vault.json")


# ---------- helpers ----------
def load_vault(path: str) -> dict:
    if not os.path.exists(path):
        return {"ideas": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_str(x):
    return "" if x is None else str(x)


def keywords_hit(text: str, kws: list[str]) -> int:
    t = text.lower()
    return sum(1 for k in kws if k.lower() in t)


# ---------- monetization logic (rule-based) ----------
MONETIZE_TEMPLATES = [
    {
        "name": "デジタル商品（テンプレ/プロンプト/素材）",
        "when": ["テンプレ", "プロンプト", "素材", "台本", "チェック", "ルーチン", "スプレッド", "シート"],
        "models": ["買い切り（¥500〜¥2,980）", "バンドル販売（まとめ売り）"],
        "channels": ["Note（有料記事）", "BOOTH", "ココナラ（データ納品）"],
        "mvp": "テンプレ1枚＋使い方1ページ＋サンプル1つ",
        "copy": [
            "今日からそのまま使えるテンプレ付き",
            "迷いゼロで前に進める設計",
            "5分で成果が出る形に整えた"
        ]
    },
    {
        "name": "アプリ収益（広告/買い切り/サブスク）",
        "when": ["アプリ", "streamlit", "ツール", "記録", "管理", "ダッシュボード", "ランチャー"],
        "models": ["広告（Ad）", "買い切り（Pro版）", "サブスク（プレミアム）"],
        "channels": ["Streamlit Community Cloud（公開）", "GitHub（導線）", "Note（使い方記事）"],
        "mvp": "無料版：基本機能＋ログ保存／Pro：分析・エクスポート強化",
        "copy": [
            "使うだけで整う“自動化ツール”",
            "続く仕組みを最初から組み込み",
            "日々のデータが資産になる"
        ]
    },
    {
        "name": "鑑定・相談メニュー（ココナラ）",
        "when": ["占い", "タロット", "四柱推命", "鑑定", "相性", "スピ", "潜在意識", "引き寄せ"],
        "models": ["単発鑑定（¥1,000〜¥10,000）", "継続（週1/月額）"],
        "channels": ["ココナラ", "X/Note（集客）", "LINE/メルマガ（継続）"],
        "mvp": "鑑定テンプレ（質問→結果→行動3つ→最後の一言）を1セット作る",
        "copy": [
            "行動まで落とし込む“現実が動く鑑定”",
            "優しく、でも前に進める言葉",
            "今日から変えられる一歩を渡す"
        ]
    },
    {
        "name": "コンテンツ（Note/KDP/講座）",
        "when": ["note", "ブログ", "記事", "本", "KDP", "講座", "教材", "まとめ"],
        "models": ["有料Note（¥300〜¥1,500）", "KDP（¥250〜¥1,250）", "ミニ講座"],
        "channels": ["Note", "Kindle(KDP)", "X（集客）"],
        "mvp": "1テーマで“導入→手順→事例→まとめ”の2000字",
        "copy": [
            "初心者でも迷わない手順つき",
            "今日から真似できる具体例",
            "短いのに本質が入ってる"
        ]
    },
    {
        "name": "コミュニティ/メンバーシップ",
        "when": ["コミュニティ", "仲間", "継続", "毎日", "習慣", "チャレンジ"],
        "models": ["月額（¥500〜¥3,000）", "イベント/勉強会"],
        "channels": ["Discord", "Noteメンバーシップ", "X（募集）"],
        "mvp": "毎日お題＋週1振り返り＋テンプレ配布",
        "copy": [
            "一人じゃ続かないを終わらせる",
            "小さく積み上げる場",
            "今日の一歩が出る仕組み"
        ]
    },
]

BOOST = {
    "収益": 2,
    "アプリ": 2,
    "Note": 1,
    "ルナ": 1,
    "世界観": 1,
    "ゲーム": 1,
    "ツール": 1
}

RISK_WORDS = ["炎上", "誹謗", "違法", "無断", "著作権", "個人情報"]


def choose_template(idea_text: str, tags: list[str]):
    # 1) テキストのキーワード一致
    best = None
    best_score = -1
    for t in MONETIZE_TEMPLATES:
        s = keywords_hit(idea_text, t["when"])
        if s > best_score:
            best_score = s
            best = t

    # 2) タグブースト（軽く）
    tag_score = sum(BOOST.get(tag, 0) for tag in tags)
    return best, best_score, tag_score


def monetize_row(idea: dict):
    text = safe_str(idea.get("text"))
    tags = idea.get("tags") or []
    priority = int(idea.get("priority") or 3)
    done = bool(idea.get("done", False))

    tmpl, kw_score, tag_score = choose_template(text, tags)

    # 簡易リスク判定（表示だけ）
    risk = "低"
    if keywords_hit(text, RISK_WORDS) >= 1:
        risk = "注意"

    # 収益化スコア（0〜10っぽく）
    score = 0
    score += min(4, kw_score * 2)          # キーワード一致
    score += min(3, tag_score)             # タグ一致
    score += (priority - 1) * 0.75         # 優先度
    if done:
        score -= 2                         # 既にdoneは“次候補”から下げる
    score = max(0, min(10, round(score, 1)))

    return {
        "idea": text,
        "tags": ", ".join(tags),
        "priority": priority,
        "done": done,
        "template": tmpl["name"] if tmpl else "未判定",
        "score": score,
        "risk": risk,
        "models": " / ".join(tmpl["models"]) if tmpl else "",
        "channels": " / ".join(tmpl["channels"]) if tmpl else "",
        "mvp": tmpl["mvp"] if tmpl else "",
        "copy_1": tmpl["copy"][0] if tmpl else "",
        "copy_2": tmpl["copy"][1] if tmpl else "",
        "copy_3": tmpl["copy"][2] if tmpl else "",
    }


# ---------- UI ----------
st.set_page_config(page_title=APP_TITLE, page_icon="💰", layout="wide")
st.title("💰 Day86：Monetize Extractor（収益化アイデア抽出）")
st.caption("Idea Vaultのアイデアを“売れる形”に変換する。まずはルールベースで確実に動く版。")

with st.sidebar:
    st.subheader("📂 読み込むVault")
    vault_path = st.text_input("Vault JSON Path", value=DEFAULT_VAULT_PATH)
    st.caption("例：data/idea_vault.json（Day85の保存ファイル）")
    st.divider()
    st.subheader("出力")
    show_done = st.checkbox("doneも表示する", value=False)

vault = load_vault(vault_path)
ideas = vault.get("ideas", [])

if not ideas:
    st.warning("Vaultが空っぽか、パスが違うかも。Day85でアイデアを1つ保存してから来てね。")
    st.stop()

rows = [monetize_row(i) for i in ideas]
df = pd.DataFrame(rows)

if not show_done:
    df = df[df["done"] == False]

df = df.sort_values(["score", "priority"], ascending=[False, False])

col1, col2 = st.columns([1.2, 0.8], gap="large")

with col1:
    st.subheader("📌 収益化スコア上位")
    topn = st.slider("表示件数", 3, 30, 10)
    st.dataframe(df.head(topn), use_container_width=True, height=420)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ CSVダウンロード", data=csv, file_name="day86_monetize_extractor.csv", mime="text/csv")

with col2:
    st.subheader("🎯 次に売りに行く1件（おすすめ）")
    best = df.head(1)
    if best.empty:
        st.info("（done除外で候補がないよ）")
    else:
        r = best.iloc[0].to_dict()
        st.markdown(f"### {r['idea']}")
        st.markdown(f"- スコア：**{r['score']}** / リスク：**{r['risk']}**")
        st.markdown(f"- 型：**{r['template']}**")
        st.markdown(f"- 収益モデル：{r['models']}")
        st.markdown(f"- 導線：{r['channels']}")
        st.markdown(f"- MVP：{r['mvp']}")
        st.markdown("**売り文句案**")
        st.write(f"・{r['copy_1']}")
        st.write(f"・{r['copy_2']}")
        st.write(f"・{r['copy_3']}")

st.divider()
st.subheader("🔎 検索・フィルタ")
q = st.text_input("キーワード検索（idea/tags/template）")
min_score = st.slider("最低スコア", 0.0, 10.0, 5.0, 0.5)

filtered = df.copy()
filtered = filtered[filtered["score"] >= min_score]
if q.strip():
    qq = q.strip().lower()
    filtered = filtered[
        filtered["idea"].str.lower().str.contains(qq) |
        filtered["tags"].str.lower().str.contains(qq) |
        filtered["template"].str.lower().str.contains(qq)
    ]

st.dataframe(filtered, use_container_width=True, height=360)
