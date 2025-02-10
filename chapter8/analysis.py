import numpy as np
import os
from sklearn.impute import KNNImputer

combine_knn_file = "combine_data_knn.csv"
col_impute = ["Ht", "Wt", "40yd", "Vertical", "Bench", "Broad Jump", "3Cone", "Shuttle"]

if not os.path.isfile(combine_knn_file):