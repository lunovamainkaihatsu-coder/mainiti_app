import streamlit as st
import pandas as pd
import json, uuid, calendar
from datetime import datetime, date
from pathlib import Path

st.set_page_config(page_title='もしも、時間があったなら', page_icon='⏳', layout='wide')
PATH = Path(__file__).parent / 'data' / 'activities.json'
CATS = ['学習','仕事・開発','健康・運動','創作','趣味','家事','家族','休息','新しい挑戦','その他']
PLACES = ['どこでも','自宅','外出先','職場']
ENERGY = ['低い','普通','高い']
def uid(): return uuid.uuid4().hex
def empty(): return {'activities':[], 'sessions':[], 'settings':{}}
def validate(d):
    assert isinstance(d,dict) and isinstance(d['settings'],dict)
    ids=set()
    for a in d['activities']:
        assert isinstance(a['id'],str) and a['id'] not in ids and isinstance(a['name'],str) and a['name'].strip()
        ids.add(a['id'])
        assert a['category'] in CATS and a['place'] in PLACES and a['energy'] in ENERGY
        assert type(a['minutes']) is int and 1<=a['minutes']<=1440 and 1<=a['priority']<=5
        for k in ['purpose','tools','memo']: assert isinstance(a[k],str)
        for k in ['favorite','repeat','done']: assert isinstance(a[k],bool)
    seen=set()
    for s in d['sessions']:
        assert s['id'] not in seen; seen.add(s['id'])
        assert s['activity_id'] in ids and s['category'] in CATS and isinstance(s['name'],str)
        date.fromisoformat(s['date']); assert 1<=s['minutes']<=10080 and 1<=s['satisfaction']<=5 and 0<=s['achievement']<=100
        assert isinstance(s['memo'],str)
    return d
def save(d):
    PATH.parent.mkdir(exist_ok=True)
    tmp=PATH.with_suffix('.tmp'); tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8'); tmp.replace(PATH)
try: d=validate(json.loads(PATH.read_text(encoding='utf-8'))) if PATH.exists() else empty()
except Exception as e: st.error(f'保存データを読み込めません。元ファイルを保護するため停止します: {e}'); st.stop()
A=d['activities']; S=d['sessions']; today=date.today().isoformat()
def commit(): save(d); st.rerun()
def choose(items,key):
    return st.selectbox('活動',items,format_func=lambda a:a['name'],key=key) if items else None
def fields(a=None):
    a=a or {}; name=st.text_input('やりたいこと',a.get('name','')); cat=st.selectbox('カテゴリー',CATS,index=CATS.index(a.get('category','学習'))); minutes=st.number_input('必要時間（分）',1,1440,a.get('minutes',15)); priority=st.slider('優先度',1,5,a.get('priority',3)); energy=st.selectbox('必要な体力',ENERGY,index=ENERGY.index(a.get('energy','普通'))); place=st.selectbox('場所',PLACES,index=PLACES.index(a.get('place','どこでも'))); purpose=st.text_area('目的',a.get('purpose','')); tools=st.text_input('必要なもの',a.get('tools','')); memo=st.text_area('メモ',a.get('memo','')); repeat=st.checkbox('繰り返し実行する',a.get('repeat',True)); favorite=st.checkbox('お気に入り',a.get('favorite',False)); done=st.checkbox('完了済み',a.get('done',False)); return dict(name=name.strip(),category=cat,minutes=minutes,priority=priority,energy=energy,place=place,purpose=purpose,tools=tools,memo=memo,repeat=repeat,favorite=favorite,done=done)
def record(a,minutes,sat,ach,memo,day):
    S.append(dict(id=uid(),activity_id=a['id'],name=a['name'],category=a['category'],date=day,minutes=minutes,satisfaction=sat,achievement=ach,memo=memo))
    if not a['repeat'] and ach==100: a['done']=True

def show(a):
    st.write(f"{a['category']} ｜ {a['minutes']}分 ｜ 優先度 {a['priority']} ｜ {a['energy']} ｜ {a['place']}")
    st.text(a['purpose']); st.text('必要なもの: '+a['tools']); st.text(a['memo'])

