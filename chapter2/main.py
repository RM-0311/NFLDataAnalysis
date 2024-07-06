import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sportsdataverse.cfb as CFB
import nfl_data_py as nfl
import webbrowser

pbp_data = CFB.load_cfb_pbp(seasons=2021).to_pandas()

# Filter for Kansas State plays using 'drive.team.abbreviation'
pbp_ksu = pbp_data[pbp_data['drive.team.abbreviation'] == "KSU"].reset_index()
# pbp_td = pbp_ksu[pbp_ksu['type.abbreviation'] == "TD"].reset_index()

# Sample first 10 rows
# sample_data = pbp_td.head(20)



pbp_pass = pd.concat([
    pbp_ksu[pbp_ksu['pass'] == True].reset_index(),
])

print(pbp_pass.head(10))
# pbp_pass['passing_yards'] = np.where(pbp_pass['statYardage'] >= 20, "long", "short")
pbp_pass['passing_yards'] = np.where(pbp_pass['statYardage'] >= 20, "long", np.where(pbp_pass['statYardage'] < 0, "backward", "short"))

pbp_pass["passing_yards"] = np.where(pbp_pass["passing_yards"].isnull(), 0, pbp_pass["passing_yards"])

print(pbp_pass["passing_yards"].describe())

# # Convert to HTML table
# html_table = pbp_pass.to_html(index=False)  # Exclude row index

# # Save to a file (optional)
# with open("table.html", "w") as f:
#     f.write(html_table)

# # Define the path to your HTML file (replace with the actual path)
# html_file_path = "table.html"  

# # Open the file in the default web browser
# webbrowser.open(html_file_path)

# ## Epa for short passes
print("Short Passes")
print(pbp_pass.query('passing_yards == "short"')["statYardage"].describe())

# ## Epa for long passes
print("Long Passes")
print(pbp_pass.query('passing_yards == "long"')["statYardage"].describe())

# ## Epa for backward passes
print("Backward Passes")
print(pbp_pass.query('passing_yards == "backward"')["statYardage"].describe())


sns.set_theme(style="whitegrid", palette='colorblind')

pbp_pass_short = pbp_pass.query('passing_yards == "short"')
pbp_pass_long = pbp_pass.query('passing_yards == "long"')

print(pbp_pass_short)


# # # Histogram of passing yards on short passes
pbp_pass_hist_short = sns.histplot(pbp_pass_short,
                                      binwidth=1,
                                      x="statYardage", kde=True)
pbp_pass_hist_short.set_xlabel("Passing Yards")
pbp_pass_hist_short.set_ylabel("Count")

pbp_pass_hist_long = sns.histplot(pbp_pass_long,
                                      binwidth=1,
                                      x="statYardage", kde=True)
pbp_pass_hist_long.set_xlabel("Passing Yards")
pbp_pass_hist_long.set_ylabel("Count")
plt.show()

# Boxplot Passing Yards
pass_boxplot = sns.boxplot(data=pbp_pass, x="passing_yards", y="statYardage")
pass_boxplot.set(
  xlabel="Pass Length (long >= 20 yards, short < 20 yards)",
  ylabel="Yards gained or lost during play",
)
plt.show()

# pbp_pass_season = pbp_pass.groupby(["passer_id", "passer", "season"]).agg({"passing_yards": ["mean", "count"]})
# pbp_pass_season.columns = list(map('_'.join, pbp_pass_season.columns.values))
# pbp_pass_season.rename(columns={"passing_yards_mean": "YPA", "passing_yards_count": "n"}, inplace=True)

# # print(pbp_pass_season.sort_values(by="YPA", ascending=False))

# #Filter by minimum 225 attempts
# pbp_pass_season_min100 = pbp_pass_season.query('n >= 100').sort_values(by="YPA", ascending=False)
# # print(pbp_pass_season_min100.head())

# # Deep vs Short Passes
# pbp_pass_season_length = pbp_pass.groupby(["passer_id", "passer", "season", "passing_yards"]).agg({"passing_yards": ["mean", "count"]})

# # Flatten the multi-level column names
# pbp_pass_season_length.columns = list(map('_'.join, pbp_pass_season_length.columns.values))

# # Rename immediately after aggregation to ensure 'YPA' is available
# pbp_pass_season_length.rename(columns={"passing_yards_mean": "YPA", "passing_yards_count": "n"}, inplace=True)

# # Reset index to bring columns from the index back as regular columns
# pbp_pass_season_length.reset_index(inplace=True)

# # Define the query condition
# q_value = (
#     '(n >= 100 & ' +
#     'passing_yards == "short") | ' +
#     '(n >= 30 & ' +
#     'passing_yards == "long")'
# )
# print(pbp_pass_season_length)
# # Apply the query and reset index again
# pbp_pass_season_length = pbp_pass_season_length.query(q_value).reset_index()

# # Select the necessary columns 
# cols_save = ["passer_id", "passer", "season", "passing_yards", "YPA"]
# air_yards = pbp_pass_season_length[cols_save].copy()  # Now 'YPA' is available


# # Create lagged data 
# # Create lagged data (exclude last season)
# air_yards_lag = air_yards.copy()
# air_yards_lag["season"] += 1
# air_yards_lag.rename(columns={"YPA": "YPA_last"}, inplace=True)

# # Merge data with lagged data (still using inner join)
# pbp_pass_season_length = air_yards.merge(air_yards_lag, how='inner', on=["passer_id", "passer", "season", "passing_yards"])
# print(pbp_pass_season_length)


# # Display the results
# # print(pbp_pass_season_length[["passing_yards", "passer", "season", "YPA", "YPA_last"]].query('passer == "P.Mahomes" | passer == "A.Rodgers"').sort_values(["passer", "passing_yards", "season"]).to_string())
# print(len(pbp_pass_season_length.passer_id.unique()))


# # # Scatterplot of YPA vs YPA_last
# # sns.lmplot(data=pbp_pass_season_length, x="YPA", y="YPA_last", col="passing_yards")
# # plt.show()

# # # Correlation of YPA and YPA_last
# # print(pbp_pass_season_length.query('YPA.notnull() & YPA.notnull()').groupby('passing_yards')[['YPA', 'YPA_last']].corr())

# ## 2017 leaderboard
# print(pbp_pass_season_length.query('passing_yards == "long" & season == 2017')[["passer_id", "passer", "YPA"]].sort_values(by="YPA", ascending=False).head(10))
# print(pbp_pass_season_length.query('passing_yards == "long" & season == 2018')[["passer_id", "passer", "YPA"]].sort_values(by="YPA", ascending=False).head(10))