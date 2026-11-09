# Analyzing Air Quality Patterns Across Texas

CSE 4334 Data Mining group project. We use EPA daily air quality data (2020–2024) for **PM2.5** and **ozone** in Texas.

## Research questions
1. How do PM2.5 and ozone levels vary across Texas locations and seasons? *(next)*
2. Can we use historical air quality data to predict pollutant concentrations? (linear regression – `notebooks/04_rq2_regression.ipynb`)
3. *TBD*

## Project status
- [x] Download EPA data and filter to Texas
- [x] Data audit (`notebooks/01_data_audit.ipynb`)
- [x] Cleaning and EDA (`notebooks/02_data_cleaning.ipynb`)
- [ ] Research Question 1
- [x] Research Question 2 – regression (`notebooks/04_rq2_regression.ipynb`, figures in `EDA_Results/RQ2_regression/`)

## Folder structure
| Folder | What's inside |
|---|---|
| `Original_Datasets/` | Original EPA ZIP files – **never edit these** |
| `Texas_Filtered_Data/` | Texas rows only, one CSV per pollutant per year |
| `Combined_Datasets/` | All years stacked per pollutant, plus a PM2.5 + ozone site-day merge |
| `Cleaned_Data/` | **Use these for analysis** – one row per site per day for PM2.5 and ozone |
| `notebooks/` | Our Jupyter notebooks (run them in order) |
| `EDA_Results/` | Figures and tables from the analysis |
| `Documentation/` | Scripts used to download/filter/combine, stats tables, verification log |

## Data source
EPA AirData daily summary files: https://aqs.epa.gov/aqsweb/airdata/download_files.html
- PM2.5 FRM/FEM Mass – parameter code `88101`
- Ozone – parameter code `44201`

## How to run
```bash
pip install -r requirements.txt
jupyter notebook
```
Open the notebooks from the `notebooks/` folder.

**Loading tip:** read the CSVs with
`pd.read_csv(path, keep_default_na=False, na_values=[""])`
otherwise pandas turns EPA's `event_type = "None"` into missing values.
