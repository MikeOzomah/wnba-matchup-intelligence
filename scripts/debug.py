import pandas as pd

df = pd.read_csv("../outputs/cleaned_player_data.csv")

print(df["team"].unique())

print(df[df["team"].str.contains("Washington", case=False, na=False)])