from ib_insync import *
import pandas as pd
import os
import datetime
import shutil
import random as r

# '2016', '2015', '2014', '2013', '2012'
# Parameters
Ticker = ['DELL', 'SQ', 'HPQ','LIT', 'SMH', 'UBER', 'ETSY', 'TWTR', 'ORCL', 'AMZN', 'DIS', 'DDOG', 'LULU', 'INTC', 'SBUX', 'MSFT', 'ENB', 'EBAY', 'DPZ', 'VALE']
Duration = '1 M'
BarSize = '1 MIN'
year =[ '2021','2020','2019','2018', '2017']
month =[ '01','02','03','04','05','06','07','08','09',
            '10','11','12']

remaining = len(year)*len(month)*len(Ticker)
time = remaining/2
hour ='0101 21:39:33 '
counter = 0
clientid = r.randint(1,30)

util.startLoop()
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=clientid)

for t in Ticker:
    # Make directories
    dirlist=['\\10Y\\', '\\5Y\\', '\\1Y\\']
    outdir = 'C:\\Users\\Omar\\OneDrive\\Desktop\\Algo\\Dataset\\'+t+'\\10Y\\'
    for l in dirlist:
        make_dir = 'C:\\Users\\Omar\\OneDrive\\Desktop\\Algo\\Dataset\\'+t+l
        if not os.path.exists(make_dir):
            os.makedirs(make_dir)
    for y in year:
        for m in month:
                stock = Stock(t, 'SMART', 'USD')
                endDate = y+m+hour
                bars = ib.reqHistoricalData(
                    stock, endDateTime=endDate, durationStr=Duration,
                    barSizeSetting=BarSize, whatToShow='MIDPOINT', useRTH=True)
                counter += 1
                time -=0.5
                  # convert to pandas dataframe
                df = util.df(bars)
                path = outdir+t+y+"_"+m+"_"+BarSize.replace(" ", "")+Duration.replace(" ", "")+'.csv'
                df.to_csv(path)
                print(df)
                print(counter,"/",remaining," downloaded!!")
                print(time/60, "/", (remaining/2)/60 ,"Hours", "remaining!!")
                
    year5 = [t+'2021', t+'2020', t+'2019', t+'2018', t+'2017', t+'2016'] 
    destination5 = 'C:\\Users\\Omar\\OneDrive\\Desktop\\Algo\\Dataset\\'+t+'\\5Y\\'
    destination1 = 'C:\\Users\\Omar\\OneDrive\\Desktop\\Algo\\Dataset\\'+t+'\\1Y\\'
    for n in year5:
        for file in os.listdir(outdir):
            if file.startswith(n):
                shutil.copy(outdir+"\\"+file, destination5)
    for file in os.listdir(outdir):
        if file.startswith(year5[0]):
            shutil.copy(outdir+"\\"+file, destination1)
            
ib.disconnect()
