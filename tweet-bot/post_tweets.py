import os
import json
import time
import tweepy
import random
from dotenv import load_dotenv
from supabase import create_client, Client as SupabaseClient


# Init .env
load_dotenv()

# Init Supabase and login
url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: SupabaseClient = create_client(url, key)
data = supabase.auth.sign_in_with_password({
    "email":
    os.environ["SUPABASE_LOGIN_EMAIL"],
    "password":
    os.environ["SUPABASE_LOGIN_PASSWORD"]
})

# Define strategies
strategies = ["THREAD", "SINGlE_TWEET"]


def login():
    # Login to Twitter v2 API via OAuth 1.0a User Context
    client = tweepy.Client(
        consumer_key=os.environ['TWITTER_API_KEY'],
        consumer_secret=os.environ['TWITTER_API_KEY_SECRET'],
        access_token=os.environ['TWITTER_ACCESS_TOKEN'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    )

    # Test the client by fetching own user details
    try:
        user_response = client.get_me()
        if user_response.data:
            print(f"Sucessfully logged in as {user_response.data}")
            return client
        else:
            print(f"Failed to fetch user details. Response: f{user_response} ")
    except Exception as e:
        print(f"An error occurred: {e}")

def growth():
    strategy = random.choice(strategies)
    if strategy is "THREAD":
        print("")

    else:
        print("")
    
    # establish strategies
        # Threads: (from {custom_instructions = SEO articles and other long-form content, industry advice, etc.} using hook templates and image gen)
        # Single tweets: (can be manually generated and pasted into single_tweets.json) 
    # randomize between the 2
        # threads:
            # send prompt and receive json
            # iteratively post tweets, each tweet should 20sec after the previous one
        # single tweets:
            # post tweet
    # update DB



def main():
    # Login to twitter with rettiwt
    client = login()

    # Lessgoo
    growth(client)


if __name__ == "__main__":
    main()