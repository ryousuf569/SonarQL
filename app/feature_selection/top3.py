import pandas as pd

import pandas as pd

def get_top3_indicators(csv_path, metric="Abs_Corr"):
    df = pd.read_csv(csv_path)

    top3 = (df[df["Indicator"] != "Adj_Close"].sort_values(metric, ascending=False).head(3)["Indicator"].tolist())

    return top3
