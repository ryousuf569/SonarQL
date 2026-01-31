import sqlite3 as sq
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_selection import mutual_info_regression

db_path = "app/db/sonarql.db"
conn = sq.connect(db_path)

nq_query = "SELECT * FROM NQ_RAW"
es_query = "SELECT * FROM ES_RAW"
ym_query = "SELECT * FROM YM_RAW"

nqdf = pd.read_sql(nq_query, conn)
esdf = pd.read_sql(es_query, conn)
ymdf = pd.read_sql(ym_query, conn)

def price_info_scores(df):

    df = df.copy()

    price_signal = df["Adj_Close"].diff()
    price_signal = price_signal / price_signal.rolling(20).std()
    price_signal = price_signal.dropna()

    X = df.drop(columns=["Date", "Open", "High", "Low", "Close"])
    X = X.loc[price_signal.index]

    scores = []

    for col in X.columns:
        series = X[col]

        s = series.diff().loc[price_signal.index]

        if s.isna().all():
            continue

        corr = s.corr(price_signal)

        r2 = corr ** 2 if corr is not None else 0

        scores.append({
            "Indicator": col,
            "Abs_Corr": abs(corr),
            "R2_Explained": r2
        })

    scores_df = pd.DataFrame(scores)
    scores_df = scores_df.sort_values("R2_Explained", ascending=False)

    return scores_df

def plot_scores(scores): # To check for outliers
    scores = scores.sort_values(ascending=False)

    plt.figure(dpi=120, figsize=(8, 4))
    plt.plot(range(len(scores)), scores.values, marker='o')
    plt.xticks(range(len(scores)), scores.index, rotation=45)
    plt.ylabel("MI Score")
    plt.title("MI Scores (Sorted) – Leakage Check")
    plt.grid(alpha=0.3)
    plt.show()

def plot_mi_hist(scores, bins=20): # To see distribution
    plt.figure(dpi=120, figsize=(6, 4))
    plt.hist(scores.values, bins=bins)
    plt.xlabel("MI Score")
    plt.ylabel("Count")
    plt.title("MI Score Distribution")
    plt.show()


nq_info = price_info_scores(nqdf)
es_info = price_info_scores(esdf)
ym_info = price_info_scores(ymdf)

nq_info.to_csv("app/data/nq_price_info.csv", index=False)
es_info.to_csv("app/data/es_price_info.csv", index=False)
ym_info.to_csv("app/data/ym_price_info.csv", index=False)
