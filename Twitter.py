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
import boto3

class Twitter:
    def __init__(self, handle):
        super().__init__()
        self.handle = handle

        # Create the Twython Twitter client using the credentials stored in SSM
        self.twitter = Twython(
            self.get_secret("CONSUMER_KEY"),
            self.get_secret("CONSUMER_SECRET"),
            self.get_secret("ACCESS_TOKEN_KEY"),
            self.get_secret("ACCESS_TOKEN_SECRET")
        )
    
    def get_secret(self, parameter_name):
        """
        Get a parameter from SSM Parameter store and decrypt it

        @param parameter_name
            - The name of the parameter in the AWS System Manager Parameter Store
        """
        ssm = boto3.client('ssm')
        parameter = ssm.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )['Parameter']['Value']
        return parameter

    def send_tweet(self, tweet_text, img_path=None):
        """
        Sends a tweet to Twitter

        @param tweet_text
            - The text being tweeted
        @param img_path
            - The path of the image to attach to the tweet if None doesn't attach anything
        """
        if img_path is None:
            self.twitter.update_status(status=tweet_text)
            return
        image = open(img_path, 'rb')
        response = self.twitter.upload_media(media=image)
        self.twitter.update_status(status=tweet_text, media_ids=[response['media_id']])

    def get_last_month_tweets_for_user(self, screen_name=None):
        """
        Gets the last months tweets for the screen_name provided

        @param screen_name
            - The person we are getting the tweets from twitter handle
        """
        if screen_name is None:
            screen_name = self.handle
        long_tweets = self.get_last_month_timeline(screen_name)
        tweets = self.shorten_tweet_object_and_filter_users(screen_name, long_tweets)
        return tweets

    def get_last_month_timeline(self, screen_name):
        """
        Gets all the tweets from the previous month

        @param screen_name
            - The person we are getting the tweets from twitter handle
        """
        long_tweets = self.get_user_timeline(screen_name)

        last_month = self.get_last_month()
        last_tweet_date = parse(long_tweets[-1]['created_at'])

        while last_tweet_date > last_month:
            new_tweets = self.get_user_timeline(screen_name, long_tweets[-1])
            if len(new_tweets) == 0: 
                break

            long_tweets.extend(new_tweets)
            last_tweet_date = parse(long_tweets[-1]['created_at'])
        
        long_tweets = list(filter(lambda x: parse(x['created_at']).month == last_month.month, long_tweets))
        return long_tweets
    
    def get_last_month(self):
        """
        Gets the 1st of last month at hour, minute and second 0
        """
        today = datetime.now(timezone.utc)
        month = today.month
        year = today.year
        if month == 0:
            month = 12
            year = year - 1
            
        last_month = today.replace(day=1, month=month, year=year, hour=0, minute=0, second=0)
        return last_month
    
    def get_user_timeline(self, screen_name, last_tweet=None):
        """
        Gets the users last 200 tweets from the last tweet
        Gets the 200 most recent if last tweet is None

        @param screen_name
            - The person we are getting the tweets from twitter handle
        @param last_tweet
            - The last tweet retrieved used to get a fresh 200 tweets
        """
        return self.twitter.get_user_timeline(screen_name=screen_name, count=200, 
                exclude_replies=True, include_rts=False, tweet_mode='extended', 
                max_id=None if last_tweet is None else last_tweet['id'])


    def shorten_tweet_object_and_filter_users(self, screen_name, long_tweets):
        """
        Returns a short version of the long tweets of only the correct user

        @param screen_name
            - The person we are getting the tweets from twitter handle
        @param long_tweets
            - List of tweet objects
        """
        tweets = []
        for long_tweet in long_tweets:
            user = long_tweet['user']
            if user['screen_name'] != screen_name:
                break

            tweet = {
                'text': long_tweet['full_text'],
                'user': user['screen_name'],
                'created_at': parse(long_tweet['created_at'])
            }
            
            tweets.append(tweet)
        return tweets
    
    def clean_text(self, text):
        """
        Returns the text without urls, ., ',', \n

        @param text
            - The text to clean
        """
        clean_text = re.sub(r'http\S+', '', text)
        clean_text = clean_text.replace('.', ' ')
        clean_text = clean_text.replace(',', ' ')
        clean_text = clean_text.replace('\n', ' ')

        return clean_text

    def get_words(self, tweets):
        """
        Gets all the words in all the tweets

        @param tweets
            - A list of tweet objects
        """
        cleaned_text = list()
        for tweet in tweets:
            cleaned_text.extend(list(map(lambda x: x.lower(), self.clean_text(tweet['text']).split())))
        return ' '.join(cleaned_text)
    
    def get_timeline(self):
        """
        Gets my mentions
        """
        return self.twitter.get_mentions_timeline(count=100, tweet_mode='extended')
