import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.utils import resample
from sklearn.preprocessing import OrdinalEncoder
import argparse
import warnings

warnings.filterwarnings('ignore')

def main():
    parser = argparse.ArgumentParser(description="script for predicting")
    
    parser.add_argument("-t", "--train_data", required=True, help="dataset for modeling")
    parser.add_argument("-m", "--base_model", required=True, help="best models for richness or dissimilarity")
    parser.add_argument("-f", "--feature_cols", required=True, help="feature")
    parser.add_argument("-i", "--input_file", required=True, help="file for predicting")
    parser.add_argument("-o", "--output_file", required=True, help="prediction result")
    parser.add_argument("-c", "--target_col", required=True, help="richness or dissimilarity")

    args = parser.parse_args()

    N_BOOTSTRAPS = 99


    df_train = pd.read_csv(args.train_data, sep='\t')
    target_features = joblib.load(args.feature_cols)

    size_order = ['FL-', 'FL', 'FL_HOST-', 'FL_HOST', 'FL+_HOST', 'HOST'] 
    depth_order = ['Epilimnion', 'Metalimnion', 'Hypolimnion', 'MIX'] 
    encoder_ordered = OrdinalEncoder(categories=[size_order, depth_order])
    df_train[['size_group', 'depth_group']] = encoder_ordered.fit_transform(df_train[['size_group', 'depth_group']])

    encoder_platform = OrdinalEncoder(categories='auto')
    df_train[['PLATFORM']] = encoder_platform.fit_transform(df_train[['PLATFORM']])

    X_train = df_train[target_features].values
    y_train = df_train[args.target_col].values

    base_model = joblib.load(args.base_model)
    best_params = base_model.get_params()


    expert_committee = []

    for i in range(N_BOOTSTRAPS):
        if (i+1) % 20 == 0:
            print(f"    - {i+1}/{N_BOOTSTRAPS} iterations finished...")

        X_res, y_res = resample(X_train, y_train, random_state=i)

        clone_model = xgb.XGBRegressor(**best_params)
        clone_model.fit(X_res, y_res)
        expert_committee.append(clone_model)

    df_pred = pd.read_csv(args.input_file)

    os.makedirs(os.path.dirname(args.output_file) or '.', exist_ok=True)

    X_pred = df_pred[target_features].values
    predictions_matrix = np.zeros((len(df_pred), N_BOOTSTRAPS))

    for i, expert in enumerate(expert_committee):
        predictions_matrix[:, i] = expert.predict(X_pred)

    predictions_matrix = np.clip(predictions_matrix, a_min=0, a_max=None)

    # calculating
    df_pred[f'{args.target_col}_Mean'] = np.mean(predictions_matrix, axis=1)
    q75 = np.percentile(predictions_matrix, 75, axis=1)
    q25 = np.percentile(predictions_matrix, 25, axis=1)
    df_pred[f'{args.target_col}_Uncertainty_IQR'] = q75 - q25
    df_pred[f'{args.target_col}_Relative_IQR'] = df_pred[f'{args.target_col}_Uncertainty_IQR'] / df_pred[f'{args.target_col}_Mean'].replace({0: np.nan})

    cols_to_keep = ['Hylak', f'{args.target_col}_Mean', f'{args.target_col}_Uncertainty_IQR', f'{args.target_col}_Relative_IQR']
    df_slim = df_pred[cols_to_keep]

    df_slim.to_csv(args.output_file, index=False)

if __name__ == "__main__":
    main()