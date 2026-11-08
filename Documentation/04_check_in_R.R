# Step 6b: Confirm every output CSV opens in R (the engine RStudio uses).
# Run from the project root in RStudio:  source("Documentation/04_check_in_R.R")
# or from a terminal:                    Rscript Documentation/04_check_in_R.R

files <- c(
  list.files("Texas_Filtered_Data", pattern = "\\.csv$", full.names = TRUE),
  list.files("Combined_Datasets", pattern = "\\.csv$", full.names = TRUE)
)

for (f in files) {
  # colClasses keeps codes such as county_code "013" as text so leading zeros survive
  hdr <- names(read.csv(f, nrows = 1))
  codes <- intersect(c("county_code", "site_num", "method_code"), hdr)
  d <- read.csv(f, colClasses = setNames(rep("character", length(codes)), codes),
                stringsAsFactors = FALSE)
  cat(sprintf("%-55s %8d rows %3d cols  years: %s\n", basename(f), nrow(d), ncol(d),
              paste(sort(unique(d$year)), collapse = ",")))
}

pm <- read.csv("Combined_Datasets/Texas_PM25_Combined.csv")
cat("\nPM2.5 analysis_record column reads as:", class(pm$analysis_record), "\n")
cat("PM2.5 arithmetic_mean reads as:", class(pm$arithmetic_mean), "\n")
cat("date_local converts to Date:", class(as.Date(pm$date_local)), "\n")
