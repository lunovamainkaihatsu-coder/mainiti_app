from __future__ import annotations

import json
import random
import datetime as dt
from pathlib import Path

import streamlit as st

APP_TITLE = "🌙 総合運夢診断ジェネレーター（Day62）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※これは創作的・心理的な解釈（フィクション含む）です。未来の保証や断定ではありません。"


# -------------------------
# 保存/読込
# -------------------------
def load_history():
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(rows):
    HISTORY_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


# -------------------------
# 総合運：ベースとなる夢シンボル
# （ここは“汎用”にして、各運勢カテゴリで読み替える）
# -------------------------
TOTAL_SIGNS = {
    "落ちる/崩れる": {
        "surface": [
            "前提が揺れる時期のサイン。『守りたいもの』がはっきりしてくる。",
            "計画の見直しや優先順位の再設定が必要という合図。",
        ],
        "deep": [
            "失敗恐怖というより、変化に適応する力が育っている可能性。",
            "“一度壊すことで整う”フェーズの入り口かも。",
        ],
        "hint": [
            "大きく変えるより、足場を整えると運が戻る。",
            "今日やることを減らすほど、回復と判断力が上がる。",
        ],
    },
    "追われる/逃げる": {
        "surface": [
            "プレッシャーや未処理タスクの象徴。抱えすぎ注意。",
            "焦りが強い時に出やすい夢。まず整理が必要。",
        ],
        "deep": [
            "本当は休みたいのに、休むことに罪悪感がある可能性。",
            "境界線（NOと言う力）を整える時期。",
        ],
        "hint": [
            "捨てる・延期するを1つ決めると運が上がる。",
            "まず“体力”を戻すと一気に状況が改善しやすい。",
        ],
    },
    "知らない場所/迷路": {
        "surface": [
            "方向性の模索、新しい段階への移行の象徴。",
            "全体像が見えない時期。小さく試すのが正解。",
        ],
        "deep": [
            "未知の才能や、新しい環境への興味が育っている可能性。",
            "“今の自分に合う居場所”を探しているサイン。",
        ],
        "hint": [
            "選択肢を増やすより、通路を減らす（絞る）。",
            "小さく試して当たりを見つけるのが最短ルート。",
        ],
    },
    "水/お風呂/雨": {
        "surface": [
            "浄化・回復・リセットの象徴。疲れを流したいサイン。",
            "感情が溜まっている時に出やすい夢。",
        ],
        "deep": [
            "心と体の回復がテーマ。整えるほど運が伸びる。",
            "過去のモヤモヤを手放す準備ができている可能性。",
        ],
        "hint": [
            "回復の行動が、そのまま運気アップになる。",
            "情報遮断・休息が最強の開運。",
        ],
    },
    "財布/お金/買い物": {
        "surface": [
            "お金・価値・安心の象徴。収支や管理意識が高まっている。",
            "“不足感”や“受け取り”がテーマになりやすい。",
        ],
        "deep": [
            "自己価値とお金が結びついている可能性。自分を低く見積もりすぎ注意。",
            "お金より“安心”を求めている心の動き。",
        ],
        "hint": [
            "固定費を1つ見直す or 稼ぐ行動を5分やる。",
            "受け取る器を整える（作品を出す/実績を積む）。",
        ],
    },
    "手をつなぐ/会話する": {
        "surface": [
            "つながり・信頼・コミュニケーションの象徴。",
            "関係性を深めたい気持ちが出ている可能性。",
        ],
        "deep": [
            "安心できる距離感を求めているサイン。無理は禁物。",
            "本音を言える関係がテーマになっている。",
        ],
        "hint": [
            "短い一言のやり取りが運を動かす。",
            "境界線を整えるほど、良い縁が残る。",
        ],
    },
    "遅刻/間に合わない": {
        "surface": [
            "焦り・責任感・締切圧の象徴。やること過多の可能性。",
            "計画が盛りすぎになっているサイン。",
        ],
        "deep": [
            "実力不足より余裕不足が原因かも。回復が先。",
            "完璧主義の解除がテーマ。",
        ],
        "hint": [
            "今日の優先を1つに絞ると流れが戻る。",
            "60点で出す＝運が回り始める。",
        ],
    },
    "病院/検査/薬": {
        "surface": [
            "点検・ケア・回復の象徴。整える意識が高まっている。",
            "体調や生活リズムの見直しタイミング。",
        ],
        "deep": [
            "休息や支援を“受け取る許可”が出始めている。",
            "心の疲れが体に影響しやすい時期かも。",
        ],
        "hint": [
            "睡眠・食事・水分の1つを上げるだけで運が変わる。",
            "不調が続くなら無理せず相談（医療/信頼できる人）。",
        ],
    },
}

EMOTIONS = ["嬉しい", "不安", "焦り", "怖い", "寂しい", "安心", "ワクワク", "怒り", "無感情"]
STATES = ["疲れてる", "挑戦中", "停滞ぎみ", "忙しい", "眠い", "メンタルが揺れる", "人疲れ", "整えたい"]


# -------------------------
# 各カテゴリの“翻訳フレーズ”テンプレ
# （同じ夢でも、運勢カテゴリ別に読み替える）
# -------------------------
def pick(lines):
    return random.choice(lines)


