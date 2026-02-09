from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Set, Optional

import streamlit as st

APP_TITLE = "🟥🟦 戦隊マッチ（戦隊名 × ○○ジャー）Day75"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "pairs.csv"


# -----------------------------
# Data
# -----------------------------
@dataclass(frozen=True)
class Pair:
    sentai: str
    ranger: str


def load_pairs(csv_path: Path) -> List[Pair]:
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} が見つからないよ。data/pairs.csv を作ってね！")

    pairs: List[Pair] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if "sentai" not in reader.fieldnames or "ranger" not in reader.fieldnames:
            raise ValueError("CSVのヘッダーは sentai,ranger にしてね。")

        for row in reader:
            s = (row.get("sentai") or "").strip()
            r = (row.get("ranger") or "").strip()
            if not s or not r:
                continue
            pairs.append(Pair(s, r))

    if not pairs:
        raise ValueError("pairs.csv に有効なデータがないよ。1行以上入れてね。")
    return pairs


def validate_pairs(pairs: List[Pair]) -> Tuple[bool, List[str]]:
    """同名重複など最低限チェック"""
    errors: List[str] = []

    # 同一sentaiが複数rangerに紐づくとクイズが壊れやすい（※わざとやるならOK）
    # ただし今回は「マッチングゲーム」としては一意が望ましいので警告。
    sentai_map: Dict[str, Set[str]] = {}
    ranger_map: Dict[str, Set[str]] = {}

    for p in pairs:
        sentai_map.setdefault(p.sentai, set()).add(p.ranger)
        ranger_map.setdefault(p.ranger, set()).add(p.sentai)

    dup_sentai = [s for s, rs in sentai_map.items() if len(rs) > 1]
    dup_ranger = [r for r, ss in ranger_map.items() if len(ss) > 1]

    if dup_sentai:
        errors.append(f"同じ sentai が複数の ranger に紐づいてる：{', '.join(dup_sentai[:10])}" + (" ..." if len(dup_sentai) > 10 else ""))
    if dup_ranger:
        errors.append(f"同じ ranger が複数の sentai に紐づいてる：{', '.join(dup_ranger[:10])}" + (" ..." if len(dup_ranger) > 10 else ""))

    # 完全重複
    seen = set()
    dups = []
    for p in pairs:
        key = (p.sentai, p.ranger)
        if key in seen:
            dups.append(f"{p.sentai} - {p.ranger}")
        seen.add(key)
    if dups:
        errors.append(f"完全に同じ行が重複してる：{', '.join(dups[:10])}" + (" ..." if len(dups) > 10 else ""))

    ok = (len(errors) == 0)
    return ok, errors


# -----------------------------
# Game State
# -----------------------------
def new_game(all_pairs: List[Pair], n: int) -> None:
    # n=0 なら全件
    pool = all_pairs[:]
    random.shuffle(pool)
    if n > 0:
        pool = pool[: min(n, len(pool))]

    st.session_state["pool_pairs"] = pool
    st.session_state["answer_map"] = {p.sentai: p.ranger for p in pool}  # sentai -> ranger
    st.session_state["remaining_sentai"] = [p.sentai for p in pool]
    st.session_state["remaining_ranger"] = [p.ranger for p in pool]
    random.shuffle(st.session_state["remaining_sentai"])
    random.shuffle(st.session_state["remaining_ranger"])

    st.session_state["selected_sentai"] = None
    st.session_state["selected_ranger"] = None
    st.session_state["matched"] = 0
    st.session_state["miss"] = 0
    st.session_state["tries"] = 0
    st.session_state["lock"] = False


def ensure_game(all_pairs: List[Pair]) -> None:
    if "remaining_sentai" not in st.session_state or "remaining_ranger" not in st.session_state:
        new_game(all_pairs, n=10)


def pick_sentai(s: str) -> None:
    if st.session_state.get("lock"):
        return
    st.session_state["selected_sentai"] = s


def pick_ranger(r: str) -> None:
    if st.session_state.get("lock"):
        return
    st.session_state["selected_ranger"] = r


