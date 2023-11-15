import openai
import os
from json2csv import readDf

# Initialize OpenAI API with your key
from dotenv import dotenv_values
env_vars = dotenv_values("../.env")
api_key = env_vars['openaiKey']
openai.api_key = api_key
engine = "gpt-3.5-turbo"

def chain_of_thought_prompting(initial_prompt, iterations=3):
    current_prompt = initial_prompt + ", think step-by-step"
    messages = [
        {"role": "system", "content":'''You are a cryptocurrency expert with trading recommendation experience. You will give a sentiment score from 0 to 1 based on the given news, with 1 being the most positive and 0 being the most negative. The news headlines is given in a descending order from latest to oldest. Answer "the score is ??" in your answer, no need for elaboration.'''},
        {"role": "user", "content": current_prompt}
    ]
    
    response = openai.ChatCompletion.create(
        model=engine,
        messages=messages,
        max_tokens=150,
        n=iterations,
    )
        
    responses = [choice['message']['content'] for choice in response['choices'] if choice['message']['role'] == 'assistant']
    print(responses)
    responses_string = "first answer: " + ', next answer:'


if __name__ == "__main__":
    prompt = '''[Cathie Wood Clarifies Gary Gensler's Reason for Postponing Approval of Spot Bitcoin ETF, Impact of a Potential Spot Bitcoin ETF Approval on Crypto Market ‚Äì Here's What Traders Can Expect, Why is the SEC Delaying Bitcoin ETF Approval? Cathie Wood Weighs In]'''
    chain_of_thought_prompting(prompt)