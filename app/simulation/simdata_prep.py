import pandas as pd
import numpy as np
import sqlite3 as sq

db_path = "app/db/sonarql.db"
conn = sq.connect(db_path)

nq_query = "SELECT * FROM NQ_RAW"
es_query = "SELECT * FROM ES_RAW"
ym_query = "SELECT * FROM YM_RAW"

nqdf = pd.read_sql(nq_query, conn)
esdf = pd.read_sql(es_query, conn)
ymdf = pd.read_sql(ym_query, conn)

nq_mi = pd.read_csv("app/data/nq_mutual_info.csv")
es_mi = pd.read_csv("app/data/es_mutual_info.csv") 
ym_mi = pd.read_csv("app/data/ym_mutual_info.csv")

nq_mi.columns = ['Indicators', 'MI Scores']
es_mi.columns = ['Indicators', 'MI Scores']
ym_mi.columns = ['Indicators', 'MI Scores']

nqmi_top3 = nq_mi.sort_values("MI Scores", ascending=False).head(3)
esmi_top3 = es_mi.sort_values("MI Scores", ascending=False).head(3)
ymmi_top3 = ym_mi.sort_values("MI Scores", ascending=False).head(3)