st.title('⏳ もしも、時間があったなら'); st.caption('Day323 — 小さな時間を、自分が納得できる時間に。')
tabs=st.tabs(['🏠 ホーム','📝 登録','🎯 今できること','📚 図鑑','⏱️ 実行・記録','📅 カレンダー','📊 分析','🛠️ 管理'])
with tabs[0]:
    cols=st.columns(3); cols[0].metric('登録活動',len(A)); cols[1].metric('今日の活動',sum(s['date']==today for s in S)); cols[2].metric('今日の時間',f"{sum(s['minutes'] for s in S if s['date']==today)}分")
    st.info('休息も大切な時間。何もしない選択も尊重しよう。')
    for s in S[::-1][:5]: st.write(f"{s['date']} ｜ {s['name']} ｜ {s['minutes']}分")
with tabs[1]:
    with st.form('new',clear_on_submit=True):
        a=fields(); submitted=st.form_submit_button('登録')
    if submitted:
        if not a['name']: st.error('名前を入力してください')
        else: A.append(dict(id=uid(),**a)); commit()
with tabs[2]:
    free=st.slider('空き時間（分）',1,720,30); en=st.radio('今の体力',ENERGY,index=1,horizontal=True); place=st.selectbox('現在の場所',PLACES,key='current_place'); cat=st.selectbox('カテゴリー',['すべて']+CATS,key='recommend_cat')
    matches=[a for a in A if not a['done'] and a['minutes']<=free and ENERGY.index(a['energy'])<=ENERGY.index(en) and (a['place']=='どこでも' or place==a['place']) and (cat=='すべて' or a['category']==cat)]
    for a in sorted(matches,key=lambda a:(-a['priority'],-int(a['favorite']),a['minutes'])):
        with st.expander(a['name']): show(a); st.caption(f"残り時間: {free-a['minutes']}分")
    if not matches: st.info('条件に合う活動はありません。休憩するのもいい選択です。')
with tabs[3]:
    q=st.text_input('検索'); cat=st.selectbox('分類',['すべて']+CATS,key='library_cat'); fav=st.checkbox('お気に入りのみ'); order=st.radio('並び順',['時間順','優先度順'],horizontal=True)
    for a in sorted(A,key=lambda a:a['minutes'] if order=='時間順' else -a['priority']):
        if (cat=='すべて' or cat==a['category']) and (not fav or a['favorite']) and q.casefold() in ' '.join([a['name'],a['purpose'],a['memo'],a['tools']]).casefold():
            with st.expander(('★ ' if a['favorite'] else '')+a['name']+('（完了）' if a['done'] else '')): show(a)
with tabs[4]:
    active=d['settings'].get('timer'); a=choose(A,'run_activity')
    if active and not any(x['id']==active['id'] for x in A): d['settings'].pop('timer'); commit()
    if active:
        a=next(x for x in A if x['id']==active['id']); elapsed=max(0,int((datetime.now()-datetime.fromisoformat(active['start'])).total_seconds())); st.write(f"実行中: {a['name']} ｜ 経過 {elapsed//60}分{elapsed%60}秒 ｜ 残り約 {max(0,a['minutes']*60-elapsed)//60}分")
        if st.button('時間表示を更新'): st.rerun()
        if st.button('タイマーを取り消す'): d['settings'].pop('timer'); commit()
    elif a and st.button('タイマー開始'): d['settings']['timer']={'id':a['id'],'start':datetime.now().isoformat()}; commit()
    if a:
        with st.form('session_'+a['id']):
            day=st.date_input('実施日',date.today()); mins=st.number_input('実際の時間（分）',1,10080,min(10080,max(1,round(elapsed/60))) if active else a['minutes']); sat=st.slider('満足度',1,5,3); ach=st.slider('達成度（%）',0,100,100); memo=st.text_area('感想'); ok=st.form_submit_button('活動を記録して終了')
        if ok: record(a,mins,sat,ach,memo,day.isoformat()); d['settings'].pop('timer',None); commit()
    else: st.info('先に活動を登録してください。')
    if S: st.dataframe(pd.DataFrame(S)[['date','name','minutes','satisfaction','achievement','memo']],hide_index=True)
