# -*- coding: utf-8 -*-
"""Women's Feature Selection and Model

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kpbsb-jRCiJeGV5pPqYqWGLi4FybgyRD
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFE
from operator import itemgetter
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn import tree

from google.colab import drive

# path from your drive to data
drive.mount('/content/drive/')

"""After data frames of the averages of the last n games have been created, each dataframe is split into an input matrix X 
and a binary classification matrix y to perform Feature Selection and Machine Learning. Initially, we look at data 
where n = 1, 5, 10, 15, and 20 to see how feature selection methods may vary based on n. 
We don't go above n=20 because we increase chances of model drift.
"""

path = '/content/drive/MyDrive/College/Senior_Year/SP/BEM_Ec_120/Project/Womens/data/n_avg_matchups/'

# n_data_dict[n][0]: dataframe of loaded csv; each row in data frame includes winner and loser stats
# n_data_dict[n][1]: X_pre_2023 (input for training data)
# n_data_dict[n][2]: y_pre_2023 (classification for training data)
# n_data_dict[n][3]: X_2023 (input for testing data)
# n_data_dict[n][4]: y_2023 (classification for testing data)

n = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,20,30}
n_data_dict = {}

for key in n:
  n_data_dict[key] = []
  n_data_dict[key].append(pd.read_csv(path + 'Mavg_matchups_n={}.csv'.format(key), index_col=0))

cols = ['Season', 'Score', 'FGM', 
        'FGA', 'FGp', 'FGM3', 'FGA3', 'FGp3', 'FTM', 
        'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl',
        'Blk', 'PF', 'TSP', 'EFGp', '3PTAr', 'FTAr', 
        'ORp', 'DRp', 'TRp', 'TR', 'Poss', 'OffRtg', 'DefRtg',
        'NetRtg', 'OffEff', 'DefEff', 'NetEff', 
        'PointDiff', 'Pace','PtsPer100', 'Ar', 'TOr', 
        'ATRatio', 'ELO', 'PythagoreanExp1', 'PythagoreanExp2']

win_cols = ['Season', 'WScore',
            'WFGM', 'WFGA', 'WFGp',
            'WFGM3', 'WFGA3', 'WFGp3', 'WFTM',
            'WFTA', 'WOR', 'WDR', 'WAst',
            'WTO', 'WStl', 'WBlk', 'WPF',
            'WTSP', 'WEFGp', 'W3PTAr',
            'WFTAr', 'WORp', 'WDRp', 'WTR', 'WPoss',
            'WOffRtg', 'WDefRtg', 'WNetRtg',
            'WNetRtg', 'WOffEff', 'WDefEff',
            'WNetEff', 'WPointDiff', 'WPace',
            'WPtsPer100', 'WAr', 'WTOr',
            'WATRatio', 'WELO', 'WPythagoreanExp1', 
            'WPythagoreanExp2']

lose_cols = ['Season', 'LScore',
            'LFGM', 'LFGA', 'LFGp',
            'LFGM3', 'LFGA3', 'LFGp3', 'LFTM',
            'LFTA', 'LOR', 'LDR', 'LAst',
            'LTO', 'LStl', 'LBlk', 'LPF',
            'LTSP', 'LEFGp', 'L3PTAr',
            'LFTAr', 'LORp', 'LDRp', 'WTR', 'LPoss',
            'LOffRtg', 'LDefRtg', 'LNetRtg',
            'LNetRtg', 'LOffEff', 'LDefEff',
            'LNetEff', 'LPointDiff', 'LPace',
            'LPtsPer100', 'LAr', 'LTOr',
            'LATRatio', 'LELO', 'LPythagoreanExp1', 
            'LPythagoreanExp2']

# Generate input and classification matrices and add them to n_data_dict given n
def generate_X_y(n):

  data = n_data_dict[n][0]

  X = pd.DataFrame(columns=cols)
  X_wins = data[win_cols].copy()
  X_losses = data[lose_cols].copy()

  X_wins.columns = cols
  X_losses.columns = cols

  ones = [1] * len(X_wins)
  y_wins = list(zip(X_wins['Season'], ones))
  zeros = [0] * len(X_losses)
  y_losses = list(zip(X_wins['Season'], zeros))
  y_list = np.concatenate((y_wins, y_losses), axis=0)

  X = pd.concat([X_wins.reset_index(drop=True), X_losses])
  y = pd.DataFrame(y_list, columns=['Season', 'WinOrLoss'])

  X_train = X.loc[X['Season'] != 2023]
  X_train = X_train.drop(['Season'], axis=1)
  y_train = y.loc[y['Season'] != 2023]
  y_train = y_train.drop(['Season'], axis=1)
  y_train = y_train['WinOrLoss'].to_numpy()

  n_data_dict[n].append(X_train)
  n_data_dict[n].append(y_train)

  X_test = X.loc[X['Season'] == 2023]
  X_test = X_test.drop(['Season'], axis=1)
  y_test = y.loc[y['Season'] == 2023]
  y_test = y_test.drop(['Season'], axis=1)
  y_test = y_test['WinOrLoss'].to_numpy()

  n_data_dict[n].append(X_test)
  n_data_dict[n].append(y_test)

for n in n_data_dict:
  generate_X_y(n)

"""# Determine optimal value of n"""

