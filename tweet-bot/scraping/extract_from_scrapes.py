import os
import json
import random
import pytesseract
import time
from PIL import Image
from dotenv import load_dotenv
from instagrapi import Client as InstagrapiClient
from instagrapi.exceptions import LoginRequired
from openai import OpenAI

# Init env
load_dotenv()

# Init Instagrapi
cl = InstagrapiClient()

# Init OpenAI
client = OpenAI()

# Load username and password
username = os.environ['INSTAGRAM_USERNAME']
password = os.environ['INSTAGRAM_PASSWORD']

# Configurations
base_dir = '/Users/gowtham/Projects/twitter-growth-tools/tweet-bot/scraping'
accounts_file_path = "accounts.txt" 
scrapes_path = "scrapes"
download_path = "images"
output_path = "outputs"
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"


# Function definitions
def login_user():
    """
    Attempts to log in to Instagram using session data if provided.
    If not, attempts to login with username/password and then stores session data. 

    Returns:
    --------
        None. The function updates the client's login state on success.

    Raises:
    -------
        Exception
            If login fails using both session data and username/password.
    """

    # Load session from file if session.json exists
    if os.path.exists("session.json"):
        session = cl.load_settings("session.json")

    # Set session to None if session.json does not exist
    else:
        session = None

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(username, password)
            cl.delay_range = [3, 5]

            # Check if session is valid
            try:
                cl.get_timeline_feed()
                print("Logged in")
            except LoginRequired:
                print(
                    "Session is invalid, need to login via username and password"
                )

                old_session = cl.get_settings()

                # Use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(username, password)
                cl.delay_range = [3, 5]
            login_via_session = True
        except Exception as e:
            print("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        # Login and store session
        try:
            print(
                "Attempting to login via username and password. Username: %s" %
                "getjoyroots")
            if cl.login(username, password):
                login_via_pw = True
                cl.dump_settings("session.json")
                cl.delay_range = [3, 5]
        except Exception as e:
            print("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")


def convert_paths_to_strings(paths):
    return [os.path.relpath(str(path),base_dir) for path in paths]

def add_entry_to_json(pk, image_type, caption, image_text, image_paths, file_path):
    # Initialize data as an empty list
    data = []

    # Check if the file exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        # Read the existing data
        with open(file_path, 'r') as file:
            data = json.load(file)

    # Convert PosixPath objects to strings if necessary
    if isinstance(image_paths, list):
        image_paths = convert_paths_to_strings(image_paths)

    # Append new entry
    new_entry = {
        "pk": pk,
        "type": image_type,
        "caption": caption,
        "image_text": image_text,
        "image_path": image_paths 
    }
    data.append(new_entry)

    # Write back to the file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def delete_media_object(file_name, pk_to_delete):
    # Load the JSON data from the file
    with open(file_name, 'r') as file:
        data = json.load(file)

    # Filter out the object with the specified pk
    data = [obj for obj in data if obj['pk'] != pk_to_delete]

    # Write the updated data back to the file
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)


def extract():
    # Open oldest file in 'scrapes'
    files = [os.path.join(scrapes_path, f) for f in os.listdir(scrapes_path) if os.path.isfile(os.path.join(scrapes_path, f))]
    random.shuffle(files)
    
    # Iterate over all scrapes
    for selected_scrape in files:

        print("Extracting from ", selected_scrape)

        # Load the JSON data from the file
        with open(selected_scrape, 'r') as file:
            medias = json.load(file)

        total_actions = 0
        selected_user = os.path.basename(selected_scrape)

        account_downloads_dir = f"{download_path}/{selected_user[:-5]}"
        if not os.path.exists(account_downloads_dir):
            os.makedirs(account_downloads_dir)

        try:
            for media in medias:
                # Photo
                if media['media_type'] == 1:
                    print("New photo retrieved")

                    # Grab caption and download image
                    caption = media['caption_text']
                    download = cl.photo_download(media['pk'], account_downloads_dir)
                    print(f"Caption: {caption}")
                    cl.delay_range = [10, 15]

                    # Extract text from image
                    relative_path = os.path.relpath(str(download), base_dir)
                    
                    attempt = 0
                    max_attempts = 100
                    while attempt < max_attempts:
                        try:
                            image = Image.open(relative_path)
                            image_text = pytesseract.image_to_string(image)
                            print(f"Image text: {image_text}")
                            break
                        except (IOError, pytesseract.TesseractError) as e:
                            print(f"Error opening image, retrying... {attempt+1}/{max_attempts}")
                            time.sleep(2)  # Wait for 2 seconds before retrying
                            attempt += 1

                    if attempt == 100:
                        image_text = ""

                    # Add all media info to media_data.json
                    add_entry_to_json(media['pk'], "photo", caption, image_text, relative_path, f"{output_path}/{selected_user}")
                    total_actions += 1

                    # Delete media object from scraped json
                    delete_media_object(selected_scrape, media['pk'])
                
                # Album    
                elif media['media_type'] == 8:
                    print("New album retrieved")

                    # Grab caption and download album
                    caption = media['caption_text']
                    download = cl.album_download(media['pk'], account_downloads_dir)
                    print(f"Caption: {caption}")

                    image_text_consolidated = ""

                    for path in download:
                        # Convert PosixPath to string and make the path relative
                        relative_path = os.path.relpath(str(path), base_dir)
                        attempt = 0
                        max_attempts = 100
                        
                        while attempt < max_attempts:
                            try:
                                image = Image.open(relative_path)
                                image_text = pytesseract.image_to_string(image)
                                image_text_consolidated += f"\n{image_text}"
                                print(f"Image text: {image_text}")
                                break
                            except (IOError, pytesseract.TesseractError) as e:
                                print(f"Error opening image, retrying... {attempt+1}/{max_attempts}")
                                time.sleep(2)  # Wait for 2 seconds before retrying
                                attempt += 1

                        if attempt == 100:
                            image_text_consolidated += ""                       

                    add_entry_to_json(media['pk'], "album", caption, image_text_consolidated, download, f"{output_path}/{selected_user}")
                    total_actions += 1
                    
                    # Delete media object from scraped json
                    delete_media_object(selected_scrape, media['pk'])
                    
                    print("Fetching next media in album...")
                    cl.delay_range = [5,6]

                else:
                    print("New video retrieved, skipping")

                print(f"Total actions: {total_actions}")
                print("Fetching next post...")
                cl.delay_range = [5, 6]

            print(f"Scraped {total_actions} from {selected_user}")

        except LoginRequired:
            # Re-login
            print("Logged out. Attempting to re-login.")
            login_user()

            # Resume strategy
            print("Resuming strategy.")
            extract()

        # Delete account from file
        os.remove(selected_scrape)
    
    print("Completed extraction from all files.")


def main():
    """
    Main function. Performs the login and then executes the strategy.

    Returns:
    --------
        None.
    """
    # Login
    login_user()
    cl.delay_range = [1, 3]

    # Begin strategy
    extract()


if __name__ == "__main__":
    main()