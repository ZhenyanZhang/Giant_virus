import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
import matplotlib.patches as mpatches
import os

data=pd.read_excel("D:/onedrive/大病毒研究/polB分析流程/gv5_host&carbon/reanalyzed0815/POC.xlsx")

lat = np.array(data['Latitude'])
lon = np.array(data['Longitude'])
Cluster = np.array(data['group'])

plt.style.use('ggplot')
plt.figure(figsize=(10, 6))

# 设置中国区域的经纬度范围
map1 = Basemap(projection='cyl',
               llcrnrlon=70,   # 左下角经度
               llcrnrlat=0,   # 左下角纬度
               urcrnrlon=140,  # 右上角经度
               urcrnrlat=60,   # 右上角纬度
               resolution='l',
               area_thresh=1000.0)

# 调整经纬线间隔和标签
#map1.drawmeridians(np.arange(70, 136, 10), labels=[0,0,0,1])  # 经度范围70-135，间隔10度
#map1.drawparallels(np.arange(15, 55, 5), labels=[1,0,0,0])    # 纬度范围15-54，间隔5度

#map1.drawcoastlines(linewidth=0.5)
#map1.drawcountries(linewidth=0.5, color='black')  # 绘制国界线
#map1.drawmapboundary(fill_color='white')
#map1.fillcontinents(color='lightgrey', alpha=0.8)

# 自定义绘制中国边界（通过重复绘制边界线加粗）
for _ in range(1):  # 多次绘制边界线使其更清晰
    map1.readshapefile('D:/onedrive/大病毒研究/polB分析流程/gv5_host&carbon/china/china_shp/china_shp2', 'china', linewidth=0.8, color='black')
for _ in range(1):  # 多次绘制边界线使其更清晰
    map1.readshapefile('D:/onedrive/大病毒研究/polB分析流程/gv5_host&carbon/china/china_shp/china_shp', 'china', linewidth=0.8, color='black')

cm = mpl.colors.ListedColormap(['lightgreen','blue'])

map1.scatter(lon, lat, latlon=True,
                alpha=1, s=1, c=Cluster,cmap=cm, linewidths=0, marker='s')

# create legend
NA = mpatches.Patch(color='lightgreen', label='NA')
RICH = mpatches.Patch(color='blue', label='RICH')
#DIS = mpatches.Patch(color='mediumpurple', label='DIS')
#BOTH = mpatches.Patch(color='red', label='BOTH')
plt.legend(handles=[NA,RICH], title='CAHNGE_PATTERN',loc=1)

# 保存为 PDF 文件
#output_pdf = f"D:/onedrive/大病毒研究/polB分析流程/gv5_host&carbon/china/doc_all_map.pdf"
#plt.savefig(output_pdf, format='pdf', bbox_inches='tight')

plt.show()
plt.close()