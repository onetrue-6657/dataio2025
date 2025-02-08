import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import wget
import folium
from mpl_toolkits.basemap import Basemap

df = pd.read_csv('ev_stations_v1.csv')

selected_columns = ["Station Name", "Street Address", "City", "State", "ZIP", "Station Phone", "Groups With Access Code", 
                    "Access Days Time", "EV Level2 EVSE Num", "EV Network", "Geocode Status", "Date Last Confirmed", 
                    "ID", "Owner Type Code", "Open Date", "EV Connector Types", "Access Code", "Facility Type", "EV Pricing"]

df = pd.DataFrame(columns=selected_columns)

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
    
# OSU Scarlet Code: #BA0C2F

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