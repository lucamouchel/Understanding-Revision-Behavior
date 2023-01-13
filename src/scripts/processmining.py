import numpy as np
import pandas as pd
import os
import pm4py
from pm4py.visualization.petri_net import  visualizer as pn_vis_factory
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import  algorithm as alpha_miner
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath("src/util/utils.py"))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from util.utils import *

def save_directly_follow_graph(csv_filepath, group_num):
    dataframe = pd.read_csv(csv_filepath, sep=';')
    event_log = pm4py.format_dataframe(dataframe, case_id='case_id', activity_key='activity', timestamp_key='timestamp')
    event_log = pm4py.convert_to_event_log(dataframe)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(event_log)
    try:
        pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, 'results/process mining/groupnum{n}.png'.format(n=group_num))
    except: 
        print('user only has 1 recipe')

ACTIONS = [';1st recipe submitted;', ';revision;', ';second recipe submitted;']
def format_user_data(user_index, case_id=1):
    recipe_indices = map_[user_index].copy()
    if user_index == len(sorted_users) - 1: last_index_where_written = len(df)
    else: last_index_where_written = indices_of_first_attempts_per_user[user_index + 1]
    recipe_indices.append(last_index_where_written)

    where_in_df = np.where(df['user_id'] == sorted_users[user_index])

    first_line = str(case_id) + ACTIONS[0] + df.iloc[where_in_df[0][0]]['event_date']             
    lines = [first_line]
    for i, index in enumerate(range(recipe_indices[0]+1, recipe_indices[-1]+1)):
        j = index
        is_new_recipe = index in recipe_indices
        while not is_new_recipe:
            line = ACTIONS[1] + df.iloc[where_in_df[0][i+1]]['event_date']
            lines.append(line)
            j+=1
            if j in recipe_indices: is_new_recipe = True
        try:
            if index in recipe_indices : lines.append(ACTIONS[2] + df.iloc[where_in_df[0][i+1]]['event_date'])
        except: continue
        
    result = lines
    for i, line in enumerate(lines):
        if line.startswith(ACTIONS[1]):
            result[i] = str(case_id) + line
           
        elif line.startswith(ACTIONS[2]):
            second_recipe_already_submitted = any([ACTIONS[2] in l for l in result[:i]])
            if second_recipe_already_submitted:
                result[i] = str(case_id) + line.replace('second', 'third') 
            else : result[i] = str(case_id) + line
        
    for i, line in enumerate(result):
        replaced = ACTIONS[2].replace('second', 'third')
        if line.startswith(str(case_id) + replaced):
            has_submitted_third_recipe = any([replaced in l for l in result[:i]])
            if has_submitted_third_recipe:
                result[i] =";;"
            else : result[i] = line 
            
    return  pd.DataFrame(sorted(set(result), key=result.index), columns=['case_id;activity;timestamp'])

for group in [1,2]:
    dframes = []
    for j, user in enumerate(INDICES[group-1]):
        A = format_user_data(user_index=user, case_id=j+1)
        dframes.append(A)

    res = pd.concat(dframes)
    path = 'data/processMiningData/group{i}.csv'.format(i=group)
    res.to_csv(path, index=False)
    save_directly_follow_graph(csv_filepath=path, group_num=group)