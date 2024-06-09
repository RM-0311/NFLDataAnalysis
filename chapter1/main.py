import pandas as pd
import nfl_data_py as nfl

pbp = nfl.import_pbp_data([2021])
filter_criteria = 'play_type == "pass" and air_yards.notnull()'  # Filter for passing plays with air yards

pbp_p = (
  pbp.query(filter_criteria)
  .groupby(['passer_id', 'passer'])
  .agg({'air_yards': ['count', 'mean']})
)

pbp_p.columns = list(map("_".join, pbp_p.columns.values))
filtered_pbp_p = pbp_p[pbp_p['air_yards_count'] >= 100].sort_values(by=('air_yards_mean'), ascending=False)
print(filtered_pbp_p)
