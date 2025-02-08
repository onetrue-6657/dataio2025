'''
This is a group project by team KFC for DataI/O 2025 hosted by Big Data Analysis Association at the Ohio State University.
The challenge is the beginner track challenge, which provides a dataset of EV Charging Stations. 
Team KFC:
Zheng Ni
Ken Ning
Rocky Fang
'''

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import streamlit as st
import matplotlib.pyplot as plt
import wget
import matplotlib.colors as mcolors
import geopandas as gpd
import folium
from mpl_toolkits.basemap import Basemap

df = pd.read_csv('ev_stations_v1.csv')

# Data Cleaning

df2 = df[['City', 'State']] # State and City

state = df2['State'].value_counts()
city = df2['City'].value_counts()

coordinates = df.dropna(subset=['Latitude', 'Longitude'])
lats = coordinates['Latitude'].tolist()
lons = coordinates['Longitude'].tolist()

# Bar plot of number of stations by state

plt.figure(figsize=(12, 6))
plt.bar(state.index, state.values)
plt.xlabel("State")
plt.ylabel("Number of Stations")
plt.title("Number of Stations by State")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(rotation=90)
plt.show()

# Bar plot of number of stations by city

city_filtered = city[:30]
plt.figure(figsize=(12, 6))
plt.bar(city_filtered.index, city_filtered.values)
plt.xlabel("City")
plt.ylabel("Number of Stations")
plt.title("Number of Stations by City")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(rotation=90)
plt.show()
    
# Draw US Map

plt.figure(figsize=(12, 8))
USMap = Basemap(projection="merc", llcrnrlat=24, urcrnrlat=50, llcrnrlon=-125, urcrnrlon=-66, resolution="l")
USMap.drawcoastlines()
USMap.drawcountries()
USMap.drawstates()
USMap.fillcontinents(color="#666666", lake_color="lightblue")
USMap.drawmapboundary(fill_color="lightblue") # Map without Alaska and Hawaii :(

# Show Facility Type Distribution Pie Chart

facility_type = df['Facility Type'].value_counts()
facility_type_labels = facility_type.index.to_list()
facility_type_sizes = facility_type.values.tolist()
threshold = 0.02 * sum(facility_type_sizes)
new_facility_type_labels = []
new_facility_type_sizes = []
other_total = 0
for label, size in zip(facility_type_labels, facility_type_sizes):
    if size < threshold:
        other_total += size
    else:
        new_facility_type_labels.append(label)
        new_facility_type_sizes.append(size)
new_facility_type_labels.append("Other")
new_facility_type_sizes.append(other_total)
plt.figure(figsize=(8, 8))
plt.pie(new_facility_type_sizes, labels=new_facility_type_labels, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black'})
plt.title("Facility Type Distribution")
plt.show()

network_state_counts = df.groupby("State")["EV Network"].value_counts().unstack().fillna(0)

# plt.figure(figsize=(12, 8))
# sns.heatmap(network_state_counts, cmap="Blues", annot=False)
# plt.xlabel("EV Network")
# plt.ylabel("State")
# plt.title("EV Network Distribution by State")
# plt.show()

# EV Network Distribution Across the U.S. Map

ev_network_map = df[df["EV Network"] != "Non-Networked"]
ev_network_map = df.dropna(subset=["Latitude", "Longitude", "EV Network"])

plt.figure(figsize=(12, 8))
USMap = Basemap(projection="merc", llcrnrlat=24, urcrnrlat=50, llcrnrlon=-125, urcrnrlon=-66, resolution="l")
USMap.drawcoastlines()
USMap.drawcountries()
USMap.drawstates()
USMap.fillcontinents(color="#666666", lake_color="lightblue")
USMap.drawmapboundary(fill_color="lightblue") # Map without Alaska and Hawaii :(
    
network_colors = {
    "Tesla": "red",
    "ChargePoint": "blue",
    "Blink": "green",
    "EVgo": "purple",
    "Other": "black"
}
ev_network_map["EV Network"] = ev_network_map["EV Network"].apply(lambda x: x if x in network_colors else "Other")

x, y = USMap(ev_network_map["Longitude"].values, ev_network_map["Latitude"].values)
colors = [network_colors[network] for network in ev_network_map["EV Network"].values]
plt.scatter(x, y, marker="o", c=colors, alpha=0.5, s=5)

plt.legend(handles=[plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=4, label=name) 
                    for name, color in network_colors.items()], loc="lower left")

plt.title("EV Network Distribution Across the U.S.")

# State vs Owner Separately

state_owner_data = df[['State', 'Owner Type Code']]
state_owner_data = state_owner_data.dropna(subset=['Owner Type Code'])
state_counts = df['State'].value_counts()

