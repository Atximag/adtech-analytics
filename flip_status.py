"""
flip_status.py
--------------
Flips the status (active <-> paused) of one advertiser so you can watch a dbt
snapshot capture the change as SCD Type 2 history.

Demo:
    dbt snapshot --profiles-dir .          (capture #1)
    python flip_status.py                  (change advertiser 1's status)
    dbt run --profiles-dir . --select stg_advertisers
    dbt snapshot --profiles-dir .          (capture #2 -> history row appears)

Run:  python flip_status.py
"""

import sys
import pandas as pd

PATH = "data/raw/advertisers.parquet"
ADVERTISER_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def main():
    df = pd.read_parquet(PATH)
    mask = df.advertiser_id == ADVERTISER_ID
    current = df.loc[mask, "status"].iloc[0]
    new = "paused" if current == "active" else "active"
    df.loc[mask, "status"] = new
    df.to_parquet(PATH, index=False)
    print(f"advertiser {ADVERTISER_ID}: {current} -> {new}")


if __name__ == "__main__":
    main()
