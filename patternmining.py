""" 

A word about ```PrefixSpan```

Parameters: 
* Minimum Support (minSupport) : support is calculated as the % of sequences containing the subsequence
* Maximum Subsequence Length (maxPatternLength) : speaks for itself

If  minSupport is little and maxPatternLength is large, the running time of PrefixSpan gets exceedingly long. 
The contrary gives reasonable running time but some subsequences can be left undiscovered.

"""
import pandas as pd
from pyspark.ml.fpm import PrefixSpan
from pyspark.shell import sc
from pyspark.sql.functions import desc
from pyspark.sql.types import Row
import matplotlib.pyplot as plt
from utils import *

NUM_PATTERNS_TO_PLOT = 25
MIN_SUPPORT = .3
MAX_PATTERN_LENGTH = 10

ins_del_dict = {'insert': 0, 'delete': 1}
recipe_sequences = []
for user in sorted(sorted_users):
    indices_where_written = df[df['user_id'] == user].index
    for index in indices_where_written:
        ks_set = all_keystrokes[index]
        recipe_sequence = []
        for entry in ks_set:
            word = entry['word']
            if word not in KEYWORDS:
                #+1 to account for the space
                recipe_sequence.append(ins_del_dict['insert'])
            elif word == 'Backspace' or word == 'Delete':
                recipe_sequence.append(ins_del_dict['delete'])
        recipe_sequences.append(recipe_sequence)                               


def apply_prefixSpan(data, minSupport=0.2, maxPatternLength=8, kind='barh', title=""):
    """
    input an array of indices on which you want to apply prefix span. So for example, we want to apply it to the first 
    thing users write so we input the indices of the first text they write in ...
    indices = list[int] -> the indices of the data we want to look at
    data = list[list[obj]] -> list of sentences ie list of lists of words
    """
    range_ = range(len(data))
    #map to rows so that
    for i in range_:
        data[i] = Row(sequence=[data[i]])

    l = [data[i] for i in range_]
    DF = sc.parallelize(l).toDF()
    prefixSpan = PrefixSpan(minSupport=minSupport, maxPatternLength=maxPatternLength, maxLocalProjDBSize=32000000)
    # Find frequent sequential patterns.
    find_pat = prefixSpan.findFrequentSequentialPatterns(DF).sort(desc('freq')).collect()
    df2 = pd.DataFrame(list(map(lambda _: _.asDict(), find_pat[:NUM_PATTERNS_TO_PLOT])))
    df2.plot(kind=kind,x='sequence', y='freq', figsize=(6, 9), title=title)
    return find_pat

def compute_prefix_span_on_revision_step(n, minSupport=.3, maxPatternLength=10):
    """
    Args:
        n (int): the revision step - usually between 0 and 3
        minSupport (float):  Defaults to 0.3.
        maxPatternLength (int):  Defaults to 10.
    """
    #We must select only users that have n revisions - not everyone has 10 revision for example.
    users_with_n_revisions =  \
        [indices_of_first_attempts_per_user[i]+n if indices_of_first_attempts_per_user[i+1] - indices_of_first_attempts_per_user[i] >= n else -1 for i in range(len(indices_of_first_attempts_per_user)-1)]
    nth_revision = []
    for index in users_with_n_revisions:
        if index != -1:
            users_nth_sequence = recipe_sequences[index]
            nth_revision.append(users_nth_sequence)
    return apply_prefixSpan(nth_revision, minSupport=minSupport, maxPatternLength=maxPatternLength, title="Prefix Span applied on users at revision step " + str(n))

sequences = compute_prefix_span_on_revision_step(1, minSupport=MIN_SUPPORT, maxPatternLength=MAX_PATTERN_LENGTH)
plt.show()