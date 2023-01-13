from datetime import datetime
import nltk.corpus 
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq
import pandas as pd
import gensim.downloader as api
from scipy import spatial
import numpy as np
import pandas as pd
import ast
import numpy as np

df = pd.read_csv('./data/keystrokes-recipes-modified.csv')
indices_of_first_attempts_per_user = df.groupby('user_id').head(1).index
noisy_punct = [',', '.', '-', ':', '(', ')']
all_keystrokes = list(map(lambda _ : ast.literal_eval(_) , df['ks'].values))
KEYWORDS = ['Alt', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'Backspace', 'CapsLock', 'Control', 'Delete', 'End', 'Enter', 'Home', 'Meta', 'PageUp', 'PageDown', 'PrintScreen','Shift', 'Tab']
sorted_users = sorted(df['user_id'].unique())
matching_data = pd.read_csv('data/groupmatching.csv')
users_to_groups = dict(pd.read_csv('data/groupmatching.csv').filter(['user_id', 'group']).values)
s = matching_data.sort_values(by=['group', 'user_id'], ascending=True)
INDICES = []

"""
    Basically what we do here is simple. We have the data matching each user to which group they belong to.
    So what we do is we create an array INDICES. We create a dictionnary which maps each group to the users in it.
    Then iterate over the users of each group and find their index in the sorted users array. 

    so INDICES has 2 arrays, each containing the indices of the users in that group.
    
"""
groups = {1: [], 2: []}
for i, dic in enumerate(s.values):
    user = dic[1]
    if user in sorted_users:
        group = users_to_groups[user]
        if group == 2:
            groups[1].append(user)
        elif group == 4:
            groups[2].append(user)


for group in [1,2]:
    indices = []
    for user in groups[group]:
        i = np.where(np.array(sorted_users) == user)
        indices.append(i[0][0])
    INDICES.append(indices)


def get_last_index_where_written(user_index, indices_of_first_attempts_per_user, num_users, num_entries):
    """
    Returns the last index where a user has written in the dataset
    ie if user 0 wrote at indices [0,1,2,3,4,5] then this would return 6, in order to include index 5 
    when iterating over user entries

    Args:
        user_index (int): index of user in the dataset
        indices_of_first_attempts_per_user (list): indices of first index where each user has written 
        num_users (int): number of users
        num_entries (int): number of entries in  the dataset

    Returns:
        int: index of last index where user has written
    """
    return indices_of_first_attempts_per_user[user_index + 1] if  user_index != num_users - 1 else num_entries - 1

def has_revision(user_index, recipe_num, function):
    """
    Checks whether a user has revisions when writing the recipe given by recipe_num

    Args:
        user_index (int): user index in the dataset
        recipe_num (int): recipe number (either 0, 1 or 2)
        function (function): function to compute the number of revision steps for this recipe

    Returns:
        bool: whether user has revisions for this recipe
    """
    try:
        sessions = function(user_index)
        return len(sessions[recipe_num]) > 1
    except: 
        return False    


def compute_user_range(user_index, num_users, recipe_insertions_deletions, indices_of_first_attempts_per_user):
    """ 
    Computes the total range of indices over which a user wrote in the dataset
    For example, if user 0 wrote in the dataset from index 0 to index 3, then this returns the tuples of insertions and deletions
    for each index in [0, 1, 2, 3] so it will be a list of 4 tuples

    Args:
        user_index (int): user in the dataframe

    Returns:
        list(tuple): list of tuples of insertions and deletions for each index in the range
    """
    user_range = None
    if user_index == num_users - 1:
        user_range = recipe_insertions_deletions[indices_of_first_attempts_per_user[user_index]: ]
    else:
        user_range = recipe_insertions_deletions[indices_of_first_attempts_per_user[user_index]: indices_of_first_attempts_per_user[user_index+1]]
    return user_range

def time_difference(time1, time2):
    """
    returns time difference between time2 and time1

    Args:
        time1 (string): initial time
        time2 (string): final time

    Returns:
        float: time difference in seconds
    """
    time1, time2 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S.%f"), datetime.strptime(time2, "%Y-%m-%d %H:%M:%S.%f")
    return (time2 - time1).total_seconds()

    
