import pandas as pd
import sqlite3 as sq

db_path = "app/db/sonarql.db"
conn = sq.connect(db_path)

nq_query = "SELECT * FROM NQ_RAW"
es_query = "SELECT * FROM ES_RAW"
ym_query = "SELECT * FROM YM_RAW"

nqdf = pd.read_sql(nq_query, conn)
esdf = pd.read_sql(es_query, conn)
ymdf = pd.read_sql(ym_query, conn)

def clean_table(df):

    df.columns = ['Date', 'Adj_Close', 'Close', 'High', 'Low', 'Open', 'Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.normalize()
    return df

cleaned_nq = clean_table(nqdf)
cleaned_es = clean_table(esdf)
cleaned_ym = clean_table(ymdf)

cleaned_nq.to_sql("NQ_RAW", conn, if_exists="replace", index=False)
cleaned_es.to_sql("ES_RAW", conn, if_exists="replace", index=False)
cleaned_ym.to_sql("YM_RAW", conn, if_exists="replace", index=False)