import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# 充电站类型颜色映射（L1, L2, DC 快充）
charging_colors = {
    "L1": "blue",
    "L2": "green",
    "DC": "red"
}

# 判断充电站类型（优先级：DC > L2 > L1）
def get_charger_type(row):
    if row["EV DC Fast Count"] > 0:
        return "DC"
    elif row["EV Level2 EVSE Num"] > 0:
        return "L2"
    elif row["EV Level1 EVSE Num"] > 0:
        return "L1"
    return None

df["Charger Type"] = df.apply(get_charger_type, axis=1)

# 过滤掉没有充电类型的数据
df_filtered = df.dropna(subset=["Charger Type"])

# 选择点样式（星标 = Private, 圆点 = Public）
df_filtered["Marker"] = np.where(df_filtered["Groups With Access Code"] == "Private", "*", "o")

# 生成地图
fig = plt.figure(figsize=(14, 8))
ax_main = fig.add_subplot(1, 1, 1)

# 主地图（美国本土）
m_main = Basemap(projection="merc", llcrnrlat=24, urcrnrlat=50, llcrnrlon=-125, urcrnrlon=-66, resolution="l", ax=ax_main)
m_main.drawcoastlines()
m_main.drawcountries()
m_main.drawstates()
m_main.fillcontinents(color="lightgray", lake_color="lightblue")
m_main.drawmapboundary(fill_color="lightblue")

# 绘制充电站（美国本土）
for charger_type, color in charging_colors.items():
    df_subset = df_filtered[df_filtered["Charger Type"] == charger_type]
    x, y = m_main(df_subset["Longitude"], df_subset["Latitude"])
    for marker in ["o", "*"]:  # Public (o), Private (*)
        df_marker = df_subset[df_subset["Marker"] == marker]
        xm, ym = m_main(df_marker["Longitude"], df_marker["Latitude"])
        m_main.scatter(xm, ym, s=10 if marker == "o" else 20, color=color, alpha=0.6, marker=marker, label=f"{charger_type} ({'Private' if marker == '*' else 'Public'})")

# 阿拉斯加地图（左下角，对齐比例）
ax_ak = plt.axes([0.02, 0.05, 0.2, 0.2])
m_ak = Basemap(projection="merc", llcrnrlat=50, urcrnrlat=72, llcrnrlon=-170, urcrnrlon=-130, resolution="l", ax=ax_ak)
m_ak.drawcoastlines()
m_ak.drawcountries()
m_ak.drawstates()
m_ak.fillcontinents(color="lightgray", lake_color="lightblue")
m_ak.drawmapboundary(fill_color="lightblue")

# 绘制充电站（阿拉斯加）
df_ak = df_filtered[(df_filtered["Latitude"] > 50) & (df_filtered["Longitude"] < -130)]
for charger_type, color in charging_colors.items():
    df_subset = df_ak[df_ak["Charger Type"] == charger_type]
    x, y = m_ak(df_subset["Longitude"], df_subset["Latitude"])
    m_ak.scatter(x, y, s=5, color=color, alpha=0.6, marker="o")

# 夏威夷地图（左下角，对齐比例）
ax_hi = plt.axes([0.25, 0.05, 0.15, 0.15])
m_hi = Basemap(projection="merc", llcrnrlat=18, urcrnrlat=22, llcrnrlon=-161, urcrnrlon=-154, resolution="l", ax=ax_hi)
m_hi.drawcoastlines()
m_hi.drawcountries()
m_hi.drawstates()
m_hi.fillcontinents(color="lightgray", lake_color="lightblue")
m_hi.drawmapboundary(fill_color="lightblue")

# 绘制充电站（夏威夷）
df_hi = df_filtered[(df_filtered["Latitude"] > 18) & (df_filtered["Latitude"] < 22) & (df_filtered["Longitude"] < -154)]
for charger_type, color in charging_colors.items():
    df_subset = df_hi[df_hi["Charger Type"] == charger_type]
    x, y = m_hi(df_subset["Longitude"], df_subset["Latitude"])
    m_hi.scatter(x, y, s=5, color=color, alpha=0.6, marker="o")

# 调整图例位置（右上方）
ax_legend = plt.axes([0.72, 0.8, 0.2, 0.15])
ax_legend.axis("off")
legend_patches = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=8, label=f"{charger_type} Public") for charger_type, color in charging_colors.items()]
legend_patches += [plt.Line2D([0], [0], marker="*", color="w", markerfacecolor=color, markersize=10, label=f"{charger_type} Private") for charger_type, color in charging_colors.items()]
ax_legend.legend(handles=legend_patches, loc="center", fontsize=9, title="Charger Types")

# 添加标题
plt.suptitle("全美电动汽车充电站分布（区分充电级别 & 访问权限）", fontsize=14)

plt.show()
