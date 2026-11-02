import json
import os
import random
import shutil
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime

import pandas as pd
import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="考えが変わった日",
    page_icon="🔄",
    layout="wide",
)


# =========================================================
# CONSTANTS
# =========================================================

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "thoughts.json")

CATEGORIES = [
    "💼 仕事",
    "💰 お金",
    "🤖 AI・テクノロジー",
    "📚 学び",
    "❤️ 恋愛・家族",
    "🤝 人間関係",
    "🌱 人生",
    "🧠 自分自身",
    "💪 健康",
    "🌍 社会",
    "🎨 趣味",
    "📦 その他",
]

TRIGGER_TYPES = [
    "🧪 経験",
    "📚 知識",
    "👤 人との出会い",
    "💬 言葉",
    "🎥 作品・コンテンツ",
    "🤖 AI",
    "⏳ 時間",
    "🤔 自分で考えた",
    "📦 その他",
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


def topic_label(topic):
    return (
        f"{topic.get('category', '')} "
        f"{topic.get('title', '')} "
        f"[{topic.get('id', '')[:6]}]"
    )


# =========================================================
# DATA
# =========================================================

def default_data():
    return {
        "topics": [],
        "updates": [],
    }


def save_data(data):
    os.makedirs(
        DATA_DIR,
        exist_ok=True,
    )

    temp_file = DATA_FILE + ".tmp"

    with open(
        temp_file,
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
        temp_file,
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
            raise ValueError(
                "JSON root is not object"
            )

        data.setdefault("topics", [])
        data.setdefault("updates", [])

        # 古いデータの補完
        for topic in data["topics"]:
            topic.setdefault(
                "id",
                new_id(),
            )
            topic.setdefault(
                "title",
                "",
            )
            topic.setdefault(
                "category",
                "📦 その他",
            )
            topic.setdefault(
                "favorite",
                False,
            )
            topic.setdefault(
                "created_at",
                now_text(),
            )
            topic.setdefault(
                "updated_at",
                topic["created_at"],
            )

        for update in data["updates"]:
            update.setdefault(
                "id",
                new_id(),
            )
            update.setdefault(
                "topic_id",
                "",
            )
            update.setdefault(
                "change_date",
                str(date.today()),
            )
            update.setdefault(
                "before",
                "",
            )
            update.setdefault(
                "after",
                "",
            )
            update.setdefault(
                "trigger_type",
                "📦 その他",
            )
            update.setdefault(
                "trigger_name",
                "",
            )
            update.setdefault(
                "trigger_note",
                "",
            )
            update.setdefault(
                "change_level",
                3,
            )
            update.setdefault(
                "note",
                "",
            )
            update.setdefault(
                "created_at",
                now_text(),
            )
            update.setdefault(
                "updated_at",
                update["created_at"],
            )

        return data

    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        # 壊れたJSONを勝手に消さない
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        broken_file = os.path.join(
            DATA_DIR,
            f"thoughts_broken_{timestamp}.json",
        )

        try:
            if os.path.exists(DATA_FILE):
                shutil.copy2(
                    DATA_FILE,
                    broken_file,
                )
        except OSError:
            pass

        data = default_data()
        save_data(data)

        st.warning(
            "⚠️ データファイルを正常に読み込めなかったため、"
            "壊れた可能性のあるJSONをバックアップして"
            "新しいデータを開始しました。"
        )

        return data


# =========================================================
# GETTERS
# =========================================================

def get_topic(data, topic_id):
    return next(
        (
            topic
            for topic in data["topics"]
            if topic.get("id") == topic_id
        ),
        None,
    )


def get_update(data, update_id):
    return next(
        (
            update
            for update in data["updates"]
            if update.get("id") == update_id
        ),
        None,
    )


def updates_for_topic(
    data,
    topic_id,
):
    result = [
        update
        for update in data["updates"]
        if update.get("topic_id")
        == topic_id
    ]

    return sorted(
        result,
        key=lambda x: (
            x.get("change_date", ""),
            x.get("created_at", ""),
        ),
    )


def latest_update(
    data,
    topic_id,
):
    updates = updates_for_topic(
        data,
        topic_id,
    )

    if not updates:
        return None

    return updates[-1]


def update_number(
    data,
    update,
):
    topic_updates = updates_for_topic(
        data,
        update.get("topic_id"),
    )

    for index, item in enumerate(
        topic_updates,
        start=1,
    ):
        if item.get("id") == update.get("id"):
            return index

    return 1


# =========================================================
# CRUD
# =========================================================

def add_topic_with_update(
    data,
    title,
    category,
    favorite,
    change_date,
    before,
    after,
    trigger_type,
    trigger_name,
    trigger_note,
    change_level,
    note,
):
    topic_id = new_id()

    topic = {
        "id": topic_id,
        "title": title,
        "category": category,
        "favorite": bool(favorite),
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    update = {
        "id": new_id(),
        "topic_id": topic_id,
        "change_date": str(change_date),
        "before": before,
        "after": after,
        "trigger_type": trigger_type,
        "trigger_name": trigger_name,
        "trigger_note": trigger_note,
        "change_level": int(
            change_level
        ),
        "note": note,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["topics"].append(topic)
    data["updates"].append(update)

    save_data(data)


def add_update(
    data,
    topic_id,
    change_date,
    before,
    after,
    trigger_type,
    trigger_name,
    trigger_note,
    change_level,
    note,
):
    update = {
        "id": new_id(),
        "topic_id": topic_id,
        "change_date": str(change_date),
        "before": before,
        "after": after,
        "trigger_type": trigger_type,
        "trigger_name": trigger_name,
        "trigger_note": trigger_note,
        "change_level": int(
            change_level
        ),
        "note": note,
        "created_at": now_text(),
        "updated_at": now_text(),
    }

    data["updates"].append(update)

    topic = get_topic(
        data,
        topic_id,
    )

    if topic:
        topic["updated_at"] = now_text()

    save_data(data)


def delete_update(
    data,
    update_id,
):
    data["updates"] = [
        update
        for update in data["updates"]
        if update.get("id")
        != update_id
    ]

    save_data(data)


def delete_topic(
    data,
    topic_id,
):
    data["topics"] = [
        topic
        for topic in data["topics"]
        if topic.get("id")
        != topic_id
    ]

    data["updates"] = [
        update
        for update in data["updates"]
        if update.get("topic_id")
        != topic_id
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
        padding: 44px 25px;
        text-align: center;
        border-radius: 28px;
        margin-bottom: 25px;

        background:
            linear-gradient(
                135deg,
                rgba(110, 150, 255, .13),
                rgba(180, 100, 255, .10),
                rgba(255, 255, 255, .02)
            );
    }

    .thought-card {
        padding: 22px;
        border-radius: 20px;
        margin-bottom: 14px;

        border:
            1px solid
            rgba(140, 120, 255, .18);
    }

    .timeline-card {
        padding: 22px;
        border-radius: 14px;
        margin: 12px 0;

        border-left:
            4px solid
            rgba(140, 120, 255, .55);

        background:
            rgba(140, 120, 255, .05);
    }

    .big-change {
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 15px;

        background:
            linear-gradient(
                135deg,
                rgba(255, 140, 80, .10),
                rgba(180, 100, 255, .06)
            );
    }

    .version-card {
        padding: 20px;
        border-radius: 18px;
        margin: 10px 0;

        background:
            rgba(110, 150, 255, .06);

        border:
            1px solid
            rgba(110, 150, 255, .15);
    }

    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 18px;

        background:
            rgba(110, 150, 255, .05);

        border:
            1px solid
            rgba(110, 150, 255, .12);
    }

    .footer {
        text-align: center;
        padding: 36px;
        margin-top: 35px;
        border-radius: 25px;

        background:
            rgba(110, 150, 255, .06);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PREPARE
# =========================================================

data = load_data()

topics = data["topics"]
updates = data["updates"]

today = date.today()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div>🔄💭 DAY 310 / 365</div>

        <h1>
            考えが変わった日
        </h1>

        <p>
            昔の自分と今の自分。
            <br>
            その間に起きたアップデートを残そう。
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
    tab_again,
    tab_lineage,
    tab_big,
    tab_update_history,
    tab_analysis,
    tab_manage,
) = st.tabs(
    [
        "🏠 ホーム",
        "🔄 考えを記録",
        "🔁 また変わった",
        "🧬 考えの系譜",
        "🌋 大きな変化",
        "🧑‍💻 MY UPDATE",
        "📊 分析",
        "🛠️ 管理",
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    st.subheader(
        "💭 自分のアップデート"
    )

    big_changes = [
        update
        for update in updates
        if int(
            update.get(
                "change_level",
                0,
            )
        ) >= 4
    ]

    trigger_counter = Counter(
        update.get("trigger_type")
        for update in updates
        if update.get("trigger_type")
    )

    top_trigger = (
        trigger_counter.most_common(1)[0][0]
        if trigger_counter
        else "-"
    )

    c1, c2, c3, c4 = (
        st.columns(4)
    )

    c1.metric(
        "🔄 考えの変化",
        f"{len(updates)}回",
    )

    c2.metric(
        "🧬 テーマ",
        f"{len(topics)}個",
    )

    c3.metric(
        "🌋 大きな変化",
        f"{len(big_changes)}回",
    )

    c4.metric(
        "⚡ 一番多いきっかけ",
        top_trigger,
    )

    # -----------------------------------------------------
    # RECENT
    # -----------------------------------------------------

    if updates:
        st.divider()

        st.subheader(
            "🆕 最近のアップデート"
        )

        recent = sorted(
            updates,
            key=lambda x: (
                x.get(
                    "change_date",
                    "",
                ),
                x.get(
                    "created_at",
                    "",
                ),
            ),
            reverse=True,
        )

        for update in recent[:5]:
            topic = get_topic(
                data,
                update.get("topic_id"),
            )

            if not topic:
                continue

            number = update_number(
                data,
                update,
            )

            st.markdown(
                f"""
                <div class="thought-card">

                    <b>
                        {topic.get("category")}
                        {topic.get("title")}
                    </b>

                    <br>

                    <small>
                        {update.get("change_date")}
                        ｜Update #{number}
                    </small>

                    <br><br>

                    💭
                    {update.get("before")}

                    <br>

                    <div style="
                        text-align:center;
                        font-size:22px;
                        padding:8px;
                    ">
                        ↓
                    </div>

                    🔄
                    <b>
                        {update.get("after")}
                    </b>

                    <br><br>

                    ⚡
                    {update.get("trigger_type")}
                    {update.get("trigger_name")}

                    <br>

                    変化：
                    {stars(
                        update.get(
                            "change_level"
                        )
                    )}

                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------
    # RANDOM
    # -----------------------------------------------------

    if updates:
        st.divider()

        st.subheader(
            "🎲 昔の自分"
        )

        candidate_ids = [
            update.get("id")
            for update in updates
        ]

        random_id = (
            st.session_state.get(
                "random_thought_update"
            )
        )

        if random_id not in candidate_ids:
            random_id = random.choice(
                candidate_ids
            )

            st.session_state[
                "random_thought_update"
            ] = random_id

        random_update = get_update(
            data,
            random_id,
        )

        random_topic = get_topic(
            data,
            random_update.get(
                "topic_id"
            ),
        )

        if random_topic:
            st.markdown(
                f"""
                <div class="thought-card">

                    <b>
                        🎲
                        {random_update.get("change_date")}
                        の自分
                    </b>

                    <h3>
                        {random_topic.get("title")}
                    </h3>

                    <p>
                        💭
                        {random_update.get("before")}
                    </p>

                    <div style="
                        text-align:center;
                        font-size:24px;
                    ">
                        ↓
                    </div>

                    <p>
                        🔄
                        <b>
                            {random_update.get("after")}
                        </b>
                    </p>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(
                "今これを読んで、"
                "また考えが変わっていたら"
                "「また変わった」から更新できます。"
            )

        if st.button(
            "🎲 別の昔の自分を見る",
            use_container_width=True,
        ):
            alternatives = [
                update_id
                for update_id
                in candidate_ids
                if update_id != random_id
            ]

            if alternatives:
                st.session_state[
                    "random_thought_update"
                ] = random.choice(
                    alternatives
                )

            st.rerun()


# =========================================================
# ADD NEW TOPIC
# =========================================================

with tab_add:

    st.subheader(
        "🔄 考えが変わった"
    )

    st.caption(
        "昔の考えを否定する必要はありません。"
        "今はどう考えているかを残してみよう。"
    )

    with st.form(
        "add_topic_form",
        clear_on_submit=True,
    ):
        title = st.text_input(
            "テーマ",
            placeholder=(
                "例：AIを使った勉強について"
            ),
        )

        category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
        )

        change_date = st.date_input(
            "考えが変わった日",
            value=today,
            max_value=today,
        )

        before = st.text_area(
            "💭 前はどう思ってた？",
            placeholder=(
                "例：AIでコードを書くと"
                "勉強にならないと思っていた"
            ),
        )

        after = st.text_area(
            "🔄 今はどう思う？",
            placeholder=(
                "例：AIを使いながら理解する"
                "勉強方法もあると思う"
            ),
        )

        trigger_type = st.selectbox(
            "⚡ 何がきっかけ？",
            TRIGGER_TYPES,
        )

        trigger_name = st.text_input(
            "きっかけになったもの",
            placeholder=(
                "例：AIと一緒に"
                "アプリを作り続けた"
            ),
        )

        trigger_note = st.text_area(
            "きっかけについて",
            placeholder=(
                "何が自分の考えに"
                "影響した？"
            ),
        )

        change_level = st.slider(
            "🌋 変化の大きさ",
            1,
            5,
            3,
        )

        st.write(
            stars(change_level)
        )

        note = st.text_area(
            "📝 今思うこと",
            placeholder=(
                "この変化について"
                "残しておきたいこと"
            ),
        )

        favorite = st.checkbox(
            "❤️ 大切なテーマにする"
        )

        submitted = (
            st.form_submit_button(
                "🔄 アップデートを記録",
                type="primary",
                use_container_width=True,
            )
        )

        if submitted:
            if not title.strip():
                st.warning(
                    "テーマを入力してね。"
                )

            elif not before.strip():
                st.warning(
                    "以前の考えを入力してね。"
                )

            elif not after.strip():
                st.warning(
                    "今の考えを入力してね。"
                )

            else:
                add_topic_with_update(
                    data=data,
                    title=title.strip(),
                    category=category,
                    favorite=favorite,
                    change_date=change_date,
                    before=before.strip(),
                    after=after.strip(),
                    trigger_type=(
                        trigger_type
                    ),
                    trigger_name=(
                        trigger_name.strip()
                    ),
                    trigger_note=(
                        trigger_note.strip()
                    ),
                    change_level=(
                        change_level
                    ),
                    note=note.strip(),
                )

                st.rerun()


# =========================================================
# AGAIN
# =========================================================

with tab_again:

    st.subheader(
        "🔁 また考えが変わった"
    )

    if not topics:
        st.info(
            "まずは最初の考えの変化を"
            "記録してみよう。"
        )

    else:
        options = {
            topic_label(topic):
            topic.get("id")
            for topic in topics
        }

        selected_label = (
            st.selectbox(
                "テーマ",
                list(options.keys()),
                key="again_topic",
            )
        )

        topic_id = options[
            selected_label
        ]

        topic = get_topic(
            data,
            topic_id,
        )

        previous = latest_update(
            data,
            topic_id,
        )

        st.markdown(
            f"### {topic.get('category')} "
            f"{topic.get('title')}"
        )

        if previous:
            st.info(
                "現在の考え：\n\n"
                + previous.get(
                    "after",
                    "",
                )
            )

        with st.form(
            "again_form"
        ):
            change_date = st.date_input(
                "今回変わった日",
                value=today,
                max_value=today,
            )

            before_default = (
                previous.get(
                    "after",
                    "",
                )
                if previous
                else ""
            )

            before = st.text_area(
                "💭 これまでの考え",
                value=before_default,
            )

            after = st.text_area(
                "🔄 今はどう思う？",
                placeholder=(
                    "今の考えを書いてみよう"
                ),
            )

            trigger_type = st.selectbox(
                "⚡ 今回のきっかけ",
                TRIGGER_TYPES,
                key="again_trigger",
            )

            trigger_name = st.text_input(
                "きっかけになったもの",
            )

            trigger_note = st.text_area(
                "きっかけについて",
            )

            change_level = st.slider(
                "🌋 今回の変化の大きさ",
                1,
                5,
                3,
            )

            note = st.text_area(
                "📝 今回のメモ"
            )

            submitted = (
                st.form_submit_button(
                    "🔁 新しい考えを追加",
                    type="primary",
                    use_container_width=True,
                )
            )

            if submitted:
                previous_date = (
                    parse_date(
                        previous.get(
                            "change_date"
                        )
                    )
                    if previous
                    else None
                )

                if not before.strip():
                    st.warning(
                        "これまでの考えを"
                        "入力してね。"
                    )

                elif not after.strip():
                    st.warning(
                        "今の考えを入力してね。"
                    )

                elif (
                    previous_date
                    and change_date
                    < previous_date
                ):
                    st.warning(
                        "前回の更新より前の日付には"
                        "できません。"
                    )

                else:
                    add_update(
                        data=data,
                        topic_id=topic_id,
                        change_date=(
                            change_date
                        ),
                        before=before.strip(),
                        after=after.strip(),
                        trigger_type=(
                            trigger_type
                        ),
                        trigger_name=(
                            trigger_name.strip()
                        ),
                        trigger_note=(
                            trigger_note.strip()
                        ),
                        change_level=(
                            change_level
                        ),
                        note=note.strip(),
                    )

                    st.rerun()


# =========================================================
# LINEAGE
# =========================================================

with tab_lineage:

    st.subheader(
        "🧬 考えの系譜"
    )

    st.caption(
        "ひとつのテーマについて、"
        "自分の考えがどう変化してきたか。"
    )

    if not topics:
        st.info(
            "まだテーマがありません。"
        )

    else:
        options = {
            topic_label(topic):
            topic.get("id")
            for topic in topics
        }

        selected_label = (
            st.selectbox(
                "見るテーマ",
                list(options.keys()),
                key="lineage_topic",
            )
        )

        topic_id = options[
            selected_label
        ]

        topic = get_topic(
            data,
            topic_id,
        )

        topic_updates = (
            updates_for_topic(
                data,
                topic_id,
            )
        )

        st.markdown(
            f"## {topic.get('category')} "
            f"{topic.get('title')}"
        )

        for index, update in enumerate(
            topic_updates,
            start=1,
        ):
            st.markdown(
                f"""
                <div class="timeline-card">

                    <b>
                        v1.{index - 1}
                        ｜{update.get("change_date")}
                    </b>

                    <br><br>

                    💭
                    {update.get("before")}

                    <br>

                    <div style="
                        text-align:center;
                        font-size:24px;
                        padding:8px;
                    ">
                        ↓
                    </div>

                    🔄
                    <b>
                        {update.get("after")}
                    </b>

                    <br><br>

                    ⚡
                    {update.get("trigger_type")}
                    {update.get("trigger_name")}

                    <br>

                    🌋
                    {stars(
                        update.get(
                            "change_level"
                        )
                    )}

                    <br><br>

                    {update.get("note", "")}

                </div>
                """,
                unsafe_allow_html=True,
            )

            if index < len(
                topic_updates
            ):
                st.markdown(
                    """
                    <div style="
                        text-align:center;
                        font-size:26px;
                    ">
                        ↓
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =========================================================
# BIG CHANGES
# =========================================================

with tab_big:

    st.subheader(
        "🌋 大きく変わった考え"
    )

    big_updates = sorted(
        [
            update
            for update in updates
            if int(
                update.get(
                    "change_level",
                    0,
                )
            ) >= 4
        ],
        key=lambda x: (
            int(
                x.get(
                    "change_level",
                    0,
                )
            ),
            x.get(
                "change_date",
                "",
            ),
        ),
        reverse=True,
    )

    if not big_updates:
        st.info(
            "変化の大きさ4以上の記録が"
            "ここに並びます。"
        )

    for update in big_updates:
        topic = get_topic(
            data,
            update.get("topic_id"),
        )

        if not topic:
            continue

        st.markdown(
            f"""
            <div class="big-change">

                <b>
                    🌋 {topic.get("category")}
                    {topic.get("title")}
                </b>

                <br>

                <small>
                    {update.get("change_date")}
                </small>

                <br><br>

                {stars(
                    update.get(
                        "change_level"
                    )
                )}

                <br><br>

                💭
                {update.get("before")}

                <div style="
                    text-align:center;
                    font-size:24px;
                ">
                    ↓
                </div>

                🔄
                <b>
                    {update.get("after")}
                </b>

                <br><br>

                ⚡
                {update.get("trigger_type")}
                {update.get("trigger_name")}

            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# MY UPDATE HISTORY
# =========================================================

with tab_update_history:

    st.subheader(
        "🧑‍💻 MY UPDATE HISTORY"
    )

    st.caption(
        "人間にも、アップデート履歴がある。"
    )

    if not updates:
        st.info(
            "アップデートはまだありません。"
        )

    else:
        all_updates = sorted(
            updates,
            key=lambda x: (
                x.get(
                    "change_date",
                    "",
                ),
                x.get(
                    "created_at",
                    "",
                ),
            ),
        )

        for index, update in enumerate(
            all_updates,
            start=1,
        ):
            topic = get_topic(
                data,
                update.get("topic_id"),
            )

            if not topic:
                continue

            major = 1 + (
                (index - 1) // 10
            )

            minor = (
                (index - 1) % 10
            )

            version = (
                f"v{major}.{minor}"
            )

            st.markdown(
                f"""
                <div class="version-card">

                    <b>
                        🧑‍💻 {version}
                    </b>

                    <small>
                        ｜{update.get("change_date")}
                    </small>

                    <br>

                    <b>
                        {topic.get("title")}
                    </b>

                    <br><br>

                    💭
                    {update.get("before")}

                    <br>

                    ↓

                    <br>

                    🔄
                    {update.get("after")}

                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# ANALYSIS
# =========================================================

with tab_analysis:

    st.subheader(
        "📊 自分はどう変わってきた？"
    )

    if not updates:
        st.info(
            "記録が増えると分析できます。"
        )

    else:
        levels = [
            int(
                update.get(
                    "change_level",
                    0,
                )
            )
            for update in updates
        ]

        multi_topics = sum(
            1
            for topic in topics
            if len(
                updates_for_topic(
                    data,
                    topic.get("id"),
                )
            ) >= 2
        )

        favorite_topics = sum(
            1
            for topic in topics
            if topic.get(
                "favorite",
                False,
            )
        )

        c1, c2, c3, c4 = (
            st.columns(4)
        )

        c1.metric(
            "🔄 更新回数",
            len(updates),
        )

        c2.metric(
            "🌋 平均変化度",
            f"{sum(levels) / len(levels):.1f}",
        )

        c3.metric(
            "🔁 複数回変化したテーマ",
            multi_topics,
        )

        c4.metric(
            "❤️ 大切なテーマ",
            favorite_topics,
        )

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 📚 よく変化した分野"
        )

        category_counter = Counter()

        for update in updates:
            topic = get_topic(
                data,
                update.get("topic_id"),
            )

            if topic:
                category_counter[
                    topic.get("category")
                ] += 1

        category_df = pd.DataFrame(
            [
                {
                    "分野": category,
                    "変化した回数": count,
                }
                for category, count
                in category_counter
                .most_common()
            ]
        )

        st.dataframe(
            category_df,
            hide_index=True,
            use_container_width=True,
        )

        if not category_df.empty:
            st.bar_chart(
                category_df.set_index(
                    "分野"
                )
            )

        # -------------------------------------------------
        # TRIGGERS
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### ⚡ 何によって考えが変わる？"
        )

        trigger_counter = Counter(
            update.get(
                "trigger_type"
            )
            for update in updates
        )

        trigger_df = pd.DataFrame(
            [
                {
                    "きっかけ": trigger,
                    "回数": count,
                }
                for trigger, count
                in trigger_counter
                .most_common()
            ]
        )

        st.dataframe(
            trigger_df,
            hide_index=True,
            use_container_width=True,
        )

        if not trigger_df.empty:
            st.bar_chart(
                trigger_df.set_index(
                    "きっかけ"
                )
            )

        # -------------------------------------------------
        # AVERAGE LEVEL BY TRIGGER
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🌋 大きな変化を生んだもの"
        )

        trigger_levels = defaultdict(
            list
        )

        for update in updates:
            trigger_levels[
                update.get(
                    "trigger_type"
                )
            ].append(
                int(
                    update.get(
                        "change_level",
                        0,
                    )
                )
            )

        trigger_level_rows = []

        for trigger, values in (
            trigger_levels.items()
        ):
            trigger_level_rows.append(
                {
                    "きっかけ":
                        trigger,
                    "回数":
                        len(values),
                    "平均変化度":
                        round(
                            sum(values)
                            / len(values),
                            1,
                        ),
                }
            )

        trigger_level_df = (
            pd.DataFrame(
                trigger_level_rows
            )
            .sort_values(
                "平均変化度",
                ascending=False,
            )
        )

        st.dataframe(
            trigger_level_df,
            hide_index=True,
            use_container_width=True,
        )

        # -------------------------------------------------
        # MONTHLY
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🗓️ 月ごとのアップデート"
        )

        monthly_counter = Counter()

        for update in updates:
            change_date = parse_date(
                update.get(
                    "change_date"
                )
            )

            if change_date:
                month = (
                    f"{change_date.year}-"
                    f"{change_date.month:02d}"
                )

                monthly_counter[
                    month
                ] += 1

        if monthly_counter:
            monthly_df = pd.DataFrame(
                [
                    {
                        "月": month,
                        "更新回数": count,
                    }
                    for month, count
                    in sorted(
                        monthly_counter.items()
                    )
                ]
            )

            st.bar_chart(
                monthly_df.set_index(
                    "月"
                )
            )

        # -------------------------------------------------
        # MOST UPDATED
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🔁 何度も考え直したテーマ"
        )

        topic_counts = []

        for topic in topics:
            count = len(
                updates_for_topic(
                    data,
                    topic.get("id"),
                )
            )

            topic_counts.append(
                (
                    count,
                    topic,
                )
            )

        topic_counts.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        for count, topic in (
            topic_counts[:10]
        ):
            st.write(
                f"**{topic.get('title')}** "
                f"— {count}回"
            )


# =========================================================
# MANAGE
# =========================================================

with tab_manage:

    st.subheader(
        "🛠️ 記録を管理"
    )

    if not topics:
        st.info(
            "まだテーマがありません。"
        )

    else:
        topic_options = {
            topic_label(topic):
            topic.get("id")
            for topic in topics
        }

        selected_label = (
            st.selectbox(
                "編集するテーマ",
                list(
                    topic_options.keys()
                ),
                key="manage_topic",
            )
        )

        topic_id = topic_options[
            selected_label
        ]

        topic = get_topic(
            data,
            topic_id,
        )

        # -------------------------------------------------
        # TOPIC
        # -------------------------------------------------

        st.markdown(
            "### 🧬 テーマ"
        )

        edit_title = st.text_input(
            "テーマ名",
            value=topic.get(
                "title",
                "",
            ),
            key="edit_topic_title",
        )

        old_category = topic.get(
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

        edit_category = st.selectbox(
            "カテゴリー",
            CATEGORIES,
            index=category_index,
            key="edit_topic_category",
        )

        edit_favorite = st.checkbox(
            "❤️ 大切なテーマ",
            value=topic.get(
                "favorite",
                False,
            ),
            key="edit_topic_favorite",
        )

        if st.button(
            "💾 テーマを保存",
            type="primary",
            use_container_width=True,
        ):
            if not edit_title.strip():
                st.warning(
                    "テーマ名を入力してね。"
                )

            else:
                topic["title"] = (
                    edit_title.strip()
                )
                topic["category"] = (
                    edit_category
                )
                topic["favorite"] = (
                    edit_favorite
                )
                topic["updated_at"] = (
                    now_text()
                )

                save_data(data)
                st.rerun()

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        st.divider()

        st.markdown(
            "### 🔄 アップデート履歴"
        )

        topic_updates = (
            updates_for_topic(
                data,
                topic_id,
            )
        )

        if not topic_updates:
            st.caption(
                "アップデートがありません。"
            )

        else:
            update_options = {
                (
                    f"{update.get('change_date')} "
                    f"｜{update.get('after', '')[:25]} "
                    f"[{update.get('id', '')[:6]}]"
                ):
                update.get("id")
                for update
                in topic_updates
            }

            update_label = (
                st.selectbox(
                    "編集する更新",
                    list(
                        update_options.keys()
                    ),
                    key="manage_update",
                )
            )

            update_id = (
                update_options[
                    update_label
                ]
            )

            update = get_update(
                data,
                update_id,
            )

            current_date = (
                parse_date(
                    update.get(
                        "change_date"
                    )
                )
                or today
            )

            edit_date = st.date_input(
                "変化した日",
                value=current_date,
                max_value=today,
                key="edit_update_date",
            )

            edit_before = st.text_area(
                "以前の考え",
                value=update.get(
                    "before",
                    "",
                ),
                key="edit_before",
            )

            edit_after = st.text_area(
                "新しい考え",
                value=update.get(
                    "after",
                    "",
                ),
                key="edit_after",
            )

            old_trigger = update.get(
                "trigger_type",
                "📦 その他",
            )

            trigger_index = (
                TRIGGER_TYPES.index(
                    old_trigger
                )
                if old_trigger
                in TRIGGER_TYPES
                else len(
                    TRIGGER_TYPES
                ) - 1
            )

            edit_trigger = (
                st.selectbox(
                    "きっかけ",
                    TRIGGER_TYPES,
                    index=trigger_index,
                    key="edit_trigger",
                )
            )

            edit_trigger_name = (
                st.text_input(
                    "きっかけになったもの",
                    value=update.get(
                        "trigger_name",
                        "",
                    ),
                    key=(
                        "edit_trigger_name"
                    ),
                )
            )

            edit_trigger_note = (
                st.text_area(
                    "きっかけについて",
                    value=update.get(
                        "trigger_note",
                        "",
                    ),
                    key=(
                        "edit_trigger_note"
                    ),
                )
            )

            edit_level = st.slider(
                "変化の大きさ",
                1,
                5,
                int(
                    update.get(
                        "change_level",
                        3,
                    )
                ),
                key="edit_level",
            )

            edit_note = st.text_area(
                "メモ",
                value=update.get(
                    "note",
                    "",
                ),
                key="edit_note",
            )

            if st.button(
                "💾 アップデートを保存",
                use_container_width=True,
            ):
                if not edit_before.strip():
                    st.warning(
                        "以前の考えを入力してね。"
                    )

                elif not edit_after.strip():
                    st.warning(
                        "新しい考えを入力してね。"
                    )

                else:
                    update[
                        "change_date"
                    ] = str(
                        edit_date
                    )

                    update["before"] = (
                        edit_before.strip()
                    )

                    update["after"] = (
                        edit_after.strip()
                    )

                    update[
                        "trigger_type"
                    ] = edit_trigger

                    update[
                        "trigger_name"
                    ] = (
                        edit_trigger_name
                        .strip()
                    )

                    update[
                        "trigger_note"
                    ] = (
                        edit_trigger_note
                        .strip()
                    )

                    update[
                        "change_level"
                    ] = int(
                        edit_level
                    )

                    update["note"] = (
                        edit_note.strip()
                    )

                    update[
                        "updated_at"
                    ] = now_text()

                    topic[
                        "updated_at"
                    ] = now_text()

                    save_data(data)
                    st.rerun()

            # DELETE UPDATE
            confirm_update_delete = (
                st.checkbox(
                    "このアップデートを削除する",
                    key=(
                        "confirm_update_"
                        + update_id
                    ),
                )
            )

            if st.button(
                "🗑️ アップデートを削除",
                disabled=(
                    not confirm_update_delete
                ),
                key=(
                    "delete_update_"
                    + update_id
                ),
                use_container_width=True,
            ):
                delete_update(
                    data,
                    update_id,
                )

                st.rerun()

        # -------------------------------------------------
        # DELETE TOPIC
        # -------------------------------------------------

        st.divider()

        st.warning(
            "テーマを削除すると、"
            "このテーマに紐づく"
            "すべてのアップデートも削除されます。"
        )

        confirm_topic_delete = (
            st.checkbox(
                "このテーマを完全に削除する",
                key=(
                    "confirm_topic_"
                    + topic_id
                ),
            )
        )

        if st.button(
            "🗑️ テーマを完全削除",
            disabled=(
                not confirm_topic_delete
            ),
            key=(
                "delete_topic_"
                + topic_id
            ),
            use_container_width=True,
        ):
            delete_topic(
                data,
                topic_id,
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
            f"thought_update_{today}.json"
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
                昔の自分と、今の自分。
            </b>
        </p>

        <p>
            違っていていい。
        </p>

        <p>
            経験して、知って、悩んで、
            <br>
            また少し考えが変わる。
        </p>

        <p>
            それはブレたのではなく、
            <br>
            世界を見る角度が
            ひとつ増えたのかもしれない。
        </p>

        <p>
            <b>
                今日の自分も、
                まだ完成版じゃない。🔄💭
            </b>
        </p>

        <br>

        <b>
            DAY 310 / 365 — COMPLETE 🔥
        </b>

    </div>
    """,
    unsafe_allow_html=True,
)
