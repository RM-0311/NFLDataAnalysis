import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

combine = pd.DataFrame()
for i in range(2000, 2024 + 1):
  url = (
    "https://www.pro-football-reference.com/draft/" + str(i) + "-combine.htm"
  )
  web_data = pd.read_html(url)[0]
  web_data["Season"] = i
  web_data = web_data.query('Ht != "Ht"')
  combine = pd.concat([combine, web_data])

combine.reset_index(drop=True, inplace=True)
combine.to_csv("combine_data.csv", index=False)

combine[["Ht_ft", "Ht_in"]] = combine["Ht"].str.split("-", expand=True)
combine = combine.astype({
  "Wt": float,
  "40yd": float,
  "Vertical": float,
  "Bench": float,
  "Broad Jump": float,
  "3Cone": float,
  "Shuttle": float,
  "Ht_ft": float,
  "Ht_in": float
})

combine["Ht"] = (combine["Ht_ft"] * 12.0 + combine["Ht_in"])

combine.drop(["Ht_ft", "Ht_in"], axis=1, inplace=True)

sns.set_theme(style="whitegrid", palette="colorblind")
# sns.regplot(data=combine, x="Ht", y="Wt")

# sns.regplot(data=combine, x="Wt", y="40yd", line_kws={"color": "red"})
# sns.regplot(data=combine, x="40yd", y="Vertical", line_kws={"color": "red"})
sns.regplot(data=combine, x="40yd", y="3Cone", line_kws={"color": "red"})


plt.show()
