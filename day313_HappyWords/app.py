
import json
import os
import random
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# 基本設定
# =========================================================

st.set_page_config(
    page_title="言われてうれしかった言葉",
    page_icon="💬",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "messages.json"

CATEGORIES = [
    "🌸 褒め言葉",
    "💪 励まし",
    "🙏 感謝",
    "❤️ 愛情",
    "🌱 成長",
    "😂 笑顔になった",
    "🧭 人生のヒント",
    "📦 その他",
]

SOURCES = [
    "👥 誰かからの言葉",
    "💌 自分からの言葉",
]


# =========================================================
# 共通関数
# =========================================================

def uid():
    return str(uuid.uuid4())


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def today_iso():
    return date.today().isoformat()


def parse_date(value):
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def stars(value):
    n = max(0, min(5, int(value)))
    return "★" * n + "☆" * (5 - n)


def signed(value):
    return f"{value:+d}"


def average_label(value):
    return f"{value:.1f}" if value is not None else "—"


def choice_index(value, choices):
    return choices.index(value) if value in choices else 0


def empty_data():
    return {
        "messages": [],
        "rereads": [],
    }


def validate_data(obj):
    if not isinstance(obj, dict):
        raise ValueError("JSON全体がオブジェクトではありません。")

    for key in ("messages", "rereads"):
        if key not in obj or not isinstance(obj[key], list):
            raise ValueError(f"{key} が配列ではありません。")

        if any(not isinstance(x, dict) for x in obj[key]):
            raise ValueError(f"{key} に不正なデータがあります。")

    ids = []

    for key in ("messages", "rereads"):
        for item in obj[key]:
            item_id = item.get("id")

            if not isinstance(item_id, str) or not item_id:
                raise ValueError(f"{key} にIDのない記録があります。")

            ids.append(item_id)

    if len(ids) != len(set(ids)):
        raise ValueError("IDが重複しています。")

    message_ids = {m["id"] for m in obj["messages"]}

    for m in obj["messages"]:
        if not isinstance(m.get("text"), str):
            raise ValueError("言葉の内容が不正です。")

        rating = m.get("importance")
        if type(rating) is not int or not 1 <= rating <= 5:
            raise ValueError("心に残った度は1〜5の整数です。")

    for r in obj["rereads"]:
        if r.get("message_id") not in message_ids:
            raise ValueError(
                "存在しない言葉に紐づく読み返し履歴があります。"
            )

        for field in ("mood_before", "mood_after"):
            value = r.get(field)
            if type(value) is not int or not 1 <= value <= 5:
                raise ValueError(
                    f"{field} は1〜5の整数です。"
                )

    return obj


def save_data(obj):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".tmp")

    with temp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    os.replace(temp, DATA_FILE)


def load_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        obj = empty_data()
        save_data(obj)
        return obj

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            obj = json.load(f)

        return validate_data(obj)

    except (OSError, ValueError, TypeError) as exc:
        st.error(
            "保存データを読み込めませんでした。"
            "既存ファイルは上書きせず保護しています。"
        )
        st.code(str(exc))
        st.stop()


def message_by_id(message_id):
    return next(
        (
            m for m in data["messages"]
            if m["id"] == message_id
        ),
        None,
    )


def rereads_of(message_id):
    return sorted(
        [
            r for r in data["rereads"]
            if r["message_id"] == message_id
        ],
        key=lambda r: (
            r.get("reread_date", ""),
            r.get("created_at", ""),
        ),
    )


def reread_stats(message_id):
    items = rereads_of(message_id)

    if not items:
        return {
            "count": 0,
            "average_change": None,
            "last": None,
        }

    changes = [
        r["mood_after"] - r["mood_before"]
        for r in items
    ]

    return {
        "count": len(items),
        "average_change": sum(changes) / len(changes),
        "last": items[-1]["reread_date"],
    }


def message_label(m):
    short = m["text"].replace("\n", " ")[:35]
    return f"{short} [{m['id'][:8]}]"


def speaker_name(m):
    if m.get("source") == SOURCES[1]:
        return "自分"

    return m.get("speaker", "").strip() or "名前なし"


def add_message(
    text,
    source,
    speaker,
    category,
    message_date,
    situation,
    feeling,
    importance,
    favorite,
):
    data["messages"].append({
        "id": uid(),
        "text": text,
        "source": source,
        "speaker": speaker,
        "category": category,
        "message_date": str(message_date),
        "situation": situation,
        "feeling": feeling,
        "importance": importance,
        "favorite": favorite,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })

    save_data(data)


