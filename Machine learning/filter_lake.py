import os
import glob
import pandas as pd
from joblib import Parallel, delayed
import argparse
import sys
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 0. 定义单张表格过滤函数 (必须放在顶层以确保 joblib 并行安全)
# ==========================================
def filter_single_month(file_path, valid_hylaks, output_dir):
    file_name = os.path.basename(file_path)
    
    # 读取当月完整的湖泊预测表
    df = pd.read_csv(file_path)
    
    # 核心操作：通过 isin 极速保留在白名单集合(set)中的湖泊
    df_filtered = df[df['Hylak'].isin(valid_hylaks)]
    
    # 保存到新文件夹
    out_path = os.path.join(output_dir, file_name)
    df_filtered.to_csv(out_path, index=False)
    
    return file_name, len(df), len(df_filtered)

def main():
    # ==========================================
    # 1. 设置命令行参数解析
    # ==========================================
    parser = argparse.ArgumentParser(description="根据 Nature 标准白名单极速过滤全球湖泊预测表")
    
    # 路径参数 (必填)
    parser.add_argument("-i", "--input_dir", required=True, help="原始完整预测表所在的文件夹")
    parser.add_argument("-w", "--whitelist_path", required=True, help="综合白名单 CSV 文件路径")
    parser.add_argument("-o", "--output_dir", required=True, help="剔除异常湖泊后输出的新文件夹")
    
    # 性能参数 (可选)
    parser.add_argument("-j", "--n_jobs", type=int, default=64, help="并行核心数 (默认: 64)")

    args = parser.parse_args()

    input_dir = args.input_dir
    whitelist_path = args.whitelist_path
    output_dir = args.output_dir
    n_jobs = args.n_jobs

    # 基础检查
    if not os.path.exists(whitelist_path):
        print(f"❌ 错误: 找不到白名单文件 '{whitelist_path}'")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f">>> 启动全球湖泊白名单极速物理过滤引擎 <<<")
    print(f"-> 并行核心数: {n_jobs}")

    # ==========================================
    # 2. 读取白名单，提取高置信度湖泊 ID
    # ==========================================
    print("\n[Step 1] 正在加载白名单并提取合法 Hylak ID...")
    df_whitelist = pd.read_csv(whitelist_path)

    # 容错检查
    if 'Is_Whitelist' not in df_whitelist.columns or 'Hylak' not in df_whitelist.columns:
        print("❌ 错误: 白名单文件中必须包含 'Hylak' 和 'Is_Whitelist' 列！")
        sys.exit(1)

    # 只保留 Is_Whitelist == 1 的湖泊，存入哈希集合(set)以获得 O(1) 的查询速度
    valid_hylaks = set(df_whitelist[df_whitelist['Is_Whitelist'] == 1]['Hylak'])
    print(f"    - 白名单中共包含 {len(valid_hylaks)} 个高置信度湖泊。")

    # ==========================================
    # 3. 开启多核并行过滤
    # ==========================================
    print("\n[Step 2] 正在启动多核并行引擎，对所有月度表进行“瘦身”...")
    input_files = glob.glob(os.path.join(input_dir, '*.csv'))

    if not input_files:
        print(f"⚠️ 警告: 在 '{input_dir}' 中没有找到任何 CSV 文件！")
        sys.exit(0)

    # 并行处理所有表格，将 valid_hylaks 和 output_dir 显式传给 worker
    results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(filter_single_month)(f, valid_hylaks, output_dir) for f in input_files
    )

    print(f"\n==================================================")
    print(f"🎉 预测表极速瘦身与过滤大功告成！")
    print(f"-> 共处理了 {len(results)} 张月度表格。")
    print(f"-> 所有过滤后的纯净表格已存入: {output_dir}")
    print(f"-> 现在，这些表格里 100% 都是合法的白名单湖泊了！")
    print(f"==================================================")

if __name__ == "__main__":
    main()