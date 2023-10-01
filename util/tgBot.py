from dotenv import dotenv_values
env_vars = dotenv_values("../.env")
# from telegram import Bot
import asyncio
import requests

tgBotKey = env_vars['tgBotKey']
mk3Id = env_vars['mk3Id']
mk5Id = env_vars['mk5Id']

def sendMsg(content, chatIds = [mk3Id,mk5Id]):
    def botSend(chatId):
        response = requests.post(
            url='https://api.telegram.org/bot{0}/{1}'.format(tgBotKey, 'sendMessage'),
            data={'chat_id': chatId, 'text': content}
        ).json()

    for id in chatIds:
        botSend(id)

