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
sns.set_theme(style="whitegrid", palette='colorblind')
## Set down to integer
pbp_runs.down = pbp_runs.down.astype(int)
# Plot yards by down
g = sns.FacetGrid(data=pbp_runs, col="down", col_wrap=2)
g.map_dataframe(sns.histplot, x="rushing_yards")
plt.show()

sns.boxplot(data=pbp_runs.query("ydstogo == 10"), x="down", y="rushing_yards")
plt.show()