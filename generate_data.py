"""
generate_data.py
----------------
Generates a synthetic ad-tech dataset for the analytics-engineering project.

Output (Parquet, written under ./data/raw/):
    advertisers.parquet                          -- dimension
    campaigns.parquet                            -- dimension
    ad_events/event_date=YYYY-MM-DD/part.parquet -- fact, partitioned by day

The fact table is partitioned by day on purpose: this is what lets us build an
INCREMENTAL dbt model later (load only new partitions instead of the whole history),
which is one of the skills the job asks for.

Run:  python generate_data.py
"""

import os
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Config -- tweak these freely. Bigger N_DAYS / EVENTS_PER_DAY = more "high load".
# ----------------------------------------------------------------------------
SEED = 42
N_ADVERTISERS = 50
N_CAMPAIGNS = 200
N_DAYS = 30
EVENTS_PER_DAY = 20_000          # impressions/day; clicks & conversions derive from these
START_DATE = pd.Timestamp("2026-05-01")
OUT_DIR = "data/raw"

rng = np.random.default_rng(SEED)

COUNTRIES = ["CY", "GR", "DE", "FR", "GB", "ES", "IT", "PL", "NL", "RO"]
DEVICES = ["mobile", "desktop", "tablet", "ctv"]
CHANNELS = ["display", "video", "native", "search"]


def make_advertisers() -> pd.DataFrame:
    return pd.DataFrame({
        "advertiser_id": np.arange(1, N_ADVERTISERS + 1),
        "advertiser_name": [f"Advertiser_{i:03d}" for i in range(1, N_ADVERTISERS + 1)],
        "country": rng.choice(COUNTRIES, N_ADVERTISERS),
        # a few advertisers churn -> useful for snapshot/SCD demonstrations later
        "status": rng.choice(["active", "paused"], N_ADVERTISERS, p=[0.85, 0.15]),
        "created_at": START_DATE - pd.to_timedelta(rng.integers(30, 400, N_ADVERTISERS), unit="D"),
    })


def make_campaigns() -> pd.DataFrame:
    return pd.DataFrame({
        "campaign_id": np.arange(1, N_CAMPAIGNS + 1),
        "advertiser_id": rng.integers(1, N_ADVERTISERS + 1, N_CAMPAIGNS),
        "campaign_name": [f"Campaign_{i:04d}" for i in range(1, N_CAMPAIGNS + 1)],
        "channel": rng.choice(CHANNELS, N_CAMPAIGNS),
        "bid_cpm": np.round(rng.uniform(0.5, 12.0, N_CAMPAIGNS), 2),   # cost per 1000 impressions
        "daily_budget": np.round(rng.uniform(50, 2000, N_CAMPAIGNS), 2),
        "start_date": START_DATE - pd.to_timedelta(rng.integers(0, 20, N_CAMPAIGNS), unit="D"),
    })


def make_events_for_day(day: pd.Timestamp, campaigns: pd.DataFrame) -> pd.DataFrame:
    """Generate one day's worth of impression/click/conversion events."""
    n = EVENTS_PER_DAY
    camp = campaigns.sample(n, replace=True, random_state=int(day.value % (2**31)))

    # base impression rows
    ts = day + pd.to_timedelta(rng.integers(0, 24 * 3600, n), unit="s")
    df = pd.DataFrame({
        "event_id": [f"{day:%Y%m%d}-{i}" for i in range(n)],
        "event_ts": ts,
        "campaign_id": camp["campaign_id"].to_numpy(),
        "device": rng.choice(DEVICES, n),
        "country": rng.choice(COUNTRIES, n),
        "event_type": "impression",
        # revenue per impression = bid_cpm / 1000, with a little noise
        "revenue": np.round(camp["bid_cpm"].to_numpy() / 1000.0 * rng.uniform(0.8, 1.2, n), 5),
    })

    # derive clicks (CTR ~ 2%) and conversions (CVR ~ 8% of clicks) as extra rows
    click_mask = rng.random(n) < 0.02
    clicks = df[click_mask].copy()
    clicks["event_type"] = "click"
    clicks["event_id"] = clicks["event_id"] + "-c"
    clicks["revenue"] = 0.0

    conv_mask = rng.random(len(clicks)) < 0.08
    convs = clicks[conv_mask].copy()
    convs["event_type"] = "conversion"
    convs["event_id"] = convs["event_id"].str.replace("-c", "-v", regex=False)

    out = pd.concat([df, clicks, convs], ignore_index=True)
    # ~2% of rows get a NULL country on purpose -> gives us something for data-quality tests
    null_idx = rng.choice(out.index, size=int(len(out) * 0.02), replace=False)
    out.loc[null_idx, "country"] = None
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    advertisers = make_advertisers()
    campaigns = make_campaigns()
    advertisers.to_parquet(f"{OUT_DIR}/advertisers.parquet", index=False)
    campaigns.to_parquet(f"{OUT_DIR}/campaigns.parquet", index=False)
    print(f"advertisers: {len(advertisers)} rows")
    print(f"campaigns:   {len(campaigns)} rows")

    total = 0
    for d in pd.date_range(START_DATE, periods=N_DAYS, freq="D"):
        part_dir = f"{OUT_DIR}/ad_events/event_date={d:%Y-%m-%d}"
        os.makedirs(part_dir, exist_ok=True)
        day_df = make_events_for_day(d, campaigns)
        day_df.to_parquet(f"{part_dir}/part.parquet", index=False)
        total += len(day_df)
    print(f"ad_events:   {total} rows across {N_DAYS} daily partitions")
    print(f"\nDone. Data written under ./{OUT_DIR}/")


if __name__ == "__main__":
    main()
