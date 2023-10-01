import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vectorbt as vbt
import pandas as pd


def entryOnlyStopBound(priceSeq, orderDirections, cooldown, bound, size, posRatio): #cooldown in hrs
    threshold = pd.Timedelta(hours=cooldown)
    filteredSignal = orderDirections[orderDirections != 0]
    filteredSignal = filteredSignal[(filteredSignal.index.to_series().diff() >= threshold) | (filteredSignal.index.to_series().diff().isnull())]
    orderDirections = pd.DataFrame({'old': orderDirections, 'new': filteredSignal}).fillna(0)['new']

    portfolio = vbt.Portfolio.from_signals(
        priceSeq, entries=orderDirections.apply(lambda signal: True if signal >= 1 else False), short_entries=orderDirections.apply(lambda signal: True if signal <= -1 else False),
        sl_stop=bound,tp_stop=bound,
        size=size*posRatio, size_type=1,
        init_cash=size, fees=0, slippage=0)
    print(portfolio.orders.records_readable)
    return portfolio

def getReturn(portfolio):

    stats = portfolio.stats()
    print(stats)

    return portfolio.total_profit(), stats['Win Rate [%]'], stats['Total Open Trades'],stats['Total Closed Trades']
    
