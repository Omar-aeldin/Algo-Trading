import backtrader as bt
import random as r
import pandas as pd
import os


class MOMSQZ(bt.Strategy):
    params = (
        ('SMAperiod',20),('EMAperiod',10),('stop_percentage',0.08),('ob',0),('os',0),
        ('ATR',1.5), ('fastSMA',4),)  

             
    def __init__(self):
        print("RUNNING STRATEGY")
        self.data_ready = False
        self.data
        self.order = {}
        for i, d in enumerate(self.datas):
            self.order[d._name] = None
        for i, d in enumerate(self.datas):
            self.inds = dict()
            for i, d in enumerate(self.datas):
                    self.inds[d] = dict()
                    self.inds[d]['bband'] = bt.indicators.BBands(d.close, period=self.p.SMAperiod)
                    self.inds[d]['SMA'] = bt.talib.SMA(d.close, timeperiod=self.p.SMAperiod)
                    self.inds[d]['ATR'] = bt.talib.ATR(d.high, d.low, d.close, timeperiod=self.p.SMAperiod)
                    self.inds[d]['kcupper'] = self.inds[d]['SMA']+self.inds[d]['ATR']*self.p.ATR
                    self.inds[d]['kclower'] = self.inds[d]['SMA']-self.inds[d]['ATR']*self.p.ATR
                    self.inds[d]['sqz'] = bt.ind.CrossOver(self.inds[d]['bband'].top, self.inds[d]['kcupper'])
                    self.inds[d]['ap'] = (d.close+d.high+d.low)/3
                    self.inds[d]['esa'] = bt.indicators.EMA( self.inds[d]['ap'], period=self.p.EMAperiod)
                    self.inds[d]['d'] = bt.indicators.EMA(abs( self.inds[d]['ap']-self.inds[d]['esa']), period=self.p.EMAperiod)
                    self.inds[d]['ci'] = ( self.inds[d]['ap']-self.inds[d]['esa'])/(0.015* self.inds[d]['d'])
                    self.inds[d]['wt1'] = bt.indicators.EMA( self.inds[d]['ci'],period=21)
                    self.inds[d]['wt2'] = bt.indicators.SMA( self.inds[d]['wt1'],period=self.p.fastSMA)
                    self.inds[d]['wt_cross'] = bt.ind.CrossOver(self.inds[d]['wt1'],self.inds[d]['wt2'])
            
    def notify_data(self, data, status):
        print('Data Status =>', data._getstatusname(status), data._name)
        if status == data.LIVE:
            self.data_ready = True
            
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        if order.status in [order.Completed, order.Cancelled]:
            self.order[order.data._name] = None
          
            
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        print('{} OPERATION PROFIT GROSS {}, NET {}'.
                format(self.datetime.datetime(),round(trade.pnl,2), round(trade.pnlcomm,2)))

    def next(self):
        for i, d in enumerate(self.datas):
             dt, dn = self.datetime.datetime(), d._name
             print('{} {} Open:{}, High:{}, Low:{}, Close:{}'.format(dt, dn, d.open[0], d.high[0], d.low[0], d.close[0]))
             
        def sigbuy():
            if  self.inds[d]['wt1']<=self.p.os:
                if self.inds[d]['wt_cross']>0:
                    return True
        def sigsell():
                 if  self.inds[d]['wt1']>=self.p.ob:
                     if self.inds[d]['wt_cross']<0:
                         return True
        def sqz():
            if self.inds[d]['sqz'][-3] < 0 or self.inds[d]['sqz'][-2] < 0 or self.inds[d]['sqz'][-1] < 0 or self.inds[d]['sqz'][-4] < 0 or self.inds[d]['sqz'][-5] < 0 or self.inds[d]['sqz'][-6] < 0 or self.inds[d]['sqz'][-7]<0 or self.inds[d]['sqz'][-3] > 0 or self.inds[d]['sqz'][-2] > 0 or self.inds[d]['sqz'][-1] > 0 or self.inds[d]['sqz'][-4] > 0 or self.inds[d]['sqz'][-5] > 0 or self.inds[d]['sqz'][-6] > 0 or self.inds[d]['sqz'][-7]>0 or self.inds[d]['sqz'][-8]>0:
                    return True
                
        for i, d in enumerate(self.datas):
             dt, dn = self.datetime.datetime(), d._name
             pos = self.getposition(d).size
             if not self.data_ready:
                 return        
             if self.order[d._name]:
                 return
             if not pos:  # no market / no orders
                if sqz() is True:
                    if sigbuy() is True:
                        self.order[d._name] = self.buy(data=d, size=50)
                        print('{} {} BUY CREATE:{}'.format(dt, dn, d.close[0]))




             else:
                if sigsell() is True:
                    self.order[d._name] = self.sell(data=d, size=50)
                    print('{} {} SELL CREATE:{}'.format(dt, dn, d.close[0],))









