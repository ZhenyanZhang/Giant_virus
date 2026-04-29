import os
import glob
import pandas as pd
from joblib import Parallel, delayed
import argparse
import sys
import warnings

warnings.filterwarnings('ignore')

def filter_single_file(file_path, valid_hylaks, output_dir):
    file_name = os.path.basename(file_path)
    
    df = pd.read_csv(file_path)

    df_filtered = df[df['Hylak'].isin(valid_hylaks)]

    out_path = os.path.join(output_dir, file_name)
    df_filtered.to_csv(out_path, index=False)
    
    return file_name, len(df), len(df_filtered)

def main():
    parser = argparse.ArgumentParser(description="filter lakes for predicting based on the whitelist")
    
    parser.add_argument("-i", "--input_dir", required=True, help="originial dir")
    parser.add_argument("-w", "--whitelist_path", required=True, help="whitelist file")
    parser.add_argument("-o", "--output_dir", required=True, help="filtered file")
    parser.add_argument("-j", "--n_jobs", type=int, default=64, help="number of job")

    args = parser.parse_args()

    input_dir = args.input_dir
    whitelist_path = args.whitelist_path
    output_dir = args.output_dir
    n_jobs = args.n_jobs

    if not os.path.exists(whitelist_path):
        print(f"erro: connot find '{whitelist_path}'")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    df_whitelist = pd.read_csv(whitelist_path)

    valid_hylaks = set(df_whitelist[df_whitelist['Is_Whitelist'] == 1]['Hylak'])

    input_files = glob.glob(os.path.join(input_dir, '*.csv'))

    if not input_files:
        print(f"erro: connot find files in '{input_dir}'")
        sys.exit(0)

    
    results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(filter_single_file)(f, valid_hylaks, output_dir) for f in input_files
    )


if __name__ == "__main__":
    main()