valid_states = state_counts[state_counts > 10].index
state_owner_filtered = state_owner_data[state_owner_data['State'].isin(valid_states)]

state_owner_counts = state_owner_filtered.groupby(['State', 'Owner Type Code']).size().unstack(fill_value=0)
state_owner_ratios = state_owner_counts.div(state_owner_counts.sum(axis=1), axis=0)

state_owner_ratios.plot(kind='bar', stacked=True, figsize=(12, 8))
plt.title("Owner Type Distribution by State")
plt.xlabel("State")
plt.ylabel("Percentage")
plt.legend(title="Owner Type")
plt.xticks(rotation=45)

plt.show()

# State vs Owner Public/Private/PPP

state_owner_data = df[['State', 'Owner Type Code']]
state_owner_data = state_owner_data.dropna(subset=['Owner Type Code'])
state_counts = df['State'].value_counts()

state_owner_data.loc[state_owner_data['Owner Type Code'].isin(['FG', 'SG', 'LG', 'T']), 'Owner Type Code'] = 'Public'
state_owner_data.loc[state_owner_data['Owner Type Code'] == 'P', 'Owner Type Code'] = 'Private'
state_owner_data.loc[state_owner_data['Owner Type Code'] == 'J', 'Owner Type Code'] = 'PPP'

valid_states = state_counts[state_counts > 10].index
state_owner_filtered = state_owner_data[state_owner_data['State'].isin(valid_states)]

state_owner_counts = state_owner_filtered.groupby(['State', 'Owner Type Code']).size().unstack(fill_value=0)
state_owner_ratios = state_owner_counts.div(state_owner_counts.sum(axis=1), axis=0)

state_owner_ratios.plot(kind='bar', stacked=True, figsize=(12, 8))
plt.title("Owner Type Distribution by State")
plt.xlabel("State")
plt.ylabel("Percentage")
plt.legend(title="Owner Type")
plt.xticks(rotation=45)

plt.show()

# State vs Owner Public/Private/PPP Sorted

state_owner_data = df[['State', 'Owner Type Code']]
state_owner_data = state_owner_data.dropna(subset=['Owner Type Code'])
state_counts = df['State'].value_counts()

state_owner_data.loc[state_owner_data['Owner Type Code'].isin(['FG', 'SG', 'LG', 'T']), 'Owner Type Code'] = 'Public'
state_owner_data.loc[state_owner_data['Owner Type Code'] == 'P', 'Owner Type Code'] = 'Private'
state_owner_data.loc[state_owner_data['Owner Type Code'] == 'J', 'Owner Type Code'] = 'PPP'

valid_states = state_counts[state_counts > 10].index
state_owner_filtered = state_owner_data[state_owner_data['State'].isin(valid_states)]

state_owner_counts = state_owner_filtered.groupby(['State', 'Owner Type Code']).size().unstack(fill_value=0)
state_owner_ratios = state_owner_counts.div(state_owner_counts.sum(axis=1), axis=0)

state_owner_ratios = state_owner_ratios.sort_values(by='Public', ascending=False)

state_owner_ratios.plot(kind='bar', stacked=True, figsize=(12, 8))
plt.title("Owner Type Distribution by State")
plt.xlabel("State")
plt.ylabel("Percentage")
plt.legend(title="Owner Type")
plt.xticks(rotation=45)

plt.show()

# Open Data Trend Quarterly

open_date_data = df[['Open Date']]
open_date_data = open_date_data.dropna(subset=['Open Date'])
open_date_data["Open Date"] = pd.to_datetime(df["Open Date"])
open_date_data = open_date_data[open_date_data["Open Date"] < "2022-01-01"]

open_date_data["Year-Quarter"] = open_date_data["Open Date"].dt.to_period("Q")
quarter_counts = open_date_data["Year-Quarter"].value_counts().sort_index()

plt.figure(figsize=(20, 6))
plt.xlim(-0.5, len(quarter_counts) - 0.5)
plt.plot(quarter_counts.index.astype(str), quarter_counts.values, marker="", linestyle="-")
plt.xlabel("Year-Quarter")
plt.ylabel("Number of New Stations")
plt.title("Quarterly Trend of EV Charging Stations Openings")
plt.xticks(rotation=45)
plt.grid(True)

plt.show()

# Open Data Trend Yearly

open_date_data = df[['Open Date']]
open_date_data = open_date_data.dropna(subset=['Open Date'])
open_date_data["Open Date"] = pd.to_datetime(df["Open Date"])
open_date_data = open_date_data[open_date_data["Open Date"] < "2022-01-01"]

