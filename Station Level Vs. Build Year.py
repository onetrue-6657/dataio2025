import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
file_path = "ev_stations_v1.csv"  # 替换为你的数据文件路径
df = pd.read_csv(file_path)

# 过滤掉没有 Open Date 的数据
df_open_date = df.dropna(subset=["Open Date"])

# 转换 Open Date 为年份
df_open_date["Open Year"] = pd.to_datetime(df_open_date["Open Date"], errors="coerce").dt.year

# 按年份统计不同级别的充电站数量
df_open_year = df_open_date.groupby("Open Year")[
    ["EV Level1 EVSE Num", "EV Level2 EVSE Num", "EV DC Fast Count"]
].sum()

# 绘制折线图
plt.figure(figsize=(12, 6))
plt.plot(df_open_year.index, df_open_year["EV Level1 EVSE Num"], marker="o", label="Level 1 Charging Stations", linestyle="-")
plt.plot(df_open_year.index, df_open_year["EV Level2 EVSE Num"], marker="s", label="Level 2 Charging Stations", linestyle="-")
plt.plot(df_open_year.index, df_open_year["EV DC Fast Count"], marker="^", label="DC Fast Charging Stations", linestyle="-")

# 添加标签和标题
plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Charging Stations", fontsize=12)
plt.title("Growth of EV Charging Stations by Level Over Time", fontsize=14)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)

# 显示图表
plt.show()
