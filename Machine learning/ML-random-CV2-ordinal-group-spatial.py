import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import ParameterGrid, KFold, GroupKFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.cluster import KMeans
from xgboost import XGBRegressor
import warnings
import joblib

warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# 1. Data loading and preparing
# ---------------------------------------------------------
print("1. Data loading...")
data_path = 'data_for_ml.txt'
df = pd.read_csv(data_path, sep='\t')

print("-> OrdinalEncoder performing...")
df_encoded = df.copy()
size_order = ['FL-', 'FL', 'FL_HOST-', 'FL_HOST', 'FL+_HOST', 'HOST']
depth_order = ['Epilimnion', 'Metalimnion', 'Hypolimnion', 'MIX']
encoder_ordered = OrdinalEncoder(categories=[size_order, depth_order])
df_encoded[['size_group', 'depth_group']] = encoder_ordered.fit_transform(df[['size_group', 'depth_group']])

encoder_platform = OrdinalEncoder(categories='auto')
df_encoded[['PLATFORM']] = encoder_platform.fit_transform(df[['PLATFORM']])
print("OrdinalEncoder finished")

# -------------------------------------------------
# 2. Getting ID for grouped CV and spatial CV
# -------------------------------------------------
print("-> Group ID generating...")
df_encoded['Site_ID'] = df_encoded['Latitude'].astype(str) + "_" + df_encoded['Longitude'].astype(str)
le_site = LabelEncoder()
df_encoded['group_id'] = le_site.fit_transform(df_encoded['Site_ID'])
groups = df_encoded['group_id'].values

print("-> Spatial Group ID generating...")
coords = df_encoded[['Latitude', 'Longitude']].values
kmeans = KMeans(n_clusters=10, random_state=911)
df_encoded['spatial_group_id'] = kmeans.fit_predict(coords)
spatial_groups = df_encoded['spatial_group_id'].values

# ---------------------------------------------------------
# 3. Features defining
# ---------------------------------------------------------
feature_cols = [col for col in df_encoded.columns if col not in
                ['sample', 'richness', 'dissimilarity', 'Latitude', 'Longitude', 'Site_ID', 'group_id', 'spatial_group_id']]
X = df_encoded[feature_cols].values

targets = ['richness', 'dissimilarity']

output_dir = 'CV_Results'
os.makedirs(output_dir, exist_ok=True)

joblib.dump(feature_cols, os.path.join(output_dir, 'Training_Feature_Columns.joblib'))

# ---------------------------------------------------------
# 4. Hyperparameter Tuning via Grid Search
# ---------------------------------------------------------
PARAM_GRID = [
    {
        'model_type': ['XGBoost'],
        'n_estimators': [300, 500, 800],
        'max_depth': [3, 5, 6],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.8],
        'colsample_bytree': [0.6, 0.8]
    },
    {
        'model_type': ['RandomForest'],
        'n_estimators': [300, 500],
        'max_depth': [None, 10, 20],
        'max_features': [0.6, 0.8],
        'min_samples_leaf': [1, 2, 4]
    }
]

grid_list = []
for p_dict in PARAM_GRID:
    grid_list.extend(list(ParameterGrid(p_dict)))

def calc_metrics(y_t, y_p):
    return r2_score(y_t, y_p), np.sqrt(mean_squared_error(y_t, y_p)), mean_absolute_error(y_t, y_p)

# defining Random K-Fold CV and grouped CV
rkf = KFold(n_splits=10, shuffle=True, random_state=911)
gkf = GroupKFold(n_splits=10)

