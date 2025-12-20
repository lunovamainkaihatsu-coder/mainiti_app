# app.py
from __future__ import annotations

import csv
import datetime as dt
import json
import re
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st

# =========================
# 基本設定
# =========================
APP_TITLE = "ReleaseList（発売日リスト）"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_PATH = DATA_DIR / "releases.json"

DEFAULT_CATEGORIES = ["ゲーム", "本", "映画", "アニメ", "ガジェット", "グッズ", "イベント", "その他"]
DEFAULT_STATUSES = ["検討", "予約済", "購入済", "見送り", "完了"]

# OGP抽出（超簡易）
META_OG_TITLE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.I)
META_OG_IMAGE = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']', re.I)
TITLE_TAG = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


# =========================
# データモデル
# =========================
@dataclass
class ReleaseItem:
    id: str
    title: str
    release_date: str  # "YYYY-MM-DD" or ""
    category: str
    status: str
    url: str
    image_url: str
    memo: str
    created_at: str  # ISO

    @staticmethod
    def new(
        title: str,
        release_date: str,
        category: str,
        status: str,
        url: str,
        image_url: str,
        memo: str,
    ) -> "ReleaseItem":
        return ReleaseItem(
            id=str(uuid.uuid4()),
            title=title.strip(),
            release_date=release_date.strip(),
            category=category.strip(),
            status=status.strip(),
            url=url.strip(),
            image_url=image_url.strip(),
            memo=memo.strip(),
            created_at=dt.datetime.now().isoformat(timespec="seconds"),
        )


# =========================
# ユーティリティ
# =========================
def load_items() -> List[ReleaseItem]:
    if not DATA_PATH.exists():
        return []
    try:
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        items: List[ReleaseItem] = []
        for r in raw:
            if isinstance(r, dict):
                items.append(
                    ReleaseItem(
                        id=str(r.get("id", "")),
                        title=str(r.get("title", "")),
                        release_date=str(r.get("release_date", "")),
                        category=str(r.get("category", "")),
                        status=str(r.get("status", "")),
                        url=str(r.get("url", "")),
                        image_url=str(r.get("image_url", "")),
                        memo=str(r.get("memo", "")),
                        created_at=str(r.get("created_at", "")),
                    )
                )
        for it in items:
            if not it.id:
                it.id = str(uuid.uuid4())
        return items
    except Exception:
        return []


