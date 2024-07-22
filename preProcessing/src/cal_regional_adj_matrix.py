import pandas as pd
from cal_adj_matrix import manhattan
from path import root_dir

adj_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\adjacency_matrix.csv')
TAZ_df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\TAZ_centroids.csv')

for i in adj_df.index:
    for j in range(len(adj_df.columns)):
        adj_df.iloc[i, j] = manhattan(TAZ_df.loc[i, '纬度'], TAZ_df.loc[i, '经度'], TAZ_df.loc[j, '纬度'], TAZ_df.loc[j, '经度']) if adj_df.iloc[i, j] == 1 else -1
adj_df.to_csv(f'{root_dir}\\preProcessing\\data\\regional_dist_matrix.csv')