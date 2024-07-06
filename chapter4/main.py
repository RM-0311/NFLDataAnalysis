import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import nfl_data_py as nfl
import statsmodels.formula.api as smf

# Load the data
seasons = range(2016, 2022 + 1)
pbp_data = nfl.import_pbp_data(seasons)

pbp_runs = pbp_data.query('play_type == "run" & rusher_id.notnull() & ' + 'down.notnull() & run_location.notnull()').reset_index()
pbp_runs.loc[pbp_runs.rushing_yards.isnull(), "rushing_yards"] = 0

# Histogram
# sns.set_theme(style="whitegrid", palette='colorblind')
## Set down to integer
pbp_runs.down = pbp_runs.down.astype(int)
# Plot yards by down
# g = sns.FacetGrid(data=pbp_runs, col="down", col_wrap=2)
# g.map_dataframe(sns.histplot, x="rushing_yards")
# plt.show()

# sns.boxplot(data=pbp_runs.query("ydstogo == 10"), x="down", y="rushing_yards")
# plt.show()

# sns.regplot(data=pbp_runs,
#             x="yardline_100",
#             y="rushing_yards",
#             scatter_kws={"alpha": 0.25},
#             line_kws={"color": "red"}
#           )
# plt.show()

pbp_runs_y100 =pbp_runs.groupby("yardline_100").agg({'rushing_yards': ['mean']})

pbp_runs_y100.columns = list(map('_'.join, pbp_runs_y100.columns))

pbp_runs_y100.reset_index(inplace=True)

# sns.regplot(data=pbp_runs_y100,
#             x="yardline_100",
#             y="rushing_yards_mean",
#             scatter_kws={"alpha": 0.25},
#             line_kws={"color": "red"}
#           )
# plt.show()

# sns.boxplot(data=pbp_runs, x="run_location", y="rushing_yards")
# plt.show()

pbp_runs_sd = pbp_runs.groupby("score_differential").agg({'rushing_yards': ['mean']})
pbp_runs_sd.columns = list(map('_'.join, pbp_runs_sd.columns))
pbp_runs_sd.reset_index(inplace=True)

# sns.regplot(data=pbp_runs_sd, x="score_differential", y="rushing_yards_mean", scatter_kws={"alpha": 0.25}, line_kws={"color": "red"})
# plt.show()

# Multiple Linear Regression
pbp_runs.down = pbp_runs.down.astype(str)
expected_yards = smf.ols(data=pbp_runs, formula="rushing_yards ~ 1 + down + ydstogo + down:ydstogo + yardline_100 + run_location + score_differential").fit()

pbp_runs["ryoe"] = expected_yards.resid
# print(expected_yards.summary())

ryoe = pbp_runs.groupby(["season", "rusher_id", "rusher"]).agg({"ryoe": ["count", "sum", "mean"], "rushing_yards": ["mean"]})

ryoe.columns = list(map('_'.join, ryoe.columns))
ryoe.reset_index(inplace=True)

ryoe = ryoe.rename(columns={"ryoe_count": "n", "ryoe_sum": "ryoe_total", "ryoe_mean": "ryoe_per", "rushing_yards_mean": "YPC"}).query("n >= 50")
# print(ryoe.sort_values("ryoe_per", ascending=False))

cols_keep = ["season", "rusher_id", "rusher", "ryoe_per", "YPC"]
ryoe_last = pd.DataFrame()
ryoe_curr = pd.DataFrame()
ryoe_curr = ryoe[cols_keep].copy()
ryoe_last = ryoe[cols_keep].copy()
ryoe_last.rename(columns={"ryoe_per": "ryoe_per_last", "YPC": "YPC_last"}, inplace=True)
print(ryoe_last)
ryoe_last["season"] = ryoe_last["season"] + 1
ryoe_lag = ryoe_curr.merge(ryoe_last, how='inner', on=["rusher_id", "rusher", "season"])

print(ryoe_lag[["YPC_last", "YPC"]].corr())
print(ryoe_lag[["ryoe_per_last", "ryoe_per"]].corr())