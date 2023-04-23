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
utils = Utils('data/keystrokes-recipes.csv')

def save_directly_follow_graph(csv_filepath, group_num):
    """
    Saves the directly follow graph for a given event log stored in a csv file

    Args:
        csv_filepath (str): event log file path
        group_num (int): event log for group number
    """
    dataframe = pd.read_csv(csv_filepath, sep=';')
    event_log = pm4py.format_dataframe(dataframe, case_id='case_id', activity_key='activity', timestamp_key='timestamp')
    event_log = pm4py.convert_to_event_log(dataframe)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(event_log)
    pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, 'results/process mining/groupnum{n}.png'.format(n=group_num))



user_to_recipes = utils.get_map_user_to_recipes()
ACTIONS = [';1st recipe submitted;', ';revision;', ';second recipe submitted;']
def generate_user_activity(user_index, case_id):
    """
    Generates the activity for one user in the event log
    For example, user 1 writes first recipe, revises, second recipe, third recipe - 
    then this is translated as 
    1;1st recipe submitted;time1
    1;revision;time2
    1;second recipe submitted;time3
    1;third recipe submitted;time4

    then when we go to the next user, case_id increments

    Args:
        user_index (int): index of user in data
        case_id (int): the case id for the user - it's basically the index of the user in their respective groups

    Returns:
        pd.DataFrame: a dataframe with the activity for the user
    """
    recipe_indices = user_to_recipes[user_index].copy()
    recipe_indices.append(utils.get_last_index_where_written(user_index))
    where_in_df = np.where(utils.df['user_id'] == utils.sorted_users[user_index])
    first_line = str(case_id) + ACTIONS[0] + utils.df.loc[where_in_df[0][0], 'event_date']             
    lines = [first_line]
    for i, index in enumerate(range(recipe_indices[0]+1, recipe_indices[-1]+1)):
        j = index
        is_new_recipe = index in recipe_indices
        while not is_new_recipe:
            line = ACTIONS[1] + utils.df.loc[where_in_df[0][i+1], 'event_date']
            lines.append(line)
            j+=1
            if j in recipe_indices: is_new_recipe = True
        try:
            if index in recipe_indices : lines.append(ACTIONS[2] + df.loc[where_in_df[0][i+1], 'event_date'])
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
                # 1 user input random text which accounts for a new recipe
                #  1 user has written 4 recipes so we remove them
                result.pop(i)
            else : result[i] = line 
    return  pd.DataFrame(sorted(set(result), key=result.index), columns=['case_id;activity;timestamp'])

def create_event_log(groupnum):
        """
        Creates an event log for a group of users. Basically joins the activity of all users in the group
        It will also save the directly follows graph for the group in the results folder
        Args:
            groupnum (int): the group number (1 or 2) 
        """
        event_log = []
        for j, user in enumerate(utils.INDICES[groupnum-1]):
            user_activity = generate_user_activity(user_index=user, case_id=j+1)
            event_log.append(user_activity)
        res = pd.concat(event_log)
        path = 'data/eventlogs/group{i}.csv'.format(i=groupnum)
        res.to_csv(path, index=False)
        save_directly_follow_graph(csv_filepath=path, group_num=groupnum)
        print("Event log for group {i} saved".format(i=groupnum))

create_event_log(groupnum=1)
create_event_log(groupnum=2)