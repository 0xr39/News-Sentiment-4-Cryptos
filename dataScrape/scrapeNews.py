import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from util.sql_tools import insertAddrToDb
from util.tools import perform_get_request, convert_to_utc
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

def getNewsCryptoPanic(assets, maxPage):
    import time
    for asset in assets:
        print(f'- [CRYPTO PANIC] downloading news for {asset}')
        result = []
        for i in range(1, maxPage+1):
            try:
                newsResult = perform_get_request(f'http://cryptopanic.com/api/v1/posts/?auth_token=55addd2e6882542290f25fce31a683a16d097b8d&currencies={asset}&kind=news&regions=en&page={i}')['results']
                result = result + [{'id': news['id'], 'title': news['title'], 'time': convert_to_utc(news['created_at'], "%Y-%m-%dT%H:%M:%SZ") if len(news['created_at'])<=20 else convert_to_utc(news['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), 'symbol': asset} for news in newsResult]
            except Exception as e:
                print(f'[WARNING] caught error when downloading news for {asset} on page {i}: {e}')
            finally:
                time.sleep(0.2)

        df = pd.DataFrame.from_records(result)
        query = 'INSERT IGNORE INTO cryptoPanic (id, asset, ts, title) VALUES (%s, %s, %s, %s)'
        dataInList = [(r['id'], r['symbol'], r['time'], r['title']) for i,r in df.iterrows()]
        insertAddrToDb(df, query, dataInList)

if __name__ == "__main__":
    getNewsCryptoPanic(getAssets(), 10)