open_date_data["Year"] = open_date_data["Open Date"].dt.to_period("Y")
year_counts = open_date_data["Year"].value_counts().sort_index()

plt.figure(figsize=(20, 6))
plt.xlim(-0.5, len(year_counts) - 0.5)
plt.ylim(0, max(year_counts.values) * 1.1)
plt.plot(year_counts.index.astype(str), year_counts.values, marker="", linestyle="-")
for i, value in enumerate(year_counts.values):
    plt.text(i, value + max(year_counts.values) * 0.02, str(value), ha="center", fontsize=10, color="black")
plt.xlabel("Year-Quarter")
plt.ylabel("Number of New Stations")
plt.title("Yearly Trend of EV Charging Stations Openings")
plt.xticks(rotation=45)
plt.grid(True)

plt.show()

# Number of Stations vs Number of EV Registrations by State

ev_registration_by_state = {
    "AL": 13047, "AK": 2697, "AZ": 89798, "AR": 7108, "CA": 1256646,
    "CO": 90083, "CT": 31557, "DL": 8435, "DC": 8066, "FL": 254878,
    "GA": 92368, "HI": 25565, "ID": 8501, "IL": 99573, "IN": 26101,
    "IO": 9031, "KS": 11271, "KT": 11617, "LA": 8150, "ME": 7377,
    "MD": 72139, "MA": 73768, "MI": 50284, "MN": 37050, "MS": 3590,
    "MO": 26861, "MT": 4608, "NE": 6920, "NV": 47361, "NH": 9861,
    "NJ": 134753, "NM": 10276, "NY": 131250, "NC": 70164, "ND": 959,
    "OH": 50393, "OK": 22843, "OR": 64361, "PA": 70154, "RI": 6396,
    "SC": 20873, "SD": 1675, "TN": 33221, "TX": 230125, "UT": 39998,
    "VT": 7816, "VA": 84936, "WA": 152101, "WV": 2758, "WI": 24943, "WY": 1139
}

state_charging_counts = df["State"].value_counts()
charging_stations_df = pd.DataFrame({"State": state_charging_counts.index, "Charging_Stations": state_charging_counts.values})
ev_counts_df = pd.DataFrame(list(ev_registration_by_state.items()), columns=["State", "EV_Count"])
merged_df = pd.merge(ev_counts_df, charging_stations_df, on="State", how="inner")

merged_df["EV/Charging Ratio"] = merged_df["EV_Count"] / merged_df["Charging_Stations"]

fig, ax1 = plt.subplots(figsize=(15, 6))

ax1.bar(merged_df["State"], np.log1p(merged_df["EV_Count"]), color='b', alpha=0.6, label="EV Count (log)")
ax1.set_xlabel("State")
ax1.set_ylabel("Log(Number of EVs)", color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.bar(merged_df["State"], merged_df["Charging_Stations"], color='#BA0C2F', alpha=0.4, label="Charging Stations")
ax2.set_ylabel("Number of Charging Stations", color='#BA0C2F')
ax2.tick_params(axis='y', labelcolor='#BA0C2F')

plt.xticks(rotation=90)

plt.title("Comparison of EV Counts and Charging Stations by State (Log Scale)")

fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))

plt.show()

# Number of Stations vs Number of EV Registrations by State Excluding California

ev_registration_by_state = {
    "AL": 13047, "AK": 2697, "AZ": 89798, "AR": 7108, 
    "CO": 90083, "CT": 31557, "DL": 8435, "DC": 8066, "FL": 254878,
    "GA": 92368, "HI": 25565, "ID": 8501, "IL": 99573, "IN": 26101,
    "IO": 9031, "KS": 11271, "KT": 11617, "LA": 8150, "ME": 7377,
    "MD": 72139, "MA": 73768, "MI": 50284, "MN": 37050, "MS": 3590,
    "MO": 26861, "MT": 4608, "NE": 6920, "NV": 47361, "NH": 9861,
    "NJ": 134753, "NM": 10276, "NY": 131250, "NC": 70164, "ND": 959,
    "OH": 50393, "OK": 22843, "OR": 64361, "PA": 70154, "RI": 6396,
    "SC": 20873, "SD": 1675, "TN": 33221, "TX": 230125, "UT": 39998,
    "VT": 7816, "VA": 84936, "WA": 152101, "WV": 2758, "WI": 24943, "WY": 1139
}

state_charging_counts = df["State"].value_counts()
charging_stations_df = pd.DataFrame({"State": state_charging_counts.index, "Charging_Stations": state_charging_counts.values})
ev_counts_df = pd.DataFrame(list(ev_registration_by_state.items()), columns=["State", "EV_Count"])
merged_df = pd.merge(ev_counts_df, charging_stations_df, on="State", how="inner")

