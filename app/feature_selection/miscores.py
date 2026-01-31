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

def mi_scores(df):

    df = df.drop(columns=['Date', 'Close', 'High', 'Low', 'Open'])
    X = df.copy()
    y = X.pop("Adj_Close")

    discrete_features = X.dtypes == int

    mi_scores = mutual_info_regression(X, y, discrete_features=discrete_features)
    mi_scores = pd.Series(mi_scores, name="MI Scores", index=X.columns)
    mi_scores = mi_scores.sort_values(ascending=False)

    return mi_scores

def plot_mi_scores(scores):
    scores = scores.sort_values(ascending=True)
    width = np.arange(len(scores))
    ticks = list(scores.index)
    plt.figure(dpi=100, figsize=(8, 5))
    plt.barh(width, scores)
    plt.yticks(width, ticks)
    plt.title("Mutual Information Scores")

    return plt.show()

nq_mi = mi_scores(nqdf)
plot_mi_scores(nq_mi)