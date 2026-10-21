"""PEA Swing v1: recherche et alertes, jamais d'ordres courtier. Python >=3.11."""
import argparse, csv, datetime as dt, hashlib, json, math, os, pathlib, sqlite3, time, urllib.request
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parent
SYMBOL='CW8.PA'
ISIN='LU1681043599'

def fee(value):
    if value<=0:return 0.
    f=.99 if value<=500 else 1.90 if value<=1000 else 2.90 if value<=2000 else 3.80 if value<=4400 else value*.0009
    return min(f,value*.005)

def load(path):
    r=json.loads(pathlib.Path(path).read_text())['chart']['result'][0]
    if r['meta'].get('dataGranularity')!='1d':raise ValueError('Des bougies quotidiennes sont requises')
    if r['meta'].get('currency')!='EUR':raise ValueError('Devise inattendue')
    if r.get('events'):raise ValueError('Opération sur titres détectée: audit manuel requis avant utilisation')
    q=r['indicators']['quote'][0];rows=[]
    for i,t in enumerate(r['timestamp']):
        row={'date':dt.datetime.fromtimestamp(t,dt.timezone.utc).astimezone(ZoneInfo('Europe/Paris')).date().isoformat()}
        for k in ['open','high','low','close']:row[k]=q[k][i]
        if any(row[k] is None for k in ['open','high','low','close']):continue
        if not all(math.isfinite(row[k]) and row[k]>0 for k in ['open','high','low','close']):raise ValueError('Prix invalide')
        if row['low']>min(row['open'],row['close'])+.02 or row['high']<max(row['open'],row['close'])-.02:raise ValueError('OHLC incohérents')
        rows.append(row)
    if len({x['date'] for x in rows})!=len(rows):raise ValueError('Dates dupliquées')
    if rows!=sorted(rows,key=lambda x:x['date']):raise ValueError('Dates non ordonnées')
    return rows