def build_total_result(sign_key: str, emotion: str, state: str, memo: str) -> str:
    base = TOTAL_SIGNS[sign_key]

    surface = pick(base["surface"])
    deep = pick(base["deep"])
    hint = pick(base["hint"])

    # 5運勢：それぞれの“見立て”を少しずつ変える
    money = pick([
        "収支の整理が吉。固定費を1つ見直すと流れが整う。",
        "稼ぐ行動を“5分だけ”やると金運が動き出す。",
        "受け取る器を整える（作品を出す/実績を積む）ほど安定する。",
        "衝動買いは一旦保留。24時間ルールが吉。",
    ])
    love = pick([
        "優しい一言が恋愛運を動かす。重い話は後でOK。",
        "距離感の調整が吉。無理しないほど良縁が残る。",
        "安心が最優先。自分を満たすほど関係が穏やかになる。",
        "本音は短く伝えると吉（責めない言い方）。",
    ])
    work = pick([
        "タスクは“3つ以内”に絞ると仕事運が上向く。",
        "60点で出す→改善で伸ばす、が最短ルート。",
        "整理（フォルダ/机/メモ）を1か所やると流れが良くなる。",
        "まず回復。体力が戻ると判断力が上がる。",
    ])
    health = pick([
        "睡眠・水分・入浴のどれかを上げると健康運が即回復しやすい。",
        "呼吸を整える（4秒吸って6秒吐く×5回）が吉。",
        "軽い散歩5分が回復のスイッチ。",
        "無理を減らすほど体が味方になる。",
    ])
    social = pick([
        "短い挨拶や一言が対人運を動かす。",
        "会う頻度/連絡頻度を整えると縁が良くなる。",
        "人疲れなら“回復時間”を先に確保する。",
        "NOと言う練習が、良い関係を残す。",
    ])

    aura = pick([
        "総合運は“気合”より“整える”で上がる。",
        "運の正体は、行動の再現性と回復の積み上げ。",
        "夢は未来予知じゃない。でも、心の方向は映す。",
        "小さく整えるほど、現実は急に動き出す。",
    ])

    one_action = pick([
        "✅ 今日の最小タスクを1つ完了する（5分でOK）",
        "✅ 机 or スマホの中を1か所だけ片づける",
        "✅ 入浴 or 温かい飲み物で体温を上げる",
        "✅ “やらないこと”を1つ決めて捨てる",
        "✅ 短い一言を誰かに送る（挨拶でもOK）",
    ])

    hint_memo = f"今回の夢メモ：『{memo.strip()}』\n" if memo.strip() else ""

    return (
        f"{hint_memo}"
        f"### 🌕 夢の総合メッセージ\n"
        f"- {surface}\n\n"
        f"### 🌑 深層メッセージ\n"
        f"- {deep}\n\n"
        f"### 🔔 感情×状態のヒント\n"
        f"- 感情：**{emotion}** ／ 状態：**{state}**\n"
        f"- {aura}\n"
        f"- {hint}\n\n"
        f"---\n"
        f"## 🎴 5運勢の見立て（短文）\n"
        f"**💰 金運**：{money}\n\n"
        f"**💗 恋愛運**：{love}\n\n"
        f"**🧠 仕事運**：{work}\n\n"
        f"**🧘‍♂️ 健康運**：{health}\n\n"
        f"**🤝 対人運**：{social}\n\n"
        f"---\n"
        f"### ✅ 今日の開運アクション（1つだけ）\n"
        f"- {one_action}\n\n"
        f"---\n"
        f"**ひとこと**：{pick(['今日は整える日でOK。', '小さく進めば運は動く。', '回復が最強の開運。', '出力を積めば現実が追いつく。'])}"
    )


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🌙 総合運夢診断ジェネレーター")
st.caption("夢を“総合運×心理”で読み解く。金運/恋愛/仕事/健康/対人をまとめて出す完結編！")
st.info(DISCLAIMER)

history = load_history()

st.divider()

col1, col2 = st.columns(2)
with col1:
    sign_key = st.selectbox("夢のシーン（選択）", list(TOTAL_SIGNS.keys()))
with col2:
    emotion = st.selectbox("感情（任意）", ["（未選択）"] + EMOTIONS)

state = st.selectbox("最近の状態（任意）", ["（未選択）"] + STATES)
memo = st.text_area("夢のメモ（任意）", height=100, placeholder="例：知らない場所で迷った／財布を落とした…など")

st.divider()

if st.button("診断する（総合）", use_container_width=True):
    e = emotion if emotion != "（未選択）" else random.choice(EMOTIONS)
    s = state if state != "（未選択）" else random.choice(STATES)
    result = build_total_result(sign_key, e, s, memo)
    st.session_state["result"] = result

if "result" in st.session_state:
    st.subheader("🪄 診断結果")
    st.markdown(st.session_state["result"])
    st.text_area("コピペ用（Markdown）", st.session_state["result"], height=260)

    cA, cB = st.columns(2)
    with cA:
        if st.button("💾 履歴に保存", use_container_width=True):
            history.append({
                "saved_at": dt.datetime.now().isoformat(timespec="seconds"),
                "sign": sign_key,
                "emotion": emotion,
                "state": state,
                "memo": memo.strip(),
                "result": st.session_state["result"],
            })
            save_history(history)
            st.success("保存したよ。")
    with cB:
        if st.button("🧹 クリア", use_container_width=True):
            st.session_state.pop("result", None)
            st.rerun()

st.divider()

with st.expander("🗂 過去の診断（最新10件）"):
    if not history:
        st.write("まだ保存がないよ。")
    else:
        for row in reversed(history[-10:]):
            st.markdown(f"**{row['saved_at']}｜{row['sign']}｜{row.get('emotion','')}｜{row.get('state','')}**")
            if row.get("memo"):
                st.caption(f"メモ：{row['memo']}")
            st.markdown(row["result"])
            st.write("---")
