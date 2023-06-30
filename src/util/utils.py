from datetime import datetime
import nltk.corpus 
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq
import pandas as pd
import gensim.downloader as api
from gensim.models import KeyedVectors
from scipy import spatial
import numpy as np
import pandas as pd
import ast
import numpy as np


class Utils:
    def __init__(self, path: str = 'data/keystrokes-recipes-groups4.csv', additional_data_path: str = 'data/groupmatching4.csv') -> None:
            
        print('Loading utils')
        self.df = pd.read_csv(path)
        self.indices_of_first_attempts_per_user = self.df.groupby('user_id').head(1).index
        self.noisy_punct = [',', '.', '-', ':', '(', ')']
        self.all_keystrokes = list(map(lambda _ : ast.literal_eval(_) , self.df['ks'].values))
        self.KEYWORDS = ['Alt', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'Backspace', 'CapsLock', 'Control', 'Delete', 'End', 'Enter', 'Home', 'Meta', 'PageUp', 'PageDown', 'PrintScreen','Shift', 'Tab']
        self.sorted_users = sorted(self.df['user_id'].unique())
        self.vectors = []
        if additional_data_path is not None:
            self.matching_data = pd.read_csv(additional_data_path)
            self.users_to_groups = dict(self.matching_data.filter(['user_id', 'group']).values)
            self.s = self.matching_data.sort_values(by=['group', 'user_id'], ascending=True)
        
        self.INDICES = []
        """
            Basically what we do here is simple. We have the data matching each user to which group they belong to.
            So what we do is we create an array INDICES. We create a dictionnary which maps each group to the users in it.
            Then iterate over the users of each group and find their index in the sorted users array. 

            so INDICES has 2 arrays, each containing the indices of the users in that group.
            
        """
        groups = {1: [], 2: [], 3: [], 4: [], 5: []}
        for i, dic in enumerate(self.s.values):
            groups[self.users_to_groups[dic[1]]].append(dic[1])
        self.INDICES = [[self.sorted_users.index(user) for user in groups[group]] for group in [1, 2,3,4,5]]

        print("Done loading")

    def get_last_index_where_written(self, user_index):
        """
        Returns the last index where a user has written in the dataset
        ie if user 0 wrote at indices [0,1,2,3,4,5] then this would return 6, in order to include index 5 
        when iterating over user entries

        Args:
            user_index (int): index of user in the dataset
        
        Returns:
            int: index of last index where user has written
        """
        return self.indices_of_first_attempts_per_user[user_index + 1] if  user_index != len(self.sorted_users) - 1 else len(self.df) - 1

    def has_revision(self, user_index, recipe_num, function):
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


    def compute_user_range(self, user_index, num_users, recipe_insertions_deletions):
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
            user_range = recipe_insertions_deletions[self.indices_of_first_attempts_per_user[user_index]: ]
        else:
            user_range = recipe_insertions_deletions[self.indices_of_first_attempts_per_user[user_index]: self.indices_of_first_attempts_per_user[user_index+1]]
        return user_range

    def time_difference(self, time1, time2):
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

        
    def time_difference_from_timestamps(self, time1, time2):
        """
        computes time difference between two timestamps

        Args:
            time1 (int): first timestamp
            time2 (int): second timestamp

        Returns:
            float: time difference in seconds
        """
        return (datetime.fromtimestamp(time2) - datetime.fromtimestamp(time1)).total_seconds()

    def compute_text(self, metric, data):
        """
        Computes text to display in the dashboard

        Args:
            metric (string): what is evaluated
            data (pd.DataFrame): data to extract information from
        """
        def compute_diff_percentage(list):
            return round((list[-1] - list[0]) / list[0] * 100, 2)

        text = """% change in {metric}
        \u2022 group 1: {group1}%
        \u2022 group 2: {group2}%
    """.format(metric=metric, 
    group1=compute_diff_percentage(data.loc['group 1']),
    group2=compute_diff_percentage(data.loc['group 2'])
    )
        return text

    def flatten(self, list):
        """
        flattens list of lists

        Args:
            list (list): list to flatten

        Returns:
            list: flattened list
        """
        return [item for sublist in list for item in sublist]

    def separate_sessions(self):
        """
        Separates writing sessions by identifying all indices in which new recipes are written
        by calculating the cosine distance between the current recipe and the previous recipe and 
        if the distance is greater than a threshold, then it is a new recipe

        Returns:
            list: indices of new recipes
        """
        print("loading GloVe model")
        try:
            model = KeyedVectors.load('data/glove.model.d2v')
        except:
            print("model not found, loading from api")
            model = api.load("glove-wiki-gigaword-50")
            model.save('data/glove.model.d2v')
        print("model loaded")
        def preprocess(s):
            res = ""
            for i, char in enumerate(list(s)):
                if char not in self.noisy_punct:
                    res += char    
            res = [i.lower() for i in res.split()]
            res = list(filter(lambda _ : _ not in self.noisy_punct, res))
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

            self.vectors= arr
            arr = np.array(arr)      
            return np.sum(arr, axis=0)

        recipes = self.df['recipe'].values

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
                if dist < .895:
                    acc.append(i)
                    return compute_recipe_indices(i, acc)

        recipes_indices = compute_recipe_indices(0, [0])

        # Out of 450 samples, we only have  31 misclassified samples that are misclassified as new recipes so the algorithm is pretty effective
        #to_remove = [13, 116, 134, 156, 168, 188, 249, 255, 256, 403, 88, 90, 128, 209, 376, 379, 381, 390, 391, 393, 394,395,  444]
        #add = [121, 204, 254, 336, 97, 360, 362, 392]
        #for i in to_remove:
        #    recipes_indices.remove(i)

        #for i in add:
        #    recipes_indices.append(i) 

        recipes_indices = sorted(recipes_indices)

        rec = [self.df['recipe'][i] for i in recipes_indices]
        users = [self.df['user_id'][i] for i in recipes_indices]
        dframe = pd.DataFrame([recipes_indices, rec, users]).transpose()
        dframe.columns =['recipe index in data', 'recipe', 'user id']
        return dframe

    
    def get_map_user_to_recipes(self):
        """
        Maps user id to the list of indices of recipes written by that user
        example: 
        User 0 writes from indices [1 -> 9]
        and writes recipe 1 at index 1, recipe 2 at index 5 and recipe 3 at index 7 for example
        then this function will return {0: [1, 5, 7]}

        Returns:
            dict: user id to list of recipe indices
        """
        return self.separate_sessions().groupby('user id')["recipe index in data"].apply(list)

    def get_vectors(self):
        return self.vectors