def download(folder):
    folder=pathlib.Path(folder);folder.mkdir(parents=True,exist_ok=True)
    end=int(dt.datetime.now(dt.timezone.utc).timestamp())
    url=f'https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?period1=1230768000&period2={end}&interval=1d&events=div,splits'
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(request,timeout=40) as response:raw=response.read()
    tmp=folder/'download.tmp';tmp.write_bytes(raw);load(tmp)
    tmp.replace(folder/f'{SYMBOL}.json')
    (folder/'download.json').write_text(json.dumps({'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'url':url,'sha256':hashlib.sha256(raw).hexdigest()},indent=2))

def target(history,asof,strategy):
    """Target for an opening on asof; history must strictly precede asof."""
    if any(x['date']>=asof for x in history):raise ValueError('Fuite temporelle')
    if strategy=='buy_hold':return True
    if strategy=='monthly10':
        month=asof[:7];last={}
        for r in history:
            if r['date'][:7]<month:last[r['date'][:7]]=r['close']
        closes=list(last.values())
        return len(closes)>=10 and closes[-1]>sum(closes[-10:])/10
    if strategy=='weekly200':
        # All closes through prior completed ISO week; same decision throughout current week.
        week=dt.date.fromisoformat(asof).isocalendar()[:2]
        closes=[r['close'] for r in history if dt.date.fromisoformat(r['date']).isocalendar()[:2]<week]
        return len(closes)>=200 and closes[-1]>sum(closes[-200:])/200
    raise ValueError(strategy)

def affordable(cash,price):
    n=int(cash/price)
    while n and n*price+fee(n*price)>cash:n-=1
    return n

def backtest(rows,start,end,strategy,capital=5000,slippage=.001):
    cash=capital;qty=0;curve=[];trades=[];history=[];previous=None
    for r in rows:
        day=r['date']
        if start<=day<=end:
            want=target(history,day,strategy)
            if want and not qty:
                p=r['open']*(1+slippage);n=affordable(cash,p)
                if n:
                    f=fee(n*p);cash-=n*p+f;qty=n;trades.append({'date':day,'side':'BUY','qty':n,'price':p,'fee':f,'signal_latest':history[-1]['date'] if history else ''})
            elif not want and qty:
                p=r['open']*(1-slippage);f=fee(qty*p);cash+=qty*p-f
                trades.append({'date':day,'side':'SELL','qty':qty,'price':p,'fee':f,'signal_latest':history[-1]['date']});qty=0
            # Net liquidation valuation, including hypothetical exit costs; no forced final sell.
            marked=qty*r['close']*(1-slippage)
            equity=cash+marked-fee(marked)
            curve.append({'date':day,'equity':equity,'cash':cash,'qty':qty,'target':int(want)})
        history.append(r)
    if not curve:raise ValueError('Période vide')
    peak=capital;dd=0
    for r in curve:peak=max(peak,r['equity']);dd=min(dd,r['equity']/peak-1)
    years=(dt.date.fromisoformat(curve[-1]['date'])-dt.date.fromisoformat(curve[0]['date'])).days/365.25
    months={}
    for r in curve:months[r['date'][:7]]=r['equity']
    monthly=[];prev=capital
    for month,e in months.items():monthly.append({'month':month,'return':e/prev-1,'pnl_eur':e-prev});prev=e
    stats={'strategy':strategy,'start':curve[0]['date'],'end':curve[-1]['date'],'capital':capital,'final':curve[-1]['equity'],'return':curve[-1]['equity']/capital-1,'cagr':(curve[-1]['equity']/capital)**(1/years)-1,'max_drawdown':dd,'orders':len(trades),'fees':sum(t['fee'] for t in trades),'exposure':sum(r['qty']>0 for r in curve)/len(curve),'negative_months':sum(r['return']<0 for r in monthly),'months':len(monthly)}
    return stats,curve,trades,monthly

def write_csv(path,rows):
    if not rows:return
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def research(folder,out):
    rows=load(pathlib.Path(folder)/f'{SYMBOL}.json');out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    stats=[]
    for label,start,end in [('full','2011-01-01','2026-10-20'),('development','2011-01-01','2019-12-31'),('validation','2020-01-01','2026-10-20')]:
        for strategy in ['monthly10','weekly200','buy_hold']:
            s,c,t,m=backtest(rows,start,end,strategy);s['period']=label;stats.append(s)
            stem=out/f'{label}_{strategy}'
            write_csv(str(stem)+'_equity.csv',c);write_csv(str(stem)+'_orders.csv',t);write_csv(str(stem)+'_months.csv',m)
    for strategy in ['monthly10','weekly200','buy_hold']:
        s,*_=backtest(rows,'2020-01-01','2026-10-20',strategy,slippage=.003);s['period']='validation_stress_30bps';stats.append(s)
    write_csv(out/'summary.csv',stats);(out/'summary.json').write_text(json.dumps(stats,indent=2))
    print(json.dumps(stats,indent=2))

def scan(folder,state,strategy,notify=False,now=None):
    now=now or dt.datetime.now(ZoneInfo('Europe/Paris'))
    # Conservative: yesterday at latest, including when run during an open session.
    rows=[r for r in load(pathlib.Path(folder)/f'{SYMBOL}.json') if r['date']<now.date().isoformat()]
    if not rows or (now.date()-dt.date.fromisoformat(rows[-1]['date'])).days>4:raise ValueError('Cours trop anciens: aucune alerte autorisée')
    want=target(rows,now.date().isoformat(),strategy)
    # No assumed holdings: this is a model regime, not an order or quantity.
    text=f'PEA Swing | {strategy} | {SYMBOL} {ISIN}\nRégime cible: {"INVESTI" if want else "LIQUIDITÉS"}\nCours contrôlé: {rows[-1]["date"]}, {rows[-1]["close"]:.2f} EUR\nSignal informatif. Vérifier vos positions et le prix chez Bourse Direct; exécution manuelle uniquement.'
    pathlib.Path(state).parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(state,timeout=30) as db:
        db.execute('CREATE TABLE IF NOT EXISTS notifications (strategy TEXT PRIMARY KEY, regime INTEGER, sent_at TEXT)')
        db.execute('BEGIN IMMEDIATE')
        old=db.execute('SELECT regime FROM notifications WHERE strategy=?',(strategy,)).fetchone()
        changed=old is None or old[0]!=int(want)
        if notify and changed:
            token=os.environ.get('PEA_TELEGRAM_BOT_TOKEN');chat=os.environ.get('PEA_TELEGRAM_CHAT_ID')
            if not token or not chat:raise ValueError('Variables Telegram absentes')
            req=urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage',data=json.dumps({'chat_id':chat,'text':text}).encode(),headers={'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(req,timeout=20) as response:answer=json.load(response)
                if not answer.get('ok'):raise RuntimeError()
            except Exception:raise RuntimeError('Échec Telegram, vérifier la connexion et les identifiants') from None
            db.execute('INSERT OR REPLACE INTO notifications VALUES (?,?,?)',(strategy,int(want),now.isoformat()))
    print(text+'\nNotification: '+('envoyée' if notify and changed else 'non envoyée'),flush=True)
    return want

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['download','backtest','scan','run']);p.add_argument('--data',default=str(ROOT/'data'));p.add_argument('--out',default=str(ROOT/'results'));p.add_argument('--state',default=str(ROOT/'state/alerts.sqlite3'));p.add_argument('--strategy',choices=['monthly10','weekly200'],default='monthly10');p.add_argument('--telegram',action='store_true');a=p.parse_args()
    if a.command=='download':download(a.data)
    elif a.command=='backtest':research(a.data,a.out)
    elif a.command=='scan':scan(a.data,a.state,a.strategy,a.telegram)
    else:
        while True:
            try:
                download(a.data);scan(a.data,a.state,a.strategy,a.telegram)
            except Exception as e:print(f'ERREUR {type(e).__name__}: {e}',flush=True)
            time.sleep(21600)
if __name__=='__main__':main()
