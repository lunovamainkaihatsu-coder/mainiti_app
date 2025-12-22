# app.py
from __future__ import annotations

import csv
import datetime as dt
import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

APP_TITLE = "迷いもの熟成リスト（Buy or Wait）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "aged_items.json"

DEFAULT_STATUSES = ["迷い中", "買った", "見送り"]
DEFAULT_TAGS = ["ガジェット", "本", "ゲーム", "服", "趣味", "生活", "その他"]


@dataclass
class AgedItem:
    id: str
    name: str
    price: Optional[int]  # yen
    url: str
    memo: str
    tag: str
    status: str
    created_at: str  # ISO datetime

    @staticmethod
    def new(name: str, price: Optional[int], url: str, memo: str, tag: str, status: str) -> "AgedItem":
        return AgedItem(
            id=str(uuid.uuid4()),
            name=name.strip(),
            price=price,
            url=url.strip(),
            memo=memo.strip(),
            tag=tag.strip() or "その他",
            status=status.strip() or "迷い中",
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )


def load_items() -> List[AgedItem]:
    if not DATA_PATH.exists():
        return []
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        items: List[AgedItem] = []
        for r in raw:
            if not isinstance(r, dict):
                continue
            price = r.get("price", None)
            if price in ("", None):
                price_val = None
            else:
                try:
                    price_val = int(price)
                except Exception:
                    price_val = None

            items.append(
                AgedItem(
                    id=str(r.get("id", "")) or str(uuid.uuid4()),
                    name=str(r.get("name", "")),
                    price=price_val,
                    url=str(r.get("url", "")),
                    memo=str(r.get("memo", "")),
                    tag=str(r.get("tag", "")) or "その他",
                    status=str(r.get("status", "")) or "迷い中",
                    created_at=str(r.get("created_at", "")) or dt.datetime.now().isoformat(timespec="seconds"),
                )
            )
        return items
    except Exception:
        return []


def save_items(items: List[AgedItem]) -> None:
    DATA_PATH.write_text(json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2), encoding="utf-8")


def days_aged(created_at_iso: str) -> int:
    try:
        created = dt.datetime.fromisoformat(created_at_iso).date()
    except Exception:
        created = dt.date.today()
    return (dt.date.today() - created).days


def parse_price(s: str) -> Tuple[bool, Optional[int]]:
    s = s.strip()
    if not s:
        return True, None
    s2 = s.replace(",", "")
    if not s2.isdigit():
        return False, None
    return True, int(s2)


def to_csv_text(items: List[AgedItem]) -> str:
    rows: List[Dict[str, str]] = []
    for it in items:
        rows.append(
            {
                "id": it.id,
                "name": it.name,
                "price": "" if it.price is None else str(it.price),
                "url": it.url,
                "memo": it.memo,
                "tag": it.tag,
                "status": it.status,
                "created_at": it.created_at,
            }
        )
    if not rows:
        return "id,name,price,url,memo,tag,status,created_at\n"
    fieldnames = list(rows[0].keys())
    out = []
    out.append(",".join(fieldnames))
    for r in rows:
        line = []
        for fn in fieldnames:
            v = r.get(fn, "") or ""
            if any(ch in v for ch in [",", '"', "\n"]):
                v = '"' + v.replace('"', '""') + '"'
            line.append(v)
        out.append(",".join(line))
    return "\n".join(out)


def import_csv_text(csv_text: str) -> Tuple[List[AgedItem], List[str]]:
    errors: List[str] = []
    imported: List[AgedItem] = []
    try:
        reader = csv.DictReader(csv_text.splitlines())
        for idx, row in enumerate(reader, start=2):
            if not row:
                continue
            name = (row.get("name") or "").strip()
            if not name:
                errors.append(f"{idx}行目: name が空です")
                continue

            price_raw = (row.get("price") or "").strip()
            ok, price_val = parse_price(price_raw)
            if not ok:
                errors.append(f"{idx}行目: price が不正です: {price_raw}")
                continue

            imported.append(
                AgedItem(
                    id=((row.get("id") or "").strip() or str(uuid.uuid4())),
                    name=name,
                    price=price_val,
                    url=(row.get("url") or "").strip(),
                    memo=(row.get("memo") or "").strip(),
                    tag=((row.get("tag") or "").strip() or "その他"),
                    status=((row.get("status") or "").strip() or "迷い中"),
                    created_at=((row.get("created_at") or "").strip() or dt.datetime.now().isoformat(timespec="seconds")),
                )
            )
    except Exception as e:
        errors.append(f"CSV解析に失敗: {e}")
    return imported, errors


