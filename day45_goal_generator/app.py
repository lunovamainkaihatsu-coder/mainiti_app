# app.py
from __future__ import annotations

import datetime as dt
import json
import random
from pathlib import Path

import streamlit as st

APP_TITLE = "来年目標ジェネレーター（Day45）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "next_year_goal.json"

YEAR = dt.date.today().year + 1

RESULTS = {
    ("しんどかった", "余白", "ゆっくり"): {
        "theme": "余白を最優先に生きる",
        "rules": [
            "無理な日は休んでいい",
            "できたことだけを見る",
            "比較しない",
        ],
        "message": "まずは回復。それが一番の前進だよ。",
    },
    ("しんどかった", "安心", "ふつう"): {
        "theme": "安心できる日を増やす",
        "rules": [
            "予定を詰めすぎない",
            "一人の時間を守る",
            "小さな楽しみを毎日に",
        ],
        "message": "守ることは、弱さじゃない。",
    },
    ("まあまあ", "成長", "ふつう"): {
        "theme": "小さく成長を積み重ねる",
        "rules": [
            "完璧を目指さない",
            "続けることを評価する",
            "月に1つ形にする",
        ],
        "message": "十分できてる。あとは積むだけ。",
    },
    ("よくやった", "成長", "速め"): {
        "theme": "楽しみながら突き抜ける",
        "rules": [
            "作ったら出す",
            "迷ったらGO",
            "勢いを信じる",
        ],
        "message": "今年の自分なら、いける。",
    },
}

DEFAULT = {
    "theme": "自分を大切にしながら前に進む",
    "rules": [
        "無理しない",
        "比べない",
        "やめる勇気を持つ",
    ],
    "message": "この目標は、ちゃんとあなた向け。",
}


def save_result(result: dict):
    DATA_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)
st.caption(f"{YEAR}年を、やさしく始めるために。")

st.subheader("🧭 3つだけ答えて")

q1 = st.radio("今年の自分は？", ["しんどかった", "まあまあ", "よくやった"])
q2 = st.radio("来年ほしいのは？", ["余白", "成長", "安心"])
q3 = st.radio("来年のペースは？", ["ゆっくり", "ふつう", "速め"])

if st.button("✨ 来年の目標を生成する", use_container_width=True):
    key = (q1, q2, q3)
    result = RESULTS.get(key, DEFAULT)
    result_out = {
        "year": YEAR,
        "answers": {"this_year": q1, "want": q2, "pace": q3},
        **result,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    save_result(result_out)

    st.success(f"🎯 {YEAR}年のテーマ")
    st.markdown(f"## 「{result_out['theme']}」")

    st.markdown("### 行動指針")
    for r in result_out["rules"]:
        st.write(f"- {r}")

    st.info(result_out["message"])

    st.caption("※ この目標は変えなくていい。思い出すだけでOK。")

if DATA_PATH.exists():
    with st.expander("📦 保存された目標"):
        st.json(json.loads(DATA_PATH.read_text(encoding='utf-8')))
