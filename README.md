# REST Countries Project - Milestone 1

Data Engineering Lab - PSUT

## Team Members
- Yahia Fawwaz - 20250581
- Feras Yaghi - 20250578
- Joud Himo - 20250400

## About the Project
We collected data from the REST Countries API, checked for missing
values, duplicates and outliers, cleaned the data and made 5 charts.

We have 254 rows and 26 columns after cleaning.

## How to Run

Install the libraries:

```
pip install pandas requests matplotlib
```

Save your API key in api_key.txt and run:

```
python src/extract.py
python src/profiling.py
python src/clean.py
python src/visualize.py
```

## Data Cleaning
- Checked for duplicates.
- Handled missing values.
- Kept countries with missing ISO codes and flagged them.
- Kept countries with zero population.
- Used IQR to flag outliers without removing them.

The datasets are in the data folder and the results and charts
are in the reports folder.

AI usage is documented in ai-logs/milestone1.