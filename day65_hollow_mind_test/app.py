import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="🧠 闇が見える心理テスト", layout="centered")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SAVE_PATH = DATA_DIR / "results.json"

DISCLAIMER = "※これは心理テスト風の創作アプリです。診断や予言ではありません。"


def load_results():
    if not SAVE_PATH.exists():
        return []
    try:
        return json.loads(SAVE_PATH.read_text(encoding="utf-8"))
    except:
        return []


def save_results(data):
    SAVE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


st.title("🧠 闇が見える心理テスト")
st.caption("あなたの心の“影”を、心理的に読み解きます。")
st.info(DISCLAIMER)

st.divider()

questions = [
    ("夜、知らない道を歩いているとき…", {
        "A": "周囲を警戒する",
        "B": "何も考えず進む",
        "C": "誰かと話して気を紛らわす"
    }),
    ("人に秘密を打ち明けるとき…", {
        "A": "ほとんど話さない",
        "B": "選んだ人だけに話す",
        "C": "つい誰かに話してしまう"
    }),
    ("強く惹かれるのはどれ？", {
        "A": "静かな場所",
        "B": "賑やかな場所",
        "C": "誰も知らない場所"
    }),
    ("対立が起きたとき、あなたは…", {
        "A": "黙って距離を取る",
        "B": "話し合おうとする",
        "C": "流れに任せる"
    }),
    ("“自分らしい”と感じる瞬間は？", {
        "A": "一人でいるとき",
        "B": "誰かに必要とされたとき",
        "C": "新しいことをしているとき"
    })
]

scores = {"A": 0, "B": 0, "C": 0}
answers = {}

for idx, (q, opts) in enumerate(questions, start=1):
    st.subheader(f"Q{idx}. {q}")
    choice = st.radio("", list(opts.keys()), format_func=lambda x: f"{x}: {opts[x]}", key=f"q{idx}")
    answers[f"Q{idx}"] = choice
    scores[choice] += 1

st.divider()

def diagnose(scores):
    a, b, c = scores["A"], scores["B"], scores["C"]

    if a >= b and a >= c:
        return {
            "type": "静かな観測者",
            "shadow": "感情を内に溜め込みやすく、表に出すのが苦手。",
            "advice": "安心できる場所では、少しずつ言葉にしてみよう。"
        }
    elif b >= a and b >= c:
        return {
            "type": "仮面の演者",
            "shadow": "周囲に合わせすぎて、自分の気持ちを後回しにしがち。",
            "advice": "“本当はどうしたいか”を一度だけ自分に聞いてみよう。"
        }
    else:
        return {
            "type": "境界の迷い子",
            "shadow": "選択に迷いやすく、他人の感情に影響されやすい。",
            "advice": "決める前に“今の自分”を基準にしてみよう。"
        }

if st.button("結果を見る", use_container_width=True):
    result = diagnose(scores)
    st.session_state["result"] = result

if "result" in st.session_state:
    res = st.session_state["result"]
    st.subheader("🪞 あなたの深層タイプ")
    st.markdown(f"### **{res['type']}**")
    st.markdown(f"🌑 影の性質：{res['shadow']}")
    st.markdown(f"✨ 活かし方：{res['advice']}")

    results = load_results()
    if st.button("💾 保存する"):
        results.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "type": res["type"],
            "answers": answers
        })
        save_results(results)
        st.success("保存しました")

with st.expander("🗂 過去の結果（最新10件）"):
    results = load_results()
    if not results:
        st.write("まだ保存がありません")
    else:
        for r in reversed(results[-10:]):
            st.markdown(f"**{r['time']}｜{r['type']}**")
            st.write(r["answers"])
            st.write("---")
