import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.patches as mpatches

# Load data
data = pd.read_excel("Z:/onedrive/大病毒研究/1.gvMAG组装与筛选/新数据0731/sample_map.xlsx")

lat = np.array(data['latitude'])
lon = np.array(data['longitude'])
number = np.array(data['number'])

plt.style.use('ggplot')
plt.figure(figsize=(10, 6))

# Initialize map
map1 = Basemap(projection='robin', lat_0=90, lon_0=0,
               resolution='l', area_thresh=1000.0)

map1.drawcoastlines(linewidth=0.2)
map1.drawcountries(linewidth=0.2)
map1.drawmapboundary(fill_color='white')
map1.fillcontinents(color='lightgrey', alpha=0.8)

map1.drawmeridians(np.arange(0, 360, 60))
map1.drawparallels(np.arange(-90, 90, 30))

# Plot points
sc = map1.scatter(lon, lat, latlon=True,
             alpha=1, s=number*2, c="blue", linewidths=0, marker='o', zorder=10)

# Create legend for point sizes
sizes = [10, 20, 40, 60, 80, 100, 120]  # Example sizes
labels = [f'{size}' for size in sizes]  # Corresponding labels

for size, label in zip(sizes, labels):
   plt.scatter([], [], s=size*2, c='blue', alpha=1, label=label)

plt.legend(title="Number", loc='lower left', scatterpoints=1, fontsize=10)

plt.show()

#plt.savefig(outfigure, dpi=300)
plt.close()
