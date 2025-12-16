import streamlit as st
import json
from pathlib import Path
from datetime import date
from typing import Dict, Any, List

APP_TITLE = "🎍 お年玉管理（大人向け）"
DATA_FILE = Path(__file__).parent / "otoshidama_data.json"


# -----------------------------
# 保存 / 読み込み
# -----------------------------
def default_state() -> Dict[str, Any]:
    return {
        "children": ["子どもA"],
        "received": [],  # {child, from, amount, d, memo}
        "spent": [],     # {child, category, amount, d, memo}
        "rules": {},     # child -> {spend_type, spend_value, save_type, save_value}
        "given": [],     # {to, amount, d, relation, memo}
    }


def load_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default_state()


def save_data(data: Dict[str, Any]) -> None:
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def money(n: int) -> str:
    return f"¥{n:,}"


def safe_int(x, default=0) -> int:
    try:
        return int(x)
    except Exception:
        return default


# -----------------------------
# 集計
# -----------------------------
def sum_received(data: Dict[str, Any], child: str) -> int:
    return sum(r["amount"] for r in data["received"] if r["child"] == child)


def sum_spent(data: Dict[str, Any], child: str) -> int:
    return sum(s["amount"] for s in data["spent"] if s["child"] == child)


def get_rule(data: Dict[str, Any], child: str) -> Dict[str, Any]:
    # ルールが未設定ならデフォルト
    rule = data.get("rules", {}).get(child)
    if not rule:
        rule = {
            "spend_type": "fixed",    # fixed or percent
            "spend_value": 5000,      # 円 or %
            "save_type": "percent",   # fixed or percent
            "save_value": 50,         # 円 or %
        }
    return rule


def calc_allowances(total_received: int, rule: Dict[str, Any]) -> Dict[str, int]:
    # 使ってOK
    if rule["spend_type"] == "fixed":
        spend_ok = max(0, safe_int(rule["spend_value"], 0))
    else:
        pct = max(0, min(100, safe_int(rule["spend_value"], 0)))
        spend_ok = (total_received * pct) // 100

    # 貯金
    if rule["save_type"] == "fixed":
        save = max(0, safe_int(rule["save_value"], 0))
    else:
        pct = max(0, min(100, safe_int(rule["save_value"], 0)))
        save = (total_received * pct) // 100

    # かぶり調整：合計が総額を超えたら縮める（貯金を優先して残す）
    if spend_ok + save > total_received:
        spend_ok = max(0, total_received - save)

    parent_hold = max(0, total_received - spend_ok - save)
    return {"spend_ok": spend_ok, "save": save, "parent_hold": parent_hold}


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("今年いくらもらって、いくら使ってOKか、いくら貯金に回すか、そして誰にいくら渡したかを管理するアプリ。データはローカルJSONに保存。")

data = load_data()

# Sidebar: 子ども管理
with st.sidebar:
    st.subheader("👪 子ども管理")
    if "children" not in data:
        data["children"] = ["子どもA"]

    col1, col2 = st.columns([2, 1])
    with col1:
        new_child = st.text_input("子どもを追加", placeholder="例：娘 / 長男 / 〇〇")
    with col2:
        if st.button("追加", use_container_width=True):
            name = (new_child or "").strip()
            if name and name not in data["children"]:
                data["children"].append(name)
                save_data(data)
                st.success(f"追加したよ：{name}")
                st.rerun()

    if data["children"]:
        remove_target = st.selectbox("削除（注意：記録は残る）", options=["（選択）"] + data["children"])
        if st.button("この子を削除", use_container_width=True):
            if remove_target != "（選択）" and remove_target in data["children"]:
                data["children"].remove(remove_target)
                save_data(data)
                st.warning(f"削除したよ：{remove_target}")
                st.rerun()

    st.divider()
    st.subheader("💾 データ")
    st.write(f"保存先：`{DATA_FILE.name}`")
    if st.button("データを初期化（全削除）", type="secondary", use_container_width=True):
        data = default_state()
        save_data(data)
        st.error("データを初期化したよ（全削除）")
        st.rerun()


tab1, tab2, tab3 = st.tabs(["① 子どものお年玉", "② 渡したお年玉", "③ 一覧・エクスポート"])

