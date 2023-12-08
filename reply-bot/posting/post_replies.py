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

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

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

def growth(client):
    total_actions = 0
    while True:
        replies = read_json_file('replies.json')
        if replies:
            for reply in replies:
                id = reply["id"]
                reply = reply["response"]
                posted_tweets = supabase.from_('Twitter Actions').select('tweet_id').eq('tweet_id', id).execute()
                if len(posted_tweets.data) is 0:
                    try:
                        response = client.create_tweet(in_reply_to_tweet_id=id, text=reply, user_auth=True)
                        print(f"Replied to tweet with id:{id}: {reply}")

                        # Update Twitter Actions table in Supabase 
                        insert_table = supabase.table('Twitter Actions').insert({'response_to_id': id, 'text': response['data']['text'], 'action': 'reply'}).execute()
                        print(f"Twitter Actions table updated")

                        total_actions += 1
                        print(f"Total actions: {total_actions}")
                        
                        # Sleep for 3 to 7 mins before posting next reply
                        interval = random.randint(180, 420)
                        print(f"Resting for {interval} seconds...")
                        time.sleep(interval)
                    except Exception as e:
                        print(f"Failed to tweet in reply to {id}: {e}")
                else:
                    print(f"Tweet with id {id} has already been replied to.")
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