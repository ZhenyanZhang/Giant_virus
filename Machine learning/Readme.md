# Workflow for Machine Learning

## Step 1: Data Preparation and Feature Selection
In this step, we collected the **environmental factors** online (details can be found in the manuscript) and curated the metadata to extract three critical **technical covariates** for each sample.
1. Downloaded the data from [Climate Data Store](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=overview), [HydroLAKES database](https://www.hydrosheds.org/products/hydrolakes) and [previous study](https://www.nature.com/articles/s41597-022-01284-8); three critical technical covariates for each sample were extracted from the metadata of each independent study.
2. To prevent multicollinearity in the machine-earning models, we evaluated Spearman’s rank correlation among all **environmental factors** using [spearman_cor.R](spearman_cor.R). For highly correlated factors (|Spearman’s _r_| > 0.6), we exclusively retained the most representative and biologically meaningful one.

## Step 2: Machine-learning model construction and validation
We identified the most suitable algorithm and associated hyperparameters for machine learning by first constructing regression models using different algorithms (XGBoost and random forest) with different combinations of hyperparameters. After hyperparametric tuning, the best combination of hyperparameters for each algorithm and each microbial index was evaluated using the performance of the models (represented as out-of-fold R2, RMSE and MAE). To evaluate the ability of extrapolation of machine-learning models, grouped cross-validation (which grouped by sampling sites) and spatial cross-validation were also used. All these work were performed by 
