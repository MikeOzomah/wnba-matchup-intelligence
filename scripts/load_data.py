import pandas as pd

# Load the CSV file
df = pd.read_csv("../data/wnba_preseason_team_game_data.csv")

# Display first 5 rows
print(df.head())

# Display column names
print("\nColumns:")
print(df.columns)

# Display dataset shape
print("\nDataset Shape:")
print(df.shape)