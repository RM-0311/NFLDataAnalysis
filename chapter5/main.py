import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import nfl_data_py as nfl
import statsmodels.formula.api as smf
import statsmodels.api as sm
import seaborn as sns

seasons = range(2016, 2022 + 1)
pbp = nfl.import_pbp_data(seasons)

pbp_pass = pbp.query('play_type == "pass" & passer_id.notnull() & air_yards.notnull()').reset_index()

sns.set_theme(style="whitegrid", palette="colorblind")

pass_pct = pbp_pass.query('0 < air_yards <= 20').groupby('air_yards').agg({"complete_pass": ["mean"]})
pass_pct.columns = list(map("_".join, pass_pct.columns))
pass_pct.reset_index(inplace=True)
pass_pct.rename(columns={"complete_pass_mean": "comp_pct"}, inplace=True)

# sns.regplot(data=pass_pct, x="air_yards", y="comp_pct", ci=None, line_kws={"color": "red"})
# plt.show()

complete_ay = smf.glm(formula="complete_pass ~ air_yards", data=pbp_pass, family=sm.families.Binomial()).fit()
# print(complete_ay.summary())

# sns.regplot(data=pbp_pass, x="air_yards", y="complete_pass", logistic=True, ci=None, line_kws={"color": "red"}, scatter_kws={"alpha": 0.05})
# plt.show()

pbp_pass["exp_completion"] = complete_ay.predict()
pbp_pass["cpoe"] = pbp_pass["complete_pass"] - pbp_pass["exp_completion"]

cpoe = pbp_pass.groupby(["season", "passer_id", "passer"]).agg({"cpoe": ["count", "mean"], "complete_pass": ["mean"]})
cpoe.columns = list(map("_".join, cpoe.columns))
cpoe.reset_index(inplace=True)
cpoe = cpoe.rename(columns = {"cpoe_count": "n", "cpoe_mean": "cpoe", "complete_pass_mean": "comp_pct"}).query('n > 100')

# print(cpoe.sort_values("cpoe", ascending=False))

pbp_pass["down"] = pbp_pass["down"].astype(str)
pbp_pass["qb_hit"] = pbp_pass["qb_hit"].astype(str)

pbp_pass_no_miss = pbp_pass[["passer", "passer_id", "season", "down", "qb_hit", "complete_pass", "ydstogo", "yardline_100", "air_yards", "pass_location"]].dropna(axis = 0)

complete_more = smf.glm(formula="complete_pass ~ down * ydstogo + yardline_100 + air_yards + pass_location + qb_hit", data=pbp_pass_no_miss, family=sm.families.Binomial()).fit()
pbp_pass_no_miss["exp_completion"] = complete_more.predict()
pbp_pass_no_miss["cpoe"] = pbp_pass_no_miss["complete_pass"] - pbp_pass_no_miss["exp_completion"]

cpoe_more = pbp_pass_no_miss.groupby(["season", "passer_id", "passer"]).agg({"cpoe": ["count", "mean"], "complete_pass": ["mean"], "exp_completion": ["mean"]})
cpoe_more.columns = list(map("_".join, cpoe_more.columns))
cpoe_more.reset_index(inplace=True)

cpoe_more = cpoe_more.rename(columns = {"cpoe_count": "n", "cpoe_mean": "cpoe", "complete_pass_mean": "comp_pct", "exp_completion_mean": "exp_completion"}).query('n > 100')

# print(cpoe_more.sort_values("cpoe", ascending=False))
cols_keep = ["season", "passer_id", "passer", "cpoe", "comp_pct", "exp_completion"]

cpoe_now = cpoe_more[cols_keep].copy()
cpoe_last = cpoe_now[cols_keep].copy()

cpoe_last.rename(columns = {"cpoe": "cpoe_last", "comp_pct": "comp_pct_last", "exp_completion": "exp_completion_last"}, inplace=True)
cpoe_last["season"] = cpoe_last["season"] + 1

cpoe_lag = cpoe_now.merge(cpoe_last, on = ["passer_id", "passer", "season"], how = "inner")

print(cpoe_lag[["comp_pct_last", "comp_pct"]].corr())
print(cpoe_lag[["cpoe_last", "cpoe"]].corr())
print(cpoe_lag[["exp_completion_last", "exp_completion"]].corr())