import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg") #switches matplotlib to backend and draws straigth into the files
import matplotlib.pyplot as plt
CHART_DIR = Path("outputs/charts")


def plot_histogram(df:pd.DataFrame,col:str,bins:int =20)-> dict:
    if col not in df.columns:
        return {"error":f"{col} not in {df.columns}"}

    if not pd.api.types.is_numeric_dtype(df[col]):
        return {"error":f" {col} is not numeric col is {df[col].dtype} "}

    data=df[col].dropna()
    if data.empty:
        return {"error":f"column {col} has no values to plot"}

    bin=max(5,min(int(bins),100))
    CHART_DIR.mkdir(parents=True,exist_ok=True)
    path=CHART_DIR/f"hist_{col}.png"

    fig,ax=plt.subplots(figsize=(6,4))
    ax.hist(data,bins=bins)
    ax.set_xlabel(col)
    ax.set_ylabel("count")
    ax.set_title(f"Distribution of {col}")
    fig.tight_layout()
    fig.savefig(path,dpi=120)
    plt.close(fig)

    return {
        "chart_path":str(path),
        "description":(
            f"Histogram of {col} with bins {bins}, based on {len(data)} non missing values"
            f"Range : {data.min():.2f} to {data.max():.2f}."
            f"skweness : {data.skew():.2f}"
        ),
    }



def get_schema(df: pd.DataFrame) -> dict:
    columns=[]
    for col in df.columns:
        columns.append({
            "name":col,
            "dtype":str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "n_unique":int(df[col].nunique())
        })

    return {
        "n_rows":int(df.shape[0]),
        "n_cols":int(df.shape[1]),
        "columns":columns,
        "sample_rows": df.head(3).to_dict(orient="records"),
    }


def describe_column(df : pd.DataFrame,col:str)-> dict:
    if col not in df.columns:
        return {"error":f"{col} not found in the dataframe with columsn {df.columns}"}

    series=df[col]
    result={"column":col,"missing": int(series.isna().sum())}

    if pd.api.types.is_numeric_dtype(series):
        result["type"] = "numeric"
        result["mean"] = round(float(series.mean()), 4)
        result["std"] = round(float(series.std()), 4)
        result["min"] = float(series.min())
        result["median"] = float(series.median())
        result["max"] = float(series.max())
    else:
        counts = series.value_counts().head(10)
        result["type"] = "categorical"
        result["n_unique"] = int(series.nunique())
        result["top_values"] = {str(k): int(v) for k, v in counts.items()}
    return result

