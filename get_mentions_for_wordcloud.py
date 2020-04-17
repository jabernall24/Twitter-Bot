#!/usr/bin/env python

import random
import json
import os
import re
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from twython import Twython
from Twitter import Twitter

COMMAND = '@jabernall24 wordcloud lm'
IMG_PATH = '/tmp/image.png'

def generate_word_cloud(words, img_path=IMG_PATH):
    """
    Given an array of tweets, generates a word cloud and saves it locally

    @param words
        - String of words seperated by a space to generate the word cloud with
    @param img_path
        - Path to the image to tweet out
    """

    wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = STOPWORDS, 
                min_font_size = 10).generate(words)

    plt.figure(figsize = (6, 6), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0)
    plt.savefig(img_path)


def handle_plot(tweet):
    """
    Gets name of user who tweeted the COMMAND
        - Generates word cloud
        - Sends out tweet
    
    @param tweet
        - The tweet object that tweeted the COMMAND
    """
    twitter = Twitter(tweet['user']['screen_name'])
    tweets = twitter.get_last_month_tweets_for_user()
    
    # Make sure the user tweeted the previous month
    if len(tweets) == 0: return
    
    words = twitter.get_words(tweets)
    generate_word_cloud(words)
    
    user = tweets[0]['user']
    month = tweets[0]['created_at'].strftime('%B')
    
    tweet_text = f"""
@{user} here are the most common words you tweeted for the month of {month}.
#visualization #wordcloud #automation #AWS #Lambda #{month}
    """
    twitter.send_tweet(tweet_text, IMG_PATH)
    
    os.remove(IMG_PATH)

def get_my_mentions():
    """
    Gets my timeline for the last minute and checks for tweets that match the COMMAND
    """
    twitter = Twitter('jabernall24')
    tweets = twitter.get_timeline()
    
    one_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
    
    tweets = list(filter(lambda x: parse(x['created_at']) > one_minutes_ago, tweets))

    for tweet in tweets:
        if tweet['full_text'].lower() == COMMAND:
            handle_plot(tweet)


def lambda_handler(event, context):
    get_my_mentions()