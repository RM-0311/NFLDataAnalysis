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