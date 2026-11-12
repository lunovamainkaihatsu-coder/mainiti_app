import json
import os
import uuid
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title='今日、誰を笑顔にできた？', page_icon='😊', layout='wide')
DATA = Path(__file__).parent / 'data' / 'smiles.json'
CATEGORIES = ['手助け', '励まし', 'プレゼント', '一緒に過ごす', '教える・伝える', '感謝・気遣い', 'その他']
RELATIONS = ['家族', '友人', '仕事仲間', '知人', '地域の人', 'その他']
STATUSES = ['予定', '実施', '見送り']
KEYS = ('smiles', 'people', 'challenges')


def blank():
    return {key: [] for key in KEYS}


def uid():
    return str(uuid.uuid4())


def now():
    return datetime.now().isoformat(timespec='seconds')


def validate(obj):
    if not isinstance(obj, dict) or any(not isinstance(obj.get(k), list) for k in KEYS):
        raise ValueError('smiles、people、challenges の配列が必要です。')
    ids = []
    for key in KEYS:
        for record in obj[key]:
            if not isinstance(record, dict) or not isinstance(record.get('id'), str) or not record['id']:
                raise ValueError(f'{key} に不正な記録があります。')
            ids.append(record['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('IDが重複しています。')
    people_ids = {p['id'] for p in obj['people']}
    for smile in obj['smiles']:
        if not isinstance(smile.get('title'), str) or not smile['title'].strip():
            raise ValueError('記録タイトルが不正です。')
        if smile.get('person_id') is not None and smile['person_id'] not in people_ids:
            raise ValueError('存在しない相手への参照があります。')
        if smile.get('category') not in CATEGORIES:
            raise ValueError('カテゴリーが不正です。')
        for field in ('joy', 'happiness'):
            value = smile.get(field)
            if type(value) is not int or not 1 <= value <= 5:
                raise ValueError('評価は1〜5の整数にしてください。')
    for person in obj['people']:
        if not isinstance(person.get('name'), str) or not person['name'].strip():
            raise ValueError('相手の名前が不正です。')
        if person.get('relation') not in RELATIONS:
            raise ValueError('関係性が不正です。')
    for challenge in obj['challenges']:
        if not isinstance(challenge.get('title'), str) or not challenge['title'].strip():
            raise ValueError('チャレンジ名が不正です。')
        if challenge.get('status') not in STATUSES:
            raise ValueError('チャレンジの状態が不正です。')
    return obj


def save():
    validate(db)
    DATA.parent.mkdir(parents=True, exist_ok=True)
    temp = DATA.with_suffix('.tmp')
    with temp.open('w', encoding='utf-8') as handle:
        json.dump(db, handle, ensure_ascii=False, indent=2)
    os.replace(temp, DATA)


def load():
    if not DATA.exists():
        return blank()
    try:
        return validate(json.loads(DATA.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError) as error:
        st.error(f'保存データを読み込めません。ファイルは変更していません：{error}')
        st.stop()


def commit():
    save()
    st.rerun()


def person_name(person_id):
    return next((p['name'] for p in db['people'] if p['id'] == person_id), '未登録・匿名')


def person_choices():
    return {'未登録・匿名': None, **{f"{p['name']} ({p['relation']}) [{p['id'][:6]}]": p['id'] for p in db['people']}}


def smile_card(record):
    with st.container(border=True):
        left, right = st.columns([5, 1])
        left.markdown(f"**😊 {record['title']}**")
        right.write('❤️' if record.get('favorite') else '🌷')
        st.caption(f"{record['date']}｜{record['category']}｜{person_name(record.get('person_id'))}")
        st.write(record.get('action', ''))
        if record.get('reaction'):
            st.write('相手の反応：', record['reaction'])
        st.caption(f"喜んだと感じた度合い {record['joy']}/5（推定）｜自分の幸福度 {record['happiness']}/5")
        if record.get('memo'):
            st.write('感想：', record['memo'])


def edit_fields(kind, record):
    """A complete, type-aware editor for each record kind."""
    fields = {}
    if kind == 'people':
        fields['name'] = st.text_input('名前・呼び名', value=record['name'])
        fields['relation'] = st.selectbox('関係性', RELATIONS, index=RELATIONS.index(record['relation']))
        fields['memo'] = st.text_area('メモ', value=record.get('memo', ''))
    elif kind == 'smiles':
        fields['title'] = st.text_input('タイトル', value=record['title'])
        fields['date'] = str(st.date_input('日付', value=date.fromisoformat(record['date'])))
        fields['category'] = st.selectbox('カテゴリー', CATEGORIES, index=CATEGORIES.index(record['category']))
        choices = person_choices()
        labels = list(choices)
        selected = next((i for i, label in enumerate(labels) if choices[label] == record.get('person_id')), 0)
        fields['person_id'] = choices[st.selectbox('相手', labels, index=selected)]
        fields['action'] = st.text_area('行動', value=record.get('action', ''))
        fields['reaction'] = st.text_area('相手の反応', value=record.get('reaction', ''))
        fields['joy'] = st.slider('喜んだと感じた度合い（推定）', 1, 5, int(record['joy']))
        fields['happiness'] = st.slider('自分の幸福度', 1, 5, int(record['happiness']))
        fields['memo'] = st.text_area('感想', value=record.get('memo', ''))
        fields['favorite'] = st.checkbox('お気に入り', value=bool(record.get('favorite', False)))
    else:
        fields['title'] = st.text_input('チャレンジ名', value=record['title'])
        fields['date'] = str(st.date_input('予定日', value=date.fromisoformat(record['date'])))
        fields['status'] = st.selectbox('状態', STATUSES, index=STATUSES.index(record['status']))
        fields['action'] = st.text_area('行動内容', value=record.get('action', ''))
        fields['result'] = st.text_area('結果', value=record.get('result', ''))
        fields['memo'] = st.text_area('感想', value=record.get('memo', ''))
    return fields


db = load()
st.title('😊🌷 今日、誰を笑顔にできた？')
st.caption('Day318 / 365 — 優しさは数字で測りきれない。でも、思い出として残せる。')
st.info('相手の喜び度は自分から見た推定です。喜んでくれたか分からないときも、無理に良い反応として解釈しなくて大丈夫。')
tabs = st.tabs(['🏠 ホーム', '😊 笑顔を登録', '🌸 優しさの種類', '📖 笑顔アルバム', '🤝 つながりマップ', '🌱 優しさチャレンジ', '📊 笑顔分析', '🛠️ 管理'])

with tabs[0]:
    st.subheader('🏠 笑顔のダッシュボード')
    cols = st.columns(4)
    metrics = [('笑顔の記録', len(db['smiles'])), ('記録した相手', len(db['people'])), ('お気に入り', sum(bool(s.get('favorite')) for s in db['smiles'])), ('実施したチャレンジ', sum(c['status'] == '実施' for c in db['challenges']))]
    for col, (name, value) in zip(cols, metrics):
        col.metric(name, value)
    st.markdown('### 最近の出来事')
    for record in sorted(db['smiles'], key=lambda x: (x['date'], x['created_at']), reverse=True)[:5]:
        smile_card(record)
    if not db['smiles']:
        st.info('最初の小さな出来事を登録してみよう！')

with tabs[1]:
    st.subheader('😊 笑顔にできた瞬間を登録')
    with st.form('new_smile', clear_on_submit=True):
        title = st.text_input('出来事のタイトル *')
        day = st.date_input('日付', value=date.today())
        category = st.selectbox('優しさの種類', CATEGORIES)
        choices = person_choices()
        person_id = choices[st.selectbox('相手（登録済みから選択）', list(choices))]
        action = st.text_area('どんなことをした？')
        reaction = st.text_area('相手の反応（分からなければ空欄でOK）')
        c1, c2 = st.columns(2)
        joy = c1.slider('相手が喜んだと感じた度合い（推定）', 1, 5, 3)
        happiness = c2.slider('自分の幸福度', 1, 5, 3)
        memo = st.text_area('感想')
        favorite = st.checkbox('お気に入りにする')
        if st.form_submit_button('😊 記録を保存', type='primary'):
            if not title.strip():
                st.warning('タイトルを入力してね。')
            else:
                db['smiles'].append(dict(id=uid(), created_at=now(), title=title.strip(), date=str(day), category=category, person_id=person_id, action=action.strip(), reaction=reaction.strip(), joy=joy, happiness=happiness, memo=memo.strip(), favorite=favorite))
                commit()
    st.caption('相手を登録するには「🤝 つながりマップ」を開いてね。')

with tabs[2]:
    st.subheader('🌸 優しさの種類')
    descriptions = {'手助け': '困っている人を助けた', '励まし': '言葉で支えた', 'プレゼント': '贈り物やサプライズ', '一緒に過ごす': '一緒の時間を大切にした', '教える・伝える': '知識や経験を役立てた', '感謝・気遣い': 'ありがとうや気遣いを伝えた', 'その他': '分類にとらわれない優しさ'}
    counts = Counter(s['category'] for s in db['smiles'])
    for category in CATEGORIES:
        with st.container(border=True):
            st.markdown(f"**{category}** — {counts[category]}件")
            st.caption(descriptions[category])
    if db['smiles']:
        st.bar_chart(pd.Series({k: counts[k] for k in CATEGORIES}, name='件数'))

with tabs[3]:
    st.subheader('📖 笑顔アルバム')
    query = st.text_input('🔎 タイトル・行動・感想を検索')
    c1, c2, c3 = st.columns(3)
    category_filter = c1.selectbox('カテゴリー', ['すべて'] + CATEGORIES)
    relation_filter = c2.selectbox('関係性', ['すべて'] + RELATIONS + ['未登録・匿名'])
    favorite_only = c3.checkbox('お気に入りのみ')
    filtered = []
    for record in db['smiles']:
        if query.lower() not in ' '.join(str(record.get(k, '')) for k in ('title', 'action', 'reaction', 'memo')).lower():
            continue
        if category_filter != 'すべて' and record['category'] != category_filter:
            continue
        person = next((p for p in db['people'] if p['id'] == record.get('person_id')), None)
        relation = person['relation'] if person else '未登録・匿名'
        if relation_filter != 'すべて' and relation != relation_filter:
            continue
        if favorite_only and not record.get('favorite'):
            continue
        filtered.append(record)
    st.caption(f'{len(filtered)}件')
    for record in sorted(filtered, key=lambda x: (x['date'], x['created_at']), reverse=True):
        smile_card(record)

with tabs[4]:
    st.subheader('🤝 人とのつながり')
    st.caption('相手の呼び名は個人情報になり得るので、ニックネームでの登録もおすすめ。')
    with st.form('new_person', clear_on_submit=True):
        name = st.text_input('相手の呼び名 *')
        relation = st.selectbox('関係性', RELATIONS)
        memo = st.text_area('メモ')
        if st.form_submit_button('🤝 相手を登録'):
            if not name.strip():
                st.warning('呼び名を入力してね。')
            else:
                db['people'].append(dict(id=uid(), created_at=now(), name=name.strip(), relation=relation, memo=memo.strip()))
                commit()
    if db['people']:
        options = {f"{p['name']} [{p['id'][:6]}]": p['id'] for p in db['people']}
        selected_id = options[st.selectbox('思い出を見る相手', list(options))]
        memories = [s for s in db['smiles'] if s.get('person_id') == selected_id]
        st.caption(f'記録 {len(memories)}件')
        for record in sorted(memories, key=lambda x: x['date'], reverse=True):
            smile_card(record)
    if db['smiles']:
        counts = Counter(next((p['relation'] for p in db['people'] if p['id'] == s.get('person_id')), '未登録・匿名') for s in db['smiles'])
        st.markdown('### 関係性別の記録件数')
        st.bar_chart(pd.Series(counts, name='件数'))

with tabs[5]:
    st.subheader('🌱 優しさチャレンジ')
    with st.form('new_challenge', clear_on_submit=True):
        title = st.text_input('小さなチャレンジ *')
        day = st.date_input('予定日', value=date.today())
        status = st.selectbox('状態', STATUSES)
        action = st.text_area('やってみたいこと')
        result = st.text_area('結果（あとから管理画面で編集できるよ）')
        memo = st.text_area('感想')
        if st.form_submit_button('🌱 チャレンジを保存'):
            if not title.strip():
                st.warning('チャレンジ名を入力してね。')
            else:
                db['challenges'].append(dict(id=uid(), created_at=now(), title=title.strip(), date=str(day), status=status, action=action.strip(), result=result.strip(), memo=memo.strip()))
                commit()
    for record in sorted(db['challenges'], key=lambda x: x['date'], reverse=True):
        with st.container(border=True):
            st.markdown(f"**{record['title']}** — {record['status']}")
            st.caption(record['date'])
            st.write(record.get('action', ''))
            if record.get('result'):
                st.write('結果：', record['result'])

with tabs[6]:
    st.subheader('📊 笑顔分析')
    if not db['smiles']:
        st.info('笑顔の記録を追加すると分析できるよ。')
    else:
        df = pd.DataFrame(db['smiles'])
        c1, c2 = st.columns(2)
        c1.metric('平均幸福度', f"{df['happiness'].mean():.2f} / 5")
        c2.metric('喜んだと感じた度合いの平均（推定）', f"{df['joy'].mean():.2f} / 5")
        st.markdown('### 月別記録件数')
        df['month'] = df['date'].str.slice(0, 7)
        st.bar_chart(df.groupby('month').size().rename('件数'))
        st.markdown('### カテゴリー別記録件数')
        st.bar_chart(df.groupby('category').size().rename('件数'))
        st.markdown('### 記録日ごとの平均幸福度')
        st.line_chart(df.groupby('date')['happiness'].mean().sort_index())
        st.caption('幸福度は自分の主観的な評価です。数値が高いほど人間関係が良い、という意味ではありません。')
    if db['challenges']:
        st.markdown('### チャレンジの状態')
        st.bar_chart(pd.Series(Counter(c['status'] for c in db['challenges']), name='件数'))

with tabs[7]:
    st.subheader('🛠️ 編集・削除・バックアップ')
    kind = st.selectbox('編集する記録', KEYS, format_func=lambda x: {'smiles': '😊 笑顔', 'people': '🤝 相手', 'challenges': '🌱 チャレンジ'}[x])
    if db[kind]:
        def record_label(record):
            return f"{record.get('title', record.get('name', '記録'))} [{record['id'][:8]}]"
        labels = {record_label(r): r['id'] for r in db[kind]}
        selected_id = labels[st.selectbox('対象', list(labels), key='edit_select_' + kind)]
        record = next(r for r in db[kind] if r['id'] == selected_id)
        with st.form(f'edit_{kind}_{selected_id}'):
            updated = edit_fields(kind, record)
            if st.form_submit_button('💾 編集内容を保存', type='primary'):
                if not updated.get('title', updated.get('name', '')).strip():
                    st.warning('タイトル・名前は空にできません。')
                else:
                    record.update(updated)
                    record['updated_at'] = now()
                    commit()
        if kind == 'people':
            st.caption('相手を削除した場合、関連する笑顔の記録は「未登録・匿名」になります。')
        confirmed = st.checkbox('削除することを確認しました', key='confirm_' + selected_id)
        if st.button('🗑️ 選択した記録を削除', disabled=not confirmed):
            if kind == 'people':
                for smile in db['smiles']:
                    if smile.get('person_id') == selected_id:
                        smile['person_id'] = None
            db[kind] = [r for r in db[kind] if r['id'] != selected_id]
            commit()
    else:
        st.info('この種類の記録はまだありません。')
    st.divider()
    st.subheader('💾 JSONバックアップ')
    st.download_button('⬇️ バックアップを保存', json.dumps(db, ensure_ascii=False, indent=2), file_name=f"smiles_{date.today().isoformat()}.json", mime='application/json')
    st.subheader('📤 JSONから復元')
    st.warning('復元すると現在のデータがすべて置き換わるよ。先にバックアップを取ってね。')
    upload = st.file_uploader('バックアップJSON', type=['json'])
    if upload:
        try:
            restored = validate(json.loads(upload.getvalue().decode('utf-8')))
            st.success('データ形式を確認しました。' + ' / '.join(f'{k}: {len(restored[k])}件' for k in KEYS))
            confirmed = st.checkbox('現在のデータを置き換えることに同意します')
            if st.button('📤 復元する', disabled=not confirmed, type='primary'):
                db = restored
                commit()
        except (ValueError, TypeError, UnicodeDecodeError) as error:
            st.error(f'復元できません：{error}')

st.divider()
st.caption('Day318 / 365 — 小さな優しさを、大切な思い出に。🌷')