merged_df["EV/Charging Ratio"] = merged_df["EV_Count"] / merged_df["Charging_Stations"]

fig, ax1 = plt.subplots(figsize=(15, 6))

ax1.bar(merged_df["State"], np.log1p(merged_df["EV_Count"]), color='b', alpha=0.6, label="EV Count (log)")
ax1.set_xlabel("State")
ax1.set_ylabel("Log(Number of EVs)", color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.bar(merged_df["State"], merged_df["Charging_Stations"], color='#BA0C2F', alpha=0.4, label="Charging Stations")
ax2.set_ylabel("Number of Charging Stations", color='#BA0C2F')
ax2.tick_params(axis='y', labelcolor='#BA0C2F')

plt.xticks(rotation=90)

plt.title("Comparison of EV Counts and Charging Stations by State Excluding CA (Log Scale)")

fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))

plt.show()

# Data comes from https://afdc.energy.gov/data/10962

# CA EV Stations Distribution by Counties

ca_zip_to_county_with_county = {
    "900": "Los Angeles County",
    "901": "Los Angeles County",
    "902": "Los Angeles County",
    "903": "Los Angeles County",
    "904": "Los Angeles County",
    "905": "Los Angeles County",
    "906": "Los Angeles County",
    "907": "Los Angeles County",
    "908": "Los Angeles County",
    "909": "San Bernardino County",
    "910": "Los Angeles County",
    "911": "Los Angeles County",
    "912": "Los Angeles County",
    "913": "Los Angeles County",
    "914": "Los Angeles County",
    "915": "Los Angeles County",
    "916": "Los Angeles County",
    "917": "San Bernardino County",
    "918": "Los Angeles County",
    "919": "San Diego County",
    "920": "San Diego County",
    "921": "San Diego County",
    "922": "Riverside County",
    "923": "San Bernardino County",
    "924": "San Bernardino County",
    "925": "Riverside County",
    "926": "Orange County",
    "927": "Orange County",
    "928": "Orange County",
    "930": "Ventura County",
    "931": "Santa Barbara County",
    "932": "Tulare County",
    "933": "Kern County",
    "934": "San Luis Obispo County",
    "935": "Los Angeles County",
    "936": "Fresno County",
    "937": "Fresno County",
    "938": "Fresno County",
    "939": "Monterey County",
    "940": "San Mateo County",
    "941": "San Francisco County",
    "942": "Sacramento County",
    "943": "Santa Clara County",
    "944": "San Mateo County",
    "945": "Alameda County",
    "946": "Alameda County",
    "947": "Alameda County",
    "948": "Contra Costa County",
    "949": "Marin County",
    "950": "Santa Clara County",
    "951": "Santa Clara County",
    "952": "San Joaquin County",
    "953": "Stanislaus County",
    "954": "Sonoma County",
    "955": "Humboldt County",
    "956": "Sacramento County",
    "957": "Sacramento County",
    "958": "Sacramento County",
    "959": "Butte County",
    "960": "Shasta County",
    "961": "Placer County"
}

ca_zip_to_county = {
    "900": "Los Angeles",
    "901": "Los Angeles",
    "902": "Los Angeles",
    "903": "Los Angeles",
    "904": "Los Angeles",
    "905": "Los Angeles",
    "906": "Los Angeles",
    "907": "Los Angeles",
    "908": "Los Angeles",
    "909": "San Bernardino",
    "910": "Los Angeles",
    "911": "Los Angeles",
    "912": "Los Angeles",
    "913": "Los Angeles",
    "914": "Los Angeles",
    "915": "Los Angeles",
    "916": "Los Angeles",
    "917": "San Bernardino",
    "918": "Los Angeles",
    "919": "San Diego",
    "920": "San Diego",
    "921": "San Diego",
    "922": "Riverside",
    "923": "San Bernardino",
    "924": "San Bernardino",
    "925": "Riverside",
    "926": "Orange",
    "927": "Orange",
    "928": "Orange",
    "930": "Ventura",
    "931": "Santa Barbara",
    "932": "Tulare",
    "933": "Kern",
    "934": "San Luis Obispo",
    "935": "Los Angeles",
    "936": "Fresno",
    "937": "Fresno",
    "938": "Fresno",
    "939": "Monterey",
    "940": "San Mateo",
    "941": "San Francisco",
    "942": "Sacramento",
    "943": "Santa Clara",
    "944": "San Mateo",
    "945": "Alameda",
    "946": "Alameda",
    "947": "Alameda",
    "948": "Contra Costa",
    "949": "Marin",
    "950": "Santa Clara",
    "951": "Santa Clara",
    "952": "San Joaquin",
    "953": "Stanislaus",
    "954": "Sonoma",
    "955": "Humboldt",
    "956": "Sacramento",
    "957": "Sacramento",
    "958": "Sacramento",
    "959": "Butte",
    "960": "Shasta",
    "961": "Placer"
}

