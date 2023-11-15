import json 
import pandas as pd
from datetime import datetime
import math
import warnings
warnings.filterwarnings('ignore')

# List of ticker
ticker_list =['BTC', 'ETH', 'LTC', 'AXS', 'MATIC', 'SAND', 'SOL', 'AVAX', 'UNI', 'DOT']

# Empty DF
def readDf():
    df = pd.DataFrame(columns=['Timestamp','Title','Ticker','sentiment'])

    # Open json file and append news to df
    for ticker in ticker_list:
        f = open(f'./news_json/{ticker}news.json')
        ticker_news = json.load(f)
        for i in range(len(ticker_news)):
            df = df.append({'Timestamp':ticker_news[i]['date'],'Title':ticker_news[i]['title'],'Ticker':ticker, 'sentiment': ticker_news[i]['sentiment']}, ignore_index=True)

    # Change Timestamp type
    df["Timestamp"] = df["Timestamp"].apply(lambda x: int(datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %z").timestamp()))
    df['sentimentScore'] = df['sentiment'].apply(lambda x: 0 if x == 'Neutral' else (1 if x == 'Positive' else -1))

    # Save all to CSV file
    df.to_csv('news.csv',index=False)

    return df

def groupDf(_df):
    df = _df.copy()
    df['dateTs'] =  df["Timestamp"].apply(lambda x: math.floor(x/86400)*86400)
    df = df.sort_values('Timestamp')
    df = df.groupby(['dateTs', 'Ticker']).agg({
        'Title': lambda x: list(x),
        'sentimentScore': 'mean'
    }).reset_index()
    
    df.to_csv('gpnews.csv',index=False)
    return df

if __name__ == "__main__":
    df = readDf()
    groupedDf = groupDf(df)

__all__ = ['readDf']