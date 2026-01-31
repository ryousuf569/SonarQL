import yfinance as yf
import pandas as pd
import sqlite3 as sq

db_path = "app/db/sonarql.db"
conn = sq.connect(db_path)

start_date = "2023-01-01"
end_date = pd.Timestamp.today().strftime("%Y-%m-%d")

for ticker, table in [("NQ=F", "NQ_RAW"),("ES=F", "ES_RAW"),("YM=F", "YM_RAW"),]:
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
    print(ticker, df.shape)

    if not df.empty:
        df.reset_index().to_sql(table, conn, if_exists="replace", index=False)

conn.close()
