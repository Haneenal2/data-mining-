"""Steps 2-4: Filter EPA daily files to Texas, flag (not delete) records, stack years, merge pollutants.

Inputs : ../Original_Datasets/daily_{88101,44201}_{2020..2024}.zip  (read directly, ZIPs untouched)
Outputs: ../Texas_Filtered_Data/Texas_{PM25,Ozone}_{year}.csv
         ../Combined_Datasets/Texas_PM25_Combined.csv
         ../Combined_Datasets/Texas_Ozone_Combined.csv
         ../Combined_Datasets/Texas_PM25_Ozone_SiteDay_Merged.csv
         ./stats/*.csv  (tables used in the report)

Run from the project root:  python Documentation/02_filter_clean_combine.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / "Original_Datasets"
FILT = ROOT / "Texas_Filtered_Data"
COMB = ROOT / "Combined_Datasets"
STATS = ROOT / "Documentation" / "stats"
YEARS = range(2020, 2025)
POLLUTANTS = {"88101": "PM25", "44201": "Ozone"}
TEXAS = "48"

# EPA column name -> R-friendly snake_case name. All 29 original columns are kept.
RENAME = {
    "State Code": "state_code", "County Code": "county_code", "Site Num": "site_num",
    "Parameter Code": "parameter_code", "POC": "poc", "Latitude": "latitude",
    "Longitude": "longitude", "Datum": "datum", "Parameter Name": "parameter_name",
    "Sample Duration": "sample_duration", "Pollutant Standard": "pollutant_standard",
    "Date Local": "date_local", "Units of Measure": "units_of_measure",
    "Event Type": "event_type", "Observation Count": "observation_count",
    "Observation Percent": "observation_percent", "Arithmetic Mean": "arithmetic_mean",
    "1st Max Value": "first_max_value", "1st Max Hour": "first_max_hour", "AQI": "aqi",
    "Method Code": "method_code", "Method Name": "method_name",
    "Local Site Name": "local_site_name", "Address": "address", "State Name": "state_name",
    "County Name": "county_name", "City Name": "city_name", "CBSA Name": "cbsa_name",
    "Date of Last Change": "date_of_last_change",
}
# A monitor-day record is unique on these columns (verified: zero duplicates in every file).
RECORD_KEY = ["site_id", "poc", "date_local", "sample_duration", "pollutant_standard", "event_type"]


def flag_records(df, pollutant):
    """Add analysis_record (bool) and record_note. Nothing is removed."""
    note = pd.Series("", index=df.index)
    keep = pd.Series(True, index=df.index)

    excluded = df["event_type"].eq("Excluded")
    keep &= ~excluded
    note[excluded] = "Exceptional-event hours removed by EPA; the 'Included' row for this monitor-day is used instead"

    if pollutant == "PM25":
        hourly = df["sample_duration"].eq("1 HOUR")
        keep &= ~hourly
        note[hourly] = ("Daily summary of continuous hourly data with no AQI/standard; the same data appears "
                        "as a '24-HR BLK AVG' row when the day is >=75% complete")
        neg = pd.to_numeric(df["arithmetic_mean"]) < 0
        note[neg & keep] = "Small negative value: valid EPA measurement near zero (instrument noise), kept"

    df["analysis_record"] = keep
    df["record_note"] = note
    return df


def to_r_csv(df, path):
    """Write CSV with booleans as TRUE/FALSE so R reads them as logical, not text."""
    out = df.copy()
    for c in out.select_dtypes("bool").columns:
        out[c] = out[c].map({True: "TRUE", False: "FALSE"})
    out.to_csv(path, index=False, encoding="utf-8")


def filter_one(code, year):
    pollutant = POLLUTANTS[code]
    src = ORIG / f"daily_{code}_{year}.zip"
    raw = pd.read_csv(src, dtype=str, keep_default_na=False, na_values=[""])
    n_original = len(raw)

    tx = raw[raw["State Code"] == TEXAS].rename(columns=RENAME).copy()
    assert (tx["state_name"] == "Texas").all()
    assert (tx["parameter_code"] == code).all()
    n_texas = len(tx)

    tx.insert(0, "site_id", tx["state_code"] + "-" + tx["county_code"] + "-" + tx["site_num"])
    tx.insert(1, "year", year)
    tx.insert(2, "pollutant", pollutant)

    n_full_dups = int(tx.duplicated().sum())
    n_key_dups = int(tx.duplicated(RECORD_KEY).sum())
    # Exact duplicate rows would be removed here; none exist in the 2020-2024 files.
    tx = tx.drop_duplicates()

    tx = flag_records(tx, pollutant)
    tx = tx.sort_values(["site_id", "poc", "date_local", "sample_duration"]).reset_index(drop=True)

    out = FILT / f"Texas_{pollutant}_{year}.csv"
    to_r_csv(tx, out)

    stats = {
        "year": year, "pollutant": pollutant, "parameter_code": code, "source_file": src.name,
        "original_records": n_original, "texas_records": n_texas,
        "exact_duplicates_removed": n_full_dups, "key_duplicates": n_key_dups,
        "records_retained": len(tx), "analysis_records": int(tx["analysis_record"].sum()),
        "sites": tx["site_id"].nunique(), "counties": tx["county_name"].nunique(),
        "first_date": tx["date_local"].min(), "last_date": tx["date_local"].max(),
        "distinct_dates": tx["date_local"].nunique(), "output_file": out.name,
    }
    return tx, stats


def missing_table(df, pollutant, year):
    na = df.isna().sum()
    return [{"pollutant": pollutant, "year": year, "column": c, "missing": int(n),
             "percent": round(100 * n / len(df), 2)} for c, n in na.items() if n > 0]


def site_coverage(df, pollutant):
    a = df[df["analysis_record"]]
    g = (a.groupby(["site_id", "year"])
          .agg(county_name=("county_name", "first"), city_name=("city_name", "first"),
               local_site_name=("local_site_name", "first"), days_with_data=("date_local", "nunique"))
          .reset_index())
    g["days_in_year"] = g["year"].map(lambda y: 366 if y % 4 == 0 else 365)
    g["percent_days"] = (100 * g["days_with_data"] / g["days_in_year"]).round(1)
    g["pollutant"] = pollutant
    return g


def site_day(df, pollutant):
    """Collapse to one row per site per date (analysis records only) for the cross-pollutant merge."""
    a = df[df["analysis_record"]].copy()
    a["arithmetic_mean"] = pd.to_numeric(a["arithmetic_mean"])
    a["first_max_value"] = pd.to_numeric(a["first_max_value"])
    a["aqi"] = pd.to_numeric(a["aqi"])
    g = a.groupby(["site_id", "date_local"])
    if pollutant == "PM25":
        out = g.agg(pm25_daily_mean_ugm3=("arithmetic_mean", "mean"),
                    pm25_aqi=("aqi", "max"),
                    pm25_n_records=("arithmetic_mean", "size"))
    else:
        out = g.agg(ozone_mda8_ppm=("first_max_value", "mean"),
                    ozone_daily_mean_ppm=("arithmetic_mean", "mean"),
                    ozone_aqi=("aqi", "max"),
                    ozone_n_records=("first_max_value", "size"))
    meta = g.agg(county_name=("county_name", "first"), city_name=("city_name", "first"),
                 local_site_name=("local_site_name", "first"),
                 latitude=("latitude", "first"), longitude=("longitude", "first"))
    return out.join(meta).reset_index()


def main():
    for d in (FILT, COMB, STATS, ROOT / "EDA_Results"):
        d.mkdir(exist_ok=True)

    summary, missing, coverage, methods, combined = [], [], [], [], {}
    for code, pollutant in POLLUTANTS.items():
        parts = []
        for year in YEARS:
            tx, st = filter_one(code, year)
            print(f"{pollutant} {year}: original={st['original_records']:,} texas={st['texas_records']:,} "
                  f"retained={st['records_retained']:,} analysis={st['analysis_records']:,}")
            summary.append(st)
            missing += missing_table(tx, pollutant, year)
            m = tx.groupby(["method_code", "method_name", "sample_duration", "units_of_measure"],
                           dropna=False).size().reset_index(name="records")
            m.insert(0, "year", year)
            m.insert(0, "pollutant", pollutant)
            methods.append(m)
            parts.append(tx)

        # STACKING (appending rows): same columns, different years; Year column identifies the source.
        stacked = pd.concat(parts, ignore_index=True)
        assert len(stacked) == sum(len(p) for p in parts)
        assert stacked.duplicated(RECORD_KEY).sum() == 0
        assert stacked["units_of_measure"].nunique() == 1
        to_r_csv(stacked, COMB / f"Texas_{pollutant}_Combined.csv")
        combined[pollutant] = stacked
        coverage.append(site_coverage(stacked, pollutant))
        print(f"  -> Texas_{pollutant}_Combined.csv: {len(stacked):,} rows")

    # MERGING (joining columns): PM2.5 and ozone matched on the exact monitoring site + date.
    pm = site_day(combined["PM25"], "PM25")
    oz = site_day(combined["Ozone"], "Ozone")
    meta_cols = ["county_name", "city_name", "local_site_name", "latitude", "longitude"]
    merged = pm.merge(oz, on=["site_id", "date_local"], how="outer", suffixes=("", "_oz"), indicator=True)
    for c in meta_cols:
        merged[c] = merged[c].fillna(merged[f"{c}_oz"])
    merged = merged.drop(columns=[f"{c}_oz" for c in meta_cols])
    merged["match_status"] = merged["_merge"].map(
        {"both": "both_pollutants", "left_only": "pm25_only", "right_only": "ozone_only"}).astype(str)
    merged = merged.drop(columns="_merge")
    merged.insert(2, "year", merged["date_local"].str[:4].astype(int))
    assert not merged.duplicated(["site_id", "date_local"]).any()
    assert (merged["match_status"] != "ozone_only").sum() == len(pm)
    assert (merged["match_status"] != "pm25_only").sum() == len(oz)
    lead = ["site_id", "date_local", "year", "match_status"] + meta_cols
    merged = merged[lead + [c for c in merged.columns if c not in lead]]
    merged = merged.sort_values(["site_id", "date_local"])
    merged.to_csv(COMB / "Texas_PM25_Ozone_SiteDay_Merged.csv", index=False, encoding="utf-8")
    print(f"  -> Texas_PM25_Ozone_SiteDay_Merged.csv: {len(merged):,} rows "
          f"({merged['match_status'].value_counts().to_dict()})")

    pd.DataFrame(summary).to_csv(STATS / "record_counts.csv", index=False)
    pd.DataFrame(missing).to_csv(STATS / "missing_values.csv", index=False)
    pd.concat(coverage).to_csv(STATS / "site_coverage.csv", index=False)
    pd.concat(methods).to_csv(STATS / "methods_units.csv", index=False)
    merged.groupby(["year", "match_status"]).size().unstack(fill_value=0).to_csv(STATS / "merge_match_counts.csv")


if __name__ == "__main__":
    main()
