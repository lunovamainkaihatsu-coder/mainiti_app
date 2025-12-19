import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, date, time as dtime
from pathlib import Path
import streamlit as st

# =========================
# 基本設定
# =========================
st.set_page_config(page_title="24時間スケジュール", page_icon="🗓️", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

TODAY = date.today().isoformat()
LOG_PATH = DATA_DIR / f"log_{TODAY}.json"
PLAN_PATH = DATA_DIR / f"plan_{TODAY}.json"

# =========================
# データ構造
# =========================
@dataclass
class Block:
    start: str       # "HH:MM"
    title: str
    minutes: int
    note: str = ""
    tag: str = "勉強"

def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def now_str():
    return datetime.now().strftime("%H:%M:%S")

def parse_hhmm(s: str):
    # "HH:MM" -> minutes from 00:00
    try:
        hh, mm = s.split(":")
        hh = int(hh); mm = int(mm)
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return hh * 60 + mm
    except Exception:
        pass
    return None

def fmt_hhmm(total_min: int):
    hh = (total_min // 60) % 24
    mm = total_min % 60
    return f"{hh:02d}:{mm:02d}"

def sort_plan(plan):
    def key(b):
        v = parse_hhmm(b.get("start", "00:00"))
        return v if v is not None else 10**9
    return sorted(plan, key=key)

def detect_conflicts(plan_sorted):
    # 開始時刻順に、前の終了 > 次の開始 なら衝突
    conflicts = []
    prev_end = None
    prev_idx = None
    for i, b in enumerate(plan_sorted):
        s = parse_hhmm(b.get("start", "00:00"))
        if s is None:
            continue
        end = s + int(b.get("minutes", 0))
        if prev_end is not None and s < prev_end:
            conflicts.append((prev_idx, i))
        prev_end = max(prev_end or end, end)
        prev_idx = i
    return conflicts

# =========================
# セッション初期化
# =========================
if "plan" not in st.session_state:
    st.session_state.plan = load_json(PLAN_PATH, default=[])

if "log" not in st.session_state:
    st.session_state.log = load_json(LOG_PATH, default=[])

if "running" not in st.session_state:
    st.session_state.running = False

if "run_total_sec" not in st.session_state:
    st.session_state.run_total_sec = 0

if "current_block_id" not in st.session_state:
    st.session_state.current_block_id = None  # index in sorted view

if "last_tick" not in st.session_state:
    st.session_state.last_tick = None

# =========================
# UI
# =========================
st.title("🗓️ 24時間スケジュール（開始時刻つき）")
st.caption("予定は“時刻で置く”。実行は“今の集中”で回す。どっちも取る。")

left, right = st.columns([1.15, 0.85])

# =========================
# 左：予定作成＆一覧
# =========================
with left:
    st.subheader("🧩 予定を登録（開始時刻つき）")

    templates = {"25分（ポモドーロ）": 25, "15分（軽め）": 15, "45分（集中）": 45, "60分（ガチ）": 60}

    c1, c2, c3 = st.columns([0.35, 0.35, 0.30])
    with c1:
        start_t = st.time_input("開始時刻", value=datetime.now().time().replace(second=0, microsecond=0))
        start_str = start_t.strftime("%H:%M")
    with c2:
        title = st.text_input("ブロック名", value="勉強", placeholder="例：民法・復習 / アプリ修正")
    with c3:
        tag = st.selectbox("カテゴリ", ["勉強", "開発", "仕事", "家事", "休憩", "その他"])

    c4, c5 = st.columns([0.5, 0.5])
    with c4:
        temp_key = st.selectbox("時間テンプレ", list(templates.keys()))
    with c5:
        minutes = st.number_input("分数", min_value=1, max_value=240, value=templates[temp_key], step=1)

    note = st.text_area("メモ（任意）", height=80, placeholder="例：このブロックでやることを1〜3行で")

    if st.button("➕ 予定に追加", use_container_width=True, disabled=st.session_state.running):
        b = Block(start=start_str, title=title.strip() or "無題", minutes=int(minutes), note=note.strip(), tag=tag)
        st.session_state.plan.append(asdict(b))
        st.session_state.plan = sort_plan(st.session_state.plan)
        save_json(PLAN_PATH, st.session_state.plan)
        st.success(f"{start_str} に追加したよ。")

    st.divider()
    st.subheader("📋 今日の予定（開始時刻順）")

    st.session_state.plan = sort_plan(st.session_state.plan)
    plan = st.session_state.plan

    if not plan:
        st.info("まだ予定がないよ。まず1つ追加してみて。")
    else:
        conflicts = detect_conflicts(plan)
        conflict_set = set()
        for a, b in conflicts:
            conflict_set.add(a); conflict_set.add(b)
        if conflicts:
            st.warning("⚠️ 時間が重なってる予定があるよ（衝突）。下で赤表示にしてる。")

        for i, b in enumerate(plan):
            is_conflict = i in conflict_set
            row = st.columns([0.12, 0.58, 0.15, 0.15])

            with row[0]:
                st.write(("🟥 " if is_conflict else "🟦 ") + f"**{b.get('start','--:--')}**")
            with row[1]:
                st.write(
                    f"**{b.get('title','')}**  ・{b.get('tag','')}\n\n"
                    f"{b.get('minutes',0)}分  /  {b.get('note','')}"
                )
            with row[2]:
                up = st.button("↑", key=f"up_{i}", use_container_width=True, disabled=(i == 0 or st.session_state.running))
                down = st.button("↓", key=f"down_{i}", use_container_width=True, disabled=(i == len(plan)-1 or st.session_state.running))
                if up:
                    plan[i-1], plan[i] = plan[i], plan[i-1]
                    save_json(PLAN_PATH, plan)
                    st.rerun()
                if down:
                    plan[i+1], plan[i] = plan[i], plan[i+1]
                    save_json(PLAN_PATH, plan)
                    st.rerun()
            with row[3]:
                del_btn = st.button("🗑️", key=f"del_{i}", use_container_width=True, disabled=st.session_state.running)
                if del_btn:
                    plan.pop(i)
                    save_json(PLAN_PATH, plan)
                    st.rerun()

        st.divider()
        cA, cB = st.columns(2)
        with cA:
            if st.button("🧹 今日の予定を全削除", use_container_width=True, disabled=st.session_state.running):
                st.session_state.plan = []
                save_json(PLAN_PATH, [])
                st.rerun()
        with cB:
            if st.button("📦 今日の履歴も全削除", use_container_width=True, disabled=st.session_state.running):
                st.session_state.log = []
                save_json(LOG_PATH, [])
                st.rerun()

# =========================
# 右：24hタイムライン＆タイマー
# =========================
with right:
    st.subheader("🕒 24h タイムライン")
    plan = sort_plan(st.session_state.plan)

    # 24hリスト表示（1時間ごとの目盛り＋該当ブロックを表示）
    hour_blocks = {h: [] for h in range(24)}
    for b in plan:
        s = parse_hhmm(b.get("start", "00:00"))
        if s is None:
            continue
        h = s // 60
        hour_blocks[h].append(b)

    # 見やすさ優先：各時間に開始する予定を箇条書き
    for h in range(24):
        label = f"{h:02d}:00"
        items = hour_blocks[h]
        if items:
            st.markdown(f"**{label}**")
            for b in items:
                s = b.get("start", "--:--")
                mins = int(b.get("minutes", 0))
                end = parse_hhmm(s)
                end_str = fmt_hhmm(end + mins) if end is not None else "--:--"
                st.write(f"- {s}〜{end_str}  {b.get('title','')}（{mins}分）")
        else:
            st.caption(label)

    st.divider()
    st.subheader("▶ 実行タイマー（選んだブロックを今やる）")

    if not plan:
        st.info("まず左で予定を追加してね。")
    else:
        # ブロック選択（実行中は固定）
        if not st.session_state.running:
            default_idx = 0
            if st.session_state.current_block_id is not None:
                default_idx = min(max(0, st.session_state.current_block_id), len(plan) - 1)

            idx = st.selectbox(
                "実行するブロック",
                options=list(range(len(plan))),
                index=default_idx,
                format_func=lambda i: f"{plan[i].get('start','--:--')}  {plan[i].get('title','')}（{plan[i].get('minutes',0)}分）",
            )
            st.session_state.current_block_id = idx
        else:
            idx = st.session_state.current_block_id or 0
            b = plan[idx]
            st.write(f"**実行中：{b.get('title','')}（{b.get('minutes',0)}分）**")

        b = plan[st.session_state.current_block_id or 0]
        total_sec = int(b.get("minutes", 0)) * 60

        # タイマー更新
        if st.session_state.running:
            now = time.time()
            if st.session_state.last_tick is None:
                st.session_state.last_tick = now
            delta = now - st.session_state.last_tick
            st.session_state.last_tick = now
            st.session_state.run_total_sec += int(delta)

            # 画面更新
            time.sleep(0.2)
            st.rerun()

        elapsed = st.session_state.run_total_sec if st.session_state.running else 0
        remaining = max(0, total_sec - elapsed)

        mm_r, ss_r = remaining // 60, remaining % 60
        mm_e, ss_e = elapsed // 60, elapsed % 60

        st.metric("残り", f"{mm_r:02d}:{ss_r:02d}")
        st.progress(min(1.0, elapsed / total_sec) if total_sec > 0 else 0.0)
        st.caption(f"経過 {mm_e:02d}:{ss_e:02d} / 合計 {int(b.get('minutes',0)):02d}:00")

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("▶ 開始", use_container_width=True, disabled=st.session_state.running):
                st.session_state.running = True
                st.session_state.last_tick = None
                st.session_state.run_total_sec = 0

                st.session_state.log.append({
                    "type": "start",
                    "time": now_str(),
                    "plan_start": b.get("start", ""),
                    "title": b.get("title", ""),
                    "minutes": int(b.get("minutes", 0)),
                    "tag": b.get("tag", ""),
                })
                save_json(LOG_PATH, st.session_state.log)
                st.rerun()

        with c2:
            if st.button("⏸ 停止", use_container_width=True, disabled=not st.session_state.running):
                st.session_state.running = False
                st.session_state.last_tick = None
                st.session_state.log.append({
                    "type": "pause",
                    "time": now_str(),
                    "title": b.get("title", ""),
                    "elapsed_sec": int(st.session_state.run_total_sec),
                })
                save_json(LOG_PATH, st.session_state.log)
                st.rerun()

        with c3:
            if st.button("✅ 完了", use_container_width=True, disabled=not plan):
                done_elapsed = int(st.session_state.run_total_sec) if st.session_state.running else 0
                st.session_state.running = False
                st.session_state.last_tick = None

                st.session_state.log.append({
                    "type": "done",
                    "time": now_str(),
                    "plan_start": b.get("start", ""),
                    "title": b.get("title", ""),
                    "minutes": int(b.get("minutes", 0)),
                    "elapsed_sec": done_elapsed,
                    "tag": b.get("tag", ""),
                    "note": b.get("note", ""),
                })
                save_json(LOG_PATH, st.session_state.log)

                # 次ブロックへ
                idx = st.session_state.current_block_id or 0
                if idx + 1 < len(plan):
                    st.session_state.current_block_id = idx + 1
                st.session_state.run_total_sec = 0

                st.success("完了！ご主人、ちゃんと前に進んでる。")
                st.rerun()

        st.divider()
        st.subheader("🗒️ 今日の履歴（直近）")
        logs = st.session_state.log
        if not logs:
            st.caption("まだ履歴がないよ。開始すると残る。")
        else:
            for item in reversed(logs[-30:]):
                t = item.get("time", "")
                typ = item.get("type", "")
                if typ == "start":
                    st.write(f"- {t} ▶ 開始：**{item.get('title','')}**（予定 {item.get('plan_start','')} / {item.get('minutes','')}分）")
                elif typ == "pause":
                    es = int(item.get("elapsed_sec", 0))
                    st.write(f"- {t} ⏸ 停止：**{item.get('title','')}**（経過 {es//60:02d}:{es%60:02d}）")
                elif typ == "done":
                    es = int(item.get("elapsed_sec", 0))
                    st.write(f"- {t} ✅ 完了：**{item.get('title','')}**（経過 {es//60:02d}:{es%60:02d}）")
                else:
                    st.write(f"- {t} {typ} {item}")

        st.divider()
        st.subheader("📤 エクスポート")
        st.download_button(
            "今日の予定JSONをダウンロード",
            data=json.dumps(st.session_state.plan, ensure_ascii=False, indent=2),
            file_name=f"plan_{TODAY}.json",
            mime="application/json",
            use_container_width=True,
        )
        st.download_button(
            "今日の履歴JSONをダウンロード",
            data=json.dumps(st.session_state.log, ensure_ascii=False, indent=2),
            file_name=f"log_{TODAY}.json",
            mime="application/json",
            use_container_width=True,
        )

st.caption("※ローカル保存：data/ に plan_YYYY-MM-DD.json と log_YYYY-MM-DD.json を作るよ。")
