#!/usr/bin/env python3
# GENERAL IMPORTS
import sys
import os
import pandas as pd
import re
from string import punctuation

# TRANSLATION AND PREPROCESSING IMPORTS
from argostranslate import package, translate
package.install_from_path('./ru_en.argosmodel')
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words('english') + ['rt', 'via'])
from nltk.stem import PorterStemmer
PS_STEM = PorterStemmer()

import logging
# logging.basicConfig(filename='./output.log', encoding='utf-8', level=logging.INFO)

# CREATE LANGUAGE TRANSLATION MODEL
INSTALLED_LANGS = translate.load_installed_languages()
RU_TRANS = INSTALLED_LANGS[1].get_translation(INSTALLED_LANGS[0])

# FILE PATHS
data_path = './data/' 
user_data_path = './user_data/'

# DEFINE SOURCE TYPES
STANDARD_SRC = ['Instagram',
 'Twitter for Android Tablets',
 'Twitter Ads Composer',
 'Twitter for Android',
 'Twitter for iPad',
 'vk.com pages',
 'LiveJournal.com',
 'Vine for Android',
 'Tumblr',
 'Twitter for Windows Phone',
 'Twitter for Samsung Tablets',
 'LinkedIn',
 'Twitter for Mac',
 'Twitter for iPhone',
 'Twitter Ads',
 'Curious Cat',
 'vk.com',
 'Google',
 'Pinterest',
 'Viber',
 'Twitter Web Client',
 'Twitter for Windows',
 'SoundCloud',
 'iOS',
 'Twitter for BlackBerry®',
 'web',
 'Twitter for BlackBerry',
 'Medium',
 'Ask.fm',
 'WordPress.com',
 'Mobile Web',
 'Periscope',
 'Mobile Web (M2)',
 'Spring.me',
 'Quora',
 'Twitter Lite',
 'Twitter for Google TV',
 'Twitter for Websites',
 'Twitter for Nokia S40',
 'Facebook',
 'Twitter Web App',
 'Samsung Mobile']

AUTOMATED_SRC = ['twittbot.net',
 'UberSocial for Android',
 'Tuitwit',
 'Twibble.io',
 'TweetAdder v4',
 'Gravity!',
 'Crowdfire Inc.',
 'UberSocial for BlackBerry',
 'Shareaholic.com',
 'Hootsuite Inc.',
 'Seesmic',
 'Foursquare',
 'Unfollowspy',
 'Tweepsmap',
 'SocialOomph',
 'TweetDeck',
 'Commun.it',
 'SocialReport.com',
 'Buffer',
 'SMMplanner',
 'RoundTeam',
 'YoruFukurou',
 'TweetCaster',
 'Twitter Media Studio',
 'Zapier.com',
 'Amplifr',
 'yoono',
 'ubertwitter',
 'Twееtbot for Mac',
 'fllwrs',
 'twiends.com',
 'Tweetbot for iOS',
 'Nubrec.com',
 'Tweetbot for iOS11',
 'GharedlyCom',
 'Twittimer',
 'Janetter for Android',
 'Gremlin Social',
 'FaWave',
 'Tweetbot for iΟS',
 'Cubi.so',
 'GroupTweet',
 'RSS2Twitter',
 'Tus mejores followers',
 'Botize',
 'IFTTT',
 'Symphony Tools',
 'TweetCaster for Android',
 'WhoUnfollowedMe Org',
 'Hootsuite',
 'Link account with KUKU.io',
 'TwitPal',
 'Tuit Útil',
 'SlackSocial',
 'HootBar',
 'Linkis: turn sharing into growth',
 'GharredNet',
 'NovaPress Publisher',
 'twitterfeed',
 'Tweetbot for Mac',
 'Panoramic moTweets',
 'Gharedly 2.3',
 'MetroTwit',
 'Microsoft Power Platform',
 'Echofon',
 'The Tweeted Times',
 'TweetList Pro',
 'Seesmic Web',
 'dlvr.it',
 'TweetCaster for iOS',
 'Microsoft PowerApps and Flow',
 'unfalert.com']

