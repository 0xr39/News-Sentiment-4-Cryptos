from poe_api_wrapper import PoeApi
import warnings

token = 'i7XUAtP0PgBSqBjf6Muh-Q=='
client = PoeApi(token)

def gpt3_5Bot(msg):
    warnings.filterwarnings("ignore")
    result = ''
    for chunk in client.send_message('chinchilla', msg):
        result = result + chunk["response"]
        # print(chunk["response"], end="", flush=True)
    client.delete_chat('chinchilla', del_all=True)
    warnings.resetwarnings()
    return result

