import json
import os
import random
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="やめたらどうなった？",
    page_icon="🌿",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "quits.json")

CATEGORIES = [
    "📱 スマホ・SNS",
    "🍔 食事",
    "💰 支出",
    "🛒 買い物",
    "🧠 考え方",
    "⏰ 時間の使い方",
    "💼 仕事",
    "🏠 生活",
    "🎮 趣味",
    "🔁 習慣",
    "📦 その他",
]

QUIT_TYPES = [
    "🚫 完全にやめる",
    "📉 減らす",
    "⏸️ 一時的にやめる",
    "🔄 別のものに置き換える",
]

STATUSES = [
    "🟢 継続中",
    "🟡 減らして継続",
    "🔄 戻した",
    "✅ 終了",
]

FEELINGS = [
    "😊 やめてよかった",
    "😐 まだ分からない",
    "🤔 あまり変わらない",
    "😕 やめない方がよかった",
]


# =========================================================
# HELPERS
# =========================================================

def new_id():
    return str(uuid.uuid4())


def now_text():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d",
        ).date()
    except (ValueError, TypeError):
        return None


def stars(value):
    if value is None:
        return "-"

    value = max(
        0,
        min(5, int(value)),
    )

    return (
        "★" * value
        + "☆" * (5 - value)
    )


def quit_label(item):
    return (
        f"{item.get('title', '')} "
        f"[{item.get('id', '')[:6]}]"
    )


def days_from_start(item, target=None):
    start = parse_date(
        item.get("start_date")
    )

    if not start:
        return None

    if target is None:
        end = date.today()
    elif isinstance(target, date):
        end = target
    else:
        end = parse_date(target)

    if not end:
        return None

    return max(
        0,
        (end - start).days,
    )


def effective_end_date(item):
    """
    戻した・終了した場合は、その日までを継続日数として扱う。
    """
    if item.get("status") == "🔄 戻した":
        returned = parse_date(
            item.get("return_date")
        )

        if returned:
            return returned

    if item.get("status") == "✅ 終了":
        ended = parse_date(
            item.get("end_date")
        )

        if ended:
            return ended

    return date.today()


def current_days(item):
    return days_from_start(
        item,
        effective_end_date(item),
    )


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "quits": [],
        "reviews": [],
    }


