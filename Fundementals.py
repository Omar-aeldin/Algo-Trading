import yfinance as yf
import pandas as pd


df=pd.read_csv('3monthearning.csv')
dfsymb=df['symbol']
stklist=dfsymb.values.tolist()
stk_mk=[]
counter=0


for s in stklist:
    try:
            stock = yf.Ticker(s)
            data=[stock.info['symbol'],stock.info['marketCap']]
            counter+=1
            print(data, counter, "/", len(stklist))
            stk_mk.append(data)
            symbol_s = [a_tuple[0] for a_tuple in stk_mk]
            marketcap_c = [a_tuple[1] for a_tuple in stk_mk]
            dictionary = {'symbol': symbol_s, 'marketCap': marketcap_c}
            df = pd.DataFrame(dictionary) 
            df.to_csv('symbolmarketcap.csv', mode='a', header=False)

    except KeyError:
            continue
        






