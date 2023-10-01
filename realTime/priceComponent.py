import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd

from util.tools import perform_get_request
from util.dataProcess import fetchPrice

from util.sql_tools import insertAddrToDb

def getUpdatedPriceCandle(assets, candleSize, dbPriceLookBack=5*86400):
    dev_null = open('/dev/null', 'w')
    sys.stdout = dev_null

    result = {}

    for inst in assets:
        print(inst)
        instId = inst+'-USDT'
        url = f'https://www.okx.com/api/v5/market/history-mark-price-candles?instId={instId}&bar={candleSize}&limit=1'
        res = [{'ts': int(int(data[0])/1000), 'openPrice': float(data[1]), 'highPrice': float(data[2]), 'lowPrice': float(data[3]), 'closePrice': float(data[4])}for data in perform_get_request(url)['data']]
        if (len(res) == 0): continue
        res = pd.DataFrame(data = res)
        res['datetime'] = pd.to_datetime(res['ts'], unit='s')
        res = res.set_index(pd.DatetimeIndex(res["datetime"]))
        res = res.drop(columns=['datetime'])
        df = fetchPrice(inst, (time.time()-dbPriceLookBack), candleSize=candleSize)
        if (df.shape[0] == 0): continue
        df = pd.concat([df,res])
        result[inst] = df

    sys.stdout = sys.__stdout__
    dev_null.close()

    return result

def priceToDB(dfDict, candleSize):
    dev_null = open('/dev/null', 'w')
    sys.stdout = dev_null

    for asset, df in dfDict.items():
        query = f'INSERT IGNORE INTO okx{candleSize}Spot (asset, ts, openPrice, highPrice, lowPrice, closePrice) VALUES (%s, %s, %s, %s, %s, %s)'
        dataInList = [(asset, r['ts'], r['openPrice'], r['highPrice'], r['lowPrice'], r['closePrice']) for i,r in df.iterrows()]
        insertAddrToDb(df, query, dataInList)
    
    sys.stdout = sys.__stdout__
    dev_null.close()