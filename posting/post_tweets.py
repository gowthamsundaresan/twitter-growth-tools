import os
import json
import time
import tweepy
import random
from dotenv import load_dotenv

load_dotenv()

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def login():
    # Login to Twitter v2 API via OAuth 1.0a User Context
    client = tweepy.Client(
        consumer_key=os.environ['TWITTER_API_KEY'],
        consumer_secret=os.environ['TWITTER_API_KEY_SECRET'],
        access_token=os.environ['TWITTER_ACCESS_TOKEN'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'])

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

def growth(client):
    total_actions = 0
    while True:
        replies = read_json_file('replies.json')
        if replies:
            for reply in replies:
                id = reply["id"]
                reply = reply["response"]
                try:
                    response = client.create_tweet(in_reply_to_tweet_id=id, text=reply, user_auth=True)
                    total_actions += 1
                    print(f"Replied to tweet with id:{id}: {reply}")
                    print(f"Total actions: {total_actions}")

                    interval = random.randint(180, 420)
                    print(f"Resting for {interval} seconds...")
                    time.sleep(interval)
                except Exception as e:
                    print(f"Failed to tweet in reply to {id}: {e}")
        else:
            print("All replies posted. Resting for 10 mins...")
            time.sleep(600)


def main():
    # Login to twitter with rettiwt
    client = login()

    # Lessgoo
    growth(client)


if __name__ == "__main__":
    main()