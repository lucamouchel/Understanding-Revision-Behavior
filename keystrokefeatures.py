"""
Relevant features:
* Time spent per user

* number of insertions and deletions - 
insertions are considered as any typed character, including whitespaces, 
excluding button presses such as `Ctrl` or `Shift`. Deletions are counted by 
the number of backspaces and the number of times the `Delete` button is pressed

* DI ratio : ratio of the number of deletions over the number of insertions - 
captures extent of editing and revisions.

* Efficiency: the ratio between number of characters typed and time spent - 
indicates general writing speed

Most of the features are inspired by ['Analysis of Keystroke Sequences in Writing Logs
'](https://doi.org/10.1002/ets2.12247)

This notebook aims at writing some generic code that can be used for any type 
of keystroke dataset, all the while respecting some conditions 
(ie having same names and same structure).

We will work with the raw dataset and generate some data for each user. 
For the dataset in our study, it is sometimes more interesting to have some more specific data for each user 
(like for each recipe they write, but for the purposes mentionned above, we generalise for each user)
    """

import pandas as pd
import numpy as np
import ast
import utils
from utils import *

dataset_path = 'data/keystrokes-recipes.csv'

df = pd.read_csv(dataset_path).sort_values(by=['user_id', 'event_date'])
df.to_csv(dataset_path, index=False)

def indices_where_written(user_id):
    return df[df['user_id'] == user_id].index 


def get_time_spent(user_id):
    indices = indices_where_written(user_id)
    first_time = df.loc[indices[0], 'event_date']
    last_time = df.loc[indices[-1], 'event_date']
    diff = utils.time_difference(first_time, last_time)
    if diff == 0: return 1
    return diff


def compute_num_insertions_deletions(user_id):
    indices = indices_where_written(user_id)
    num_insertions = 0
    num_deletions = 0
    for i in indices:
        assert df.iloc[i]['user_id'] == user_id
        ks = ast.literal_eval(df.loc[i, 'ks'])
        chars = [entry['character'] for entry in ks]
        num_insertions += len(list(filter(lambda _ : _  not in KEYWORDS, chars)))
        num_deletions += len(list(filter(lambda _ : _ == 'Backspace' or _ == 'Delete', chars)))
    return (num_insertions, num_deletions)

def get_DIRatio(num_insertions, num_deletions):
    return num_deletions / num_insertions

def get_efficiency(time_spent, num_insertions):
    return num_insertions / time_spent

ks_features = {}
for user in df['user_id'].unique():
    inserts, deletions = compute_num_insertions_deletions(user)
    time_spent = get_time_spent(user)
    ks_features[user] = {'time_spent': time_spent, 'num insert delete': (inserts, deletions) , 'DIRatio': get_DIRatio(inserts, deletions), 'efficiency': get_efficiency(time_spent, inserts)}