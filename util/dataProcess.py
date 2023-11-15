import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.sql_tools import queryDB
import pandas as pd

def fetchNews(asset, afterCutoffTs, beforeCutoffTs, candleSize=900, model='palmOutputV1'): #cutoffTs in s, candleSize in s
    import re
    sql = f'''select title, ts, asset, {model} as LLM, (FLOOR(ts/{candleSize})+1)*{candleSize} as candleTime from cryptoPanic where  ts>={afterCutoffTs} and ts<={beforeCutoffTs} and asset = '{asset}' and {model} is not null '''
    # sql = f'''select title, ts, asset, {model} as LLM, (FLOOR(ts/{candleSize})+1)*{candleSize} as candleTime from cryptoPanic where  ts>={afterCutoffTs} and ts<={beforeCutoffTs} and asset = '{asset}' and {model} is not null and (LOWER(title) LIKE '%breaking%' OR LOWER(title) LIKE '%just in%')'''
    df = queryDB(sql)
    df['datetime'] = pd.to_datetime(df['candleTime'], unit='s')
    df['LLM'] = df['LLM'].apply(lambda text: re.sub(r'[^\w\s]', ' ', text).replace('\n', ' ')) #replace all symbol and linebreak with space
    df['LLMSentiment'] = df['LLM'].apply(lambda text: 1 if text.split(' ')[0] == 'YES' else (-1 if text.split(' ')[0] == 'NO' else 0) )
    return df

def fetchPrice(asset, afterCutoffTs, beforeCutoffTs,candleSize='15m'): #cutoffTs in s
    sql = f'''SELECT ts, openPrice, highPrice, lowPrice, closePrice FROM okx{candleSize}Spot WHERE ts>={afterCutoffTs} and ts<={beforeCutoffTs} and asset = '{asset}' '''
    df = queryDB(sql)
    df['datetime'] = pd.to_datetime(df['ts'], unit='s')
    df = df.set_index(pd.DatetimeIndex(df["datetime"]))
    df = df.drop(columns=['datetime'])
    return df