import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import nfl_data_py as nfl

seasons = range(2016, 2022 + 1)
pbp_data = nfl.import_pbp_data(seasons)

pbp_passing = pbp_data.query('play_type == "pass" and air_yards.notnull()').reset_index()

pbp_passing['pass_length_air_yards'] = np.where(pbp_passing['air_yards'] >= 20, "long", "short")
pbp_passing["passing_yards"] = np.where(pbp_passing["passing_yards"].isnull(), 0, pbp_passing["passing_yards"])

# print(pbp_passing["passing_yards"].describe())

## Epa for short passes
# print(pbp_passing.query('pass_length_air_yards == "short"')["epa"].describe())

## Epa for long passes
# print(pbp_passing.query('pass_length_air_yards == "long"')["epa"].describe())

sns.set_theme(style="whitegrid", palette='colorblind')

pbp_passing_short = pbp_passing.query('pass_length_air_yards == "short"')
pbp_passing_long = pbp_passing.query('pass_length_air_yards == "long"')


# # Histogram of passing yards on short passes
# pbp_passing_hist_short = sns.histplot(pbp_passing_short,
#                                       binwidth=1,
#                                       x="passing_yards", kde=True)
# pbp_passing_hist_short.set_xlabel("Passing Yards")
# pbp_passing_hist_short.set_ylabel("Count")
# plt.show()

# # Boxplot Passing Yards
# pass_boxplot = sns.boxplot(data=pbp_passing, x="pass_length_air_yards", y="passing_yards")
# pass_boxplot.set(
#   xlabel="Pass Length (long >= 20 yards, short < 20 yards)",
#   ylabel="Yards gained or lost during play",
# )
# plt.show()

pbp_passing_season = pbp_passing.groupby(["passer_id", "passer", "season"]).agg({"passing_yards": ["mean", "count"]})
pbp_passing_season.columns = list(map('_'.join, pbp_passing_season.columns.values))
pbp_passing_season.rename(columns={"passing_yards_mean": "YPA", "passing_yards_count": "n"}, inplace=True)

# print(pbp_passing_season.sort_values(by="YPA", ascending=False))

#Filter by minimum 225 attempts
pbp_passing_season_min100 = pbp_passing_season.query('n >= 100').sort_values(by="YPA", ascending=False)
# print(pbp_passing_season_min100.head())

# Deep vs Short Passes
pbp_passing_season_length = pbp_passing.groupby(["passer_id", "passer", "season", "pass_length_air_yards"]).agg({"passing_yards": ["mean", "count"]})

# Flatten the multi-level column names
pbp_passing_season_length.columns = list(map('_'.join, pbp_passing_season_length.columns.values))

# Rename immediately after aggregation to ensure 'YPA' is available
pbp_passing_season_length.rename(columns={"passing_yards_mean": "YPA", "passing_yards_count": "n"}, inplace=True)

# Reset index to bring columns from the index back as regular columns
pbp_passing_season_length.reset_index(inplace=True)

# Define the query condition
q_value = (
    '(n >= 100 & ' +
    'pass_length_air_yards == "short") | ' +
    '(n >= 30 & ' +
    'pass_length_air_yards == "long")'
)
print(pbp_passing_season_length)
# Apply the query and reset index again
pbp_passing_season_length = pbp_passing_season_length.query(q_value).reset_index()

# Select the necessary columns 
cols_save = ["passer_id", "passer", "season", "pass_length_air_yards", "YPA"]
air_yards = pbp_passing_season_length[cols_save].copy()  # Now 'YPA' is available


# Create lagged data 
# Create lagged data (exclude last season)
air_yards_lag = air_yards.copy()
air_yards_lag["season"] += 1
air_yards_lag.rename(columns={"YPA": "YPA_last"}, inplace=True)

# Merge data with lagged data (still using inner join)
pbp_passing_season_length = air_yards.merge(air_yards_lag, how='inner', on=["passer_id", "passer", "season", "pass_length_air_yards"])
print(pbp_passing_season_length)


# Display the results
print(pbp_passing_season_length[["pass_length_air_yards", "passer", "season", "YPA", "YPA_last"]].query('passer == "P.Mahomes" | passer == "A.Rodgers"').sort_values(["passer", "pass_length_air_yards", "season"]).to_string())
