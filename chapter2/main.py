import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import nfl_data_py as nfl

seasons = range(2016, 2023)
pbp_data = nfl.import_pbp_data(seasons)

pbp_passing = pbp_data.query('play_type == "pass" and air_yards.notnull()').reset_index()

pbp_passing['pass_length_air_yards'] = np.where(pbp_passing['air_yards'] >= 20, "long", "short")

print(pbp_passing["passing_yards"].describe())

## Epa for short passes
print(pbp_passing.query('pass_length_air_yards == "short"')["epa"].describe())

## Epa for long passes
print(pbp_passing.query('pass_length_air_yards == "long"')["epa"].describe())

sns.set_theme(style="whitegrid", palette='colorblind')

pbp_passing_short = pbp_passing.query('pass_length_air_yards == "short"')

pbp_passing_hist_short = sns.histplot(pbp_passing_short, x="passing_yards", kde=True)
pbp_passing_hist_short.set_title("Passing Yards on Short Passes")
pbp_passing_hist_short.set_xlabel("Passing Yards")
pbp_passing_hist_short.set_ylabel("Count")
plt.show()