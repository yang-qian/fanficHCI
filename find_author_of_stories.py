yield
# coding: utf-8

#### ====== Get authors of stories.csv ====== #### 
# :param: <path to stories.csv> (str)
# :output: files <authors.csv> and <pseudos.csv>
# 
# Notes
# * Add 5 second delays before requesting from AO3's server are in compliance with the AO3 terms of service.
# * Cannot scrape restricted fics, which require login. Can use https://pypi.org/project/ao3/ to log in but cannot use it to scrape restricted fics.
# * Some accounts no longer exist. i.e. ``ButterflyPup``.
# * Skip
#     * `orphan_account`, which is a default pseud of the Orphan Account for works that are no longer associated with their creator's account;
#     * `*_archivist`, e.g., `HPFandom_archivist`, `TheHexFiles_archivist`.

# In[1]:

blacklisted_accounts = ['orphan_account']
# 'orphan_account' is a default pseud of the Orphan Account for works that are no longer associated with their creator's account.
# other accounts: 'HPFandom_archivist', 'TheHexFiles_archivist'
sns_kw = ['tumblr', 'ffnet', 'fanfiction.net', 'twitter','facebook', 'youtube', 'instagram']

# In[1]:

import pandas as pd
import json
get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import pprint
from datetime import datetime
import numpy as np
import requests
from bs4 import BeautifulSoup
import argparse
import time
import os
import csv
import sys
from unidecode import unidecode
from itertools import groupby
from operator import itemgetter

# In[2]:

# path_to_stories = sys.argv[-1] 
path_to_stories = 'sampledata/ao3_harrypotter_text_stories.csv'
author_fout = 'sampleoutput/sampleoutput_authors.csv'
pseudo_fout = 'sampleoutput/sampleoutput_pseudos.csv'

authorschema = ('author_key',
                'pseudos',
                'bday',
                'author_fic_ids',
                'joined_on',
                'live_in',
                'author_work_count',
                'author_bookmark_count',
                'bio',
                'linked_social_media')

pseudoschema = ('author_key',
                'pseudo',
                'pd_work_count',
                'pd_bookmark_count',
                'pd_fic_ids')

# In[3]:

def get_authors_from_storiescsv(path_to_stories):
    '''
    param: path to stories.csv
    return: df, columns are fic_id (lists) and author_key(str)
    '''
    df = pd.read_csv(path_to_stories,usecols = ['fic_id','author_key'])
    return df.groupby('author_key')['fic_id'].apply(list) # Series

