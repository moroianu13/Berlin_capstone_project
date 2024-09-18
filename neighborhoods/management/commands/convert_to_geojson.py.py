import geopandas as gpd

# Load the shapefile
shapefile_path = "path/to/berlin_postleitzahlen.shp"
gdf = gpd.read_file(shapefile_path)

# Convert to GeoJSON
geojson_path = "path/to/berlin_postleitzahlen.geojson"
gdf.to_file(geojson_path, driver="GeoJSON")
