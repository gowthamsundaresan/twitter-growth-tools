import os
import json
import random
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client, Client as SupabaseClient


# Init .env
load_dotenv()

# Init OpenAI client
client = OpenAI()

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

# Controls
strategies = ["SINGLE_TWEET"]
st_user_message_1 = '''
Let me tell you more about me:

I'm a person who has solved her anxiety and reached great mental health with healthy practices and natural/herbal supplements. I am against drugs like SSRIs, etc. for mental health as I've experienced lot of side effects with them. Natural ways, taking care of body, mind, nutrition, exercise, sleep etc. is the way to go!

Now I want to spread the message (on twitter) of how to deal with anxiety and stress and how to lead a more happy and fulfilling life!

Anyway, feel free to expand on what I told you about myself when you devise tweet ideas. Don't be limited just by this description!

In the next message I will give you some writing guidelines
'''
st_user_message_2 = '''
I need you to help me write tweets in a very human-like way. Here are some guidelines:

Tone and style: Make these tweets very opinionated and polarizing. Don't worry about being offensive or impolite. Let's be super bold, we need to create a MOVEMENT! Avoid formal language. Don't be a nice guy, just be relatable. Draw on a range of real-life perspectives and experiences related to mental wellness.

Grammar and words: Don't use exclamation marks. Don't use any hashtags. Don't use perfect grammar. Skip commas, full stops, capitalization. Make mistakes. Don’t use phrases like "ain't" ”isn’t it?”, “right?”, “huh?”, "eh?".

It's ok not to make much sense. Twitter is a very chill place, we DO NOT want to be formal or robotic! 

In the next message I will give you templates to use to craft tweets!
'''
st_user_message_3 = '''
Note:
Output your result as a json string like this
[{template_no: <template number>, tweet1: <first tweet>, tweet2: <second tweet>, tweet3: <third tweet>}]
Output only the valid json string as I will be sending your response directly to an API
'''

tfb_user_message_1 = '''
Let's write a tweet thread! We’d need to convert this article into a killer tweet thread:
'''
tfb_user_message_2 = '''
Here are some templates for writing a killer “first tweet” for a thread! Just have a look and understand them. In the next message I will give you some more writing guidelines. Templates:

"The GOLDEN rule about [Topic] is this: there are no shortcuts... You either [Achieve Specific Goal] or you don't. No one can do the work but you. No one can [Critical Action] but you. No one can [Another Essential Action] but you..."

"HOW I MADE MY FIRST $[Amount] BY [Action or Strategy Used]. This is a thread of the exact steps I took [Time Period] ago to [Achievement] and how you can do the same today. Let’s dive in 🥂"

"I've [Achievements and Failures in Field]. Here are [Number] lessons I learned the hard way (so you don't have to) 👇"

"What's the most profitable skill set you could have? If I had to guess, I'd say [Skill 1] + [Skill 2]. Here are [Number] [Concepts or Techniques] I used to [Accomplishment]. (They're powerful, so use them ethically):"

"How did a [Age] year old [Adjective] [Demographic] go from [Starting Point] to [Remarkable Achievement]? [Thread]"

"There are [Number] funnels you can choose to build your [Project or Product]. Choose the right one and you could easily make $[Amount]/mo from just a [Simple Action]:"

"Become Unrecognizable by [Year]. ([Number] Steps to Transforming Your Life in the Next [Time Period]) >>THREAD<<"

"I interviewed [Number] [Type of Experts] this week. I asked them to share their lessons learned on [Topics]. Here's what they told me:"

“What I Learned in [Time Period] of [Activity or Experiment] Since [Starting Point], I’ve [Background Activity]. For the past [Time Period], I’ve been intentionally [Specific Action]. This is called [Term]. Here’s what I’ve learned:”

“[Number] mistakes to avoid before your [Age Milestone]”

“Nobody wants to be a [Negative Stereotype]. I've helped dozens of [Professionals or Creatives] hit their first [Goal]. Here are [Number] similarities that held them back:”
'''
tfb_user_message_3 = '''
You need to write tweets in a very human-like way. Here are some guidelines:

Tone and style: Make these tweets very opinionated and polarizing. Don't worry about being offensive or impolite. Let's be super bold, we need to create a MOVEMENT! Avoid formal language. Don't be a nice guy, just be relatable. Use conversational phrases and millennial slang where appropriate. Draw on a range of real-life perspectives and experiences related to mental wellness.

Grammar and words: Don't use exclamation marks. Don't use any hashtags. Don’t use perfect grammar. Skip commas and full stops. Don’t use phrases like ”isn’t it?”, “right?”, “huh?”, “ain’t”, “eh?”.

Important note:
Please output in the form of a json string like
{
'tweet_1':'<your text>',
'tweet_2':<'your text'>
}

Only output the json string because I will send your response straight to an API call

Now please write a killer tweet thread!
'''

def growth():
    while True:
        strategy = random.choice(strategies)

        if strategy == "SINGLE_TWEET":
            print("Single tweet")
            with open('single_tweet_templates.json', 'r') as file:
                data = json.load(file)
                templates = random.sample(data, 3)

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": ""
                },
                {
                    "role": "user",
                    "content": st_user_message_1 + " \n\nIn the next message, I'll give you some more writing guidelines"
                },
                {
                    "role": "user",
                    "content": st_user_message_2
                },
                {
                    "role": "user",
                    "content": "Please write 3 tweets for each given template: " + str(templates) + st_user_message_3
                }]
            )
            tweets = response.choices[0].message.content
            data = json.loads(tweets)
            print("json loaded :" + str(data))

            all_tweets = []

            for item in data:
                all_tweets.append(item['tweet1'])
                all_tweets.append(item['tweet2'])
                all_tweets.append(item['tweet3'])

            for tweet in all_tweets:
                print(tweet)
                insert_table = supabase.table('Twitter Queue').insert({'type': 'single_tweet', 'text': tweet}).execute()
        elif strategy == "THREAD_FROM_BLOG":
            articles = supabase.from_('Published Articles').select('article_plain_text').eq('is_converted_to_tweet', False).execute()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": ""
                },
                {
                    "role": "user",
                    "content": tfb_user_message_1 + articles.data
                },
                {
                    "role": "user",
                    "content": tfb_user_message_2
                },
                {
                    "role": "user",
                    "content": tfb_user_message_3
                }]
            )
            tweets = response.choices[0].message.content
            insert_table = supabase.table('Twitter Queue').insert({'type': 'thread_from_blog', 'text': tweets}).execute()



    # if THREAD_FROM_SOURCE:  
        # pull random source text from source_articles.json
        # string together 3 prompts
        # parse output json and write to Tweet Queue







def main():
    # Lessgoo
    growth()


if __name__ == "__main__":
    main()