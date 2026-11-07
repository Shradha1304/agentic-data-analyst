import sys

import pandas as pd

from analyst.agent import run_agent

path = sys.argv[1] if len(sys.argv) > 1 else "data/titanic.csv"
df = pd.read_csv(path)

result = run_agent(df)
print("\n===== SUMMARY =====")
print(result["summary"])