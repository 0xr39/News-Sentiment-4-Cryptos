import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.dataProcess import fetchNews, fetchPrice
from util.sql_tools import queryDB
from backtest import entryOnlyStopBound, getReturn
import pandas as pd
import numpy as np
import time
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

def calculateNews(df, row, delta):
    timeNow = row.name
    filteredDf = df[(df.index > timeNow-pd.Timedelta(minutes=delta)) & (df.index <= timeNow)]
    row['lookbackSum'] = filteredDf['sum'].sum()
    row['lookbackCount'] = filteredDf['count'].sum()
    return row

def groupedNews(newsDf, freq, timeDelta = 60):
    df = newsDf.copy()
    df = df.groupby('datetime')['LLMSentiment'].agg(['sum', 'count'])
    df = df.resample(freq).asfreq().fillna(0)
    df = df.apply(lambda row: calculateNews(df, row, timeDelta), axis=1)
    return df.drop(columns=['sum', 'count']).rename(columns={'lookbackSum': 'sum', 'lookbackCount': 'count'})
    
def getRSI(df, length):
    import pandas_ta as ta
    
    df = df.copy()
    rsi  = df.ta.rsi(length=length, scalar = 100)
    df['rsi'] = rsi
    return df

def calculateBound(df, row, covFactor):
    timeNow = row.name
    filteredDf = df[(df.index >= timeNow-pd.Timedelta(hours=72)) & (df.index <= timeNow)]
    bound = (filteredDf['closePrice'].std()/row['closePrice'])*covFactor
    bound = bound if not np.isnan(bound) else 0
    return min(max(bound,0.001),0.05)
#%%

def mainPlay(flip, lengthRsi, upperRsi, lowerRsi, newsTimeDelta, covFactor,
             durationDict= {'candleSize': '15m', 'candleSizeTs': 900, 'candleSizeDatetime': '15T'},
             afterCutoff = 1692057600, beforeCutoff = time.time(),
             size = 30000, posRatio = 1):
    assetList = queryDB('''select DISTINCT asset from cryptoPanic where asset not in ('USDT','USDC','DAI')''')
    # assetList = pd.DataFrame({'asset': ['BTC','ETH']})
    plDf = pd.DataFrame(columns=['pl','winRate','openTrade','closedTrade'],index=assetList['asset'])
    newsRecord = {}
    pfRecord = {}
    
    for asset in assetList['asset']:
        print(asset)
    
        df = fetchPrice(asset, afterCutoff, beforeCutoff, candleSize=durationDict['candleSize'])
        if (df.shape[0] == 0): continue
    
        dfTa = getRSI(df, lengthRsi)
        rsi = dfTa['rsi']
        rsiSignal = rsi.apply(lambda rsi: 1 if rsi >= upperRsi else (-1 if rsi <= lowerRsi else 0))
        
        news = fetchNews(asset, afterCutoff, beforeCutoff, candleSize=durationDict['candleSizeTs'])
        if (news.shape[0] == 0): continue
        newsScore = groupedNews(news, durationDict['candleSizeDatetime'], timeDelta=newsTimeDelta)
        overall = pd.DataFrame({'rsi': rsiSignal, 'sum': newsScore['sum'], 'count': newsScore['count']}).dropna(subset=['rsi'])
        overall['signal'] = overall.apply(lambda row: 1*flip if ((row['sum'] >= 1 ) and row['rsi'] >= 1) else (-1*flip if ((row['sum'] <= -1) and row['rsi'] <= -1) else 0),axis=1)
    
        # signal = rsiSignal
        signal = overall['signal']
        if (signal[signal != 0].shape[0] == 0): continue
    
        df['bound'] = df.apply(lambda row: calculateBound(df, row, covFactor), axis = 1)
        
        pf = entryOnlyStopBound(df['closePrice'], signal, 12, df['bound'], size, posRatio)
        pfRecord[asset] = pf
        pl, winRate, openTrade ,closedTrade = getReturn(pf)
        plDf.loc[asset] = [pl,winRate,openTrade,closedTrade]
        newsRecord[asset] = news

    plDf = plDf.dropna()
    return plDf, pfRecord, newsRecord

#%%

plDf, pfRecord, newsRecord = mainPlay(1, 30, 75 , 25, 60, 3)

#%%


print(' === Summary ===')
# print(plDf['pl'].sum()*100/size)
plDf['winPos'] = plDf.apply(lambda row: row['winRate']/100 * row['closedTrade'], axis = 1)
print(plDf['winPos'].sum() / plDf['closedTrade'].sum())
print(plDf['closedTrade'].sum())

entryTradesRecord = {k: i.entry_trades.records_readable for k, i in pfRecord.items()}

entryTradesDf = pd.concat([df.assign(asset=key) for key, df in entryTradesRecord.items()], ignore_index=True)

print(entryTradesDf['Return'].sum())