ca_zip_codes = df[df["State"] == "CA"]["ZIP"].astype(str)
ca_zip_codes_prefix = ca_zip_codes.str[:3]
df.loc[df["State"] == "CA", "County"] = ca_zip_codes_prefix.map(ca_zip_to_county)
county_station_counts = df[df["State"] == "CA"]["County"].value_counts().sort_values(ascending=False)

plt.figure(figsize=(12, 6))
plt.bar(county_station_counts.index, county_station_counts.values, color="#BA0C2F")
plt.xlabel("County")
plt.ylabel("Number of Charging Stations")
plt.title("EV Charging Stations Distribution by County in California")
plt.xticks(rotation=90)
plt.grid(axis="y", linestyle="--", alpha=0.7)

plt.show()

# California County Distribution Map

california_map = gpd.read_file("california-counties.geojson")

county_station_counts = df[df["State"] == "CA"]["County"].value_counts().reset_index()
county_station_counts.columns = ["County", "Charging_Stations"]

all_counties = pd.DataFrame({"County": california_map["name"]})
county_station_counts = all_counties.merge(county_station_counts, on="County", how="left").fillna(0)

california_map = california_map.merge(county_station_counts, left_on="name", right_on="County", how="left")

fig, ax = plt.subplots(figsize=(10, 10))
california_map.plot(column="Charging_Stations", cmap="OrRd", linewidth=0.8, edgecolor="black", legend=True, ax=ax)
plt.title("EV Charging Stations Density by County in California")
plt.axis("off")

plt.show()

# Station Level vs Build Year By Ken Ning

df_open_date = df.dropna(subset=["Open Date"])
df_open_date["Open Year"] = pd.to_datetime(df_open_date["Open Date"], errors="coerce").dt.year
df_open_date = df_open_date[df_open_date["Open Year"] != 2022]

df_open_year = df_open_date.groupby("Open Year")[
    ["EV Level1 EVSE Num", "EV Level2 EVSE Num", "EV DC Fast Count"]
].sum()

plt.figure(figsize=(12, 6))
plt.plot(df_open_year.index, df_open_year["EV Level1 EVSE Num"], marker="o", label="Level 1 Charging Stations", linestyle="-")
plt.plot(df_open_year.index, df_open_year["EV Level2 EVSE Num"], marker="s", label="Level 2 Charging Stations", linestyle="-")
plt.plot(df_open_year.index, df_open_year["EV DC Fast Count"], marker="^", label="DC Fast Charging Stations", linestyle="-")

plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Charging Stations", fontsize=12)
plt.title("Growth of EV Charging Stations by Level Over Time (Excluding 2022)", fontsize=14)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)

plt.show()

# Postal Code Search by Ken Ning

df_filtered = df[['ZIP', 'City', 'State', 'Station Name', 'Street Address', 'EV Level1 EVSE Num', 'EV Level2 EVSE Num', 'EV DC Fast Count', 'EV Network']]
df_filtered = df_filtered.dropna(subset=['ZIP'])
df_filtered['ZIP'] = df_filtered['ZIP'].astype(str)

unique_zips = df_filtered[['ZIP']].drop_duplicates()
st.title("EV Charging Station Search")
zip_code = st.text_input("Input your postal code (ZIP Code)", "")

if zip_code:
    location_info = df_filtered[df_filtered['ZIP'] == zip_code][['City', 'State']].drop_duplicates()
    
    if not location_info.empty:
        city, state = location_info.iloc[0]
        st.write(f"Postal code {zip_code} belongs to {city}, {state}。")
        
        stations = df_filtered[df_filtered['ZIP'] == zip_code]
        
        if not stations.empty:
            st.write("The charging stations in this postal code are as follows:")
            st.dataframe(stations)
        else:
            st.write("No charging station information found in this postal code.")
            
            zip_list = df_filtered[['ZIP']].drop_duplicates().values.flatten()
            zip_tree = KDTree(zip_list.reshape(-1, 1).astype(float))
            
            try:
                nearest_idx = zip_tree.query([[float(zip_code)]], k=5)[1][0]
                nearby_zips = zip_list[nearest_idx]
                nearby_stations = df_filtered[df_filtered['ZIP'].isin(nearby_zips)]
                
                if not nearby_stations.empty:
                    st.write("The charging stations in the nearby area are as follows:")
                    st.dataframe(nearby_stations)
                else:
                    st.write("No charging station information found in the nearby area.")
            except:
                st.write("An error occurred while searching for nearby postal codes.")
    else:
        st.write("Postal code not found.")