# =========================================================
# 5. Hyperparameter Tuning and random CV
# =========================================================
for target_name in targets:
    print(f"\n==================================================")
    print(f"Random CV for {target_name}...")
    print(f"==================================================")

    y_raw = df_encoded[target_name].values

    if target_name == 'richness':
        y_model = np.sqrt(y_raw)
    else:
        y_model = y_raw

    best_score = -float('inf')
    best_params = None
    best_model_name = ""

    print(f"-> Performing 10-Fold Random CV with hyperparameter tuning...")

    for params in grid_list:
        m_type = params['model_type']
        kwargs = {k: v for k, v in params.items() if k != 'model_type'}

        if m_type == 'XGBoost':
            model = XGBRegressor(random_state=911, n_jobs=64, **kwargs)
        else:
            model = RandomForestRegressor(random_state=911, n_jobs=64, **kwargs)

        fold_r2s = []

        for train_idx, test_idx in rkf.split(X):
            model.fit(X[train_idx], y_model[train_idx])
            preds_transformed = model.predict(X[test_idx])

            if target_name == 'richness':
                preds = preds_transformed ** 2
            else:
                preds = preds_transformed

            fold_r2s.append(r2_score(y_raw[test_idx], preds))

        avg_r2 = np.mean(fold_r2s)
        if avg_r2 > best_score:
            best_score = avg_r2
            best_params = params
            best_model_name = m_type

    print(f"\n   {target_name} Hyperparameter Tuning finished ！")
    print(f"   Best algorithm: {best_model_name}")
    print(f"   Best hyperparameters: {best_params}")

    #----------------------------------------------------------
    # 6. OOF validation
    #----------------------------------------------------------
    print(f"\n-> OOF validation...")
    final_kwargs = {k: v for k, v in best_params.items() if k != 'model_type'}
    if best_model_name == 'XGBoost':
        eval_model = XGBRegressor(random_state=911, n_jobs=64, **final_kwargs)
    else:
        eval_model = RandomForestRegressor(random_state=911, n_jobs=64, **final_kwargs)

    oof_predictions = np.zeros(len(y_raw))
    fold_metrics = []
    distribution_data = []  

    fold_idx = 1
    for train_idx, test_idx in rkf.split(X):
        for val in y_raw[train_idx]:
            distribution_data.append({'Fold': f'Fold {fold_idx}', 'Dataset': 'Train', 'Value': val})
        for val in y_raw[test_idx]:
            distribution_data.append({'Fold': f'Fold {fold_idx}', 'Dataset': 'Test', 'Value': val})

        eval_model.fit(X[train_idx], y_model[train_idx])
        preds_transformed = eval_model.predict(X[test_idx])

        if target_name == 'richness':
            preds = preds_transformed ** 2
        else:
            preds = preds_transformed

        oof_predictions[test_idx] = preds

        r2, rmse, mae = calc_metrics(y_raw[test_idx], preds)
        fold_metrics.append({'Target': target_name, 'Random_Fold': fold_idx, 'R2': r2, 'RMSE': rmse, 'MAE': mae})
        print(f"   - Fold {fold_idx}: R2 = {r2:.3f}, RMSE = {rmse:.3f}, MAE = {mae:.3f}")
        fold_idx += 1

    pd.DataFrame(fold_metrics).to_csv(os.path.join(output_dir, f'{target_name}_random_fold_metrics.csv'), index=False)

    oof_r2, oof_rmse, oof_mae = calc_metrics(y_raw, oof_predictions)
    print(f"\n   >>> {target_name} Random OOF results <<<")
    print(f"   OOF R2:   {oof_r2:.4f}")
    print(f"   OOF RMSE: {oof_rmse:.4f}")
    print(f"   OOF MAE:  {oof_mae:.4f}")

    # ---------------------------------------------------------
    # 7. OOF ploting
    # ---------------------------------------------------------
    plt.figure(figsize=(7, 6))
    df_plot = pd.DataFrame({'Observed': y_raw, 'Predicted': oof_predictions})
    sns.scatterplot(data=df_plot, x='Predicted', y='Observed', color='#e41a1c', alpha=0.6, edgecolor='w', s=60)
    min_val = min(y_raw.min(), oof_predictions.min())
    max_val = max(y_raw.max(), oof_predictions.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', lw=2, label='1:1 Line')

    textstr = '\n'.join((
        f'Algorithm: {best_model_name}',
        f'$Random\\ CV\\ R^2$ = {oof_r2:.3f}',
        f'RMSE = {oof_rmse:.3f}',
        f'MAE = {oof_mae:.3f}'
    ))
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
    plt.gca().text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=11, verticalalignment='top', bbox=props)
    plt.title(f'Global Interpolation (Random CV) - {target_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted Value (Out-of-Fold)', fontsize=12)
    plt.ylabel('Observed Value (Actual)', fontsize=12)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{target_name}_OOF_Random_Validation.pdf'), dpi=300)
    plt.close()

    # ------------------------------------------------------------------------------
    # 8. Final Modeling with the best combinations of algorithm and hyperparameters
    # ------------------------------------------------------------------------------
    final_model = eval_model.fit(X, y_model)
    model_filename = os.path.join(output_dir, f'Final_Random_Model_{target_name}.joblib')
    joblib.dump(final_model, model_filename)

    param_filename = os.path.join(output_dir, f'Best_Parameters_{target_name}.txt')
    with open(param_filename, 'w') as f:
        f.write(f"Target: {target_name}\n")
        f.write(f"Best Algorithm: {best_model_name}\n")
        f.write("Best Hyperparameters:\n")
        for k, v in best_params.items():
            f.write(f"  {k}: {v}\n")

    # --------------------------
    # 9. Performing Grouped CV
    # --------------------------
    print(f"\n-> Performing Grouped CV with the best combinations of algorithm and hyperparameters...")
    
    oof_preds_group = np.zeros(len(y_raw))
    fold_metrics_group = []

    fold_idx = 1
    for train_idx, test_idx in gkf.split(X, y_model, groups):
        if best_model_name == 'XGBoost':
            group_eval_model = XGBRegressor(random_state=911, n_jobs=64, **final_kwargs)
        else:
            group_eval_model = RandomForestRegressor(random_state=911, n_jobs=64, **final_kwargs)

        group_eval_model.fit(X[train_idx], y_model[train_idx])
        preds_transformed = group_eval_model.predict(X[test_idx])

        if target_name == 'richness':
            preds = preds_transformed ** 2
        else:
            preds = preds_transformed

        oof_preds_group[test_idx] = preds

        r2, rmse, mae = calc_metrics(y_raw[test_idx], preds)
        fold_metrics_group.append({'Target': target_name, 'Group_Fold': fold_idx, 'R2': r2, 'RMSE': rmse, 'MAE': mae})
        print(f"   - Group Fold {fold_idx}: R2 = {r2:.3f}, RMSE = {rmse:.3f}, MAE = {mae:.3f}")
        fold_idx += 1

    pd.DataFrame(fold_metrics_group).to_csv(os.path.join(output_dir, f'{target_name}_group_fold_metrics.csv'), index=False)

    oof_r2_g, oof_rmse_g, oof_mae_g = calc_metrics(y_raw, oof_preds_group)
    print(f"\n   >>> {target_name} Group OOF results <<<")
    print(f"   OOF R2:   {oof_r2_g:.4f}")
    print(f"   OOF RMSE: {oof_rmse_g:.4f}")
    print(f"   OOF MAE:  {oof_mae_g:.4f}")

    plt.figure(figsize=(7, 6))
    df_plot_g = pd.DataFrame({'Observed': y_raw, 'Predicted': oof_preds_group})
    sns.scatterplot(data=df_plot_g, x='Predicted', y='Observed', color='#377eb8', alpha=0.6, edgecolor='w', s=60)
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', lw=2, label='1:1 Line')

    textstr_g = '\n'.join((
        f'Algorithm: {best_model_name}',
        f'$Grouped\\ CV\\ R^2$ = {oof_r2_g:.3f}',
        f'RMSE = {oof_rmse_g:.3f}',
        f'MAE = {oof_mae_g:.3f}'
    ))
    plt.gca().text(0.05, 0.95, textstr_g, transform=plt.gca().transAxes, fontsize=11, verticalalignment='top', bbox=props)
    plt.title(f'Site-level Extrapolation (Grouped CV) - {target_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted Value (Out-of-Fold)', fontsize=12)
    plt.ylabel('Observed Value (Actual)', fontsize=12)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{target_name}_OOF_Group_Validation.pdf'), dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # 10. Performing spatial CV
    # ---------------------------------------------------------
    print(f"\n-> Performing spatial CV with the best combinations of algorithm and hyperparameters...")
    
    oof_preds_spatial = np.zeros(len(y_raw))
    fold_metrics_spatial = []
    gkf_spatial = GroupKFold(n_splits=10)

    fold_idx = 1
    for train_idx, test_idx in gkf_spatial.split(X, y_model, spatial_groups):
        if best_model_name == 'XGBoost':
            spatial_eval_model = XGBRegressor(random_state=911, n_jobs=64, **final_kwargs)
        else:
            spatial_eval_model = RandomForestRegressor(random_state=911, n_jobs=64, **final_kwargs)

        spatial_eval_model.fit(X[train_idx], y_model[train_idx])
        preds_transformed = spatial_eval_model.predict(X[test_idx])

        if target_name == 'richness':
            preds = preds_transformed ** 2
        else:
            preds = preds_transformed

        oof_preds_spatial[test_idx] = preds

        r2, rmse, mae = calc_metrics(y_raw[test_idx], preds)
        fold_metrics_spatial.append({'Target': target_name, 'Spatial_Fold': fold_idx, 'R2': r2, 'RMSE': rmse, 'MAE': mae})
        print(f"   - Spatial Fold {fold_idx}: R2 = {r2:.3f}, RMSE = {rmse:.3f}, MAE = {mae:.3f}")
        fold_idx += 1

    pd.DataFrame(fold_metrics_spatial).to_csv(os.path.join(output_dir, f'{target_name}_spatial_fold_metrics.csv'), index=False)

    oof_r2_s, oof_rmse_s, oof_mae_s = calc_metrics(y_raw, oof_preds_spatial)
    print(f"\n   >>> {target_name} Spatial OOF results <<<")
    print(f"   OOF R2:   {oof_r2_s:.4f}")
    print(f"   OOF RMSE: {oof_rmse_s:.4f}")
    print(f"   OOF MAE:  {oof_mae_s:.4f}")

    plt.figure(figsize=(7, 6))
    df_plot_s = pd.DataFrame({'Observed': y_raw, 'Predicted': oof_preds_spatial})

    sns.scatterplot(data=df_plot_s, x='Predicted', y='Observed', color='#4daf4a', alpha=0.6, edgecolor='w', s=60)
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', lw=2, label='1:1 Line')

    textstr_s = '\n'.join((
        f'Algorithm: {best_model_name}',
        f'$Spatial\\ CV\\ R^2$ = {oof_r2_s:.3f}',
        f'RMSE = {oof_rmse_s:.3f}',
        f'MAE = {oof_mae_s:.3f}'
    ))
    plt.gca().text(0.05, 0.95, textstr_s, transform=plt.gca().transAxes, fontsize=11, verticalalignment='top', bbox=props)
    plt.title(f'Spatial Block Extrapolation (Spatial CV) - {target_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted Value (Out-of-Fold)', fontsize=12)
    plt.ylabel('Observed Value (Actual)', fontsize=12)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{target_name}_OOF_Spatial_Validation.pdf'), dpi=300)
    plt.close()

    print(f"--------------------------------------------------\n")

print("All finished!!!")