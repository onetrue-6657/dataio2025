import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from mpl_toolkits.basemap import Basemap
import io
import base64
import numpy as nppip

# Load dataset
file_path = "E:\Learn\OSU\DataIO\ev_stations_v1.csv"
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

# State abbreviations with approximate central coordinates
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

# Create figure and axis
fig, ax_main = plt.subplots(figsize=(12, 8))

# Define the main USA map
m_main = Basemap(
    projection='merc',
    llcrnrlat=20, urcrnrlat=50,  # Latitude range (Mainland USA)
    llcrnrlon=-125, urcrnrlon=-65,  # Longitude range (Mainland USA)
    resolution='l', ax=ax_main
)

# Draw main USA map details
m_main.drawcoastlines()
m_main.drawcountries()
m_main.drawstates()
m_main.fillcontinents(color='lightgray', lake_color='white')

# Plot charger locations
df_sampled["x_main"], df_sampled["y_main"] = m_main(df_sampled["Longitude"].values, df_sampled["Latitude"].values)

for charger, color in color_mapping.items():
    subset_public = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Public")]
    subset_private = df_sampled[(df_sampled["Charger Type"] == charger) & (df_sampled["Access Type"] == "Private")]

    ax_main.scatter(subset_public["x_main"], subset_public["y_main"], s=5, color=color, alpha=0.7, marker='o')
    ax_main.scatter(subset_private["x_main"], subset_private["y_main"], s=10, color=color, alpha=0.7, marker='*')
    
# Add state abbreviations (excluding AK and HI in the mainland)
for state, (lat, lon) in state_labels.items():
    x, y = m_main(lon, lat)
    ax_main.text(x, y, state, fontsize=10, fontweight='bold', ha='center', va='center', color='black')

# Alaska and Hawaii to the bottom-left
ax_alaska = fig.add_axes([0.104, 0.106, 0.22, 0.22])  # Bottom-left
ax_hawaii = fig.add_axes([0.264, 0.106, 0.15,0.15])  # Below Alaska

# Define the Alaska map
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

# Filter Alaska data
df_alaska = df_sampled[(df_sampled["Latitude"] > 50) & (df_sampled["Longitude"] < -130)]
df_alaska["x_alaska"], df_alaska["y_alaska"] = m_alaska(df_alaska["Longitude"].values, df_alaska["Latitude"].values)

# Plot Alaska charging stations
for charger, color in color_mapping.items():
    subset_public = df_alaska[df_alaska["Charger Type"] == charger][df_alaska["Access Type"] == "Public"]
    subset_private = df_alaska[df_alaska["Charger Type"] == charger][df_alaska["Access Type"] == "Private"]

    ax_alaska.scatter(subset_public["x_alaska"], subset_public["y_alaska"], s=5, color=color, alpha=0.7, marker='o')
    ax_alaska.scatter(subset_private["x_alaska"], subset_private["y_alaska"], s=10, color=color, alpha=0.7, marker='*')

x_ak, y_ak = m_alaska(-152.0, 63.5)
ax_alaska.text(x_ak, y_ak, "AK", fontsize=10, fontweight='bold', ha='center', va='center', color='black')

# Define the Hawaii map
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

# Filter Hawaii data
df_hawaii = df_sampled[(df_sampled["Latitude"] < 23) & (df_sampled["Longitude"] < -150)]
df_hawaii["x_hawaii"], df_hawaii["y_hawaii"] = m_hawaii(df_hawaii["Longitude"].values, df_hawaii["Latitude"].values)

# Plot Hawaii charging stations
for charger, color in color_mapping.items():
    subset_public = df_hawaii[df_hawaii["Charger Type"] == charger][df_hawaii["Access Type"] == "Public"]
    subset_private = df_hawaii[df_hawaii["Charger Type"] == charger][df_hawaii["Access Type"] == "Private"]

    ax_hawaii.scatter(subset_public["x_hawaii"], subset_public["y_hawaii"], s=5, color=color, alpha=0.7, marker='o')
    ax_hawaii.scatter(subset_private["x_hawaii"], subset_private["y_hawaii"], s=10, color=color, alpha=0.7, marker='*')

