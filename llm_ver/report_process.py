import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.sql_tools import queryDB
import pandas as pd

ticker_list =['BTC', 'ETH', 'LTC', 'AXS', 'MATIC', 'SAND', 'SOL', 'AVAX', 'UNI', 'DOT']

def getPrice(startTs, endTs):
    query = f'''SELECT ts, asset, (closePrice/openPrice) as priceDelta FROM okx1DutcSpot WHERE ts >= {startTs} and ts <= {endTs} and asset in ('BTC', 'ETH', 'LTC', 'AXS', 'MATIC', 'SAND', 'SOL', 'AVAX', 'UNI', 'DOT')'''
    df = queryDB(query)
    return df

def plot_regression_lines(df, predictor_cols, target_col, save_path):
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, predictor_col in enumerate(predictor_cols):
        # Scatter plot
        scatter = ax.scatter(df[predictor_col], df[target_col], label=predictor_col)

        # Linear regression
        model = LinearRegression()
        X = df[predictor_col].values.reshape(-1, 1)
        y = df[target_col].values.reshape(-1, 1)
        model.fit(X, y)
        y_pred = model.predict(X)

        # Plotting the regression line
        ax.plot(df[predictor_col], y_pred)

        # R-squared value
        r2 = r2_score(y, y_pred)
        scatter.set_label(f"{predictor_col} (R-squared: {r2:.5f})")

    # Plot settings
    ax.set_xlabel("Predictor")
    ax.set_ylabel("Target")

    # Create a legend with updated labels
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='best')

    # Adjust spacing
    plt.tight_layout()

    # Save the plot as a PNG image
    plt.savefig(save_path)

    # plt.show()

priceDf = getPrice(1696982400,1699660800).rename(columns={'ts': 'dateTs','asset': 'Ticker'})
priceDf['dateTs'] = priceDf['dateTs'] - 86400
newsDf = pd.read_csv('./mapping.csv', index_col=0)
merged_df = pd.merge(priceDf, newsDf, on=['dateTs', 'Ticker'])
merged_df = merged_df.sort_values('dateTs')
merged_df = merged_df.dropna()
print(merged_df)

plot_regression_lines(merged_df, ['normalPrompt','cot','cotsc'], 'sentimentScore', './sentiment_reg.png')

plot_regression_lines(merged_df, ['sentimentScore','cotsc'], 'priceDelta', './price_reg.png')

