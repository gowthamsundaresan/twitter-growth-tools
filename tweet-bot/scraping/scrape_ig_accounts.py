import os
import json
import re
from dotenv import load_dotenv
from instagrapi import Client as InstagrapiClient
from instagrapi.exceptions import LoginRequired

# Init env
load_dotenv()

# Init Instagrapi
cl = InstagrapiClient()

# Load username and password
username = os.environ['INSTAGRAM_USERNAME']
password = os.environ['INSTAGRAM_PASSWORD']

# Configurations
accounts_file_path = "accounts.txt" 
scrapes_path = "scrapes"


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


def read_lines_from_file(file_path):
    """
    Reads lines from a file located at 'file_path'.

    Parameters:
    -----------
        file_path : str
            The path of the file to read from.

    Returns:
    --------
        list of str
            A list containing each line in the file as a separate string.
    """
    with open(file_path, 'r') as file:
        return file.readlines()

def remove_line_and_write_back(file_path, line_to_remove):
    # Read all lines from the file
    lines = read_lines_from_file(file_path)

    # Filter out the line to remove
    lines = [line for line in lines if line.strip("\n") != line_to_remove]

    # Write the remaining lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)


def scrape():
    print("Entered scrape()")

    try:
        # Read all accounts from file
        accounts = read_lines_from_file(accounts_file_path)
        for account in accounts:
            # Scrape first 100 posts
            print(f"Now scraping {account}")
            user_id = cl.user_id_from_username(account)
            cl.delay_range = [1, 3]
            medias = cl.user_medias(user_id, 100)

            print(f"Got {len(medias)} posts")

            # Clean data
            pattern = r"Media\(pk='(\d+)', .*? media_type=(\d+), .*? caption_text='(.*?)',"
            matches = re.findall(pattern, str(medias), re.DOTALL)
            cleaned_data = [{"pk": pk, "media_type": int(media_type), "caption_text": caption_text} for pk, media_type, caption_text in matches]
            cleaned_json = json.dumps(cleaned_data, indent=4)

            # Write to file
            file_name = f"scrapes/{account}.json"
            with open(file_name, 'w') as file:
                json.dump(cleaned_data, file, indent=4)

            print(f"Data written to {file_name}")
            remove_line_and_write_back(accounts_file_path, account)

            # Rest
            print(f"Resting...")
            cl.delay_range = [30, 60]

    except LoginRequired:
        # Re-login
        print("Logged out. Attempting to re-login.")
        login_user()


        # Resume strategy
        print("Resuming strategy.")
        scrape()

    print("Completed scraping all given users")

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
    scrape()

if __name__ == "__main__":
    main()