"""
add_day.py
----------
Appends ONE new day of ad events after the latest day already present in
data/raw/ad_events/. Used to demonstrate dbt incremental models:

    1. dbt run --select fct_campaign_performance --full-refresh   (build all)
    2. python add_day.py                                          (add 1 day)
    3. dbt run --select fct_campaign_performance                  (only new day!)

Run:  python add_day.py
"""

import os
import glob
import importlib.util

import pandas as pd

RAW_EVENTS = "data/raw/ad_events"


def load_generator():
    """Reuse make_events_for_day() from generate_data.py."""
    spec = importlib.util.spec_from_file_location("gen", "generate_data.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


def latest_day() -> pd.Timestamp:
    dirs = glob.glob(f"{RAW_EVENTS}/event_date=*")
    days = [pd.Timestamp(d.split("event_date=")[-1]) for d in dirs]
    return max(days)


def main():
    gen = load_generator()
    campaigns = pd.read_parquet("data/raw/campaigns.parquet")

    next_day = latest_day() + pd.Timedelta(days=1)
    part_dir = f"{RAW_EVENTS}/event_date={next_day:%Y-%m-%d}"
    os.makedirs(part_dir, exist_ok=True)

    df = gen.make_events_for_day(next_day, campaigns)
    df.to_parquet(f"{part_dir}/part.parquet", index=False)
    print(f"Added new day {next_day:%Y-%m-%d}: {len(df)} events")


if __name__ == "__main__":
    main()
