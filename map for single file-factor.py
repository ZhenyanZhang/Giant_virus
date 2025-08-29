import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

path = r"D:/onedrive/大病毒研究/polB分析流程/gv4_annual/factor_change_map.csv"  # 文件路径
files = glob.glob(path)
plt.style.use('ggplot')

for file in files:
    data = pd.read_csv(file)
    file_name = os.path.basename(file)
    file_name_without_extension = os.path.splitext(file_name)[0]
    print(f"Processing file: {file_name_without_extension}")

    # 确定需要绘制的指标列（排除ID、经纬度列）
    exclude_cols = ['Hylak', 'lat', 'long']  # 请根据实际列名修改
    plot_columns = [col for col in data.columns if col not in exclude_cols]

    # 创建3×4布局的子图（增加底部空间用于放置图例）
    fig, axes = plt.subplots(4, 3, figsize=(20, 18))  # 增加高度为20
    axes_flat = axes.flatten()  # 将二维轴数组转换为一维

    # 处理每个指标列
    for i, col in enumerate(plot_columns):
        if i >= 12:  # 最多处理12个指标（3×4布局）
            break

        ax = axes_flat[i]
        print(f"  Processing column: {col}")

        # 只保留increased和decreased的点
        filtered_data = data[data[col].isin(['increased', 'decreased'])]

        if filtered_data.empty:
            ax.set_title(f"{col}\n(No valid data)", fontsize=10)
            continue

        # 初始化地图
        map1 = Basemap(projection='cyl', lat_0=90, lon_0=0,
                       resolution='l', area_thresh=1000.0, ax=ax)

        map1.drawcoastlines(linewidth=0.2)
        map1.drawmapboundary(fill_color='white')
        map1.fillcontinents(color='lightgrey', alpha=0.5)

        # 创建颜色映射 - 只绘制increased和decreased的点
        colors = filtered_data[col].map({'increased': 'red', 'decreased': 'blue'})

        # 绘制散点
        map1.scatter(filtered_data['long'], filtered_data['lat'],
                     latlon=True, alpha=0.7, s=1,
                     c=colors, linewidths=0, marker='s', ax=ax, zorder=10)

        # 设置子图标题
        ax.set_title(col, fontsize=18, pad=10)

    # 隐藏多余的子图
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis('off')

    # 在底部创建图例（居中位置）
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, label='Increased'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', markersize=10, label='Decreased')
    ]

    # 在最下方添加图例（居中）
    fig.legend(handles=legend_elements, loc='lower center',
               ncol=2, fontsize=18, frameon=True,
               bbox_to_anchor=(0.5, 0.05))  # 位于图的底部中间

    # 调整布局 - 为底部图例留出空间
    plt.tight_layout(pad=3.0, rect=[0, 0.05, 1, 0.95])  # rect参数调整子图区域（底部留出5%空间）

    # 保存输出
    output_pdf = f"D:/onedrive/大病毒研究/polB分析流程/gv4_annual/{file_name_without_extension}_multiplot.pdf"
    plt.savefig(output_pdf, format='pdf', bbox_inches='tight')
    print(f"Saved: {output_pdf}")

    # 保存输出 - PNG格式（300dpi）
    output_png = f"D:/onedrive/大病毒研究/polB分析流程/gv4_annual/{file_name_without_extension}_multiplot.png"
    plt.savefig(output_png, format='png', bbox_inches='tight', dpi=300)
    print(f"Saved PNG: {output_png} (300 dpi)")

    # 显示并关闭
    plt.show()
    plt.close()

print("All processing completed.")