# Map By Ken Ning

charging_colors = {
    "L1": "blue",
    "L2": "green",
    "DC": "red"
}

def get_charger_type(row):
    if row["EV DC Fast Count"] > 0:
        return "DC"
    elif row["EV Level2 EVSE Num"] > 0:
        return "L2"
    elif row["EV Level1 EVSE Num"] > 0:
        return "L1"
    return None

df["Charger Type"] = df.apply(get_charger_type, axis=1)

df_filtered = df.dropna(subset=["Charger Type"])

df_filtered["Marker"] = np.where(df_filtered["Groups With Access Code"] == "Private", "*", "o")

fig = plt.figure(figsize=(14, 8))
ax_main = fig.add_subplot(1, 1, 1)

m_main = Basemap(projection="merc", llcrnrlat=24, urcrnrlat=50, llcrnrlon=-125, urcrnrlon=-66, resolution="l", ax=ax_main)
m_main.drawcoastlines()
m_main.drawcountries()
m_main.drawstates()
m_main.fillcontinents(color="lightgray", lake_color="lightblue")
m_main.drawmapboundary(fill_color="lightblue")

for charger_type, color in charging_colors.items():
    df_subset = df_filtered[df_filtered["Charger Type"] == charger_type]
    x, y = m_main(df_subset["Longitude"], df_subset["Latitude"])
    for marker in ["o", "*"]:  # Public (o), Private (*)
        df_marker = df_subset[df_subset["Marker"] == marker]
        xm, ym = m_main(df_marker["Longitude"], df_marker["Latitude"])
        m_main.scatter(xm, ym, s=10 if marker == "o" else 20, color=color, alpha=0.6, marker=marker, label=f"{charger_type} ({'Private' if marker == '*' else 'Public'})")

ax_ak = plt.axes([0.02, 0.05, 0.2, 0.2])
m_ak = Basemap(projection="merc", llcrnrlat=50, urcrnrlat=72, llcrnrlon=-170, urcrnrlon=-130, resolution="l", ax=ax_ak)
m_ak.drawcoastlines()
m_ak.drawcountries()
m_ak.drawstates()
m_ak.fillcontinents(color="lightgray", lake_color="lightblue")
m_ak.drawmapboundary(fill_color="lightblue")

df_ak = df_filtered[(df_filtered["Latitude"] > 50) & (df_filtered["Longitude"] < -130)]
for charger_type, color in charging_colors.items():
    df_subset = df_ak[df_ak["Charger Type"] == charger_type]
    x, y = m_ak(df_subset["Longitude"], df_subset["Latitude"])
    m_ak.scatter(x, y, s=5, color=color, alpha=0.6, marker="o")

ax_hi = plt.axes([0.25, 0.05, 0.15, 0.15])
m_hi = Basemap(projection="merc", llcrnrlat=18, urcrnrlat=22, llcrnrlon=-161, urcrnrlon=-154, resolution="l", ax=ax_hi)
m_hi.drawcoastlines()
m_hi.drawcountries()
m_hi.drawstates()
m_hi.fillcontinents(color="lightgray", lake_color="lightblue")
m_hi.drawmapboundary(fill_color="lightblue")

df_hi = df_filtered[(df_filtered["Latitude"] > 18) & (df_filtered["Latitude"] < 22) & (df_filtered["Longitude"] < -154)]
for charger_type, color in charging_colors.items():
    df_subset = df_hi[df_hi["Charger Type"] == charger_type]
    x, y = m_hi(df_subset["Longitude"], df_subset["Latitude"])
    m_hi.scatter(x, y, s=5, color=color, alpha=0.6, marker="o")

ax_legend = plt.axes([0.72, 0.8, 0.2, 0.15])
ax_legend.axis("off")
legend_patches = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=8, label=f"{charger_type} Public") for charger_type, color in charging_colors.items()]
legend_patches += [plt.Line2D([0], [0], marker="*", color="w", markerfacecolor=color, markersize=10, label=f"{charger_type} Private") for charger_type, color in charging_colors.items()]
ax_legend.legend(handles=legend_patches, loc="center", fontsize=9, title="Charger Types")

plt.suptitle("全美电动汽车充电站分布（区分充电级别 & 访问权限）", fontsize=14)
plt.show()

# Map By Rocky
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df_clean = df.dropna(subset=['Latitude', 'Longitude'])

color_mapping = {
    "Level 1": "red",
    "Level 2": "blue",
    "DC Fast": "green"
}

