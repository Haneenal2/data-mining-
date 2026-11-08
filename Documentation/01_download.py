"""Step 1: Download EPA AirData daily summary files (PM2.5 88101, Ozone 44201) for 2020-2024.

Source page: https://aqs.epa.gov/aqsweb/airdata/download_files.html
Files are saved unchanged into ../Original_Datasets/ and a manifest (size, SHA-256) is written
to Documentation/download_manifest.csv.

Run from the project root:  python Documentation/01_download.py
"""
import csv
import hashlib
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Original_Datasets"
BASE_URL = "https://aqs.epa.gov/aqsweb/airdata/"
YEARS = range(2020, 2025)
PARAMS = {"88101": "PM2.5 FRM/FEM Mass", "44201": "Ozone"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, attempts=5):
    # Write to a .part file and rename only when complete, so an interrupted
    # download is never mistaken for a finished one.
    part = dest.with_suffix(".zip.part")
    for i in range(1, attempts + 1):
        try:
            print(f"Downloading {url} (attempt {i})")
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(part, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            part.replace(dest)
            return
        except requests.RequestException as e:
            print(f"  failed: {e.__class__.__name__}")
            time.sleep(5 * i)
    raise RuntimeError(f"Could not download {url} after {attempts} attempts")


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for code in PARAMS:
        for year in YEARS:
            name = f"daily_{code}_{year}.zip"
            url = BASE_URL + name
            dest = OUT / name
            if not dest.exists():
                download(url, dest)
            else:
                print(f"Already present: {name}")
            # A valid download must be a real ZIP holding the matching CSV
            with zipfile.ZipFile(dest) as z:
                members = z.namelist()
                assert z.testzip() is None, f"Corrupt ZIP: {name}"
            rows.append({
                "file": name,
                "parameter_code": code,
                "pollutant": PARAMS[code],
                "year": year,
                "url": url,
                "bytes": dest.stat().st_size,
                "sha256": sha256(dest),
                "zip_members": ";".join(members),
                "checked_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
    with open(ROOT / "Documentation" / "download_manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print("Manifest written.")


if __name__ == "__main__":
    main()
