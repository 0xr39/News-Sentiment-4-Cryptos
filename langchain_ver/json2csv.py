import json 
import pandas as pd
from datetime import datetime

# List of ticker
ticker_list =['BTC', 'ETH', 'LTC', 'AXS', 'MATIC', 'SAND', 'SOL', 'AVAX', 'UNI', 'DOT']

# Empty DF
df = pd.DataFrame(columns=['Timestamp','Title','Ticker'])

# Open json file and append news to df
for ticker in ticker_list:
    f = open(f'{ticker}news.json')
    ticker_news = json.load(f)
    for i in range(len(ticker_news)):
        df = df.append({'Timestamp':ticker_news[i]['date'],'Title':ticker_news[i]['title'],'Ticker':ticker}, ignore_index=True)

# Change Timestamp type
df["Timestamp"] = df["Timestamp"].apply(lambda x: int(datetime.strptime(x, "%a, %d %b %Y %H:%M:%S %z").timestamp()))

# Save all to CSV file
df.to_csv('news.csv',index=False)