# FUNCTION: cleans text (still needs to remove user mentions, translate and lemmatize)
def clean_text(row):
    if int(row.name)%100 == 0:
        logging.info('--> finished processing {} lines'.format(row.name))
    text = row['tweet_text']
    txt = text.lower() # to lowercase
    txt = ' '.join(txt.split()) # remove extra whitespace
    txt = re.sub(r"https?://\S+", "", txt) # remove URL
    txt = re.sub(r"@[^\s]+", "", txt) # remove user mentions
    txt = re.sub(r"\#[^\s]+", "", txt) # remove hashtags

    # translate to english
    if row['tweet_language'] == 'ru':
        txt = RU_TRANS.translate(txt).lower()

    
    txt = re.sub(r"(?:(?!\u0301)[\W\d_])+", " ", txt) # remove punctuation
    txt = re.sub(r"\b[0-9]+\b\s*", "", txt) # remove numbers
    txt = " ".join([t for t in txt.split() if len(t) > 1 and t not in STOP_WORDS]) # remove length==1 words and possible stop words

    txt = " ".join([PS_STEM.stem(w) for w in txt.split() if w not in STOP_WORDS]) # lemmatize and remove final stop words

    return txt

# FUNCTION: determines if a tweet interacts with someone inside or outside of the network
def check_in_out(row, in_users):
    user = None
    if not pd.isnull(row['in_reply_to_userid']):
        user = str(row['in_reply_to_userid'])
    elif not pd.isnull(row['user_mentions']) and row['user_mentions'] != '[]':
        mentions = row['user_mentions'].split(',')
        mentions[0] = mentions[0][1:]
        mentions[-1] = mentions[-1][:-1]
        mentions = [x.strip() for x in mentions]
        user = mentions[0]
    else:
        pass
    
    if user is None:
        return 'None'
    else:
        if user in in_users:
            return 'Within'
        else:
            return 'Outside'

# FUNCTION: encodes activity as automated, standard, or other
def source_encode(cell):
    return 'standard' if cell in STANDARD_SRC else 'automated' if cell in AUTOMATED_SRC else 'other'

# MAIN
if __name__ == '__main__':
    # process parameters
    camp_name = str(sys.argv[1])

    # MAIN LOOP: builds dataframe
    df_list = []
    for file in os.listdir(data_path + camp_name):
        logging.info('Processing file: {}'.format(file))

        # read in users to decide if interaction faces in or out
        users = set([str(x) for x in pd.read_csv(user_data_path + camp_name + '.csv')['userid']])

        # error handling for malformed lines
        if camp_name == 'russia_oct2018' and file == 'ira_tweets_csv_hashed.csv':
            skip_this = [1826345]
        else:
            skip_this = []

        # read in csv
        df = pd.read_csv(data_path + camp_name + '/' + file, skiprows=skip_this)
        logging.info('original length: {}'.format(len(df)))

        # only keep russian and english
        df = df[df['tweet_language'].isin(['en', 'ru'])]
        logging.info('language filtered: {}'.format(len(df)))

        # only keep rows that interact inside or outside of campaign
        df['interaction_type'] = df.apply(lambda x: check_in_out(x, users), axis=1)
        df = df[df['interaction_type'] != 'None']
        logging.info('ENG: {}, RUS: {}'.format(len(df[df['tweet_language']=='en']), len(df[df['tweet_language']=='ru'])))
        
        # sample down to 1/3rd of original data size
        df = df.groupby('tweet_language').apply(lambda x: x.sample(frac=0.1667)).reset_index(drop=True)
        logging.info('ENG: {}, RUS: {}'.format(len(df[df['tweet_language']=='en']), len(df[df['tweet_language']=='ru'])))

        # # translate and clean text
        df['cleaned_text'] = df.apply(clean_text, axis=1)
        df['source_type'] = df['tweet_client_name'].apply(source_encode)
        df_list.append(df)

    # combine all dataframes into one
    final_df = pd.concat(df_list)
    # SAVE TO CSV
    final_df.to_csv('./' + camp_name + '.csv', encoding='utf-8', index=False)
    logging.info('Campaign CSV completed')