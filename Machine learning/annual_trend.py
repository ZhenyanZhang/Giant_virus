import pandas as pd
import numpy as np
from scipy.stats import t
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. Data loading
# ==========================================
input_file = "D:/PNAS_revised/annual_trend/Summary_Table3_Annual_Matrix_richness.csv"
output_file = "D:/PNAS_revised/annual_trend/richness_Significant_Lake_Trends.csv"

df = pd.read_csv(input_file)

id_col_name = df.columns[0]
year_cols = df.columns[1:]

years = np.array([int(y) for y in year_cols])
Y = df[year_cols].values.astype(float)
X = np.tile(years, (Y.shape[0], 1)).astype(float)
X[np.isnan(Y)] = np.nan

valid_n = np.sum(~np.isnan(Y), axis=1)
df_resid = valid_n - 2

print(f"-> find {len(df)} lakes for analysis...")

# ==========================================
# 2. Linear regression
# ==========================================
X_mean = np.nanmean(X, axis=1, keepdims=True)
Y_mean = np.nanmean(Y, axis=1, keepdims=True)

X_diff = X - X_mean
Y_diff = Y - Y_mean

SS_xx = np.nansum(X_diff ** 2, axis=1)
SS_xy = np.nansum(X_diff * Y_diff, axis=1)

with np.errstate(divide='ignore', invalid='ignore'):
    slopes = SS_xy / SS_xx

intercepts = np.squeeze(Y_mean) - slopes * np.squeeze(X_mean)

# ==========================================
# 3. p
# ==========================================
Y_pred = slopes[:, None] * X + intercepts[:, None]

SS_res = np.nansum((Y - Y_pred) ** 2, axis=1)

with np.errstate(divide='ignore', invalid='ignore'):
    SE_slope = np.sqrt((SS_res / df_resid) / SS_xx)

    t_stats = slopes / SE_slope

    p_values = 2 * t.sf(np.abs(t_stats), df=df_resid)

# ==========================================
# 4. annual trend (% / year)
# ==========================================
y_mean_flat = np.squeeze(Y_mean)
with np.errstate(divide='ignore', invalid='ignore'):
    annual_rate_pct = (slopes / y_mean_flat) * 100

# ==========================================
# 5. output
# ==========================================
df_result = df.copy()
df_result['Multi_Year_Mean'] = y_mean_flat
df_result['Trend_Slope'] = slopes
df_result['P_Value'] = p_values
df_result['Annual_Change_Rate_%'] = annual_rate_pct

df_significant = df_result[df_result['P_Value'] < 0.05].copy()

df_significant.to_csv(output_file, index=False)