def time_difference_from_timestamps(time1, time2):
    """
    computes time difference between two timestamps

    Args:
        time1 (int): first timestamp
        time2 (int): second timestamp

    Returns:
        float: time difference in seconds
    """
    return (datetime.fromtimestamp(time2) - datetime.fromtimestamp(time1)).total_seconds()

def compute_text(metric, data):
    """
    Computes text to display in the dashboard

    Args:
        metric (string): what is evaluated
        data (pd.DataFrame): data to extract information from
    """
    def compute_diff_percentage(list):
        return round((list[-1] - list[0]) / list[0] * 100, 2)

    text = """Percentage change in {metric}
    group 1: {group1}%
    group 2: {group2}%
    """.format(metric=metric, 
    group1=compute_diff_percentage(data.loc['group 1']),
    group2=compute_diff_percentage(data.loc['group 2'])
    )
    return text

def flatten(list):
    """
    flattens list of lists

    Args:
        list (list): list to flatten

    Returns:
        list: flattened list
    """
    return [item for sublist in list for item in sublist]

##############
def summarize(text):
    """
    returns a summary of 'text'

    Args:
        text (str): text to summarize

    Returns:
        str: summary of text
    """
    stopwords = nltk.corpus.stopwords.words('english')
    word_frequencies = {}
    try:
        sentence_list = nltk.sent_tokenize(text)
    except: 
        print()
    for word in nltk.word_tokenize(text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    maximum_frequncy = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(5, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary


###########################
def separate_sessions():
    """
    Separates writing sessions by identifying all indices in which new recipes are written
    by calculating the cosine distance between the current recipe and the previous recipe and 
    if the distance is greater than a threshold, then it is a new recipe

    Returns:
        list: indices of new recipes
    """
    model = api.load("glove-wiki-gigaword-50")
    def preprocess(s):
        res = ""
        for i, char in enumerate(list(s)):
            if char not in noisy_punct:
                res += char    
        res = [i.lower() for i in res.split()]
        res = list(filter(lambda _ : _ not in noisy_punct, res))
        return res

    def get_vector(s):
        """
        Get the vector representation of a sentence from the model

        Args:
            s (str): text

        """
        arr = []
        for i in preprocess(s):
            key = None
            try: 
                key = model[i]
                arr.append(key)
            except:
                continue

        arr = np.array(arr)
        return np.sum(arr, axis=0)

    recipes = df['recipe'].values

    def compute_recipe_indices(start_index, acc):
        """
        Computes the list of indices where each recipe in the dataset begins
        Basically, user 0 writes 3 recipes:
        starts writing at t = 0, revises once at t = 1, a second time at t = 2 and 
        starts a new recipe at t = 3, then this function will return [0, 3] 

        Args:
            start_index (int): index to compare with the other recipes
            acc (list(int)): list to return

        Returns:
            list(int) : list of indices of beginning of each recipe
        """
        if start_index >= len(recipes) - 1:
            return acc
        vec = get_vector(recipes[start_index])
        for i in range(start_index, len(recipes)):
            dist = 1 - spatial.distance.cosine(vec, get_vector(recipes[i]))
            if dist < .995:
                acc.append(i)
                return compute_recipe_indices(i, acc)

    recipes_indices = compute_recipe_indices(0, [0])

    # Out of 450 samples, we only have  31 misclassified samples that are misclassified as new recipes so the algorithm is pretty effective
    to_remove = [13, 116, 134, 156, 168, 188, 249, 255, 256, 403, 88, 90, 128, 209, 376, 379, 381, 390, 391, 393, 394,395,  444]
    add = [121, 204, 254, 336, 97, 360, 362, 392]
    for i in to_remove:
        recipes_indices.remove(i)

    for i in add:
        recipes_indices.append(i) 

    recipes_indices = sorted(recipes_indices)

    rec = [df['recipe'][i] for i in recipes_indices]
    users = [df['user_id'][i] for i in recipes_indices]
    dframe = pd.DataFrame([recipes_indices, rec, users]).transpose()
    dframe.columns =['recipe index in data', 'recipe', 'user id']
    return dframe

map_ = separate_sessions().groupby('user id')["recipe index in data"].apply(list)
