import os
import json
import time
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

def growth():
    print("")
    # iterate over tweet queue
    #  


def main():
    # Lessgoo
    growth()


if __name__ == "__main__":
    main()