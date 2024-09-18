import pandas as pd
from neighborhoods.models import Bezirke

def load_bezirke():
    # Load the CSV file
    file_path = "path/to/berlin_bezirke.csv"
    df = pd.read_csv(file_path)

    # Iterate over the CSV rows and create Bezirke objects
    for index, row in df.iterrows():
        Bezirke.objects.create(
            name=row['Name'],
            population=row['Population'],
            area=row['Area'],
            latitude=row['Latitude'],
            longitude=row['Longitude']
        )
