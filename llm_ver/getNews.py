import requests
import json

# Empty list to store news 
news_list = []

# Page limit 100
page_limit = 101

# List of download ticker
ticker_list =['BTC', 'ETH', 'LTC', 'AXS', 'MATIC', 'SAND', 'SOL', 'AVAX', 'UNI', 'DOT']

# Downloading loop
for ticker in ticker_list:
    for page in range(1,page_limit):
        try:
            news = requests.get(f'https://cryptonews-api.com/api/v1?tickers={ticker}&items=100&page={page}&token=7eyzb0unkoyzsrqkrveeokogjljp9efmnclryybx').json()
            for i in news["data"]:
                news_list.append(i)
        except:
            break
    
    # Save to json file one by one
    with open(f'{ticker}news.json', 'w') as f:
        json.dump(news_list, f)