def add_reread(
    message_id,
    reread_date,
    mood_before,
    mood_after,
    note,
):
    data["rereads"].append({
        "id": uid(),
        "message_id": message_id,
        "reread_date": str(reread_date),
        "mood_before": mood_before,
        "mood_after": mood_after,
        "note": note,
        "created_at": now_iso(),
    })

    save_data(data)


def delete_message(message_id):
    data["messages"] = [
        m for m in data["messages"]
        if m["id"] != message_id
    ]

    data["rereads"] = [
        r for r in data["rereads"]
        if r["message_id"] != message_id
    ]

    save_data(data)


def show_message(m, detailed=True):
    stats = reread_stats(m["id"])

    with st.container(border=True):
        st.caption(
            f"{m.get('category', '')} "
            f"｜{m.get('message_date', '')}"
        )

        st.markdown(f"### 「{m['text']}」")

        st.write(f"**― {speaker_name(m)} より**")

        st.write(
            f"心に残った度：{stars(m['importance'])}"
        )

        if m.get("favorite"):
            st.caption("❤️ 大切な言葉")

        if detailed:
            if m.get("situation"):
                st.write(
                    f"**どんな場面？** {m['situation']}"
                )

            if m.get("feeling"):
                st.write(
                    f"**そのときの気持ち：** {m['feeling']}"
                )

            change = stats["average_change"]

            change_text = (
                f"{change:+.1f}"
                if change is not None else "—"
            )

            st.caption(
                f"🔁 読み返し {stats['count']}回 "
                f"｜平均気分変化 {change_text}"
            )


# =========================================================
# データ初期化
# =========================================================

data = load_data()
messages = data["messages"]
rereads = data["rereads"]
today = date.today()