# =========================
# UI
# =========================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("買うか迷っているものを登録して“熟成”させる。時間が経っても欲しいなら買う。冷めたら見送り。")

# session_stateは[]アクセス（items衝突回避）
if "aged_items" not in st.session_state:
    st.session_state["aged_items"] = load_items()
items: List[AgedItem] = st.session_state["aged_items"]

# サイドバー
with st.sidebar:
    st.header("フィルタ")
    all_statuses = sorted(set([*DEFAULT_STATUSES, *[i.status for i in items if i.status]]))
    all_tags = sorted(set([*DEFAULT_TAGS, *[i.tag for i in items if i.tag]]))

    status_filter = st.multiselect("ステータス", options=all_statuses, default=[])
    tag_filter = st.multiselect("タグ", options=all_tags, default=[])
    keyword = st.text_input("検索（名前・メモ）", value="")
    sort_mode = st.radio("並び順", ["熟成が長い順", "新しい順", "価格が高い順", "価格が安い順"], index=0)

    st.divider()
    st.subheader("データ")
    st.write(f"保存先: `{DATA_PATH}`")
    if st.button("💾 保存（手動）"):
        save_items(items)
        st.success("保存したよ")


# 追加フォーム
st.subheader("➕ 追加")

with st.form("add_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([1.4, 0.6, 1.0])
    name = c1.text_input("名前（必須）", value="", placeholder="例：外付けSSD 1TB / 新刊○○")
    price_str = c2.text_input("価格（円・任意）", value="", placeholder="例：12800")
    tag = c3.selectbox("タグ", options=all_tags, index=all_tags.index("その他") if "その他" in all_tags else 0)

    url = st.text_input("URL（任意）", value="", placeholder="https:// ...")
    memo = st.text_area("メモ（任意）", value="", height=80)

    status = st.selectbox("ステータス", options=all_statuses, index=all_statuses.index("迷い中") if "迷い中" in all_statuses else 0)

    add = st.form_submit_button("✅ 追加して保存")

    if add:
        if not name.strip():
            st.error("名前は必須だよ！")
        else:
            ok, price_val = parse_price(price_str)
            if not ok:
                st.error("価格は数字だけ（カンマOK）で入れてね！")
            else:
                items.append(AgedItem.new(name=name, price=price_val, url=url, memo=memo, tag=tag, status=status))
                save_items(items)
                st.success("追加したよ！")
                st.rerun()

st.divider()
st.subheader("📋 一覧")

def apply_filters(items_: List[AgedItem]) -> List[AgedItem]:
    out = items_
    if status_filter:
        out = [i for i in out if i.status in status_filter]
    if tag_filter:
        out = [i for i in out if i.tag in tag_filter]
    if keyword.strip():
        k = keyword.strip().lower()
        out = [i for i in out if (k in i.name.lower()) or (k in i.memo.lower())]
    return out


def sort_items(items_: List[AgedItem]) -> List[AgedItem]:
    if sort_mode == "熟成が長い順":
        return sorted(items_, key=lambda i: days_aged(i.created_at), reverse=True)
    if sort_mode == "新しい順":
        return sorted(items_, key=lambda i: i.created_at, reverse=True)
    if sort_mode == "価格が高い順":
        return sorted(items_, key=lambda i: (-(i.price or -1), i.name.lower()))
    # 価格が安い順（Noneは最後）
    return sorted(items_, key=lambda i: (10**18 if i.price is None else i.price, i.name.lower()))


view_items = sort_items(apply_filters(items))

# メトリクス
m1, m2, m3, m4 = st.columns(4)
m1.metric("件数", f"{len(view_items)}")
m2.metric("迷い中", f"{len([i for i in view_items if i.status == '迷い中'])}")
m3.metric("買った", f"{len([i for i in view_items if i.status == '買った'])}")
m4.metric("見送り", f"{len([i for i in view_items if i.status == '見送り'])}")

if not view_items:
    st.info("まだ何もないか、フィルタ条件で0件だよ。")
else:
    for it in view_items:
        aged = days_aged(it.created_at)
        if it.status == "迷い中":
            badge = f"🫙 熟成 {aged}日"
        elif it.status == "買った":
            badge = f"✅ 購入（熟成 {aged}日）"
        else:
            badge = f"🧊 見送り（熟成 {aged}日）"

        with st.container(border=True):
            left, right = st.columns([1.3, 0.7], gap="large")
            with left:
                st.markdown(f"### {it.name}")
                st.write(f"**{badge}**　タグ：`{it.tag}`　ステータス：`{it.status}`")
                if it.price is None:
                    st.write("価格：—")
                else:
                    st.write(f"価格：**{it.price:,}円**")
                st.write(f"登録日：{it.created_at.split('T')[0]}")
                if it.url:
                    st.write(f"🔗 {it.url}")
                if it.memo:
                    st.write(it.memo)

            with right:
                with st.expander("✏️ 編集 / 🗑 削除", expanded=False):
                    with st.form(f"edit_{it.id}"):
                        new_name = st.text_input("名前", value=it.name)
                        new_price = st.text_input("価格（円・任意）", value="" if it.price is None else str(it.price))
                        new_tag = st.text_input("タグ", value=it.tag)
                        new_status = st.text_input("ステータス", value=it.status)
                        new_url = st.text_input("URL", value=it.url)
                        new_memo = st.text_area("メモ", value=it.memo, height=80)

                        a, b = st.columns(2)
                        do_update = a.form_submit_button("💾 更新")
                        do_delete = b.form_submit_button("🗑 削除")

                        if do_update:
                            if not new_name.strip():
                                st.error("名前は必須！")
                            else:
                                ok, price_val = parse_price(new_price)
                                if not ok:
                                    st.error("価格は数字だけ（カンマOK）！")
                                else:
                                    it.name = new_name.strip()
                                    it.price = price_val
                                    it.tag = new_tag.strip() or "その他"
                                    it.status = new_status.strip() or "迷い中"
                                    it.url = new_url.strip()
                                    it.memo = new_memo.strip()
                                    save_items(items)
                                    st.success("更新したよ！")
                                    st.rerun()

                        if do_delete:
                            st.session_state["aged_items"] = [x for x in items if x.id != it.id]
                            save_items(st.session_state["aged_items"])
                            st.success("削除したよ！")
                            st.rerun()

st.divider()
st.subheader("📦 CSV 入出力")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown("#### ⬇️ エクスポート")
    csv_text = to_csv_text(items)
    st.download_button(
        "⬇️ CSVをダウンロード",
        data=csv_text.encode("utf-8"),
        file_name="buy_or_wait.csv",
        mime="text/csv",
        use_container_width=True,
    )

with c2:
    st.markdown("#### ⬆️ インポート（追加）")
    up = st.file_uploader("CSVファイル", type=["csv"])
    pasted = st.text_area("CSV貼り付け（任意）", value="", height=140)
    if st.button("⬆️ 取り込む（追加）", use_container_width=True):
        txt = ""
        if up is not None:
            txt = up.read().decode("utf-8", errors="replace")
        elif pasted.strip():
            txt = pasted.strip()

        if not txt:
            st.warning("CSVがないよ！")
        else:
            imported, errs = import_csv_text(txt)
            if errs:
                st.error("エラー：\n- " + "\n- ".join(errs))
            else:
                # id重複は回避
                existing = {i.id for i in items}
                for it in imported:
                    if it.id in existing:
                        it.id = str(uuid.uuid4())
                    items.append(it)
                save_items(items)
                st.success(f"{len(imported)}件 追加したよ！")
                st.rerun()

with st.expander("⚠️ 危険：全削除", expanded=False):
    st.warning("元に戻せません。")
    if st.button("🧨 全データ削除", type="primary"):
        st.session_state["aged_items"] = []
        save_items([])
        st.success("全削除しました。")
        st.rerun()
