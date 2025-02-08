import pandas as pd
import streamlit as st
from scipy.spatial import KDTree

# 读取数据
file_path = "ev_stations_v1.csv"  # 替换为你的数据文件路径
df = pd.read_csv(file_path)

# 选择需要的字段
df_filtered = df[['ZIP', 'City', 'State', 'Station Name', 'Street Address', 'EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count', 'EV Network']]

# 去除 ZIP 为空的行
df_filtered = df_filtered.dropna(subset=['ZIP'])

# 转换 ZIP 为字符串（防止前导零丢失）
df_filtered['ZIP'] = df_filtered['ZIP'].astype(str)

# 获取唯一的 ZIP 列表
unique_zips = df_filtered[['ZIP']].drop_duplicates()

# 创建 Streamlit 应用
st.title("EV 充电站查询")

# 用户输入邮政编码
zip_code = st.text_input("输入邮政编码 (ZIP Code)", "")

if zip_code:
    # 查找匹配的城市和州
    location_info = df_filtered[df_filtered['ZIP'] == zip_code][['City', 'State']].drop_duplicates()
    
    if not location_info.empty:
        city, state = location_info.iloc[0]
        st.write(f"邮政编码 {zip_code} 属于 {city}, {state}。")
        
        # 查找该 ZIP 代码下的所有充电站
        stations = df_filtered[df_filtered['ZIP'] == zip_code]
        
        if not stations.empty:
            st.write("相关充电站信息：")
            st.dataframe(stations)
        else:
            st.write("该邮政编码内未找到充电站信息。")
            
            # 提供附近邮编的充电站信息
            zip_list = df_filtered[['ZIP']].drop_duplicates().values.flatten()
            zip_tree = KDTree(zip_list.reshape(-1, 1).astype(float))
            
            try:
                nearest_idx = zip_tree.query([[float(zip_code)]], k=5)[1][0]
                nearby_zips = zip_list[nearest_idx]
                nearby_stations = df_filtered[df_filtered['ZIP'].isin(nearby_zips)]
                
                if not nearby_stations.empty:
                    st.write("附近邮政编码的充电站信息：")
                    st.dataframe(nearby_stations)
                else:
                    st.write("附近区域也未找到充电站信息。")
            except:
                st.write("无法找到相近的邮政编码。")
    else:
        st.write("未找到该邮政编码的相关信息。")
