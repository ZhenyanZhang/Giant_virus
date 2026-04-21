# Workflow for Machine Learning

## Step 1: Data Preparation and Feature Selection
In this step, we collected the **environmental factors** online (details can be found in the manuscript).
1. Downloaded the data from [Climate Data Store](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=overview), [HydroLAKES database](https://www.hydrosheds.org/products/hydrolakes) and [previous study](https://www.nature.com/articles/s41597-022-01284-8);
2. Extract the environmental factors for each sample based on the sampling date (accurate to month and year for the climatic factors and human footprint index, respectively) and sampling location (accurate to longitude and latitude) using the script1.factor_extract.py
