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
  .rolling(window=13)
  .mean()
  )
sns.scatterplot(draft_chart, x="Pick", y="roll_DrAV", color="red")
plt.show()