from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_TITLE = "🌿 今日の回復アクションAI（Day66）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※これは一般的なセルフケア提案です。強い不調や痛みが続く場合は医療機関へ。"


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
# 回復アクション辞書
# -------------------------
ACTIONS = {
    "精神（モヤモヤ/不安/焦り）": {
        "micro": [
            "紙に“今気になってること”を3つ書いて、今日はそのうち1つだけでOKにする",
            "4秒吸って6秒吐く×5回（呼吸で神経を落ち着かせる）",
            "スマホを裏返して3分だけ目を閉じる（情報遮断）",
            "『いまの自分に優しい言葉』を1行だけ書く",
        ],
        "message": [
            "いまは整える時間。焦らなくていい。",
            "回復は前進。今日はそれで十分。",
            "心が揺れる日は、守ることが一番偉い。",
        ],
    },
    "身体（だるい/痛い/眠い）": {
        "micro": [
            "水を一杯飲む＋首/肩をゆっくり回す（30秒）",
            "温かい飲み物を用意して、ゆっくり3口飲む",
            "軽い散歩3分（外に出られなければその場足踏み30回）",
            "入浴 or シャワーで体温を上げる（難しければ手を温める）",
        ],
        "message": [
            "体が味方になると、全部が進む。",
            "今日は“回復優先”で勝ち。",
            "だるさはサイン。ちゃんとケアしよう。",
        ],
    },
    "人間関係（人疲れ/気を遣いすぎ）": {
        "micro": [
            "連絡を返す前に深呼吸1回（即レスしない）",
            "今日の“会話の上限”を決める（例：30分）",
            "安心できる人に一言だけ送る（『今日は疲れた〜』でOK）",
            "SNS/チャットを10分だけ閉じる（境界線の練習）",
        ],
        "message": [
            "距離感を整えるほど、対人運も戻る。",
            "優しさは残していい。無理は捨てていい。",
            "自分を守れる人が、いちばん強い。",
        ],
    },
    "不明（なんとなくしんどい）": {
        "micro": [
            "部屋の中で“1か所だけ”片づける（30秒でOK）",
            "音を1つだけ選ぶ（環境音/音楽）→3分流す",
            "温かいものを食べる/飲む（汁物が最強）",
            "『今日はここまででOK』を声に出す",
        ],
        "message": [
            "理由が分からない日も、ちゃんとある。",
            "整えるだけで、明日は違う。",
            "何もしない時間も回復のうち。",
        ],
    },
}

INTENSITY_OPTIONS = ["1分", "3分", "5分", "10分"]
TIME_OPTIONS = ["いま（すぐ）", "昼休み", "帰宅後", "寝る前"]


def pick_action(category: str, intensity: str, timing: str, free_text: str) -> dict:
    bucket = ACTIONS[category]
    action = random.choice(bucket["micro"])
    msg = random.choice(bucket["message"])

    # ほんの少しだけ“入力”を反映（演出）
    note = ""
    if free_text.strip():
        note = f"今の気分メモ：『{free_text.strip()}』\n"

    # 強度・タイミングを結果に織り込む
    return {
        "action": f"✅ {timing}に、{intensity}だけ：{action}",
        "message": msg,
        "note": note,
    }


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🌿 今日の回復アクションAI")
st.caption("今日のあなたに合う“回復の一手”を1つだけ提案するよ。")
st.info(DISCLAIMER)

history = load_history()

st.divider()

col1, col2 = st.columns(2)
with col1:
    category = st.selectbox("疲れの種類", list(ACTIONS.keys()))
with col2:
    intensity = st.selectbox("できそうな強さ", INTENSITY_OPTIONS)

timing = st.selectbox("やるタイミング", TIME_OPTIONS)
free_text = st.text_area("いまの気分（任意）", height=80, placeholder="例：焦ってる、眠い、なんとなくしんどい…")

st.divider()

if st.button("回復アクションを出す", use_container_width=True):
    result = pick_action(category, intensity, timing, free_text)
    st.session_state["result"] = result

if "result" in st.session_state:
    r = st.session_state["result"]
    st.subheader("🫧 今日の回復メニュー")
    if r["note"]:
        st.caption(r["note"])
    st.markdown(r["action"])
    st.markdown(f"🌙 **ひとこと**：{r['message']}")

    st.text_area(
        "コピペ用（Markdown）",
        f"{r['note']}{r['action']}\n\nひとこと：{r['message']}",
        height=160
    )

    cA, cB = st.columns(2)
    with cA:
        if st.button("💾 履歴に保存", use_container_width=True):
            history.append({
                "time": datetime.now().isoformat(timespec="seconds"),
                "category": category,
                "intensity": intensity,
                "timing": timing,
                "free_text": free_text.strip(),
                "action": r["action"],
                "message": r["message"],
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
            st.markdown(f"**{row['time']}｜{row['category']}｜{row['timing']}｜{row['intensity']}**")
            if row.get("free_text"):
                st.caption(f"気分：{row['free_text']}")
            st.markdown(row["action"])
            st.caption(f"ひとこと：{row['message']}")
            st.write("---")
