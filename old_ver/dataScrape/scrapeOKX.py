import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
import pandas as pd
from util.sql_tools import insertAddrToDb
from util.tools import perform_get_request
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

    
def getAssets():
    instType = 'SPOT'
    print(f'- [OKX] downloading instrument list for {instType}')
    instruments = [ele['instId'] for ele in perform_get_request(f'https://www.okx.com/api/v5/public/instruments?instType={instType}')['data']]
    # print(instruments)
    assets = list(set([ele.split('-')[0] for ele in instruments]))
    print(f'- [OKX] instrument list: {assets}')
    return assets

def getPrice(candleSize, candleSizeTs, inst, cutoffTs):
    instId = inst+'-USDT'
    ts = int(time.time()*1000)
    result=[]
    while (ts > cutoffTs):
        
            url = f'https://www.okx.com/api/v5/market/history-mark-price-candles?instId={instId}&after={ts}&bar={candleSize}&limit=100'
            res = [{'asset': inst, 'ts': int(int(data[0])/1000), 'open': data[1], 'high': data[2], 'low': data[3], 'close': data[4]}for data in perform_get_request(url)['data']]
            result = result + res
            ts = ts - 100*candleSizeTs
            time.sleep(0.1)
        

    df = pd.DataFrame.from_records(result)

    # insert to db
    query = f'INSERT IGNORE INTO okx{candleSize}Spot (asset, ts, openPrice, highPrice, lowPrice, closePrice) VALUES (%s, %s, %s, %s, %s, %s)'
    dataInList = [(r['asset'], r['ts'], r['open'], r['high'], r['low'], r['close']) for i,r in df.iterrows()]
    insertAddrToDb(df, query, dataInList)

def allAssetGetPrice(candleSize, candleSizeTs, cutoffTs):
    # cutoffTs in ms
    assets = getAssets()
    retries = 0
    for i in assets:
        try:
            print(f'- [download OKX data] instrument: {i}, candle size: {candleSize}')
            getPrice(candleSize, candleSizeTs, i, cutoffTs)
        except Exception as e:
            print(f'- [download OKX data] instrument: {i}, problem caught as {e}')
            retries += 1
            time.sleep(3)



if __name__ == "__main__":
    allAssetGetPrice('15m', 900000, 1695081600000)