def save_data(data):
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    temp_path = DATA_FILE + ".tmp"

    with open(
        temp_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    os.replace(
        temp_path,
        DATA_FILE,
    )


def load_data():
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            data = default_data()

        data.setdefault("quits", [])
        data.setdefault("reviews", [])

        # 古いデータへの補完
        for item in data["quits"]:
            item.setdefault("id", new_id())
            item.setdefault("title", "")
            item.setdefault(
                "category",
                "📦 その他",
            )
            item.setdefault(
                "quit_type",
                "🚫 完全にやめる",
            )
            item.setdefault(
                "start_date",
                str(date.today()),
            )
            item.setdefault("reason", "")
            item.setdefault(
                "burden_before",
                3,
            )
            item.setdefault(
                "expected_effect",
                3,
            )
            item.setdefault(
                "desired_change",
                "",
            )
            item.setdefault(
                "status",
                "🟢 継続中",
            )
            item.setdefault(
                "replacement",
                "",
            )
            item.setdefault(
                "return_date",
                None,
            )
            item.setdefault(
                "return_reason",
                "",
            )
            item.setdefault(
                "end_date",
                None,
            )
            item.setdefault(
                "favorite",
                False,
            )
            item.setdefault(
                "created_at",
                now_text(),
            )
            item.setdefault(
                "updated_at",
                item["created_at"],
            )

        for review in data["reviews"]:
            review.setdefault(
                "id",
                new_id(),
            )
            review.setdefault(
                "quit_id",
                "",
            )
            review.setdefault(
                "review_date",
                str(date.today()),
            )
            review.setdefault(
                "positive_effect",
                3,
            )
            review.setdefault(
                "ease",
                3,
            )
            review.setdefault(
                "feeling",
                "😐 まだ分からない",
            )
            review.setdefault(
                "change_note",
                "",
            )
            review.setdefault(
                "new_space",
                "",
            )
            review.setdefault(
                "created_at",
                now_text(),
            )

        return data

    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        data = default_data()
        save_data(data)
        return data


# =========================================================
# GETTERS
# =========================================================

def get_quit(data, quit_id):
    return next(
        (
            item
            for item in data["quits"]
            if item.get("id") == quit_id
        ),
        None,
    )


def get_review(data, review_id):
    return next(
        (
            review
            for review in data["reviews"]
            if review.get("id")
            == review_id
        ),
        None,
    )


def reviews_for_quit(
    data,
    quit_id,
):
    result = [
        review
        for review in data["reviews"]
        if review.get("quit_id")
        == quit_id
    ]

    return sorted(
        result,
        key=lambda r: (
            r.get("review_date", ""),
            r.get("created_at", ""),
        ),
    )


def latest_review(
    data,
    quit_id,
):
    result = reviews_for_quit(
        data,
        quit_id,
    )

    if not result:
        return None

    return result[-1]


# =========================================================
# CRUD
# =========================================================

def add_quit(
    data,
    title,
    category,
    quit_type,
    start_date,
    reason,
    burden_before,
    expected_effect,
    desired_change,
    replacement,
    favorite,
):
    item = {
        "id": new_id(),
        "title": title,
        "category": category,
        "quit_type": quit_type,
        "start_date": str(start_date),
        "reason": reason,
        "burden_before": int(
            burden_before
        ),
        "expected_effect": int(
            expected_effect
        ),
        "desired_change":
            desired_change,
        "status": (
            "🟡 減らして継続"
            if quit_type
            == "📉 減らす"
            else "🟢 継続中"
        ),
        "replacement": replacement,
        "return_date": None,
        "return_reason": "",
        "end_date": None,
        "favorite": bool(favorite),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["quits"].append(item)
    save_data(data)


def add_review(
    data,
    quit_id,
    review_date,
    positive_effect,
    ease,
    feeling,
    change_note,
    new_space,
):
    review = {
        "id": new_id(),
        "quit_id": quit_id,
        "review_date": str(
            review_date
        ),
        "positive_effect": int(
            positive_effect
        ),
        "ease": int(ease),
        "feeling": feeling,
        "change_note": change_note,
        "new_space": new_space,
        "created_at": now_text(),
    }

    data["reviews"].append(review)

    item = get_quit(
        data,
        quit_id,
    )

    if item:
        item["updated_at"] = now_text()

    save_data(data)


def delete_quit(
    data,
    quit_id,
):
    data["quits"] = [
        item
        for item in data["quits"]
        if item.get("id") != quit_id
    ]

    data["reviews"] = [
        review
        for review in data["reviews"]
        if review.get("quit_id")
        != quit_id
    ]

    save_data(data)


def delete_review(
    data,
    review_id,
):
    data["reviews"] = [
        review
        for review in data["reviews"]
        if review.get("id")
        != review_id
    ]

    save_data(data)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .hero {
        padding: 42px 25px;
        text-align: center;
        border-radius: 28px;
        margin-bottom: 25px;
        background:
            linear-gradient(
                135deg,
                rgba(90, 190, 120, .13),
                rgba(130, 180, 255, .08),
                rgba(255,255,255,.02)
            );
    }

    .quit-card {
        padding: 20px;
        border-radius: 20px;
        border:
            1px solid
            rgba(90, 190, 120, .20);
        margin-bottom: 12px;
    }

    .timeline {
        padding: 17px 20px;
        margin: 10px 0;
        border-left:
            4px solid
            rgba(90, 190, 120, .55);
        border-radius: 8px;
        background:
            rgba(90, 190, 120, .05);
    }

    .green-card {
        padding: 25px;
        border-radius: 22px;
        margin-bottom: 15px;
        background:
            linear-gradient(
                135deg,
                rgba(90,190,120,.10),
                rgba(255,255,255,.02)
            );
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;
        background:
            rgba(90,190,120,.05);
        border:
            1px solid
            rgba(90,190,120,.12);
    }

    .footer {
        text-align: center;
        padding: 35px;
        margin-top: 35px;
        border-radius: 25px;
        background:
            rgba(90,190,120,.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()
quits = data["quits"]
reviews = data["reviews"]

today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>🚫➡️🌿 DAY 309 / 365</div>
        <h1>やめたらどうなった？</h1>
        <p>
            手放したことで生まれた変化を、
            静かに観察する。
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

(
    tab_home,
    tab_add,
    tab_review,
    tab_timeline,
    tab_good,
    tab_analysis,
    tab_library,
    tab_manage,
) = st.tabs(
    [
        "🏠 ホーム",
        "🚫 やめること登録",
        "🌱 どうなった？",
        "🕰️ 変化タイムライン",
        "🌿 やめてよかった",
        "📊 分析",
        "📚 やめたこと図鑑",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    active = [
        item
        for item in quits
        if item.get("status")
        in [
            "🟢 継続中",
            "🟡 減らして継続",
        ]
    ]

    returned = [
        item
        for item in quits
        if item.get("status")
        == "🔄 戻した"
    ]

    reviewed_ids = {
        review.get("quit_id")
        for review in reviews
    }

    good_count = 0

    for item in quits:
        latest = latest_review(
            data,
            item.get("id"),
        )

        if (
            latest
            and latest.get("feeling")
            == "😊 やめてよかった"
            and int(
                latest.get(
                    "positive_effect",
                    0,
                )
            ) >= 4
        ):
            good_count += 1

    st.subheader(
        "🌿 手放したもの"
    )

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "🚫 記録",
        f"{len(quits)}個",
    )

    c2.metric(
        "🌱 継続中",
        f"{len(active)}個",
    )

    c3.metric(
        "🔎 経過観察済み",
        f"{len(reviewed_ids)}個",
    )

    c4.metric(
        "🌿 やめてよかった",
        f"{good_count}個",
    )

    if active:
        st.divider()

        st.subheader(
            "🌱 今、手放しているもの"
        )

        active_sorted = sorted(
            active,
            key=lambda x: (
                current_days(x) or 0
            ),
            reverse=True,
        )

        for item in active_sorted:
            days = current_days(item)
            latest = latest_review(
                data,
                item.get("id"),
            )

            with st.container(
                border=True
            ):
                c1, c2 = st.columns(
                    [3, 1]
                )

                with c1:
                    st.markdown(
                        f"### "
                        f"{item.get('category')} "
                        f"{item.get('title')}"
                    )

                    st.caption(
                        f"{item.get('quit_type')} "
                        f"｜{item.get('status')}"
                    )

                with c2:
                    st.metric(
                        "経過",
                        f"{days}日"
                        if days is not None
                        else "-",
                    )

                if latest:
                    st.write(
                        f"最新の良い影響："
                        f"{stars(latest.get('positive_effect'))}"
                    )

                    st.caption(
                        latest.get(
                            "feeling",
                            "",
                        )
                    )

                else:
                    st.caption(
                        "まだ経過記録はありません。"
                    )

    # 最長
    if quits:
        st.divider()

        st.subheader(
            "🏆 長く続いているもの"
        )

        ranking = sorted(
            quits,
            key=lambda x: (
                current_days(x) or 0
            ),
            reverse=True,
        )

        for rank, item in enumerate(
            ranking[:5],
            start=1,
        ):
            st.write(
                f"**{rank}. "
                f"{item.get('title')}** "
                f"— {current_days(item)}日 "
                f"{item.get('status')}"
            )

        st.caption(
            "※長く続いていることが"
            "偉さを表すものではありません。"
        )


# =========================================================
# ADD
# =========================================================

with tab_add:

    st.subheader(
        "🚫 何を手放してみる？"
    )

    st.caption(
        "完全にやめなくても大丈夫。"
        "減らす・一時停止・置き換えるも"
        "立派な実験です。"
    )

    with st.form(
        "add_quit_form",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "やめる・減らすこと",
            placeholder=(
                "例：寝る前にSNSを見る"
            ),
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        quit_type = st.selectbox(
            "どうする？",
            QUIT_TYPES,
        )

        start_date = st.date_input(
            "始める日",
            value=today,
            max_value=today,
        )

        reason = st.text_area(
            "🤔 なぜやめる？",
            placeholder=(
                "例：寝る時間が"
                "遅くなってしまうから"
            ),
        )

        burden = st.slider(
            "😣 やめる前の負担",
            1,
            5,
            3,
        )

        st.write(
            stars(burden)
        )

        expected = st.slider(
            "🌿 変化への期待",
            1,
            5,
            3,
        )

        st.write(
            stars(expected)
        )

        desired = st.text_area(
            "✨ 何が変わってほしい？",
            placeholder=(
                "例：早く寝られるようになりたい"
            ),
        )

        replacement = st.text_input(
            "🔄 代わりにすること",
            placeholder=(
                "例：寝る前に本を読む"
            ),
            help=(
                "特に決めていなければ"
                "空欄でOK"
            ),
        )

        favorite = st.checkbox(
            "❤️ お気に入りにする"
        )

        submitted = (
            st.form_submit_button(
                "🚫 記録を始める",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.warning(
                    "やめることを入力してね。"
                )

            else:
                add_quit(
                    data=data,
                    title=title.strip(),
                    category=category,
                    quit_type=quit_type,
                    start_date=start_date,
                    reason=reason.strip(),
                    burden_before=burden,
                    expected_effect=expected,
                    desired_change=(
                        desired.strip()
                    ),
                    replacement=(
                        replacement.strip()
                    ),
                    favorite=favorite,
                )

                st.rerun()


# =========================================================
# REVIEW
# =========================================================

with tab_review:

    st.subheader(
        "🌱 やめてみて、どうなった？"
    )

    if not quits:
        st.info(
            "まずは手放してみるものを"
            "登録しよう。"
        )

    else:
        options = {
            quit_label(item):
            item.get("id")
            for item in quits
        }

        selected_label = (
            st.selectbox(
                "振り返るもの",
                list(options.keys()),
                key="review_quit",
            )
        )

        selected_id = options[
            selected_label
        ]

        item = get_quit(
            data,
            selected_id,
        )

        st.markdown(
            f"### {item.get('category')} "
            f"{item.get('title')}"
        )

        st.caption(
            f"{item.get('quit_type')} "
            f"｜開始：{item.get('start_date')}"
        )

        days = days_from_start(
            item
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "経過",
            f"{days}日"
            if days is not None
            else "-",
        )

        c2.metric(
            "最初の期待",
            f"{item.get('expected_effect')} / 5",
        )

        latest = latest_review(
            data,
            selected_id,
        )

        c3.metric(
            "最新の良い影響",
            (
                f"{latest.get('positive_effect')} / 5"
                if latest
                else "-"
            ),
        )

        if item.get("desired_change"):
            st.info(
                "✨ 期待していた変化："
                + item.get(
                    "desired_change"
                )
            )

        with st.form(
            "add_review_form"
        ):
            review_date = st.date_input(
                "振り返る日",
                value=today,
                max_value=today,
            )

            positive_effect = st.slider(
                "🌿 生活への良い影響",
                1,
                5,
                3,
            )

            ease = st.slider(
                "🌱 続けやすさ",
                1,
                5,
                3,
            )

            feeling = st.selectbox(
                "今どう思う？",
                FEELINGS,
            )

            change_note = st.text_area(
                "どう変わった？",
                placeholder=(
                    "例：寝る時間が"
                    "20分くらい早くなった"
                ),
            )

            new_space = st.text_area(
                "🌿 空いた場所に何が入った？",
                placeholder=(
                    "例：本を読む時間が増えた"
                ),
            )

            submitted = (
                st.form_submit_button(
                    "🌱 経過を記録",
                    type="primary",
                    use_container_width=True,
                )
            )

            if submitted:
                start = parse_date(
                    item.get("start_date")
                )

                if (
                    start
                    and review_date < start
                ):
                    st.warning(
                        "開始日より前には"
                        "記録できません。"
                    )

                else:
                    add_review(
                        data=data,
                        quit_id=selected_id,
                        review_date=(
                            review_date
                        ),
                        positive_effect=(
                            positive_effect
                        ),
                        ease=ease,
                        feeling=feeling,
                        change_note=(
                            change_note.strip()
                        ),
                        new_space=(
                            new_space.strip()
                        ),
                    )

                    st.rerun()


# =========================================================
# TIMELINE
# =========================================================

with tab_timeline:

    st.subheader(
        "🕰️ 変化タイムライン"
    )

    if not quits:
        st.info(
            "まだ記録がありません。"
        )

    else:
        options = {
            quit_label(item):
            item.get("id")
            for item in quits
        }

        selected_label = (
            st.selectbox(
                "見る記録",
                list(options.keys()),
                key="timeline_select",
            )
        )

        selected_id = options[
            selected_label
        ]

        item = get_quit(
            data,
            selected_id,
        )

        item_reviews = reviews_for_quit(
            data,
            selected_id,
        )

        st.markdown(
            f"## 🚫 {item.get('title')}"
        )

        st.markdown(
            f"""
            <div class="timeline">
                <b>
                    🚫 {item.get("start_date")}
                </b>
                <br>
                スタート
                <br><br>
                😣 やめる前の負担：
                {stars(item.get("burden_before"))}
                <br>
                🌿 期待：
                {stars(item.get("expected_effect"))}
                <br><br>
                {item.get("reason", "")}
            </div>
            """,
            unsafe_allow_html=True,
        )

        for review in item_reviews:
            review_days = (
                days_from_start(
                    item,
                    review.get(
                        "review_date"
                    ),
                )
            )

            st.markdown(
                "<div style='text-align:center;'>↓</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="timeline">
                    <b>
                        🌱 {review.get("review_date")}
                    </b>
                    <br>
                    {review_days}日後
                    <br><br>

                    🌿 良い影響：
                    {stars(review.get("positive_effect"))}
                    <br>

                    🌱 続けやすさ：
                    {stars(review.get("ease"))}
                    <br>

                    {review.get("feeling")}
                    <br><br>

                    {review.get("change_note", "")}
                    <br>

                    {
                        "✨ " + review.get("new_space")
                        if review.get("new_space")
                        else ""
                    }
                </div>
                """,
                unsafe_allow_html=True,
            )

        if item.get("status") == "🔄 戻した":
            st.markdown(
                "<div style='text-align:center;'>↓</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="timeline">
                    <b>
                        🔄 {item.get("return_date") or "-"}
                    </b>
                    <br>
                    元に戻した
                    <br><br>
                    {item.get("return_reason", "")}
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif item.get("status") == "✅ 終了":
            st.markdown(
                "<div style='text-align:center;'>↓</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="timeline">
                    <b>
                        ✅ {item.get("end_date") or "-"}
                    </b>
                    <br>
                    観察終了
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# GOOD
# =========================================================

with tab_good:

    st.subheader(
        "🌿 やめてよかった"
    )

    good_items = []

    for item in quits:
        latest = latest_review(
            data,
            item.get("id"),
        )

        if (
            latest
            and latest.get("feeling")
            == "😊 やめてよかった"
            and int(
                latest.get(
                    "positive_effect",
                    0,
                )
            ) >= 4
        ):
            good_items.append(
                (
                    int(
                        latest.get(
                            "positive_effect",
                            0,
                        )
                    ),
                    item,
                    latest,
                )
            )

    good_items.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    if not good_items:
        st.info(
            "最新評価が「やめてよかった」かつ"
            "良い影響4以上の記録が"
            "ここに並びます。"
        )

    for effect, item, latest in (
        good_items
    ):
        st.markdown(
            f"""
            <div class="green-card">
                <h3>
                    🌿 {item.get("title")}
                </h3>

                <p>
                    {item.get("category")}
                    ｜{current_days(item)}日
                </p>

                <p>
                    良い影響：
                    {stars(effect)}
                </p>

                <p>
                    {latest.get("change_note", "")}
                </p>

                <p>
                    {
                        "✨ 生まれたもの："
                        + latest.get("new_space")
                        if latest.get("new_space")
                        else ""
                    }
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 何を手放すと変化した？"
    )

    if not quits:
        st.info(
            "記録が増えると"
            "ここに分析が表示されます。"
        )

    else:
        latest_effects = []
        latest_eases = []

        for item in quits:
            latest = latest_review(
                data,
                item.get("id"),
            )

            if latest:
                latest_effects.append(
                    int(
                        latest.get(
                            "positive_effect",
                            0,
                        )
                    )
                )

                latest_eases.append(
                    int(
                        latest.get(
                            "ease",
                            0,
                        )
                    )
                )

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "🚫 手放したもの",
            len(quits),
        )

        c2.metric(
            "🌿 平均良い影響",
            (
                f"{sum(latest_effects) / len(latest_effects):.1f}"
                if latest_effects
                else "-"
            ),
        )

        c3.metric(
            "🌱 平均続けやすさ",
            (
                f"{sum(latest_eases) / len(latest_eases):.1f}"
                if latest_eases
                else "-"
            ),
        )

        c4.metric(
            "🔄 戻した",
            sum(
                1
                for item in quits
                if item.get("status")
                == "🔄 戻した"
            ),
        )

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 📦 カテゴリー別"
        )

        category_rows = []

        for category in CATEGORIES:
            category_items = [
                item
                for item in quits
                if item.get("category")
                == category
            ]

            if not category_items:
                continue

            effects = []
            eases = []

            for item in category_items:
                latest = latest_review(
                    data,
                    item.get("id"),
                )

                if latest:
                    effects.append(
                        int(
                            latest.get(
                                "positive_effect",
                                0,
                            )
                        )
                    )

                    eases.append(
                        int(
                            latest.get(
                                "ease",
                                0,
                            )
                        )
                    )

            returned_count = sum(
                1
                for item in category_items
                if item.get("status")
                == "🔄 戻した"
            )

            category_rows.append(
                {
                    "カテゴリー":
                        category,
                    "件数":
                        len(category_items),
                    "平均良い影響":
                        (
                            round(
                                sum(effects)
                                / len(effects),
                                1,
                            )
                            if effects
                            else None
                        ),
                    "平均続けやすさ":
                        (
                            round(
                                sum(eases)
                                / len(eases),
                                1,
                            )
                            if eases
                            else None
                        ),
                    "戻した数":
                        returned_count,
                }
            )

        category_df = pd.DataFrame(
            category_rows
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        if not category_df.empty:
            chart_df = (
                category_df[
                    [
                        "カテゴリー",
                        "件数",
                    ]
                ]
                .set_index(
                    "カテゴリー"
                )
            )

            st.bar_chart(chart_df)

        # -------------------------------------------------
        # EXPECTATION VS REALITY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🤔 期待と実際"
        )

        comparison_rows = []

        for item in quits:
            latest = latest_review(
                data,
                item.get("id"),
            )

            if not latest:
                continue

            expected = int(
                item.get(
                    "expected_effect",
                    0,
                )
            )

            actual = int(
                latest.get(
                    "positive_effect",
                    0,
                )
            )

            comparison_rows.append(
                {
                    "やめたこと":
                        item.get("title"),
                    "期待":
                        expected,
                    "実際":
                        actual,
                    "差":
                        actual - expected,
                }
            )

        if comparison_rows:
            comparison_df = (
                pd.DataFrame(
                    comparison_rows
                )
            )

            st.dataframe(
                comparison_df,
                hide_index=True,
                use_container_width=True,
            )

            better = [
                row
                for row
                in comparison_rows
                if row["差"] >= 2
            ]

            lower = [
                row
                for row
                in comparison_rows
                if row["差"] <= -2
            ]

            c1, c2 = st.columns(2)

            with c1:
                st.markdown(
                    "#### 😲 思った以上"
                )

                if better:
                    for row in better:
                        st.write(
                            f"・{row['やめたこと']} "
                            f"{row['期待']} → "
                            f"{row['実際']}"
                        )
                else:
                    st.caption(
                        "まだありません。"
                    )

            with c2:
                st.markdown(
                    "#### 🤔 思ったほどではなかった"
                )

                if lower:
                    for row in lower:
                        st.write(
                            f"・{row['やめたこと']} "
                            f"{row['期待']} → "
                            f"{row['実際']}"
                        )
                else:
                    st.caption(
                        "まだありません。"
                    )

        else:
            st.caption(
                "経過記録を追加すると"
                "比較できます。"
            )

        # -------------------------------------------------
        # NEW SPACE
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🌿 空いた場所に入ってきたもの"
        )

        spaces = [
            review.get(
                "new_space",
                ""
            ).strip()
            for review in reviews
            if review.get(
                "new_space",
                ""
            ).strip()
        ]

        if spaces:
            for space in reversed(
                spaces[-10:]
            ):
                st.write(
                    f"✨ {space}"
                )
        else:
            st.caption(
                "まだ記録がありません。"
            )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🔄 今どうなっている？"
        )

        status_counter = Counter(
            item.get("status")
            for item in quits
        )

        status_df = pd.DataFrame(
            [
                {
                    "状態": status,
                    "件数": count,
                }
                for status, count
                in status_counter.items()
            ]
        ).set_index("状態")

        st.bar_chart(status_df)

        # -------------------------------------------------
        # RANDOM OLD
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🎲 これ、やめたの覚えてる？"
        )

        old_items = [
            item
            for item in quits
            if (
                days_from_start(item)
                is not None
                and days_from_start(item)
                >= 30
            )
        ]

        candidates = (
            old_items
            if old_items
            else quits
        )

        candidate_ids = [
            item.get("id")
            for item in candidates
        ]

        random_id = (
            st.session_state.get(
                "random_quit_id"
            )
        )

        if random_id not in candidate_ids:
            random_id = random.choice(
                candidate_ids
            )

            st.session_state[
                "random_quit_id"
            ] = random_id

        random_item = get_quit(
            data,
            random_id,
        )

        random_latest = latest_review(
            data,
            random_id,
        )

        with st.container(
            border=True
        ):
            st.markdown(
                f"### 🚫 "
                f"{random_item.get('title')}"
            )

            st.caption(
                f"{days_from_start(random_item)}日前に開始"
            )

            st.write(
                "当時の期待："
                + stars(
                    random_item.get(
                        "expected_effect"
                    )
                )
            )

            if random_latest:
                st.write(
                    "最新の良い影響："
                    + stars(
                        random_latest.get(
                            "positive_effect"
                        )
                    )
                )

                st.write(
                    random_latest.get(
                        "feeling"
                    )
                )

                if random_latest.get(
                    "new_space"
                ):
                    st.success(
                        "🌿 生まれたもの："
                        + random_latest.get(
                            "new_space"
                        )
                    )

        if st.button(
            "🎲 別の記録を見る",
            use_container_width=True,
        ):
            alternatives = [
                item_id
                for item_id
                in candidate_ids
                if item_id != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_quit_id"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# LIBRARY
# =========================================================

with tab_library:

    st.subheader(
        "📚 やめたこと図鑑"
    )

    search = st.text_input(
        "🔎 検索",
        key="library_search",
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        category_filter = (
            st.selectbox(
                "カテゴリー",
                ["すべて"]
                + CATEGORIES,
                key="library_category",
            )
        )

    with c2:
        status_filter = (
            st.selectbox(
                "状態",
                ["すべて"]
                + STATUSES,
                key="library_status",
            )
        )

    with c3:
        type_filter = (
            st.selectbox(
                "やめ方",
                ["すべて"]
                + QUIT_TYPES,
                key="library_type",
            )
        )

    favorite_only = st.checkbox(
        "❤️ お気に入りだけ",
        key="library_favorite",
    )

    rows = []

    for item in quits:
        if (
            category_filter
            != "すべて"
            and item.get("category")
            != category_filter
        ):
            continue

        if (
            status_filter
            != "すべて"
            and item.get("status")
            != status_filter
        ):
            continue

        if (
            type_filter
            != "すべて"
            and item.get("quit_type")
            != type_filter
        ):
            continue

        if (
            favorite_only
            and not item.get(
                "favorite",
                False,
            )
        ):
            continue

        searchable = " ".join(
            [
                item.get(
                    "title",
                    "",
                ),
                item.get(
                    "reason",
                    "",
                ),
                item.get(
                    "desired_change",
                    "",
                ),
                item.get(
                    "replacement",
                    "",
                ),
            ]
        ).lower()

        if (
            search.strip()
            and search.strip().lower()
            not in searchable
        ):
            continue

        latest = latest_review(
            data,
            item.get("id"),
        )

        rows.append(
            {
                "やめたこと":
                    item.get("title"),
                "カテゴリー":
                    item.get("category"),
                "開始":
                    item.get("start_date"),
                "日数":
                    current_days(item),
                "やめ方":
                    item.get("quit_type"),
                "状態":
                    item.get("status"),
                "期待":
                    item.get(
                        "expected_effect"
                    ),
                "最新影響":
                    (
                        latest.get(
                            "positive_effect"
                        )
                        if latest
                        else "-"
                    ),
                "経過記録":
                    len(
                        reviews_for_quit(
                            data,
                            item.get("id"),
                        )
                    ),
                "❤️":
                    (
                        "❤️"
                        if item.get(
                            "favorite"
                        )
                        else ""
                    ),
            }
        )

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            use_container_width=True,
        )

    else:
        st.info(
            "条件に合う記録は"
            "ありません。"
        )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 記録を管理"
    )

    if not quits:
        st.info(
            "まだ記録がありません。"
        )

    else:
        options = {
            quit_label(item):
            item.get("id")
            for item in quits
        }

        selected_label = (
            st.selectbox(
                "編集する記録",
                list(options.keys()),
                key="manage_quit",
            )
        )

        selected_id = options[
            selected_label
        ]

        item = get_quit(
            data,
            selected_id,
        )

        # -------------------------------------------------
        # BASIC
        # -------------------------------------------------

        st.markdown(
            "### 🚫 基本情報"
        )

        edit_title = st.text_input(
            "やめたこと",
            value=item.get(
                "title",
                "",
            ),
        )

        old_category = item.get(
            "category",
            "📦 その他",
        )

        category_index = (
            CATEGORIES.index(
                old_category
            )
            if old_category
            in CATEGORIES
            else len(CATEGORIES) - 1
        )

        edit_category = (
            st.selectbox(
                "カテゴリー",
                CATEGORIES,
                index=category_index,
                key="manage_category",
            )
        )

        old_type = item.get(
            "quit_type",
            QUIT_TYPES[0],
        )

        type_index = (
            QUIT_TYPES.index(
                old_type
            )
            if old_type in QUIT_TYPES
            else 0
        )

        edit_type = st.selectbox(
            "やめ方",
            QUIT_TYPES,
            index=type_index,
            key="manage_type",
        )

        current_start = (
            parse_date(
                item.get("start_date")
            )
            or today
        )

        edit_start = st.date_input(
            "開始日",
            value=current_start,
            max_value=today,
            key="manage_start",
        )

        edit_reason = st.text_area(
            "理由",
            value=item.get(
                "reason",
                "",
            ),
            key="manage_reason",
        )

        edit_burden = st.slider(
            "やめる前の負担",
            1,
            5,
            int(
                item.get(
                    "burden_before",
                    3,
                )
            ),
            key="manage_burden",
        )

        edit_expected = st.slider(
            "変化への期待",
            1,
            5,
            int(
                item.get(
                    "expected_effect",
                    3,
                )
            ),
            key="manage_expected",
        )

        edit_desired = st.text_area(
            "期待していた変化",
            value=item.get(
                "desired_change",
                "",
            ),
            key="manage_desired",
        )

        edit_replacement = (
            st.text_input(
                "代わりにすること",
                value=item.get(
                    "replacement",
                    "",
                ),
                key="manage_replacement",
            )
        )

        edit_favorite = st.checkbox(
            "❤️ お気に入り",
            value=item.get(
                "favorite",
                False,
            ),
            key="manage_favorite",
        )

        if st.button(
            "💾 基本情報を保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_title.strip():
                st.warning(
                    "やめたことを入力してね。"
                )

            else:
                item["title"] = (
                    edit_title.strip()
                )
                item["category"] = (
                    edit_category
                )
                item["quit_type"] = (
                    edit_type
                )
                item["start_date"] = str(
                    edit_start
                )
                item["reason"] = (
                    edit_reason.strip()
                )
                item["burden_before"] = int(
                    edit_burden
                )
                item["expected_effect"] = int(
                    edit_expected
                )
                item["desired_change"] = (
                    edit_desired.strip()
                )
                item["replacement"] = (
                    edit_replacement.strip()
                )
                item["favorite"] = (
                    edit_favorite
                )
                item["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🔄 今どうなってる？"
        )

        old_status = item.get(
            "status",
            "🟢 継続中",
        )

        status_index = (
            STATUSES.index(
                old_status
            )
            if old_status in STATUSES
            else 0
        )

        edit_status = st.selectbox(
            "状態",
            STATUSES,
            index=status_index,
            key="manage_status",
        )

        return_date = None
        return_reason = ""
        end_date = None

        if edit_status == "🔄 戻した":
            old_return = (
                parse_date(
                    item.get(
                        "return_date"
                    )
                )
                or today
            )

            return_date = st.date_input(
                "戻した日",
                value=old_return,
                max_value=today,
                key="return_date",
            )

            return_reason = (
                st.text_area(
                    "なぜ戻した？",
                    value=item.get(
                        "return_reason",
                        "",
                    ),
                    key="return_reason",
                )
            )

        elif edit_status == "✅ 終了":
            old_end = (
                parse_date(
                    item.get(
                        "end_date"
                    )
                )
                or today
            )

            end_date = st.date_input(
                "終了日",
                value=old_end,
                max_value=today,
                key="end_date",
            )

        if st.button(
            "💾 状態を保存",
            use_container_width=True,
        ):
            start = parse_date(
                item.get("start_date")
            )

            invalid = False

            if (
                edit_status
                == "🔄 戻した"
                and start
                and return_date < start
            ):
                st.warning(
                    "戻した日は開始日より"
                    "後にしてね。"
                )
                invalid = True

            if (
                edit_status
                == "✅ 終了"
                and start
                and end_date < start
            ):
                st.warning(
                    "終了日は開始日より"
                    "後にしてね。"
                )
                invalid = True

            if not invalid:
                item["status"] = (
                    edit_status
                )

                if (
                    edit_status
                    == "🔄 戻した"
                ):
                    item["return_date"] = (
                        str(return_date)
                    )
                    item["return_reason"] = (
                        return_reason.strip()
                    )
                    item["end_date"] = None

                elif (
                    edit_status
                    == "✅ 終了"
                ):
                    item["end_date"] = (
                        str(end_date)
                    )
                    item["return_date"] = None
                    item["return_reason"] = ""

                else:
                    item["return_date"] = None
                    item["return_reason"] = ""
                    item["end_date"] = None

                item["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # -------------------------------------------------
        # REVIEW EDIT
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🌱 経過記録を管理"
        )

        item_reviews = reviews_for_quit(
            data,
            selected_id,
        )

        if not item_reviews:
            st.caption(
                "経過記録はまだありません。"
            )

        else:
            review_options = {
                (
                    f"{review.get('review_date')} "
                    f"｜影響 "
                    f"{review.get('positive_effect')} "
                    f"[{review.get('id', '')[:6]}]"
                ):
                review.get("id")
                for review in item_reviews
            }

            review_label = (
                st.selectbox(
                    "編集する経過記録",
                    list(
                        review_options.keys()
                    ),
                    key="manage_review",
                )
            )

            review_id = (
                review_options[
                    review_label
                ]
            )

            review = get_review(
                data,
                review_id,
            )

            old_review_date = (
                parse_date(
                    review.get(
                        "review_date"
                    )
                )
                or today
            )

            edit_review_date = (
                st.date_input(
                    "振り返り日",
                    value=old_review_date,
                    max_value=today,
                    key="edit_review_date",
                )
            )

            edit_effect = st.slider(
                "良い影響",
                1,
                5,
                int(
                    review.get(
                        "positive_effect",
                        3,
                    )
                ),
                key="edit_effect",
            )

            edit_ease = st.slider(
                "続けやすさ",
                1,
                5,
                int(
                    review.get(
                        "ease",
                        3,
                    )
                ),
                key="edit_ease",
            )

            old_feeling = review.get(
                "feeling",
                FEELINGS[1],
            )

            feeling_index = (
                FEELINGS.index(
                    old_feeling
                )
                if old_feeling
                in FEELINGS
                else 1
            )

            edit_feeling = (
                st.selectbox(
                    "今どう思う？",
                    FEELINGS,
                    index=feeling_index,
                    key="edit_feeling",
                )
            )

            edit_change = (
                st.text_area(
                    "どう変わった？",
                    value=review.get(
                        "change_note",
                        "",
                    ),
                    key="edit_change",
                )
            )

            edit_space = st.text_area(
                "空いた場所に入ったもの",
                value=review.get(
                    "new_space",
                    "",
                ),
                key="edit_space",
            )

            if st.button(
                "💾 経過記録を保存",
                use_container_width=True,
            ):
                start = parse_date(
                    item.get(
                        "start_date"
                    )
                )

                if (
                    start
                    and edit_review_date
                    < start
                ):
                    st.warning(
                        "開始日より前には"
                        "設定できません。"
                    )

                else:
                    review[
                        "review_date"
                    ] = str(
                        edit_review_date
                    )

                    review[
                        "positive_effect"
                    ] = int(
                        edit_effect
                    )

                    review["ease"] = int(
                        edit_ease
                    )

                    review["feeling"] = (
                        edit_feeling
                    )

                    review[
                        "change_note"
                    ] = (
                        edit_change.strip()
                    )

                    review["new_space"] = (
                        edit_space.strip()
                    )

                    item["updated_at"] = (
                        now_text()
                    )

                    save_data(data)
                    st.rerun()

            confirm_review_delete = (
                st.checkbox(
                    "この経過記録を削除する",
                    key=(
                        "confirm_review_"
                        + review_id
                    ),
                )
            )

            if st.button(
                "🗑️ 経過記録を削除",
                disabled=(
                    not confirm_review_delete
                ),
                key=(
                    "delete_review_"
                    + review_id
                ),
                use_container_width=True,
            ):
                delete_review(
                    data,
                    review_id,
                )

                st.rerun()

        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        st.divider()

        st.warning(
            "この記録を削除すると、"
            "紐づいている経過記録も"
            "すべて削除されます。"
        )

        confirm_delete = st.checkbox(
            "完全に削除する",
            key=(
                "confirm_delete_"
                + selected_id
            ),
        )

        if st.button(
            "🗑️ 完全削除",
            disabled=(
                not confirm_delete
            ),
            key=(
                "delete_quit_"
                + selected_id
            ),
            use_container_width=True,
        ):
            delete_quit(
                data,
                selected_id,
            )

            st.rerun()

    # -----------------------------------------------------
    # BACKUP
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "💾 バックアップ"
    )

    backup_text = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )

    st.download_button(
        "⬇️ JSONバックアップ",
        data=backup_text,
        file_name=(
            f"quit_tracker_{today}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        <p>
            <b>
                何かを始めなくても、
                人生は変えられる。
            </b>
        </p>

        <p>
            やめる。
            <br>
            減らす。
            <br>
            少し距離を置く。
        </p>

        <p>
            そうして空いた場所に、
            <br>
            今まで入る余地のなかった何かが
            やってくることもある。
        </p>

        <p>
            <b>
                やめたことで何がなくなったかではなく、
                <br>
                何が生まれたのかを見てみよう。🌿
            </b>
        </p>

        <br>

        <b>
            DAY 309 / 365 — COMPLETE 🔥
        </b>

    </div>
    """,
    unsafe_allow_html=True,
)
