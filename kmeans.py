"""
Created on Sat Nov 25 12:39:26 2017

@author: yuliabarannikova
"""

from pymongo import MongoClient
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

plt.rcParams['figure.figsize'] = (10, 9)


client = MongoClient()

db = client.league_of_legends

playtraces_gt_27 = db.playtraces_gt_27

actionTypes = playtraces_gt_27.distinct('playtrace.type')
df =  pd.DataFrame(list(playtraces_gt_27.find()))

def get_period_range_list(end,n):
    period_range_list = []
    start = 0
    period_len = end/n
    for i in range(n):
        period_range_list.append((int(start), int(start+period_len)))
        start += period_len
    return period_range_list
            
# create a df qith action counts for n periods
def divide(df,n):
    action_count_dict = {k:0 for k in ["%s_count_%s" % (a,p) for p in range(n) for a in actionTypes]}
    action_count_dict['id'] = ''
    new_df = pd.DataFrame(columns=action_count_dict.keys())
    for i in range(len(df)):
        row = df.iloc[i,:].copy()
        row_action_count_dict = action_count_dict.copy()
        if row['playtrace'] != []:
            last_action_time=row['playtrace'][-1]['timestamp']
            period_range_list = get_period_range_list(last_action_time,n)
            for action in row['playtrace']:
                for p in period_range_list:
                    if action['timestamp'] in range(p[0],p[1]):
                        t = period_range_list.index(p)
                k = "%s_count_%s" % (action['type'], t)
                row_action_count_dict[k] += 1
        row_action_count_dict['id']=row['id']
        new_df=new_df.append(row_action_count_dict, ignore_index=True)
    return new_df


from sklearn.cluster import KMeans
df_4_periods = divide(df,4)
X_4 = df_4_periods.iloc[:,:-1].values
X_1 = df_1_period.iloc[:,:-1].values
X_6 = df_6_periods.iloc[:,:-1].values
X_10 = df_10_periods.iloc[:,:-1].values
X_20 = df_20_periods.iloc[:,:-1].values

from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X_6_pca = pca.fit_transform(X_6)
f1 = X_6_pca[:,0]
f2 = X_6_pca[:,1]
plt.scatter(f1,f2, s=1, c='black')


pca = PCA(n_components=2)
X_4_pca = pca.fit_transform(X_4)
variance4=pca.explained_variance_ratio_
f1 = X_4_pca[:,0]
f2 = X_4_pca[:,1]
plt.scatter(f1,f2, s=1, c='black')

pca = PCA()
X_10_pca = pca.fit_transform(X_10)
variance10=pca.explained_variance_ratio_
f1 = X_10_pca[:,0]
f2 = X_10_pca[:,1]
plt.scatter(f1,f2, s=1, c='black')
plt.show()

s=MinMaxScaler()
X_10_scaled=s.fit_transform(X_10)
X_10_pca_scaled = pca.fit_transform(X_10_scaled)
variance10_scaled=pca.explained_variance_ratio_
f1 = X_10_pca_scaled[:,0]
f2 = X_10_pca_scaled[:,1]
plt.scatter(f1,f2, s=1, c='black')
plt.show()


pca = PCA()
X_20_pca = pca.fit_transform(X_20)
variance20=pca.explained_variance_ratio_
f1 = X_20_pca[:,0]
f2 = X_20_pca[:,1]
plt.scatter(f1,f2, s=1, c='black')
plt.show()

s=MinMaxScaler()
X_20_scaled=s.fit_transform(X_20)
X_20_pca_scaled = pca.fit_transform(X_20_scaled)
variance10_scaled=pca.explained_variance_ratio_
f1 = X_20_pca_scaled[:,0]
f2 = X_20_pca_scaled[:,1]
plt.scatter(f1,f2, s=1, c='black')
plt.show()


from sklearn.preprocessing import StandardScaler, MinMaxScaler
sc = StandardScaler()
X_20= sc.fit_transform(X_20)

s = MinMaxScaler()
X_4 = s.fit_transform(X_4)

s=MinMaxScaler()
X_10_scaled=s.fit_transform(X_10)

s=MinMaxScaler()
X_6=s.fit_transform(X_6)


s=MinMaxScaler()
X_20=s.fit_transform(X_20)


kmeans = KMeans(n_clusters=2)
# Fitting the input data
kmeans.fit(X_6_pca)
# Getting the cluster labels
labels = kmeans.predict(X_6_pca)
# Centroid values
centroids = kmeans.cluster_centers_

plt.scatter(f1, f2, c=labels, s=1, cmap='rainbow')
plt.scatter(centroids[:, 0], centroids[:, 1], c='black', s=10)

from scipy.spatial.distance import cdist
distortions=[]
for k in range(1,10):
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(X_4_pca)
    distortions.append(sum(np.min(cdist(X_4_pca, kmeans.cluster_centers_, 'euclidean'), axis=1)) / X_4_pca.shape[0])

plt.plot(range(1,10), distortions, 'bx-')
plt.xlabel('k')
plt.ylabel('Distortion')
plt.title('The Elbow Method showing the optimal k')
plt.show()