def classify_charger(row):
    if row["EV DC Fast Count"] > 0:
        return "DC Fast"
    elif row["EV Level2 EVSE Num"] > 0:
        return "Level 2"
    elif row["EV Level1 EVSE Num"] > 0:
        return "Level 1"
    return "Unknown"

df_clean["Charger Type"] = df_clean.apply(classify_charger, axis=1)
df_clean["Access Type"] = df_clean["Groups With Access Code"].apply(lambda x: "Public" if x == "Public" else "Private")
df_sampled = df_clean.sample(frac=0.1, random_state=42)
state_labels = {
    "AL": (32.8, -86.8), "AZ": (34.0, -111.0), "AR": (34.8, -92.2),
    "CA": (37.2, -119.4), "CO": (39.0, -105.5), "CT": (41.6, -72.7), "DE": (39.0, -75.5),
    "FL": (27.8, -81.6), "GA": (32.6, -83.4), "ID": (44.0, -114.0),
    "IL": (40.0, -89.0), "IN": (39.8, -86.1), "IA": (42.0, -93.5), "KS": (38.5, -98.0),
    "KY": (37.5, -85.0), "LA": (30.9, -91.1), "ME": (45.5, -69.0), "MD": (39.0, -76.7),
    "MA": (42.3, -71.5), "MI": (44.3, -85.4), "MN": (46.4, -94.6), "MS": (32.7, -89.7),
    "MO": (38.5, -92.5), "MT": (47.0, -110.0), "NE": (41.5, -99.7), "NV": (39.0, -116.5),
    "NH": (43.8, -71.6), "NJ": (40.2, -74.7), "NM": (34.5, -106.0), "NY": (42.9, -75.6),
    "NC": (35.5, -79.4), "ND": (47.5, -100.5), "OH": (40.3, -82.8), "OK": (35.6, -97.5),
    "OR": (44.0, -120.5), "PA": (41.2, -77.2), "RI": (41.7, -71.5), "SC": (33.9, -81.2),
    "SD": (44.5, -100.3), "TN": (35.9, -86.6), "TX": (31.5, -99.3), "UT": (39.4, -111.6),
    "VT": (44.0, -72.7), "VA": (37.8, -78.2), "WA": (47.4, -120.7), "WV": (38.6, -80.5),
    "WI": (44.6, -89.6), "WY": (43.0, -107.5)
}

fig, ax_main = plt.subplots(figsize=(12, 8))
m_main = Basemap(
    projection='merc',
    llcrnrlat=20, urcrnrlat=50,
    llcrnrlon=-125, urcrnrlon=-65,
    resolution='l', ax=ax_main
)

m_main.drawcoastlines()
m_main.drawcountries()
m_main.drawstates()
m_main.fillcontinents(color='lightgray', lake_color='white')

df_sampled["x_main"], df_sampled["y_main"] = m_main(df_sampled["Longitude"].values, df_sampled["Latitude"].values)

for charger, color in color_mapping.items():
    subset_public = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Public")]
    subset_private = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Private")]

    ax_main.scatter(subset_public["x_main"], subset_public["y_main"], s=5, color=color, alpha=0.7, marker='o')
    ax_main.scatter(subset_private["x_main"], subset_private["y_main"], s=10, color=color, alpha=0.7, marker='*')
    
for state, (lat, lon) in state_labels.items():
    x, y = m_main(lon, lat)
    ax_main.text(x, y, state, fontsize=10, fontweight='bold', ha='center', va='center', color='black')

ax_alaska = fig.add_axes([0.104, 0.106, 0.22, 0.22])
ax_hawaii = fig.add_axes([0.264, 0.106, 0.15,0.15])

m_alaska = Basemap(
    projection='merc',
    llcrnrlat=50, urcrnrlat=72,
    llcrnrlon=-170, urcrnrlon=-130,
    resolution='l', ax=ax_alaska
)

m_alaska.drawcoastlines()
m_alaska.drawcountries()
m_alaska.drawstates()
m_alaska.fillcontinents(color='lightgray', lake_color='white')

df_alaska = df_sampled[(df_sampled["Latitude"] > 50) & (df_sampled["Longitude"] < -130)]
df_alaska["x_alaska"], df_alaska["y_alaska"] = m_alaska(df_alaska["Longitude"].values, df_alaska["Latitude"].values)

for charger, color in color_mapping.items():
    subset_public = df_alaska[df_alaska["Charger Type"] == charger][df_alaska["Access Type"] == "Public"]
    subset_private = df_alaska[df_alaska["Charger Type"] == charger][df_alaska["Access Type"] == "Private"]

    ax_alaska.scatter(subset_public["x_alaska"], subset_public["y_alaska"], s=5, color=color, alpha=0.7, marker='o')
    ax_alaska.scatter(subset_private["x_alaska"], subset_private["y_alaska"], s=10, color=color, alpha=0.7, marker='*')