num_stat_combos = 50
features = cols[1:]
stat_combos = []

for i in range(num_stat_combos):
  num_features = random.randint(10, 25)
  combo = random.sample(features, k=num_features)
  stat_combos.append(combo)

n = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}

accuracies_list = []
accuracies_index = 0

for stat_list in stat_combos:
  # avg accuracies per n for specified stat combo
  accuracies_list_n = []
  for N in n:

    data = n_data_dict[N]
    X_train = data[1]
    y_train = data[2]

    X_train_select = X_train[stat_list]

    # average the accuracy over runs of the model within the training data
    accuracies = []
    for _ in range(50):

      X_train_train, X_train_test, y_train_train, y_train_test = train_test_split(X_train_select, y_train, test_size=0.25)

      gnb = GaussianNB()
      y_pred = gnb.fit(X_train_train, y_train_train).predict(X_train_test)
      accuracies.append(1- ((y_train_test != y_pred).sum())/X_train_test.shape[0])
    
    # print("N = {}, stats = {}".format(N, stat_list))
    mean = np.mean(accuracies)
    # print(mean)
    accuracies_list_n.append(mean)

  accuracies_list.append(accuracies_list_n)

n = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

plt.figure()
plt.xlabel("Average number of games taken as input (n)")
plt.ylabel("Accuracy")
plt.title("Women\'s Random Feature Subset Accuracy per n"")
plt.xticks(np.linspace(1,15,15))

for i in range(len(accuracies_list)):
  plt.plot(n, accuracies_list[i])

plt.show()

transposed_acc_list = np.transpose(accuracies_list)

avg_acc = []

for i in range(len(transposed_acc_list)):
  avg_acc.append(np.mean(transposed_acc_list[i]))

print(max(avg_acc))

plt.figure()
plt.xlabel("Average number of games taken as input (n)")
plt.ylabel("Accuracy")
plt.title("Women\'s Average Random Feature Subset Accuracy per n")
plt.xticks(np.linspace(1,15,15))

plt.plot(n, avg_acc)
plt.show()

"""Note, model accuracy is maximized at n = 9.

# Create correlation matrix of features for each n based on training data
"""

corr_matrix_n_list = [9]
for n in corr_matrix_n_list:
  X_pre_2023 = n_data_dict[n][1]
  plt.figure(figsize=(15, 12))
  plt.title('Women\'s Correlation Matrix, n={}'.format(n))
  correlation_heatmap = sns.heatmap(X_pre_2023.corr(), annot=True, fmt =".1f", annot_kws={"fontsize":8})
  plt.show()

"""Analysis: as n increases, the magnitude of correlation increases between features.

# Recursive Feature Elimination
"""

regressor = RandomForestRegressor(n_estimators=100, max_depth=10)
num_features_to_select = 1
rfe = RFE(regressor, n_features_to_select=num_features_to_select, verbose=3)
rfe.fit(n_data_dict[9][1], n_data_dict[9][2])

from operator import itemgetter
features = n_data_dict[9][1].columns.to_list()
for x, y in (sorted(zip(rfe.ranking_ , features), key=itemgetter(0))):
    print(x, y)

ranks = list(map(float, rfe.ranking_))
order = -1
minmax = MinMaxScaler()
ranks = minmax.fit_transform(order*np.array([ranks]).T).T[0]
ranks = map(lambda x: round(x, 2), ranks)

rank_dict = dict(zip(cols[1:], ranks))

print(rank_dict)

rank_dict = dict(sorted(rank_dict.items(), key=lambda item: item[1], reverse=True))

rank_df = pd.DataFrame(list(rank_dict.items()), columns=['Feature', 'RFE Ranking'])

fig, ax = plt.subplots(figsize=(8, 8))
plt.title('Women\'s RFE Ranking Plot at n=9')
sns.barplot(x="RFE Ranking", y="Feature", data=rank_df, ax=ax, palette="flare")
plt.show()

"""# Models

## SVM
"""

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler 
from sklearn.svm import SVC # "Support vector classifier"  
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

features_selected = ["OffRtg","Pace","TRp","PointDiff"]

X_train_selected = n_data_dict[9][1][features_selected]
x = X_train_selected.values
standard_scaler = StandardScaler()
x_scaled = standard_scaler.fit_transform(x)
X_train_selected = pd.DataFrame(x_scaled, columns=features_selected)

y_train_selected = n_data_dict[9][2]

X_train_train, X_train_test, y_train_train, y_train_test = train_test_split(X_train_selected, y_train_selected, test_size=0.3)

svm = SVC(kernel='rbf', gamma='auto', C=100, random_state=0, verbose=3)  
y_pred = svm.fit(X_train_train, y_train_train)
print("SVM accuracy: ", svm.score(X_train_test, y_train_test))

# 2023 data
X_test_2023 = n_data_dict[9][3][features_selected]
y_test_2023 = n_data_dict[9][4]

ree = svm.score(X_test_2023, y_test_2023)
print("SVM accuracy on 2023 season: ", svm.score(X_test_2023, y_test_2023))

"""## GNB"""

N = 9
data = pd.read_csv("/content/drive/MyDrive/Undergrad/Smore Year/Classes/BEM 120/data/avg_matchups_n={}.csv".format(N), sep=",")

stat_combos = [["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg"],
               ["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg","ELO"],
               ["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg","ELO","FGA"],
               ["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg","ELO","FGp3"],
               ["NetRtg","Pace","TRp","PythagoreanExp1","FGA","TOr","DefEff","Ar"],
               ['OffRtg', 'Pace', 'TRp', 'PointDiff', 'DefRtg', 'PythagoreanExp1', 'NetRtg', 'ELO', 'FGA'],
               ["NetRtg","ELO","ATRatio","Pace","DefEff","OffEff","DRp","ORp","FTAr","EFGp"],
               ["OffRtg","DefRtg","ELO","Ar","TOr","ORp","DRp","TRp","TSP","3PTAr"]]

for stat_list in stat_combos:

  cols = ['Season', 'Score', 'FGM', 
          'FGA', 'FGp', 'FGM3', 'FGA3', 'FGp3', 'FTM', 
          'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl',
          'Blk', 'PF', 'TSP', 'EFGp', '3PTAr', 'FTAr', 
          'ORp', 'DRp', 'TRp', 'TR', 'Poss', 'OffRtg', 'DefRtg',
          'NetRtg', 'OffEff', 'DefEff', 'NetEff', 
          'PointDiff', 'Pace','PtsPer100', 'Ar', 'TOr', 
          'ATRatio', 'ELO', 'PythagoreanExp1', 'PythagoreanExp2']

  X = pd.DataFrame(columns=cols)

  X_wins = data[['Season', 'WScore',
                        'WFGM', 'WFGA', 'WFGp',
                        'WFGM3', 'WFGA3', 'WFGp3', 'WFTM',
                        'WFTA', 'WOR', 'WDR', 'WAst',
                        'WTO', 'WStl', 'WBlk', 'WPF',
                        'WTSP', 'WEFGp', 'W3PTAr',
                        'WFTAr', 'WORp', 'WDRp', 'WTR', 'WPoss',
                        'WOffRtg', 'WDefRtg', 'WNetRtg',
                        'WNetRtg', 'WOffEff', 'WDefEff',
                        'WNetEff', 'WPointDiff', 'WPace',
                        'WPtsPer100', 'WAr', 'WTOr',
                        'WATRatio', 'WELO', 'WPythagoreanExp1', 'WPythagoreanExp2']].copy()
  X_wins.columns = cols

  X_losses = data[['Season', 'LScore',
                        'LFGM', 'LFGA', 'LFGp',
                        'LFGM3', 'LFGA3', 'LFGp3', 'LFTM',
                        'LFTA', 'LOR', 'LDR', 'LAst',
                        'LTO', 'LStl', 'LBlk', 'LPF',
                        'LTSP', 'LEFGp', 'L3PTAr',
                        'LFTAr', 'LORp', 'LDRp', 'WTR', 'LPoss',
                        'LOffRtg', 'LDefRtg', 'LNetRtg',
                        'LNetRtg', 'LOffEff', 'LDefEff',
                        'LNetEff', 'LPointDiff', 'LPace',
                        'LPtsPer100', 'LAr', 'LTOr',
                        'LATRatio', 'LELO', 'LPythagoreanExp1', 'LPythagoreanExp2']].copy().reset_index(drop=True)
  X_losses.columns = cols

  ones = [1] * len(X_wins)
  y_wins = list(zip(X_wins['Season'], ones))

  zeros = [0] * len(X_losses)
  y_losses = list(zip(X_wins['Season'], zeros))

  y_list = np.concatenate((y_wins, y_losses), axis=0)

  # X -> training data
  # y -> classification (1 for win, 0 for loss)
  X = pd.concat([X_wins.reset_index(drop=True), X_losses])
  y = pd.DataFrame(y_list, columns=['Season', 'WinOrLoss'])

  # data before 2023 is training split, 2023 is testing split
  X_train = X.loc[X['Season'] != 2023]
  X_train = X_train.drop(['Season'], axis=1)

  X_test = X.loc[X['Season'] == 2023]
  X_test = X_test.drop(['Season'], axis=1)

  y_train = y.loc[y['Season'] != 2023]
  y_train = y_train.drop(['Season'], axis=1)
  y_train = y_train['WinOrLoss'].to_numpy()

  y_test = y.loc[y['Season'] == 2023]
  y_test = y_test.drop(['Season'], axis=1)
  y_test = y_test['WinOrLoss'].to_numpy()

  X_train_select = X_train[stat_list]
  X_test_select = X_test[stat_list]

  # average the accuracy over runs of the model within the training data
  accuracies = []
  for _ in range(50):

    X_train_train, X_train_test, y_train_train, y_train_test = train_test_split(X_train_select, y_train, test_size=0.25)

    gnb = GaussianNB()
    y_pred = gnb.fit(X_train_train, y_train_train).predict(X_train_test)
    accuracies.append(1- ((y_train_test != y_pred).sum())/X_train_test.shape[0])
  
  print("stats = {}".format(stat_list))
  print(np.mean(accuracies))
  y_test_pred = gnb.fit(X_train_select, y_train).predict(X_test_select)
  print(1- ((y_test != y_test_pred).sum())/X_test.shape[0])

"""## DT"""

N = 9
data = pd.read_csv("/content/drive/MyDrive/Undergrad/Smore Year/Classes/BEM 120/data/avg_matchups_n={}.csv".format(N), sep=",")

stat_combos = [["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg"],
               ["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg","ELO"],
               ["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg","ELO","FGA"],
               ["OffRtg","Pace","TRp","PointDiff","DefRtg","PythagoreanExp1","NetRtg","ELO","FGp3"],
               ["NetRtg","Pace","TRp","PythagoreanExp1","FGA","TOr","DefEff","Ar"],
               ['OffRtg', 'Pace', 'TRp', 'PointDiff', 'DefRtg', 'PythagoreanExp1', 'NetRtg', 'ELO', 'FGA'],
               ["NetRtg","ELO","ATRatio","Pace","DefEff","OffEff","DRp","ORp","FTAr","EFGp"],
               ["OffRtg","DefRtg","ELO","Ar","TOr","ORp","DRp","TRp","TSP","3PTAr"]]

for stat_list in stat_combos:

  cols = ['Season', 'Score', 'FGM', 
          'FGA', 'FGp', 'FGM3', 'FGA3', 'FGp3', 'FTM', 
          'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl',
          'Blk', 'PF', 'TSP', 'EFGp', '3PTAr', 'FTAr', 
          'ORp', 'DRp', 'TRp', 'TR', 'Poss', 'OffRtg', 'DefRtg',
          'NetRtg', 'OffEff', 'DefEff', 'NetEff', 
          'PointDiff', 'Pace','PtsPer100', 'Ar', 'TOr', 
          'ATRatio', 'ELO', 'PythagoreanExp1', 'PythagoreanExp2']

  X = pd.DataFrame(columns=cols)

  X_wins = data[['Season', 'WScore',
                        'WFGM', 'WFGA', 'WFGp',
                        'WFGM3', 'WFGA3', 'WFGp3', 'WFTM',
                        'WFTA', 'WOR', 'WDR', 'WAst',
                        'WTO', 'WStl', 'WBlk', 'WPF',
                        'WTSP', 'WEFGp', 'W3PTAr',
                        'WFTAr', 'WORp', 'WDRp', 'WTR', 'WPoss',
                        'WOffRtg', 'WDefRtg', 'WNetRtg',
                        'WNetRtg', 'WOffEff', 'WDefEff',
                        'WNetEff', 'WPointDiff', 'WPace',
                        'WPtsPer100', 'WAr', 'WTOr',
                        'WATRatio', 'WELO', 'WPythagoreanExp1', 'WPythagoreanExp2']].copy()
  X_wins.columns = cols

  X_losses = data[['Season', 'LScore',
                        'LFGM', 'LFGA', 'LFGp',
                        'LFGM3', 'LFGA3', 'LFGp3', 'LFTM',
                        'LFTA', 'LOR', 'LDR', 'LAst',
                        'LTO', 'LStl', 'LBlk', 'LPF',
                        'LTSP', 'LEFGp', 'L3PTAr',
                        'LFTAr', 'LORp', 'LDRp', 'WTR', 'LPoss',
                        'LOffRtg', 'LDefRtg', 'LNetRtg',
                        'LNetRtg', 'LOffEff', 'LDefEff',
                        'LNetEff', 'LPointDiff', 'LPace',
                        'LPtsPer100', 'LAr', 'LTOr',
                        'LATRatio', 'LELO', 'LPythagoreanExp1', 'LPythagoreanExp2']].copy().reset_index(drop=True)
  X_losses.columns = cols

  ones = [1] * len(X_wins)
  y_wins = list(zip(X_wins['Season'], ones))

  zeros = [0] * len(X_losses)
  y_losses = list(zip(X_wins['Season'], zeros))

  y_list = np.concatenate((y_wins, y_losses), axis=0)

  # X -> training data
  # y -> classification (1 for win, 0 for loss)
  X = pd.concat([X_wins.reset_index(drop=True), X_losses])
  y = pd.DataFrame(y_list, columns=['Season', 'WinOrLoss'])

  # data before 2023 is training split, 2023 is testing split
  X_train = X.loc[X['Season'] != 2023]
  X_train = X_train.drop(['Season'], axis=1)

  X_test = X.loc[X['Season'] == 2023]
  X_test = X_test.drop(['Season'], axis=1)

  y_train = y.loc[y['Season'] != 2023]
  y_train = y_train.drop(['Season'], axis=1)
  y_train = y_train['WinOrLoss'].to_numpy()

  y_test = y.loc[y['Season'] == 2023]
  y_test = y_test.drop(['Season'], axis=1)
  y_test = y_test['WinOrLoss'].to_numpy()

  X_train_select = X_train[stat_list]
  X_test_select = X_test[stat_list]

  # average the accuracy over runs of the model within the training data
  accuracies = []
  for _ in range(50):

    X_train_train, X_train_test, y_train_train, y_train_test = train_test_split(X_train_select, y_train, test_size=0.25)

    model = tree.DecisionTreeClassifier(random_state=5)
    y_pred = model.fit(X_train_train, y_train_train).predict(X_train_test)
    accuracies.append(1- ((y_train_test != y_pred).sum())/X_train_test.shape[0])
  
  print("stats = {}".format(stat_list))
  print(np.mean(accuracies))
  y_test_pred = model.fit(X_train_select, y_train).predict(X_test_select)
  print(1- ((y_test != y_test_pred).sum())/X_test.shape[0])