if __name__ == '__main__':
    print("Intializing Live Trading")
    cerebro = bt.Cerebro()
    clientid = r.randint(1,30)
    store = bt.stores.IBStore(port=7497, clientId=clientid,reconnect=-1)

    # datalist = [
    # ('USD.JPY', 'USDJPY'), #[0] = Data file, [1] = Data name
    # ('EUR.USD', 'EURUSD'),]
    # path=r'C:/Users/Omar/OneDrive/Desktop/Algo/nasdaq_screener_1646237213704.csv'
    # df=pd.read_csv(path)
    # datalist=list(zip(df.Symbol, df.Symbol))
    
    
    allstk=os.listdir(r'C:\Users\Omar\OneDrive\Desktop\Algo\Dataset')
    # datalist =[('AAPL','AAPL'), 
    #             ('AMD','AMD'),]
    # allstk=['MMM', 'AOS', 'ABT', 'ABBV', 'ABMD', 'ACN', 'ATVI', 'ADM', 'ADBE', 'AAP', 'AMD', 'AES', 'AFL', 'A',
    #             'APD', 'AKAM', 'ALK', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN',
    #             'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'ADI', 'ANSS', 'ANTM',
    #             'AON', 'APA', 'AAPL', 'AMAT', 'APTV', 'ANET', 'AJG', 'AIZ']

    datalist=tuple(zip(allstk, allstk))

    
    # datalist=[('ABM', 'ABM'), ('AL', 'AL'), ('AMN', 'AMN'), ('AMRC', 'AMRC'), ('AORT', 'AORT'),
    # ('ARCH', 'ARCH'), ('ASGN', 'ASGN'), ('ASH', 'ASH'), ('ASIX', 'ASIX'), ('ATI', 'ATI'), 
    # ('AVD', 'AVD'), ('AVLR', 'AVLR'), ('AVNT', 'AVNT'), ('AXTA', 'AXTA'), ('AYX', 'AYX'), 
    # ('BHE', 'BHE'), ('BHVN', 'BHVN'), ('BOC', 'BOC'), ('BOX', 'BOX'), ('BSM', 'BSM'), 
    # ('BTU', 'BTU'), ('BW', 'BW'), ('CACI', 'CACI'), ('CALX', 'CALX'), ('CBT', 'CBT'),
    # ('CEQP', 'CEQP'), ('CHE', 'CHE'), ('CIVI', 'CIVI'), ('CMC', 'CMC'), ('CNMD', 'CNMD'), 
    # ('DAVA', 'DAVA'), ('DBD', 'DBD'), ('DLB', 'DLB'), ('DLX', 'DLX'), ('DNA', 'DNA'), ('DOCN', 'DOCN'),
    # ('DY', 'DY'), ('CPB', 'CPB'), ('ECVT', 'ECVT'), ('EGY', 'EGY'), ('EHC', 'EHC'), ('EQT', 'EQT'), 
    # ('ESI', 'ESI'), ('ESTC', 'ESTC'), ('EVH', 'EVH'), ('FOUR', 'FOUR'), ('FSS', 'FSS'), ('FTAI', 'FTAI'), 
    # ('GLT', 'GLT'), ('GMED', 'GMED'), ('GPK', 'GPK'), ('GTLS', 'GTLS'), ('HAE', 'HAE'), ('HL', 'HL'), 
    # ('HNGR', 'HNGR'), ('HUN', 'HUN'), ('INSP', 'INSP'), ('ITGR', 'ITGR'), ('JBL', 'JBL'), ('KAI', 'KAI'), 
    # ('KFY', 'KFY'), ('KLR', 'KLR'), ('KOP', 'KOP'), ('KRO', 'KRO'), ('SPY', 'SPY'), ('SNAP', 'SNAP'), 
    # ('GPS', 'GPS'), ('LEVI', 'LEVI'), ('MGY', 'MGY'), ('MIR', 'MIR'), ('MKFG', 'MKFG'),]


    
    for i in range(len(datalist)):
        data = store.getdata(dataname=datalist[i][0], sectype='STK', exchange='NYSE', currency='USD', timeframe=bt.TimeFrame.Minutes)
        # data = store.getdata(dataname=datalist[i][0], sectype='CASH', exchange='IDEALPRO')
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5)
        # cerebro.adddata(data)
    
    cerebro.broker = store.getbroker()
    cerebro.addstrategy(MOMSQZ)
    cerebro.run()
