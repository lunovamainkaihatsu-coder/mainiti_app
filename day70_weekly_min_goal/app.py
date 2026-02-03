from __future__ import annotations

import json
import random
from datetime import datetime, date
from pathlib import Path

import streamlit as st

APP_TITLE = "🗓 週の最小目標AI（Day70）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※これはタスク整理のための提案です。体調優先。ゼロの日があってもOK。"


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
# 候補（週版）
# -------------------------
GOALS = {
    "開発（アプリ/コード）": [
        "新しいDayを1本だけ完成させる",
        "既存アプリを1本だけ改善してPushする",
        "UIだけ整える（見出し/余白/ボタン）を1回やる",
        "次の企画を3つ考えてメモする",
        "READMEを1本ぶん整える",
    ],
    "発信（Note/X/ブログ）": [
        "投稿を1本だけ出す（短文でOK）",
        "下書きを1本だけ作る（公開しなくてOK）",
        "1週間のまとめ記事の骨子だけ作る",
        "過去アプリ紹介を1本書く",
        "タイトル案を10個だけ出す",
    ],
    "学習（勉強/資格）": [
        "問題を3問だけ解く（合計でOK）",
        "1章だけ読む（途中まででもOK）",
        "復習メモを1ページだけ作る",
        "苦手テーマを1つだけ洗い出す",
    ],
    "生活（家/体）": [
        "部屋の1エリアだけ片づける（机/棚など）",
        "散歩を1回だけする（5分でもOK）",
        "睡眠を1日だけ“守る日”にする",
        "食事を1回だけ整える（汁物/野菜）",
    ],
    "メンタル（整える）": [
        "不安を書き出す時間を1回だけ取る（5分）",
        "スマホ断ち10分を1回やる",
        "自分を褒めるを週に1回だけやる",
        "『やらないこと』を1つ決める",
    ],
}

ENERGY_WEEK = {
    "守り週（とにかく回復）": [
        "『休む』を週の最小目標にする",
        "病院/手続き/生活の維持を最優先にする",
        "“外に出る”を1回だけでOKにする",
    ],
    "ゆる週（少し戻す）": [
        "1回だけやる（曜日は決めない）",
        "準備だけ1回する",
        "短時間で終わる形にする",
    ],
    "通常週（進める）": [
        "小さく1本仕上げる",
        "1つ改善して記録を残す",
        "週末に軽くまとめる",
    ],
    "攻め週（伸ばす）": [
        "“完成”を週に1回作る",
        "投稿と開発を1回ずつやる",
        "次週の段取りまで作る",
    ],
}

LUNA_LINES = [
    "週は長い。最小目標があるだけで勝ち。",
    "“これだけ”があると、迷いが消える。",
    "週の終わりに、ちゃんと自信が残るよ。",
    "小さく積む人が、結局いちばん強い。",
    "体調優先でOK。最小目標は逃げない。",
]


def week_id(today: date) -> str:
    # ISO週番号（例：2026-W06）
    y, w, _ = today.isocalendar()
    return f"{y}-W{w:02d}"


def pick_week_goal(domain: str, energy: str, notes: str) -> dict:
    if energy == "守り週（とにかく回復）":
        goal = random.choice(ENERGY_WEEK[energy])
    else:
        base = random.choice(GOALS[domain])
        modifier = random.choice(ENERGY_WEEK[energy])
        goal = f"{base}（{modifier}）"

    line = random.choice(LUNA_LINES)
    note_line = f"メモ：『{notes.strip()}』\n" if notes.strip() else ""
    return {"goal": goal, "line": line, "note_line": note_line}


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🗓 週の最小目標AI")
st.caption("今週はこれ“だけ”やればOK。週の迷いを消すアプリ。")
st.info(DISCLAIMER)

history = load_history()

st.divider()

today = date.today()
wid = week_id(today)
st.markdown(f"**今週：{wid}**")

col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("週の軸", list(GOALS.keys()))
with col2:
    energy = st.selectbox("週のエネルギー", list(ENERGY_WEEK.keys()))

notes = st.text_area("今週の状況メモ（任意）", height=90, placeholder="例：忙しい／回復優先／投稿を戻したい…")

st.divider()

if st.button("今週の最小目標を決める", use_container_width=True):
    r = pick_week_goal(domain, energy, notes)
    st.session_state["result"] = r

if "result" in st.session_state:
    r = st.session_state["result"]
    st.subheader("✅ 今週の最小目標")
    if r["note_line"]:
        st.caption(r["note_line"])
    st.markdown(f"### {r['goal']}")
    st.markdown(f"🌙 **ルナ**：{r['line']}")

    copy_text = f"今週：{wid}\n{r['note_line']}週の最小目標：{r['goal']}\n\nルナ：{r['line']}"
    st.text_area("コピペ用", copy_text, height=180)

    cA, cB = st.columns(2)
    with cA:
        if st.button("💾 履歴に保存", use_container_width=True):
            history.append({
                "time": datetime.now().isoformat(timespec="seconds"),
                "week": wid,
                "domain": domain,
                "energy": energy,
                "notes": notes.strip(),
                "goal": r["goal"],
                "line": r["line"],
            })
            save_history(history)
            st.success("保存したよ。")
    with cB:
        if st.button("🧹 クリア", use_container_width=True):
            st.session_state.pop("result", None)
            st.rerun()

st.divider()

with st.expander("🗂 履歴（最新10件）"):
    if not history:
        st.write("まだ履歴がないよ。")
    else:
        for row in reversed(history[-10:]):
            st.markdown(f"**{row['time']}｜{row.get('week','')}｜{row['domain']}｜{row['energy']}**")
            if row.get("notes"):
                st.caption(f"メモ：{row['notes']}")
            st.markdown(f"✅ {row['goal']}")
            st.caption(f"ルナ：{row['line']}")
            st.write("---")
