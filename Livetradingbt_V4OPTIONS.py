import backtrader as bt
import random as r
import pandas as pd
import os
from ib_insync import *
import datetime
import numpy as np
import time
import math as m
clientid = r.randint(1,30)


def myround(x, base=5):
    return base * round(x/base)

def strikeC(symbol,stock_price):
    df=pd.read_csv('stock-iv-rank-and-iv-percentile-03-14-2022.csv')
    df['IV'] = df['Imp Vol'].str.strip('%').astype(float)    
    row = df.loc[df['Symbol'].str.contains(symbol, case=False)]
    iv=row['IV'].values[0]
    sd=(stock_price*iv/100)*(m.sqrt(31/365))
    strike_priceC=round(myround((stock_price+(0.3*sd))))
    return strike_priceC


def strikeP(symbol,stock_price):
    df=pd.read_csv('stock-iv-rank-and-iv-percentile-03-14-2022.csv')
    df['IV'] = df['Imp Vol'].str.strip('%').astype(float)    
    row = df.loc[df['Symbol'].str.contains(symbol, case=False)]
    iv=row['IV'].values[0]
    sd=(stock_price*iv/100)*(m.sqrt(31/365))
    strike_priceP=round(myround((stock_price-(0.3*sd))))
    return strike_priceP
    
    
def option_straddle(symbol, stock_price):
    
    action = 'SELL'
    #Obtain strike date
    strike_date = 20220414
    strike_priceC = strikeC(symbol,stock_price)
    strike_priceP = strikeP(symbol,stock_price)

    
    call = Option(symbol, strike_date, strike_priceC, 'C', 'SMART')
    ib.qualifyContracts(call)
    
    put = Option(symbol, strike_date, strike_priceP, 'P', 'SMART')
    ib.qualifyContracts(put)
    #Create a straddle contract
    contract = Contract()
    contract.symbol = put.symbol
    contract.secType = "BAG"
    contract.currency = put.currency
    contract.exchange = put.exchange
    
    leg1 = ComboLeg()
    leg1.conId = call.conId 
    leg1.ratio = 1
    leg1.action = action
    leg1.exchange = put.exchange
    
    leg2 = ComboLeg()
    leg2.conId = put.conId
    leg2.ratio = 1
    leg2.action = action
    leg2.exchange = call.exchange
    
    contract.comboLegs = []
    contract.comboLegs.append(leg1)
    contract.comboLegs.append(leg2)
    
    #Obtain straddle price
    bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='60 s',
            barSizeSetting='10 secs',
            whatToShow='MIDPOINT',
            useRTH=True,
            formatDate=1)
       
    df = util.df(bars)   
    avg = round(np.nanmean(df.close),2) 
    order = LimitOrder('BUY', 1, round(avg*0.995,2), tif="DAY", account = '<account number>') ##algos only DAY         
    trade = ib.placeOrder(contract, order)     
    time.sleep(5)
    return trade



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
                    # self.inds[d]['ap'] = (d.close+d.high+d.low)/3
                    # self.inds[d]['esa'] = bt.indicators.EMA( self.inds[d]['ap'], period=self.p.EMAperiod)
                    # self.inds[d]['d'] = bt.indicators.EMA(abs( self.inds[d]['ap']-self.inds[d]['esa']), period=self.p.EMAperiod)
                    # self.inds[d]['ci'] = ( self.inds[d]['ap']-self.inds[d]['esa'])/(0.015* self.inds[d]['d'])
                    # self.inds[d]['wt1'] = bt.indicators.EMA( self.inds[d]['ci'],period=21)
                    # self.inds[d]['wt2'] = bt.indicators.SMA( self.inds[d]['wt1'],period=self.p.fastSMA)
                    # self.inds[d]['wt_cross'] = bt.ind.CrossOver(self.inds[d]['wt1'],self.inds[d]['wt2'])
            
    def notify_data(self, data, status):
        print('Data Status =>', data._getstatusname(status), data._name)
        if status == data.LIVE:
            self.data_ready = True
            


    def next(self):
        for i, d in enumerate(self.datas):
             dt, dn = self.datetime.datetime(), d._name
             print('{} {} Open:{}, High:{}, Low:{}, Close:{}'.format(dt, dn, d.open[0], d.high[0], d.low[0], d.close[0]))
             
        def sigLong():
            if  self.inds[d]['wt1']<=self.p.os:
                if self.inds[d]['wt_cross']>0:
                    return True
        def sigShort():
                 if  self.inds[d]['wt1']>=self.p.ob:
                     if self.inds[d]['wt_cross']<0:
                         return True
        def sqz():
            if self.inds[d]['sqz'][-3] < 0 or self.inds[d]['sqz'][-2] < 0 or self.inds[d]['sqz'][-1] < 0 or self.inds[d]['sqz'][-4] < 0 or self.inds[d]['sqz'][-5] < 0 or self.inds[d]['sqz'][-6] < 0 or self.inds[d]['sqz'][-7]<0 or self.inds[d]['sqz'][-3] > 0 or self.inds[d]['sqz'][-2] > 0 or self.inds[d]['sqz'][-1] > 0 or self.inds[d]['sqz'][-4] > 0 or self.inds[d]['sqz'][-5] > 0 or self.inds[d]['sqz'][-6] > 0 or self.inds[d]['sqz'][-7]>0 or self.inds[d]['sqz'][-8]>0:
                    return True
                
        for i, d in enumerate(self.datas):
             dt, dn = self.datetime.datetime(), d._name
             pos = sum([v.position for v in ib.positions() if v.contract.symbol == d._name])
             opentrade = [v for v in ib.openTrades() if v.contract.symbol == d._name]
             # opentrade = [v.orderStatus.status  for v in ib.openTrades() if v.contract.symbol == d._name]
             if not self.data_ready:
                 return        
             if len(opentrade) > 0:
                 return
             if pos==0:  # no market / no orders
                if sqz() is True:
                    # if sigShort() is True or sigLong() is True:                     
                    self.order[d._name] = option_straddle(d._name,round(d.close[0]))



             # else:
             #     if sigsell() is True:
             #          self.order[d._name] = option_straddle_sell(d._name,2,round(d.close[0]))
             #          # while not self.order[d._name].isDone():
             #          #     ib.waitOnUpdate()

if __name__ == '__main__':
    # Connections
    print("Intializing Live Trading")
    util.startLoop()
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=clientid+1)
    cerebro = bt.Cerebro()
    clientid = r.randint(1,30)
    store = bt.stores.IBStore(port=7497, clientId=clientid,reconnect=-1)
    
    # allstk=['TSLA']

    allstk = ['RBLX', 'AKBA', 'PARA', 'OXY', 'AAL', 'BA', 'AFRM', 'MULN', 'FCX', 
              'SE', 'AA', 'XPEV', 'T', 'IQ', 'CVX', 'PFE', 'DKNG', 'PYPL', 'TSLA', 
              'JD', 'DIDI', 'AMD', 'GOLD', 'DVN', 'MOS', 'BAC', 'PLTR', 'AAPL', 'BIDU', 'BABA']

    datalist=tuple(zip(allstk, allstk))


    for i in range(len(datalist)):
        data = store.getdata(dataname=datalist[i][0], sectype='STK', exchange='SMART', currency='USD', timeframe=bt.TimeFrame.Minutes)
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)
    
    cerebro.broker = store.getbroker()
    cerebro.addstrategy(MOMSQZ)
    cerebro.run()