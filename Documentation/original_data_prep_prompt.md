I am working on a university Data Mining project (CSE 4334) titled **"Analyzing Air Quality Patterns Across Texas."**

My professor requires us to use data covering multiple years. I need you to download, organize, and prepare real air quality datasets from the official U.S. Environmental Protection Agency (EPA) website.

### 1. Download the datasets

Use the official EPA AirData website:

[https://aqs.epa.gov/aqsweb/airdata/download_files.html](https://aqs.epa.gov/aqsweb/airdata/download_files.html)

I would prefer data covering **2020–2024**, but I understand that not every pollutant, location, or year may have complete data.

We are studying:

- PM2.5 (Fine Particulate Matter), parameter code 88101
- Ground-level Ozone (O₃), parameter code 44201

Check the availability of both pollutants for each year.

**Important instructions about data availability:**

- Check whether Texas measurements exist for each pollutant and year.
- If Texas data is unavailable for a particular year, clearly tell me.
- If a year has only limited Texas data, explain what is missing.
- If another five-year period would provide better coverage, recommend it and explain why.
- Do not automatically change the selected years without asking me first.
- Do not substitute data from another state.
- Do not invent or estimate missing measurements.
- It is acceptable if some counties or monitoring stations have missing observations. Document those limitations.

I want to work with actual EPA measurements, even if the data is incomplete.

### 2. Save the files to my Desktop



Organize it into these subfolders:

- **Original_Datasets:** All original EPA ZIP files, unchanged.
- **Texas_Filtered_Data:** Individual CSV files filtered to Texas, separated by year and pollutant.
- **Combined_Datasets:** Combined CSV files containing measurements from multiple years.
- **EDA_Results:** An empty folder for our future analysis.
- **Documentation:** Reports explaining the sources, cleaning, and combining process.

Use descriptive filenames that identify the pollutant and year.

### 3. Filter and clean the data

For each dataset:

1. Extract the original CSV.
2. Filter to Texas using State Code 48.
3. Preserve the original measurement values and dates.
4. Keep relevant information such as county, city, monitoring station, date, pollutant concentration, measurement units, and AQI when available.
5. Identify missing values and duplicate records.
6. Explain any cleaning decisions.
7. Preserve valid measurements from different monitoring stations.
8. Check whether measurement methods, units, or averaging periods differ across files.

Do not delete records simply because they contain missing values. First determine whether removing them is necessary.

### 4. Combine the datasets

After filtering the files, create:

- `Texas_PM25_Combined.csv`
- `Texas_Ozone_Combined.csv`

Each file should contain all available observations from the selected years.

Include a Year column so we can compare pollution levels over time.

If appropriate, you may also create a combined PM2.5 and ozone dataset for analyses that require both pollutants.

**Be careful when combining data:**

- Do not accidentally duplicate records.
- Do not lose valid measurements.
- Do not mix incompatible measurement units.
- Do not assume two observations come from the same monitoring station simply because they are in the same county.
- If merging the pollutants, match records using appropriate geographic and date information.
- Clearly distinguish between stacking yearly datasets and merging different pollutants.
- Explain how you handled missing dates or locations.
- Preserve the original data in case we need to verify anything.

### 5. Write a detailed data preparation report

This is very important.

Inside the Documentation folder, create a report named:

**Data_Preparation_and_Combining_Report.md**

I want a detailed, student-friendly explanation of everything you did.

The report must include:

**A. Data sources**

- The official EPA source URLs
- The selected years
- The pollutants
- The original filenames

**B. Data availability**

- Which years contain Texas measurements
- Whether both pollutants are available
- Which counties or stations have missing data
- Any years with limited observations
- Any recommended alternative years and the reasons

**C. Cleaning process**

Explain step by step:

- How you filtered for Texas
- Which columns you kept
- How you identified missing values
- How you handled duplicates
- Whether any records were removed and why
- Whether measurement units or methods required special handling

**D. Combining process**

Explain exactly how you combined the datasets.

Include:

1. Which files were combined.
2. Which columns were used.
3. Whether you appended rows or joined tables.
4. Which keys were used for any joins.
5. How you handled missing or unmatched records.
6. How you avoided duplicates.
7. How you verified that the combined dataset was correct.

Include a small example showing how records from different years were combined.

**E. Dataset statistics**

Create a summary table containing:

| Year | Pollutant | Original Records | Texas Records | Records Retained |
| ---- | --------- | ---------------- | ------------- | ---------------- |

Also report the total number of observations in each combined dataset.

**F. Limitations**

Explain any problems with missing measurements, incomplete geographic coverage, different monitoring stations, or inconsistent measurement methods.

**G. Reproducibility**

Include the exact code or commands used to download, filter, clean, and combine the datasets.

Save any scripts in the Documentation folder so we can reproduce the results.

The report should be detailed enough that I can understand the process and explain it to my professor.

### 6. Verify the results

Before finishing:

- Confirm that every downloaded file contains actual EPA data.
- Confirm that all filtered records are from Texas.
- Confirm that the combined files contain the intended years.
- Compare record counts before and after combining.
- Verify that no observations were unintentionally lost or duplicated.
- Make sure the CSV files can be opened in RStudio.
- Clearly identify any steps that could not be completed.

### 7. Final deliverables

I want:

1. Original EPA datasets.
2. Texas-filtered datasets.
3. Combined multi-year datasets.
4. A detailed data preparation and combining report.
5. Reproducible scripts.
6. A summary of data availability and record counts.

**Do not start EDA, clustering, PCA, regression, or classification yet.**

First, complete the dataset preparation and documentation.

If Texas data is missing for any requested year, investigate alternative years and present your recommendation to me before changing the date range.

If you can access my Desktop, save everything in the specified folder. Otherwise, tell me what access is missing and provide an alternative way to create the files.

Once finished, show me exactly what you created and explain any issues you encountered.
