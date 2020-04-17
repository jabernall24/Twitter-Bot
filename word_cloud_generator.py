#!/usr/bin/env python

import os
from Twitter import Twitter
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import boto3

IMG_PATH = '/tmp/image.png'
TABLE_NAME=os.environ['TABLE_NAME']

def get_twitter_handle_from_dynamodb():
    dynamodb = boto3.client('dynamodb')

    response = dynamodb.scan(
        TableName=TABLE_NAME,
        Select='ALL_ATTRIBUTES',
        FilterExpression='tweeted = :tweeted',
        ExpressionAttributeValues={
            ':tweeted': {
                'BOOL': False
            }
        }
    )

    if len(response['Items']) == 0:
        print("No handle found")
        return None
    twitter_handle = response['Items'][0]['handle']['S']

    response = dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={
            'handle': {
                'S': twitter_handle
            }
        },
        UpdateExpression='SET tweeted = :tweeted',
        ExpressionAttributeValues={
            ':tweeted': {
                'BOOL': True
            }
        }
    )
    print(f'Handle{twitter_handle}')
    return twitter_handle

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


def lambda_handler(event, context):
    twitter_handle = get_twitter_handle_from_dynamodb()
    twitter = Twitter(twitter_handle)
    tweets = twitter.get_last_month_tweets_for_user()

    # Make sure the user tweeted the previous month
    if len(tweets) == 0: return

    words = twitter.get_words(tweets)
    generate_word_cloud(words)

    user = tweets[0]['user']
    month = tweets[0]['created_at'].strftime('%B')

    tweet_text = f"""
@{user} these are the most common words you tweeted for the month of {month}.
#visualization #wordcloud #automation #AWS #Lambda #{month}
    """
    twitter.send_tweet(tweet_text, IMG_PATH)

    os.remove(IMG_PATH)

