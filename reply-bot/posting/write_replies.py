import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

# Init .env
load_dotenv()

# Init OpenAI
client = OpenAI()

def read_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Splitting the content at each user message section
    parts = content.split('[')

    # Extracting user_message_1 and user_message_2
    user_message_1 = next((part for part in parts if part.startswith('user_message_1')), None)
    user_message_2 = next((part for part in parts if part.startswith('user_message_2')), None)

    # Removing the section headers and returning the messages
    return user_message_1.split(']', 1)[1].strip(), user_message_2.split(']', 1)[1].strip()

def process_next_tweetset(folder_path):
    # List all .json files
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    if not json_files:
        return None, None, "No JSON files found."

    # Find the oldest file
    oldest_file = min(json_files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
    oldest_file_path = os.path.join(folder_path, oldest_file)

    # Read and parse the JSON file
    try:
        with open(oldest_file_path, 'r') as file:
            data = json.load(file)
    except Exception as e:
        return None, oldest_file_path, f"Error reading {oldest_file}: {e}"

    # Return the parsed data
    return data, oldest_file_path, None

def delete_tweetset(file_path):
    try:
        os.remove(file_path)
        return None
    except Exception as e:
        return f"Error deleting {file_path}: {e}"

def write_to_json_file(data, file_name):
    try:
        # Try to load JSON to check if it's valid
        parsed_json = json.loads(data)
        
        # Write the valid JSON to a file
        with open(file_name, 'w') as file:
            json.dump(parsed_json, file, indent=4)
        return "JSON written to file successfully."
    except json.JSONDecodeError as e:
        # Handle invalid JSON
        return f"Invalid JSON: {e}"


def growth():
    # Pick next oldest file in selected_tweets folder
    user_message_1, user_message_2 = read_prompts('prompts.txt')
    while True:
        data, path, error = process_next_tweetset('selected_tweets')
        print(f"Processing {path}")
        if data:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": ""
                }, {
                    "role": "user",
                    "content": user_message_1
                },
                {
                    "role": "user",
                    "content": user_message_2 + str(data)
                }]
            )
            replies = response.choices[0].message.content
            result = write_to_json_file(replies, 'replies.json')
            print(result)
            delete_tweetset(path)
        elif error:
            # No more files to process
            print("Processed all tweet sets, resting for 10 mins")
            time.sleep(36000)
    

def main():
    # Lessgoo
    growth()


if __name__ == "__main__":
    main()