# Analyzing Air Quality Patterns Across Texas

CSE 4334 Data Mining group project. We use EPA daily air quality data (2020–2024) for **PM2.5** and **ozone** in Texas.

## Research questions
1. How do PM2.5 and ozone levels vary across Texas locations and seasons? *(next)*
2. *TBD*
3. *TBD*

## Project status
- [x] Download EPA data and filter to Texas
- [x] Data audit (`notebooks/01_data_audit.ipynb`)
- [ ] Cleaning (`notebooks/02_data_cleaning.ipynb`) – waiting for team approval of the cleaning plan
- [ ] Research Question 1

## Folder structure
| Folder | What's inside |
|---|---|
| `Original_Datasets/` | Original EPA ZIP files – **never edit these** |
| `Texas_Filtered_Data/` | Texas rows only, one CSV per pollutant per year |
| `Combined_Datasets/` | All years stacked per pollutant, plus a PM2.5 + ozone site-day merge |
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
