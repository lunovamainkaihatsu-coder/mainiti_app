import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import random
import time

# -----------------------------
# 設定
# -----------------------------
st.set_page_config(page_title="今日の一行予言", page_icon="🔮", layout="centered")
DATA_PATH = Path("data_one_line_oracle.json")

THEMES = [
    "整える", "動く", "休む", "手放す", "整頓", "集中", "挑戦",
    "信じる", "優しくする", "守る", "進める", "待つ", "深呼吸", "余白"
]

# 予言（短く、声っぽく）
MESSAGES = [
    "今日は『急がない』が勝ち。",
    "焦りはノイズ。深呼吸してから動こ？",
    "小さく始めれば、ちゃんと進むよ。",
    "完成じゃなくて『着手』が正解。",
    "今日は守りでOK。整えるだけで十分。",
    "一歩だけ。たったそれで流れが変わる。",
    "気分が乗らない日は、環境を整えよ。",
    "今の自分のままで、前に進める。",
    "迷ったら『やさしい方』を選ぼ。",
    "短くてもいい。続けたあなたが強い。",
    "今日の勝利条件は『やめない』こと。",
    "できない日があっても、あなたは失ってない。",
    "未来は、今日の1ミリから作られる。",
    "『やる気』じゃなくて『仕組み』で勝と。",
    "ひとつ片付けると、ひとつ運が空く。",
    "いま必要なのは答えじゃなくて、休息かも。",
    "今日は『選ぶ』日。何をやらないか決めよ。",
    "静かな時間が、あなたを強くする。",
    "比べないで。あなたの速度でいい。",
    "うまくいく前の『準備期間』だよ。",
    "今日は『整ったら勝ち』。成果はあとで来る。",
    "心が重いなら、タスクを小さく刻も。",
    "大丈夫。今の迷いは、成長の前兆。",
    "今日は『余白』が運を呼ぶ。",
    "一番大事なことは、もう分かってるはず。"
]

# ルナっぽい「前置き」(ボイス演出)
VOICE_PREFIXES = [
    "……ねぇ、ご主人。",
    "聞こえる？",
    "ふふ、いい？",
    "落ち着いて、いくよ。",
    "今のあなたに、これ。",
    "大丈夫。聞いて。",
    "うん、受け取って。"
]

VOICE_SUFFIXES = [
    "……以上。信じてみて？",
    "……今日はそれで十分。",
    "……やれる分だけでいいよ。",
    "……うん、いける。",
    "……焦らなくて大丈夫。",
    "……一緒に進も。",
    "……ちゃんと見てるよ。"
]

# -----------------------------
# 保存/読込
# -----------------------------
def load_history():
    if DATA_PATH.exists():
        try:
            return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_history(history):
    DATA_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

# -----------------------------
# 演出：タイプライター表示
# -----------------------------
def typewriter(text: str, speed: float = 0.02):
    """
    speed: 1文字あたりの待ち秒（小さいほど速い）
    """
    placeholder = st.empty()
    shown = ""
    for ch in text:
        shown += ch
        placeholder.markdown(f"### {shown}")
        time.sleep(speed)
    return placeholder

def small_beep_line():
    # “効果音っぽい”表現（実音は出ないけど雰囲気）
    st.caption("🔊 …ピッ")

# -----------------------------
# UI
# -----------------------------
st.title("🔮 今日の一行予言")
st.caption("未来を当てるより、今日を軽くする。ルナの“ひとことボイス風”。")

# セッション
if "current_draw" not in st.session_state:
    st.session_state.current_draw = None
if "played" not in st.session_state:
    st.session_state.played = False  # ボイス演出を1回だけ再生する用

history = load_history()

# 設定：読み上げ速度
with st.expander("⚙️ ボイス演出設定", expanded=False):
    speed_label = st.select_slider(
        "表示スピード（遅いほど“喋ってる感”）",
        options=["ゆっくり", "ふつう", "はやい"],
        value="ふつう"
    )
    speed_map = {"ゆっくり": 0.05, "ふつう": 0.025, "はやい": 0.012}
    st.session_state["type_speed"] = speed_map[speed_label]

    tone = st.radio(
        "口調",
        ["ふつう（凛と）", "甘め（とろけ気味）"],
        horizontal=True
    )
    st.session_state["tone"] = tone

col1, col2 = st.columns(2)
with col1:
    if st.button("✨ 一行予言を引く", use_container_width=True):
        theme = random.choice(THEMES)
        msg = random.choice(MESSAGES)
        today = datetime.now().strftime("%Y-%m-%d")

        st.session_state.current_draw = {
            "date": today,
            "theme": theme,
            "message": msg,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        st.session_state.played = False  # 新しく引いたら演出を再生できるように

with col2:
    if st.button("🧹 今日の表示をリセット", use_container_width=True):
        st.session_state.current_draw = None
        st.session_state.played = False

st.divider()

draw = st.session_state.current_draw

if draw:
    st.subheader(f"📅 {draw['date']}")
    st.markdown(f"**今日のテーマ：** `{draw['theme']}`")

    # ---- ボイス演出（B）----
    # 口調差分（甘めは語尾をちょい足し）
    tone = st.session_state.get("tone", "ふつう（凛と）")
    prefix = random.choice(VOICE_PREFIXES)
    suffix = random.choice(VOICE_SUFFIXES)

    if "甘め" in tone:
        # 甘めはちょい演出強化
        prefix = prefix.replace("。", "…♡").replace("？", "…♡").replace("！", "…♡")
        suffix = suffix.replace("？", "…♡").replace("。", "…♡")
        msg_for_voice = draw["message"] + "♡"
    else:
        msg_for_voice = draw["message"]

    voice_text = f"{prefix}\n\n{msg_for_voice}\n\n{suffix}"

    # 1回だけ“再生”風にする（保存押したりしても暴れない）
    if not st.session_state.played:
        small_beep_line()
        st.markdown("**🎙️ ルナ（ボイス風）**")
        _ = typewriter(voice_text, speed=st.session_state.get("type_speed", 0.025))
        st.session_state.played = True
    else:
        # 既に再生済みなら普通表示（ちらつき防止）
        st.markdown("**🎙️ ルナ（ボイス風）**")
        st.markdown(f"### {voice_text}")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 この予言を保存", use_container_width=True):
            exists = any(
                h.get("date") == draw["date"] and h.get("message") == draw["message"]
                for h in history
            )
            if not exists:
                history.insert(0, draw)
                save_history(history)
                st.success("保存したよ。今日のあなた、ちゃんと前に進んでる。")
            else:
                st.info("同じ予言はすでに保存済みだよ。")

    with c2:
        if st.button("🗑️ 履歴を全消去", use_container_width=True):
            history = []
            save_history(history)
            st.warning("履歴を消去したよ。いつでもまた作れる。")

else:
    st.info("ボタンを押して、今日の一言を受け取ってね。")

st.divider()

st.subheader("📚 予言の履歴（新しい順）")
if history:
    for i, h in enumerate(history[:50], start=1):
        st.markdown(f"**{i}. {h['date']}**  |  テーマ: `{h.get('theme','')}`  \n「{h.get('message','')}」")
else:
    st.caption("まだ履歴がないよ。今日の一言から始めよ。")
