import csv
import requests
import pandas as pd
import os
key="MXNBQO0DD61619NO"
symbols = 'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey=key'

df=pd.read_csv('3monthearning.csv')
dfsymb=df['symbol']
print(dfsymb.values.tolist())
print(dfsymb)



        