#%%
def find_author_of_ficid(fic_id):
    '''
    para: fic_id(str)
    output: author_key (str), pseud (str)
    '''
    
    r1 = requests.get("https://archiveofourown.org/works/" + fic_id,
                        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'})
    soup1 = BeautifulSoup(r1.content, "html.parser")
    try:
        url_splits = soup1.find("a", rel="author")['href'].split('/')
        author_key = url_splits[2]
        pseud = url_splits[-1]
        return author_key, pseud
    except:
        print('Cannot find author for', fic_id)
        return None,None

#%%
def find_sns_from_bio(bio, sns_kw):
    '''
    bio (str), sns_kw (list)
    '''
    incl = []
    for sns in sns_kw:
        if sns in bio.lower():
            incl.append(sns)
    return incl

# In[16]:

def find_bookmark_work_counts(soup, url):
    # :outputs: the # of fics this author/pseudo has bookmarked
    try:
        bookmark_cnt = soup.find("a", attrs = {'href': lambda x: x and x.lower() == url.lower() + "/bookmarks"}).text 
        bookmark_cnt = bookmark_cnt[11:-1]
    except:
        print('Error finding bookmarks of', url + "/bookmarks")
    
    # get the # of fics this author/pseduo has created (incl. WIP)
    try:
        work_cnt = soup.find("a", attrs = {'href': lambda x: x and x.lower() == url.lower() + "/works"}).text # i.e. "Works (1)"
        work_cnt = work_cnt[7:-1]
    except:
        print('Error finding bookmarks of' + url + "/works")
    
    return bookmark_cnt, work_cnt

# In[14]:
def profile_an_author(author_key,fic_author_lookup,
                     authorschema = authorschema,
                     pseudoschema = pseudoschema,
                     sns_kw = sns_kw):
    '''
    param: author_key (str)
           fic_author_lookup (Series of author_key and list of fic_ids tied to the author)
    return: df of the author, linked_social_media left as None
    each row is an author identity (author_key and psudo pair)
    '''
    
    author = pd.DataFrame(columns= authorschema)
    pseudodf = pd.DataFrame(columns= pseudoschema)
    
    # ==== profile the author ==== #
    # get start_date, location
    r1 = requests.get("https://archiveofourown.org/users/" + author_key + "/profile",
                      headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'})
    soup1 = BeautifulSoup(r1.content, "html.parser")
    
    try:
        # if the author_key exists
        umeta = [dd.text for dd in soup1.find("dl", class_="meta").findAll("dd")]
        # print('Found author %s.'%author_key)
    except:
        print ('Cannot find author %s.'%author_key)
        return None, None
    
    start_date = umeta[1]
    try:
        location = umeta[2]
    except:
        location = ""
        
    # get all pseudos of the author_key
    pseudos = [i['href'].split('/')[-1] for i in soup1.find("dd", class_ = "pseuds").findAll("a")]
    
    # find the author's bio, if any
    biosoup = soup1.find("div", class_="bio module")
    if biosoup is not None:
        try:
            bio = biosoup.find("blockquote", class_ = "userstuff").text
            mentioned_sns = find_sns_from_bio(bio, sns_kw)
        except Exception as e:
            print(author_key, e)
            bio = "<!ERROR!>"
            mentioned_sns = None
    else:
        bio = None
        mentioned_sns = None
        
    # find the author's bday, if listed
    try:
        bday = soup1.find("dd", class_="birthday").text
    except:
        bday = ""
    
    author_bookmark_cnt, author_work_cnt = find_bookmark_work_counts(soup1, "/users/" + author_key)
    author_fic_ids = fic_author_lookup[author_key]
    author = author.append({'author_key': author_key,
                            'bday': bday,
                            'pseudos': pseudos,
                            'joined_on': start_date,
                            'live_in': location,
                            'author_work_count': author_work_cnt,
                            'author_bookmark_count': author_bookmark_cnt,
                            'author_fic_ids': author_fic_ids, # fill in when scaping fic_ids associated with pseudo
                            'bio': bio,
                            'linked_social_media': mentioned_sns},
                             ignore_index = True)
    author.set_index('author_key')

    # ==== generate fic_pseudo_lookup ==== #
    fic_pseudo_lookup = {}
    for author_fic in author_fic_ids:
        this_pseudo = find_author_of_ficid(str(author_fic))[1]
        if this_pseudo in fic_pseudo_lookup:
            fic_pseudo_lookup[this_pseudo].append(author_fic)
        else:
            fic_pseudo_lookup[this_pseudo] = [author_fic]
    
    # print('fic_pseudo_lookup::',fic_pseudo_lookup)
    
    # ==== profile the pseudos ==== #
    for pseudo in pseudos:
        print('pseudo --- ', pseudo)
        
        # characterize the actives of the pseudo (# of bookmarks, works)
        r2 = requests.get("https://archiveofourown.org/users/" + author_key + "/pseuds/" + pseudo,
                      headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'})
        soup2 = BeautifulSoup(r2.content, "html.parser")
        
        pd_bookmark_cnt, pd_work_cnt = find_bookmark_work_counts(soup2, "/users/" + author_key + "/pseuds/" + pseudo)

        pseudodf = pseudodf.append({'author_key': author_key,
                                    'pseudo': pseudo,
                                    'pd_work_count': pd_work_cnt,
                                    'pd_bookmark_count': pd_bookmark_cnt,
                                    'pd_fic_ids': fic_pseudo_lookup[pseudo]},
                                     ignore_index = True)

    # TO-DO
    # for all fics of this author in the stories.csv
    # find the ones tied to this pseudo
    # for fici in author_fic_ids:
    #     pseudo = find_author_of_ficid(fici)[1]
    # pseudoddf.set_index('pseudo')

    return author, pseudodf

# In[15]:

# Test cases:
# - allmylovesatonce 39 works
# - alexdesro08 2 pseudos, no works finished
# - liketolaugh 103 works (Interview study participant)

# profile_an_author('allmylovesatonce')
# profile_an_author('liketolaugh')
# profile_an_author('alexdesro08')
# profile_an_author('Tara')[1]
# profile_an_author('Falmarien')

# In[19]:
def get_authors_from_stories(path_to_stories,author_fout = author_fout, pseudo_fout = pseudo_fout):

    fic_author_lookup = get_authors_from_storiescsv(path_to_stories) # Series
    # print(fic_author_lookup.index, fic_author_lookup.values)
    author_key_list = list(fic_author_lookup.index)

    authors = pd.DataFrame(columns= authorschema)
    pseudos = pd.DataFrame(columns= pseudoschema)

    cnt = 0

    for author_key in author_key_list:
        if cnt >= 5:
            break

        if author_key in blacklisted_accounts:
            # skip ``orphan_account`` and other blacklisted accounts
            pass
        else:
            author, pseudo = profile_an_author(author_key,fic_author_lookup)
            authors = authors.append(author)
            pseudos = pseudos.append(pseudo)
            cnt += 1

    authors.to_csv(author_fout, mode='w+', index=False)
    pseudos.to_csv(pseudo_fout, mode='w+', index=False)

get_authors_from_stories(path_to_stories)