def save_items(items: List[ReleaseItem]) -> None:
    DATA_PATH.write_text(
        json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_date_yyyy_mm_dd(s: str) -> Tuple[bool, str]:
    s = s.strip()
    if not s:
        return True, ""  # 未定OK
    try:
        dt.datetime.strptime(s, "%Y-%m-%d")
        return True, s
    except ValueError:
        return False, ""


def days_until(date_str: str) -> Optional[int]:
    if not date_str:
        return None
    try:
        d = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        today = dt.date.today()
        return (d - today).days
    except Exception:
        return None


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def fetch_title_and_image(url: str, timeout_sec: int = 8) -> Tuple[str, str, str]:
    """
    超簡易URL補完：
    - og:title / og:image を優先
    - なければ <title>
    戻り値: (title, image_url, error_message)
    """
    url = url.strip()
    if not url:
        return "", "", "URLが空です"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (ReleaseList bot; +https://example.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        r = requests.get(url, headers=headers, timeout=timeout_sec)
        r.raise_for_status()
        html = r.text

        ogt = META_OG_TITLE.search(html)
        ogi = META_OG_IMAGE.search(html)
        ttag = TITLE_TAG.search(html)

        title = ""
        image_url = ""

        if ogt:
            title = normalize_ws(ogt.group(1))
        elif ttag:
            title = normalize_ws(ttag.group(1))

        if ogi:
            image_url = normalize_ws(ogi.group(1))

        if not title and not image_url:
            return "", "", "タイトル/画像を取得できませんでした（ページがJS生成の可能性）"
        return title, image_url, ""
    except Exception as e:
        return "", "", f"取得に失敗: {e}"


def to_csv_rows(items: List[ReleaseItem]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for it in items:
        rows.append(
            {
                "id": it.id,
                "title": it.title,
                "release_date": it.release_date,
                "category": it.category,
                "status": it.status,
                "url": it.url,
                "image_url": it.image_url,
                "memo": it.memo,
                "created_at": it.created_at,
            }
        )
    return rows


def import_csv_text(csv_text: str) -> Tuple[List[ReleaseItem], List[str]]:
    errors: List[str] = []
    items: List[ReleaseItem] = []

    try:
        reader = csv.DictReader(csv_text.splitlines())
        for idx, row in enumerate(reader, start=2):
            if not row:
                continue
            title = (row.get("title") or "").strip()
            if not title:
                errors.append(f"{idx}行目: title が空です")
                continue

            rd_raw = (row.get("release_date") or "").strip()
            ok, rd = parse_date_yyyy_mm_dd(rd_raw)
            if not ok:
                errors.append(f"{idx}行目: release_date が不正です（YYYY-MM-DD）: {rd_raw}")
                continue

            item = ReleaseItem(
                id=((row.get("id") or "").strip() or str(uuid.uuid4())),
                title=title,
                release_date=rd,
                category=(row.get("category") or "その他").strip() or "その他",
                status=(row.get("status") or "検討").strip() or "検討",
                url=(row.get("url") or "").strip(),
                image_url=(row.get("image_url") or "").strip(),
                memo=(row.get("memo") or "").strip(),
                created_at=(row.get("created_at") or dt.datetime.now().isoformat(timespec="seconds")).strip(),
            )
            items.append(item)
    except Exception as e:
        errors.append(f"CSVの解析に失敗: {e}")

    return items, errors


# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("手動登録＋URL自動補完（タイトル/サムネ）で、発売予定をまとめる簡易アプリ。")

# ✅ ここが重要：session_stateは必ず [] でアクセスする
if "items" not in st.session_state:
    st.session_state["items"] = load_items()

items: List[ReleaseItem] = st.session_state["items"]

# サイドバー：フィルタ
with st.sidebar:
    st.header("フィルタ")
    all_categories = sorted(set([*DEFAULT_CATEGORIES, *[i.category for i in items if i.category]]))
    all_statuses = sorted(set([*DEFAULT_STATUSES, *[i.status for i in items if i.status]]))

    cat_sel = st.multiselect("カテゴリ", options=all_categories, default=[])
    st_sel = st.multiselect("ステータス", options=all_statuses, default=[])
    keyword = st.text_input("検索（タイトル・メモ）", value="")
    show_tbd_only = st.checkbox("発売日未定（TBD）だけ", value=False)
    sort_mode = st.radio("並び順", ["発売日が近い順", "追加が新しい順", "タイトル順"], index=0)

    st.divider()
    st.subheader("データ")
    st.write(f"保存先: `{DATA_PATH}`")
    if st.button("💾 保存（手動）"):
        save_items(items)
        st.success("保存しました")

# 追加フォーム
st.subheader("➕ 追加 / URL自動補完")

colA, colB = st.columns([1.2, 1.0], gap="large")

with colA:
    with st.form("add_form", clear_on_submit=False):
        url = st.text_input("URL（任意・貼ると自動補完）", value="", placeholder="https:// ...")
        auto_btn = st.form_submit_button("🔎 URLから補完（タイトル/サムネ）")

        if auto_btn:
            t, img, err = fetch_title_and_image(url)
            if err:
                st.warning(err)
            if t:
                st.session_state["draft_title"] = t
            if img:
                st.session_state["draft_image_url"] = img
            st.session_state["draft_url"] = url

    draft_title = st.session_state.get("draft_title", "")
    draft_image_url = st.session_state.get("draft_image_url", "")
    draft_url = st.session_state.get("draft_url", "")

    with st.form("save_form", clear_on_submit=True):
        title = st.text_input("タイトル", value=draft_title, placeholder="例：新作ゲーム○○ / 新刊△△")
        release_date = st.text_input("発売日（YYYY-MM-DD / 未定なら空）", value="", placeholder="2026-01-15")
        category = st.selectbox("カテゴリ", options=all_categories, index=all_categories.index("ゲーム") if "ゲーム" in all_categories else 0)
        status = st.selectbox("ステータス", options=all_statuses, index=all_statuses.index("検討") if "検討" in all_statuses else 0)
        memo = st.text_area("メモ（価格、予約先、優先度など）", value="", height=90)
        url2 = st.text_input("URL（保存用）", value=draft_url)
        image_url = st.text_input("サムネURL（自動で入ることあり）", value=draft_image_url)

        save_btn = st.form_submit_button("✅ 追加して保存")

        if save_btn:
            ok, rd = parse_date_yyyy_mm_dd(release_date)
            if not title.strip():
                st.error("タイトルは必須だよ！")
            elif not ok:
                st.error("発売日は YYYY-MM-DD 形式（例：2026-01-15）か、未定なら空でOK！")
            else:
                new_item = ReleaseItem.new(
                    title=title,
                    release_date=rd,
                    category=category,
                    status=status,
                    url=url2,
                    image_url=image_url,
                    memo=memo,
                )
                items.append(new_item)
                save_items(items)

                st.session_state["draft_title"] = ""
                st.session_state["draft_image_url"] = ""
                st.session_state["draft_url"] = ""

                st.success("追加したよ！")

with colB:
    st.markdown("#### プレビュー（サムネが取れた場合）")
    preview_url = st.session_state.get("draft_url", "")
    preview_img = st.session_state.get("draft_image_url", "")
    preview_title = st.session_state.get("draft_title", "")

    if preview_title:
        st.write(f"**{preview_title}**")
    if preview_img:
        st.image(preview_img, use_container_width=True)
    if preview_url:
        st.write(preview_url)
    if not (preview_title or preview_img or preview_url):
        st.info("URL補完をすると、ここにプレビューが出るよ。")

st.divider()

# 一覧表示
st.subheader("📋 一覧")

def filter_items(items_: List[ReleaseItem]) -> List[ReleaseItem]:
    out = items_
    if cat_sel:
        out = [i for i in out if i.category in cat_sel]
    if st_sel:
        out = [i for i in out if i.status in st_sel]
    if keyword.strip():
        k = keyword.strip().lower()
        out = [i for i in out if (k in i.title.lower()) or (k in i.memo.lower())]
    if show_tbd_only:
        out = [i for i in out if not i.release_date]
    return out

def sort_items(items_: List[ReleaseItem]) -> List[ReleaseItem]:
    if sort_mode == "発売日が近い順":
        def key(i: ReleaseItem):
            d = days_until(i.release_date)
            return (999999 if d is None else d, i.title.lower())
        return sorted(items_, key=key)
    if sort_mode == "追加が新しい順":
        return sorted(items_, key=lambda i: i.created_at, reverse=True)
    return sorted(items_, key=lambda i: i.title.lower())

view_items = sort_items(filter_items(items))

c1, c2, c3, c4 = st.columns(4)
c1.metric("件数", f"{len(view_items)}")
soon = [i for i in view_items if (days_until(i.release_date) is not None and 0 <= days_until(i.release_date) <= 7)]
c2.metric("7日以内", f"{len(soon)}")
tbd = [i for i in view_items if not i.release_date]
c3.metric("未定(TBD)", f"{len(tbd)}")
over = [i for i in view_items if (days_until(i.release_date) is not None and days_until(i.release_date) < 0)]
c4.metric("発売済(過去日)", f"{len(over)}")

if not view_items:
    st.info("条件に一致するデータがないよ。左でフィルタを調整してね。")
else:
    for it in view_items:
        d = days_until(it.release_date)
        if d is None:
            badge = "🟦 TBD"
        elif d < 0:
            badge = f"🟨 発売済（{abs(d)}日前）"
        elif d == 0:
            badge = "🔥 今日！"
        elif d <= 7:
            badge = f"🔥 もうすぐ（あと{d}日）"
        else:
            badge = f"⏳ あと{d}日"

        with st.container(border=True):
            left, right = st.columns([1.2, 0.8], gap="large")

            with left:
                st.markdown(f"### {it.title}")
                st.write(f"**{badge}**")
                st.write(f"カテゴリ：`{it.category}`　／　ステータス：`{it.status}`")
                st.write(f"発売日：**{it.release_date or '未定'}**")
                if it.url:
                    st.write(f"🔗 {it.url}")
                if it.memo:
                    st.write(it.memo)

            with right:
                if it.image_url:
                    st.image(it.image_url, use_container_width=True)

                with st.expander("✏️ 編集 / 🗑 削除", expanded=False):
                    with st.form(f"edit_{it.id}"):
                        new_title = st.text_input("タイトル", value=it.title)
                        new_release_date = st.text_input("発売日（YYYY-MM-DD / 未定なら空）", value=it.release_date)
                        new_category = st.text_input("カテゴリ", value=it.category)
                        new_status = st.text_input("ステータス", value=it.status)
                        new_url = st.text_input("URL", value=it.url)
                        new_image_url = st.text_input("サムネURL", value=it.image_url)
                        new_memo = st.text_area("メモ", value=it.memo, height=90)

                        colx, coly = st.columns(2)
                        update = colx.form_submit_button("💾 更新")
                        delete = coly.form_submit_button("🗑 削除")

                        if update:
                            ok, rd = parse_date_yyyy_mm_dd(new_release_date)
                            if not new_title.strip():
                                st.error("タイトルは必須だよ！")
                            elif not ok:
                                st.error("発売日は YYYY-MM-DD 形式か、未定なら空！")
                            else:
                                it.title = new_title.strip()
                                it.release_date = rd
                                it.category = new_category.strip() or "その他"
                                it.status = new_status.strip() or "検討"
                                it.url = new_url.strip()
                                it.image_url = new_image_url.strip()
                                it.memo = new_memo.strip()
                                save_items(items)
                                st.success("更新したよ！")
                                st.rerun()

                        if delete:
                            st.session_state["items"] = [x for x in items if x.id != it.id]
                            save_items(st.session_state["items"])
                            st.success("削除したよ！")
                            st.rerun()

st.divider()

# CSV入出力
st.subheader("📦 CSV 入出力（バックアップ / 移行）")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### ⬇️ エクスポート")
    rows = to_csv_rows(items)
    csv_buf = []
    if rows:
        fieldnames = list(rows[0].keys())
        csv_buf.append(",".join(fieldnames))
        for r in rows:
            line = []
            for fn in fieldnames:
                v = (r.get(fn) or "")
                if any(ch in v for ch in [",", '"', "\n"]):
                    v = '"' + v.replace('"', '""') + '"'
                line.append(v)
            csv_buf.append(",".join(line))
    csv_text = "\n".join(csv_buf) if csv_buf else "id,title,release_date,category,status,url,image_url,memo,created_at\n"

    st.download_button(
        label="⬇️ CSVをダウンロード",
        data=csv_text.encode("utf-8"),
        file_name="releaselist.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col2:
    st.markdown("#### ⬆️ インポート")
    st.caption("CSVの中身を貼り付けるか、ファイルをアップロードして取り込みできます。")
    up = st.file_uploader("CSVファイル", type=["csv"])
    pasted = st.text_area("CSVを貼り付け（任意）", value="", height=160)

    import_btn = st.button("⬆️ 取り込む（上書きではなく追加）", use_container_width=True)

    if import_btn:
        csv_text_in = ""
        if up is not None:
            csv_text_in = up.read().decode("utf-8", errors="replace")
        elif pasted.strip():
            csv_text_in = pasted.strip()

        if not csv_text_in:
            st.warning("CSVがないよ！アップロードか貼り付けをしてね。")
        else:
            new_items, errs = import_csv_text(csv_text_in)
            if errs:
                st.error("エラーがあるよ：\n- " + "\n- ".join(errs))
            else:
                existing_ids = {i.id for i in items}
                for ni in new_items:
                    if ni.id in existing_ids:
                        ni.id = str(uuid.uuid4())
                    items.append(ni)
                save_items(items)
                st.success(f"{len(new_items)}件取り込んだよ！")
                st.rerun()

st.divider()

with st.expander("⚠️ 危険：全データ削除", expanded=False):
    st.warning("この操作は元に戻せません。")
    if st.button("🧨 全削除する", type="primary"):
        st.session_state["items"] = []
        save_items([])
        st.success("全削除しました。")
        st.rerun()
