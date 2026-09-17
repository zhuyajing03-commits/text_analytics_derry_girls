import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# read data
df = pd.read_excel('derry_girls_negative_analysis.xlsx')

# select characters to be analyzed
characters = ['Erin', 'Clare', 'Michelle']
df_filtered = df[df['Speaker'].isin(characters)].copy()

# integrate episode label (e.g. S1E1)
df_filtered['Episode_Label'] = 'S' + df_filtered['Season'].astype(str) + 'E' + df_filtered['Episode'].astype(str)

# 1. plot the bar chart
plt.figure(figsize=(10, 6))
sns.countplot(data=df_filtered, x='Speaker', hue='Negative Emotion')
plt.title('Negative Emotions Distribution by Character')
plt.savefig('bar_chart.png')

# 2. plot the heatmap (count the instances of negative emotion for each character)
heatmap_data = df_filtered.groupby(['Speaker', 'Episode_Label']).size().unstack(fill_value=0)
# make sure the episodes are in order
sort_order = [f'S{s}E{e}' for s in [1, 2] for e in range(1, 7)]
heatmap_data = heatmap_data.reindex(columns=sort_order)

plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd')
plt.title('Negative Energy Intensity Heatmap')
plt.savefig('heatmap.png')