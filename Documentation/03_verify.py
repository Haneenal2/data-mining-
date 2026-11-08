"""Step 6: Independent verification of every output file.

Re-reads the original ZIPs and the written CSVs from disk and checks:
  - each ZIP is real EPA AirData (expected 29-column header, single parameter code, many states)
  - every filtered record is Texas (state code 48) and matches the source row count exactly
  - filtered values are byte-identical to the original EPA values (no altered measurements/dates)
  - combined files contain exactly the intended years and equal the sum of the yearly files
  - no duplicate records; merged file has one row per site per date and loses no site-days
Writes Documentation/verification_results.txt.

Run from the project root:  python Documentation/03_verify.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
YEARS = list(range(2020, 2025))
POLLUTANTS = {"88101": "PM25", "44201": "Ozone"}
EPA_HEADER = ["State Code", "County Code", "Site Num", "Parameter Code", "POC", "Latitude", "Longitude",
              "Datum", "Parameter Name", "Sample Duration", "Pollutant Standard", "Date Local",
              "Units of Measure", "Event Type", "Observation Count", "Observation Percent",
              "Arithmetic Mean", "1st Max Value", "1st Max Hour", "AQI", "Method Code", "Method Name",
              "Local Site Name", "Address", "State Name", "County Name", "City Name", "CBSA Name",
              "Date of Last Change"]
KEY = ["site_id", "poc", "date_local", "sample_duration", "pollutant_standard", "event_type"]

lines, failures = [], []


def check(ok, msg):
    lines.append(f"[{'PASS' if ok else 'FAIL'}] {msg}")
    if not ok:
        failures.append(msg)


def read(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])


for code, pol in POLLUTANTS.items():
    yearly_total = 0
    for y in YEARS:
        raw = read(ROOT / "Original_Datasets" / f"daily_{code}_{y}.zip")
        check(list(raw.columns) == EPA_HEADER, f"{pol} {y}: ZIP has the standard EPA AirData daily header")
        check(raw["Parameter Code"].eq(code).all(), f"{pol} {y}: ZIP contains only parameter {code}")
        check(raw["State Code"].nunique() > 40, f"{pol} {y}: ZIP is national ({raw['State Code'].nunique()} state codes)")
        check(raw["Date Local"].str[:4].eq(str(y)).all(), f"{pol} {y}: all ZIP dates are in {y}")

        src_tx = raw[raw["State Code"] == "48"]
        f = read(ROOT / "Texas_Filtered_Data" / f"Texas_{pol}_{y}.csv")
        check(f["state_code"].eq("48").all() and f["state_name"].eq("Texas").all(),
              f"{pol} {y}: all {len(f):,} filtered records are Texas")
        check(len(f) == len(src_tx), f"{pol} {y}: filtered rows ({len(f):,}) == Texas rows in ZIP ({len(src_tx):,})")
        check(not f.duplicated(KEY).any(), f"{pol} {y}: no duplicate monitor-day records")

        # Compare original values cell by cell after aligning on the record key
        orig = src_tx.rename(columns=dict(zip(EPA_HEADER, [c for c in f.columns if c not in
                             ("site_id", "year", "pollutant", "analysis_record", "record_note")])))
        orig = orig.assign(site_id=orig["state_code"] + "-" + orig["county_code"] + "-" + orig["site_num"])
        cols = [c for c in orig.columns]
        a = orig[cols].sort_values(KEY).reset_index(drop=True).fillna("<NA>")
        b = f[cols].sort_values(KEY).reset_index(drop=True).fillna("<NA>")
        check(a.equals(b), f"{pol} {y}: every original value and date preserved unchanged")
        yearly_total += len(f)

    c = read(ROOT / "Combined_Datasets" / f"Texas_{pol}_Combined.csv")
    check(sorted(c["year"].astype(int).unique()) == YEARS, f"{pol} combined: years are exactly {YEARS}")
    check((c["date_local"].str[:4] == c["year"]).all(), f"{pol} combined: year column matches date_local")
    check(len(c) == yearly_total, f"{pol} combined: rows ({len(c):,}) == sum of yearly files ({yearly_total:,})")
    check(not c.duplicated(KEY).any(), f"{pol} combined: no duplicate records across years")
    check(c["units_of_measure"].nunique() == 1, f"{pol} combined: single unit ({c['units_of_measure'].iloc[0]})")

m = read(ROOT / "Combined_Datasets" / "Texas_PM25_Ozone_SiteDay_Merged.csv")
check(not m.duplicated(["site_id", "date_local"]).any(), "merged: one row per site per date")
for pol, col in (("PM25", "pm25_daily_mean_ugm3"), ("Ozone", "ozone_mda8_ppm")):
    c = read(ROOT / "Combined_Datasets" / f"Texas_{pol}_Combined.csv")
    sd = c[c["analysis_record"] == "TRUE"][["site_id", "date_local"]].drop_duplicates()
    check(m[col].notna().sum() == len(sd), f"merged: all {len(sd):,} {pol} site-days present (none lost)")
check(sorted(m["year"].astype(int).unique()) == YEARS, "merged: years are exactly 2020-2024")

lines.append("")
lines.append("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED")
out = "\n".join(lines)
print(out)
(ROOT / "Documentation" / "verification_results.txt").write_text(out + "\n", encoding="utf-8")