x_ak, y_ak = m_alaska(-152.0, 63.5)
ax_alaska.text(x_ak, y_ak, "AK", fontsize=10, fontweight='bold', ha='center', va='center', color='black')

m_hawaii = Basemap(
    projection='merc',
    llcrnrlat=18, urcrnrlat=22,
    llcrnrlon=-161, urcrnrlon=-154,
    resolution='l', ax=ax_hawaii
)

m_hawaii.drawcoastlines()
m_hawaii.drawcountries()
m_hawaii.drawstates()
m_hawaii.fillcontinents(color='lightgray', lake_color='white')

df_hawaii = df_sampled[(df_sampled["Latitude"] < 23) & (df_sampled["Longitude"] < -150)]
df_hawaii["x_hawaii"], df_hawaii["y_hawaii"] = m_hawaii(df_hawaii["Longitude"].values, df_hawaii["Latitude"].values)

for charger, color in color_mapping.items():
    subset_public = df_hawaii[df_hawaii["Charger Type"] == charger][df_hawaii["Access Type"] == "Public"]
    subset_private = df_hawaii[df_hawaii["Charger Type"] == charger][df_hawaii["Access Type"] == "Private"]

    ax_hawaii.scatter(subset_public["x_hawaii"], subset_public["y_hawaii"], s=5, color=color, alpha=0.7, marker='o')
    ax_hawaii.scatter(subset_private["x_hawaii"], subset_private["y_hawaii"], s=10, color=color, alpha=0.7, marker='*')

x_hi, y_hi = m_hawaii(-157.5, 20)
ax_hawaii.text(x_hi,y_hi, "HI", fontsize=10, fontweight='bold', ha='center', va='center', color='black')

legend_ax = fig.add_axes([0.75, 0.13, 0.2, 0.2])
legend_ax.axis("off")  

legend_ax.text(0.1, 0.9, "Charger Type", fontsize=12, fontweight="bold")
legend_ax.text(0.1, 0.75, "• Level 1 (Public)", fontsize=10, color="red")
legend_ax.text(0.1, 0.65, "* Level 1 (Private)", fontsize=10, color="red")
legend_ax.text(0.1, 0.50, "• Level 2 (Public)", fontsize=10, color="blue")
legend_ax.text(0.1, 0.40, "* Level 2 (Private)", fontsize=10, color="blue")
legend_ax.text(0.1, 0.25, "• DC Fast (Public)", fontsize=10, color="green")
legend_ax.text(0.1, 0.15, "* DC Fast (Private)", fontsize=10, color="green")

ax_main.set_title("EV Charging Stations in the USA with Standardized Alaska & Hawaii Placement", fontsize=14)
plt.show()

# Map With Types and Locations by Rocky

df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df_clean = df.dropna(subset=['Latitude', 'Longitude'])

color_mapping = {
    "Level 1": "red",
    "Level 2": "blue",
    "DC Fast": "green"
}

def classify_charger(row):
    if row["EV DC Fast Count"] > 0:
        return "DC Fast"
    elif row["EV Level2 EVSE Num"] > 0:
        return "Level 2"
    elif row["EV Level1 EVSE Num"] > 0:
        return "Level 1"
    return "Unknown"

df_clean["Charger Type"] = df_clean.apply(classify_charger, axis=1)
df_clean["Access Type"] = df_clean["Groups With Access Code"].apply(lambda x: "Public" if x == "Public" else "Private")
df_sampled = df_clean.sample(frac=0.1, random_state=42)

fig, ax = plt.subplots(figsize=(12, 8))

m = Basemap(
    projection='merc',
    llcrnrlat=24, urcrnrlat=50,
    llcrnrlon=-125, urcrnrlon=-65,
    resolution='l', ax=ax
)

m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.fillcontinents(color='lightgray', lake_color='white')

df_sampled["x"], df_sampled["y"] = m(df_sampled["Longitude"].values, df_sampled["Latitude"].values)

for charger, color in color_mapping.items():
    subset_public = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Public")]
    subset_private = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Private")]

    ax.scatter(subset_public["x"], subset_public["y"], s=10, color=color, label=f"{charger} (Public)", alpha=0.7, marker='o')

    ax.scatter(subset_private["x"], subset_private["y"], s=40, color=color, label=f"{charger} (Private)", alpha=0.7, marker='*')

ax.set_title("EV Charging Stations in the USA by Charger Type & Access Type", fontsize=14)
ax.legend(title="Charger Type & Access Type", loc="upper right", fontsize=10)

plt.show()
