import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import nfl_data_py as nfl
import statsmodels.formula.api as smf
import statsmodels.api as sm
import seaborn as sns
from scipy.stats import poisson

seasons = range(2016, 2022 + 1)
pbp = nfl.import_pbp_data(seasons)

pbp_pass = pbp.query('passer_id.notnull()').reset_index()