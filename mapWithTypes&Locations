import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.basemap import Basemap

# Load dataset
file_path = "/mnt/data/ev_stations_v1.csv"
df = pd.read_csv(file_path)

# Convert Longitude to numeric (fix mixed types issue)
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

# Drop rows with missing location data
df_clean = df.dropna(subset=['Latitude', 'Longitude'])

# Define color mapping based on charger type
color_mapping = {
    "Level 1": "red",
    "Level 2": "blue",
    "DC Fast": "green"
}

# Classify station types based on available charger counts
def classify_charger(row):
    if row["EV DC Fast Count"] > 0:
        return "DC Fast"
    elif row["EV Level2 EVSE Num"] > 0:
        return "Level 2"
    elif row["EV Level1 EVSE Num"] > 0:
        return "Level 1"
    return "Unknown"

df_clean["Charger Type"] = df_clean.apply(classify_charger, axis=1)

# Classify stations as public or private
df_clean["Access Type"] = df_clean["Groups With Access Code"].apply(lambda x: "Public" if x == "Public" else "Private")

# Sample the dataset for faster rendering
df_sampled = df_clean.sample(frac=0.1, random_state=42)

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Define the map with USA boundaries
m = Basemap(
    projection='merc',
    llcrnrlat=24, urcrnrlat=50,   # Latitude range (USA)
    llcrnrlon=-125, urcrnrlon=-65, # Longitude range (USA)
    resolution='l', ax=ax
)

# Draw map details
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.fillcontinents(color='lightgray', lake_color='white')

# Convert latitude and longitude to map coordinates for sampled data
df_sampled["x"], df_sampled["y"] = m(df_sampled["Longitude"].values, df_sampled["Latitude"].values)

# Plot different charger types and access types
for charger, color in color_mapping.items():
    subset_public = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Public")]
    subset_private = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Private")]

    # Public stations as dots
    ax.scatter(subset_public["x"], subset_public["y"], s=10, color=color, label=f"{charger} (Public)", alpha=0.7, marker='o')

    # Private stations as stars
    ax.scatter(subset_private["x"], subset_private["y"], s=40, color=color, label=f"{charger} (Private)", alpha=0.7, marker='*')

# Add title and legend
ax.set_title("EV Charging Stations in the USA by Charger Type & Access Type", fontsize=14)
ax.legend(title="Charger Type & Access Type", loc="upper right", fontsize=10)

# Show the map
plt.show()