def evaluate_selection() -> None:
    s = st.session_state.get("selected_sentai")
    r = st.session_state.get("selected_ranger")
    if not s or not r:
        return

    st.session_state["lock"] = True
    st.session_state["tries"] += 1

    ans = st.session_state["answer_map"].get(s)
    if ans == r:
        st.session_state["matched"] += 1
        # remove from remaining lists
        st.session_state["remaining_sentai"] = [x for x in st.session_state["remaining_sentai"] if x != s]
        st.session_state["remaining_ranger"] = [x for x in st.session_state["remaining_ranger"] if x != r]
        st.toast("✨ 正解！ペア成立！", icon="✅")
    else:
        st.session_state["miss"] += 1
        st.toast("😵 不正解！", icon="❌")

    # clear selection
    st.session_state["selected_sentai"] = None
    st.session_state["selected_ranger"] = None
    st.session_state["lock"] = False


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title("🟥🟦 戦隊マッチ（戦隊名 × ○○ジャー）")
st.caption("左（戦隊名）と右（○○ジャー）を選んで、正しいペアを揃えよう。50+も対応！")

# load + validate
try:
    pairs = load_pairs(CSV_PATH)
except Exception as e:
    st.error(str(e))
    st.stop()

ok, errs = validate_pairs(pairs)
with st.expander("⚙️ データチェック（大事）", expanded=not ok):
    st.write(f"読み込み件数：**{len(pairs)}** ペア")
    if ok:
        st.success("問題なし！このまま遊べるよ。")
    else:
        st.warning("重複があると“正解が一意に決まらない”ことがあるよ（ゲームが難化/破綻する可能性）。")
        for msg in errs:
            st.write("・", msg)
        st.caption("※あえて重複を入れて“鬼難易度”にしたいならOK。基本は一意がおすすめ。")

ensure_game(pairs)

# Top controls
colA, colB, colC, colD = st.columns([2, 2, 2, 2])
with colA:
    mode = st.selectbox(
        "出題数",
        ["10問（サクッと）", "20問（ほどよく）", "50問（本気）", "全部（50+）"],
        index=0
    )
with colB:
    if st.button("🔁 リスタート", use_container_width=True):
        n = 10 if mode.startswith("10") else 20 if mode.startswith("20") else 50 if mode.startswith("50") else 0
        new_game(pairs, n=n)
        st.rerun()
with colC:
    if st.button("🎲 シャッフル（同じ出題数）", use_container_width=True):
        n = 10 if mode.startswith("10") else 20 if mode.startswith("20") else 50 if mode.startswith("50") else 0
        new_game(pairs, n=n)
        st.rerun()
with colD:
    if st.button("🧹 選択クリア", use_container_width=True):
        st.session_state["selected_sentai"] = None
        st.session_state["selected_ranger"] = None
        st.rerun()

# Stats
total = len(st.session_state["pool_pairs"])
remaining = len(st.session_state["remaining_sentai"])
matched = st.session_state["matched"]
tries = st.session_state["tries"]
miss = st.session_state["miss"]

st.write(f"🎯 出題：**{total}**　✅ 成立：**{matched}**　🧩 残り：**{remaining}**　🕹 試行：**{tries}**　❌ ミス：**{miss}**")

st.divider()

# Selection preview
sel_s = st.session_state.get("selected_sentai")
sel_r = st.session_state.get("selected_ranger")
st.markdown(f"### 選択中：🟥 **{sel_s or '（未選択）'}**  ｜  🟦 **{sel_r or '（未選択）'}**")

# Board: two columns lists
left, right = st.columns(2)

with left:
    st.subheader("🟥 戦隊名")
    for s in st.session_state["remaining_sentai"]:
        st.button(
            s,
            key=f"s_{s}",
            use_container_width=True,
            type="primary" if s == sel_s else "secondary",
            disabled=st.session_state.get("lock", False),
            on_click=pick_sentai,
            args=(s,),
        )

with right:
    st.subheader("🟦 ○○ジャー")
    for r in st.session_state["remaining_ranger"]:
        st.button(
            r,
            key=f"r_{r}",
            use_container_width=True,
            type="primary" if r == sel_r else "secondary",
            disabled=st.session_state.get("lock", False),
            on_click=pick_ranger,
            args=(r,),
        )

# Evaluate when both selected
if st.session_state.get("selected_sentai") and st.session_state.get("selected_ranger"):
    evaluate_selection()
    st.rerun()

# Clear
if remaining == 0:
    st.success(f"🎉 クリア！ 出題 {total} を全部揃えた！ 試行：{tries} / ミス：{miss}")
    st.caption("次の進化：難易度（タイムアタック/連続正解ボーナス/ランク表示）も入れられるよ。")