# -----------------------------
# ① 子どものお年玉
# -----------------------------
with tab1:
    if not data["children"]:
        st.info("まずは左のサイドバーで子どもを追加してね。")
    else:
        selected_child = st.selectbox("対象の子ども", options=data["children"])

        # 集計
        total_r = sum_received(data, selected_child)
        total_s = sum_spent(data, selected_child)
        rule = get_rule(data, selected_child)
        allowances = calc_allowances(total_r, rule)
        spend_ok = allowances["spend_ok"]
        save_amt = allowances["save"]
        parent_hold = allowances["parent_hold"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("合計もらった", money(total_r))
        c2.metric("合計使った", money(total_s))
        c3.metric("残高（現時点）", money(max(0, total_r - total_s)))
        c4.metric("使ってOK枠（ルール）", money(spend_ok))

        st.divider()

        left, right = st.columns([1, 1])

        # ルール設定
        with left:
            st.subheader("🧾 ルール（この子の使ってOK / 貯金 / 親管理）")
            spend_type = st.radio(
                "使ってOKの決め方",
                options=["固定額（円）", "割合（%）"],
                index=0 if rule["spend_type"] == "fixed" else 1,
                horizontal=True,
            )
            if spend_type == "固定額（円）":
                spend_value = st.number_input("使ってOK（円）", min_value=0, step=500, value=safe_int(rule["spend_value"], 5000))
                _spend_type = "fixed"
                _spend_value = int(spend_value)
            else:
                spend_value = st.number_input("使ってOK（%）", min_value=0, max_value=100, step=5, value=max(0, min(100, safe_int(rule["spend_value"], 30))))
                _spend_type = "percent"
                _spend_value = int(spend_value)

            save_type = st.radio(
                "貯金の決め方",
                options=["固定額（円）", "割合（%）"],
                index=0 if rule["save_type"] == "fixed" else 1,
                horizontal=True,
            )
            if save_type == "固定額（円）":
                save_value = st.number_input("貯金（円）", min_value=0, step=500, value=safe_int(rule["save_value"], 0))
                _save_type = "fixed"
                _save_value = int(save_value)
            else:
                save_value = st.number_input("貯金（%）", min_value=0, max_value=100, step=5, value=max(0, min(100, safe_int(rule["save_value"], 50))))
                _save_type = "percent"
                _save_value = int(save_value)

            if st.button("この子のルールを保存", use_container_width=True):
                data.setdefault("rules", {})
                data["rules"][selected_child] = {
                    "spend_type": _spend_type,
                    "spend_value": _spend_value,
                    "save_type": _save_type,
                    "save_value": _save_value,
                }
                save_data(data)
                st.success("保存したよ！")
                st.rerun()

            # ルール適用後の内訳
            rule_now = get_rule(data, selected_child)
            allowances_now = calc_allowances(total_r, rule_now)
            st.info(
                f"ルール内訳（総額 {money(total_r)}）\n\n"
                f"- 使ってOK：{money(allowances_now['spend_ok'])}\n"
                f"- 貯金：{money(allowances_now['save'])}\n"
                f"- 親管理：{money(allowances_now['parent_hold'])}"
            )

        # 入力（もらった・使った）
        with right:
            st.subheader("📝 記録を追加")

            subtab_a, subtab_b = st.tabs(["もらったを追加", "使ったを追加"])

            with subtab_a:
                d = st.date_input("日付", value=date.today(), key="recv_date")
                from_person = st.text_input("誰から", placeholder="例：じいじ / ばあば / おじさん", key="recv_from")
                amount = st.number_input("金額（円）", min_value=0, step=500, value=1000, key="recv_amount")
                memo = st.text_input("メモ（任意）", placeholder="例：帰省で / お正月会食で", key="recv_memo")

                if st.button("＋ 追加（もらった）", use_container_width=True):
                    if (from_person or "").strip() and int(amount) > 0:
                        data["received"].append({
                            "child": selected_child,
                            "from": from_person.strip(),
                            "amount": int(amount),
                            "d": str(d),
                            "memo": (memo or "").strip()
                        })
                        save_data(data)
                        st.success("追加したよ！")
                        st.rerun()
                    else:
                        st.warning("「誰から」と「金額」を入れてね。")

            with subtab_b:
                d2 = st.date_input("日付", value=date.today(), key="spent_date")
                category = st.text_input("使い道", placeholder="例：おもちゃ / 本 / ゲーム / お菓子", key="spent_cat")
                amount2 = st.number_input("金額（円）", min_value=0, step=500, value=500, key="spent_amount")
                memo2 = st.text_input("メモ（任意）", placeholder="例：本人希望 / セールだった", key="spent_memo")

                if st.button("＋ 追加（使った）", use_container_width=True):
                    if (category or "").strip() and int(amount2) > 0:
                        data["spent"].append({
                            "child": selected_child,
                            "category": category.strip(),
                            "amount": int(amount2),
                            "d": str(d2),
                            "memo": (memo2 or "").strip()
                        })
                        save_data(data)
                        st.success("追加したよ！")
                        st.rerun()
                    else:
                        st.warning("「使い道」と「金額」を入れてね。")

        st.divider()

        # アラート
        st.subheader("🚦 アラート")
        balance = max(0, total_r - total_s)
        if total_s > total_r:
            st.error("使った金額が、もらった総額を超えてるよ！記録ミスかも。")
        else:
            # 使ってOK枠を超えたら注意
            if total_s > spend_ok:
                st.warning(
                    f"使ってOK枠（{money(spend_ok)}）を超えてるよ。"
                    f" 今の使用額：{money(total_s)} / 超過：{money(total_s - spend_ok)}"
                )
            else:
                st.success("ルール範囲内だよ。")

        st.caption(f"現在残高：{money(balance)} / ルール上の貯金目安：{money(save_amt)} / 親管理目安：{money(parent_hold)}")

        st.divider()

        # 明細表示＆削除
        st.subheader("📚 明細（この子）")

        colA, colB = st.columns(2)

        with colA:
            st.markdown("### もらった")
            recv_rows = [r for r in data["received"] if r["child"] == selected_child]
            if recv_rows:
                for i, r in enumerate(recv_rows[::-1], start=1):
                    with st.container(border=True):
                        st.write(f"**{r['d']}**  {r['from']}  —  **{money(r['amount'])}**")
                        if r.get("memo"):
                            st.caption(r["memo"])
                        if st.button("削除（この行）", key=f"del_recv_{selected_child}_{len(recv_rows)-i}"):
                            # 元の順序のindexを求める
                            idx = data["received"].index(r)
                            data["received"].pop(idx)
                            save_data(data)
                            st.rerun()
            else:
                st.info("まだ記録がないよ。")

        with colB:
            st.markdown("### 使った")
            spent_rows = [s for s in data["spent"] if s["child"] == selected_child]
            if spent_rows:
                for i, s in enumerate(spent_rows[::-1], start=1):
                    with st.container(border=True):
                        st.write(f"**{s['d']}**  {s['category']}  —  **{money(s['amount'])}**")
                        if s.get("memo"):
                            st.caption(s["memo"])
                        if st.button("削除（この行）", key=f"del_spent_{selected_child}_{len(spent_rows)-i}"):
                            idx = data["spent"].index(s)
                            data["spent"].pop(idx)
                            save_data(data)
                            st.rerun()
            else:
                st.info("まだ記録がないよ。")


# -----------------------------
# ② 渡したお年玉
# -----------------------------
with tab2:
    st.subheader("🧧 渡したお年玉（親の支出管理）")

    total_given = sum(g["amount"] for g in data["given"])
    st.metric("合計支出", money(total_given))

    st.divider()

    left, right = st.columns([1, 1])

    with left:
        st.markdown("### 追加")
        d = st.date_input("日付", value=date.today(), key="given_date")
        to = st.text_input("誰にあげた", placeholder="例：甥（太郎）/ 姪（花子）", key="given_to")
        relation = st.text_input("関係（任意）", placeholder="例：兄の子 / 友人の子", key="given_rel")
        amt = st.number_input("金額（円）", min_value=0, step=500, value=1000, key="given_amount")
        memo = st.text_input("メモ（任意）", placeholder="例：今年は増やした / 来年同額で", key="given_memo")

        if st.button("＋ 追加（渡した）", use_container_width=True):
            if (to or "").strip() and int(amt) > 0:
                data["given"].append({
                    "to": to.strip(),
                    "relation": (relation or "").strip(),
                    "amount": int(amt),
                    "d": str(d),
                    "memo": (memo or "").strip()
                })
                save_data(data)
                st.success("追加したよ！")
                st.rerun()
            else:
                st.warning("「誰にあげた」と「金額」を入れてね。")

    with right:
        st.markdown("### 明細")
        if data["given"]:
            for i, g in enumerate(data["given"][::-1], start=1):
                with st.container(border=True):
                    title = f"**{g['d']}**  {g['to']}  —  **{money(g['amount'])}**"
                    st.write(title)
                    meta = []
                    if g.get("relation"):
                        meta.append(f"関係：{g['relation']}")
                    if g.get("memo"):
                        meta.append(f"メモ：{g['memo']}")
                    if meta:
                        st.caption(" / ".join(meta))

                    if st.button("削除（この行）", key=f"del_given_{len(data['given'])-i}"):
                        idx = data["given"].index(g)
                        data["given"].pop(idx)
                        save_data(data)
                        st.rerun()
        else:
            st.info("まだ記録がないよ。")


# -----------------------------
# ③ 一覧・エクスポート
# -----------------------------
with tab3:
    st.subheader("📦 一覧・エクスポート")

    st.markdown("### 現在のデータ（JSON）")
    st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")

    st.download_button(
        label="⬇️ JSONをダウンロード",
        data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="otoshidama_data.json",
        mime="application/json",
        use_container_width=True,
    )

    st.markdown("### ざっくりサマリー")
    # 子ども別まとめ
    if data["children"]:
        for child in data["children"]:
            total_r = sum_received(data, child)
            total_s = sum_spent(data, child)
            rule = get_rule(data, child)
            alw = calc_allowances(total_r, rule)
            st.write(
                f"- **{child}**：もらった {money(total_r)} / 使った {money(total_s)} / "
                f"残 {money(max(0, total_r - total_s))} / 使ってOK {money(alw['spend_ok'])} / "
                f"貯金目安 {money(alw['save'])} / 親管理 {money(alw['parent_hold'])}"
            )

    st.write(f"- **渡した合計**：{money(sum(g['amount'] for g in data['given']))}")
    st.caption("このまま“来年のテンプレ”としても使えるよ。")
