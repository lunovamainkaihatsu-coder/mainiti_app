from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_TITLE = "🌙 明日のひとつだけAI（Day69）"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

DISCLAIMER = "※これはタスク整理のための提案です。体調が悪い日は“休む”が最優先。"


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
# “ひとつだけ”候補
# -------------------------
ONE_THINGS = {
    "開発（アプリ/コード）": [
        "プロジェクトを開くだけ（起動だけでOK）",
        "1行だけ改善する（変数名/表示文など）",
        "READMEに1行追記する",
        "バグを1つだけ再現してメモする",
        "UIを1か所だけ整える（余白/見出し/ボタン）",
        "Push準備だけする（add/commitは後でOK）",
    ],
    "発信（Note/X/ブログ）": [
        "タイトルだけ決める",
        "見出しを3つ作る",
        "200文字だけ書く",
        "ネタを箇条書きで5個出す",
        "過去アプリを1つ紹介する文章を作る",
    ],
    "学習（勉強/資格）": [
        "テキストを開いて1ページだけ読む",
        "問題を1問だけ解く",
        "今日の疑問を1つメモする",
        "重要語句を3つだけ書き出す",
    ],
    "生活（家/体）": [
        "机の上を1か所だけ片づける（30秒でもOK）",
        "洗い物を“1つだけ”洗う",
        "明日の準備を1つだけする（服/カバン/水）",
        "5分だけ散歩 or ストレッチ",
        "湯船 or 温かい飲み物で体温を上げる",
    ],
    "メンタル（整える）": [
        "不安を1行だけ書き出して終了",
        "スマホを裏返して3分休む",
        "深呼吸（4秒吸って6秒吐く×5回）",
        "『今日できたこと』を1つ思い出す",
    ],
}

ENERGY_LEVELS = {
    "ほぼゼロ（守る日）": [
        "『休む』をひとつだけとして採用（布団に入るだけ）",
        "水をひと口飲む",
        "目を閉じて1分だけ呼吸する",
    ],
    "低め（ゆっくり）": [
        "5分だけやる",
        "準備だけする",
        "1か所だけ整える",
    ],
    "普通（いける）": [
        "短いアウトプットを出す",
        "1つ改善する",
        "1つ終わらせる",
    ],
    "高め（攻められる）": [
        "小さめの完成まで持っていく",
        "1本投稿する",
        "次の段取りまで作る",
    ],
}

LUNA_LINES = [
    "それだけで十分。明日は進む。",
    "小さく勝つと、流れが戻る。",
    "“ひとつだけ”は最強の戦略。",
    "今日のあなたに合うサイズでいこう。",
    "できたら勝ち。できなくても、また選び直せばいい。",
]


def pick_one(domain: str, energy: str, notes: str) -> dict:
    # エネルギーによって“強度”を調整する演出
    if energy == "ほぼゼロ（守る日）":
        one = random.choice(ENERGY_LEVELS[energy])
    else:
        base = random.choice(ONE_THINGS[domain])
        modifier = random.choice(ENERGY_LEVELS[energy])
        # modifierは文章として使うので軽く整形
        if "だけ" in base:
            one = base
        else:
            one = f"{base}（{modifier}）"

    line = random.choice(LUNA_LINES)
    note_line = f"メモ：『{notes.strip()}』\n" if notes.strip() else ""
    return {"one": one, "line": line, "note_line": note_line}


# -------------------------
# UI
# -------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🌙 明日のひとつだけAI")
st.caption("明日は“これだけ”やればOK。最小タスクを1つ決めるアプリ。")
st.info(DISCLAIMER)

history = load_history()

st.divider()

col1, col2 = st.columns(2)
with col1:
    domain = st.selectbox("明日の軸", list(ONE_THINGS.keys()))
with col2:
    energy = st.selectbox("明日のエネルギー", list(ENERGY_LEVELS.keys()))

notes = st.text_area("明日の状況メモ（任意）", height=90, placeholder="例：忙しい／寝不足／投稿を戻したい／アプリ触りたい…")

st.divider()

if st.button("明日の“ひとつだけ”を決める", use_container_width=True):
    r = pick_one(domain, energy, notes)
    st.session_state["result"] = r

if "result" in st.session_state:
    r = st.session_state["result"]
    st.subheader("✅ 明日のひとつだけ")
    if r["note_line"]:
        st.caption(r["note_line"])
    st.markdown(f"### {r['one']}")
    st.markdown(f"🌙 **ルナ**：{r['line']}")

    copy_text = f"{r['note_line']}明日のひとつだけ：{r['one']}\n\nルナ：{r['line']}"
    st.text_area("コピペ用", copy_text, height=170)

    cA, cB = st.columns(2)
    with cA:
        if st.button("💾 履歴に保存", use_container_width=True):
            history.append({
                "time": datetime.now().isoformat(timespec="seconds"),
                "domain": domain,
                "energy": energy,
                "notes": notes.strip(),
                "one": r["one"],
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
            st.markdown(f"**{row['time']}｜{row['domain']}｜{row['energy']}**")
            if row.get("notes"):
                st.caption(f"メモ：{row['notes']}")
            st.markdown(f"✅ {row['one']}")
            st.caption(f"ルナ：{row['line']}")
            st.write("---")