# =========================================================
# デザイン
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1300px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .hero {
        padding: 40px 20px;
        text-align: center;
        border-radius: 25px;
        background: linear-gradient(
            135deg,
            rgba(255,130,170,.16),
            rgba(160,120,240,.12)
        );
        margin-bottom: 24px;
    }
    .hero h1 {
        margin-bottom: 8px;
    }
    [data-testid="stMetric"] {
        padding: 12px;
        border-radius: 14px;
        border: 1px solid rgba(150,150,150,.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div>💬💖 DAY 313 / 365</div>
        <h1>言われてうれしかった言葉</h1>
        <p>
            あの日の言葉が、<br>
            今日の自分を支えてくれる。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# タブ
# =========================================================

(
    tab_home,
    tab_add,
    tab_album,
    tab_reread,
    tab_ranking,
    tab_people,
    tab_analysis,
    tab_manage,
) = st.tabs([
    "🏠 ホーム",
    "💬 言葉を登録",
    "📖 言葉のアルバム",
    "🔁 読み返し記録",
    "🏆 心に残った言葉",
    "👥 言葉をくれた人",
    "📊 分析",
    "🛠️ 管理",
])


# =========================================================
# 1. ホーム
# =========================================================

with tab_home:
    st.subheader("🏠 応援アルバム")

    changes = [
        r["mood_after"] - r["mood_before"]
        for r in rereads
    ]

    avg_change = (
        sum(changes) / len(changes)
        if changes else None
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💬 集めた言葉", len(messages))
    c2.metric("🔁 読み返した回数", len(rereads))
    c3.metric(
        "❤️ 大切な言葉",
        sum(bool(m.get("favorite")) for m in messages),
    )
    c4.metric(
        "🌱 平均気分変化",
        f"{avg_change:+.1f}"
        if avg_change is not None else "—",
    )

    if not messages:
        st.info(
            "まだ言葉がありません。"
            "「💬 言葉を登録」から最初の言葉を残そう！"
        )
    else:
        st.divider()
        st.markdown("### 💖 今日の応援メッセージ")

        favorite_messages = [
            m for m in messages if m.get("favorite")
        ]

        candidates = favorite_messages or messages
        ids = [m["id"] for m in candidates]

        if st.session_state.get("today_message") not in ids:
            st.session_state["today_message"] = random.choice(ids)

        selected = message_by_id(
            st.session_state["today_message"]
        )

        show_message(selected)

        if st.button(
            "🎲 別の言葉を届ける",
            key="home_shuffle",
        ):
            alternatives = [
                x for x in ids if x != selected["id"]
            ]

            if alternatives:
                st.session_state["today_message"] = random.choice(
                    alternatives
                )

            st.rerun()

        st.divider()
        st.markdown("### 📝 最近集めた言葉")

        recent = sorted(
            messages,
            key=lambda m: (
                m.get("message_date", ""),
                m.get("created_at", ""),
            ),
            reverse=True,
        )[:3]

        for m in recent:
            show_message(m, detailed=False)


# =========================================================
# 2. 言葉を登録
# =========================================================

with tab_add:
    st.subheader("💬 心に残った言葉を記録")

    st.caption(
        "短い一言でも大丈夫。"
        "自分に贈りたい言葉も登録できるよ。"
    )

    with st.form("add_message", clear_on_submit=True):
        text = st.text_area(
            "うれしかった言葉",
            placeholder="例：前よりずっと上達したね！",
            height=110,
        )

        source = st.selectbox(
            "言葉の送り主",
            SOURCES,
        )

        speaker = st.text_input(
            "言ってくれた人",
            placeholder="例：職場の先輩、自分",
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        message_date = st.date_input(
            "言われた日",
            value=today,
            max_value=today,
        )

        situation = st.text_area(
            "どんな場面だった？",
            placeholder="どんなときに言われた？",
        )

        feeling = st.text_area(
            "そのときの気持ち",
            placeholder="どう感じた？",
        )

        importance = st.slider(
            "心に残った度",
            1, 5, 5,
        )

        favorite = st.checkbox(
            "❤️ 大切な言葉にする",
            value=True,
        )

        submitted = st.form_submit_button(
            "💖 言葉を保存",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not text.strip():
                st.warning("言葉を入力してね。")
            else:
                add_message(
                    text.strip(),
                    source,
                    speaker.strip(),
                    category,
                    message_date,
                    situation.strip(),
                    feeling.strip(),
                    importance,
                    favorite,
                )
                st.rerun()


# =========================================================
# 3. 言葉のアルバム
# =========================================================

with tab_album:
    st.subheader("📖 言葉のアルバム")

    if not messages:
        st.info("言葉を登録するとここに並ぶよ。")
    else:
        search = st.text_input(
            "🔍 言葉を検索",
            placeholder="キーワードを入力",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            category_filter = st.selectbox(
                "カテゴリー",
                ["すべて"] + CATEGORIES,
                key="album_category",
            )

        with c2:
            speaker_filter = st.selectbox(
                "言ってくれた人",
                ["すべて"] + sorted({
                    speaker_name(m) for m in messages
                }),
            )

        with c3:
            favorite_only = st.checkbox(
                "❤️ 大切な言葉だけ",
            )

        filtered = []

        for m in messages:
            searchable = " ".join([
                m.get("text", ""),
                speaker_name(m),
                m.get("situation", ""),
                m.get("feeling", ""),
            ]).lower()

            if search.lower() not in searchable:
                continue

            if (
                category_filter != "すべて"
                and m.get("category") != category_filter
            ):
                continue

            if (
                speaker_filter != "すべて"
                and speaker_name(m) != speaker_filter
            ):
                continue

            if favorite_only and not m.get("favorite"):
                continue

            filtered.append(m)

        filtered.sort(
            key=lambda m: (
                m.get("message_date", ""),
                m.get("created_at", ""),
            ),
            reverse=True,
        )

        st.caption(f"{len(filtered)}件の言葉")

        for m in filtered:
            show_message(m)


# =========================================================
# 4. 読み返し記録
# =========================================================

with tab_reread:
    st.subheader("🔁 あの日の言葉を読み返す")

    if not messages:
        st.info("先に言葉を登録しよう。")
    else:
        options = {
            message_label(m): m["id"]
            for m in messages
        }

        selected_label = st.selectbox(
            "読み返した言葉",
            list(options),
            key="reread_select",
        )

        message_id = options[selected_label]
        selected = message_by_id(message_id)

        show_message(selected, detailed=False)

        with st.form("add_reread", clear_on_submit=True):
            reread_date = st.date_input(
                "読み返した日",
                value=today,
                max_value=today,
            )

            c1, c2 = st.columns(2)

            with c1:
                mood_before = st.slider(
                    "読む前の気分",
                    1, 5, 2,
                )

            with c2:
                mood_after = st.slider(
                    "読んだ後の気分",
                    1, 5, 4,
                )

            note = st.text_area(
                "今日の気づき",
                placeholder="読み返してどう感じた？",
            )

            submitted = st.form_submit_button(
                "🔁 読み返しを記録",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                add_reread(
                    message_id,
                    reread_date,
                    mood_before,
                    mood_after,
                    note.strip(),
                )
                st.rerun()

        st.divider()
        st.markdown("### 📚 読み返し履歴")

        history = list(reversed(
            rereads_of(message_id)
        ))

        if not history:
            st.caption("まだ読み返し履歴はありません。")

        for r in history:
            change = (
                r["mood_after"] - r["mood_before"]
            )

            with st.container(border=True):
                st.markdown(
                    f"**{r['reread_date']}｜気分変化 "
                    f"{signed(change)}**"
                )

                st.write(
                    f"読む前 {stars(r['mood_before'])} "
                    f"→ 読んだ後 {stars(r['mood_after'])}"
                )

                if r.get("note"):
                    st.write(r["note"])


# =========================================================
# 5. ランキング
# =========================================================

with tab_ranking:
    st.subheader("🏆 心に残った言葉ランキング")

    if not messages:
        st.info("まだランキング対象がありません。")
    else:
        sort_mode = st.selectbox(
            "並び替え",
            [
                "心に残った度が高い順",
                "読み返した回数が多い順",
                "気分変化が大きい順",
            ],
        )

        ranking = []

        for m in messages:
            stats = reread_stats(m["id"])

            ranking.append({
                "message": m,
                "count": stats["count"],
                "average_change": stats["average_change"],
            })

        if sort_mode == "心に残った度が高い順":
            ranking.sort(
                key=lambda x: (
                    x["message"]["importance"],
                    x["count"],
                ),
                reverse=True,
            )

        elif sort_mode == "読み返した回数が多い順":
            ranking.sort(
                key=lambda x: (
                    x["count"],
                    x["message"]["importance"],
                ),
                reverse=True,
            )

        else:
            ranking.sort(
                key=lambda x: (
                    x["average_change"] is not None,
                    x["average_change"] or 0,
                    x["count"],
                ),
                reverse=True,
            )

        rows = []

        for i, item in enumerate(ranking, start=1):
            m = item["message"]
            change = item["average_change"]

            rows.append({
                "順位": i,
                "言葉": m["text"],
                "送り主": speaker_name(m),
                "心に残った度": stars(m["importance"]),
                "読み返し回数": item["count"],
                "平均気分変化": (
                    f"{change:+.1f}"
                    if change is not None else "—"
                ),
            })

        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

        st.divider()
        st.markdown("### 💖 TOP 3")

        for i, item in enumerate(ranking[:3], start=1):
            medal = ["🥇", "🥈", "🥉"][i - 1]
            m = item["message"]

            with st.container(border=True):
                st.markdown(
                    f"### {medal}「{m['text']}」"
                )
                st.caption(
                    f"― {speaker_name(m)} より"
                )
                st.write(
                    f"心に残った度：{stars(m['importance'])}"
                )
                st.write(
                    f"読み返し：{item['count']}回"
                )


# =========================================================
# 6. 言葉をくれた人
# =========================================================

with tab_people:
    st.subheader("👥 言葉をくれた人図鑑")

    if not messages:
        st.info("言葉が増えると人別に振り返れるよ。")
    else:
        people = defaultdict(list)

        for m in messages:
            people[speaker_name(m)].append(m)

        people_names = sorted(
            people,
            key=lambda name: len(people[name]),
            reverse=True,
        )

        selected_person = st.selectbox(
            "言葉をくれた人",
            people_names,
        )

        person_messages = people[selected_person]

        total_rereads = sum(
            reread_stats(m["id"])["count"]
            for m in person_messages
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "💬 もらった言葉",
            len(person_messages),
        )
        c2.metric(
            "🔁 読み返した回数",
            total_rereads,
        )

        st.divider()

        for m in sorted(
            person_messages,
            key=lambda x: x.get("message_date", ""),
            reverse=True,
        ):
            show_message(m)


# =========================================================
# 7. 分析
# =========================================================

with tab_analysis:
    st.subheader("📊 言葉の分析")

    if not messages:
        st.info("言葉が増えると分析できるよ。")
    else:
        st.markdown("### 🌸 カテゴリー分布")

        category_counts = Counter(
            m.get("category", "📦 その他")
            for m in messages
        )

        category_df = pd.DataFrame([
            {"カテゴリー": k, "件数": v}
            for k, v in category_counts.items()
        ])

        st.bar_chart(
            category_df.set_index("カテゴリー")
        )

        st.divider()
        st.markdown("### 🗓️ 月ごとの登録数")

        monthly = Counter()

        for m in messages:
            d = parse_date(m.get("message_date"))
            if d:
                monthly[d.strftime("%Y-%m")] += 1

        if monthly:
            monthly_df = pd.DataFrame([
                {"月": month, "件数": count}
                for month, count in sorted(monthly.items())
            ])

            st.bar_chart(
                monthly_df.set_index("月")
            )

        st.divider()
        st.markdown("### 👥 言葉をくれた人別の件数")

        speaker_counts = Counter(
            speaker_name(m)
            for m in messages
        )

        speaker_df = pd.DataFrame([
            {"人": name, "件数": count}
            for name, count in speaker_counts.items()
        ])

        st.bar_chart(
            speaker_df.set_index("人")
        )

        st.divider()
        st.markdown("### 🌱 読み返し前後の気分")

        if rereads:
            before_avg = (
                sum(r["mood_before"] for r in rereads)
                / len(rereads)
            )

            after_avg = (
                sum(r["mood_after"] for r in rereads)
                / len(rereads)
            )

            mood_df = pd.DataFrame([
                {
                    "項目": "読む前",
                    "平均気分": round(before_avg, 2),
                },
                {
                    "項目": "読んだ後",
                    "平均気分": round(after_avg, 2),
                },
            ])

            st.bar_chart(
                mood_df.set_index("項目")
            )

            st.metric(
                "平均気分変化",
                f"{after_avg - before_avg:+.2f}",
            )

            st.caption(
                "※気分の変化は本人の記録に基づくもので、"
                "言葉を読んだことだけが原因とは限りません。"
            )
        else:
            st.caption("まだ読み返し記録はありません。")

        st.divider()
        st.markdown("### ❤️ 大切な言葉の割合")

        favorites = sum(
            bool(m.get("favorite"))
            for m in messages
        )

        st.progress(favorites / len(messages))

        st.caption(
            f"{favorites} / {len(messages)} 件"
        )


# =========================================================
# 8. 管理
# =========================================================

with tab_manage:
    st.subheader("🛠️ 言葉の編集・削除")

    if messages:
        options = {
            message_label(m): m["id"]
            for m in messages
        }

        selected_label = st.selectbox(
            "編集する言葉",
            list(options),
            key="manage_message",
        )

        message_id = options[selected_label]
        m = message_by_id(message_id)

        # メッセージIDごとにフォームを分け、
        # 別の記録の入力値が混ざるのを防ぐ。
        with st.form(f"edit_message_{message_id}"):
            edit_text = st.text_area(
                "言葉",
                value=m["text"],
            )

            edit_source = st.selectbox(
                "送り主の種類",
                SOURCES,
                index=choice_index(
                    m.get("source"), SOURCES
                ),
            )

            edit_speaker = st.text_input(
                "言ってくれた人",
                value=m.get("speaker", ""),
            )

            edit_category = st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=choice_index(
                    m.get("category"), CATEGORIES
                ),
            )

            edit_date = st.date_input(
                "言われた日",
                value=(
                    parse_date(m.get("message_date"))
                    or today
                ),
                max_value=today,
            )

            edit_situation = st.text_area(
                "場面",
                value=m.get("situation", ""),
            )

            edit_feeling = st.text_area(
                "そのときの気持ち",
                value=m.get("feeling", ""),
            )

            edit_importance = st.slider(
                "心に残った度",
                1, 5,
                int(m["importance"]),
            )

            edit_favorite = st.checkbox(
                "❤️ 大切な言葉",
                value=m.get("favorite", False),
            )

            saved = st.form_submit_button(
                "💾 変更を保存",
                type="primary",
                use_container_width=True,
            )

            if saved:
                if not edit_text.strip():
                    st.warning("言葉を入力してね。")
                else:
                    m.update({
                        "text": edit_text.strip(),
                        "source": edit_source,
                        "speaker": edit_speaker.strip(),
                        "category": edit_category,
                        "message_date": str(edit_date),
                        "situation": edit_situation.strip(),
                        "feeling": edit_feeling.strip(),
                        "importance": edit_importance,
                        "favorite": edit_favorite,
                        "updated_at": now_iso(),
                    })

                    save_data(data)
                    st.rerun()

        st.divider()
        st.markdown("### 🔁 読み返し履歴の管理")

        item_rereads = rereads_of(message_id)

        if item_rereads:
            reread_options = {
                (
                    f"{r['reread_date']} "
                    f"[{r['id'][:8]}]"
                ): r["id"]
                for r in item_rereads
            }

            reread_label = st.selectbox(
                "編集する読み返し記録",
                list(reread_options),
                key=f"manage_reread_{message_id}",
            )

            reread_id = reread_options[reread_label]

            r = next(
                x for x in data["rereads"]
                if x["id"] == reread_id
            )

            with st.form(f"edit_reread_{reread_id}"):
                edit_reread_date = st.date_input(
                    "読み返した日",
                    value=(
                        parse_date(r.get("reread_date"))
                        or today
                    ),
                    max_value=today,
                )

                edit_before = st.slider(
                    "読む前の気分",
                    1, 5,
                    int(r["mood_before"]),
                )

                edit_after = st.slider(
                    "読んだ後の気分",
                    1, 5,
                    int(r["mood_after"]),
                )

                edit_note = st.text_area(
                    "気づき",
                    value=r.get("note", ""),
                )

                if st.form_submit_button(
                    "💾 読み返し記録を保存"
                ):
                    r.update({
                        "reread_date": str(edit_reread_date),
                        "mood_before": edit_before,
                        "mood_after": edit_after,
                        "note": edit_note.strip(),
                    })

                    save_data(data)
                    st.rerun()

            confirm_reread_delete = st.checkbox(
                "この読み返し記録を削除する",
                key=f"confirm_reread_{reread_id}",
            )

            if st.button(
                "🗑️ 読み返し記録を削除",
                disabled=not confirm_reread_delete,
                key=f"delete_reread_{reread_id}",
            ):
                data["rereads"] = [
                    x for x in data["rereads"]
                    if x["id"] != reread_id
                ]

                save_data(data)
                st.rerun()

        else:
            st.caption("読み返し履歴はありません。")

        st.divider()
        st.markdown("### ⚠️ 言葉を完全削除")

        st.warning(
            "この言葉を削除すると、"
            "紐づく読み返し履歴も削除されます。"
        )

        confirm_delete = st.checkbox(
            "この言葉と全履歴を削除する",
            key=f"confirm_message_{message_id}",
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=not confirm_delete,
            key=f"delete_message_{message_id}",
        ):
            delete_message(message_id)
            st.rerun()

    else:
        st.info("編集できる言葉はまだありません。")

    st.divider()
    st.subheader("💾 JSONバックアップ")

    backup_json = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ バックアップをダウンロード",
        data=backup_json,
        file_name=f"happy_words_{today_iso()}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.divider()
    st.subheader("📤 バックアップから復元")

    st.warning(
        "復元すると現在の全データが置き換わります。"
        "必要なら先にバックアップを保存してください。"
    )

    uploaded = st.file_uploader(
        "復元するJSONファイル",
        type=["json"],
    )

    if uploaded is not None:
        try:
            restored = json.loads(
                uploaded.getvalue().decode("utf-8")
            )

            validate_data(restored)

            st.success(
                f"読み込みOK："
                f"言葉 {len(restored['messages'])}件、"
                f"読み返し {len(restored['rereads'])}件"
            )

            confirm_restore = st.checkbox(
                "現在のデータを置き換えることに同意する"
            )

            if st.button(
                "📤 復元を実行",
                disabled=not confirm_restore,
                type="primary",
            ):
                save_data(restored)
                st.rerun()

        except (ValueError, UnicodeDecodeError) as exc:
            st.error(f"復元できないJSONです：{exc}")


# =========================================================
# フッター
# =========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:25px;">
        <p><b>あの日の何気ない一言が、</b></p>
        <p><b>未来の自分を支えてくれる。</b></p>
        <p>
            忘れたくない言葉を、<br>
            忘れない場所へ。
        </p>
        <h3>言葉は、時間を越えて届く贈り物。💬💖</h3>
        <p><b>DAY 313 / 365 — COMPLETE 🔥</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)
