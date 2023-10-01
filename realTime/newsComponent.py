import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.tools import perform_get_request, convert_to_utc
from dataScrape.prompt import promptPaLM
from util.sql_tools import insertAddrToDb, queryDB

import re
import pandas as pd

def getUpdatedNewsCryptoPanic(assets):
    try:
        newsResult = perform_get_request(f'http://cryptopanic.com/api/v1/posts/?auth_token=55addd2e6882542290f25fce31a683a16d097b8d&kind=news&regions=en&page=1')['results']
        result = [([{'id': news['id'], 'title': news['title'], 'time': convert_to_utc(news['created_at'], "%Y-%m-%dT%H:%M:%SZ") if len(news['created_at'])<=20 else convert_to_utc(news['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), 'asset': currency['code']} for currency in news['currencies']]) for news in newsResult if 'currencies' in news.keys()]
        result = [element for sublist in result for element in sublist]
        result = [ele for ele in result if ele['asset'] in assets]
        return pd.DataFrame.from_records(result)
    except Exception as e:
        print(f'[WARNING] caught error when downloading news: {e}')
        return pd.DataFrame()

def newsDfToLLM(df, existLLM ,cutoffTs):
    def getExistLLMValue(asset, id):
        values = existLLM[(existLLM['asset'] == asset) & (existLLM['id'] == id)]['LLM'].values
        if len(values) > 0:
            return values[0]
        else:
            return None
        
    df = df.copy()
    if df.shape[0] > 0:
        df = df[df['time'] >= cutoffTs]
    if df.shape[0] > 0:
        df['LLM'] = df.apply(lambda row: getExistLLMValue(row['asset'], row['id']), axis =1)
        df['LLM'] = df.apply(lambda row: promptPaLM(row['asset'], row['title']) if row['LLM'] == None else row['LLM'], axis =1)
    return df

def newsToSignal(newsDf): # return dict of newsSignal in 1,0,-1
    if newsDf.shape[0] > 0:
        df = newsDf.copy()
        df['LLM'] = df['LLM'].apply(lambda text: re.sub(r'[^\w\s]', ' ', text).replace('\n', ' ')) #replace all symbol and linebreak with space
        df['LLMSentiment'] = df['LLM'].apply(lambda text: 1 if text.split(' ')[0] == 'YES' else (-1 if text.split(' ')[0] == 'NO' else 0) )
        sentiment = df.groupby('asset')['LLMSentiment'].agg(['sum','count'])
        return {i: [r['sum'],r['count']] for i,r in sentiment.iterrows()}
    else:
        return {}
    
def processedNewsToDB(newsDf):
    dev_null = open('/dev/null', 'w')
    sys.stdout = dev_null

    query = 'INSERT IGNORE INTO cryptoPanic (id, asset, ts, title, palmOutputV1) VALUES (%s, %s, %s, %s, %s)'
    dataInList = [(r['id'], r['asset'], r['time'], r['title'], r['LLM']) for i,r in newsDf.iterrows()]
    insertAddrToDb(newsDf, query, dataInList)
    
    sys.stdout = sys.__stdout__
    dev_null.close()

def fetchNewsRaw(cutoffTs, model = 'palmOutputV1'):
    sql = f'''select id, asset, {model} as LLM from cryptoPanic where ts>={cutoffTs} and {model} is not null '''
    df = queryDB(sql)
    return df

def newsFactor(assets, cutoffTs): 
    newsDf = getUpdatedNewsCryptoPanic(assets)
    print(f'[NEWS FACTOR] Recent News: {newsDf}')
    existLLM = fetchNewsRaw(cutoffTs)
    LLMNewsDf = newsDfToLLM(newsDf, existLLM,cutoffTs)
    newsSignal = newsToSignal(LLMNewsDf)
    print(f'[NEWS FACTOR] News Signal: {newsSignal}')
    processedNewsToDB(LLMNewsDf)

    return newsSignal

