import pandas as pd

# Load dataset
df = pd.read_csv("../data/wnba_preseason_team_game_data.csv")

# Convert column names to lowercase
df.columns = df.columns.str.lower()

# Remove extra spaces from column names
df.columns = df.columns.str.strip()

# Fix possible misspellings of possessions
df = df.rename(columns={
    'posession': 'possessions',
    'possesions': 'possessions'
})

# Print all column names
print("Columns:")
print(df.columns.tolist())

# Remove extra spaces from text columns
df['team'] = df['team'].str.strip()
df['opponent'] = df['opponent'].str.strip()

# Convert numeric columns
numeric_cols = [
    'fgm', 'fga', 'fg%', '3pm', '3pa', '3p%',
    'ftm', 'fta', 'ft%', 'oreb', 'dreb', 'reb',
    'ast', 'stl', 'blk', 'to', 'pf', 'pts',
    '+/-', 'possessions', 'ball_security',
    'shot_value', 'offensive_flow'
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Display cleaned dataset info
print("\nDataset Shape:")
print(df.shape)

print("\nData Types:")
print(df.dtypes)

# Save cleaned dataset
df.to_csv("../outputs/cleaned_wnba_data.csv", index=False)

print("\nCleaned dataset saved successfully.")