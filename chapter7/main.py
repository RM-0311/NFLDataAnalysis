import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import numpy as np

url = "https://www.pro-football-reference.com/years/2023/draft.htm"

draft = pd.DataFrame()
for i in range(2000,2023 + 1):
  url = "https://www.pro-football-reference.com/years/" + \
    str(i) + \
    "/draft.htm"
  web_data = pd.read_html(url, header=1)[0]
  web_data["Season"] = i
  web_data = web_data.query('Tm != "Tm"')
  draft = pd.concat([draft, web_data])

draft.reset_index(drop=True, inplace=True)
conditions = [
  (draft.Tm == "SDG"),
  (draft.Tm == "OAK"),
  (draft.Tm == "STL"),
]
choices = ["LAC", "LV", "LAR"]
draft["Tm"] = np.select(conditions, choices, default=draft.Tm)

draft.loc[draft["DrAV"].isnull(), "DrAV"] = 0
draft.to_csv("draft.csv", index=False)

draft_use = draft[["Season", "Pick", "Tm", "Player", "Pos", "wAV", "DrAV"]]

sns.set_theme(style="whitegrid", palette="colorblind")
draft_use_pre2020 = draft_use.query("Season <= 2020")
draft_use_pre2020 = draft_use_pre2020.astype({"Pick": int, "DrAV": float})
# sns.regplot(data=draft_use_pre2020,
#             x="Pick",
#             y="DrAV",
#             line_kws={"color": "red"},
#             scatter_kws={"alpha": 0.2})

draft_chart = draft_use_pre2020.groupby(["Pick"]).agg({"DrAV": ["mean"]})
draft_chart.columns = list(map("_".join, draft_chart.columns))
draft_chart.loc[draft_chart.DrAV_mean.isnull()] = 0
draft_chart["roll_DrAV"] = (
  draft_chart["DrAV_mean"]
  .rolling(window=13, min_periods=1, center=True)
  .mean()
  )
# sns.scatterplot(draft_chart, x="Pick", y="roll_DrAV", color="red")
draft_chart.reset_index(inplace=True)
draft_chart["roll_DrAV_log"] = np.log(draft_chart["roll_DrAV"] + 1)

DrAV_pick_fit = smf.ols(formula="roll_DrAV_log ~ Pick", data=draft_chart).fit()

draft_chart["fitted_DrAV"] = np.exp(DrAV_pick_fit.predict()) - 1

draft_use_pre2020 = draft_use_pre2020.merge(draft_chart[["Pick", "fitted_DrAV"]], on="Pick")
draft_use_pre2020["OE"] = (draft_use_pre2020["DrAV"] - draft_use_pre2020["fitted_DrAV"])
draft_use_pre2020.groupby("Tm").agg({"OE": ["count", "mean", "std"]}).reset_index().sort_values(("OE", "mean"), ascending=False)

draft_use_pre2020 = draft_use_pre2020.merge(draft_chart[["Pick", "fitted_DrAV"]], on="Pick")
draft_use_pre2020_tm = draft_use_pre2020.groupby("Tm").agg({"OE": ["count", "mean", "std"]}).reset_index().sort_values(("OE", "mean"), ascending=False)
draft_use_pre2020_tm.columns = list(map("_".join, draft_use_pre2020_tm.columns))
draft_use_pre2020_tm.reset_index(inplace=True)
draft_use_pre2020_tm["se"] = (draft_use_pre2020_tm["OE_std"] / np.sqrt(draft_use_pre2020_tm["OE_count"]))
draft_use_pre2020_tm["lower bound"] = draft_use_pre2020_tm["OE_mean"] - 1.96 * draft_use_pre2020_tm["se"]
draft_use_pre2020_tm["upper bound"] = draft_use_pre2020_tm["OE_mean"] + 1.96 * draft_use_pre2020_tm["se"]

print(draft_use_pre2020_tm)