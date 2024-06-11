import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import nfl_data_py as nfl
import statsmodels.formula.api as smf

# Load the data
seasons = range(2016, 2022 + 1)
pbp_data = nfl.import_pbp_data(seasons)

pbp_runs = pbp_data.query('play_type == "run" & rusher_id.notnull()').reset_index()
pbp_runs.loc[pbp_runs.rushing_yards.isnull(), "rushing_yards"] = 0

# Initial Plot
# sns.set_theme(style="whitegrid", palette='colorblind')
# sns.scatterplot(data=pbp_runs, x="ydstogo", y="rushing_yards")
# plt.show()

# Reg Plot
# sns.regplot(data=pbp_runs, x="ydstogo", y="rushing_yards")
# plt.show()

# Average the data
# pbp_runs_avg = pbp_runs.groupby(["ydstogo"]).agg({"rushing_yards": ["mean"]})
# pbp_runs_avg.columns = list(map('_'.join, pbp_runs_avg.columns))
# pbp_runs_avg.reset_index(inplace=True)

# sns.regplot(data=pbp_runs_avg, x="ydstogo", y="rushing_yards_mean")
# plt.show()

# Simple Regression
yards_to_go = smf.ols(formula="rushing_yards ~ 1 + ydstogo", data=pbp_runs)

# print(yards_to_go.fit().summary())

pbp_runs["ryoe"] = yards_to_go.fit().resid

# Rush Yards over Expected
ryoe = pbp_runs.groupby(["season", "rusher_id", "rusher"]).agg({"ryoe": ["mean", "sum", "count"], "rushing_yards": ["mean"]})
ryoe.columns = list(map('_'.join, ryoe.columns))
ryoe.reset_index(inplace=True)
ryoe = ryoe.rename(columns={"ryoe_mean": "ryoe_per", "ryoe_sum": "ryoe_total", "ryoe_count": "n", "rushing_yards_mean": "YPC"}).query("n >= 50")

# print(ryoe.sort_values("ryoe_per", ascending=False))

# RYOE vs YPC
cols_keep = ["season", "rusher_id", "rusher", "ryoe_per", "YPC"]
ryoe_curr = ryoe[cols_keep].copy()
ryoe_last = ryoe[cols_keep].copy()
ryoe_last = ryoe_last.rename(columns={"ryoe_per": "ryoe_per_last", "YPC": "YPC_last"})
ryoe_last["season"] = ryoe_last["season"] + 1
ryoe_lag = ryoe_curr.merge(ryoe_last, how='inner', on=["season", "rusher_id", "rusher"])
print(ryoe_lag[["YPC_last", "YPC"]].corr())
print(ryoe_lag[["ryoe_per_last", "ryoe_per"]].corr())