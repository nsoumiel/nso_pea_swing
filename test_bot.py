import os, sqlite3
from unittest.mock import patch
import io
import unittest,datetime as dt,tempfile,pathlib,json
from bot import fee,affordable,target,backtest,load,scan,ZoneInfo

def rows(n=240):
    return [{'date':(dt.date(2020,1,1)+dt.timedelta(days=i)).isoformat(),'open':100.,'high':101.,'low':99.,'close':100.} for i in range(n)]
class Tests(unittest.TestCase):
    def test_costs(self):
        self.assertAlmostEqual(fee(100),.5);self.assertEqual(fee(1000),1.9);self.assertAlmostEqual(fee(5000),4.5)
    def test_cash(self):
        self.assertEqual(affordable(5000,500),9)
        self.assertEqual(affordable(100,101),0)
    def test_lookahead_guard(self):
        r=rows();self.assertRaises(ValueError,target,r,r[-1]['date'],'monthly10')
    def test_month_signal_frozen(self):
        r=rows(420)
        for i,x in enumerate(r):x['close']=100+i
        day='2021-02-15';h=[x for x in r if x['date']<day]
        before=target(h,day,'monthly10')
        for x in h:
            if x['date'].startswith('2021-02'):x['close']=.01
        self.assertEqual(before,target(h,day,'monthly10'))
    def test_next_open_and_no_borrow(self):
        r=rows(2);r[0]['open']=200;r[0]['high']=201;r[0]['close']=200
        s,c,t,m=backtest(r,r[0]['date'],r[-1]['date'],'buy_hold')
        self.assertAlmostEqual(t[0]['price'],200.2);self.assertEqual(t[0]['qty'],24)
        self.assertTrue(all(x['cash']>=0 for x in c))
    def test_future_does_not_change_history(self):
        r=rows(500)
        for i,x in enumerate(r):x['close']=100+i/10;x['open']=x['close']
        end=r[390]['date'];a=backtest(r,r[300]['date'],end,'monthly10')
        for x in r[391:]:x['close']=1e6;x['open']=1e6
        b=backtest(r,r[300]['date'],end,'monthly10')
        self.assertEqual(a,b)
    def test_flat_market_loses_only_costs(self):
        r=rows(20);s,c,t,m=backtest(r,r[0]['date'],r[-1]['date'],'buy_hold')
        self.assertLess(s['final'],5000);self.assertEqual(len(t),1)
        self.assertAlmostEqual(c[0]['equity'],c[-1]['equity'])
    def test_corporate_actions_block(self):
        with tempfile.TemporaryDirectory() as p:
            f=pathlib.Path(p)/'bad.json';f.write_text(json.dumps({'chart':{'result':[{'meta':{'dataGranularity':'1d','currency':'EUR'},'events':{'splits':{'x':2}}}]}}))
            self.assertRaises(ValueError,load,f)
    def test_stale_blocks(self):
        with tempfile.TemporaryDirectory() as p, patch('bot.load',return_value=rows(420)):
            self.assertRaises(ValueError,scan,p,str(pathlib.Path(p)/'state.db'),'monthly10',False,dt.datetime(2026,1,1,tzinfo=ZoneInfo('Europe/Paris')))
    def test_telegram_dedup_and_dry_run(self):
        history=rows(420);now=dt.datetime(2021,2,24,tzinfo=ZoneInfo('Europe/Paris'))
        with tempfile.TemporaryDirectory() as p, patch('bot.load',return_value=history), patch.dict(os.environ,{'PEA_TELEGRAM_BOT_TOKEN':'test','PEA_TELEGRAM_CHAT_ID':'test'}), patch('bot.urllib.request.urlopen',return_value=io.BytesIO(b'{"ok":true}')) as send:
            state=str(pathlib.Path(p)/'state.db')
            scan(p,state,'monthly10',False,now)
            self.assertEqual(send.call_count,0)
            scan(p,state,'monthly10',True,now)
            scan(p,state,'monthly10',True,now)
            self.assertEqual(send.call_count,1)
    def test_failed_notification_not_recorded(self):
        with tempfile.TemporaryDirectory() as p, patch('bot.load',return_value=rows(420)), patch.dict(os.environ,{'PEA_TELEGRAM_BOT_TOKEN':'test','PEA_TELEGRAM_CHAT_ID':'test'}), patch('bot.urllib.request.urlopen',side_effect=OSError()):
            state=str(pathlib.Path(p)/'state.db')
            self.assertRaises(RuntimeError,scan,p,state,'monthly10',True,dt.datetime(2021,2,24,tzinfo=ZoneInfo('Europe/Paris')))
            with sqlite3.connect(state) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM notifications').fetchone()[0],0)
if __name__=='__main__':unittest.main()