x_hi, y_hi = m_hawaii(-157.5, 20)
ax_hawaii.text(x_hi,y_hi, "HI", fontsize=10, fontweight='bold', ha='center', va='center', color='black')

# legend to the bottom-right
legend_ax = fig.add_axes([0.75, 0.13, 0.2, 0.2])
legend_ax.axis("off")  

# Legend content
legend_ax.text(0.1, 0.9, "Charger Type", fontsize=12, fontweight="bold")
legend_ax.text(0.1, 0.75, "• Level 1 (Public)", fontsize=10, color="red")
legend_ax.text(0.1, 0.65, "* Level 1 (Private)", fontsize=10, color="red")
legend_ax.text(0.1, 0.50, "• Level 2 (Public)", fontsize=10, color="blue")
legend_ax.text(0.1, 0.40, "* Level 2 (Private)", fontsize=10, color="blue")
legend_ax.text(0.1, 0.25, "• DC Fast (Public)", fontsize=10, color="green")
legend_ax.text(0.1, 0.15, "* DC Fast (Private)", fontsize=10, color="green")

# Add title
ax_main.set_title("EV Charging Stations in the USA with Standardized Alaska & Hawaii Placement", fontsize=14)

# Show the final map
plt.show()



# Convert static map to image
#buf = io.BytesIO()
#plt.savefig(buf, format='png')
#buf.seek(0)
#encoded_image = base64.b64encode(buf.read()).decode()
#static_map_html = f'data:image/png;base64,{encoded_image}'
#plt.close()

# Aggregate charging station count per region
#df_region = df_clean.groupby(["State", "Latitude", "Longitude"]).size().reset_index(name="Count")

# Initialize Dash app
#app = Dash(__name__)
#app.layout = html.Div([
#    html.Img(id='static-map', src=static_map_html, style={'width': '100%'}),
#    dcc.Graph(id='ev-map', style={'display': 'none'}),
#    html.P("Hover over a state to rotate the map and visualize station distribution dynamically."),
#    dcc.Slider(
#        id='rotation-slider',
#        min=0, max=360, step=5, value=0,
#        marks={0: "0°", 90: "90°", 180: "180°", 270: "270°", 360: "360°"}
#    )
#])

# Define initial interactive 3D bar map
#fig_3d = go.Figure()
#fig_3d.add_trace(go.Scattermapbox(
#    lat=df_region["Latitude"],
#    lon=df_region["Longitude"],
#    marker=dict(size=5, color='blue'),
#    hoverinfo='text',
#    text=df_region["State"]
#))

#fig_3d.add_trace(go.Bar3d(
#    x=df_region["Longitude"],
#    y=df_region["Latitude"],
#    z=df_region["Count"],
#    marker=dict(color='blue', opacity=0.6),
#    width=0.5
#))

#fig_3d.update_layout(
#    scene=dict(
#        xaxis_title='Longitude',
#        yaxis_title='Latitude',
#       zaxis_title='Charging Stations',
#        camera=dict(eye=dict(x=1.5, y=1.5, z=1))
#    ),
#    mapbox_style="carto-positron",
#    margin=dict(l=0, r=0, t=0, b=0)
#)

#@app.callback(
#    [Output('ev-map', 'figure'), Output('ev-map', 'style'), Output('static-map', 'style')],
#    [Input('ev-map', 'hoverData'), Input('rotation-slider', 'value')]
#)
#def update_map(hoverData, rotation_value):
#    fig_3d.update_layout(
#        scene=dict(
#            camera=dict(eye=dict(x=np.cos(np.radians(rotation_value)), y=np.sin(np.radians(rotation_value)), z=1))
#        )
#    )
    
#    if hoverData and 'points' in hoverData:
#        point = hoverData['points'][0]
#        lat, lon = point['lat'], point['lon']
#        return fig_3d, {'display': 'block'}, {'display': 'none'}
    
#    return fig_3d, {'display': 'none'}, {'display': 'block'}

# Run Dash App
#if __name__ == '__main__':
#    app.run_server(debug=True)

