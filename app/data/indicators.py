import pandas as pd
import numpy as np
import sqlite3 as sq

"""
Using code from an older project I worked on with Johan Naresh

View the code:
https://github.com/johannaresh/CSC-project/blob/main/tickerdataframe.py
"""

db_path = "app/db/sonarql.db"
conn = sq.connect(db_path)

nq_query = "SELECT * FROM NQ_RAW"
es_query = "SELECT * FROM ES_RAW"
ym_query = "SELECT * FROM YM_RAW"

nqdf = pd.read_sql(nq_query, conn)
esdf = pd.read_sql(es_query, conn)
ymdf = pd.read_sql(ym_query, conn)

def simple_ma(df, n=5): # Simple Moving Average
    df = df.copy()
    df[f"SMA{n}"] = df['Adj_Close'].rolling(window=n).mean()
    return df

def exp_ma(series, n=20):
    delta = 2 / (n + 1)
    ema = [series.iloc[0]]
    for t in range(1, len(series)):
        ema.append(delta * series.iloc[t] + (1 - delta) * ema[-1])
    return ema

def calc_exp(df, column="Adj_Close", n=20):
    df = df.copy()
    df[f"EMA{n}"] = exp_ma(df[column], n)
    return df

def calc_rsi(df, column="Adj_Close", n=14): # Relative Strength Index
    df = df.copy()
    delta = df[column].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=n).mean()
    avg_loss = loss.rolling(window=n).mean()

    rs = avg_gain / avg_loss
    df[f"RSI{n}"] = 100 - (100 / (1 + rs))
    return df

def calc_atr(df, n=14): # Average True Range
    df = df.copy()
    high, low, close = df["High"], df["Low"], df["Adj_Close"]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df[f"ATR{n}"] = tr.rolling(window=n).mean()
    return df

# OBV increases when price rises on high volume, decreases when it falls on high volume
def calc_obv(df, close_col="Adj_Close", vol_col="Volume"): 
    df = df.copy()
    direction = np.sign(df[close_col].diff()).fillna(0)
    df["OBV"] = (direction * df[vol_col]).cumsum()
    return df

#shows where the current price sits within its volatility range (0 = lower band, 1 = upper band)
def calc_bollinger_percent_b(df, column="Adj_Close", n=20, k=2):
    df = df.copy()
    sma = df[column].rolling(window=n).mean()
    std = df[column].rolling(window=n).std() # Rolling standard deviation

    upper = sma + k * std
    lower = sma - k * std

    df[f"Boll_%B{n}"] = (df[column] - lower) / (upper - lower)
    return df

def indicators(df):

    sma_df = simple_ma(df)
    ema_df = calc_exp(sma_df)
    rsi_df = calc_rsi(ema_df)
    atr_df = calc_atr(rsi_df)
    obv_df = calc_obv(atr_df)
    bol_df = calc_bollinger_percent_b(obv_df)

    df = bol_df.dropna()

    return df

nqdf = indicators(nqdf)
esdf = indicators(esdf)
ymdf = indicators(ymdf)

nqdf.to_sql("NQ_RAW", conn, if_exists="replace", index=False)
esdf.to_sql("ES_RAW", conn, if_exists="replace", index=False)
ymdf.to_sql("YM_RAW", conn, if_exists="replace", index=False)