# This script analyzes the tags

# check out lit on mining SNS for identity dev & suicidal predictions
# excluding no plot fics


# This analysis includes non-English fics since tags are English anyways.

# # raw = raw[raw.language == 'English'].drop(['language'], axis=1)
# print('Removing non-English fics... %d rows left; ' %len(raw))


#%%
import json
import pandas as pd
from pprint import pprint
from collections import Counter
from empath import Empath
import seaborn as sns
sns.set(style="darkgrid")
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np
import scipy.stats as stats

#%%
fin_root = 'sampledata/'
# storiesfile = 'ao3_harrypotter_text/stories.csv'
storiesfile = 'ao3_starwars_text/stories.csv'
# storiesfile = 'ao3_allmarvel_text/stories.csv'
# storiesfile = 'ao3_haikyuu_text/stories.csv'
# storiesfile = 'ao3_supernatural_text/stories.csv'
# storiesfile = 'ao3_dcu_text/stories.csv'
# storiesfile = 'ao3_sherlock_text/stories.csv'
path_to_stories = fin_root + storiesfile
sensitive_tags = {'rape': 'rape',
'noncon': ['noncon', 'non-con'],
'rape_noncon': ['rape','noncon', 'non-con'], 
'abuse': ['abusive', 'abuse'],
'suicidal': ['suicidal', 'suicide']}


### Import Stories ### 

def str_to_list(s):
    return s[2:-2].split('''", "''')

def import_stories(path_to_stories, withprint = False):
    """
    import stories.csv into a df
    with orphan_account and archivist fics removed
    """
    raw = pd.read_csv(path_to_stories, parse_dates= ['published','status date'])

    df = raw[~raw['author_key'].str.contains('archivist', na=False)]
    df = df[df.author_key != 'orphan_account']
    df['additional tags'] = df['additional tags'].str.lower()

    if withprint:
        print('Imported %d rows;'  %len(raw))
        print('Removing orphan_account and archivist accounts... %d rows left; ' %len(df))
        print('Columns: ', list(df.columns))
    return df

def add_warning_tags(df, sensitive_tags = sensitive_tags):
    """
    param: df (output of import_stories, in which df['additional tags'] are strings in lowercase)
    sensitive_tags (dictionary)
    prints occurance of each tag 
    returns: new df with tags in additional bool columns
    """
    total_cnt = len(df)

    for label, tags in sensitive_tags.items():
        # tag occurance as a new column (boolean)
        if type(tags) is list:
            df['tagged_%s'%label] = df['additional tags'].str.contains('|'.join(tags))
        else:
            df['tagged_%s'%label] = df['additional tags'].str.contains(tags)

        # count tag occurance
        t_cnt = df['tagged_%s'%label].sum() 
        print('%d tagged as %s, %s' % (t_cnt, label, "{:.3%}".format(t_cnt/total_cnt)))

    new_col_list = ['tagged_'+ k for k in sensitive_tags.keys()] # new column names
    df['tagged_sensitive_all'] = df[new_col_list].any(axis='columns')
    return df

def get_most_common_ships(col, topn = 5):
    """
    find the most common n relationships in the df['relationship'] column
    output: pd.Series
    """
    col = col.apply(str_to_list)
    all_ships = [item for sublist in col for item in sublist]
    result = pd.Series(list(filter(None, all_ships))).value_counts().index.tolist()[:topn]
    return result

def dayofyear_to_season(dayofyear):
    spring = range(80, 172)
    summer = range(172, 264)
    fall = range(264, 355)
    if dayofyear in spring:
        season = 'spring'
    elif dayofyear in summer:
        season = 'summer'
    elif dayofyear in fall:
        season = 'fall'
    else:
        season = 'winter'
    return season

def plot_time_tag(tag, df = df, showplot = False):

    if showplot:
        sns.distplot(df[df[tag] == True]['published_dayofyear'] , color='red', label= tag)
        sns.distplot(df[df[tag] == False]['published_dayofyear'] , color= 'skyblue', label="Others")
        plt.xlim(0,max(df['published_dayofyear']))
        plt.legend()
        plt.show()

    corr1 = stats.pearsonr(df['published_dayofyear'], df[tag])
    print('dayofY >>> corr', "{:.5f}".format(corr1[0]), 'pval ', "{:.5f}".format(corr1[1]))
    corr2 = stats.pearsonr([_date.month for _date in df['published']], df[tag])
    print('month >>> corr', "{:.5f}".format(corr2[0]), 'pval ', "{:.5f}".format(corr2[1]))

def cramers_v(x, y):
    """ calculate Cramers V statistic for categorial-categorial association.
        uses correction from Bergsma and Wicher,
        Journal of the Korean Statistical Society 42 (2013): 323-328
        source: https://towardsdatascience.com/the-search-for-categorical-correlation-a1cf7f1888c9
    """
    confusion_matrix = pd.crosstab(x,y)
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2/n
    r,k = confusion_matrix.shape
    phi2corr = max(0, phi2-((k-1)*(r-1))/(n-1))
    rcorr = r-((r-1)**2)/(n-1)
    kcorr = k-((k-1)**2)/(n-1)
    result = np.sqrt(phi2corr/min((kcorr-1),(rcorr-1)))
    print('>>> cramers_v ', "{:.5}".format(result))
    return result

#%%
df = import_stories(path_to_stories, withprint = False)
df['published_dayofyear'] = df['published'].apply(lambda _date: _date.timetuple().tm_yday)
df['published_season'] = df['published_dayofyear'].apply(dayofyear_to_season)
unique_fics = df['fic_id'].nunique()

print('Importing %s...' % storiesfile)
print('Imported %d unique fics' % unique_fics)

#%%
df = add_warning_tags(df)
topShips = get_most_common_ships(df['relationship'])
# print('Most common ships:', topShips)

rank = 1
for ship in topShips:
    print('\n===', ship, '===')
    df['ship%d'%rank] = df['relationship'].str.contains(ship)

    for label in sensitive_tags.keys():
        sub = df[df['ship%d'%rank] == True]
        print('\n',label.upper())
        plot_time_tag('tagged_%s'%label, sub, showplot = True)
        cramers_v(sub['published_season'], sub['tagged_%s'%label])
    rank += 1
    
#%%

#%%
# for col in ['fandom', 'category', 'rating', 'relationship', 'character', 'additional tags']:
#     df[col] = df[col].apply(str_to_list)

#%%
### Tag Cooccurance ### 

# if __name__== "__main__":

    # parameters
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-story', '--storiesfile', required = True, dest = 'storiesfile', type = str, help = "Path to stories.csv file (<fandom folder>/<filename>)")
    # parser.add_argument('-test', '--localtestorserverrun', required = False, default = False, dest = 'test', type=bool, help="Local test (true) or server run (false)" )
    # args = parser.parse_args()

    # if args.test == True:
    #     fin_root = 'sampledata/'
    #     fout_root = 'sampleoutput/'
    # else:
    #     fin_root = '/usr2/scratch/fanfic/'
    #     fout_root = '/usr0/home/qyang1/fanfic_authors/'

    # path_to_stories = fin_root + args.storiesfile
    # authorlist_fout = fout_root + args.storiesfile[:-4] + "authorlist.pkl"
    # author_fout = fout_root + args.storiesfile[:-4] + '_authors.csv'
    # pseudo_fout = fout_root + args.storiesfile[:-4] + '_pseudos.csv'
