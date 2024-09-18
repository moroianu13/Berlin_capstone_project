import geopandas as gpd

# Load the shapefile
shapefile_path = "D:/ADRIAN/projects/rentfinder/berlin_postleitzahlen.shp"
gdf = gpd.read_file(shapefile_path)

# Convert to GeoJSON
geojson_path = "D:/ADRIAN/projects/rentfinder/berlin_postleitzahlen.geojson"
gdf.to_file(geojson_path, driver="GeoJSON")

print(f"GeoJSON file has been saved at {geojson_path}")
