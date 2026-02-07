from __future__ import annotations

import random
import time
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st

APP_TITLE = "🧠 神経衰弱（画像版 / Day73）"

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
CARDS_DIR = ASSETS_DIR / "cards"
BACK_PATH = ASSETS_DIR / "back.png"

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


# -----------------------------
# デッキ生成（画像パス）
# -----------------------------
def list_card_images() -> List[Path]:
    if not CARDS_DIR.exists():
        return []
    imgs = [p for p in CARDS_DIR.iterdir() if p.suffix.lower() in IMG_EXTS and p.is_file()]
    imgs.sort()
    return imgs


def make_board(size: int, seed: Optional[int] = None) -> List[str]:
    """
    size: 4 or 6 (4x4=16枚 / 6x6=36枚)
    deck: List[str] 画像パス（文字列）を並べる
    """
    if seed is not None:
        random.seed(seed)

    n_cards = size * size
    n_pairs = n_cards // 2

    images = list_card_images()
    if len(images) < n_pairs:
        raise RuntimeError(f"カード画像が足りません：必要 {n_pairs}枚 / 現在 {len(images)}枚")

    picks = random.sample(images, k=n_pairs)  # 1種類 = 1枚
    deck = [str(p) for p in (picks + picks)]  # ペアにする
    random.shuffle(deck)
    return deck


def rc_to_idx(r: int, c: int, size: int) -> int:
    return r * size + c


# -----------------------------
# state
# -----------------------------
def init_game(size: int) -> None:
    st.session_state["size"] = size
    st.session_state["deck"] = make_board(size)
    st.session_state["matched"] = [False] * (size * size)
    st.session_state["opened"] = []
    st.session_state["moves"] = 0
    st.session_state["started_at"] = time.time()
    st.session_state["lock"] = False


def ensure_state() -> None:
    if "size" not in st.session_state:
        init_game(4)


def all_matched() -> bool:
    return all(st.session_state["matched"])


# -----------------------------
# UI helpers
# -----------------------------
def can_click(i: int) -> bool:
    if st.session_state["lock"]:
        return False
    if st.session_state["matched"][i]:
        return False
    if i in st.session_state["opened"]:
        return False
    if len(st.session_state["opened"]) >= 2:
        return False
    return True


def handle_click(i: int) -> None:
    if not can_click(i):
        return
    st.session_state["opened"].append(i)

    if len(st.session_state["opened"]) == 2:
        st.session_state["moves"] += 1
        st.session_state["lock"] = True


def evaluate_opened() -> None:
    opened = st.session_state["opened"]
    if len(opened) != 2:
        st.session_state["lock"] = False
        return

    deck = st.session_state["deck"]
    a, b = opened
    if deck[a] == deck[b]:
        st.session_state["matched"][a] = True
        st.session_state["matched"][b] = True
        st.session_state["opened"] = []
        st.session_state["lock"] = False
        st.toast("✨ ペア！", icon="✅")
    else:
        time.sleep(0.6)
        st.session_state["opened"] = []
        st.session_state["lock"] = False
        st.toast("😵 ちがう！", icon="❌")


def card_image_path(i: int) -> str:
    """表示する画像パス（裏 or 表）"""
    deck = st.session_state["deck"]
    matched = st.session_state["matched"]
    opened = st.session_state["opened"]

    if matched[i] or i in opened:
        return deck[i]  # 表
    return str(BACK_PATH)  # 裏


# -----------------------------
# App
# -----------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title("🧠 神経衰弱（画像版）")
st.caption("画像でペアをそろえる神経衰弱。クリック2枚で判定！")

# assetsチェック
if not BACK_PATH.exists():
    st.error("assets/back.png が見つからないよ。裏画像を置いてね！")
    st.stop()

if not CARDS_DIR.exists():
    st.error("assets/cards/ が見つからないよ。カード画像を置いてね！")
    st.stop()

ensure_state()

# Controls
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    size = st.selectbox("盤面", [4, 6], index=0, format_func=lambda x: f"{x}×{x}")
with c2:
    if st.button("🔁 リスタート", use_container_width=True):
        init_game(size)
        st.rerun()
with c3:
    if st.button("🎲 シャッフル", use_container_width=True):
        init_game(st.session_state["size"])
        st.rerun()

# サイズ変更
if size != st.session_state["size"]:
    init_game(size)
    st.rerun()

elapsed = int(time.time() - st.session_state["started_at"])
st.write(f"🕹 手数：**{st.session_state['moves']}**　⏱ 経過：**{elapsed}秒**")

st.divider()

# Board（画像表示 + ボタン）
size = st.session_state["size"]
for r in range(size):
    cols = st.columns(size)
    for c in range(size):
        i = rc_to_idx(r, c, size)
        with cols[c]:
            st.image(card_image_path(i), use_container_width=True)
            st.button(
                "選ぶ",
                key=f"pick_{i}",
                use_container_width=True,
                disabled=not can_click(i),
                on_click=handle_click,
                args=(i,),
            )

# 評価（2枚開いたら）
if st.session_state["lock"] and len(st.session_state["opened"]) == 2:
    evaluate_opened()
    st.rerun()

# クリア
if all_matched():
    total_time = int(time.time() - st.session_state["started_at"])
    st.success(f"🎉 クリア！ 手数：{st.session_state['moves']} / 時間：{total_time}秒")
    st.caption("次は“テーマ切替”や“難易度追加（8×8）”もできるよ。")
