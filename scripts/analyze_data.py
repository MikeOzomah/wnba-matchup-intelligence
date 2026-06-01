import pandas as pd

# Load cleaned dataset
df = pd.read_csv("../outputs/cleaned_wnba_data.csv")

# Team averages
team_summary = df.groupby("team")[[
    "pts",
    "possessions",
    "ball_security",
    "shot_value",
    "offensive_flow"
]].mean()

# Sort by offensive flow
team_summary = team_summary.sort_values(
    by="offensive_flow",
    ascending=False
)

# Display results
print("\nTEAM ANALYTICS SUMMARY:")
print(team_summary)

# Save analytics summary
team_summary.to_csv(
    "../outputs/team_analytics_summary.csv"
)

print("\nAnalytics summary saved successfully.")