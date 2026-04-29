import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import joblib
from sklearn.preprocessing import OrdinalEncoder


input_dir = 'predict'
output_dir = 'predict/SHAP_Analysis_Results'
os.makedirs(output_dir, exist_ok=True)

data_path = 'predict/data_for_ml.txt'
df = pd.read_csv(data_path, sep='\t')

df_encoded = df.copy()

size_order = ['FL-', 'FL', 'FL_HOST-', 'FL_HOST', 'FL+_HOST', 'HOST']
depth_order = ['Epilimnion', 'Metalimnion', 'Hypolimnion', 'MIX'] 

encoder_ordered = OrdinalEncoder(categories=[size_order, depth_order])
df_encoded[['size_group', 'depth_group']] = encoder_ordered.fit_transform(df[['size_group', 'depth_group']])

encoder_platform = OrdinalEncoder(categories='auto')
df_encoded[['PLATFORM']] = encoder_platform.fit_transform(df[['PLATFORM']])

feature_cols = joblib.load(os.path.join(input_dir, 'Training_Feature_Columns.joblib'))
X = df_encoded[feature_cols]

targets = ['dissimilarity', 'richness']

for target_name in targets:
    print(f"\n==================================================")
    print(f"shap for {target_name}...")
    print(f"==================================================")

    model_path = os.path.join(input_dir, f'Final_Random_Model_{target_name}.joblib')
    if not os.path.exists(model_path):
        print(f"cannot find {model_path}")
        continue
    
    model = joblib.load(model_path)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X, check_additivity=False)

    if isinstance(shap_values, list):
        shap_values = shap_values[1] 

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X, plot_type="bar", show=False, max_display=15, color='#4575b4')
    plt.title(f'Global Feature Importance (SHAP) - {target_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{target_name}_SHAP_Bar_Plot.pdf'), dpi=300)
    plt.close()


    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    
    feature_importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'Mean_Abs_SHAP': mean_abs_shap
    }).sort_values(by='Mean_Abs_SHAP', ascending=False)

    csv_path = os.path.join(output_dir, f'{target_name}_SHAP_Feature_Importance.csv')
    feature_importance_df.to_csv(csv_path, index=False)
    
