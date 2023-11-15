import openai
import os
from json2csv import readDf
import json

# Initialize OpenAI API with your key
from dotenv import dotenv_values
env_vars = dotenv_values("../.env")
api_key = env_vars['openaiKey']
openai.api_key = api_key
engine = "gpt-3.5-turbo"

def chain_of_thought_prompting(initial_prompt, iter=1):
    # current_prompt = initial_prompt + ", think step-by-step"
    current_prompt = initial_prompt
    messages = [
        {"role": "system", "content":'''You are a cryptocurrency expert with trading recommendation experience. You will give a sentiment score from -1 to 1 based on the given news, with 1 being the most positive and -1 being the most negative. The news headlines is given in a descending order from latest to oldest. Answer "the score is " in your answer, no need for elaboration.'''},
        {"role": "user", "content": current_prompt}
    ]
    
    response = openai.ChatCompletion.create(
        model=engine,
        messages=messages,
        max_tokens=70,
        n=iter,
    )
        
    responses = [choice['message']['content'] for choice in response['choices'] if choice['message']['role'] == 'assistant']
    return responses


def normalPrompt(news, token):
    import re
    import numpy as np
    try:
        # news = ['Protocol Hosting Google reCAPTCHA Competitor Expands to Polkadot', "Gavin Wood: Polkadot is a ‚Äòbet against blockchain maximalism'"]
        # token = 'DOT'
        prompt = f'''
        This is the news headlines of the day:
        {json.dumps(news)[:2000]}
        , regarding token : {token}.
        '''.strip()[:4097]
        res = chain_of_thought_prompting(prompt)
        # print(f'Normal Prompt {res}')
        res = [float(re.findall(r'-?\d+\.\d+|-?\d+', string)[0]) for string in res if len(re.findall(r'-?\d+\.\d+|-?\d+', string)) > 0]
        # print(f'Normal Prompt {res}')
        return res[0] if len(res) > 0 else 0
    except Exception as e:
        print(e)
        return np.nan
    
def cot(news, token, iter=1):
    import re
    import statistics
    import numpy as np
    try:
        # news = ['First DeFi project on Cardano shifts over from Polkadot', 'IoT on Polkadot: Why Amazon Web Services for IoT Is No Longer in the Game', 'Price analysis 12/11: BTC, ETH, XRP, LTC, BCH, LINK, ADA, DOT, BNB, XLM']
        # token = 'DOT'
        prompt = f'''
        Question: This is the news headlines of the day:
        ['First DeFi project on Cardano shifts over from Polkadot', 'IoT on Polkadot: Why Amazon Web Services for IoT Is No Longer in the Game', 'Price analysis 12/11: BTC, ETH, XRP, LTC, BCH, LINK, ADA, DOT, BNB, XLM']
        , regarding token : DOT.

        Answer: The score is -0.333333333

        Question: This is the news headlines of the day:
        ['Litecoin Price Prediction, How High Will LTC Rise in 2021?', 'Price analysis 4/28: BTC, ETH, BNB, XRP, ADA, DOGE, DOT, UNI, LTC, BCH', 'Here Are Key Bullish Levels for Cardano, Dogecoin, and Litecoin, According to Trader Scott Melker']
        , regarding token : LTC.

        Answer: The score is 0.666666667

        This is the news headlines of the day:
        {json.dumps(news)[:2000]}
        , regarding token : {token}.

        Answer: 
        '''.strip()[:4097]
        # print(prompt)
        res = chain_of_thought_prompting(prompt, iter=iter)
        # print(f'COT Prompt {res}')
        res = [float(re.findall(r'-?\d+\.\d+|-?\d+', string)[0]) for string in res if len(re.findall(r'-?\d+\.\d+|-?\d+', string)) > 0]
        # print(f'COT Prompt {res}')
        return statistics.mode(res) if len(res) > 0 else 0
    except Exception as e:
        print(e)
        return np.nan

if __name__ == '__main__':
    news = ['First DeFi project on Cardano shifts over from Polkadot', 'IoT on Polkadot: Why Amazon Web Services for IoT Is No Longer in the Game', 'Price analysis 12/11: BTC, ETH, XRP, LTC, BCH, LINK, ADA, DOT, BNB, XLM']
    token = 'DOT'
    cot(news, token, 3)

__all__ = ['cot','normalPrompt']