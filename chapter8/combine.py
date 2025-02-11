import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.impute import KNNImputer
from sklearn.decomposition import PCA
from scipy.cluster.vq import vq, kmeans

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
# sns.regplot(data=combine, x="40yd", y="3Cone", line_kws={"color": "red"})

combine_knn_file = "combine_data_knn.csv"
col_impute = ["Ht", "Wt", "40yd", "Vertical", "Bench", "Broad Jump", "3Cone", "Shuttle"]

if not os.path.isfile(combine_knn_file):
  combine_knn = combine.drop(col_impute, axis=1)
  imputer = KNNImputer(n_neighbors=10)
  knn_out = imputer.fit_transform(combine[col_impute])
  knn_out = pd.DataFrame(knn_out)
  knn_out.columns = col_impute
  combine_knn = pd.concat([combine_knn, knn_out], axis=1)
  combine_knn.to_csv(combine_knn_file)
else:
  combine_knn = pd.read_csv(combine_knn_file)

pca_wt_ht = PCA(svd_solver="full")
wt_ht = combine[["Wt", "Ht"]].query("Wt.notnull() and Ht.notnull()").copy()

pca_fit_wt_ht = pca_wt_ht.fit_transform(wt_ht)

# plt.plot(pca_fit_wt_ht[:, 0], pca_fit_wt_ht[:, 1], "o")

scaled_combine_knn = (
  combine_knn[col_impute] - combine_knn[col_impute].mean()) / combine_knn[col_impute].std()
pca = PCA(svd_solver="full")
pca_fit = pca.fit_transform(scaled_combine_knn)
rotation = pd.DataFrame(pca.components_, index=col_impute)
print(pca.explained_variance_)
pca_percent = pca.explained_variance_ratio_.round(4) * 100
print(pca_percent)

pca_fit = pd.DataFrame(pca_fit)
pca_fit.columns = ["PC" + str(x + 1) for x in range(len(pca_fit.columns))]
combine_knn = pd.concat([combine_knn, pca_fit], axis=1)
# sns.scatterplot(data=combine_knn, x="PC1", y="PC2", hue="Pos")

k_means_fit = kmeans(combine_knn[["PC1", "PC2"]], 6, seed = 1234)
combine_knn["cluster"] = vq(combine_knn[["PC1", "PC2"]], k_means_fit[0])[0]
# print(
#   combine_knn.query("cluster == 1")
#   .groupby("Pos")
#   .agg({"Ht": ["count", "mean"], "Wt": ["count", "mean"]}))

combine_knn_cluster = combine_knn.groupby(["cluster", "Pos"]).agg({"Ht": ["count", "mean"], "Wt": ["mean"]})
combine_knn_cluster.columns = list(map("_".join, combine_knn_cluster.columns))
combine_knn_cluster.reset_index(inplace=True)
combine_knn_cluster.rename(columns={"Ht_count": "n",
                                     "Ht_mean": "Ht",
                                     "Wt_mean": "Wt"}, inplace=True)

combine_knn_cluster.cluster = combine_knn_cluster.cluster.astype(str)
# sns.catplot(combine_knn_cluster, x="n", y="Pos", col="cluster", col_wrap=3, kind="bar")

print(combine_knn_cluster.groupby("cluster").agg({"Ht": ["mean"], "Wt": ["mean"]}))