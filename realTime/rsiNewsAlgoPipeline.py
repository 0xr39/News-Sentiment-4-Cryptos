import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataScrape.scrapeOKX import allAssetGetPrice, getAssets

from realTime.newsComponent import newsFactor
from realTime.priceComponent import getUpdatedPriceCandle, priceToDB
from realTime.rsiComponent import rsiProcess

from util.tgBot import sendMsg

import time
import math
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

candleSize = '15m'
candleSizeTs = 900
startTime = (math.floor(time.time()/candleSizeTs)+1)*candleSizeTs
dbPriceLookBack = 5*86400

def getBound(df, row):
    timeNow = row.name
    filteredDf = df[(df.index >= timeNow-pd.Timedelta(hours=72)) & (df.index <= timeNow)]
    bound = (filteredDf['closePrice'].std()/row['closePrice'])*3
    bound = min(max(bound,0.001),0.05)
    return (1+bound)*row['closePrice'] , (1-bound)*row['closePrice']

# pre start
def preStartPriceFetch():
    global startTime
    while True:
        if time.time()>=startTime-300:
            print('[REAL TIME] Pre start price fetch start ... ')
            allAssetGetPrice(candleSize, candleSizeTs*1000, (time.time()-dbPriceLookBack)*1000)
            # startTime += candleSizeTs
            break
        else:
            time.sleep(1)

# main
if __name__ == "__main__":
    assets = getAssets()
    assets = [ele for ele in assets if not(ele in ['USDT','USDC','DAI'])]
    print(f'[REAL TIME] Assets to use: {assets}')
    preStartPriceFetch()
    
    # perpertual run
    newsSignal = {}
    rsiSignalDict = {}
    kanban = {}

    retries = 0

    while True:
        try:
            if time.time()>=startTime:
                print(f'[REAL TIME] Process News: {time.time()}')
                newsSignal = newsFactor(assets ,startTime-3600)

                print(f'[REAL TIME] Process Price: {time.time()}')
                priceDfDict = getUpdatedPriceCandle(assets, candleSize)
        
                rsiSignalDict = rsiProcess(priceDfDict)
                print(f'[REAL TIME] Signal Dict: {rsiSignalDict}')
                
                # check signal here
                for asset, newsSignal in newsSignal.items():
                    newsSum = newsSignal[0]
                    newsCount = newsSignal[1]
                    if newsCount >= 1 and rsiSignalDict[asset] >= 1 and asset not in kanban:
                        tp, sl = getBound(priceDfDict[asset], priceDfDict[asset].sort_index().iloc[-1])
                        print(f'Long Signal for {asset}, tp: {tp}, sl: {sl}')
                        sendMsg(f'<<{asset} 多倉 LONG>>  \n現時 time: {int(time.time())} \n止盈 tp: {tp} \n止損 sl: {sl}')
                        kanban[asset] = f'Long Signal for {asset}, tp: {tp}, sl: {sl}'
                        
                    elif newsCount <= -1 and rsiSignalDict[asset] <= -1 and asset not in kanban:
                        sl, tp = getBound(priceDfDict[asset], priceDfDict[asset].sort_index().iloc[-1])
                        print(f'Short Signal for {asset}, tp: {tp}, sl: {sl}')
                        sendMsg(f'<<{asset} 空倉 SHORT>>  \n現時 time: {int(time.time())} \n止盈 tp: {tp} \n止損 sl: {sl}')
                        kanban[asset] = f'Short Signal for {asset}, tp: {tp}, sl: {sl}'
                    
                # reset signal 
                newsSignal = {}
                rsiSignalDict = {}
                
                # to DB
                priceToDB(priceDfDict, candleSize)
                startTime += candleSizeTs
            
                print(f'[REAL TIME] Kanban: {kanban}')

                
            time.sleep(1)
        except Exception as e:
            print(f'[REAL TIME] Problem Caught: {e}')
            retries += 1
            time.sleep(1)
            if retries >= 3:
                print(f'[REAL TIME] retries: {retries}, aborting ... ')
                break





    

