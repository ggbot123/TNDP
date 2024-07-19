import pandas as pd
from path import root_dir

df = pd.read_csv(f'{root_dir}\\preProcessing\\data\\unique_equivalence_stios.csv')
df_OD = pd.read_csv(f'{root_dir}\\preProcessing\\data\\OD_unique.csv')

merged_df = pd.merge(df_OD, df[['格式化站点编号', '在主城区']], left_on='格式化上车站点编号', right_on='格式化站点编号', how='left', sort=False)
merged_df = merged_df.rename(columns={'在主城区': '上车站点在主城区'}).drop(columns=['格式化站点编号'])
merged_df = pd.merge(merged_df, df[['格式化站点编号', '在主城区']], left_on='格式化下车站点编号', right_on='格式化站点编号', how='left')
merged_df = merged_df.rename(columns={'在主城区': '下车站点在主城区'}).drop(columns=['格式化站点编号'])
merged_df['OD在主城区'] = merged_df.apply(
    lambda row: row['上车站点在主城区']==True and row['下车站点在主城区']==True, axis=1)
print(merged_df)
assert merged_df['OD在主城区'].isnull().any() == False
merged_df = merged_df[merged_df['OD在主城区'] == True]

merged_df.to_csv(f'{root_dir}\\preProcessing\\data\\OD_unique_downtown.csv', index=False)