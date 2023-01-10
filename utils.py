from datetime import datetime

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