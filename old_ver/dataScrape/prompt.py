import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from util.sql_tools import queryDB, insertAddrToDb
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# model functions

def promptPaLM(asset, headline):# local machine auth is needed with google cli, https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev
    # V1
    setUpPrompt = 'You are a cryptocurrency expert with trading recommendation experience.'
    prompt = f'''Is this headline good or bad for the price of {asset} in 12 hrs? Answer “YES” if the price is expected to rise, “NO” if the price is expected to fall, "UNCERTAIN" if it's uncertain. Then elaborate with one concise sentence.  Headline: {headline}'''
    print(f'[PaLM] Doing prompt: {prompt}')

    vertexai.init(project="plated-dryad-398916", location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "max_output_tokens": 50,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    chat = chat_model.start_chat(
        context=f"""{setUpPrompt}""",
    )
    response = chat.send_message(f"""{prompt}""", **parameters)
    print(f"Response from Model: {response.text}")
    return response.text

def promptGpt3_5V1(asset, headline):
    # V1
    setUpPrompt = 'You are a cryptocurrency expert with trading recommendation experience.'
    prompt = f'''Is this headline good or bad for the price of {asset} in 12 hrs? Answer “YES” if the price is expected to rise, “NO” if the price is expected to fall, "UNCERTAIN" if it's uncertain. Then elaborate with one concise sentence.  Headline: {headline}'''
    print(f'[GPT3.5] Doing prompt: {prompt}')

    return gpt3_5Bot(setUpPrompt+prompt)

modelFunc = {
   'palmOutputV1' : promptPaLM,
   'gpt3_5OutputV1' : promptGpt3_5V1
}

# process news 

def getNewsToProcess(cutoffTs, model):
    # cutoffTs in s
    sql = f'''SELECT id, asset, title FROM cryptoPanic WHERE {model} is null and ts>{cutoffTs} and asset not in ('USDT','USDC','DAI')'''
    df = queryDB(sql)
    return df

def newsToSentiment(cutoffTs, model):
    import time
    import random

    try_time = 0    
    while True:
        try:
            df = getNewsToProcess(cutoffTs, model)
            print('[NEWS] News Headlines To Process: ', df.shape[0])

            for index, row in df.iterrows():
                startTime = time.time()
                # df['sentiment'] = df.apply(lambda row: promptPaLM(row['asset'], row['title']), axis=1)
                sentiment = modelFunc[model](row['asset'], row['title'])

                
                # update to DB
                query = f'''UPDATE cryptoPanic SET {model} = CASE '''+'''WHEN id = %s and asset = %s THEN %s '''+f'''ELSE {model} END;'''
                dataInList = [(row['id'], row['asset'], sentiment)]
                insertAddrToDb(df, query, dataInList)
                waitTime = max((1-(time.time() - startTime)),0) 
                print(f'[NEWS] wait time: {waitTime}')
                time.sleep(waitTime)
                try_time = 0 
            break
        except Exception as e:
            try_time += 1
            print(e)
            if try_time == 3:
                print("- [WARNING] LLM Fail, retry limit reached")
                break
            retryCooldown = random.uniform(30,35)
            print(f"- [WARNING] LLM Fail, retrying in ... {retryCooldown}")
            time.sleep(retryCooldown)
            
    
if __name__ == "__main__":
    newsToSentiment(1693872000, 'palmOutputV1')

