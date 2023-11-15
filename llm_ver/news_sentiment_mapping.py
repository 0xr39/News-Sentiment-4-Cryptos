import pandas as pd
from cotsc import normalPrompt, cot

class news_sentiment_mapping():

    def __init__(self, startTs, endTs) -> None:
        self.df = pd.read_csv('./gpnews.csv')
        self.df = self.df[(self.df['dateTs'] >= startTs) & (self.df['dateTs'] <= endTs)]

    @property
    def result(self) -> pd.DataFrame():
        return self.df
    
    def addNormalPrompt(self) -> None:
        self.df['normalPrompt'] = self.df.apply(lambda row: normalPrompt(row['Title'],row['Ticker']),axis =1)

    def addCOT(self) -> None:
        self.df['cot'] = self.df.apply(lambda row: cot(row['Title'],row['Ticker']),axis =1)
    
    def addCOTSC(self, iter) -> None:
        self.df['cotsc'] = self.df.apply(lambda row: cot(row['Title'],row['Ticker'], iter=iter),axis =1)

if __name__ == '__main__':
    mapping = news_sentiment_mapping(1696896000,1699574400)
    print('starting LLM')
    mapping.addNormalPrompt()
    mapping.addCOT()
    mapping.addCOTSC(5)

    mapping.result.to_csv('./mapping.csv')