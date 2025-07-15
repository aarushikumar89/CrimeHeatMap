import requests 
import geopandas as gpd # reading GeoJSON files into GeoDataFrame
import pandas as pd # for data cleaning and manipulation

# Loading the live GeoJSON data from the URL
url = "https://services5.arcgis.com/ROBnTHSNjoZ2Wm1P/arcgis/rest/services/Crime_Reports_Jul2022_Present/FeatureServer/2/query?outFields=*&where=1%3D1&f=geojson"
gdf = gpd.read_file(url) # takes the url above and reads information

# Extracting the Steet Address, City, & Crime 
df = gdf[['Street', 'City', 'CrimeDescription']].copy()

# Combining the Street + City 
df['Address'] = df['Street'].astype(str).str.title() + ", " + df['City'].astype(str).str.title()

def categorize_crime(description): 
    desc = description.upper()
    if 'ASSAULT' in desc or 'BATTERY' in desc:
        return 'Violent'
    elif 'BURGLARY' in desc or 'THEFT' in desc:
        return 'Property'
    elif 'DUI' in desc or 'DRIVING' in desc:
        return 'Traffic'
    elif 'WARRANT' in desc: 
        return 'Legal'
    else: 
        return 'Other'

df ['Category'] = df['CrimeDescription'].apply(categorize_crime) # new colum to map each crime into general, relevant category

...
df['Category'] = df['CrimeDescription'].apply(categorize_crime)

# START OF NEW BLOCK
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

geolocator = Nominatim(user_agent="crime_map_app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, max_retries=3, error_wait_seconds=5, swallow_exceptions=True)


latitudes = []
longitudes = []

print("Starting geocoding...")
df = df.iloc[:20].copy()
for address in df['Address']:
    try:
        location = geocode(address, timeout=10)
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        latitudes.append(None)
        longitudes.append(None)
    

df['Latitude'] = latitudes
df['Longitude'] = longitudes
# END OF NEW BLOCK

clean_df = df[['Address', 'CrimeDescription', 'Category', 'Latitude', 'Longitude']]
print(clean_df.head())
clean_df.to_csv('alameda_live_crime_geocoded.csv', index=False)