with tabs[5]:
    y=st.number_input('年',1900,2100,date.today().year); m=st.number_input('月',1,12,date.today().month); totals={}
    for s in S: totals[s['date']]=totals.get(s['date'],0)+s['minutes']
    rows=[]
    for week in calendar.Calendar(firstweekday=6).monthdayscalendar(y,m):
        rows.append([f'{day}日 / {totals.get(date(y,m,day).isoformat(),0)}分' if day else '' for day in week])
    st.table(pd.DataFrame(rows,columns=list('日月火水木金土')))
    selected=st.date_input('詳細を見る日',date.today(),key='calendar_day')
    for s in S:
        if s['date']==selected.isoformat(): st.write(f"{s['name']}：{s['minutes']}分")
with tabs[6]:
    if S:
        df=pd.DataFrame(S); period=st.selectbox('期間',['全期間','今月','直近7日']); now=pd.Timestamp(date.today()); dates=pd.to_datetime(df.date)
        if period=='今月': df=df[dates.dt.to_period('M')==now.to_period('M')]
        elif period=='直近7日': df=df[(dates>=now-pd.Timedelta(days=6))&(dates<=now)]
        if not df.empty:
            c=st.columns(4); c[0].metric('合計時間',f'{df.minutes.sum()/60:.1f}時間'); c[1].metric('回数',len(df)); c[2].metric('平均時間',f'{df.minutes.mean():.1f}分'); c[3].metric('平均満足度',f'{df.satisfaction.mean():.1f}/5'); st.subheader('カテゴリー別時間（分）'); st.bar_chart(df.groupby('category').minutes.sum()); st.subheader('日別時間（分）'); st.line_chart(df.groupby('date').minutes.sum()); st.subheader('活動頻度・満足度'); st.dataframe(df.groupby('name').agg(回数=('id','count'),平均満足度=('satisfaction','mean')).sort_values('回数',ascending=False))
        else: st.info('対象期間の記録がありません。')
    else: st.info('活動を記録すると分析が表示されます。')
with tabs[7]:
    st.subheader('活動の編集・削除'); a=choose(A,'edit_activity')
    if a:
        with st.form('edit_'+a['id']):
            updated=fields(a); ok=st.form_submit_button('変更を保存')
        if ok:
            if updated['name']: a.update(updated); commit()
            else: st.error('名前を入力してください')
        confirm=st.checkbox('関連する活動履歴も削除することを確認')
        if st.button('活動を削除',disabled=not confirm):
            d['activities']=[x for x in A if x['id']!=a['id']]; d['sessions']=[s for s in S if s['activity_id']!=a['id']]
            if d['settings'].get('timer',{}).get('id')==a['id']: d['settings'].pop('timer')
            commit()
    st.subheader('履歴の編集・削除')
    if S:
        s=st.selectbox('履歴',S,format_func=lambda s:f"{s['date']} {s['name']} ({s['minutes']}分)")
        with st.form('edit_session_'+s['id']):
            day=st.date_input('日付',date.fromisoformat(s['date'])); mins=st.number_input('時間',1,10080,s['minutes']); sat=st.slider('満足度',1,5,s['satisfaction']); ach=st.slider('達成度',0,100,s['achievement']); memo=st.text_area('感想',s['memo']); ok=st.form_submit_button('履歴を保存')
        if ok: s.update(date=day.isoformat(),minutes=mins,satisfaction=sat,achievement=ach,memo=memo); commit()
        if st.button('選択した履歴を削除',disabled=not st.checkbox('履歴削除を確認')): S.remove(s); commit()
    st.subheader('バックアップ'); st.download_button('JSON保存',json.dumps(d,ensure_ascii=False,indent=2),'timepocket.json','application/json'); st.download_button('履歴CSV',pd.DataFrame(S).to_csv(index=False).encode('utf-8-sig'),'sessions.csv','text/csv'); f=st.file_uploader('JSON復元',type=['json']); confirm=st.checkbox('現在のデータを上書きする')
    if st.button('復元',disabled=not(f and confirm)):
        try:
            restored=validate(json.loads(f.getvalue())); restored['settings'].pop('timer',None); save(restored)
        except Exception as e: st.error(f'復元できません: {e}')
        else: st.rerun()
