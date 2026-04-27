import os
import glob
import joblib
import numpy as np
import pandas as pd
from scipy.stats import chi2
from scipy.spatial.distance import cdist
from joblib import Parallel, delayed
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. Data Loading
# ==========================================
train_data_path = 'data_for_ml.txt'
feature_cols_path = 'Training_Feature_Columns.joblib'
original_dir = 'original_dataset'
output_masks_dir = 'Monthly_Mahalanobis_Masks'
output_whitelist = 'Global_Lakes_Whitelist.csv'

FREQUENCY_THRESHOLD = 0.50
N_JOBS = 64
os.makedirs(output_masks_dir, exist_ok=True)

df_train = pd.read_csv(train_data_path, sep='\t')
target_features = joblib.load(feature_cols_path)

tech_factors = ['size_group', 'depth_group', 'PLATFORM']
env_features = [f for f in target_features if f not in tech_factors]
X_train_env = df_train[env_features].values

# ==========================================
# 2. environmental boundary identification
# ==========================================
centroid = np.mean(X_train_env, axis=0)

cov_matrix = np.cov(X_train_env, rowvar=False)
inv_cov_matrix = np.linalg.pinv(cov_matrix)

df_degrees = len(env_features)
chi2_threshold_sq = chi2.ppf(0.90, df_degrees)
mahalanobis_threshold = np.sqrt(chi2_threshold_sq)

print(f"\n environmental boundary:")
print(f"    - degrees of freedom: {df_degrees}")
print(f"    - threshold of mahalanobis distance: {mahalanobis_threshold:.4f}")

# ==========================================
# 3. environmental outlier identification
# ==========================================
def process_single_month(file_path):
    file_name = os.path.basename(file_path)
    df_pred = pd.read_csv(file_path)
    X_pred_env = df_pred[env_features].values

    dists = cdist(X_pred_env, [centroid], metric='mahalanobis', VI=inv_cov_matrix).flatten()
    
    is_valid = (dists <= mahalanobis_threshold).astype(int)
    
    df_mask = pd.DataFrame({
        'Hylak': df_pred['Hylak'],
        'Is_Valid': is_valid
    })
    
    out_mask_path = os.path.join(output_masks_dir, f"mask_{file_name}")
    df_mask.to_csv(out_mask_path, index=False)
    
    return pd.Series(is_valid, index=df_pred['Hylak'])

pred_files = glob.glob(os.path.join(original_dir, '*.csv'))

results = Parallel(n_jobs=N_JOBS, verbose=10)(
    delayed(process_single_month)(f) for f in pred_files
)

# ==========================================
# 4. Statistics
# ==========================================
pass_counts = sum(results)
total_files = len(pred_files)
pass_rate = pass_counts / total_files

whitelist_hylaks = pass_rate[pass_rate >= FREQUENCY_THRESHOLD].index

df_whitelist = pd.DataFrame({
    'Hylak': pass_rate.index,
    'Pass_Rate': pass_rate.values,
    'Is_Whitelist': (pass_rate >= FREQUENCY_THRESHOLD).astype(int)
})

df_whitelist.to_csv(output_whitelist, index=False)