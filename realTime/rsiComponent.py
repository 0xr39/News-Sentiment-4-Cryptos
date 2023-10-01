def getRSI(df, length):
    import pandas_ta as ta
    
    df = df.copy()
    
    rsi  = df.ta.rsi(length=length, scalar = 100)
    df['rsi'] = rsi
    return df

def rsiProcess(dfDict):
    result = {}
    for asset, df in dfDict.items():
        dfTa = getRSI(df, 30)
        rsi = dfTa['rsi']
        latestRsi = rsi.sort_index().iloc[-1]
        # rsiSignal = rsi.apply(lambda rsi: 1 if rsi >= 70 else (-1 if rsi <= 30 else 0))
        rsiSignal =  1 if latestRsi >= 75 else (-1 if latestRsi <= 25 else 0)
        result[asset] = rsiSignal
    return result