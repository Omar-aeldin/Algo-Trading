import backtrader as bt
import pandas as pd
import quantstats as qs
import webbrowser
import backtrader.indicators 
import pathlib
import os

path =pathlib.PurePath( r'C:/Users/Omar/Desktop/Algo/Dataset/AAPL')
files = [os.path.join(path, file) for file in os.listdir(path)]
df = pd.concat(pd.read_csv(f,index_col='date', parse_dates=True) 
                for f in files if f.endswith('csv'))
df.to_csv('AAPL_10YR.csv')
