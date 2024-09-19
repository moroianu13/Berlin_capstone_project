import json
import random

# List of Berlin boroughs and neighborhoods with their approximate coordinates
# (Coordinates are approximate and simplified for demonstration purposes)
neighborhoods = [
    {"name": "Charlottenburg-Wilmersdorf", "coordinates": [13.3027, 52.5026]},
    {"name": "Friedrichshain-Kreuzberg", "coordinates": [13.4301, 52.5077]},
    {"name": "Lichtenberg", "coordinates": [13.5127, 52.5207]},
    {"name": "Marzahn-Hellersdorf", "coordinates": [13.5722, 52.5450]},
    {"name": "Mitte", "coordinates": [13.4050, 52.5200]},
    {"name": "Neukölln", "coordinates": [13.4447, 52.4804]},
    {"name": "Pankow", "coordinates": [13.4132, 52.5524]},
    {"name": "Reinickendorf", "coordinates": [13.3208, 52.5833]},
    {"name": "Spandau", "coordinates": [13.2052, 52.5363]},
    {"name": "Steglitz-Zehlendorf", "coordinates": [13.2419, 52.4554]},
    {"name": "Tempelhof-Schöneberg", "coordinates": [13.3879, 52.4756]},
    {"name": "Treptow-Köpenick", "coordinates": [13.5844, 52.4429]},
    {"name": "Wedding", "coordinates": [13.3547, 52.5486]},
    {"name": "Prenzlauer Berg", "coordinates": [13.4285, 52.5386]},
    {"name": "Moabit", "coordinates": [13.3439, 52.5302]}
]

# Generate the mock GeoJSON data
geojson_data = {
    "type": "FeatureCollection",
    "features": []
}

for neighborhood in neighborhoods:
    rent = random.randint(300, 3000)  # Random rent between 300€ and 3000€
    family_friendly = random.choice([True, False])
    party_animal = random.choice([True, False])
    pets_friendly = random.choice([True, False])
    cultural = random.choice([True, False])

    lat = neighborhood["coordinates"][1]
    lon = neighborhood["coordinates"][0]

    feature = {
        "type": "Feature",
        "properties": {
            "name": neighborhood["name"],
            "rent": rent,
            "family_friendly": family_friendly,
            "party_animal": party_animal,
            "pets_friendly": pets_friendly,
            "cultural": cultural
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[lon, lat], [lon + 0.01, lat], [lon + 0.01, lat + 0.01], [lon, lat + 0.01], [lon, lat]]]
        }
    }

    geojson_data["features"].append(feature)

# Save the generated data to the neighborhoods file
output_path = "static/geojson/neighborhoods_mock.geojson"
with open(output_path, 'w') as outfile:
    json.dump(geojson_data, outfile)

print("Mock data for all Berlin neighborhoods added successfully.")
